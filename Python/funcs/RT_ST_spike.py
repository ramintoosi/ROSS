import numpy as np
import sklearn.decomposition as decomp
import math
from fcmeans import FCM
from resources.funcs.sort_utils import *
from scipy import linalg
from scipy.spatial.distance import cdist
from scipy.special import gamma, digamma, erf

def skew_t_sorter(SpikeMat, config, REM=[], INPCA=True):
# This function sorts detected spikes using mixtures of multivariate ske-t distributions. SpikeMat is matrix of detected spikes, config is settings.
# REM contains spikes after statistical filtering. INPCA is a logical vwhich determines whether considering noise spikes in computing pca or not.

    out = dict()
    # removing REM if it is given in wrong format
    if not np.array_equal(REM, REM.astype(bool)) or len(REM) != SpikeMat.shape[0]:
        REM = []

    g_max = config.g_max
    g_min = config.g_min

    # removing outliers using given REM
    if not INPCA and not REM.size == 0:
        SpikeMat = SpikeMat[np.logical_not(REM), :]

    # returns principal component scores in SpikeMat and the principal component variances in latent
    pca = decomp.PCA()
    SpikeMat = pca.fit_transform(SpikeMat)
    latent = pca.explained_variance_

    # choosing number of pca coefficients such that 0.95 of variance is covered
    h = np.nonzero(np.cumsum(latent) / sum(latent) > 0.95)
    h = h[0][0] + 1

    # limiting number of pca coefficients(h) by n_pca_max
    if h > config.PCA_num:
        h = config.PCA_num

    # considering firs "h" pca scores
    SpikeMat = SpikeMat[:, :h]

    if not REM.size == 0 and INPCA:
        SpikeMat = SpikeMat[np.logical_not(REM), :]

    # initial value for nu parameter
    nu = config.nu
    L_max = -math.inf

    g = g_max
    nrow = lambda x: x.shape[0]
    ncol = lambda x: x.shape[1]

    n_feat = ncol(SpikeMat)
    n_spike = nrow(SpikeMat)

    # initialization

    # simple clustering method
    # running FCM on SpikeMat. initial value for mu is considered cluster centers returned from fcm function. this step
    # is done only for first g(g_max)
    fcm = FCM(n_clusters=g, max_iter=20)
    fcm.fit(SpikeMat)
    mu = fcm.centers
    U = fcm.u
    mu = np.asarray(mu)
    mu = mu.copy()
    U = np.asarray(U)

    # Estimate staring point for Sigma and Pi from simple clustering method peformed before
    rep = np.reshape(np.tile(np.expand_dims(np.arange(g), 1), (1, n_spike)), (g * n_spike, 1))
    rep = np.squeeze(rep)
    rep_data = np.tile(SpikeMat, (g, 1))
    diffs = rep_data - mu[rep, :]  # X - mu
    diffs = np.asarray(diffs)
    del rep_data

    idx = np.argmax(U, axis=1)

    shape = []
    Sigma = []
    for j in range(g):
        shape.append(np.sign(np.sum(np.power((SpikeMat[idx == j, :] - np.tile(mu[j], ((SpikeMat[idx == j, :]).shape[0], 1))), 3), axis=0)))
        Sigma.append((np.dot(np.transpose((np.expand_dims(U[:, j], 1) * np.ones((1, n_feat))) * diffs[rep == j]), diffs[rep == j, :])) / sum(U[:, j]))

    pii = sum(U) / sum(sum(U))

    delta = []
    Delta = []
    Gama = []

    # running clustering algorithm for g in [g_max, ...,  g_min]
    while (g >= g_min):
        for k in range(g):
            delta.append(shape[k] / np.sqrt(1 + np.dot(shape[k], np.transpose(shape[k]))))
            Delta.append(np.transpose(np.dot(matrix_sqrt(Sigma[k]), np.transpose(delta[k]))))
            Gama.append(Sigma[k] - np.dot(np.expand_dims(Delta[k], axis=1), np.expand_dims(Delta[k], axis=0)))

        Delta_old = Delta
        criterio = 1
        count = 0
        lkante = 1

        # starting EM algorithm to find optimum set of parameters. EM algorithm ends when maximum change among all
        # parameters is smaller than an error. or when reaching "max_iter".

        while (criterio > config.error) and (count <= config.max_iter):
            count = count + 1
            tal = np.zeros((n_spike, g))
            S1 = np.zeros((n_spike, g))
            S2 = np.zeros((n_spike, g))
            S3 = np.zeros((n_spike, g))
            for j in range(g):
                # Expectation
                Dif = SpikeMat - np.tile(mu[j], (n_spike, 1))
                Mtij2 = 1 / (1 + np.dot(np.expand_dims(Delta[j], axis=0), (np.linalg.lstsq(Gama[j], np.expand_dims(Delta[j], axis=1), rcond=None)[0])))
                Mtij = np.sqrt(Mtij2)
                mtuij = np.sum(np.tile(Mtij2 * (np.linalg.lstsq(np.transpose(Gama[j]), np.expand_dims(Delta[j], axis=1), rcond=None)[0].T), (n_spike, 1)) * Dif, axis=1)
                A = mtuij / Mtij
                dj = np.power((cdist(SpikeMat, np.expand_dims(mu[j], axis=0), 'mahalanobis', np.linalg.inv(Sigma[j]))), 2)
                E = (2 * np.power(nu, nu / 2) * gamma((n_feat + nu + 1) / 2) * np.power(((dj + nu + np.power(A.T, 2))), (-(n_feat + nu + 1) / 2))) / (gamma(nu / 2) * np.power((np.sqrt(np.pi)), (n_feat + 1)) * np.sqrt(np.linalg.det(Sigma[j]))*dmvt_ls(SpikeMat, mu[j], Sigma[j], shape[j], nu))
                t = scipy.stats.t(n_feat + nu + 2)
                u = ((4 * np.power(nu, nu / 2) * gamma((n_feat + nu + 2) / 2) * np.power((dj + nu), (-(n_feat + nu + 2) / 2))) / (gamma(nu / 2) * np.sqrt(np.power(np.pi, n_feat)) * np.sqrt(np.linalg.det(Sigma[j])) * dmvt_ls(SpikeMat, mu[j], Sigma[j], shape[j], nu)))*t.cdf(np.sqrt((n_feat + nu + 2) / (dj + nu)) * A.T)

                d1 = dmvt_ls(SpikeMat, mu[j], Sigma[j], shape[j], nu)
                if sum(d1 == 0):
                    intmax = 2147483647
                    d1[d1 == 0] = 1 / intmax
                d2 = d_mixedmvST(SpikeMat, pii, mu, Sigma, shape, nu)
                if sum(d2 == 0):
                    intmax = 2147483647
                    d2[d2 == 0] = 1 / intmax

                tal[:, j] = np.squeeze(d1 * pii[j] / d2)
                S1[:, j] = tal[:, j] * np.squeeze(u)
                S2[:, j] = tal[:, j] * (mtuij * np.squeeze(u) + Mtij * np.squeeze(E))
                S3[:, j] = tal[:, j] * (np.power(mtuij, 2) * np.squeeze(u) + Mtij2 + Mtij * mtuij *np.squeeze(E))
                # maximization
                pii[j] = (1 / n_spike) * sum(tal[:, j])
                mu[j] = np.sum(np.expand_dims(S1[:, j], axis=1) * SpikeMat - np.expand_dims(S2[:, j], axis=1) * np.tile(Delta_old[j], (n_spike, 1)), axis=0) / sum(S1[:, j])
                Dif = SpikeMat - mu[j]
                Delta[j] = np.sum(np.expand_dims(S2[:, j], axis=1) * Dif, axis=0) / sum(S3[:, j])
                sum2 = np.zeros((n_feat, n_feat))
                for i in range(n_spike):
                    sum2 = sum2 + (S1[i, j] * (np.transpose(SpikeMat[i, :] - mu[j])) * (SpikeMat[i, :] - mu[j]) - S2[i, j] * (np.transpose(Delta[j]) * (SpikeMat[i, :] - mu[j])) - S2[i, j] * (np.transpose(SpikeMat[i, :] - mu[j]) * (Delta[j])) + S3[i, j] * (np.transpose(Delta[j]) * (Delta[j])))
                Gama[j] = sum2 / sum(tal[:, j])
                #Sigma[j] = Gama[j] + np.dot(np.expand_dims(Delta[j], axis=1), np.expand_dims(Delta[j], axis=0))
                #shape[j] = (np.linalg.lstsq(matrix_sqrt(Sigma[j]).T, np.expand_dims(Delta[j], axis=1), rcond=None)[0].T) / np.sqrt(np.abs(1 - np.dot(np.linalg.lstsq(Sigma[j].T, np.expand_dims(Delta[j], axis=1), rcond=None)[0].T, np.expand_dims(Delta[j], axis=1))))
                #shape[j] = np.squeeze(shape[j])
            logvero_ST = lambda nu: -1 * sum(np.log(d_mixedmvST(SpikeMat, pii, mu, Sigma, shape, nu)))

            nu = scipy.optimize.fminbound(logvero_ST, 0, 100, xtol=0.000001)
            pii[g-1] = 1 - (sum(pii) - pii[g-1])

            zero_pos = pii == 0
            pii[zero_pos] = 1e-10
            pii[pii == max(pii)] = max(pii) - sum(pii[zero_pos])
            lk = sum(np.log(d_mixedmvST(SpikeMat, pii, mu, Sigma, shape, nu)))
            criterio = abs((lk / lkante) - 1)
            lkante = lk
            Delta_old = Delta
            # computing log likelihood function as a criterion to find the best g.
            cl = np.argmax(tal, axis=1)
            L = 0
            for j in range(g):
                L = L + sum(np.log(pii[j] * dmvt_ls(SpikeMat[cl == j, :], mu[j], Sigma[j], shape[j], nu)))
            # for first g(g_max) L_max has been -inf, for next iterations (g_max - 1, ..., g_min) L is compared
            # to largest L between all previous iters.
            if L > L_max:
                L_max = L
                # assigning cluster indices to each spike. if REM is given the outliers must be assigned to cluster 255.
                if REM.size == 0:
                    out['cluster_index'] = np.argmax(tal, axis=1)
                else:
                    c_i = np.argmax(tal, axis=1)
                    cluster_index = np.zeros((len(REM), 1))
                    cluster_index[np.logical_not(REM)] = np.expand_dims(c_i, axis=1)
                    cluster_index[REM] = 255  # removed
                    out['cluster_index'] = cluster_index
            else:
                break
        # set smallest component to zero
        m_pii = min(pii)
        indx_remove = (pii == m_pii) | (pii < 0.01)
        # Purge components
        mu = mu[np.logical_not(indx_remove)]
        #Sigma = Sigma[np.logical_not(indx_remove)]
        Sigma = [d for (d, remove) in zip(Sigma, indx_remove) if not remove]
        pii = pii[np.logical_not(indx_remove)]
        #shape = shape[np.logical_not(indx_remove)]
        shape = [d for (d, remove) in zip(shape, indx_remove) if not remove]

        g = g - sum(indx_remove)

    return out