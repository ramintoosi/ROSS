import numpy as np
import pywt
import pyyawt
import scipy.signal

#Filtering
def filtering(data, forder, fRp, fRs, sr):
    b, a = scipy.signal.butter(forder, (fRp/(sr/2), fRs/(sr/2)), btype='bandpass')
    data_filtered = scipy.signal.filtfilt(b, a, data)
    return data_filtered
	

# Threshold
def threshold_calculator(method, thr_factor, data):
    if method == 'median':
        thr = thr_factor * np.median((np.abs(data))/0.6745)
    elif method == 'wavelet':
        c, l = pyyawt.wavedec(data, 2, 'db3')
        thr = thr_factor * pyyawt.denoising.wnoisest(c,l)[1]
    elif method == 'plexon':
        full_signal_sigma = np.std(data)
        indx_discard = (data > 2.7*full_signal_sigma) | (data < -2.7*full_signal_sigma)
        thr = thr_factor * np.std(data[np.logical_not(indx_discard)])
    elif method == 'energy':
        thr = 0.065
    else:
        raise Exception('Wrong method of threshold calculator!')
    return thr


# Spike Detector
def spike_detector(data, thr, config_struct):
    pre_thresh = config_struct.pre_thresh
    post_thresh = config_struct.post_thresh
    side = config_struct.side
    dead_time = config_struct.dead_time
    
    n_points_per_spike = pre_thresh + post_thresh + 1
    
    # Thresholding
    if side == "mean":
        sign_mean = np.sign(np.mean(data))
        if sign_mean > 0:
            side = "positive"
        else:
            side = "negative"
    
    if side == "both":
        spike_detected = (data > thr) | (data < -thr)
    elif side == "positive":
        spike_detected = (data > thr)
    elif side == "negative":
        spike_detected = (data < -thr)
    else:
        raise Exception
    
    ind_det = np.nonzero(spike_detected)[0]
    
    for i, i_s in enumerate(ind_det):
        if spike_detected[i_s] == 0:
            continue  
        if i_s + n_points_per_spike - pre_thresh + dead_time <= len(data):
            ind_min = np.argmin(data[i_s:i_s + n_points_per_spike - pre_thresh  + dead_time])  
            spike_detected[i_s:i_s + n_points_per_spike - pre_thresh  + dead_time] = 0 
            spike_detected[i_s+ind_min] = True
        else:
            ind_min = np.argmin(data[i_s:])
            spike_detected[i_s:] = 0
            spike_detected[i_s+ind_min] = True


    # update detected indices by throwing away unwanted detections
    indx_spikes = np.nonzero(spike_detected)[0]

    SpikeMat = np.zeros((len(indx_spikes), n_points_per_spike))
    SpikeTime = np.zeros((len(indx_spikes), 1))

    # assigning SpikeMat and SpikeTime matrices
    for i, curr_indx in enumerate(indx_spikes):
        # check if all indices of the spike waveform are inside signal
        if (((curr_indx - pre_thresh) > -1) and (curr_indx - pre_thresh + n_points_per_spike) <= len(data)):
            SpikeMat[i,:] = data[curr_indx - pre_thresh : curr_indx - pre_thresh + n_points_per_spike]
            SpikeTime[i] = curr_indx + 1

    ind_rm = np.where(SpikeTime==0)[0] 
    SpikeMat = np.delete(SpikeMat, ind_rm, axis=0)
    SpikeTime = np.delete(SpikeTime, ind_rm, axis=0)

    return SpikeMat, SpikeTime