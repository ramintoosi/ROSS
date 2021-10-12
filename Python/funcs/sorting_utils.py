import numpy as np
import scipy


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


def dmvt_ls (y, mu, Sigma, landa, nu):
    # This function computes Density/CDF of Skew-T with scale location.
    # y must be a matrix where each row has a multivariate vector of dimension col(y) = p , nrow(y) = sample size. mu, lambda: must be of the vector type of the same dimension equal to ncol(y) = lambda: 1 x p Sigma: Matrix p x p
    nrow = lambda x: x.shape[0]
    ncol = lambda x: x.shape[1]
    n = nrow(y)
    p = ncol(y)
    mahalanobis_d = np.power(cdist(y, np.expand_dims(mu, axis=0), 'mahalanobis',Sigma), 2)
    denst = (gamma((p + nu)/2)/(gamma(nu/2) * np.power(np.pi, p/2))) * np.power(nu, -p/2) * np.power(np.abs(np.linalg.det(Sigma)), (-1/2)) * np.power((1 + mahalanobis_d/nu), (-(p + nu)/2))
    t = scipy.stats.t(nu + p)
    dens = 2 * (denst) * t.cdf(np.sqrt((p + nu)/(mahalanobis_d + nu)) * np.expand_dims(np.sum(np.tile(np.expand_dims(np.linalg.lstsq(matrix_sqrt(Sigma).T, landa.T, rcond=None)[0], axis=0), (n, 1)) * (y - mu), axis=1), axis=1))
    return dens

def d_mixedmvST (y, pi1, mu, Sigma, landa, nu):
    # y: the data matrix
    # pi1: must be of the vector type of dimension g
    # mu: must be of type list with g entries. Each entry in the list must be a vector of dimension p
    # Sigma: must be of type list with g entries. Each entry in the list must be an matrix p x p
    # lambda: must be of type list with g entries. Each entry in the list must be a vector of dimension p
    # nu: a number
    g = np.size(pi1)
    dens = 0
    for j in range(g):
        dens = dens + pi1[j] * dmvt_ls(y, mu[j], Sigma[j], landa[j], nu)   # lnda
    return dens

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
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan-1, indnan+1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size-1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind]-x[ind-1], x[ind]-x[ind+1]]), axis=0)
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