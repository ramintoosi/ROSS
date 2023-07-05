import numpy as np
import pyqtgraph as pg

from model.api import API


class HDF5Plot(pg.PlotCurveItem):
    res = None
    SS = None

    def __init__(self, *args, **kwds):
        self.cluster = None
        # self.pen = None
        self.api = None
        self.hdf5 = None
        self.limit = 10000
        pg.PlotCurveItem.__init__(self, *args, **kwds)

    def setHDF5(self, data, pen=None):
        self.hdf5 = data
        self.pen = pen
        if self.pen is not None:
            self.setPen(self.pen)
        # self.updateHDF5Plot()

    def setAPI(self, api: API):
        self.api = api

    def viewRangeChanged(self):
        self.updateHDF5Plot()

    def setCluster(self, cluster):
        self.cluster = cluster

    def updateHDF5Plot(self):

        vb = self.getViewBox()
        if vb is None:
            return

        xrange = vb.viewRange()[0]
        if xrange[1] - xrange[0] < 10:
            return

        start = max(0, int(xrange[0]) - 1)

        if self.hdf5 is None:
            stop = int(xrange[1] + 2)
            if (HDF5Plot.SS is None) or ([start, stop] != HDF5Plot.SS):
                res = self.api.get_raw_data(start, stop, self.limit)
                HDF5Plot.SS = [start, stop]
                HDF5Plot.res = res
            else:
                res = HDF5Plot.res
            if not res['stat']:
                self.setData([])
                return
            stop = res['stop']
            visible = res['visible'].copy()
            ds = res['ds']
        else:
            stop = min(len(self.hdf5), int(xrange[1] + 2))
            ds = int((stop - start) / self.limit) + 1
            visible = self.hdf5[start:stop:ds].copy()

        x = np.arange(start, stop, ds)

        if self.cluster is not None:
            # visible = visible[self.cluster[x]]
            # x = x[self.cluster[x]]
            visible[np.logical_not(self.cluster[x])] = np.nan
            # x[not self.cluster[x]] = np.nan
        self.setData(x, visible, connect='finite')
        # if self.pen is not None:
        #     self.setPen(self.pen)
        self.resetTransform()
