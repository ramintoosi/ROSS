from PyQt5 import QtWidgets


class ExportResults(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 300)

        layout_out = QtWidgets.QVBoxLayout()
        groupbox = QtWidgets.QGroupBox("Export variables")

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

        groupboxradio = QtWidgets.QGroupBox("Export type")

        hboxradio = QtWidgets.QHBoxLayout()

        groupboxradio.setLayout(hboxradio)

        self.radioPickle = QtWidgets.QRadioButton("pickle")
        self.radioMat = QtWidgets.QRadioButton("mat")

        self.radioPickle.setChecked(True)

        hboxradio.addWidget(self.radioPickle)
        hboxradio.addWidget(self.radioMat)

        hboxpush = QtWidgets.QHBoxLayout()
        self.pushExport = QtWidgets.QPushButton("Export")
        self.pushClose = QtWidgets.QPushButton("Close")

        hboxpush.addWidget(self.pushExport)
        hboxpush.addWidget(self.pushClose)
        self.labelDownload = QtWidgets.QLabel()
        self.progbar = QtWidgets.QProgressBar()

        layout_out.addWidget(groupbox)
        layout_out.addWidget(groupboxradio)
        layout_out.addWidget(self.labelDownload)
        # layout_out.addWidget(self.progbar)
        layout_out.addLayout(hboxpush)

        self.setLayout(layout_out)

        self.setWindowTitle("Export Dialog")
