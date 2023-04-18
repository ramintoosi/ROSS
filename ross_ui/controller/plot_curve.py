from pyqtgraph import PlotCurveItem


class PlotCurve(PlotCurveItem):
    def __init__(self, *args, **kwargs):
        PlotCurveItem.__init__(self, *args, **kwargs)

    def set_curve(self, curve):
        self.curve = curve
        self.updatePlot()

    def viewRangeChanged(self):
        self.updatePlot()

    def updatePlot(self):
        print('in update plot')
        vb = self.getViewBox()
        if vb is None:
            xstart = 0
            xend = 400
        else:
            xstart = int(vb.viewRange()[0][0]) + 1
            xend = int(vb.viewRange()[0][1]) + 1

        if self.curve.end <= xend and self.curve.start >= xstart:
            print('here 1')
            visible = self.curve.pos_y
            print(len(visible))
            self.setData(visible)
            self.setPos(self.curve.start, 0)
            self.setPen(self.curve.pen)

        elif self.curve.end <= xend and self.curve.start < xstart:
            print('here 2')
            visible = self.curve.pos_y[xstart:]
            print(len(visible))
            self.setData(visible)
            self.setPos(xstart, 0)
            self.setPen(self.curve.pen)

        elif self.curve.end > xend and self.curve.start >= xstart:
            print('here 3')
            visible = self.curve.pos_y[:xend]
            print(len(visible))
            self.setData(visible)
            self.setPos(self.curve.start, 0)
            self.setPen(self.curve.pen)

        elif self.curve.end > xend and self.curve.start < xstart:
            print('here 4')
            visible = self.curve.pos_y[xstart: xend]
            print(len(visible))
            self.setData(visible)
            self.setPos(xstart, 0)
            self.setPen(self.curve.pen)

        else:
            pass
