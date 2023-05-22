from PyQt5 import QtWidgets


class ExportView(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 300)

        layout_out = QtWidgets.QVBoxLayout()
        groupbox = QtWidgets.QGroupBox("Export variables")
        groupbox.setCheckable(True)

        vbox = QtWidgets.QVBoxLayout()
        groupbox.setLayout(vbox)

        self.checkSpikeMat = QtWidgets.QCheckBox("Spike Waveforms")
        self.checkSpikeTime = QtWidgets.QCheckBox("Spike Times")
        self.checkClusters = QtWidgets.QCheckBox("Sorting Results (Cluster Indexes)")

        self.checkSpikeTime.setChecked(True)
        self.checkClusters.setChecked(True)

        vbox.addWidget(self.checkSpikeMat)
        vbox.addWidget(self.checkSpikeTime)
        vbox.addWidget(self.checkClusters)

        hbox = QtWidgets.QHBoxLayout()
        self.pushExport = QtWidgets.QPushButton("Export")
        self.pushClose = QtWidgets.QPushButton("Close")

        hbox.addWidget(self.pushExport)
        hbox.addWidget(self.pushClose)

        layout_out.addLayout(vbox)
        layout_out.addLayout(hbox)

        self.setLayout(layout_out)

        self.setWindowTitle("Export Dialog")
