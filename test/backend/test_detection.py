from dataclasses import dataclass

import numpy as np

from ross_backend.resources.funcs.detection import startDetection


@dataclass
class Config:
    filter_type = "butter"
    filter_order = 4
    pass_freq = 300
    stop_freq = 3000
    sampling_rate = 40000
    thr_method = "median"
    side_thr = "negative"
    pre_thr = 40
    post_thr = 59
    dead_time = 20


def get_data(num_spikes=3, config=None):
    if config is None:
        config = Config()
    x = np.arange(0, 0.001, 1 / config.sampling_rate)
    y = 2 * np.sin(2 * np.pi * 1000 * x)
    z = np.zeros((config.pre_thr + config.post_thr + config.dead_time))
    return np.tile(np.concatenate((z, y, z)), num_spikes)


def test_start_detection():
    config = Config()
    num_spikes = 4
    data = get_data(num_spikes=num_spikes)
    SpikeMat, _, _, _ = startDetection(data, config)

    assert SpikeMat.shape[0] == num_spikes
