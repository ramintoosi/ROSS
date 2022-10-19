from models.data import DetectResultModel
from models.config import ConfigSortModel
import io
import numpy as np
from resources.funcs.sort_utils import *
from resources.funcs.skew_t_sorter import *
from resources.funcs.t_sorting import *
from resources.funcs.kmeans import *
from resources.funcs.gmm import *


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
        spike_mat, spike_time = spike_alignment(spike_mat, spike_time, config)

    if config.filtering:
        pass
        #REM = spikeFiltering(spike_mat, config)

    print('config.sorting_type : ', config.sorting_type)

    if config.sorting_type == 't dist':
        optimal_set = t_dist_sorter(spike_mat, config)
    elif config.sorting_type == 'skew-t dist':
        optimal_set = skew_t_sorter(spike_mat, config)
    elif config.sorting_type == 'K-means':
        optimal_set = kmeans(spike_mat, config)
    elif config.sorting_type == 'GMM':
        optimal_set = gmm_sorter(spike_mat, config)

    return optimal_set

