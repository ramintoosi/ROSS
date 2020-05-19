function out = RT_ST_spike_sorter(SpikeMat,sdd,REM,INPCA)
% this function sorts detected spikes using mixtures of multivariate skew-t
% distributions. SpikeMat is matrix of detected spikes, sdd is settings,
% REM contains spikes after statistical filtering. INPCA is a logical value
% which determines whether considering noise spikes in computing PCA or not.

% default values for REM and INPCA
if nargin < 3
    REM = [];
    INPCA = true;
end

if nargin < 4
    INPCA = true;
end

% removing REM if it is given in wrong format
if ~islogical(REM) || length(REM) ~= size(SpikeMat,1)
    REM = [];
end

seed = sdd.sort.random_seed;

g_max = sdd.sort.g_max;
g_min = sdd.sort.g_min;

% removing outliers using given REM
if ~INPCA && ~isempty(REM)
    SpikeMat(REM,:) = [];
end

% returns principal component scores in SpikeMat and the principal
% component variances in latent
[~,SpikeMat,latent] = pca(SpikeMat);

% choosing number of pca coefficients shuch that 0.95 of variance is covered
h = find(cumsum(latent)/sum(latent) > 0.95);
h = h(1);

% limiting number of pca coefficients (h) by n_pca_max
if h > sdd.sort.n_pca_max
    h = sdd.sort.n_pca_max;
end

% considering first "h" pca scores
SpikeMat = SpikeMat(:,1:h);

if ~isempty(REM) && INPCA
    SpikeMat(REM,:) = [];
end

% initial value for nu parameter
nu = sdd.sort.nu;
L_max = -inf;

g = g_max; % j

nrow = @(x) size(x,1);
ncol = @(x) size(x,2);


n_feat = ncol(SpikeMat);
n_spike = nrow(SpikeMat);


% initialization

% simple clustering method
rng(seed)

% running FCM on SpikeMat. initial value for mu is considered cluster
% centers returned from fcm function. this step is done only for first g (g_max)
[mu,U] = fcm(SpikeMat,g,[2,20,1,0]);

% Estimate starting point for Sigma and Pi from simple clustering method
% performed before
rep=reshape(repmat(1:g,n_spike,1),g*n_spike,1);
rep_data=repmat(SpikeMat,g,1);
diffs=rep_data-mu(rep,:); % X - mu
clear rep_data;
[~,idx] = max(U);
U=U';

