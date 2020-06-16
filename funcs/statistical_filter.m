function L = statistical_filter(SpikeMat,sdd)
% This functions does statistical filtering on detected spikes by
% thresholding on waveform std and mean, and returns a logical matrix 
% containing location of detected outliers (L).

Max_std = sdd.stat_filter.max_std;
Max_mean = sdd.stat_filter.max_mean;

spike_std = std(SpikeMat,0,2);
spike_mean = mean(SpikeMat,2);

% finding locations of threshold crossing points
L = (spike_std > Max_std) | (spike_mean > Max_mean) | (spike_mean < -Max_mean);

% check if perecent of detected outliers exceeds maximum allowed percent
if sum(L)/length(L) > sdd.stat_filter.max_percent_of_outliers
    % limiting number of detected outlier to maximum allowed percent by
    % sorting them based on criterion
    criterion = spike_std/std(spike_std) + abs(spike_mean)/std(spike_mean);
    criterion_s = sort(criterion,'descend');
    L = criterion > criterion_s(ceil(length(L)*sdd.stat_filter.max_percent_of_outliers));
end