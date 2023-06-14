import numpy as np
import scipy
from scipy import signal
from scipy.interpolate import CubicSpline
from scipy.spatial.distance import cdist
from scipy.special import gamma


def matrix_sqrt(A):
    # This function returns square root of input matrix(A).
    (u, s, v) = np.linalg.svd(A)
    (m, n) = A.shape
    C = np.array([[s[j] if i == j else 0 for j in range(n)] for i in range(m)])
    s = C
    v = v.T
    d = np.diag(s)
    if (min(d) >= 0):
        Asqrt = np.transpose(np.dot(v, (u * (np.sqrt(d))).T))
    else:
        raise Exception('Matrix square root is not defined.')
    return Asqrt


def dmvt_ls(y, mu, Sigma, landa, nu):
    # This function computes Density/CDF of Skew-T with scale location.
    # y must be a matrix where each row has a multivariate vector of dimension col(y) = p ,
    # nrow(y) = sample size. mu, lambda: must be of the vector type of the same dimension
    # equal to ncol(y) = lambda: 1 x p Sigma: Matrix p x p
    nrow = lambda x: x.shape[0]
    ncol = lambda x: x.shape[1]
    n = nrow(y)
    p = ncol(y)
    mahalanobis_d = np.power(cdist(y, np.expand_dims(mu, axis=0), metric='mahalanobis', VI=np.linalg.inv(Sigma)), 2)
    denst = (gamma((p + nu) / 2) / (gamma(nu / 2) * np.power(np.pi, p / 2))) * np.power(nu, -p / 2) * np.power(
        np.abs(np.linalg.det(Sigma)), (-1 / 2)) * np.power((1 + mahalanobis_d / nu), (-(p + nu) / 2))
    t = scipy.stats.t(nu + p)
    dens = 2 * (denst) * t.cdf(np.sqrt((p + nu) / (mahalanobis_d + nu)) * np.expand_dims(np.sum(
        np.tile(np.expand_dims(np.linalg.lstsq(matrix_sqrt(Sigma).T, landa.T, rcond=None)[0], axis=0), (n, 1)) * (
                y - mu), axis=1), axis=1))
    return dens


def d_mixedmvST(y, pi1, mu, Sigma, landa, nu):
    # y: the data matrix
    # pi1: must be of the vector type of dimension g
    # mu: must be of type list with g entries. Each entry in the list must be a vector of dimension p
    # Sigma: must be of type list with g entries. Each entry in the list must be an matrix p x p
    # lambda: must be of type list with g entries. Each entry in the list must be a vector of dimension p
    # nu: a number
    g = np.size(pi1)
    dens = 0
    for j in range(g):
        dens = dens + pi1[j] * dmvt_ls(y, mu[j], Sigma[j], landa[j], nu)  # lnda
    return dens


def matlab_round(num):
    res = (int(num > 0) - int(num < 0)) * int(abs(num) + 0.5)
    return res


# Statistical Filtering
def statistical_filter(SpikeMat, config):
    max_mean = config.max_mean
    max_std = config.max_std
    max_percent_outlier = config.max_outliers

    spike_mean = np.mean(SpikeMat, axis=1)
    spike_std = np.std(SpikeMat, axis=1)

    L = (spike_std > max_std) | (spike_mean > max_mean) | (spike_mean < -max_mean)
    ind = np.where(L == True)[0]
    num_outliers = len(ind)

    if num_outliers > max_percent_outlier * len(SpikeMat):
        criterion = spike_std / np.std(spike_std) + np.abs(spike_mean) / np.std(spike_mean)
        criterion_s = np.sort(criterion)[::-1]
        L = criterion > criterion_s[np.ceil(len(L) * max_percent_outlier)]

    return L


