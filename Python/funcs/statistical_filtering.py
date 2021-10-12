import numpy as np


# Statistical Filtering
def statistical_filter(SpikeMat, SpikeTime, max_mean, max_std, max_percent_outlier):

    spike_mean = np.mean(SpikeMat, axis=1)
    spike_std = np.std(SpikeMat, axis=1)
    
    L = (spike_std > max_std) | (spike_mean > max_mean) | (spike_mean < -max_mean)
    ind = np.where(L==True)[0]
    num_outliers = len(ind)
    
    if num_outliers > max_percent_outlier * len(SpikeMat):
        criterion = spike_std/np.std(spike_std) + np.abs(spike_mean)/np.std(spike_mean)
        criterion_s = np.sort(criterion)[::-1]
        L = criterion > criterion_s[np.ceil(len(L)*max_percent_of_outliers)]
        ind = np.where(L==True)[0]
        
    #SpikeMat = np.delete(SpikeMat, ind, axis=0)
    #SpikeTime = np.delete(SpikeTime, ind, axis=0)
    
    return L, ind