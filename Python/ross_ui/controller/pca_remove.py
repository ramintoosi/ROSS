import numpy as np
import matplotlib.pyplot as plt
from controller.select_from_collection import SelectFromCollection


class PCARemove:
    def __init__(self, data):
        self.temp_pca = None
        self.fig, self.ax = plt.subplots()
        self.data = data
        h, x_edges, y_edges, image = self.ax.hist2d(self.data[:, 0], self.data[:, 1], bins=(50, 50), cmap=plt.cm.jet)
        self.selector = SelectFromCollection(self.ax, h)
        #self.ax.figure.canvas.mpl_connect("key_press_event", self.accept)

    def accept(self, event):
        if event.key == "enter":
            print('in accept')
            selected_ind = np.squeeze([np.logical_and(np.logical_and(self.selector.min_point[0] < self.data[:, 0],
                                                                     self.data[:, 0] < self.selector.max_point[0]),
                                                      np.logical_and(self.selector.min_point[1] < self.data[:, 1],
                                                                     self.data[:, 1] < self.selector.max_point[1]))])
            self.temp_pca = self.clusters[selected_ind]
            self.selector.disconnect()
            self.ax.set_title("")
            self.ax.fig.canvas.draw()

