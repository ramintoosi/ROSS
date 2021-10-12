import alignment_utils *


# Alignment
def spike_alignment(SpikeMat,SpikeTime, ss):
    
    max_shift = ss.alignment_max_shift
    
    # upsampling rate is considered 10
    r_upsample = 10
    n_spike, n_feat = SpikeMat.shape
    n_upsample = r_upsample * n_feat
    
    # max shift in upsampled spike equals to r_upsample*max_shift
    max_spline_align_shift = r_upsample * max_shift
    
    n_peaks = ss.alignment_n_peaks
    n_bin = ss.alignment_number_of_hist_bins
    
    amp_min = np.min(SpikeMat, axis=1)
    ind_min = np.argmin(SpikeMat, axis=1)
    amp_max = np.max(SpikeMat, axis=1)
    ind_max = np.argmax(SpikeMat, axis=1)
    
    if ss.alignment_comparison_mode == 'index':
        # grouping samples based on index
        ind_neg = ind_min < ind_max
    elif ss.alignment_comparison_mode == 'magnitude':
        # grouping samples based on magnitude
        ind_neg = np.abs(amp_min) < np.abs(amp_max)
    else:
        raise Exception
    
    # indices of first group minimum
    ind_min_neg = ind_min[ind_neg]
    
    # calculating samples histogram
    freq_neg, cen_neg = np.histogram(ind_min_neg+1, n_bin)
    cen_neg = cen_neg[:-1] + np.diff(cen_neg)/2
    
    # cubic spline interpolation of histogram
    f = scipy.interpolate.CubicSpline(cen_neg, freq_neg)
    sample = np.linspace(min(cen_neg), max(cen_neg), 5*n_bin)
    s_neg = f(sample)
    
    # further smoothing
    s_neg = rt_smoother(s_neg,100)
    
    # finding local maxima of the smoothed histogram
    loc_peaks_neg = scipy.signal.find_peaks(s_neg)
    loc_peaks_neg = np.asarray(loc_peaks_neg[0])
    
    # adding to resolution to find peaks more precisely
    x = np.linspace(min(cen_neg),max(cen_neg),5*n_bin)
    loc_peaks_neg = np.round(x[loc_peaks_neg])
    
    # choosing first "n_peaks" peaks (peaks are sorted in descending order)
    loc_peaks_neg = np.sort(loc_peaks_neg)[::-1]
    if len(loc_peaks_neg) > n_peaks:
        loc_peaks_neg = loc_peaks_neg[0:n_peaks]
    
    # "max_shift" number of samples are removed from the begining and end
    newSpikeMat = SpikeMat[:, max_shift:-max_shift]
    
    # shifting time with the amount of "max_shift" because first "max_shift" samples are ignored.
    time_shift = np.zeros((n_spike,1)) + max_shift
    
    # indices of neg group
    ind_neg_find = np.nonzero(ind_neg)[0]
    
    for i in range(len(ind_min_neg)):
        # finding minimum distance between indices of samples minimum and selected histogram peaks, ind_cluster determines index of the final selected peak as alignment point.
        d = abs(np.tile(ind_min_neg[i] + 1, (1, len(loc_peaks_neg))) - loc_peaks_neg)
        ind_cluster = d.argmin()
        min_shift = d[0][ind_cluster] 
        # ignore spike shifting if min_shift exceeds maximum allowed shift
        if min_shift > max_spline_align_shift:
            continue

        # calculating n_shift based on found "ind_cluster", then dividing it by r_upsample to achieve shift of the original signal
        n_shift = matlab_round((ind_min_neg[i] + 1 - loc_peaks_neg[ind_cluster]) / r_upsample)

        # shifting
        if n_shift > 0:
            L = int(max_shift + n_shift)
            R = int(max_shift - n_shift)
            if R == 0:
                newSpikeMat[ind_neg_find[i], :] = spike_mat[ind_neg_find[i], L:]
            else:
                newSpikeMat[ind_neg_find[i], :] = spike_mat[ind_neg_find[i], L:- R]
            time_shift[ind_neg_find[i]] = time_shift[ind_neg_find[i]] + n_shift / 2
        else:
            L = int(max_shift - abs(n_shift))
            R = int(max_shift + abs(n_shift))
            if R == 0:
                newSpikeMat[ind_neg_find[i], :] = spike_mat[ind_neg_find[i], L:]
            else:
                newSpikeMat[ind_neg_find[i], :] = spike_mat[ind_neg_find[i], L: - R]
            time_shift[ind_neg_find[i]] = time_shift[ind_neg_find[i]] - n_shift / 2
     
    #################################################################################
    # indices of second group maximum
    ind_max_pos = ind_max[np.logical_not(ind_neg)]
    
    # calculating samples histogram
    freq_pos, cen_pos = np.histogram(ind_max_pos+1, n_bin)
    cen_pos = cen_pos[:-1] + np.diff(cen_pos)/2
    
    # cubic spline interpolation of histogram
    f = scipy.interpolate.CubicSpline(cen_pos, freq_pos)
    sample_pos = np.linspace(min(cen_pos), max(cen_pos), 5*n_bin)
    s_pos = f(sample_pos)
    
    # further smoothing
    s_pos = rt_smoother(s_pos,100)
    
    # finding local maxima of the smoothed histogram
    loc_peaks_pos = scipy.signal.find_peaks(s_pos)
    loc_peaks_pos = np.asarray(loc_peaks_pos[0])
    
    # adding to resolution to find peaks more precisely
    x_pos = np.linspace(min(cen_pos),max(cen_pos),5*n_bin)
    loc_peaks_pos = np.round(x[loc_peaks_pos])
    
    # choosing first "n_peaks" peaks (peaks are sorted in descending order)
    loc_peaks_pos = np.sort(loc_peaks_pos)[::-1]
    if len(loc_peaks_pos) > n_peaks:
        loc_peaks_pos = loc_peaks_pos[0:n_peaks]
        
    # indices of pos group
    ind_pos_find = np.nonzero(np.logical_not(ind_neg))[0]
    for i in range(len(ind_max_pos)):
        # finding minimum distance between indices of samples maximum and selected histogram peaks, ind_cluster determines index of the final selected peak as alignment point.
        d = abs(np.tile(ind_max_pos[i] + 1, (1, len(loc_peaks_pos))) - loc_peaks_pos)
        ind_cluster = d.argmin()
        min_shift = d[0][ind_cluster]
        # min_shift, ind_cluster = min(abs(np.repmat(ind_max_pos[i], 1, len(loc_peaks_pos)) - loc_peaks_pos))
        # ignore spike shifting if min_shift exceeds maximum allowed shift
        if min_shift > max_spline_align_shift:
            continue
        # calculating n_shift based on found "ind_cluster", then dividing it by r_upsample to archieve hsift of the original signal


        n_shift = matlab_round((ind_max_pos[i] + 1 - loc_peaks_pos[ind_cluster]) / r_upsample)

        # shifting
        if n_shift > 0:
            L = int(max_shift + n_shift)
            R = int(max_shift - n_shift)
            if R == 0:
                newSpikeMat[ind_pos_find[i], :] = spike_mat[int(ind_pos_find[i]), L:]
            else:
                newSpikeMat[ind_pos_find[i], :] = spike_mat[int(ind_pos_find[i]), L: - R]
            time_shift[ind_pos_find[i]] = time_shift[ind_pos_find[i]] - n_shift / 2
        else:
            L = int(max_shift - abs(n_shift))
            R = int(max_shift + abs(n_shift))
            if R == 0:
                newSpikeMat[ind_pos_find[i], :] = spike_mat[ind_pos_find[i], L:]
            else:
                newSpikeMat[ind_pos_find[i], :] = spike_mat[ind_pos_find[i], L:- R]
            time_shift[ind_pos_find[i]] = time_shift[ind_pos_find[i]] - n_shift / 2

    newSpikeTime = spike_time + time_shift 
    
    return newSpikeMat, newSpikeTime