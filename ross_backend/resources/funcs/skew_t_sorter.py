import numpy as np
import sklearn.decomposition as decomp
from scipy import stats
from scipy import optimize
from scipy.spatial.distance import cdist
from scipy.special import gamma, digamma, erf
from resources.funcs.fcm import FCM
from resources.funcs.sort_utils import (
    matrix_sqrt,
    dmvt_ls,
    d_mixedmvST,
    matlab_round,
    statistical_filter,
    spike_alignment,
    rt_smoother,
    detect_peaks,
)


def skew_t_sorter(alignedSpikeMat, sdd, REM=np.array([]), INPCA=False):
    out = dict()

    # seed = sdd.sort_random_seed
    g_max = sdd.g_max
    g_min = sdd.g_min
    n_pca = 15
    print('n pca : ', n_pca)

    # returns principal component scores in SpikeMat and the principal component variances in latent
    print('*' * 20)
    print('PCA started...')
    pca = decomp.PCA(n_pca)
    SpikeMat = pca.fit_transform(alignedSpikeMat)
    latent = pca.explained_variance_

    # choosing number of pca coefficients shuch that 0.95 of variance is covered
    h = np.nonzero(np.cumsum(latent) / sum(latent) > 0.95)
    h = h[0][0]

    # limiting number of pca coefficients(h) by n_pca_max
    if h > sdd.PCA_num:
        h = sdd.PCA_num
    # test
    elif h < 2:
        h = 2

    # considering firs "h" pca scores
    SpikeMat = SpikeMat[:, :h]
    print('h in PCA = ', h)
    print('...PCA Done!')

    # initial value for nu parameter
    nu = sdd.nu
    L_max = -np.inf

    g = g_max  # j

    nrow = lambda x: x.shape[0]
    ncol = lambda x: x.shape[1]

    n_feat = ncol(SpikeMat)
    n_spike = nrow(SpikeMat)

    # initialization

    # running FCM on SpikeMat. initial value for mu is considered cluster
    # centers returned from fcm function. this step is done only for first g (g_max)
    print('*' * 20)
    print('FCM stared...')
    mu, U, _ = FCM(SpikeMat, g, [2, 20, 1, 0])
    clusters = np.argmax(U, axis=0)
    cls = []
    print(clusters)
    for i in range(9):
        cls.append(np.sum(clusters == i))
    print('Clusters : ', cls)
    print('mu shape = ', mu.shape)
    print('U sha', U.shape)

    # Estimate starting point for Sigma and Pi from simple clustering method
    # performed before
    rep = np.reshape(np.tile(np.expand_dims(np.arange(g), 1), (1, n_spike)), (g * n_spike, 1))
    rep = np.squeeze(rep)
    rep_data = np.tile(SpikeMat, (g, 1))
    diffs = rep_data - mu[rep, :]
    del rep_data

    idx = np.argmax(U, axis=0)
    U = U.T

    shape = []
    Sigma = []

    for j in range(g):
        shape.append(np.sign(np.sum(
            np.power((SpikeMat[idx == j, :] - np.tile(mu[j],
                                                      (nrow(SpikeMat[idx == j]), 1))), 3), axis=0)))
        Sigma.append((((np.expand_dims(U[:, j], 1) @ np.ones([1, n_feat])) * diffs[rep == j, :]).T
                      @ diffs[rep == j, :]) / np.sum(U[:, j]))

    pii = np.sum(U, axis=0) / np.sum(np.sum(U, axis=0))
    pii = np.expand_dims(pii, axis=1)

    print('*' * 20)
    print('Clustering Started...')
    # running clustering algorithm for g in [g_max, ...,g_min]
    while g >= g_min:
        delta = []
        Delta = []
        Gama = []
        for k in range(g):
            delta.append(shape[k] / np.sqrt(1 + shape[k] @ shape[k].T))
            Delta.append(matrix_sqrt(Sigma[k]) @ (delta[k]).T)
            Gama.append(Sigma[k] - np.dot(np.expand_dims(Delta[k], axis=1), np.expand_dims(Delta[k], axis=0)))

        Delta_old = Delta.copy()
        criterio = 1
        count = 0
        lkante = 1

        # starting EM algorithm to find optimum set of parameters. EM algorithm
        # ends when maximum change among all parameters is smaller than a
        # error, or when reaching "max_iter".
        print('-' * 15)
        print('EM started...')
        # Changing iter manualy
        # count <= sdd.max_iter
        while ((criterio > sdd.error) and (count <= 500)):
            count = count + 1;
            tal = np.zeros([n_spike, g])
            S1 = np.zeros([n_spike, g])
            S2 = np.zeros([n_spike, g])
            S3 = np.zeros([n_spike, g])

            for j in range(g):
                print('-.-' * 10)
                print('j = ', j)
                print('Expectation started...')
                # Expectation
                Dif = SpikeMat - np.tile(mu[j], (n_spike, 1))
                Mtij2 = 1 / (1 + Delta[j] @ (np.linalg.inv(Gama[j]) @ Delta[j].T))
                Mtij = np.sqrt(Mtij2)
                mtuij = np.sum(np.tile(Mtij2 * (Delta[j] @ np.linalg.inv(Gama[j])), (n_spike, 1)) * Dif, axis=1)

                A = mtuij / Mtij
                A = np.expand_dims(A, axis=1)

                dj = np.power(cdist(SpikeMat, np.expand_dims(mu[j], axis=0),
                                    metric='mahalanobis', VI=np.linalg.inv(Sigma[j])), 2)
                E = (2 * np.power(nu, nu / 2) * gamma((n_feat + nu + 1) / 2) * np.power(dj + nu + np.power(A, 2),
                                                                                        -((n_feat + nu + 1) / 2))) / (
                                gamma(nu / 2) * np.power(np.sqrt(np.pi), (n_feat + 1)) * np.sqrt(
                            np.linalg.det(Sigma[j])) * dmvt_ls(SpikeMat, mu[j], Sigma[j], shape[j], nu))
                t = stats.t(n_feat + nu + 2)
                u = ((4 * np.power(nu, nu / 2) * gamma((n_feat + nu + 2) / 2) * np.power((dj + nu),
                                                                                         (-(n_feat + nu + 2) / 2))) / (
                                 gamma(nu / 2) * np.sqrt(np.power(np.pi, n_feat)) * np.sqrt(
                             np.linalg.det(Sigma[j])) * dmvt_ls(SpikeMat, mu[j], Sigma[j], shape[j], nu))) * t.cdf(
                    np.sqrt((n_feat + nu + 2) / (dj + nu)) * A)
                d1 = dmvt_ls(SpikeMat, mu[j], Sigma[j], shape[j], nu)
                if np.sum(d1 == 0):
                    intmax = 2147483647
                    d1[d1 == 0] = 1 / intmax

                d2 = d_mixedmvST(SpikeMat, pii, mu, Sigma, shape, nu)
                if np.sum(d2 == 0):
                    intmax = 2147483647
                    d2[d2 == 0] = 1 / intmax

                tal[:, j] = np.squeeze(d1 * pii[j] / d2)
                S1[:, j] = np.squeeze(np.expand_dims(tal[:, j], axis=1) * u)
                S2[:, j] = np.squeeze(np.expand_dims(tal[:, j], axis=1) *
                                      (np.expand_dims(mtuij, axis=1) * u + Mtij * E))
                S3[:, j] = np.squeeze(np.expand_dims(tal[:, j], axis=1) *
                                      (np.power(np.expand_dims(mtuij, axis=1), 2) * u + Mtij2 + Mtij * np.expand_dims(
                                          mtuij, axis=1) * E))

                print('...Expectation Done!')
                # Maximization
                print('-' * 10)
                print('Maximization Started...')
                pii[j] = (1 / n_spike) * sum(tal[:, j])
                mu[j] = (np.sum(
                    np.expand_dims(S1[:, j], axis=1) * SpikeMat - np.expand_dims(S2[:, j], axis=1) * np.tile(
                        Delta_old[j], (n_spike, 1)), axis=0)) / np.sum(S1[:, j])
                Dif = SpikeMat - mu[j]
                Delta[j] = np.sum(np.expand_dims(S2[:, j], axis=1) * Dif, axis=0) / np.sum(S3[:, j])

                sum2 = np.zeros((n_feat, n_feat))
                for i in range(n_spike):
                    sum2 = sum2 + S1[i, j] * (
                                np.expand_dims(SpikeMat[i, :] - mu[j], axis=1) @ np.expand_dims(SpikeMat[i, :] - mu[j],
                                                                                                axis=0)) - S2[i, j] * (
                                       np.expand_dims(Delta[j], axis=1) @ np.expand_dims(SpikeMat[i, :] - mu[j],
                                                                                         axis=0)) - S2[i, j] * (
                                       np.expand_dims(SpikeMat[i, :] - mu[j], axis=1) @ np.expand_dims(Delta[j],
                                                                                                       axis=0)) + S3[
                               i, j] * (np.expand_dims(Delta[j], axis=1) @ np.expand_dims(Delta[j], axis=0))

                Gama[j] = sum2 / np.sum(tal[:, j])
                print('...Maximization Done!')

            logvero_ST = lambda nu: -1 * np.sum(np.log(d_mixedmvST(SpikeMat, pii, mu, Sigma, shape, nu)), axis=0)
            nu = optimize.fminbound(logvero_ST, 0, 100, xtol=0.000001)
            # pii = pii / np.sum(pii)
            pii[g - 1] = 1 - (sum(pii) - pii[g - 1])
            zero_pos = pii == 0
            pii[zero_pos] = 1e-10
            pii[pii == max(pii)] = max(pii) - sum(pii[zero_pos])
            lk = np.sum(np.log(d_mixedmvST(SpikeMat, pii, mu, Sigma, shape, nu)), axis=0)[0]
            criterio = np.abs((lk / lkante) - 1)
            lkante = lk.copy()
            Delta_old = Delta.copy()
            print('pii = ', pii)

        print('...EM Done!')

        cl = np.argmax(tal, axis=1)
        print('Clusters after EM: ')
        for i in range(g):
            print(SpikeMat[cl == i, :].shape)

        L = 0
        for j in range(g):
            L = L + np.sum(np.log(pii[j] * dmvt_ls(SpikeMat[cl == j, :], mu[j], Sigma[j], shape[j], nu)), axis=0)
        # for first g(g_max) L_max has been -inf, for next iterations (g_max - 1, ..., g_min) L is compared
        # to largest L between all previous iters.
        if L > L_max:
            L_max = L
            # assigning cluster indices to each spike. if REM is given the outliers must be assigned to cluster 255.
            out['cluster_index'] = np.argmax(tal, axis=1)
        else:
            print('...Clustering Done!')
            break
        # set smallest component to zero
        m_pii = min(pii)
        indx_remove = np.squeeze((pii == m_pii) | (pii < 0.01))
        # Purge components
        mu = mu[np.logical_not(indx_remove)]
        # Sigma = Sigma[np.logical_not(indx_remove)]
        Sigma = [d for (d, remove) in zip(Sigma, indx_remove) if not remove]
        pii = pii[np.logical_not(indx_remove)]
        # shape = shape[np.logical_not(indx_remove)]
        shape = [d for (d, remove) in zip(shape, indx_remove) if not remove]
        g = g - sum(indx_remove)
        g = g

    print('*' * 20)
    print('...Clustering Done!')
    print('Clusters : ', out['cluster_index'])
    print("out : ", out)
    return out['cluster_index']

