import numpy as np
import scipy.linalg
import sklearn.decomposition as decomp
from scipy.special import gamma
from resources.funcs.fcm import FCM


def t_dist_sorter(alignedSpikeMat, sdd):
    out = dict()
    print('t-sorting started!')

    g_max = sdd.g_max
    g_min = sdd.g_min

    pca = decomp.PCA(15)
    SpikeMat = pca.fit_transform(alignedSpikeMat)
    latent = pca.explained_variance_

    # Typicallity Limit
    u_limit = sdd.u_lim

    # Initialization
    print('-*-' * 20)
    print('Initialization Started...')
    nrow = lambda x: x.shape[0]
    ncol = lambda x: x.shape[1]
    n_feat = ncol(SpikeMat)
    n_spike = nrow(SpikeMat)

    Sigma = np.tile(np.expand_dims(np.eye(n_feat), axis=2), (1, 1, g_max))

    v = sdd.nu
    L_max = -np.inf
    N = sdd.N
    g = g_max
    delta_L_limit = 0.1
    delta_v_limit = 0.1
    delta_L = 100
    delta_v = 100
    max_iter = sdd.max_iter
    print('...Initialization Done!')

    # FCM
    print('-*-' * 20)
    print('FCM started...')
    mu, U, _ = FCM(SpikeMat, g, [2, 20, 1, 0])
    print('...FCM Done!')

    # Estimate starting point for Sigma and Pi from simple clustering method
    # performed before
    print('-*-' * 20)
    print('Estimating Sigma and Pi...')
    rep = np.reshape(np.tile(np.expand_dims(np.arange(g), 1), (1, n_spike)), (g * n_spike, 1))
    rep = np.squeeze(rep)
    rep_data = np.tile(SpikeMat, (g, 1))
    diffs = rep_data - mu[rep, :]
    del rep_data

    U = U.T

    for i in range(g):
        Sigma[:, :, i] = (((np.expand_dims(U[:, i], 1) @ np.ones((1, n_feat))) * diffs[rep == i, :]).T
                          @ diffs[rep == i, :]) / np.sum(U[:, i], axis=0)

    Pi = np.sum(U, axis=0) / np.sum(np.sum(U, axis=0), axis=0)

    L_old = -np.inf
    v_old = v
    Ltt = []

    print('...Estimation Done!')

    # Running clustering algorithm for g in [g_max, ...,g_min]
    print('-*-' * 20)
    print('Clustering Started...')
    while g >= g_min:
        itr = 0
        # EM
        print('#' * 10)
        print('EM Alg. Started...')
        while ((delta_L > delta_L_limit) or (delta_v > delta_v_limit)) and itr < max_iter:
            print('iteration number = ', itr)
            print('g = ', g)
            print('Pi = ', Pi)
            print('#' * 5)
            n_sigma = Sigma.shape[2]
            detSigma = np.zeros((1, n_sigma))
            rep = np.reshape(np.tile(np.expand_dims(np.arange(g), 1), (1, n_spike)), (g * n_spike, 1))
            rep = np.squeeze(rep)
            rep_data = np.tile(SpikeMat, (g, 1))
            diffs = rep_data - mu[rep, :]

            for i in range(n_sigma):
                detSigma[:, i] = 1 / np.sqrt(np.linalg.det(Sigma[:, :, i]))

            M = np.zeros((n_spike, g))
            for i in range(n_sigma):
                M[:, i] = np.real(np.sum(np.power(scipy.linalg.sqrtm(np.linalg.pinv(Sigma[:, :, i])) @
                                                  (diffs[rep == i, :].T), 2), axis=0).T)

            c = gamma((v + n_feat) / 2) / (gamma(v / 2) * np.power(np.pi * v, (n_feat / 2)))
            P = c * np.exp(-(v + n_feat) * np.log(1 + M / v) / 2) @ np.diag(np.squeeze(detSigma))

            # Membership
            num_z = np.tile(np.expand_dims(Pi, axis=0), (n_spike, 1)) * P
            den_z = np.sum(num_z, axis=1)
            z = num_z / np.tile(np.expand_dims(den_z, axis=1), (1, g))

            # Typicallity update
            delta_distance = M.copy()
            u = (n_feat + v) / (delta_distance + v)

            # M-step
            deltaP = 1

            while deltaP > 0.0001:
                gtmp = g
                Pi_old = Pi.copy()
                num_ztmp = np.tile(np.expand_dims(Pi, axis=0), (n_spike, 1)) * P
                den_ztmp = np.sum(num_ztmp, axis=1)
                ztmp = num_ztmp / np.tile(np.expand_dims(den_ztmp, axis=1), (1, gtmp))
                Pi_num = np.sum(ztmp, axis=0) - (N / 2)
                Pi_num[Pi_num < 0] = 0
                Pi = Pi_num / (n_spike - gtmp * N / 2)
                if any(Pi == 0):
                    gtmp = gtmp - np.sum(Pi > 0)
                deltaP = np.linalg.norm(Pi_old - Pi, ord=1)

            Pi = Pi / np.sum(Pi, axis=0)

            # Update mu
            for j in range(g):
                num = np.sum(np.tile(np.expand_dims(z[:, 0], axis=1), n_feat) *
                             np.tile(np.expand_dims(u[:, 0], axis=1), n_feat) * SpikeMat, axis=0)
                mu[j, :] = num / np.sum(z[:, j] * u[:, j], axis=0)

            ZU = z * u
            # Update Sigma
            for j in range(g):
                diffs = SpikeMat - np.ones((n_spike, 1)) @ np.expand_dims(mu[j, :], axis=0)
                Sigma[:, :, j] = ((np.expand_dims(ZU[:, j], axis=1) @ np.ones((1, n_feat))) * diffs).T @ diffs / np.sum(
                    ZU[:, j], axis=0)

            # Update v
            a_yt = z * (scipy.special.psi((n_feat + v) / 2) + np.log(2 / (delta_distance + v)) - u)
            b_yt = np.expand_dims(np.sum(z, axis=0), axis=0)
            yt = np.dot(a_yt, np.linalg.pinv(b_yt))
            y = np.real(-np.sum(yt, axis=0))
            v = 2 / (y + np.log(y) - 1) + 0.0416 * (
                        1 + scipy.special.erf(0.6594 * np.log(2.1971 / (y + np.log(y) - 1))))
            v = v[0]

            # Probability (t-dist)
            n_sigma = Sigma.shape[2]
            detSigma = np.zeros((1, n_sigma))
            rep = np.reshape(np.tile(np.expand_dims(np.arange(g), 1), (1, n_spike)), (g * n_spike, 1))
            rep = np.squeeze(rep)
            rep_data = np.tile(SpikeMat, (g, 1))
            diffs = rep_data - mu[rep, :]

            for i in range(n_sigma):
                detSigma[:, i] = 1 / np.sqrt(np.linalg.det(Sigma[:, :, i]))

            M = np.zeros((n_spike, g))
            for i in range(n_sigma):
                M[:, i] = np.real(np.sum(np.power(scipy.linalg.sqrtm(np.linalg.pinv(Sigma[:, :, i])) @
                                                  (diffs[rep == i, :].T), 2), axis=0).T)

            c = gamma((v + n_feat) / 2) / (gamma(v / 2) * np.power(np.pi * v, (n_feat / 2)))
            P = c * np.exp(-(v + n_feat) * np.log(1 + M / v) / 2) @ np.diag(np.squeeze(detSigma))

            # Update L
            min_mess_len_criterion = N / 2 * np.sum(
                np.log(n_feat * Pi / 12) + 0.5 * g * np.log(n_feat / 12) + g * (N + 1) / 2, axis=0)
            l_log = np.sum(np.log(np.sum(np.tile(np.expand_dims(Pi, axis=0), (n_spike, 1)) * Pi, axis=1)), axis=0)
            L = l_log - min_mess_len_criterion

            # Convergence criteria
            delta_L = np.abs(L - L_old)
            delta_v = np.abs(v - v_old)

            L_old = L
            v_old = v

            Ltt.append(L)

            itr += 1
            if itr == max_iter:
                raise Exception('CONVERGENCE FAILED FOR delta_L')

            indx_remove = np.squeeze((Pi == 0))
            mu = mu[np.logical_not(indx_remove)]
            Sigma = Sigma[:, :, indx_remove == False]
            Pi = Pi[indx_remove == False]
            # Pi = np.array([d for (d, remove) in zip(Pi, indx_remove) if not remove])
            z = z[:, indx_remove == False]
            # z = np.array([d for (d, remove) in zip(z, indx_remove) if not remove])
            u = u[:, indx_remove == False]
            # u = np.array([d for (d, remove) in zip(u, indx_remove) if not remove])
            P = P[:, indx_remove == False]
            # P = np.array([d for (d, remove) in zip(P, indx_remove) if not remove])
            delta_distance = delta_distance[:, indx_remove == False]
            # delta_distance = np.array([d for (d, remove) in zip(delta_distance, indx_remove) if not remove])
            g = g - np.sum(indx_remove, axis=0)
            g = g

            print('Sigma Shape : ', Sigma.shape)
            print('Pi shape : ', Pi.shape)
            print('z shape : ', z.shape)
            print('u shape : ', u.shape)
            print('P shape : ', P.shape)
            print('delta distance shape : ', delta_distance.shape)

        print('...Em Done!')

        if L > L_max:
            L_max = L
            out['cluster_index'] = np.argmax(z, axis=1)

            out['set.u'] = u
        else:
            break

        # Set smallest component to zero
        ind_min = np.argmin(Pi)
        Pi[ind_min] = 0
        # Purge components where Pi = 0
        indx_remove = np.squeeze((Pi == 0))
        mu = mu[np.logical_not(indx_remove)]
        Sigma = Sigma[:, :, indx_remove == False]
        Pi = np.array([d for (d, remove) in zip(Pi, indx_remove) if not remove])
        z = np.array([d for (d, remove) in zip(z, indx_remove) if not remove])
        u = np.array([d for (d, remove) in zip(u, indx_remove) if not remove])
        P = np.array([d for (d, remove) in zip(P, indx_remove) if not remove])
        delta_distance = np.array([d for (d, remove) in zip(delta_distance, indx_remove) if not remove])
        g = g - 1

    print('clusters', out['cluster_index'])

    return out['cluster_index']



