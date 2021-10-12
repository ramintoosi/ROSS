from models.data import DetectResultModel
from models.config import ConfigSortModel
import io
import numpy as np
from scipy import linalg
from scipy.special import gamma, digamma, erf
import sklearn.decomposition as decomp
from fcmeans import FCM
from resources.funcs.sort_utils import *
from resources.funcs.skew_t_sorter import *

import math

def startSorting(user_id):
    detect_result = DetectResultModel.find_by_user_id(user_id)
    if not detect_result:
        raise Exception("No detection result exists.")

    if not detect_result.data:
        raise Exception("No detection result exists.")



    config = ConfigSortModel.find_by_user_id(user_id)
    if not config:
        raise Exception("No sorting config exists.")

    b = io.BytesIO()
    b.write(detect_result.data)
    b.seek(0)

    d = np.load(b, allow_pickle=True)

    spike_mat = d['spike_mat']
    spike_time = d['spike_time']


    if config.alignment:
        spike_mat, spike_time = spikeAlignment(spike_mat, spike_time, config)

    if config.filtering:
        REM = spikeFiltering(spike_mat, config)
    print(config.sorting_type)
    if config.sorting_type == 't dist':
        optimal_set = t_dist_sorter(spike_mat, config, REM, False)
    elif config.sorting_type == 'skew-t dist':
        optimal_set = skew_t_sorter(spike_mat, config, REM, False)


    return spike_mat, spike_time


