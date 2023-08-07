import numpy as np

class Raw:
    def __init__(self, raw: np.ndarray):
        self._raw = raw
        # error if raw has more than two dims
        if len(raw.shape) > 2:
            raise ValueError("Raw data must be 2D")
        # make sure the first dim of raw is always smaller
        if raw.shape[0] > raw.shape[1]:
            self._raw = raw.T

    def __call__(self, channel=0):
        if len(self._raw.shape) > 1:
            return self._raw[channel].flatten()
        else:
            return self._raw.flatten()

    @property
    def channels(self):
        return self._raw.shape[0] if len(self._raw.shape) > 1 else 0