# Alignment
def spike_alignment(spike_mat, spike_time, ss):
    max_shift = ss.max_shift

    # upsampling rate is considered 10
    r_upsample = 10
    n_spike, n_feat = spike_mat.shape
    n_upsample = r_upsample * n_feat

    # max shift in upsampled spike equals to r_upsample*max_shift
    max_spline_align_shift = r_upsample * max_shift

    n_peaks = ss.num_peaks
    n_bin = ss.histogram_bins

    amp_min = np.min(spike_mat, axis=1)
    ind_min = np.argmin(spike_mat, axis=1)
    amp_max = np.max(spike_mat, axis=1)
    ind_max = np.argmax(spike_mat, axis=1)

    if ss.compare_mode == 'index':
        # grouping samples based on index
        ind_neg = ind_min < ind_max
    elif ss.compare_modee == 'magnitude':
        # grouping samples based on magnitude
        ind_neg = np.abs(amp_min) < np.abs(amp_max)
    else:
        raise Exception

    # indices of first group minimum
    ind_min_neg = ind_min[ind_neg]

    # calculating samples histogram
    freq_neg, cen_neg = np.histogram(ind_min_neg + 1, n_bin)
    cen_neg = cen_neg[:-1] + np.diff(cen_neg) / 2

    # cubic spline interpolation of histogram
    f = scipy.interpolate.CubicSpline(cen_neg, freq_neg)
    sample = np.linspace(min(cen_neg), max(cen_neg), 5 * n_bin)
    s_neg = f(sample)

    # further smoothing
    s_neg = rt_smoother(s_neg, 100)

    # finding local maxima of the smoothed histogram
    loc_peaks_neg = scipy.signal.find_peaks(s_neg)
    loc_peaks_neg = np.asarray(loc_peaks_neg[0])

    # adding to resolution to find peaks more precisely
    x = np.linspace(min(cen_neg), max(cen_neg), 5 * n_bin)
    loc_peaks_neg = np.round(x[loc_peaks_neg])

    # choosing first "n_peaks" peaks (peaks are sorted in descending order)
    loc_peaks_neg = np.sort(loc_peaks_neg)[::-1]
    if len(loc_peaks_neg) > n_peaks:
        loc_peaks_neg = loc_peaks_neg[0:n_peaks]

    # "max_shift" number of samples are removed from the begining and end
    newSpikeMat = spike_mat[:, max_shift:-max_shift]

    # shifting time with the amount of "max_shift" because first "max_shift" samples are ignored.
    time_shift = np.zeros((n_spike,)) + max_shift

    # indices of neg group
    ind_neg_find = np.nonzero(ind_neg)[0]

    for i in range(len(ind_min_neg)):
        # finding minimum distance between indices of samples minimum and selected histogram peaks,
        # ind_cluster determines index of the final selected peak as alignment point.
        d = abs(np.tile(ind_min_neg[i] + 1, (1, len(loc_peaks_neg))) - loc_peaks_neg)
        ind_cluster = d.argmin()
        min_shift = d[0][ind_cluster]
        # ignore spike shifting if min_shift exceeds maximum allowed shift
        if min_shift > max_spline_align_shift:
            continue

        # calculating n_shift based on found "ind_cluster",
        # then dividing it by r_upsample to achieve shift of the original signal
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
    freq_pos, cen_pos = np.histogram(ind_max_pos + 1, n_bin)
    cen_pos = cen_pos[:-1] + np.diff(cen_pos) / 2

    # cubic spline interpolation of histogram
    f = scipy.interpolate.CubicSpline(cen_pos, freq_pos)
    sample_pos = np.linspace(min(cen_pos), max(cen_pos), 5 * n_bin)
    s_pos = f(sample_pos)

    # further smoothing
    s_pos = rt_smoother(s_pos, 100)

    # finding local maxima of the smoothed histogram
    loc_peaks_pos = scipy.signal.find_peaks(s_pos)
    loc_peaks_pos = np.asarray(loc_peaks_pos[0])

    # adding to resolution to find peaks more precisely
    x_pos = np.linspace(min(cen_pos), max(cen_pos), 5 * n_bin)
    loc_peaks_pos = np.round(x[loc_peaks_pos])

    # choosing first "n_peaks" peaks (peaks are sorted in descending order)
    loc_peaks_pos = np.sort(loc_peaks_pos)[::-1]
    if len(loc_peaks_pos) > n_peaks:
        loc_peaks_pos = loc_peaks_pos[0:n_peaks]

    # indices of pos group
    ind_pos_find = np.nonzero(np.logical_not(ind_neg))[0]
    for i in range(len(ind_max_pos)):
        # finding minimum distance between indices of samples maximum and selected histogram peaks,
        # ind_cluster determines index of the final selected peak as alignment point.
        d = abs(np.tile(ind_max_pos[i] + 1, (1, len(loc_peaks_pos))) - loc_peaks_pos)
        ind_cluster = d.argmin()
        min_shift = d[0][ind_cluster]
        # min_shift, ind_cluster = min(abs(np.repmat(ind_max_pos[i], 1, len(loc_peaks_pos)) - loc_peaks_pos))
        # ignore spike shifting if min_shift exceeds maximum allowed shift
        if min_shift > max_spline_align_shift:
            continue
        # calculating n_shift based on found "ind_cluster",
        # then dividing it by r_upsample to archieve hsift of the original signal

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


# Rt_smoother
def rt_smoother(y, win_length=5):
    win_alpha = 1
    win = scipy.signal.windows.gaussian(win_length, std=win_length / win_alpha)
    win /= np.sum(win)
    conved = scipy.signal.convolve(y, win, mode='same')
    return conved


def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
                 kpsh=False, valley=False, show=False, ax=None):
    """Detect peaks in data based on their amplitude and other features.

    Parameters
    ----------
    x : 1D array_like
        data.
    mph : {None, number}, optional (default = None)
        detect peaks that are greater than minimum peak height.
    mpd : positive integer, optional (default = 1)
        detect peaks that are at least separated by minimum peak distance (in
        number of data).
    threshold : positive number, optional (default = 0)
        detect peaks (valleys) that are greater (smaller) than `threshold`
        in relation to their immediate neighbors.
    edge : {None, 'rising', 'falling', 'both'}, optional (default = 'rising')
        for a flat peak, keep only the rising edge ('rising'), only the
        falling edge ('falling'), both edges ('both'), or don't detect a
        flat peak (None).
    kpsh : bool, optional (default = False)
        keep peaks with same height even if they are closer than `mpd`.
    valley : bool, optional (default = False)
        if True (1), detect valleys (local minima) instead of peaks.
    show : bool, optional (default = False)
        if True (1), plot data in matplotlib figure.
    ax : a matplotlib.axes.Axes instance, optional (default = None).

    Returns
    -------
    ind : 1D array_like
        indeces of the peaks in `x`.

    Notes
    -----
    The detection of valleys instead of peaks is performed internally by simply
    negating the data: `ind_valleys = detect_peaks(-x)`

    The function can handle NaN's

    See this IPython Notebook [1]_.

    References
    ----------
    .. [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectPeaks.ipynb

    """

    x = np.atleast_1d(x).astype('float64')
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
    # find indices of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ['rising', 'both']:
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan - 1, indnan + 1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size - 1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind] - x[ind - 1], x[ind] - x[ind + 1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
                       & (x[ind[i]] > x[ind] if kpsh else True)
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indices by their occurrence
        ind = np.sort(ind[~idel])

    # if show:
    #     if indnan.size:
    #         x[indnan] = np.nan
    #     if valley:
    #         x = -x
    #      _plot(x, mph, mpd, threshold, edge, valley, ax, ind)

    return ind
