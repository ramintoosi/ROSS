function sdd = settings_sorting_default()
% Default settings for sorting.
% alignment
sdd.alignment.max_shift = 10; % int pos 1-size(spike_mat,2)/2 -1
sdd.alignment.n_peaks = 3; % int pos 1-size(spike_mat,2)
sdd.alignment.number_of_hist_bins = 75; 
sdd.alignment.comparison_mode = 'index'; % index, magnitude

% statistical filtering
sdd.stat_filter.max_std = 3; % float pos 0.0000001 - inf
sdd.stat_filter.max_mean = 1; % float pos 0.0000001 - inf
sdd.stat_filter.max_percent_of_outliers = 5; % 0-100 float

% t-distribution sorting
sdd.sort.type = 't dist';
sdd.sort.nu = 20; %float 0-inf
sdd.sort.g_max = 9; %int g_min-inf
sdd.sort.g_min = 1; %int 1-g_max
sdd.sort.max_iter = 500; %int pos 1-inf
sdd.sort.u_lim = 0.01; % float 0-1
sdd.sort.N = 15; %float 0-inf
sdd.sort.n_pca = 5; %int 1-size(spike_mat,2)
sdd.sort.n_pca_max = 5; %
sdd.sort.random_seed = 561371; %any
sdd.sort.error = 1e-1;% float
sdd.sort.uni_Gama = false;% boolean %NOTE: not provided in the ui yet

write_arguments_to_json(sdd,'config_sorting');
