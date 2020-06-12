function sigma = estimate_noise(raw,config_struct)
% This function filters signal and estimates noise from the filtered raw 
% data. corresponding time. "raw" is raw signal. config_struct is a structure
% containig the following variables: spike_filter_type, spike_filter_order,
% spike_Rp, spike_Rs and sampling rate.

Spike = raw;
clear raw


% filter characteristics
ftype = config_struct.spike_filter_type;
forder = config_struct.spike_filter_order;
fRp = config_struct.spike_Rp;
fRs = config_struct.spike_Rs;
sr = config_struct.sampling_rate;

% ftype is filtering function name ("butter")
% [b,a] is the transfer function coefficients of filter
[b,a]= feval(ftype,forder,[fRp,fRs]/(sr/2));
sigma = median((abs(Spike))./0.6745);
end
