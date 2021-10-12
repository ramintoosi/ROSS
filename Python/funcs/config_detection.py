#Settings_detection_default
class Config_Detection:
    def __init__(self):
        self.thr_method = 'median' #median, wavelet, plexon, energy
        self.side = 'negative' #both, positive, negative, mean
        self.spike_filter_type = 'butter'
        self.spike_filter_order = 4
        self.spike_Rp = 300
        self.spike_Rs = 3000
        self.pre_thresh = 40
        self.post_thresh = 59
        self.dead_time = 20
        self.sampling_rate = 40000
    
    def assign(self, thr_method, side, spike_filter_type, spike_filter_order, spike_Rp, spike_Rs, 
              pre_thresh, post_thresh, dead_time, sampling_rate):
        self.thr_method = thr_method
        self.side = side
        self.spike_filter_type = spike_filter_type
        self.spike_filter_order = spike_filter_order
        self.spike_Rp = spike_Rp
        self.spike_Rs = spike_Rs
        self.pre_thresh = pre_thresh
        self.post_thresh = post_thresh
        self.dead_time = dead_time
        self.sampling_rate = sampling_rate