import math

import matplotlib.pyplot as plt


class MatPlotFigures:
    def __init__(self, fig_title, number_of_clusters, width=10, height=6, dpi=100):
        fig = plt.figure(figsize=(width, height), dpi=dpi)
        fig.canvas.manager.set_window_title(fig_title)
        self.axes = []
        nrows = math.ceil(number_of_clusters / 3)
        for i in range(number_of_clusters):
            self.axes.append(fig.add_subplot(nrows, 3, i+1))
