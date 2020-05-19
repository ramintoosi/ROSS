function optimal_set = RT_spike_sorter_faster(SpikeMat,sdd,REM,INPCA)
% this function sorts detected spikes according to the following paper:
% Robust, automatic spike sorting using mixtures of multivariate
% t-distributions. SpikeMat is matrix of detected spikes, sdd is settings,
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

if isempty(SpikeMat)
    optimal_set = [];
    return
end

[~,SpikeMat] = pca(SpikeMat,'NumComponents',sdd.sort.n_pca);

if ~isempty(REM) && INPCA
    SpikeMat(REM,:) = [];
end

% typicallity Limit
u_limit = sdd.sort.u_lim;

% Initialization
n_spike = size(SpikeMat,1); % i
n_feat = size(SpikeMat,2); % p in paper
Sigma = repmat(eye(n_feat),1,1,g_max);
v = sdd.sort.nu;
L_max = -inf;
% Theoreticaally :  N =  p(p+1)/2+p but in the paper it is determined emprically
% N = (n_feat)*(n_feat+1)/2 + n_feat;
N = sdd.sort.N;
g = g_max;

delta_L_limit = 0.1;
delta_v_limit = 0.1;

delta_L = 100;
delta_v = 100;

max_iter = sdd.sort.max_iter;

