function new_index = cluster_index_cleaner(cluster_index)
% This function is needed whenever cluster indices are changed. 

[~,~, new_index] = unique(cluster_index);
new_index(cluster_index > 200) = cluster_index(cluster_index > 200);

