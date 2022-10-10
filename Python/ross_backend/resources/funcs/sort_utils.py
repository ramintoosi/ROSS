import numpy as np
import scipy
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
    mahalanobis_d = np.power(cdist(y, np.expand_dims(mu, axis=0), metric = 'mahalanobis',VI=np.linalg.inv(Sigma)), 2)
    denst = (gamma((p + nu)/2)/(gamma(nu/2) * np.power(np.pi, p/2))) * np.power(nu, -p/2) * np.power(np.abs(np.linalg.det(Sigma)), (-1/2)) * np.power((1 + mahalanobis_d/nu), (-(p + nu)/2))
    t = scipy.stats.t(nu + p)
    dens = 2 * (denst) * t.cdf(np.sqrt((p + nu)/(mahalanobis_d + nu)) * np.expand_dims(np.sum(np.tile(np.expand_dims(np.linalg.lstsq(matrix_sqrt(Sigma).T, landa.T, rcond=None)[0], axis=0), (n, 1)) * (y - mu), axis=1), axis=1))
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
        dens = dens + pi1[j] * dmvt_ls(y, mu[j], Sigma[j], landa[j], nu)   # lnda
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
