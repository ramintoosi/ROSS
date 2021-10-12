import detection_utils *

def spike_detection(data, config):
    thr_method = config.thr_method
    fRp = config.spike_Rp
    fRs = config.spike_Rs
    forder = config.spike_filter_order
    sr = config.sampling_rate
    pre_thr = config.pre_thresh
    post_thr = config.post_thresh
    dead_time = config.dead_time
    thr_side = config.side
    
    if thr_method == 'wavelet':
        thr = threshold_calculator('wavelet', 4, data)
        
    data_filtered = filtering(data, forder, fRp, fRs, sr)
    if not thr_method == 'wavelet':
        thr = threshold_calculator(thr_method, 3, data_filtered)
    
    SpikeMat, SpikeTime = spike_detector(data_filtered, thr, config)
    
    return SpikeMat, SpikeTime