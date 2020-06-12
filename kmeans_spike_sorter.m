function optimal_set = kmeans_spike_sorter(SpikeMat,sdd,REM,INPCA)
% this function sorts detected spikes based on k-means clustering method
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

% GMM clustering method
rng(seed)
options = statset('MaxIter',max_iter);
myfunc = @(X,K)(kmeans(X, K, 'replicate',5, 'Options', options));
eva = evalclusters(SpikeMat,myfunc,'CalinskiHarabasz','klist',[g_min:g_max]);
if isempty(REM)
    optimal_set.cluster_index = kmeans(SpikeMat,eva.OptimalK,'replicate',5,'Options',options);
else
    optimal_set.cluster_index(~REM) = kmeans(SpikeMat,eva.OptimalK,'replicate',5,'Options',options);
    optimal_set.cluster_index(REM) = 255; % removed
end


