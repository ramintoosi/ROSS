from models.data import RawModel
from models.config import ConfigDetectionModel
import numpy as np
import pywt
import pyyawt
import scipy.signal
import io


def startDetection(user_id):
    raw = RawModel.find_by_user_id(user_id)
    if not raw:
        raise Exception
    config = ConfigDetectionModel.find_by_user_id(user_id)
    if not config:
        raise Exception
    
    if not raw.data:
        raise Exception

    b = io.BytesIO()
    b.write(raw.data)
    b.seek(0)
    d = np.load(b, allow_pickle=True)
    data = d['raw']
    b.close()

    thr_method = config.thr_method
    fRp = config.pass_freq
    fRs = config.stop_freq
    forder = config.filter_order
    sr = config.sampling_rate
    pre_thr = config.pre_thr
    post_thr = config.post_thr
    dead_time = config.dead_time
    thr_side = config.side_thr

    if thr_method == 'wavelet':
        thr = thresholdCalculator(data, 'wavelet')
        print(thr)

    b, a = scipy.signal.butter(forder, (fRp/(sr/2), fRs/(sr/2)), btype='bandpass')

    data_filtered = scipy.signal.filtfilt(b, a, data)
    if not thr_method == 'wavelet':
        thr = thresholdCalculator(data_filtered, thr_method)

    # spike detection
    SpikeMat, SpikeTime = spike_detector(data_filtered, thr, pre_thr, post_thr, dead_time, thr_side)

    # filter Spikes between Rp and Rs provided in config file.
    ind = np.where(SpikeTime==0)[0]#indices(SpikeTime, lambda x:(x == 0))
    SpikeMat = np.delete(SpikeMat, ind, axis=0) #[SpikeTime==0,:] = []
    SpikeTime = np.delete(SpikeTime, ind, axis=0)#[SpikeTime==0,:] = []

    print(SpikeMat.shape, SpikeTime.shape)
    return SpikeMat, SpikeTime
    

def thresholdCalculator(data, method):
    if method == 'median':
        thr = 3 * np.median((np.abs(data))/0.6745)
    elif method == 'wavelet':
        print(data.shape)
        c, l = pyyawt.wavedec(data,2, 'db3')
        print(c.shape, l.shape)
        thr = 5*pyyawt.denoising.wnoisest(c,l)[1] # [1] gives results like matlab [0] gives another result
    else: #'plexon'
        full_signal_sigma = np.std(data)
        indx_discard = (data > 2.7*full_signal_sigma) | (data < -2.7*full_signal_sigma)
        thr = 4*np.std(data[np.logical_not(indx_discard)])
    return thr


def spike_detector(data, thr, pre_thr, post_thr, dead_time, thr_side='both'):
# This function detects spikes and return each spike and its corresponding
# time. each row of spike mat corresponds to one detected spike.

    n_points_per_spike = pre_thr + post_thr + 1
    if thr_side == "mean":
        # automatic choice between positive and negative based on sign of mean
        sign_mean = np.sign(np.mean(data))
        if sign_mean > 0:
            thr_side = "positive"
        else:
            thr_side = "negative"

    # thresholding
    if thr_side == "both":
        spike_detected = (data > thr) | (data < -thr)
    elif thr_side == "positive":
        spike_detected = (data > thr)
    elif thr_side == "negative":
        spike_detected = (data < -thr)
    else:
        raise Exception

    # ind_det: indices of non-zero detected points
    ind_det = np.nonzero(spike_detected)[0]
    for i, i_s in enumerate(ind_det):
        # i_s = ind_det[i]
        if spike_detected[i_s] == 0:
            continue
        # if post_thresh + dead_time does not exceed spike length
        if i_s + n_points_per_spike - pre_thr + dead_time <= len(data):  # -1 from matlab eliminated
            # finding minimum amplitude in post threshold + dead_time
            ind_min = np.argmin(data[i_s:i_s + n_points_per_spike - pre_thr  + dead_time])  # -1 from matlab eliminated
            # removing possible detection in post threshold + dead_time
            # interval after the current detected index including current index
            spike_detected[i_s:i_s + n_points_per_spike - pre_thr  + dead_time] = 0  # -1 from matlab eliminated
            # setting minimum index as detected
            spike_detected[i_s+ind_min] = True
        # else: post_thresh + dead_time exceeds spike length,
        else:
            # finding minimum amplitude in remaining spike samples
            ind_min = np.argmin(data[i_s:])
            # removing possible detection after the current detected index 
            # including current index
            spike_detected[i_s:] = 0
            # setting minimum index as detected 
            spike_detected[i_s+ind_min] = True  # -1 from matlab eliminated


    # update detected indices by throwing away unwanted detections
    indx_spikes = np.nonzero(spike_detected)[0]

    SpikeMat = np.zeros((len(indx_spikes), n_points_per_spike))
    SpikeTime = np.zeros((len(indx_spikes), 1))

    # assigning SpikeMat and SpikeTime matrices
    for i, curr_indx in enumerate(indx_spikes):
        # curr_indx = indx_spikes[i]
        # check if all indices of the spike waveform are inside signal
        if (((curr_indx - pre_thr) > -1) and (curr_indx - pre_thr + n_points_per_spike) <= len(data)):# removing -1
            SpikeMat[i,:] = data[curr_indx - pre_thr : curr_indx - pre_thr + n_points_per_spike]# removing -1
            SpikeTime[i] = curr_indx + 1

    # ind_rm = (np.sum(SpikeMat,1) == 0)  # 2 -> 1
    # SpikeMat = np.delete(SpikeMat, ind_rm, axis=0) # = []
    # SpikeTime= np.delete(SpikeTime, ind_rm)#[ind_rm] = []

    return SpikeMat, SpikeTime


# def indices(a, func):
#     return [i for (i, val) in enumerate(a) if func(val)]