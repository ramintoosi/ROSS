from dataclasses import dataclass

import numpy as np

from ross_backend.resources.funcs.gmm import gmm_sorter


@dataclass
class Config:
    g_max = 10
    g_min = 2
    max_iter = 1000
    error = 1e-5


def generate_data(num_clusters=2, n_per_class=200):
    data = np.zeros((num_clusters * n_per_class, 2))
    for i in range(num_clusters):
        data[i * n_per_class: (i + 1) * n_per_class, :] = np.random.multivariate_normal(
            [2 * i, 2 * i], [[0.01, 0], [0, 0.01]], size=(n_per_class,)
        )
    return data


def test_gmm():
    num_clusters = 3
    config = Config()
    data = generate_data(num_clusters)
    cluster_index = gmm_sorter(data, config)

    assert len(np.unique(cluster_index)) == num_clusters