mu = mat2cell(mu,ones(size(mu,1),1))';
shape = cell(1, g); Sigma = cell(1, g);
for j=1:g
    shape{j} = sign(sum((SpikeMat(idx == j, :) - repmat(mu{j}, [nrow(SpikeMat(idx == j, :)), 1])).^3, 1));
    Sigma{j}=(((U(:,j)*ones(1,n_feat)).*diffs(rep==j,:))'*diffs(rep==j,:))/sum(U(:,j));
end


pii=sum(U) /sum(sum(U));


delta = cell(1, g);
Delta = cell(1, g);
Gama = cell(1, g);

% running clustering algorithm for g in [g_max, ...,g_min]
while(g >= g_min)
    for k = 1 : g
        delta{k} = shape{k} ./ sqrt(1 + shape{k} * transpose(shape{k}));
        Delta{k} = transpose(matrix_sqrt(Sigma{k}) * transpose(delta{k}));
        Gama{k} = Sigma{k} - transpose(Delta{k}) * Delta{k};
    end
    
    if sdd.sort.uni_Gama
        Gama_uni = plus(Gama{:}) / g;
        Gama(:) = {Gama_uni};
    end
    Delta_old = Delta;
    criterio = 1;
    count = 0;
    lkante = 1;
    
    % starting EM algorithm to find optimum set of parameters. EM algorithm
    % ends when maximum change among all parameters is smaller than a
    % error, or when reaching "max_iter".
    while ((criterio > sdd.sort.error) && (count <= sdd.sort.max_iter))
        count = count + 1;
        tal = zeros(n_spike, g);
        S1 = zeros(n_spike, g);
        S2 = zeros(n_spike, g);
        S3 = zeros(n_spike, g);
        for j = 1 : g
            % Expectation
            Dif = SpikeMat - repmat(mu{j}, [n_spike, 1]);
            Mtij2 = 1./(1 + Delta{j} * (Gama{j} \ transpose(Delta{j})));
            Mtij = sqrt(Mtij2);
            mtuij = sum(repmat(Mtij2 .* (Delta{j} / Gama{j}), [n_spike, 1]) .* Dif, 2);
            A = mtuij ./ Mtij;
            
            dj = (pdist2(SpikeMat,mu{j},'mahalanobis',Sigma{j})).^2;
            
            E = (2 .* (nu).^(nu./2) .* gamma((n_feat + nu + 1)./2) .* ((dj + nu + A.^2)).^(-(n_feat + nu + 1)./2))./(gamma(nu./2) .* (sqrt(pi)).^(n_feat + 1) .* sqrt(det(Sigma{j})) .* dmvt_ls(SpikeMat, mu{j}, Sigma{j}, shape{j}, nu));
            u = ((4 .* (nu).^(nu./2) .* gamma((n_feat + nu + 2)./2) .* (dj + nu).^(-(n_feat + nu + 2)./2))./(gamma(nu./2) .* sqrt(pi.^n_feat) .* sqrt(det(Sigma{j})) .* dmvt_ls(SpikeMat, mu{j}, Sigma{j}, shape{j}, nu))) .* tcdf(sqrt((n_feat + nu + 2) ./ (dj + nu)) .* A, n_feat + nu + 2);
            
            d1 = dmvt_ls(SpikeMat, mu{j}, Sigma{j}, shape{j}, nu);
            if sum(d1 == 0)
                d1(d1 == 0) = 1/intmax;
            end
            d2 = d_mixedmvST(SpikeMat, pii, mu, Sigma, shape, nu);
            if sum(d2 == 0)
                d2(d2 == 0) = 1/intmax;
            end
            
            tal(:, j) = d1 .* pii(j)./d2;
            S1(:, j) = tal(:, j) .* u;
            S2(:, j) = tal(:, j) .* (mtuij .* u + Mtij .* E);
            S3(:, j) = tal(:, j) .* (mtuij.^2 .* u + Mtij2 + Mtij .* mtuij .* E);
            
            % maximization
            pii(j) = (1./n_spike) .* sum(tal(:, j));
            
            mu{j} = sum(S1(:, j) .* SpikeMat - S2(:, j) .* repmat(Delta_old{j}, [n_spike, 1]), 1)./sum(S1(:, j));
            Dif = SpikeMat - mu{j};
            Delta{j} = sum(S2(:, j) .* Dif, 1)./sum(S3(:, j));
            
            sum2 = zeros(n_feat);
            for i = 1 : n_spike
                sum2 = sum2 + (S1(i, j) .* (transpose(SpikeMat(i, :) - mu{j})) * (SpikeMat(i, :) - mu{j}) - ...
                    S2(i, j) .* (transpose(Delta{j}) * (SpikeMat(i, :) - mu{j})) - ...
                    S2(i, j) .* (transpose(SpikeMat(i, :) - mu{j}) * (Delta{j})) + ...
                    S3(i, j) .* (transpose(Delta{j}) * (Delta{j})));
            end
            
            Gama{j} = sum2 ./ sum(tal(:, j));
            
            if ~sdd.sort.uni_Gama
                Sigma{j} = Gama{j} + transpose(Delta{j}) * Delta{j};
                shape{j} = (Delta{j} / matrix_sqrt(Sigma{j})) / (1 - Delta{j} / Sigma{j} * transpose(Delta{j})).^(1/2);
            end
        end
        
        logvero_ST = @(nu) -1*sum(log(d_mixedmvST(SpikeMat, pii, mu, Sigma, shape, nu)));
        options = optimset('TolX', 0.000001);
        nu = fminbnd(logvero_ST, 0, 100, options);
        pii(g) = 1 - (sum(pii) - pii(g));
        
        zero_pos = pii == 0;
        pii(zero_pos) = 1e-10;
        pii(pii == max(pii)) = max(pii) - sum(pii(zero_pos));
        
        lk = sum(log(d_mixedmvST(SpikeMat, pii, mu, Sigma, shape, nu)));
        criterio = abs((lk./lkante) - 1);
        
        lkante = lk;
        % mu_old = mu;
        Delta_old = Delta;
        % Gama_old = Gama;
        
        
    end
    % computing log likelihood function as a criterion to find the best g.
    [~, cl] = max(tal, [], 2);
    L = 0;
    for j = 1 : g
        L = L + sum(log(pii(j) .* dmvt_ls(SpikeMat(cl == j,:), mu{j}, Sigma{j}, shape{j}, nu)));
    end
    
    % for first g (g_max) L_max has been -inf, for next iterations
    % (g_max-1, ..., g_min) L is compared to largest L between all previous
    % iters. 
    if L > L_max     
        L_max = L; 
        % assigning cluster indices to each spike. if REM is given the
        % outliers must be assigned to cluster 255.
        if isempty(REM) 
            [~,out.cluster_index] = max(tal,[],2);
        else
            [~,c_i] = max(tal,[],2);
            cluster_index = zeros(length(REM),1);
            cluster_index(~REM) = c_i;
            cluster_index(REM) = 255; % removed
            out.cluster_index = cluster_index;
        end
    else
        break
    end
    
    % set smalletst component to zero
    m_pii = min(pii);
    indx_remove = (pii == m_pii) | (pii < 0.01);
    % Purge components
    mu(indx_remove) = [];
    Sigma(indx_remove) = [];
    pii(indx_remove) = [];
    shape(indx_remove) = [];
    g = g-sum(indx_remove);

end


end
