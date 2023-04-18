import matplotlib.pyplot as plt


class MatPlotFigures:
    def __init__(self, fig_title, number_of_clusters, width=10, height=6, dpi=100, subplot_base='13'):
        fig = plt.figure(figsize=(width, height), dpi=dpi)
        fig.canvas.set_window_title(fig_title)
        self.axes = []
        for i in range(int(subplot_base) // 10):
            if i == (int(subplot_base) // 10) - 1:
                for j in range(number_of_clusters % 3):
                    sub = int(subplot_base + str((i * 3) + j + 1))
                    self.axes.append(fig.add_subplot(sub))
            else:
                for j in range(3):
                    sub = int(subplot_base + str((i * 3) + j + 1))
                    self.axes.append(fig.add_subplot(sub))
