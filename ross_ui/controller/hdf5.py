import numpy as np
import pyqtgraph as pg


class HDF5Plot(pg.PlotCurveItem):
    def __init__(self, *args, **kwds):
        self.hdf5 = None
        self.limit = 10000
        pg.PlotCurveItem.__init__(self, *args, **kwds)

    def setHDF5(self, data, pen=None):
        self.hdf5 = data
        self.pen = pen
        self.updateHDF5Plot()

    def viewRangeChanged(self):
        self.updateHDF5Plot()

    def updateHDF5Plot(self):
        if self.hdf5 is None:
            self.setData([])
            return

        vb = self.getViewBox()
        if vb is None:
            return

        xrange = vb.viewRange()[0]
        start = max(0, int(xrange[0]) - 1)
        stop = min(len(self.hdf5), int(xrange[1] + 2))

        ds = int((stop - start) / self.limit) + 1
        visible = self.hdf5[start:stop:ds]
        x = np.arange(start, stop, ds)

        self.setData(x, visible)
        if self.pen is not None:
            self.setPen(self.pen)
        self.resetTransform()