import pickle

import numpy as np
import pyyawt
import scipy.signal
from models.config import ConfigDetectionModel
from models.data import RawModel


def startDetection(project_id):
    raw = RawModel.find_by_project_id(project_id)

    if not raw:
        raise Exception
    config = ConfigDetectionModel.find_by_project_id(project_id)
    if not config:
        raise Exception
    if not raw.data:
        raise Exception

    # print("raw.data", raw.data)
    # b = io.BytesIO()
    # b.write(raw.data)
    # b.seek(0)
    # d = np.load(b, allow_pickle=True)
    # data_address = d['raw']

    with open(raw.data, 'rb') as f:
        new_data = pickle.load(f)
        data = new_data

    # b.close()

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
        thr = threshold_calculator('wavelet', 4, data)

    data_filtered = filtering(data, forder, fRp, fRs, sr)
    if not thr_method == 'wavelet':
        thr = threshold_calculator(thr_method, 3, data_filtered)

    # spike detection
    SpikeMat, SpikeTime = spike_detector(data_filtered, thr, pre_thr, post_thr, dead_time, thr_side)
    # print("SpikeMat shape and SpikeTime shape : ", SpikeMat.shape, SpikeTime.shape)
    return SpikeMat, SpikeTime


# Threshold
def threshold_calculator(method, thr_factor, data):
    if method == 'median':
        thr = thr_factor * np.median((np.abs(data)) / 0.6745)
    elif method == 'wavelet':
        c, l = pyyawt.wavedec(data, 2, 'db3')
        thr = thr_factor * pyyawt.denoising.wnoisest(c, l)[1]
    elif method == 'plexon':
        full_signal_sigma = np.std(data)
        indx_discard = (data > 2.7 * full_signal_sigma) | (data < -2.7 * full_signal_sigma)
        thr = thr_factor * np.std(data[np.logical_not(indx_discard)])
    elif method == 'energy':
        thr = 0.065
    else:
        raise Exception('Wrong method of threshold calculator!')
    return thr


# Filtering
def filtering(data, forder, fRp, fRs, sr):
    # print('inside filtering!')
    b, a = scipy.signal.butter(forder, (fRp / (sr / 2), fRs / (sr / 2)), btype='bandpass')
    # print('after b, a')
    data_filtered = scipy.signal.filtfilt(b, a, data)
    # print('after filtfilt!')
    return data_filtered


# Spike Detector
def spike_detector(data, thr, pre_thresh, post_thresh, dead_time, side):
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
            ind_min = np.argmin(data[i_s:i_s + n_points_per_spike - pre_thresh + dead_time])
            spike_detected[i_s:i_s + n_points_per_spike - pre_thresh + dead_time] = 0
            spike_detected[i_s + ind_min] = True
        else:
            ind_min = np.argmin(data[i_s:])
            spike_detected[i_s:] = 0
            spike_detected[i_s + ind_min] = True

    # update detected indices by throwing away unwanted detections
    indx_spikes = np.nonzero(spike_detected)[0]

    SpikeMat = np.zeros((len(indx_spikes), n_points_per_spike))
    SpikeTime = np.zeros((len(indx_spikes), 1))

    # assigning SpikeMat and SpikeTime matrices
    for i, curr_indx in enumerate(indx_spikes):
        # check if all indices of the spike waveform are inside signal
        if ((curr_indx - pre_thresh) > -1) and (curr_indx - pre_thresh + n_points_per_spike) <= len(data):
            SpikeMat[i, :] = data[curr_indx - pre_thresh: curr_indx - pre_thresh + n_points_per_spike]
            SpikeTime[i] = curr_indx + 1

    ind_rm = np.where(SpikeTime == 0)[0]
    SpikeMat = np.delete(SpikeMat, ind_rm, axis=0)
    SpikeTime = np.delete(SpikeTime, ind_rm, axis=0)

    return SpikeMat, SpikeTime
