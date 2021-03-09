function [SpikeMat,SpikeTime] = spike_detection(raw,config_struct)
% This function filters signal and detects spikes with their 
% corresponding time. "raw" is raw signal. config_struct is a structure
% containig the following variables: thr_method, side, spike_filter_type,
% spike_filter_order, spike_Rp, spike_Rs and sampling rate.

clear global Spike SpikeMat SpikeTime SpikeMatChunk SpikeTimeChunk
% Global Variables
global Spike
Spike = raw;
clear raw

% thr method TODO: move me to the config file
thr_method = config_struct.thr_method;
side = config_struct.side;


% filter characteristics
ftype = config_struct.spike_filter_type;
forder = config_struct.spike_filter_order;
fRp = config_struct.spike_Rp;
fRs = config_struct.spike_Rs;
sr = config_struct.sampling_rate;
threshold_factor = config_struct.threshold_factor;

% ftype is filtering function name ("butter")
% [b,a] is the transfer function coefficients of filter
[b,a]= feval(ftype,forder,[fRp,fRs]/(sr/2));

% if threshold method is 'wavelet', 'threshold calculater' uses 'Spike'
% variable without filtering, else zero phase filtering is done first.
if strcmpi(thr_method,'wavelet')
    thr = threshold_calculater(thr_method, threshold_factor);
end

% filtering 'Spike' before using threshold calcalator for threshold methods
% other than 'wavelet'
Spike = filtfilt(b,a,Spike);
if ~strcmpi(thr_method,'wavelet')
    thr = threshold_calculater(thr_method, threshold_factor);
end

% spike detection
[SpikeMat, SpikeTime] = spike_detector(thr,side,config_struct);

% filter Spikes between Rp and Rs provided in config file.
SpikeMat(SpikeTime==0,:) = [];
SpikeTime(SpikeTime==0,:) = [];
size(SpikeMat)
size(SpikeTime)
clear Spike
end

%%%%% SUPPORING FUNCTIONS %%%%%

function thr = threshold_calculater(method, threshold_factor)
% This function calculates threshold for spike detection. four methods are
% supported: "median", "wavelet", "plexon", and "energy".

global Spike

% default method
if nargin < 1
    method = "median";
end
switch(method)
    case "median"
        thr= threshold_factor * median((abs(Spike))./0.6745);
    case "wavelet"
        %  computing the wavelet decomposition of Spike at level 2 
        %  using 'db3' wavelet
        [c,l] = wavedec(Spike,2,'db3');
        % estimating noise of 1-D wavelet coefficients [c,l]
        thr = threshold_factor*wnoisest(c,l,2);
    case "plexon"
        % full signal sigma
        full_signal_sigma = std(Spike);
        % applying fake positive negative threshold
        indx_discard = (Spike > 2.7*full_signal_sigma) | (Spike < -2.7*full_signal_sigma);
        thr = threshold_factor*std(Spike(~indx_discard));
    case "energy"
        % a constant threshold independent from Spike
        thr = 0.065;
    otherwise
        error("not supported thresholding method")
end

end

function [SpikeMat,SpikeTime] = spike_detector(thr,side,config_struct)
% This function detects spikes and return each spike and its corresponding
% time. each row of spike mat corresponds to one detected spike.
global Spike
% parameters
pre_thresh = config_struct.pre_thresh;
n_points_per_spike = config_struct.pre_thresh + config_struct.post_thresh + 1;

% DEAD TIME
dead_time = config_struct.dead_time;

% default for threshold side is both sides
if nargin < 2
    side = "two";
end

if strcmpi(side,"mean")
    % automatic choice between positive and negative based on sign of mean
    sign_mean = sign(mean(Spike));
    if sign_mean > 0
        side = "positive";
    else
        side = "negative";
    end
end

% thresholding
switch(side)
    case "two"
        spike_detected = (Spike > thr) | (Spike < -thr);
    case "positive"
        spike_detected = (Spike > thr);
    case "negative"
        spike_detected = (Spike < -thr);
    otherwise
        error("side error")
end

% ind_det: indices of non-zero detected points
ind_det = find(spike_detected);
for i = 1 : length(ind_det)
    i_s = ind_det(i);
    if spike_detected(i_s) == 0
        continue
    end
    % if post_thresh + dead_time does not exceed spike length
    if i_s + n_points_per_spike - pre_thresh -1 + dead_time <= length(Spike)
        % finding minimum amplitude in post threshold + dead_time
        [~,ind_min] = min(Spike(i_s:i_s + n_points_per_spike - pre_thresh -1 + dead_time));
        % removing possible detection in post threshold + dead_time
        % interval after the current detected index including current index
        spike_detected(i_s:i_s + n_points_per_spike - pre_thresh -1 + dead_time) = 0;
        % setting minimum index as detected
        spike_detected(i_s+ind_min-1) = true;
    % else: post_thresh + dead_time exceeds spike length,
    else
        % finding minimum amplitude in remaining spike samples
        [~,ind_min] = min(Spike(i_s:end));
        % removing possible detection after the current detected index 
        % including current index
        spike_detected(i_s:end) = 0;
        % setting minimum index as detected 
        spike_detected(i_s+ind_min-1) = true;
    end
    
end

% update detected indices by throwing away unwanted detections
indx_spikes = find(spike_detected ~= 0);

SpikeMat  = zeros(length(indx_spikes),n_points_per_spike);
SpikeTime  = zeros(length(indx_spikes),1);

% assigning SpikeMat and SpikeTime matrices
for i = 1 : length(indx_spikes)
    
    curr_indx = indx_spikes(i);
    % check if all indices of the spike waveform are inside signal
    if (((curr_indx - pre_thresh) > 0) && (curr_indx - pre_thresh ...
            + n_points_per_spike - 1) <= length(Spike))
        
        SpikeMat (i,:) = Spike(curr_indx - pre_thresh : curr_indx - pre_thresh ...
            + n_points_per_spike - 1);
        SpikeTime (i) = curr_indx;
        
    end
    
end

ind_rm = sum(SpikeMat,2) == 0;
SpikeMat(ind_rm,:) = [];
SpikeTime(ind_rm) = [];

end