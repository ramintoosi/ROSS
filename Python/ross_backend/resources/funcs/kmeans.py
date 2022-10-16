import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def kmeans(alignedSpikeMat, sdd):
    out = dict()
    print('kmeans')

    g_max = sdd.g_max
    g_min = sdd.g_min
    max_iter = sdd.max_iter
    n_cluster_range = np.arange(g_min + 1, g_max + 1)
    scores = []

    for n_cluster in n_cluster_range:
        clusterer = KMeans(n_clusters=n_cluster, max_iter=max_iter, random_state=5)
        cluster_labels = clusterer.fit_predict(alignedSpikeMat)
        silhouette_avg = silhouette_score(alignedSpikeMat, cluster_labels)
        print('For n_cluster={0} ,score={1}'.format(n_cluster, silhouette_avg))
        scores.append(silhouette_avg)

    k = n_cluster_range[np.argmax(scores)]
    clusterer = KMeans(n_clusters=k, max_iter=max_iter, random_state=5)
    out['cluster_index'] = clusterer.fit_predict(alignedSpikeMat)
    print('clusters : ', out['cluster_index'])

    return out['cluster_index']