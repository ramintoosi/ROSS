import os
import pathlib
import pickle
import random
import traceback
from uuid import uuid4

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyqtgraph
import pyqtgraph.exporters
import pyqtgraph.opengl as gl
import scipy.io as sio
import scipy.stats as stats
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPixmap, QTransform, QColor, QIcon
from colour import Color
from nptdms import TdmsFile
from shapely.geometry import Point, Polygon
from sklearn.neighbors import NearestNeighbors

from controller.detectedMatSelect import DetectedMatSelectApp as detected_mat_form
from controller.detectedTimeSelect import DetectedTimeSelectApp as detected_time_form
from controller.hdf5 import HDF5Plot
from controller.matplot_figures import MatPlotFigures
from controller.projectSelect import projectSelectApp as project_form
from controller.rawSelect import RawSelectApp as raw_form
from controller.saveAs import SaveAsApp as save_as_form
from controller.serverAddress import ServerApp as server_form
from controller.serverFileDialog import ServerFileDialogApp as sever_dialog
from controller.signin import SigninApp as signin_form
from view.mainWindow import MainWindow

icon_path = './view/icons/'

os.makedirs('.tmp', exist_ok=True)


class MainApp(MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()

        self.setWindowIcon(QtGui.QIcon('view/icons/ross.png'))

        # initial values for software options
        self.plotHistFlag = False
        self.pca_manual = None
        self.image = None
        self.pca_spikes = None
        self.number_of_clusters = None
        self.clusters_tmp = None
        self.clusters_init = None
        self.clusters = None
        self.inds = None
        self.colors = self.distin_color(127)

        self.url = 'http://localhost:5000'

        self.raw = None
        self.spike_mat = None
        self.spike_time = None
        self.cluster_time_vec = None

        self.Raw_data_path = os.path.join(pathlib.Path(__file__).parent, '../ross_data/Raw_Data')
        self.pca_path = os.path.join(pathlib.Path(__file__).parent, '../ross_data/pca_images')

        pathlib.Path(self.Raw_data_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.pca_path).mkdir(parents=True, exist_ok=True)

        self.user = None
        self.user_name = None
        self.current_project = None
        self.saveManualFlag = False
        self.plotManualFlag = False
        self.resetManualFlag = False
        self.undoManualFlag = False
        self.tempList = []

        self.startDetection.pressed.connect(self.onDetect)
        self.startSorting.pressed.connect(self.onSort)
        self.plotButton.pressed.connect(self.Plot3d)
        self.actManual.pressed.connect(self.onActManualSorting)
        self.plotManual.pressed.connect(self.onPlotManualSorting)
        self.undoManual.pressed.connect(self.onUndoManualSorting)
        self.resetManual.pressed.connect(self.onResetManualSorting)
        self.saveManual.pressed.connect(self.onSaveManualSorting)
        self.closeButton3d.pressed.connect(self.close3D)
        self.closeButton3dDet.pressed.connect(self.closeDetect3D)
        self.assign_close_button.pressed.connect(self.closeAssign)
        self.assign_button.pressed.connect(self.onAssignManualSorting)

        # PCA MANUAL
        self.resetBottonPCAManual.clicked.connect(self.PCAManualResetButton)
        self.closeBottonPCAManual.clicked.connect(self.PCAManualCloseButton)
        self.doneBottonPCAManual.clicked.connect(self.PCAManualDoneButton)

    def resetOnSignOutVars(self):

        self.raw = None
        self.spike_mat = None
        self.spike_time = None
        self.user_name = None
        self.user = None
        self.image = None
        self.pca_spikes = None
        self.number_of_clusters = None
        self.clusters_tmp = None
        self.clusters_init = None
        self.clusters = None
        self.cluster_time_vec = None

        self.user = None
        self.user_name = None
        self.current_project = None

        self.saveManualFlag = False
        self.plotManualFlag = False
        self.resetManualFlag = False
        self.undoManualFlag = False

        self.tempList = []

    def resetOnImportVars(self):

        # initial values for software options
        self.pca_manual = None
        self.image = None
        self.pca_spikes = None
        self.number_of_clusters = None
        self.clusters_tmp = None
        self.clusters_init = None
        self.clusters = None

        self.spike_mat = None
        self.spike_time = None
        self.cluster_time_vec = None

        self.saveManualFlag = False
        self.plotManualFlag = False
        self.resetManualFlag = False
        self.undoManualFlag = False
        self.tempList = []

    def onUserAccount(self):
        if self.user is None:
            self.open_signin_dialog()

    def onImportRaw(self):
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                   self.tr("Open file"),
                                                                   os.getcwd(),
                                                                   self.tr("Raw Files(*.mat *.csv *.tdms)")
                                                                   )

        if not filename:
            raise FileNotFoundError('you should select a file')

        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)

        self.statusBar().showMessage(self.tr("Loading..."))
        self.wait()
        file_extension = os.path.splitext(filename)[-1]
        if file_extension == '.mat':
            file_raw = sio.loadmat(filename)
            variables = list(file_raw.keys())
            if '__version__' in variables: variables.remove('__version__')
            if '__header__' in variables: variables.remove('__header__')
            if '__globals__' in variables: variables.remove('__globals__')

            if len(variables) > 1:
                variable = self.open_raw_dialog(variables)
                if not variable:
                    self.statusBar().showMessage(self.tr(" "))
                    return
            else:
                variable = variables[0]

            temp = file_raw[variable].flatten()

            self.raw = temp

            # ------------------ save raw data as pkl file in data_set folder ---------------------------------------
            address = os.path.join(self.Raw_data_path, str(uuid4()) + '.pkl')

            with open(address, 'wb') as f:
                pickle.dump(temp, f)

            # -----------------------------------------------------------------------------------------------------

        elif file_extension == '.csv':
            df = pd.read_csv(filename, skiprows=1)
            temp = df.to_numpy()
            address = os.path.join(self.Raw_data_path, str(uuid4()) + '.pkl')
            self.raw = temp
            with open(address, 'wb') as f:
                pickle.dump(temp, f)
        elif file_extension == '.tdms':
            tdms_file = TdmsFile.read(filename)
            i = 0
            for group in tdms_file.groups():
                df = tdms_file.object(group).as_dataframe()
                variables = list(df.keys())
                i = i + 1

            if len(variables) > 1:
                variable = self.open_raw_dialog(variables)
                if not variable:
                    self.statusBar().showMessage('')
                    return
            else:
                variable = variables[0]
            # group = tdms_file['group name']
            # channel = group['channel name']
            # channel_data = channel[:]
            # channel_properties = channel.properties
            temp = np.array(df[variable]).flatten()
            self.raw = temp

            address = os.path.join(self.Raw_data_path, os.path.split(filename)[-1][:-5] + '.pkl')
            with open(address, 'wb') as f:
                pickle.dump(temp, f)

        else:
            raise TypeError(f'File type {file_extension} is not supported!')

        self.refreshAct.setEnabled(True)
        self.statusBar().showMessage(self.tr("Successfully loaded file"), 2500)
        self.wait()

        self.statusBar().showMessage(self.tr("Plotting..."), 2500)
        self.wait()
        self.plotRaw()

        self.resetOnImportVars()

        self.plot_histogram_pca.clear()
        self.plot_clusters_pca.clear()
        self.widget_waveform.clear()

        if self.user:
            self.statusBar().showMessage(self.tr("Uploading to server..."))
            self.wait()

            res = self.user.post_raw_data(address)
            if res['stat']:
                self.statusBar().showMessage(self.tr("Uploaded"), 2500)
                self.wait()
            else:
                self.wait()

    def onImportDetected(self):
        pass
        # filename, filetype = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Open file"), os.getcwd(),
        #                                                            self.tr("Detected Spikes Files(*.mat *.csv *.tdms)"))
        #
        # if not filename:
        #     return FileNotFoundError('you should select a file')
        #
        # if not os.path.isfile(filename):
        #     raise FileNotFoundError(filename)
        #
        # self.statusBar().showMessage(self.tr("Loading..."))
        # self.wait()
        # file_extension = os.path.splitext(filename)[-1]
        # if file_extension == '.mat':
        #     file_raw = sio.loadmat(filename)
        #     variables = list(file_raw.keys())
        #     if '__version__' in variables:
        #         variables.remove('__version__')
        #     if '__header__' in variables:
        #         variables.remove('__header__')
        #     if '__globals__' in variables:
        #         variables.remove('__globals__')
        #
        #     if len(variables) > 1:
        #         variable1 = self.open_detected_mat_dialog(variables)
        #         # self.wait()
        #         if not variable1:
        #             self.statusBar().showMessage(self.tr(" "))
        #             return
        #         variable2 = self.open_detected_time_dialog(variables)
        #         if not variable2:
        #             self.statusBar().showMessage(self.tr(" "))
        #             return
        #     else:
        #         return
        #
        #     temp = file_raw[variable1].flatten()
        #     self.spike_mat = temp
        #
        #     temp = file_raw[variable2].flatten()
        #     self.spike_time = temp
        #
        # elif file_extension == '.csv':
        #     pass
        #
        # else:
        #     pass
        #
        # self.refreshAct.setEnabled(True)
        # self.statusBar().showMessage(self.tr("Successfully loaded file"), 2500)
        # self.wait()
        #
        # self.statusBar().showMessage(self.tr("Plotting..."), 2500)
        # self.wait()
        # self.plotWaveForms()
        # self.plotDetectionResult()
        # self.plotPcaResult()
        #
        # if self.user:
        #     self.statusBar().showMessage(self.tr("Uploading to server..."))
        #     self.wait()
        #
        #     res = self.user.post_detected_data(self.spike_mat, self.spike_time)
        #
        #     if res['stat']:
        #         self.statusBar().showMessage(self.tr("Uploaded"), 2500)
        #         self.wait()
        #     else:
        #         self.wait()

    def onImportSorted(self):
        pass

    def csv_reader(self, path):
        with open(path) as csv:
            for row in csv.readlines()[1:]:
                yield row.rstrip().split(',')

    @QtCore.pyqtSlot()
    def open_signin_dialog(self):
        dialog = signin_form(self.url)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.user = dialog.user
            self.user_name = dialog.textEdit_username.text()
            self.accountButton.setIcon(QtGui.QIcon(icon_path + "verified.png"))
            self.accountButton.setText(self.user_name)
            menu = QtWidgets.QMenu(self)
            menu.addAction(self.logOutAct)
            self.accountButton.setMenu(menu)
            self.accountButton.setStatusTip("Signed In")
            self.logInAct.setEnabled(False)
            self.logOutAct.setEnabled(True)
            # self.saveAct.setEnabled(True)
            # self.saveAsAct.setEnabled(True)
            self.importMenu.setEnabled(True)
            self.openAct.setEnabled(True)
            self.exportMenu.setEnabled(True)
            self.runMenu.setEnabled(True)
            self.visMenu.setEnabled(True)

            self.statusBar().showMessage(self.tr("Loading Data..."))
            #  self.wait()
            self.loadDefaultProject()
            self.statusBar().showMessage(self.tr("Loaded."), 2500)

    @QtCore.pyqtSlot()
    def open_file_dialog_server(self):
        dialog = sever_dialog(self.user)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.refreshAct.setEnabled(True)
            self.statusBar().showMessage(self.tr("Successfully loaded file"), 2500)
            self.wait()

            self.statusBar().showMessage(self.tr("Plotting..."), 2500)
            self.wait()
            self.plotRaw()

            self.resetOnImportVars()

            self.plot_histogram_pca.clear()
            self.plot_clusters_pca.clear()
            self.widget_waveform.clear()

    def open_server_dialog(self):
        dialog = server_form(server_text=self.url)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.url = dialog.lineEdit.text()

    def open_raw_dialog(self, variables):
        dialog = raw_form(variables)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            variable = dialog.comboBox.currentText()
            return variable

    def open_detected_mat_dialog(self, variables):
        dialog = detected_mat_form(variables)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            variable = dialog.comboBox.currentText()
            return variable

    def open_detected_time_dialog(self, variables):
        dialog = detected_time_form(variables)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            variable = dialog.comboBox.currentText()
            return variable

    def open_project_dialog(self, projects):
        dialog = project_form(projects)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.current_project = dialog.comboBox.currentText()
            self.statusBar().showMessage(self.tr("Loading project..."))
            self.wait()
            self.user.load_project(self.current_project)
            self.loadDefaultProject()
            self.statusBar().showMessage(self.tr("Loaded."), 2500)
            self.setWindowTitle(self.AppTitle + '    Current Project: ' + self.current_project)
            self.saveAct.setEnabled(True)

    def open_save_as_dialog(self):
        dialog = save_as_form(user=self.user)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.current_project = dialog.project_name
            self.setWindowTitle(self.AppTitle + '    Current Project: ' + self.current_project)
            self.saveAct.setEnabled(True)

            res = self.user.get_config_detect()
            if res['stat']:
                self.update_config_detect(res['config'])

    def onSignOut(self):
        res = self.user.sign_out()
        if res['stat']:
            self.resetOnSignOutVars()

            self.accountButton.setIcon(QtGui.QIcon(icon_path + "unverified.png"))
            self.accountButton.setMenu(None)
            self.accountButton.setText('')
            self.accountButton.setStatusTip("Sign In/Up")
            self.logInAct.setEnabled(True)
            self.logOutAct.setEnabled(False)
            # self.saveAct.setEnabled(False)
            # self.saveAsAct.setEnabled(False)
            self.importMenu.setEnabled(False)
            self.exportMenu.setEnabled(False)
            self.runMenu.setEnabled(False)
            self.visMenu.setEnabled(False)
            self.widget_raw.clear()
            self.plot_histogram_pca.clear()
            self.plot_clusters_pca.clear()
            self.widget_waveform.clear()
        else:
            print(res['message'])

    def onOpen(self):
        projects = self.user.get_projects()['projects']
        project_names = [p['name'] for p in projects if p['name'] is not None]
        self.open_project_dialog(project_names)

    def onSaveAs(self):
        self.open_save_as_dialog()

    def onSave(self):
        self.statusBar().showMessage(self.tr("Saving..."))
        self.wait()
        res = self.user.save_project(self.current_project)
        if res['stat']:
            self.statusBar().showMessage(self.tr("Saved."), 2500)
        else:
            self.statusBar().showMessage(self.tr(res["message"]), 2500)
            # self.wait() 

    def onDetect(self):
        if self.user is None:
            QtWidgets.QMessageBox.critical(self, "Not Signed In", "First sign in to the server!")
            return
        config_detect = self.read_config_detect()
        self.statusBar().showMessage(self.tr("Detection Started..."))
        self.wait()
        res = self.user.start_detection(config_detect)

        if res['stat']:
            self.statusBar().showMessage(self.tr("Detection Done."), 2500)
            res = self.user.get_detection_result()
            if res['stat']:
                self.spike_mat = res['spike_mat']
                self.spike_time = res['spike_time']
                self.pca_spikes = res['pca_spikes']
                self.inds = res['inds']
                self.statusBar().showMessage(self.tr("Plotting..."), 2500)
                self.wait()
                self.plotDetectionResult()
                self.plotPcaResult()
                self.plotWaveForms()

    def manualResort(self, selected_clusters):
        config_sort = self.read_config_sort()
        self.statusBar().showMessage(self.tr("Manual ReSorting Started..."))
        self.wait()

        res = self.user.start_Resorting(config_sort, self.clusters_tmp, selected_clusters)
        if res['stat']:
            self.statusBar().showMessage(self.tr("Manual ReSorting Done."), 2500)
            self.clusters_tmp = np.array(res['clusters'])

            self.UpdatedClusterIndex()
            self.statusBar().showMessage(self.tr("Clusters Waveforms Updated..."), 2500)
            self.wait()
            self.updateplotWaveForms(self.clusters_tmp)
            self.wait()
            self.update_plotRaw(self.clusters_tmp)
            self.wait()
            self.updateManualClusterList(self.clusters_tmp)
        else:
            self.statusBar().showMessage(self.tr("Manual ReSorting got error"))

    def onSort(self):
        if self.user is None:
            QtWidgets.QMessageBox.critical(self, "Not Signed In", "First sign in to the server!")
            return
        config_sort = self.read_config_sort()
        self.statusBar().showMessage(self.tr("Sorting Started..."))
        self.wait()
        res = self.user.start_sorting(config_sort)
        if res['stat']:
            self.statusBar().showMessage(self.tr("Sorting Done."), 2500)
            res = self.user.get_sorting_result()
            if res['stat']:
                self.clusters = res['clusters']
                self.cluster_time_vec = res["cluster_time_vec"]
                self.clusters_init = self.clusters.copy()
                self.clusters_tmp = self.clusters.copy()
                self.statusBar().showMessage(self.tr("Clusters Waveforms..."), 2500)
                self.wait()
                self.updateplotWaveForms(self.clusters)
                self.wait()
                self.update_plotRaw()
                self.wait()
                self.updateManualClusterList(self.clusters_tmp)
                self.plotDetectionResult()
                self.plotPcaResult()

        else:
            self.statusBar().showMessage(self.tr("Sorting got error"))

    def plotRaw(self):
        curve = HDF5Plot()
        curve.setAPI(self.user)
        curve.setHDF5(self.raw)
        self.widget_raw.clear()
        self.widget_raw.addItem(curve)
        self.widget_raw.setXRange(0, 10000)
        self.widget_raw.showGrid(x=True, y=True)
        self.widget_raw.setMouseEnabled(y=False)

    def update_plotRaw(self):
        curve = HDF5Plot()
        curve.setAPI(self.user)
        curve.setHDF5(self.raw)
        self.widget_raw.clear()
        self.widget_raw.showGrid(x=True, y=True)
        self.widget_raw.setMouseEnabled(y=False)
        self.widget_raw.addItem(curve)

        if self.cluster_time_vec is not None:
            for i, i_cluster in enumerate(np.unique(self.cluster_time_vec)):
                if i_cluster == 0:
                    continue
                color = self.colors[i - 1]
                pen = pyqtgraph.mkPen(color=color)
                curve = HDF5Plot()
                curve.setAPI(self.user)
                curve.setHDF5(self.raw, pen)
                curve.setCluster(self.cluster_time_vec == i_cluster)
                self.widget_raw.addItem(curve)
        self.widget_raw.setXRange(0, 10000)

    def onVisPlot(self):
        self.widget_visualizations()

    def plotWaveForms(self):
        if self.clusters_tmp is not None:
            spike_mat = self.spike_mat[self.clusters_tmp != -1, :]
        else:
            spike_mat = self.spike_mat

        self.widget_waveform.clear()
        x = np.empty(np.shape(spike_mat))
        x[:] = np.arange(np.shape(spike_mat)[1])[np.newaxis, :]
        self.widget_waveform.showGrid(x=True, y=True)
        self.widget_waveform.enableAutoRange(False, False)
        if np.shape(spike_mat)[0] > 200:
            ind = np.arange(spike_mat.shape[0])
            np.random.shuffle(ind)
            spike_mat = spike_mat[ind[:200], :]
        else:
            spike_mat = spike_mat
        for i in range(len(spike_mat)):
            self.widget_waveform.addItem(pyqtgraph.PlotCurveItem(x[i, :], spike_mat[i, :]))
        self.widget_waveform.autoRange()

    def hsv_to_rgb(self, h, s, v):
        if s == 0.0:
            # v = v * 255;
            v = v * 255
            return (v, v, v)
        i = int(h * 6.)
        f = (h * 6.) - i
        p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(255 * (v * (1. - s * (1. - f))))
        v = v * 255
        i = i % 6
        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        if i == 5: return (v, p, q)

    def distin_color(self, number_of_colors):
        colors = []
        golden_ratio_conjugate = 0.618033988749895
        # h = np.random.rand(1)[0]
        h = 0
        for i in range(number_of_colors):
            h += golden_ratio_conjugate
            h = h % 1
            colors.append(self.hsv_to_rgb(h, 0.99, 0.99))

        return np.array(colors)

    def updateplotWaveForms(self, clusters_=None):
        if clusters_ is None:
            clusters_ = self.clusters_tmp.copy()

        if self.clusters_tmp is not None:
            spike_mat = self.spike_mat[self.clusters_tmp[self.inds,] != -1, :]
        else:
            spike_mat = self.spike_mat

        clusters = clusters_[self.inds][clusters_[self.inds] != -1]

        un = np.unique(clusters)

        self.number_of_clusters = len(un[un >= 0])
        spike_clustered = dict()
        for i in range(self.number_of_clusters):
            spike_clustered[i] = spike_mat[clusters == i, :]

        self.widget_waveform.clear()
        self.widget_waveform.showGrid(x=True, y=True)
        self.widget_waveform.enableAutoRange(False, False)

        for i in range(self.number_of_clusters):
            avg = np.average(spike_clustered[i], axis=0)
            color = self.colors[i]
            # selected_spike = spike_clustered[i][np.sum(np.power(spike_clustered[i] - avg, 2), axis=1) <
            #                                     np.sum(np.power(avg, 2)) * 0.2]

            # if self.saveManualFlag or self.plotManualFlag:
            if len(spike_clustered[i]) > 100:
                ind = np.arange(spike_clustered[i].shape[0])
                np.random.shuffle(ind)
                spike = spike_clustered[i][ind[:100], :]
            else:
                spike = spike_clustered[i]

            # else:
            #     if len(selected_spike) > 100:
            #         ind = np.arange(selected_spike.shape[0])
            #         np.random.shuffle(ind)
            #         spike = selected_spike[ind[:100], :]
            #     else:
            #         spike = selected_spike

            x = np.empty(np.shape(spike))
            x[:] = np.arange(np.shape(spike)[1])[np.newaxis]

            pen = pyqtgraph.mkPen(color=color, width=4)
            self.widget_waveform.addItem(pyqtgraph.PlotCurveItem(x[0, :], avg, pen=pen))

            for j in range(len(spike)):
                color = self.colors[i]
                pen = pyqtgraph.mkPen(color=color, width=0.2)
                self.widget_waveform.addItem(pyqtgraph.PlotCurveItem(x[j, :], spike[j, :], pen=pen))

        self.widget_waveform.autoRange()

    def create_sub_base(self):
        self.number_of_clusters = np.shape(np.unique(self.clusters))[0]
        # self.number_of_clusters = len(np.unique(self.clusters))
        if self.number_of_clusters % 3 != 0:
            nrow = int(self.number_of_clusters / 3) + 1
        else:
            nrow = int(self.number_of_clusters / 3)

        self.sub_base = str(nrow) + str(3)

    def onPlotClusterWave(self):
        try:
            self.create_sub_base()
            number_of_clusters = self.number_of_clusters
            colors = self.colors
            spike_clustered = dict()
            for i in range(number_of_clusters):
                spike_clustered[i] = self.spike_mat[self.clusters_tmp == i]

            figure = MatPlotFigures('Clusters Waveform', number_of_clusters, width=10, height=6, dpi=100,
                                    subplot_base=self.sub_base)

            for i, ax in enumerate(figure.axes):
                avg = np.average(spike_clustered[i], axis=0)
                selected_spike = spike_clustered[i][np.sum(np.power(spike_clustered[i] - avg, 2), axis=1) <
                                                    np.sum(np.power(avg, 2)) * 0.2]

                # selected_spike = spike_clustered[i][:5]
                ax.plot(avg, color='red', linewidth=3)
                for spike in selected_spike[:100]:
                    ax.plot(spike, color=tuple(colors[i] / 255), linewidth=1, alpha=0.125)
                ax.set_title('Cluster {}'.format(i + 1))
            plt.tight_layout()
            plt.show()

        except:
            pass

    def onPlotLiveTime(self):
        try:
            self.create_sub_base()
            number_of_clusters = self.number_of_clusters
            colors = self.colors
            spike_clustered_time = dict()
            for i in range(number_of_clusters):
                spike_clustered_time[i] = self.spike_time[self.clusters == i]

            figure = MatPlotFigures('LiveTime', number_of_clusters, width=10, height=6, dpi=100,
                                    subplot_base=self.sub_base)
            for i, ax in enumerate(figure.axes):
                ax.hist(spike_clustered_time[i], bins=100, color=tuple(colors[i] / 255))
                ax.set_title('Cluster {}'.format(i + 1))
            plt.tight_layout()
            plt.show()

        except:
            pass

    def onPlotIsi(self):
        try:
            self.create_sub_base()
            number_of_clusters = self.number_of_clusters
            colors = self.colors
            spike_clustered_time = dict()
            spike_clustered_delta = dict()
            for i in range(number_of_clusters):
                spike_clustered_time[i] = self.spike_time[self.clusters == i]
                tmp2 = spike_clustered_time[i][:len(spike_clustered_time[i]) - 1].copy()
                tmp1 = spike_clustered_time[i][1:].copy()
                spike_clustered_delta[i] = tmp1 - tmp2

            figure = MatPlotFigures('ISI', number_of_clusters, width=10, height=6, dpi=100, subplot_base=self.sub_base)

            for i, ax in enumerate(figure.axes):
                gamma = stats.gamma
                x = np.linspace(0, np.max(spike_clustered_delta[i]), 100)
                param = gamma.fit(spike_clustered_delta[i], floc=0)
                pdf_fitted = gamma.pdf(x, *param)
                max_pdf = np.partition(pdf_fitted.flatten(), -2)[-2]
                plotted_pdf = pdf_fitted / max_pdf
                ax.plot(x, plotted_pdf, color='r')
                counts, bins = np.histogram(spike_clustered_delta[i], bins=100)
                weights = counts / np.max(counts)
                ax.hist(bins[:-1], bins, weights=weights, color=tuple(colors[i] / 255))
                ax.set_title('Cluster {}'.format(i + 1))
            plt.tight_layout()
            plt.show()

        except:
            pass

    def onPlot3d(self):
        # self.subwindow_3d.setVisible(self.plot3dAct.isChecked())
        self.subwindow_3d.setVisible(True)

    def Plot3d(self):
        try:
            self.plot_3d.setCameraPosition(distance=30)
            axis1 = self.axis1ComboBox.currentIndex()
            axis2 = self.axis2ComboBox.currentIndex()
            axis3 = self.axis3ComboBox.currentIndex()
            number_of_clusters = len(np.unique(self.clusters))

            # Prepration

            pca_spikes = self.pca_spikes
            pca1 = pca_spikes[:, 0]
            pca2 = pca_spikes[:, 1]
            pca3 = pca_spikes[:, 2]
            spike_time = np.squeeze(self.spike_time / 100000)
            p2p = np.squeeze(np.abs(np.amax(self.spike_mat, axis=1) - np.amin(self.spike_mat, axis=1)))
            duty = np.squeeze(np.abs(np.argmax(self.spike_mat, axis=1) - np.argmin(self.spike_mat, axis=1)) / 5)

            gx = gl.GLGridItem()
            gx.rotate(90, 0, 1, 0)
            gx.setSize(15, 15)
            gx.translate(-7.5, 0, 0)
            self.plot_3d.addItem(gx)
            gy = gl.GLGridItem()
            gy.rotate(90, 1, 0, 0)
            gy.setSize(15, 15)
            gy.translate(0, -7.5, 0)
            self.plot_3d.addItem(gy)
            gz = gl.GLGridItem()
            gz.setSize(15, 15)
            gz.translate(0, 0, -7.5)
            self.plot_3d.addItem(gz)

            mode_flag = False
            mode_list = [pca1, pca2, pca3, spike_time, p2p, duty]
            if (axis1 != axis2) and (axis1 != axis3) and (axis2 != axis3):
                pos = np.array((mode_list[axis1], mode_list[axis2], mode_list[axis3])).T
                mode_flag = True

            if mode_flag:
                colors = self.colors
                items = self.plot_3d.items.copy()
                for it in items:
                    if type(it) == pyqtgraph.opengl.items.GLScatterPlotItem.GLScatterPlotItem:
                        self.plot_3d.removeItem(it)

                for i in range(number_of_clusters):
                    pos_cluster = pos[self.clusters == i, :]
                    avg = np.average(pos_cluster, axis=0)
                    selected_pos = pos_cluster[np.sum(np.power((pos[self.clusters == i, :] - avg), 2), axis=1) <
                                               0.05 * np.amax(np.sum(np.power((pos[self.clusters == i, :] - avg), 2),
                                                                     axis=1)), :]
                    ind = np.arange(selected_pos.shape[0])
                    np.random.shuffle(ind)
                    scattered_pos = selected_pos[ind[:300], :]
                    color = np.zeros([np.shape(scattered_pos)[0], 4])
                    color[:, 0] = colors[i][0] / 255
                    color[:, 1] = colors[i][1] / 255
                    color[:, 2] = colors[i][2] / 255
                    color[:, 3] = 1
                    self.plot_3d.addItem(gl.GLScatterPlotItem(pos=scattered_pos, size=3, color=color))
            else:
                print('Same Axis Error')

        except:
            pass

    def close3D(self):
        self.subwindow_3d.setVisible(False)

    def plotDetectionResult(self):
        try:
            if self.clusters_tmp is not None:
                spike_mat = self.spike_mat[self.clusters_tmp != -1, :]
            else:
                spike_mat = self.spike_mat

            self.plot_histogram_pca.clear()
            pca_spikes = self.pca_spikes
            hist, xedges, yedges = np.histogram2d(pca_spikes[:, 0], pca_spikes[:, 1], bins=512)

            x_range = xedges[-1] - xedges[0]
            y_range = yedges[-1] - yedges[0]

            blue, red = Color('blue'), Color('red')
            colors = blue.range_to(red, 256)
            colors_array = np.array([np.array(color.get_rgb()) * 255 for color in colors])
            colors_array_white = np.array([np.array([0, 0, 0])] + list(colors_array))
            look_up_table = colors_array_white.astype(np.uint8)
            image = pyqtgraph.ImageItem()
            image.setLookupTable(look_up_table)
            image.setImage(hist, pos=(xedges[0], yedges[0]), rect=[xedges[0], yedges[0], x_range, y_range])
            view_box = pyqtgraph.ViewBox()
            view_box.addItem(image)
            view_box.setAspectLocked(lock=True)
            view_box.setAutoPan()
            plot = pyqtgraph.PlotItem(viewBox=view_box)
            grid_is_visible = True
            for key in plot.axes:
                ax = plot.getAxis(key)
                if grid_is_visible:
                    ax.setGrid(225)
                else:
                    ax.setGrid(False)
                ax.setZValue(1)
            self.plot_histogram_pca.addItem(plot)
            self.plot_histogram_pca.show()

        except:
            pass

    def plotPcaResult(self):
        self.plot_clusters_pca.clear()

        if self.clusters_tmp is not None:
            clusters_ = self.clusters_tmp[self.clusters_tmp != -1]
            x_data = self.pca_spikes[self.clusters_tmp != -1, 0]
            y_data = self.pca_spikes[self.clusters_tmp != -1, 1]
        else:
            clusters_ = None
            x_data = self.pca_spikes[:, 0]
            y_data = self.pca_spikes[:, 1]

        scatter = pyqtgraph.ScatterPlotItem()

        if clusters_ is None:
            if x_data.shape[0] > 1000:
                x = x_data[random.sample(range(x_data.shape[0]), 1000)]
                y = y_data[random.sample(range(x_data.shape[0]), 1000)]
            else:
                x, y = x_data, y_data
            scatter.addPoints(x, y, pen={'color': "w", 'width': 0.1}, size=3)
        else:
            un = np.unique(clusters_)
            n_clusters = len(un[un >= 0])
            print("clusters", n_clusters)
            new_colors = self.distin_color(n_clusters)
            for i in range(n_clusters):
                xx = x_data[clusters_ == i]
                yy = y_data[clusters_ == i]
                if xx.shape[0] > 1000:
                    x = xx[random.sample(range(xx.shape[0]), 1000)]
                    y = yy[random.sample(range(yy.shape[0]), 1000)]
                else:
                    x, y = xx, yy
                scatter.addPoints(x, y, pen={'color': new_colors[i], 'width': 0.1},
                                  brush=[new_colors[i]] * x.shape[0], size=3)

        view_box = pyqtgraph.ViewBox()
        view_box.addItem(scatter)
        view_box.setAspectLocked(lock=True)
        view_box.setAutoPan()
        plot = pyqtgraph.PlotItem(viewBox=view_box)
        grid_is_visible = True
        for key in plot.axes:
            ax = plot.getAxis(key)
            if grid_is_visible:
                ax.setGrid(225)
            else:
                ax.setGrid(False)
            ax.setZValue(1)

        self.plot_clusters_pca.addItem(plot)
        self.plot_clusters_pca.show()

    def onDetect3D(self):
        # self.subwindow_detect3d.setVisible(self.detect3dAct.isChecked())
        self.subwindow_detect3d.setVisible(True)

        try:
            pca_spikes = self.pca_spikes
            hist, xedges, yedges = np.histogram2d(pca_spikes[:, 0], pca_spikes[:, 1], bins=512)

            gx = gl.GLGridItem()
            gx.rotate(90, 0, 1, 0)
            gx.setSize(100, 100)
            gx.translate(0, 50, 50)
            self.plot_detect3d.addItem(gx)
            gy = gl.GLGridItem()
            gy.rotate(90, 1, 0, 0)
            gy.setSize(100, 100)
            gy.translate(50, 0, 50)
            self.plot_detect3d.addItem(gy)
            gz = gl.GLGridItem()
            gz.setSize(100, 100)
            gz.translate(50, 50, 0)
            self.plot_detect3d.addItem(gz)

            # regular grid of starting positions
            pos = np.mgrid[0:100, 0:100, 0:1].reshape(3, 100, 100).transpose(1, 2, 0)
            for p1 in pos:
                for p2 in p1:
                    size = np.empty((1, 1, 3))
                    size[..., 0:2] = 1
                    size[..., 2] = 100 * (hist[p2[0]][p2[1]] - np.amin(hist)) / (np.amax(hist) - np.amin(hist))
                    bg = gl.GLBarGraphItem(np.array([p2]), size)
                    cmap = plt.get_cmap('jet')
                    rgba_img = cmap((size[..., 2]) / 100)
                    # color = pyqtgraph.intColor(size[...,2][0][0])
                    bg.setColor(tuple(rgba_img[0][0]))
                    self.plot_detect3d.addItem(bg)

        except:
            pass

    def closeDetect3D(self):
        self.subwindow_detect3d.setVisible(False)

    def onDetect3D1(self):
        pca_spikes = self.pca_spikes
        hist, xedges, yedges = np.histogram2d(pca_spikes[:, 0], pca_spikes[:, 1], bins=512)
        xpos, ypos = np.meshgrid(xedges[:-1] + xedges[1:], yedges[:-1] + yedges[1:]) - (xedges[1] - xedges[0])
        xpos = xpos.flatten() * 1. / 2
        ypos = ypos.flatten() * 1. / 2
        zpos = np.zeros_like(xpos)
        dx = xedges[1] - xedges[0]
        dy = yedges[1] - yedges[0]
        dz = hist.flatten()
        cmap = plt.cm.get_cmap('jet')
        max_height = np.max(dz)
        min_height = np.min(dz)
        rgba = [cmap((k - min_height) / max_height) for k in dz]

        fig = plt.figure()  # create a canvas, tell matplotlib it's 3d
        ax = fig.add_subplot(111, projection='3d')

        ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=rgba, zsort='average')
        plt.title("Detection Reslut Histogram over PCA")
        plt.xlabel("PCA1")
        plt.ylabel("PCA2")
        plt.tight_layout()
        plt.show()

    def onRefresh(self):
        pass

    def onToggleStatusBar(self):
        """Toggles the visibility of the status bar."""
        self.statusBar().setVisible(self.statusbarAct.isChecked())

    def onWaveforms(self):
        """Toggles the visibility of the waveforms."""
        self.subwindow_waveforms.setVisible(self.waveformsAct.isChecked())

    def onRawData(self):
        """Toggles the visibility of the raw data."""
        self.subwindow_raw.setVisible(self.rawDataAct.isChecked())

    def onSettings(self):
        """Toggles the visibility of the settings."""
        self.subwindow_settings.setVisible(self.settingsAct.isChecked())

    def onVisualization(self):
        """Toggles the visibility of the visualizations."""
        self.subwindow_visualization.setVisible(self.visualizationAct.isChecked())

    def onContents(self):
        QtWidgets.QMessageBox.information(self, self.tr("Contents"), self.tr("<p>Please refer to...</p>"))

    def onAbout(self):
        QtWidgets.QMessageBox.information(self, self.tr("About"),
                                          self.tr("<p><strong>{}</strong></p>"
                                                  "<p>Version {}</p>"
                                                  "<p>Authors: ...</p>").format(self.AppTitle, self.AppVersion)
                                          )

    def onWatchdogEvent(self):
        """Perform checks in regular intervals."""
        self.mdiArea.checkTimestamps()

    def wait(self):
        QtWidgets.QApplication.processEvents()

    def UpdatedClusterIndex(self):
        cl_ind = np.unique(self.clusters_tmp)
        cnt = 0
        for i, ind in enumerate(cl_ind):
            if not ind == -1:
                self.clusters_tmp[self.clusters_tmp == ind] = cnt
                cnt += 1

    def manualPreparingSorting(self, temp):
        if len(self.tempList) == 5:
            self.tempList.pop(0)
        self.tempList.append(temp)
        self.plotManualFlag = True
        self.resetManualFlag = True
        self.saveManualFlag = True

    def updateManualClusterList(self, cluster_temp):
        self.listWidget.clear()
        # n_clusters = np.shape(np.unique(temp))[0]
        n_clusters = len(np.unique(cluster_temp)[np.unique(cluster_temp) >= 0])
        colors = self.distin_color(n_clusters)
        for i in range(n_clusters):
            item = QtWidgets.QListWidgetItem("Cluster {} ({:4.2f} %)".format(i + 1, (cluster_temp == i).mean() * 100))
            pixmap = QPixmap(50, 50)
            pixmap.fill(QColor(colors[i, 0], colors[i, 1], colors[i, 2]))
            icon = QIcon(pixmap)
            item.setIcon(icon)
            self.listWidget.addItem(item)

    def onActManualSorting(self):
        try:
            act = self.manualActWidget.currentItem()
            clusters = self.listWidget.selectedIndexes()
            selected_clusters = [cl.row() for cl in clusters]
            if act.text() == 'Merge':
                try:
                    self.mergeManual(selected_clusters)
                    self.manualPreparingSorting(self.clusters_tmp.copy())
                    self.updateManualClusterList(self.clusters_tmp.copy())
                except:
                    print("an error accrued in manual Merge")
                    print(traceback.format_exc())
            elif act.text() == 'Remove':
                try:
                    self.removeManual(selected_clusters)
                    self.manualPreparingSorting(self.clusters_tmp.copy())
                    self.updateManualClusterList(self.clusters_tmp.copy())
                    self.plotHistFlag = True
                except:
                    print("an error accrued in manual Remove")
                    print(traceback.format_exc())
            elif act.text() == 'Assign to nearest':
                try:
                    self.assignManual()
                    self.manualPreparingSorting(self.clusters_tmp.copy())

                except:
                    print("an error accrued in manual Assign to nearest")
                    print(traceback.format_exc())
            elif act.text() == "PCA Remove":
                try:
                    self.pca_manual = "Remove"
                    self.OnPcaRemove()
                    self.manualPreparingSorting(self.clusters_tmp.copy())
                    self.plotHistFlag = True

                except:
                    print("an error accrued in manual pcaRemove")
                    print(traceback.format_exc())
                    pass
            elif act.text() == "PCA Group":
                try:
                    self.pca_manual = "Group"
                    self.OnPcaRemove()
                    self.manualPreparingSorting(self.clusters_tmp.copy())

                except:
                    print("an error accrued in manual pcaGroup")
                    print(traceback.format_exc())
                    pass

            elif act.text() == "Resort":
                try:
                    self.manualResort(selected_clusters)
                    self.manualPreparingSorting(self.clusters_tmp.copy())
                    self.updateManualClusterList(self.clusters_tmp.copy())
                except:
                    print("an error accrued in manual resort")
                    print(traceback.format_exc())
            if self.autoPlotManualCheck.isChecked():
                self.onPlotManualSorting()
        except:
            print(traceback.format_exc())
            self.statusBar().showMessage(self.tr("an error accrued in manual act !"), 2000)

    def onPlotManualSorting(self):
        # update 2d pca plot
        self.plotPcaResult()
        if self.plotHistFlag:
            self.plotDetectionResult()
            self.plotHistFlag = False

        if self.plotManualFlag:
            self.updateplotWaveForms(self.clusters_tmp.copy())
            self.statusBar().showMessage(self.tr("Updating Spikes Waveforms..."))
            self.wait()
            self.update_plotRaw()
            self.statusBar().showMessage(self.tr("Updating Raw Data Waveforms..."), 2000)
            self.plotManualFlag = False

    def onResetManualSorting(self):

        self.clusters_tmp = self.clusters_init.copy()
        self.tempList = []

        # update 2d pca plot
        self.plotDetectionResult()
        self.plotPcaResult()

        # update cluster list
        self.updateManualClusterList(self.clusters_tmp.copy())
        self.updateplotWaveForms(self.clusters_init.copy())
        self.statusBar().showMessage(self.tr("Resetting Spikes Waveforms..."))
        self.wait()

        self.update_plotRaw(self.clusters_init.copy())
        self.statusBar().showMessage(self.tr("Resetting Raw Data Waveforms..."), 2000)

        self.resetManualFlag = False
        self.plotManualFlag = False
        self.saveManualFlag = False

    def onSaveManualSorting(self):
        # if self.saveManualFlag:
        self.clusters = self.clusters_tmp.copy()
        # self.number_of_clusters = np.shape(np.unique(self.clusters))[0]
        self.statusBar().showMessage(self.tr("Save Clustering Results..."))
        self.wait()

        res = self.user.save_sort_results(self.clusters)
        if res['stat']:
            self.wait()
            self.statusBar().showMessage(self.tr("Updating Spikes Waveforms..."))
            self.updateplotWaveForms(self.clusters)
            self.wait()
            self.statusBar().showMessage(self.tr("Updating Raw Data Waveforms..."), 2000)
            self.update_plotRaw()
            self.wait()
            self.statusBar().showMessage(self.tr("Saving Done."))
            self.updateManualClusterList(self.clusters_tmp)
            # self.updateManualSortingView()
        else:
            self.statusBar().showMessage(self.tr("An error occurred in saving!..."), 2000)

        self.saveManualFlag = False

    def onUndoManualSorting(self):
        try:
            self.tempList.pop()
            if len(self.tempList) != 0:
                self.clusters_tmp = self.tempList[-1]
            else:
                self.clusters_tmp = self.clusters_init.copy()

            # update cluster list
            self.updateManualClusterList(self.clusters_tmp)

            # update 2d pca plot
            if self.autoPlotManualCheck.isChecked():
                self.plotDetectionResult()
                self.plotPcaResult()

                self.updateplotWaveForms(self.clusters_tmp.copy())
                self.statusBar().showMessage(self.tr("Undoing Spikes Waveforms..."), 2000)
                self.wait()
                self.statusBar().showMessage(self.tr("Undoing Raw Data Waveforms..."), 2000)
                self.update_plotRaw(self.clusters_tmp.copy())
            self.statusBar().showMessage(self.tr("Undoing Done!"), 2000)
            self.wait()

        except:
            self.statusBar().showMessage(self.tr("There is no manual act for undoing!"), 2000)

    def mergeManual(self, selected_clusters):
        if len(selected_clusters) >= 2:
            self.statusBar().showMessage(self.tr("Merging..."))
            self.wait()
            sel_cl = selected_clusters[0]

            for ind in selected_clusters:
                self.clusters_tmp[self.clusters_tmp == ind] = sel_cl

            self.UpdatedClusterIndex()

            self.statusBar().showMessage(self.tr("...Merging Done!"), 2000)
            self.wait()
        else:
            self.statusBar().showMessage(self.tr("For Merging you should select at least two clusters..."), 2000)

    def removeManual(self, selected_clusters):
        if len(selected_clusters) != 0:
            self.statusBar().showMessage(self.tr("Removing..."))
            self.wait()
            for sel_cl in selected_clusters:
                self.clusters_tmp[self.clusters_tmp == sel_cl] = - 1
            self.UpdatedClusterIndex()
            self.statusBar().showMessage(self.tr("...Removing Done!"), 2000)
        else:
            self.statusBar().showMessage(self.tr("For Removing you should select at least one clusters..."), 2000)

    def assignManual(self):
        self.subwindow_assign.setVisible(True)
        try:
            n_clusters = self.number_of_clusters

        except:
            n_clusters = 0
        # try:
        #     self.listSourceWidget.close()
        #     self.listTargetsWidget.close()
        #     self.assign_button.close()
        #     self.assign_close_button.close()
        # except:
        #     pass
        try:
            self.listSourceWidget.clear()
            for i in range(n_clusters):
                item = QtWidgets.QListWidgetItem("Cluster %i" % (i + 1))
                self.listSourceWidget.addItem(item)
            self.listSourceWidget.setCurrentItem(item)

            self.listTargetsWidget.clear()
            for i in range(n_clusters):
                item_target = QtWidgets.QListWidgetItem("Cluster %i" % (i + 1))
                self.listTargetsWidget.addItem(item_target)
            self.listTargetsWidget.setCurrentItem(item_target)
        except:
            pass

    def onAssignManualSorting(self):
        source = self.listSourceWidget.currentItem()
        targets = self.listTargetsWidget.selectedItems()

        source_cluster = int(source.text().strip('Cluster')) - 1
        target_clusters = [int(cl.text().strip('Cluster')) - 1 for cl in targets]

        # source_spikes = dict()
        try:
            if len(target_clusters) >= 1:
                self.statusBar().showMessage(self.tr("Assigning Source Cluster to Targets..."))
                self.wait()

                source_spikes = self.spike_mat[self.clusters_tmp == source_cluster]
                source_ind = np.nonzero(self.clusters_tmp == source_cluster)

                target_avg = np.zeros((len(target_clusters), source_spikes.shape[1]))
                for it, target in enumerate(target_clusters):
                    target_avg[it, :] = np.average(self.spike_mat[self.clusters_tmp == target], axis=0)
                # TODO: check different nearest_neighbors algorithms
                nbrs = NearestNeighbors(n_neighbors=1).fit(target_avg)
                indices = nbrs.kneighbors(source_spikes, return_distance=False)
                self.clusters_tmp[source_ind] = np.array(target_clusters)[indices.squeeze()]

                self.UpdatedClusterIndex()

                self.statusBar().showMessage(self.tr("...Assigning to Nearest Clusters Done!"), 2000)
                self.wait()

                self.listSourceWidget.clear()
                self.listTargetsWidget.clear()

                for i in range(len(np.unique(self.clusters_tmp))):
                    item = QtWidgets.QListWidgetItem("Cluster %i" % (i + 1))
                    self.listSourceWidget.addItem(item)

                for i in range(len(np.unique(self.clusters_tmp))):
                    item_target = QtWidgets.QListWidgetItem("Cluster %i" % (i + 1))
                    self.listTargetsWidget.addItem(item_target)

                self.manualPreparingSorting(self.clusters_tmp.copy())
            else:
                self.statusBar().showMessage(self.tr("You Should Choose One Source and at least One Target..."), 2000)

            self.updateManualClusterList(self.clusters_tmp)
        except:
            pass

    def closeAssign(self):
        self.subwindow_assign.setVisible(False)

    def OnPcaRemove(self):

        self.pca_spikes = self.pca_spikes
        hist, xedges, yedges = np.histogram2d(self.pca_spikes[:, 0], self.pca_spikes[:, 1], bins=512)

        x_range = xedges[-1] - xedges[0]
        y_range = yedges[-1] - yedges[0]

        blue, red = Color('blue'), Color('red')
        colors = blue.range_to(red, 256)
        colors_array = np.array([np.array(color.get_rgb()) * 255 for color in colors])
        colors_array_white = np.array([np.array([0, 0, 0])] + list(colors_array))
        look_up_table = colors_array_white.astype(np.uint8)
        image = pyqtgraph.ImageItem()
        image.setLookupTable(look_up_table)
        image.setImage(hist, pos=(xedges[0], yedges[0]), rect=[xedges[0], yedges[0], x_range, y_range])
        if image._renderRequired:
            image.render()
        image.qimage = image.qimage.transformed(QTransform().scale(1, -1))
        image.save('.tmp/test.png')

        self.PCAManualResetButton()
        self.subwindow_pca_manual.setVisible(True)

    # TODO: "correct update waveform plot"
    def PCAManualDoneButton(self):

        points = self.subwindow_pca_manual.widget().points.copy()

        self.pca_spikes = self.pca_spikes
        hist, xedges, yedges = np.histogram2d(self.pca_spikes[:, 0], self.pca_spikes[:, 1], bins=512)
        x_range = xedges[-1] - xedges[0]
        y_range = yedges[-1] - yedges[0]

        image_width = self.image.width()
        image_height = self.image.height()

        norm_points = [list(item) for item in points]
        # TODO : CONVERT TO NUMPY ARRAY AND NOT DO IN FOR LOOP
        for n in range(len(norm_points)):
            norm_points[n][0] = ((norm_points[n][0] / image_width) * x_range) + xedges[0]
            norm_points[n][1] = (((image_height - norm_points[n][1]) / image_height) * y_range) + yedges[0]

        poly = Polygon(norm_points)

        if self.pca_manual == "Remove":
            for i in range(len(self.pca_spikes)):
                p1 = Point(self.pca_spikes[i])
                if not (p1.within(poly)):
                    self.clusters_tmp[i] = -1

        elif self.pca_manual == "Group":
            clusters = self.clusters_tmp.copy()
            un = np.unique(clusters[clusters != -1])
            num_of_clusters = len(un[un >= 0])

            for i in range(len(self.pca_spikes)):
                p1 = Point(self.pca_spikes[i])
                if p1.within(poly):
                    if self.clusters_tmp[i] != -1:
                        self.clusters_tmp[i] = num_of_clusters

        else:
            print("pca manual flag is not define")

        self.UpdatedClusterIndex()
        self.subwindow_pca_manual.widget().reset()
        self.subwindow_pca_manual.setVisible(False)
        self.updateplotWaveForms(self.clusters_tmp.copy())
        self.updateManualClusterList(self.clusters_tmp.copy())
        self.plotDetectionResult()
        self.plotPcaResult()

    def PCAManualResetButton(self):
        self.subwindow_pca_manual.widget().reset()
        self.image = QPixmap('.tmp/test.png')
        self.label_pca_manual.setMaximumWidth(self.image.width())
        self.label_pca_manual.setMaximumHeight(self.image.height())
        self.label_pca_manual.resize(self.image.width(), self.image.height())
        self.label_pca_manual.setStyleSheet('border: 2px solid black;')
        w = self.image.width() * 1.2
        h = self.image.height() * 1.2
        self.subwindow_pca_manual.setFixedWidth(w)
        self.subwindow_pca_manual.setFixedHeight(h)
        self.subwindow_pca_manual.setVisible(True)
        self.label_pca_manual.resize(self.image.width(), self.image.height())
        self.label_pca_manual.setPixmap(self.image)
        self.subwindow_pca_manual.widget().setPixmap(self.image)

    def PCAManualCloseButton(self):
        self.subwindow_pca_manual.widget().reset()
        self.subwindow_pca_manual.setVisible(False)

    def loadDefaultProject(self):
        flag_raw = False
        flag_update_raw = False
        SERVER_MODE = False

        res = self.user.get_config_detect()
        if res['stat']:
            self.update_config_detect(res['config'])

        res = self.user.get_config_sort()
        if res['stat']:
            self.update_config_sort(res['config'])

        res = self.user.get_raw_data()
        if res['stat']:
            if 'raw' in res:
                with open(res['raw'], 'rb') as f:
                    new_data = pickle.load(f)

                self.raw = new_data
                self.statusBar().showMessage(self.tr("Plotting..."), 2500)
                self.wait()
            else:
                SERVER_MODE = True
            flag_raw = True

        res = self.user.get_detection_result()
        if res['stat']:
            self.spike_mat = res['spike_mat']
            self.spike_time = res['spike_time']
            self.pca_spikes = res['pca_spikes']
            self.inds = res['inds']
            self.plotWaveForms()
            self.plotDetectionResult()
            self.plotPcaResult()

        # done
        res = self.user.get_sorting_result()
        if res['stat']:
            self.clusters_init = res['clusters']
            self.cluster_time_vec = res['cluster_time_vec']
            self.clusters = self.clusters_init.copy()
            self.clusters_tmp = self.clusters_init.copy()
            self.updateplotWaveForms(self.clusters_init.copy())
            self.wait()
            flag_update_raw = True
            self.updateManualClusterList(self.clusters_tmp)
            self.plotPcaResult()

        if flag_raw:
            if flag_update_raw:
                self.update_plotRaw()
            else:
                self.plotRaw()

    def read_config_detect(self):
        config = dict()
        config['filter_type'] = self.filterType.currentText()
        config['filter_order'] = self.filterOrder.value()
        config['pass_freq'] = int(self.passFreq.text())
        config['stop_freq'] = int(self.stopFreq.text())
        config['sampling_rate'] = int(self.samplingRate.value())
        config['thr_method'] = self.thresholdMethod.currentText()
        config['side_thr'] = self.signalSideThresholding.currentText()
        config['pre_thr'] = int(self.preThreshold.text())
        config['post_thr'] = int(self.postThreshold.text())
        config['dead_time'] = int(self.deadTime.text())
        return config

    def read_config_sort(self):
        config = dict()
        # alignment config
        config['max_shift'] = self.maxShift.value()
        config['num_peaks'] = self.numPeaks.value()
        config['histogram_bins'] = self.histogramBins.value()
        config['compare_mode'] = self.compareMode.currentText()

        # filtering config
        config['max_std'] = float(self.maxStd.text())
        config['max_mean'] = float(self.maxMean.text())
        config['max_outliers'] = float(self.maxOutliers.text())

        # sorting config
        config['alignment'] = self.alignment.isChecked()
        config['filtering'] = self.filtering.isChecked()
        config['nu'] = float(self.nu.text())
        config['max_iter'] = self.maxIter.value()
        config['PCA_num'] = self.pcaNum.value()
        config['g_max'] = self.gMax.value()
        config['g_min'] = self.gMin.value()
        config['u_lim'] = float(self.uLim.text())
        config['N'] = int(self.n.text())
        # config['random_seed'] = int(self.randomSeed.text())
        config['sorting_type'] = self.sortingType.currentText()

        config['error'] = float(self.error.text())
        config['tol'] = float(self.tol.text())
        config['matching_mode'] = self.matching_mode.currentText()
        config['alpha'] = float(self.alpha.text())
        config['combination'] = self.combination.isChecked()
        config['custom_template'] = self.custom_templates.isChecked()

        return config

    def update_config_detect(self, config_dict):
        index = self.filterType.findText(config_dict['filter_type'], QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.filterType.setCurrentIndex(index)
        self.filterOrder.setValue(config_dict['filter_order'])
        self.passFreq.setText(str(config_dict['pass_freq']))
        self.stopFreq.setText(str(config_dict['stop_freq']))
        self.samplingRate.setValue(config_dict['sampling_rate'])
        index = self.thresholdMethod.findText(config_dict['thr_method'], QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.thresholdMethod.setCurrentIndex(index)
        index = self.signalSideThresholding.findText(config_dict['side_thr'], QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.signalSideThresholding.setCurrentIndex(index)
        self.preThreshold.setText(str(config_dict['pre_thr']))
        self.postThreshold.setText(str(config_dict['post_thr']))
        self.deadTime.setText(str(config_dict['dead_time']))

    def update_config_sort(self, config_dict):
        self.maxShift.setValue(config_dict['max_shift'])
        self.histogramBins.setValue(config_dict['histogram_bins'])
        self.numPeaks.setValue(config_dict['num_peaks'])
        index = self.compareMode.findText(config_dict['compare_mode'], QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.compareMode.setCurrentIndex(index)

        self.maxStd.setText(str(config_dict['max_std']))
        self.maxMean.setText(str(config_dict['max_mean']))
        self.maxOutliers.setText(str(config_dict['max_outliers']))
        self.nu.setText(str(config_dict['nu']))
        self.maxIter.setValue(config_dict['max_iter'])
        self.pcaNum.setValue(config_dict['PCA_num'])
        self.gMax.setValue(config_dict['g_max'])
        self.gMin.setValue(config_dict['g_min'])
        self.uLim.setText(str(config_dict['u_lim']))
        self.error.setText(str(config_dict['error']))
        self.tol.setText(str(config_dict['tol']))
        self.n.setText(str(config_dict['N']))
        index = self.matching_mode.findText(config_dict['matching_mode'], QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.matching_mode.setCurrentIndex(index)

        self.alpha.setText(str(config_dict['alpha']))
        self.combination.setChecked(config_dict['combination'])
        self.custom_templates.setChecked(config_dict['custom_templates'])
        index = self.sortingType.findText(config_dict['sorting_type'], QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.sortingType.setCurrentIndex(index)

        self.alignment.setChecked(config_dict['alignment'])
        self.filtering.setChecked(config_dict['filtering'])
