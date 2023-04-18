import numpy as np


class MultiColoredCurve:
    def __init__(self, data, segmented_time, num_of_clusters, raw_len):
        self.data = data
        self.segmented = segmented_time
        self.curves = dict()

        for i in range(num_of_clusters + 1):
            self.curves['{}'.format(i)] = np.zeros(raw_len)

        for seg in self.segmented.segmented:
            if seg.spike:
                start = int(seg.start)
                end = int(seg.end)
                if int(seg.color) >= 0:
                    self.curves[str(int(seg.color))][start: end] = self.data[start: end].copy()
                else:
                    self.curves[str(num_of_clusters)][start: end] = self.data[start: end].copy()

            else:
                start = int(seg.start)
                end = int(seg.end)
                self.curves[str(num_of_clusters)][start: end] = self.data[start: end].copy()
