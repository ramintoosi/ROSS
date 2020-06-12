function optimal_set = template_matching_sorter(given_templates,SpikeMat,sdd,REM,sigma)
% this function sorts detected spikes based on template matching method
% given_templates is a matrix containing one template in each row. SpikeMat
% is matrix of detected spikes, sdd is settings, REM contains spikes after 
% statistical filtering.

% removing REM if it is given in wrong format
if ~islogical(REM) || length(REM) ~= size(SpikeMat,1)
    REM = [];
end

[~, n_samples] = size(SpikeMat);
if ~isempty(REM)
    Spikes = SpikeMat(~REM, :);
else
    Spikes = SpikeMat;
end
n_cluster = size(given_templates, 1);
if sdd.sort.templates_combination && n_cluster > 1
    combined = combnk(1:n_cluster, 2);
    n_templates = n_cluster + size(combined, 1);
else
    n_templates = n_cluster;
end

templates = zeros(n_templates, n_samples);
for i = 1:n_cluster
    size(templates(i,:))
    size(given_templates(i,:))
    templates(i,:) = given_templates(i,:);
end

% considering combinations of the given templates
for i = n_cluster+1:n_templates
    templates(i,:) = (templates(combined(i-n_cluster, 1),:) + templates(combined(i-n_cluster, 2),:))/2;
end

[n_spikes, ~]  = size(Spikes);
cluster_index = zeros(1, n_spikes);
d = zeros(1, n_templates);
mode = sdd.sort.matching_mode;
switch mode
    case 'Euclidean'
        for i = 1:n_spikes
            for j = 1:n_templates
                d(j) = (Spikes(i,:) - templates(j,:))*(Spikes(i,:)-templates(j,:))';
            end
            [~, cluster_index(i)] = min(d);
        end
        
    case 'Correlation'
        for i = 1:n_spikes
            for j = 1:n_templates
                d(j) = corr(Spikes(i,:)', templates(j,:)');
            end
            [~, cluster_index(i)] = max(d);
        end
        
    case 'Chi-squared'        
        res = zeros(n_templates, n_samples);
        alpha = sdd.sort.alpha;
        for i = 1:n_spikes
            candidate_clusters = logical(zeros(1, n_templates));
            candidate_sigmas = zeros(1, n_templates);
            for j = 1:n_templates
                res(j,:) = Spikes(i,:)-templates(j,:);
                [h,p] = chi2gof(res(j,:), 'Alpha', alpha,'cdf',{@normcdf,0,sigma});                
                nu2 = cov(res(j,:));
                candidate_sigmas(1,j) = nu2;
                if h==0 && ~isnan(p)
                    candidate_clusters(1,j) = true;
                end
                arguments = find(candidate_clusters(1,:));
                if sum(candidate_clusters) > 0
                    [~, m] = min(candidate_sigmas(candidate_clusters));
                    cluster_index(i) = arguments(m);
                else
                    [~, cluster_index(i)] = min(candidate_sigmas(1,:));
                end
            end
        end        
end
cluster_index = cluster_index_cleaner(cluster_index);

% assigning REM samples to cluster number 255
if isempty(REM)
    optimal_set.cluster_index = cluster_index;
else
    optimal_set.cluster_index(~REM) = cluster_index;
    optimal_set.cluster_index(REM) = 255; % removed
end

