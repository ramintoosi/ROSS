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
