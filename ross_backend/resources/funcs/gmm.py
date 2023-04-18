import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture as GMM


def gmm_sorter(alignedSpikeMat, ss):
    out = dict()
    print('GMM')

    g_max = ss.g_max
    g_min = ss.g_min
    max_iter = ss.max_iter
    n_cluster_range = np.arange(g_min + 1, g_max + 1)
    scores = []
    error = ss.error

    for n_cluster in n_cluster_range:
        clusterer = GMM(n_components=n_cluster, random_state=5, tol=error, max_iter=max_iter)
        cluster_labels = clusterer.fit_predict(alignedSpikeMat)
        silhouette_avg = silhouette_score(alignedSpikeMat, cluster_labels)
        print('For n_cluster={0} ,score={1}'.format(n_cluster, silhouette_avg))
        scores.append(silhouette_avg)

    k = n_cluster_range[np.argmax(scores)]
    clusterer = GMM(n_components=k, random_state=5, tol=error, max_iter=max_iter)
    out['cluster_index'] = clusterer.fit_predict(alignedSpikeMat)
    print('clusters : ', out['cluster_index'])

    return out['cluster_index']
