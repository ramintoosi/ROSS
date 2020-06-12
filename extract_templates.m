function [templates,REM] = extract_templates(os,SpikeMat,REM)
% this function extracts templates from sorting results. os is sorting 
% result struct containing "cluster_index" fieldSpikeMat is matrix of 
% detected spikes, REM contains spikes after statistical filtering. The 
% average of the spike waveforms is computed as template, and a matrix of
% templates is returned. REM is updated by adding clusters with 
% cluster_index more than 200 in os.

% removing REM if it is given in wrong format
if ~islogical(REM) || length(REM) ~= size(SpikeMat,1)
    REM = [];
end

if ~isempty(REM)
    temp = os.cluster_index > 200;
    REM = REM | temp';
elseif os.cluster_index > 200
    REM = os.cluster_index > 200;
end

if ~isempty(REM)
    n_cluster = max(os.cluster_index(~REM));
else
    n_cluster = max(os.cluster_index);
end
[~, n_samples] = size(SpikeMat);
if ~isempty(REM)
    Spikes = SpikeMat(~REM, :);
    
    cluster_index_spikes = os.cluster_index(~REM);
else
    Spikes = SpikeMat;
    cluster_index_spikes = os.cluster_index;
end

n_templates = n_cluster;

templates = zeros(n_templates, n_samples);
for i = 1:n_cluster
    cluster_spikes = Spikes(cluster_index_spikes==i, :);
    m = mean(cluster_spikes, 1);
    templates(i,:) = m(1,:);
end

save('temp.mat', 'templates')