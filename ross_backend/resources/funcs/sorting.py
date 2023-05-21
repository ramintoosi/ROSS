import pickle
from typing import Iterable

from models.config import ConfigSortModel
from models.data import DetectResultModel
from resources.funcs.gmm import *
from resources.funcs.kmeans import *
from resources.funcs.skew_t_sorter import *
from resources.funcs.sort_utils import *
from resources.funcs.t_sorting import *


def create_cluster_time_vec(spike_time: np.ndarray, clusters, config: dict):
    cluster_time_vec = np.zeros(spike_time[-1] + config['post_thr'], dtype=np.int8)
    for i, t in enumerate(spike_time):
        cluster_time_vec[t - config['pre_thr']: t + config['post_thr']] = clusters[i]+1
    return cluster_time_vec


# TODO: combine two sorting functions into one

def startSorting(project_id):
    detect_result = DetectResultModel.find_by_project_id(project_id)
    if not detect_result:
        raise Exception("No detection result exists.")

    if not detect_result.data:
        raise Exception("No detection result exists.")

    config = ConfigSortModel.find_by_project_id(project_id)
    if not config:
        raise Exception("No sorting config exists.")

    with open(detect_result.data, 'rb') as f:
        d = pickle.load(f)

    spike_mat = d['spikeMat']
    spike_time = d['spikeTime']
    config_det = d['config']

    if config.alignment:
        spike_mat, spike_time = spike_alignment(spike_mat, spike_time, config)

    # TODO : CHECK AND CORRECT
    if config.filtering:
        pass
        # REM = spikeFiltering(spike_mat, config)

    print('config.sorting_type : ', config.sorting_type)

    if config.sorting_type == 't dist':
        optimal_set = t_dist_sorter(spike_mat, config)
    elif config.sorting_type == 'skew-t dist':
        optimal_set = skew_t_sorter(spike_mat, config)
    elif config.sorting_type == 'K-means':
        optimal_set = kmeans(spike_mat, config)
    elif config.sorting_type == 'GMM':
        optimal_set = gmm_sorter(spike_mat, config)
    else:
        raise NotImplementedError(f'{config.sorting_type} not implemented')

    return optimal_set, create_cluster_time_vec(spike_time=d['spikeTime'], clusters=optimal_set, config=config_det)


def startReSorting(project_id, clusters, selected_clusters):
    detect_result = DetectResultModel.find_by_project_id(project_id)
    if not detect_result:
        raise Exception("No detection result exists.")

    if not detect_result.data:
        raise Exception("No detection result exists.")

    config = ConfigSortModel.find_by_project_id(project_id)
    if not config:
        raise Exception("No sorting config exists.")

    with open(detect_result.data, 'rb') as f:
        d = pickle.load(f)

    spike_mat = d['spikeMat']
    spike_time = d['spikeTime']
    config_det = d['config']

    # TODO : CHECK AND CORRECT
    # if config.alignment:
    #     spike_mat, spike_time = spike_alignment(spike_mat, spike_time, config)

    if config.filtering:
        pass
        # REM = spikeFiltering(spike_mat, config)

    print('config.sorting_type : ', config.sorting_type)

    spike_mat = np.array(spike_mat)[np.isin(clusters, selected_clusters), :]

    if config.sorting_type == 't dist':
        optimal_set = t_dist_sorter(spike_mat, config)
    elif config.sorting_type == 'skew-t dist':
        optimal_set = skew_t_sorter(spike_mat, config)
    elif config.sorting_type == 'K-means':
        optimal_set = kmeans(spike_mat, config)
    elif config.sorting_type == 'GMM':
        optimal_set = gmm_sorter(spike_mat, config)
    else:
        raise NotImplementedError(f'{config.sorting_type} not implemented')

    clusters = np.array(clusters)
    clusters[np.isin(clusters, selected_clusters)] = optimal_set + np.max(clusters) + 1
    return clusters.tolist(), create_cluster_time_vec(spike_time=d['spikeTime'], clusters=clusters, config=config_det)