def t_dist_sorter(SpikeMat, config, REM=[], INPCA=True):
# this function sorts detected spikes according to the following paper: Robust, automatic spike sorting using mixtures
# of multivariate t-distributions. spike_mat is matrix of detected spikes, config contains settings, REM contains
# spikes after statistical filtering. INPCA is a logical value which determines whether considering noise spikes in
# computing PCA or not.

    optimal_set = dict()
    # removing REM if it is given in wrong format
    if not np.array_equal(REM, REM.astype(bool)) or len(REM) != SpikeMat.shape[0]:
        REM = []

    g_max = config.g_max
    g_min = config.g_min
    # removing outliers using given REM

    if not INPCA and not REM.size == 0:
        SpikeMat = SpikeMat[np.logical_not(REM), :]

    if SpikeMat.size == 0:
        optimal_set = dict()
        return optimal_set

    pca = decomp.PCA(n_components=config.PCA_num)
    SpikeMat = pca.fit_transform(SpikeMat)

    if not REM.size == 0 and INPCA:
        SpikeMat = SpikeMat[np.logical_not(REM), :]

    # typicallity limit
    u_limit = config.u_lim
    # Initialization
    n_spike = SpikeMat.shape[0]  # i
    n_feat = SpikeMat.shape[1]  # p in paper
    Sigma = np.tile(np.expand_dims(np.eye(n_feat), 2), (1, 1, g_max))
    v = config.nu
    L_max = -math.inf
    # Theoreticaally: N = p(p + 1) / 2 + p but in the paper it is determined emprically
    N = config.N
    g = g_max

    delta_L_limit = 0.1
    delta_v_limit = 0.1

    delta_L = 100
    delta_v = 100

    max_iter = config.max_iter
    # simple clustering method to determine centers
    # running FCM on SpikeMat.initial value for mu is considered cluster centers returned from fcm function. this step
    # is done only for first g(g_max)

    fcm = FCM(n_clusters=g, max_iter=20)#, error=1)  # default for error is 1e-5
    fcm.fit(SpikeMat)
    mu = fcm.centers
    U = fcm.u
    mu = np.asarray(mu)
    mu = mu.copy()
    # [mu, U] = FCM(SpikeMat, g, [2, 20, 1, 0])

    # Estimate starting point for Sigma and Pi from simple clustering method performed before
    rep = np.reshape(np.tile(np.expand_dims(np.arange(g), 1), (1, n_spike)), (g * n_spike, 1))
    rep = np.squeeze(rep)
    rep_data = np.tile(SpikeMat, (g, 1))
    diffs = rep_data - mu[rep, :]  # X - mu
    diffs = np.asarray(diffs)
    del rep_data

    for i in range(g):
        Sigma[:, :, i] = (np.dot(np.transpose((np.expand_dims(U[:, i], 1) * np.ones((1, n_feat))) * diffs[rep == i]), diffs[rep == i, :])) / sum(U[:, i])

    Pi = sum(U) / sum(sum(U))
    L_old = -math.inf
    v_old = v
    Ltt = []
    # running clustering algorithm for g in [g_max, ...,g_min]
    while (g >= g_min):
        iter = 1
        # starting EM algorithm to find optimum set of parameters. EM algorithm ends when maximum change along all
        # parameters is smaller than a threshold or when reaching "max_iter".
        while ((delta_L > delta_L_limit or delta_v > delta_v_limit) and iter < max_iter):
            n_sigma = Sigma.shape[2]  # number of sigma
            detSigma = np.zeros((1, n_sigma))
            rep = np.reshape(np.tile(np.expand_dims(np.arange(g), 1), (1, n_spike)), (g * n_spike, 1))
            rep = np.squeeze(rep)
            rep_data = np.tile(SpikeMat, (g, 1))
            diffs = rep_data - mu[rep, :]  # Distances to cluster center
            diffs = np.asarray(diffs)
            for i in range(n_sigma):
                detSigma[0, i] = 1 / np.sqrt(linalg.det(Sigma[:, :, i]))
            M = np.zeros((n_spike, g))
            for i in range(n_sigma):
                M[:, i] = np.real(np.sum(np.transpose(np.power((np.dot(matrix_sqrt(linalg.pinv(Sigma[:, :, i])), (np.transpose(diffs[rep == i, :])))), 2)), axis=1))  # Mahalanobis distances
            c = gamma((v + n_feat) / 2) / (gamma(v / 2) * np.power((np.pi * v), (n_feat / 2)))
            P = c * np.dot(np.exp(-(v + n_feat) * np.log(1 + M / v) / 2), np.diag(np.squeeze(detSigma)))  # probabilities
            # membership
            num_z = np.tile(Pi, (n_spike, 1)) * P
            den_z = np.sum(num_z, axis=1)
            z = num_z / np.tile(np.expand_dims(den_z, 1), (1, g))
            # typicallity update
            delta_distance = M
            u = (n_feat + v) / (delta_distance + v)
            # M - Step
            deltaP = 1
            while (deltaP > 1e-4):
                gtmp = g
                Pi_old = Pi
                num_ztmp = np.tile(Pi, (n_spike, 1)) * P
                den_ztmp = np.sum(num_ztmp, axis=1)
                ztmp = num_ztmp / np.tile(np.expand_dims(den_ztmp, axis=1), (1, gtmp))
                Pi_num = (np.sum(ztmp, axis=0) - N / 2)  # Eq 7
                Pi_num[Pi_num < 0] = 0
                Pi = Pi_num / (n_spike - gtmp * N / 2)
                if any(Pi == 0):
                    gtmp = gtmp - np.sum(Pi > 0)
                deltaP = np.linalg.norm(Pi_old - Pi, ord=1)
            Pi = Pi / sum(Pi)  # normalize
            # update mu, sigma Eq8
            for j in range(g):
                # update mu
                num = sum((np.tile(np.expand_dims(z[:, j], axis=1), (1, n_feat)) * np.tile(np.expand_dims(u[:, j], axis=1), (1, n_feat)) * SpikeMat))
                mu[j, :] = num / sum(z[:, j] * u[:, j])
            # update Sigma
            ZU = z * u
            for j in range(g):
                diffs = SpikeMat - np.ones((n_spike, 1)) * mu[j,:]
                Sigma[:, :, j] = (np.dot(np.transpose((np.expand_dims(ZU[:, j], axis=1) * np.ones((1, n_feat))) * diffs), diffs))/sum(ZU[:, j])
            # update v Eq 10 Eq 11
            a = z * (digamma((n_feat + v) / 2) + np.log(2 / (delta_distance + v)) - u)
            b = np.expand_dims(sum(z), axis=0)
            yt = np.linalg.lstsq(b.T, a.T, rcond=None)[0].T
            y = np.real(-sum(np.squeeze(yt)))
            v = 2 / (y + np.log(y) - 1) + 0.0416 * (1 + erf(0.6594 * np.log(2.1971 / (y + np.log(y) - 1))))
            # Probability(t - dist)
            n_sigma = Sigma.shape[2]
            detSigma = np.zeros((1, n_sigma))
            rep = np.reshape(np.tile(np.expand_dims(np.arange(g), 1), (1, n_spike)), (g * n_spike, 1))
            rep = np.squeeze(rep)
            rep_data = np.tile(SpikeMat, (g, 1))
            diffs = rep_data - mu[rep, :]  # Distances to cluster center
            for i in range(n_sigma):
                detSigma[0, i] = 1 / np.sqrt(np.linalg.det(Sigma[:, :, i]))
            M = np.zeros((n_spike, g))
            for i in range(n_sigma):
                M[:, i] = sum((np.power((np.dot(matrix_sqrt(linalg.pinv(Sigma[:, :, i])), (np.transpose(diffs[rep == i, :])))), 2)))  # Mahalanobis distances
            c = gamma((v + n_feat) / 2) / (gamma(v / 2) * np.power((np.pi * v), (n_feat / 2)))
            P = c * np.dot(np.exp(-(v + n_feat) * np.log(1 + M / v) / 2), np.diag(np.squeeze(detSigma)))  # probabilities

            # update L Eq 5
            min_mess_len_criterion = N / 2 * sum(np.log(n_feat * Pi / 12) + 0.5 * g * np.log(n_feat / 12) + g * (N + 1) / 2)
            l_log = np.sum(np.log(np.sum(np.tile(np.expand_dims(Pi, axis=0), (n_spike, 1)) * P, axis=1)), axis=0)
            L = l_log - min_mess_len_criterion

            # convergence criteria
            delta_L = abs(L - L_old)
            delta_v = abs(v - v_old)
            L_old = L
            v_old = v
            Ltt.append(L)
            iter = iter + 1
            if iter == max_iter:
                raise Warning('CONVERGENCE FAILED FOR delta_L')
            indx_remove = (Pi == 0)
            # mu[indx_remove,:] = []
            mu = mu[np.logical_not(indx_remove), :]
            Sigma = Sigma[:, :, np.logical_not(indx_remove)]
            Pi = Pi[np.logical_not(indx_remove)]
            z = z[:,np.logical_not(indx_remove)]
            u = u[:, np.logical_not(indx_remove)]
            P = P[:, np.logical_not(indx_remove)]
            delta_distance = delta_distance[:, np.logical_not(indx_remove)]
            g = g - sum(indx_remove)

        if L > L_max:
            L_max = L
            if REM.size == 0:
                optimal_set['cluster_index'] = np.argmax(z, 1)
            else:
                c_i = np.argmax(z, 1)
                cluster_index = np.zeros((len(REM), 1))
                cluster_index[np.logical_not(REM)] = np.expand_dims(c_i, 1)
                cluster_index[REM] = 255  # removed
                optimal_set['cluster_index'] = cluster_index
            optimal_set['u'] = u
        else:
            break
        # set smallest component to zero
        ind_min = np.argmin(Pi)
        Pi[ind_min] = 0
        # Purge components where Pi = 0
        indx_remove = (Pi == 0)
        mu = mu[np.logical_not(indx_remove), :]
        Sigma = Sigma[:, :, np.logical_not(indx_remove)]
        Pi = Pi[np.logical_not(indx_remove)]
        z = z[:, np.logical_not(indx_remove)]
        u = u[:, np.logical_not(indx_remove)]
        P = P[:, np.logical_not(indx_remove)]
        delta_distance = delta_distance[:, np.logical_not(indx_remove)]
        g = g - 1

    # find not typical spikes based on typicality limit and assign them to cluster 254
    if REM.size == 0:
        u_final = np.zeros((n_spike, 1))
        for i in range(n_spike):
            u_final[i] = optimal_set['u'][i, optimal_set.cluster_index[i]]
            if u_final(i) < u_limit:
                optimal_set['cluster_index'][i] = 254
        optimal_set['typicallity'] = u_final
    else:
        ind_nor_rem = np.nonzero(np.logical_not(REM))[0]
        u_final = np.zeros((len(REM), 1))
        for i in range(n_spike):
            u = optimal_set['u']
            cluster_index = optimal_set['cluster_index']
            u_final[ind_nor_rem[i]] = u[i, int(cluster_index[ind_nor_rem[i]])]
            if u_final[ind_nor_rem[i]] < u_limit:
                optimal_set['cluster_index'][ind_nor_rem[i]] = 254
        optimal_set['typicallity'] = u_final
        # optimal_set.pop('u')
    return optimal_set

