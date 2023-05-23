from scipy.io import savemat
from PyQt5 import QtWidgets

from model.api import API
from view.exportResults import ExportResults


class ExportResultsApp(ExportResults):
    def __init__(self, api: API):
        super().__init__()
        self.api = api
        self.data_dict = {}
        self.type = 'mat'

        self.pushExport.clicked.connect(self.pushExportClicked)
        self.pushClose.clicked.connect(self.reject)

    def pushExportClicked(self):
        if self.checkSpikeMat.isChecked():
            self.labelDownload.setText('Download spike waveforms from server ...')
            QtWidgets.QApplication.processEvents()
            res = self.api.get_spike_mat()
            if res['stat']:
                self.labelDownload.setText('Download Done!')
                QtWidgets.QApplication.processEvents()
                self.data_dict['SpikeWaveform'] = res['spike_mat']
            else:
                self.labelDownload.setText('Download Error!')
                QtWidgets.QMessageBox.critical(self, 'Error in Download', res['message'])
        if self.radioMat.isChecked():
            self.type = 'mat'
        elif self.radioPickle.isChecked():
            self.type = 'pickle'

        self.accept()
