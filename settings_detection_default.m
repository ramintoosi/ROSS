function sdd = settings_detection_default()
% Default settings for detection.
sdd.thr_method = 'median'; % median, wavelet, plexon
sdd.side = 'negative'; % two, positive, negative, mean
sdd.spike_filter_type = 'butter';
sdd.spike_filter_order = 4;
sdd.spike_Rp = 300; % Hz
sdd.spike_Rs = 3000; % Hz
sdd.pre_thresh = 40; % samples
sdd.post_thresh = 59; % samples
sdd.dead_time = 20; % samples
sdd.sampling_rate = 40000; % sampling rate

write_arguments_to_json(sdd,'config_detection');
