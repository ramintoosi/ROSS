import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture as GMM


def gmm_sorter(aligned_spikemat, ss):
    g_max = ss.g_max
    g_min = ss.g_min
    max_iter = ss.max_iter
    n_cluster_range = np.arange(g_min + 1, g_max + 1)
    error = ss.error

    scores = []

    for n_cluster in n_cluster_range:
        cluster = GMM(n_components=n_cluster, random_state=5, tol=error, max_iter=max_iter)
        cluster_labels = cluster.fit_predict(aligned_spikemat)
        silhouette_avg = silhouette_score(aligned_spikemat, cluster_labels)
        scores.append(silhouette_avg)

    k = n_cluster_range[np.argmax(scores)]
    cluster = GMM(n_components=k, random_state=5, tol=error, max_iter=max_iter)
    cluster_index = cluster.fit_predict(aligned_spikemat)

    return cluster_index