% simple clustering method to determine centers
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
U=U';
for i=1:g
    Sigma(:,:,i)=(((U(:,i)*ones(1,n_feat)).*diffs(rep==i,:))'*diffs(rep==i,:))/sum(U(:,i));
end

Pi=sum(U) /sum(sum(U));

L_old = -inf;
v_old = v;

Ltt = [];

% running clustering algorithm for g in [g_max, ...,g_min]
while(g >= g_min)
    iter = 1;
    % starting EM algorithm to find optimum set of parameters. EM algorithm
    % ends when maximum change among all parameters is smaller than a
    % threshold, or when reaching "max_iter".
    while((delta_L > delta_L_limit || delta_v > delta_v_limit) && iter < max_iter)
        % Probability , this way is better than the mvtpdf of MATLAB itself
        n_sigma=size(Sigma,3); % number of sigma
        detSigma=zeros(1,n_sigma);
        rep=reshape(repmat(1:g,n_spike,1),g*n_spike,1);
        rep_data=repmat(SpikeMat,g,1);
        diffs=rep_data-mu(rep,:); % Distances to cluster center
        for i=1:n_sigma
            detSigma(i)=1/sqrt(det(Sigma(:,:,i)));
        end
        M=zeros(n_spike,g);
        for i=1:n_sigma
            M(:,i)=real(sum(((sqrtm(pinv(Sigma(:,:,i)))*(diffs(rep==i,:)')).^2))'); %Mahalanobis distances
        end
        c=gamma((v+n_feat)/2)/(gamma(v/2)*(pi*v)^(n_feat/2));
        P =c*exp(-(v+n_feat)*log(1+M/v)/2)*diag(detSigma); % probabilities
        
        % membership
        num_z = repmat(Pi,n_spike,1).*P;
        den_z  = sum(num_z,2);
        z = num_z./repmat(den_z,1,g);
        
        % typicallity update
        delta_distance = M;
        u = (n_feat+v) ./ (delta_distance + v); 
        
        % M-Step
        deltaP = 1;
               
        while(deltaP > 1e-4)
            gtmp = g;
            Pi_old = Pi;
            num_ztmp = repmat(Pi,n_spike,1).*P;
            den_ztmp  = sum(num_ztmp,2);
            ztmp = num_ztmp./repmat(den_ztmp,1,gtmp);
            Pi_num = (sum(ztmp,1) - N/2); % Eq 7
            Pi_num(Pi_num<0) = 0;
            Pi = Pi_num ./ (n_spike-gtmp*N/2);         
            if any(Pi==0)
                gtmp = gtmp - sum(Pi > 0);
            end
            deltaP = norm(Pi_old-Pi,1);
            
        end
        
        Pi = Pi./sum(Pi); % normalize
        % update mu , sigma Eq 8
        for j = 1 : g
            % update mu
            num = sum((repmat(z(:,j),1,n_feat).*repmat(u(:,j),1,n_feat).*SpikeMat));
            mu(j,:) = num ./ sum(z(:,j).*u(:,j));
        end
        % update Sigma
        ZU = z.*u;
        for j=1:g
            diffs=SpikeMat-ones(n_spike,1)*mu(j,:);
            Sigma(:,:,j)=(((ZU(:,j)*ones(1,n_feat)).*diffs)'*diffs)/sum(ZU(:,j));
        end
        
        % update v Eq 10  Eq 11
        yt = [];
        yt = z.* (psi((n_feat+v)/2) + log(2./(delta_distance + v)) - u) / sum(z);
        y = real(-sum(yt(:)));
        v = 2 / (y+log(y) - 1) + 0.0416*(1 + erf(0.6594*log(2.1971/(y+log(y) - 1))));
        
        % Probability (t-dist)
        n_sigma=size(Sigma,3);
        detSigma=zeros(1,n_sigma);
        rep=reshape(repmat(1:g,n_spike,1),g*n_spike,1);
        rep_data=repmat(SpikeMat,g,1);
        diffs=rep_data-mu(rep,:); % Distances to cluster center
        for i=1:n_sigma
            detSigma(i)=1/sqrt(det(Sigma(:,:,i)));
        end
        M=zeros(n_spike,g);
        for i=1:n_sigma
            M(:,i)=sum(((sqrtm(pinv(Sigma(:,:,i)))*(diffs(rep==i,:)')).^2))'; % Mahalanobis distances
        end
        c=gamma((v+n_feat)/2)/(gamma(v/2)*(pi*v)^(n_feat/2));
        P =c*exp(-(v+n_feat)*log(1+M/v)/2)*diag(detSigma); % probabilities
        
        % update L Eq 5
        min_mess_len_criterion = N/2 * sum(log(n_feat.*Pi/12) + 0.5*g*log(n_feat/12) + g*(N+1)/2);
        l_log = sum(log(sum(repmat(Pi,n_spike,1).*P,2)),1);
        L = l_log - min_mess_len_criterion;
        
        % convergence criteria   
        delta_L = abs(L - L_old);
        delta_v = abs(v - v_old);
               
        L_old = L;
        v_old = v;
               
        Ltt = [Ltt,L];
        
        iter = iter + 1;
        if iter == max_iter
            warning('CONVERGENCE FAILED FOR delta_L')
        end
        indx_remove = Pi == 0;
        mu(indx_remove,:) = [];
        Sigma(:,:,indx_remove) = [];
        Pi(indx_remove) = [];
        z(:,indx_remove) = [];
        u(:,indx_remove) = [];
        P(:,indx_remove) = [];
        delta_distance(:,indx_remove) = [];
        g = g - sum(indx_remove);
        
    end
    
    if L > L_max
        
        L_max = L;
        if isempty(REM)
            [~,optimal_set.cluster_index] = max(z,[],2);         
        else
            [~,c_i] = max(z,[],2);
            cluster_index = zeros(length(REM),1);
            cluster_index(~REM) = c_i;
            cluster_index(REM) = 255; % removed
            optimal_set.cluster_index = cluster_index;
        end
        optimal_set.u = u;
        
    else
        break;
    end
    
    % set smalletst component to zero
    [~,ind_min] = min(Pi);
    Pi(ind_min) = 0;
    % Purge components where Pi = 0
    indx_remove = Pi == 0;
    mu(indx_remove,:) = [];
    Sigma(:,:,indx_remove) = [];
    Pi(indx_remove) = [];
    z(:,indx_remove) = [];
    u(:,indx_remove) = [];
    P(:,indx_remove) = [];
    delta_distance(:,indx_remove) = [];
    g = g-1;
    
end

% find not typical spikes based on typicality limit and assign them to
% cluster 254
if isempty(REM)
    u_final = zeros(n_spike,1);
    for i = 1 : n_spike
        u_final(i) = optimal_set.u(i,optimal_set.cluster_index(i));
        if u_final(i) < u_limit
            optimal_set.cluster_index(i) = 254;
        end
    end
    optimal_set.typicallity = u_final;
else
    % also spikes not included in REM must be assigned to cluster 255.
    ind_nor_rem = find(~REM);
    u_final = zeros(length(REM),1);
    for i = 1 : n_spike
        u_final(ind_nor_rem(i)) = optimal_set.u(i,optimal_set.cluster_index(ind_nor_rem(i)));
        if u_final(ind_nor_rem(i)) < u_limit
            optimal_set.cluster_index(ind_nor_rem(i)) = 255;
        end
    end
    optimal_set.typicallity = u_final;
    optimal_set = rmfield(optimal_set,'u');
end

end
