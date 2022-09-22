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
        thr = threshold_calculator('wavelet', 4, data)

    data_filtered = filtering(data, forder, fRp, fRs, sr)
    if not thr_method == 'wavelet':
        thr = threshold_calculator(thr_method, 3, data_filtered)

    # spike detection
    SpikeMat, SpikeTime = spike_detector(data_filtered, thr, pre_thr, post_thr, dead_time, thr_side)


    print(SpikeMat.shape, SpikeTime.shape)
    return SpikeMat, SpikeTime
    

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


# Filtering
def filtering(data, forder, fRp, fRs, sr):
    print('inside filtering!')
    b, a = scipy.signal.butter(forder, (fRp/(sr/2), fRs/(sr/2)), btype='bandpass')
    print('after b, a')
    data_filtered = scipy.signal.filtfilt(b, a, data)
    print('after filtfilt!')
    return data_filtered

