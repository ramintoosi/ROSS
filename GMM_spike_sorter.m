function optimal_set = GMM_spike_sorter(SpikeMat,sdd,REM,INPCA)
% this function sorts detected spikes based on GMM clustering method
% SpikeMat is matrix of detected spikes, sdd is settings, REM contains 
% spikes after statistical filtering. INPCA is a logical value which 
% determines whether considering noise spikes in computing PCA or not.

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

error = sdd.sort.error; % the termination tolerance for the loglikelihood function value.

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

max_iter = sdd.sort.max_iter;

% simple clustering method to determine centers
rng(seed)
options = statset('MaxIter',max_iter, 'TolFun', error);
myfunc = @(X,K)(cluster(fitgmdist(X, K, 'Replicates',5, 'Options', options), X));
eva = evalclusters(SpikeMat,myfunc, 'CalinskiHarabasz', 'KList',[g_min:g_max]);
BestModel = fitgmdist(SpikeMat,eva.OptimalK,'Options',options,'Replicates', 5);
if isempty(REM)
    optimal_set.cluster_index = cluster(BestModel, SpikeMat);
else
    optimal_set.cluster_index(~REM) = cluster(BestModel, SpikeMat);
    optimal_set.cluster_index(REM) = 255; % removed
end


