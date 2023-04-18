from controller.plot_time import PlotTime


class SegmentedTime:
    def __init__(self, spike_time, clusters, sr=40000):
        self.segmented = []
        self.segmented.append(PlotTime(0, spike_time[0] - sr * 0.001, spike=False, color=-1))
        for i in range(1, spike_time.shape[0]):
            try:
                self.segmented.append(
                    PlotTime(spike_time[i - 1] - sr * 0.001, spike_time[i - 1] + sr * 0.0015, spike=True,
                             color=clusters[i - 1] if clusters[i - 1] >= 0 else -1))

                self.segmented.append(PlotTime(spike_time[i - 1] + sr * 0.0015, spike_time[i] - sr * 0.001, spike=False,
                                               color=-1))
            except:
                break
