import numpy as np
import pyqtgraph as pg

from model.api import API


class HDF5Plot(pg.PlotCurveItem):
    def __init__(self, *args, **kwds):
        self.pen = None
        self.api = None
        self.hdf5 = None
        self.limit = 10000
        pg.PlotCurveItem.__init__(self, *args, **kwds)

    def setHDF5(self, data, pen=None):
        self.hdf5 = data
        self.pen = pen
        self.updateHDF5Plot()

    def setAPI(self, api: API):
        self.api = api

    def viewRangeChanged(self):
        self.updateHDF5Plot()

    def updateHDF5Plot(self):

        vb = self.getViewBox()
        if vb is None:
            return

        xrange = vb.viewRange()[0]
        start = max(0, int(xrange[0]) - 1)

        if self.hdf5 is None:
            stop = int(xrange[1] + 2)
            res = self.api.get_raw_data(start, stop, self.limit)
            if not res['stat']:
                self.setData([])
                return
            stop = res['stop']
            visible = res['visible']
            ds = res['ds']
        else:
            stop = min(len(self.hdf5), int(xrange[1] + 2))
            ds = int((stop - start) / self.limit) + 1
            visible = self.hdf5[start:stop:ds]

        x = np.arange(start, stop, ds)

        self.setData(x, visible)
        if self.pen is not None:
            self.setPen(self.pen)
        self.resetTransform()
