function [newSpikeMat,newSpikeTime] = spike_alignment(SpikeMat,SpikeTime, ss)
% This function takes SpikeMat, SpikeTime and ss (settings) and returns the
% alligned SpikeMat.

max_shift = ss.alignment.max_shift;

% upsampling rate is considered 10
r_upsample = 10;
[n_spike,n_feat] = size(SpikeMat);
n_upsample = r_upsample * n_feat;

% max shift in upsampled spike equals to r_upsample*max_shift
max_spline_align_shift = r_upsample*max_shift;

n_peaks = ss.alignment.n_peaks;
n_bin = ss.alignment.number_of_hist_bins;

ind_min = zeros(n_spike,1);
ind_max = zeros(n_spike,1);

% finding min and max indices for each spike
for i = 1 : size(SpikeMat,1)
    % cubic spline interpolation, S contains values corresponding to
    % the query points in linspace(1,n_feat,n_upsample)
    S = spline(1:n_feat,SpikeMat(i,:),linspace(1,n_feat,n_upsample));
    [amp_min(i),ind_min(i)] = min(S);
    [amp_max(i),ind_max(i)] = max(S);   
end

if strcmpi(ss.alignment.comparison_mode, 'index')
    % grouping samples based on index
    ind_neg = ind_min < ind_max;
elseif strcmpi(ss.alignment.comparison_mode, 'magnitude')
    % grouping samples based on magnitude
    ind_neg = abs(amp_min) < abs(amp_max);
else
    error('Comparison Mode in alignment is not supported')
end

% indices of first group minimums
ind_min_neg = ind_min(ind_neg);
% calculating samples histogram
[freq_neg,cen_neg] = hist(ind_min_neg,n_bin);
% cubic spline interpolation of histogram
s_neg = spline(cen_neg,freq_neg,linspace(min(cen_neg),max(cen_neg),5*n_bin));
% further smoothing
s_neg = rt_smoother(s_neg,100);
% finding local maxima of the smoothed histogram
[~,loc_peaks_neg] = findpeaks(s_neg,'sortstr','descend','MinPeakDistance',...
    max_spline_align_shift/2);
% adding to resolution to find peaks more precisely
x = linspace(min(cen_neg),max(cen_neg),5*n_bin);
loc_peaks_neg = round(x(loc_peaks_neg));
% choosing first "n_peaks" peaks (peaks are sorted in descending order)
if length(loc_peaks_neg) > n_peaks
    loc_peaks_neg = loc_peaks_neg(1:n_peaks);
end

% "max_shift" number of samples are removed from the begining and end
newSpikeMat = SpikeMat(:,1+max_shift:end-max_shift);
% indices of neg group
ind_neg_find = find(ind_neg);
% shifting time with the amount of "max_shift" because first "max_shift" 
% samples are ignored.
time_shift = zeros(n_spike,1) + max_shift;

for i = 1 : length(ind_min_neg)
    
    % finding minimum distance between indices of samples minimum and 
    % selected histogram peaks, ind_cluster determines index of the
    % final selected peak as alignment point.
    [min_shift,ind_cluster] = ...
        min(abs(repmat(ind_min_neg(i),1,length(loc_peaks_neg)) - loc_peaks_neg));
    % ignore spike shifting if min_shift exceeds maximum allowed shift
    if min_shift > max_spline_align_shift
        continue
    end
    
    % calculating n_shift based on found "ind_cluster", then dividing it by
    % r_upsample to achieve shift of the original signal
    n_shift = round((ind_min_neg(i) - loc_peaks_neg(ind_cluster))/r_upsample);
    
    % shifting
    if n_shift > 0
        L = max_shift + n_shift;
        R = max_shift - n_shift;
        newSpikeMat(ind_neg_find(i),:) = SpikeMat(ind_neg_find(i),1+L:end-R);
        time_shift(ind_neg_find(i)) = time_shift(ind_neg_find(i)) + n_shift/2;
    else
        L = max_shift - abs(n_shift);
        R = max_shift + abs(n_shift);
        newSpikeMat(ind_neg_find(i),:) = SpikeMat(ind_neg_find(i),1+L:end-R);
        time_shift(ind_neg_find(i)) = time_shift(ind_neg_find(i)) - n_shift/2;
    end  
    
end

% indices of second group maximums
ind_max_pos = ind_max(~ind_neg);
% calculating samples histogram
[freq_pos,cen_pos] = hist(ind_max_pos,n_bin);
% cubic spline interpolation of histogram
s_pos = spline(cen_pos,freq_pos,linspace(min(cen_pos),max(cen_pos),5*n_bin));
% further smoothing
s_pos = rt_smoother(s_pos,50);
% finding local maxima of the smoothed histogram
[~,loc_peaks_pos] = findpeaks(s_pos,'sortstr','descend','MinPeakDistance'...
    ,max_spline_align_shift/2);
% adding to resolution to find peaks more precisely
x = linspace(min(cen_pos),max(cen_pos),5*n_bin);
loc_peaks_pos = round(x(loc_peaks_pos));
% choosing first "n_peaks" peaks (peaks are sorted in descending order)
if length(loc_peaks_pos) > n_peaks
    loc_peaks_pos = loc_peaks_pos(1:n_peaks);
end

% indices of pos group
ind_pos_find = find(~ind_neg);

for i = 1 : length(ind_max_pos)
    % finding minimum distance between indices of samples maximum and 
    % selected histogram peaks, ind_cluster determines index of the
    % final selected peak as alignment point.
    [min_shift,ind_cluster] = ...
        min(abs(repmat(ind_max_pos(i),1,length(loc_peaks_pos)) - loc_peaks_pos));
    % ignore spike shifting if min_shift exceeds maximum allowed shift
    if min_shift > max_spline_align_shift
        continue
    end
    
    % calculating n_shift based on found "ind_cluster", then dividing it by
    % r_upsample to achieve shift of the original signal
    n_shift = round((ind_max_pos(i) - loc_peaks_pos(ind_cluster)) / r_upsample);
    
    % shifting
    if n_shift > 0
        L = max_shift + n_shift;
        R = max_shift - n_shift;
        newSpikeMat(ind_pos_find(i),:) = SpikeMat(ind_pos_find(i),1+L:end-R);
        time_shift(ind_pos_find(i)) = time_shift(ind_pos_find(i)) - n_shift/2;
    else
        L = max_shift - abs(n_shift);
        R = max_shift + abs(n_shift);
        newSpikeMat(ind_pos_find(i),:) = SpikeMat(ind_pos_find(i),1+L:end-R);
        time_shift(ind_pos_find(i)) = time_shift(ind_pos_find(i)) - n_shift/2;
    end
    
end
newSpikeTime = SpikeTime + time_shift;

