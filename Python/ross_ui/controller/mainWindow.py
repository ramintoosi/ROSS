import sklearn.decomposition
from view.mainWindow import MainWindow
from PyQt5 import QtCore, QtWidgets, QtGui
from controller.signin import SigninApp as signin_form
from controller.serverAddress import ServerApp as server_form
from controller.rawSelect import RawSelectApp as raw_form
from controller.detectedMatSelect import DetectedMatSelectApp as detected_mat_form
from controller.detectedTimeSelect import DetectedTimeSelectApp as detected_time_form
from controller.projectSelect import projectSelectApp as project_form
from controller.saveAs import SaveAsApp as save_as_form
from controller.hdf5 import HDF5Plot
from controller.multicolor_curve import MultiColoredCurve
from controller.segmented_time import SegmentedTime
from controller.matplot_figures import MatPlotFigures
from controller.pca_remove import PCARemove
from controller.select_from_collection import SelectFromCollection
import sys, os
import scipy.io as sio
import numpy as np
from nptdms import TdmsFile
import time
import sklearn.decomposition as decom
import pyqtgraph.opengl as gl
import pyqtgraph
from colour import Color
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import scipy.stats as stats


icon_path = './view/icons/'


class MainApp(MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        # initial values for software options
        self.url = 'http://127.0.0.1:5000'
        self.user = None
        self.user_name = None
        self.current_project = None
        self.saveManualFlag = False
        self.plotManualFlag = False
        self.resetManualFlag = False
        self.undoManualFlag = False
        self.flag_assign_temp = False

        self.tempClusterList = []
        self.tempSpikeMatList = []
        self.tempSpikeTimeList = []

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

    def onUserAccount(self):
        if self.user == None:
            self.open_signin_dialog()

    def onImportRaw(self):
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(self,
            self.tr("Open file"),
            os.getcwd(),
            self.tr("Raw Files(*.mat *.csv *.tdms)")
        )

        if not filename:
            return FileNotFoundError('you should select a file')

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
        elif file_extension == '.csv':
            temp = np.load(filename)
            self.raw = temp
        else:
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
        self.refreshAct.setEnabled(True)
        self.statusBar().showMessage(self.tr("Successfully loaded file"), 2500)
        self.wait()   

        self.statusBar().showMessage(self.tr("Plotting..."), 2500) 
        self.wait()    
        self.plotRaw()

        if self.user:
            self.statusBar().showMessage(self.tr("Uploading to server..."))
            self.wait()
            res = self.user.post_raw_data(self.raw)
            if res['stat']:
                self.statusBar().showMessage(self.tr("Uploaded"), 2500)
                self.wait()
            else:
                self.wait()

    def onImportDetected(self):
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Open file"), os.getcwd(),
                                                                   self.tr("Detected Spikes Files(*.mat *.csv *.tdms)"))

        if not filename:
            return FileNotFoundError('you should select a file')

        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)

        self.statusBar().showMessage(self.tr("Loading..."))
        self.wait()
        file_extension = os.path.splitext(filename)[-1]
        if file_extension == '.mat':
            file_raw = sio.loadmat(filename)
            variables = list(file_raw.keys())
            if '__version__' in variables:
                variables.remove('__version__')
            if '__header__' in variables:
                variables.remove('__header__')
            if '__globals__' in variables:
                variables.remove('__globals__')

            if len(variables) > 1:
                variable1 = self.open_detected_mat_dialog(variables)
                print('here after var1')
                print(variable1)
                #self.wait()
                if not variable1:
                    self.statusBar().showMessage(self.tr(" "))
                    print('var1')
                    return
                print(variable1)
                variable2 = self.open_detected_time_dialog(variables)
                if not variable2:
                    self.statusBar().showMessage(self.tr(" "))
                    return
                print(variable2)
            else:
                return

            temp = file_raw[variable1].flatten()
            self.spike_mat = temp

            temp = file_raw[variable2].flatten()
            self.spike_time = temp

        elif file_extension == '.csv':
            pass

        else:
            pass

        self.refreshAct.setEnabled(True)
        self.statusBar().showMessage(self.tr("Successfully loaded file"), 2500)
        self.wait()

        self.statusBar().showMessage(self.tr("Plotting..."), 2500)
        self.wait()
        self.plotWaveForms()
        self.plotDetectionResult()

        if self.user:
            self.statusBar().showMessage(self.tr("Uploading to server..."))
            self.wait()
            res = self.user.post_detected_data(self.spike_mat, self.spike_time)
            if res['stat']:
                self.statusBar().showMessage(self.tr("Uploaded"), 2500)
                self.wait()
            else:
                self.wait()

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
            self.saveAsAct.setEnabled(True)
            self.openAct.setEnabled(True)

            self.statusBar().showMessage(self.tr("Loading Data..."))
            # # self.wait()
            self.loadDefaultProject()
            self.statusBar().showMessage(self.tr("Loaded."), 2500)
            self.saveAct.setEnabled(True)

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
        print('here in open dialog')
        dialog = detected_mat_form(variables)
        print('here 1')
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            print('here2')
            variable = dialog.comboBox.currentText()
            print('here3')
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

            # self.raw = self.user.get_raw_data()
            # self.statusBar().showMessage(self.tr("Plotting..."), 2500) 
            # self.wait()    
            # self.plotRaw()

            # config_detect = self.user.get_config_detect()
            # self.update_config_detect(config_detect)
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
            self.user_name = None
            self.accountButton.setIcon(QtGui.QIcon(icon_path + "unverified.png"))
            self.accountButton.setMenu(None)
            self.accountButton.setText('')
            self.accountButton.setStatusTip("Sign In/Up")
            self.logInAct.setEnabled(True)
            self.logOutAct.setEnabled(False)
            self.user = None
            self.saveAct.setEnabled(False)
            self.saveAsAct.setEnabled(False)
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
        print(config_detect)
        self.statusBar().showMessage(self.tr("Detection Started..."))
        self.wait()
        res = self.user.start_detection(config_detect)
        if res['stat']:
            self.statusBar().showMessage(self.tr("Detection Done."), 2500)
            res = self.user.get_detection_result()
            if res['stat']:
                self.spike_mat = res['spike_mat']
                self.spike_time = res['spike_time']
                self.statusBar().showMessage(self.tr("Plotting..."), 2500)
                self.wait()
                self.plotDetectionResult()
                self.plotWaveForms()

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
                self.statusBar().showMessage(self.tr("Clusters Waveforms..."), 2500)
                self.wait()
                self.updateplotWaveForms(self.spike_mat, self.clusters)
                self.wait()
                self.update_plotRaw(self.spike_time, self.clusters)
                self.wait()
                self.updateManualSortingView()
        else:
            self.statusBar().showMessage(self.tr("Sorting got error"))

    def plotRaw(self):
        curve = HDF5Plot()
        curve.setHDF5(self.raw)
        self.widget_raw.clear()
        self.widget_raw.addItem(curve)
        self.widget_raw.setXRange(0,10000)
        self.widget_raw.showGrid(x=True, y=True)
        self.widget_raw.setMouseEnabled(y=False)

    def update_plotRaw(self, spike_time_inp, clusters):
        data = self.raw
        colors = self.colors
        num_of_clusters = self.number_of_clusters
        spike_time = spike_time_inp
        time = SegmentedTime(spike_time, clusters)
        multi_curve = MultiColoredCurve(data, time, num_of_clusters, len(data))
        self.widget_raw.clear()
        for i in range(num_of_clusters + 1):
            curve = HDF5Plot()
            if i == num_of_clusters:
                color = (255, 255, 255)
                pen = pyqtgraph.mkPen(color=color)
            else:
                color = colors[i]
                pen = pyqtgraph.mkPen(color=color)
            curve.setHDF5(multi_curve.curves[str(i)], pen)
            self.widget_raw.addItem(curve)
            self.widget_raw.setXRange(0, 10000)
            self.widget_raw.showGrid(x=True, y=True)
            self.widget_raw.setMouseEnabled(y=False)

    def onVisPlot(self):
        self.widget_visualizations()

    def plotWaveForms(self):
        self.widget_waveform.clear()
        x = np.empty(np.shape(self.spike_mat))
        x[:] = np.arange(np.shape(self.spike_mat)[1])[np.newaxis, :]
        self.widget_waveform.showGrid(x=True, y=True)
        self.widget_waveform.enableAutoRange(False, False)
        if np.shape(self.spike_mat)[0] > 200:
            ind = np.arange(self.spike_mat.shape[0])
            np.random.shuffle(ind)
            spike_mat = self.spike_mat[ind[:200], :]
        else:
            spike_mat = self.spike_mat
        for i in range(len(spike_mat)):
            self.widget_waveform.addItem(pyqtgraph.PlotCurveItem(x[i, :], spike_mat[i, :]))
        self.widget_waveform.autoRange()

    def hsv_to_rgb(self, h, s, v):
        if s == 0.0:
            v = v * 255; return (v, v, v)
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
        colors= []
        golden_ratio_conjugate = 0.618033988749895
        # h = np.random.rand(1)[0]
        h = 0
        for i in range(number_of_colors):
            h += golden_ratio_conjugate
            h = h % 1
            colors.append(self.hsv_to_rgb(h, 0.99, 0.99))

        return np.array(colors)

    def updateplotWaveForms(self, spike_mat, clusters):
        un = np.unique(clusters)
        self.number_of_clusters = len(un[un >= 0])
        self.colors = self.distin_color(self.number_of_clusters)
        spike_clustered = dict()
        for i in range(self.number_of_clusters):
            spike_clustered[i] = spike_mat[clusters == i]

        self.widget_waveform.clear()
        self.widget_waveform.showGrid(x=True, y=True)
        self.widget_waveform.enableAutoRange(False, False)

        for i in range(self.number_of_clusters):
            avg = np.average(spike_clustered[i], axis=0)
            color = self.colors[i]
            selected_spike = spike_clustered[i][np.sum(np.power(spike_clustered[i] - avg, 2), axis=1) <
                                                np.sum(np.power(avg, 2)) * 0.2]

            if self.saveManualFlag or self.plotManualFlag:
                if len(spike_clustered[i]) > 100:
                    ind = np.arange(spike_clustered[i].shape[0])
                    np.random.shuffle(ind)
                    spike = spike_clustered[i][ind[:100], :]
                else:
                    spike = spike_clustered[i]

            else:
                if len(selected_spike) > 100:
                    ind = np.arange(selected_spike.shape[0])
                    np.random.shuffle(ind)
                    spike = selected_spike[ind[:100], :]
                else:
                    spike = selected_spike

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
        self.number_of_clusters = len(np.unique(self.clusters))
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
                spike_clustered[i] = self.spike_mat[self.clusters == i]

            figure = MatPlotFigures('Clusters Waveform', number_of_clusters, width=10, height=6, dpi=100,
                                    subplot_base=self.sub_base)

            for i, ax in enumerate(figure.axes):
                avg = np.average(spike_clustered[i], axis=0)
                selected_spike = spike_clustered[i][np.sum(np.power(spike_clustered[i] - avg, 2), axis=1) <
                                                    np.sum(np.power(avg, 2)) * 0.2]
                ax.plot(avg, color='red', linewidth=3)
                for spike in selected_spike[:100]:
                    ax.plot(spike, color=tuple(colors[i]/255), linewidth=1, alpha=0.125)
                ax.set_title('Cluster {}'.format(i + 1))
            plt.tight_layout()
            plt.show()

        except:
            pass

    # def onPlotClusterWave1(self):

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
                ax.hist(spike_clustered_time[i], bins=100, color=tuple(colors[i]/255))
                ax.set_title('Cluster {}'.format(i+1))
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
                tmp2 = spike_clustered_time[i][:len(spike_clustered_time[i])-1].copy()
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
                ax.hist(bins[:-1], bins, weights=weights, color=tuple(colors[i]/255))
                ax.set_title('Cluster {}'.format(i+1))
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
            pca = decom.PCA(n_components=3)
            pca_spikes = pca.fit_transform(self.spike_mat)
            pca1 = pca_spikes[:, 0]
            pca2 = pca_spikes[:, 1]
            pca3 = pca_spikes[:, 2]
            spike_time = np.squeeze(self.spike_time / 100000)
            p2p = np.squeeze(np.abs(np.amax(self.spike_mat, axis=1) - np.amin(self.spike_mat, axis=1)))
            duty = np.squeeze(np.abs(np.argmax(self.spike_mat, axis=1) - np.argmin(self.spike_mat,axis=1))/5)

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
            self.plot_clusters.clear()
            pca = decom.PCA(n_components=2)
            pca_spikes = pca.fit_transform(self.spike_mat)
            hist, xedges, yedges = np.histogram2d(pca_spikes[:, 0], pca_spikes[:, 1], bins=100)

            x_range = xedges[-1] - xedges[0]
            y_range = yedges[-1] - yedges[0]

            blue, red = Color('blue'), Color('red')
            colors = blue.range_to(red, 256)
            colors_array = np.array([np.array(color.get_rgb()) * 255 for color in colors])
            colors_array_white = np.array([np.array([0, 0, 0])] + list(colors_array))
            look_up_table = colors_array_white.astype(np.uint8)
            image = pyqtgraph.ImageItem()
            image.setLookupTable(look_up_table)
            image.setImage(hist, pos=(xedges[0], yedges[0]), scale=(x_range / 100, y_range / 100))
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
            self.plot_clusters.addItem(plot)
            self.plot_clusters.show()

        except:
            pass

    def onDetect3D(self):
        # self.subwindow_detect3d.setVisible(self.detect3dAct.isChecked())
        self.subwindow_detect3d.setVisible(True)

        try:
            pca = decom.PCA(n_components=2)
            pca_spikes = pca.fit_transform(self.spike_mat)
            hist, xedges, yedges = np.histogram2d(pca_spikes[:, 0], pca_spikes[:, 1], bins=100)

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
        pca = decom.PCA(n_components=2)
        pca_spikes = pca.fit_transform(self.spike_mat)
        hist, xedges, yedges = np.histogram2d(pca_spikes[:, 0], pca_spikes[:, 1], bins=100)
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
            "<p>Authors: {}</p>").format(self.AppTitle, self.AppVersion, 'Toosi, Mirsharji, Dinashi')
        )

    def onWatchdogEvent(self):
        """Perform checks in regular intervals."""
        self.mdiArea.checkTimestamps()

    def wait(self, duration=2.0):
        QtWidgets.QApplication.processEvents()
        time.sleep(duration)

    def manualPreparingSorting(self, temp_spike_time, temp_spike_mat, temp_cluster):
        if len(self.tempClusterList) == 5:
            self.tempClusterList.pop(0)
        if len(self.tempSpikeMatList) == 5:
            self.tempSpikeMatList.pop(0)
        if len(self.tempSpikeTimeList) == 5:
            self.tempSpikeTimeList.pop(0)
        self.tempClusterList.append(temp_cluster)
        self.tempSpikeMatList.append(temp_spike_mat)
        self.tempSpikeTimeList.append(temp_spike_time)
        self.plotManualFlag = True
        self.resetManualFlag = True
        self.saveManualFlag = True

    def updateManualSortingView(self):
        try:
            n_clusters = self.number_of_clusters
        except:
            n_clusters = 0
        try:
            self.listWidget.close()
        except:
            pass
        try:
            self.listWidget = QtWidgets.QListWidget()
            self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
            for i in range(n_clusters):
                item = QtWidgets.QListWidgetItem("Cluster %i" % (i + 1))
                self.listWidget.addItem(item)
            self.listWidget.setCurrentItem(item)
            scroll_bar = QtWidgets.QScrollBar(self)
            scroll_bar.setStyleSheet("background : lightgreen;")
            self.listWidget.setVerticalScrollBar(scroll_bar)
            label = QtWidgets.QLabel("Select Clusters : ", self)
            label.setWordWrap(True)
            self.cluster_list_layout = QtWidgets.QVBoxLayout()
            self.cluster_list_layout.addWidget(label)
            self.cluster_list_layout.addWidget(self.listWidget)
            self.layout_manual_sorting.addLayout(self.cluster_list_layout, 0, 1)
        except:
            pass

    def onActManualSorting(self):
        try:
            act = self.manualActWidget.currentItem()
            clusters = self.listWidget.selectedItems()
            selected_clusters = [int(cl.text().strip('Cluster')) for cl in clusters]
            if act.text() == 'Merge':
                try:
                    self.temp_cluster = self.mergeManual(selected_clusters)
                    self.temp_spike_mat = self.spike_mat.copy()
                    self.temp_spike_time = self.spike_time.copy()
                    self.manualPreparingSorting(self.temp_spike_time, self.temp_spike_mat, self.temp_cluster)
                except:
                    pass
            elif act.text() == 'Remove':
                try:
                    self.temp_cluster = self.removeManual(selected_clusters)
                    self.temp_spike_mat = self.spike_mat.copy()
                    self.temp_spike_time = self.spike_time.copy()
                    self.manualPreparingSorting(self.temp_spike_time, self.temp_spike_mat, self.temp_cluster)
                except:
                    pass
            elif act.text() == 'Assign to nearest':
                try:
                    self.assignManual()
                    self.temp_spike_mat = self.spike_mat.copy()
                    self.temp_spike_time = self.spike_time.copy()
                    self.manualPreparingSorting(self.temp_spike_time, self.temp_spike_mat, self.temp_cluster)
                except:
                    pass
            elif act.text() == 'PCA Remove':
                try:
                    self.pcaRemoveManual()
                except:
                    pass
            elif act.text() == 'PCA Group':
                try:
                    self.pcaGroupManual()
                except:
                    pass
            elif act.text() == 'Resort':
                try:
                    self.resortManual()
                except:
                    pass
            else:
                pass
        except:
            self.statusBar().showMessage(self.tr("There is no clustering result!"), 2000)

    def onPlotManualSorting(self):
        if self.plotManualFlag:
            self.updateplotWaveForms(self.temp_spike_mat, self.temp_cluster)
            self.statusBar().showMessage(self.tr("Updating Spikes Waveforms..."))
            self.wait()
            self.update_plotRaw(self.temp_spike_time, self.temp_cluster)
            self.statusBar().showMessage(self.tr("Updating Raw Data Waveforms..."), 2000)
            self.plotManualFlag = False

    def onResetManualSorting(self):
        if self.resetManualFlag:
            self.tempSpikeMatList = []
            self.tempSpikeTimeList = []
            self.tempClusterList = []
            self.updateplotWaveForms(self.spike_mat, self.clusters)
            self.statusBar().showMessage(self.tr("Resetting Spikes Waveforms..."))
            self.wait()
            self.update_plotRaw(self.spike_time, self.clusters)
            self.statusBar().showMessage(self.tr("Raw Data Waveforms..."), 2000)
            self.resetManualFlag = False
            self.plotManualFlag = False
            self.saveManualFlag = False

    def onSaveManualSorting(self):
        if self.saveManualFlag:
            self.clusters = self.temp_cluster.copy()
            self.spike_mat = self.temp_spike_mat.copy()
            self.spike_time = self.temp_spike_time.copy()
            self.number_of_clusters = np.shape(np.unique(self.clusters))[0]
            self.statusBar().showMessage(self.tr("Updating Clustering Results..."))
            self.wait()
            res = self.user.save_sort_results(self.clusters)
            if res['stat']:
                self.statusBar().showMessage(self.tr("Done."))
                self.statusBar().showMessage(self.tr("Updating Plots..."), 2000)
                self.wait()
                self.updateplotWaveForms(self.spike_mat, self.clusters)
                self.wait()
                self.update_plotRaw(self.spike_time, self.clusters)
                self.wait()
                self.updateManualSortingView()
            else:
                self.statusBar().showMessage(self.tr("An error occurred!..."), 2000)

            self.saveManualFlag = False

    def onUndoManualSorting(self):
        try:
            self.tempClusterList.pop()
            self.tempSpikeMatList.pop()
            self.tempSpikeTimeList.pop()
            if (len(self.tempClusterList) != 0) and (len(self.tempSpikeMatList) != 0) and (len(self.tempSpikeTimeList) != 0):
                self.temp_cluster = self.tempClusterList[-1]
                self.temp_spike_mat = self.tempSpikeMatList[-1]
                self.temp_spike_time = self.tempSpikeTimeList[-1]
            else:
                self.temp_cluster = self.clusters.copy()
                self.temp_spike_mat = self.spike_mat.copy()
                self.temp_spike_time = self.spike_time.copy()
            self.statusBar().showMessage(self.tr("Updating Plots..."))
            self.wait()
            self.updateplotWaveForms(self.temp_spike_mat, self.temp_cluster)
            self.wait()
            self.update_plotRaw(self.temp_spike_time, self.temp_cluster)
            self.statusBar().showMessage(self.tr("...Done!"), 2000)
            self.wait()
        except:
            self.statusBar().showMessage(self.tr("There is no manual act for undoing!"), 2000)

    def mergeManual(self, selected_clusters):
        if len(selected_clusters) >= 2:
            self.statusBar().showMessage(self.tr("Merging..."))
            self.wait()
            sel_cl = selected_clusters[0] - 1
            temp = self.clusters.copy()
            for ind in selected_clusters:
                temp[temp == ind - 1] = sel_cl
            cl_ind = np.unique(temp)
            for i, ind in enumerate(cl_ind):
                temp[temp == ind] = i
            self.statusBar().showMessage(self.tr("...Merging Done!"), 2000)
            self.wait()
            return temp
        else:
            self.statusBar().showMessage(self.tr("For Merging you should select at least two clusters..."), 2000)

    def removeManual(self, selected_clusters):
        if len(selected_clusters) != 0:
            self.statusBar().showMessage(self.tr("Removing..."))
            self.wait()
            temp = self.clusters.copy()
            for sel_cl in selected_clusters:
                temp[temp == sel_cl-1] = -1
            cl_ind = np.sort(np.unique(temp))
            for i, ind in enumerate(cl_ind):
                if ind != -2:
                    temp[temp == ind] = i - 1
            self.statusBar().showMessage(self.tr("...Removing Done!"), 2000)
            return temp
        else:
           pass

    def assignManual(self):
        self.subwindow_assign.setVisible(True)
        try:
            n_clusters = self.number_of_clusters
        except:
            n_clusters = 0
        try:
            self.listSourceWidget.close()
            self.listTargetsWidget.close()
            self.assign_button.close()
            self.assign_close_button.close()

        except:
            pass
        try:
            self.listSourceWidget = QtWidgets.QListWidget()
            for i in range(n_clusters):
                item = QtWidgets.QListWidgetItem("Cluster %i" % (i + 1))
                self.listSourceWidget.addItem(item)
            self.listSourceWidget.setCurrentItem(item)
            scroll_bar = QtWidgets.QScrollBar(self)
            scroll_bar.setStyleSheet("background : lightgreen;")
            self.listSourceWidget.setVerticalScrollBar(scroll_bar)
            label = QtWidgets.QLabel("Source : ", self)
            label.setWordWrap(True)
            self.source_list_layout = QtWidgets.QVBoxLayout()
            self.source_list_layout.addWidget(label)
            self.source_list_layout.addWidget(self.listSourceWidget)
            self.layout_assign_manual.addLayout(self.source_list_layout, 0, 0)
            self.listTargetsWidget = QtWidgets.QListWidget()
            self.listTargetsWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
            for i in range(n_clusters):
                item_target = QtWidgets.QListWidgetItem("Cluster %i"%(i+1))
                self.listTargetsWidget.addItem(item_target)
            self.listTargetsWidget.setCurrentItem(item_target)
            self.listTargetsWidget.setVerticalScrollBar(scroll_bar)
            label2 = QtWidgets.QLabel("Targets : ", self)
            label2.setWordWrap(True)
            self.targets_list_layout = QtWidgets.QVBoxLayout()
            self.targets_list_layout.addWidget(label2)
            self.targets_list_layout.addWidget(self.listTargetsWidget)
            self.layout_assign_manual.addLayout(self.targets_list_layout, 0, 1)

            self.assign_button = QtWidgets.QPushButton(text='Assign')
            self.assign_button.pressed.connect(self.onAssignManualSorting)
            self.layout_assign_manual.addWidget(self.assign_button)

            self.assign_close_button = QtWidgets.QPushButton(text='Close')
            self.assign_close_button.pressed.connect(self.closeAssign)
            self.layout_assign_manual.addWidget(self.assign_close_button)

            self.widget_assign_manual.setLayout(self.layout_assign_manual)

        except:
            pass

    def onAssignManualSorting(self):
        source = self.listSourceWidget.currentItem()
        targets = self.listTargetsWidget.selectedItems()

        source_cluster = int(source.text().strip('Cluster')) - 1
        target_clusters = [int(cl.text().strip('Cluster')) - 1 for cl in targets]
        try:
            if len(target_clusters) >= 1:
                self.statusBar().showMessage(self.tr("Assigning Source Cluster to Targets..."))
                self.wait()

                temp_cluster = self.clusters.copy()
                temp_spike_mat = self.spike_mat.copy()
                temp_spike_time = self.spike_time.cop()

                source_spikes = self.spike_mat[self.clusters == source_cluster]
                source_ind = np.nonzero(self.clusters == source_cluster)

                target_avg = dict()
                for target in target_clusters:
                    target_avg[target] = np.average(self.spike_mat[self.clusters == target], axis=0)

                for data, ind in zip(source_spikes, source_ind):
                    min_diff = np.inf
                    for k, v in target_avg.items():
                        diff = np.sum(np.power(data - v, 2), axis=0)
                        if diff <= min_diff:
                            min_tar = k
                            min_diff = diff
                    temp_cluster[ind] = min_tar

                cl_ind = np.unique(temp_cluster)
                for i, ind in enumerate(cl_ind):
                    temp_cluster[temp_cluster == ind] = i
                self.statusBar().showMessage(self.tr("...Assigning to Nearest Clusters Done!"), 2000)
                self.wait()

                self.temp_cluster = temp_cluster
                self.temp_spike_mat = temp_spike_mat
                self.temp_spike_time = temp_spike_time
                self.manualPreparingSorting(self.temp_spike_time, self.temp_spike_mat, self.temp_cluster)

            else:
                self.statusBar().showMessage(self.tr("You Should Choose One Source and at least One Target..."), 2000)
        except:
            pass

    def closeAssign(self):
        self.subwindow_assign.setVisible(False)

    def pcaRemoveManual(self):
        spikes = self.spike_mat.copy()
        pca = sklearn.decomposition.PCA(2)
        spikes_pca = pca.fit_transform(spikes)
        fig, ax = plt.subplots()
        h, x_edges, y_edges, image = ax.hist2d(spikes_pca[:, 0], spikes_pca[:, 1], bins=(50, 50), cmap=plt.cm.jet)
        selector = SelectFromCollection(ax, h)
        temp_clusters = None
        temp_spike_mat = None
        temp_spike_time = None

        def accept(event):
            global temp_clusters, temp_spike_mat, temp_spike_time
            if event.key == "enter":
                selected_ind = np.squeeze([np.logical_and(np.logical_and(selector.min_point[0] < spikes_pca[:, 0],
                                                                         spikes_pca[:, 0] < selector.max_point[0]),
                                                          np.logical_and(selector.min_point[1] < spikes_pca[:, 1],
                                                                         spikes_pca[:, 1] < selector.max_point[1]))])
                temp_clusters = self.clusters[selected_ind]
                temp_spike_mat = self.spike_mat[selected_ind]
                temp_spike_time = self.spike_time[selected_ind]
                cl_ind = np.unique(temp_clusters)
                for i, ind in enumerate(cl_ind):
                    temp_clusters[temp_clusters == ind] = i
                self.assign_temp(temp_spike_time, temp_spike_mat, temp_clusters)
                self.manualPreparingSorting(self.temp_spike_time, self.temp_spike_mat, self.temp_cluster)
                selector.disconnect()
                ax.set_title("")
                fig.canvas.draw()
                plt.close()

        fig.canvas.mpl_connect("key_press_event", accept)
        ax.set_title("Press enter to accept selected points.")
        plt.show()

    def pcaGroupManual(self):
        spikes = self.spike_mat.copy()
        pca = sklearn.decomposition.PCA(2)
        spikes_pca = pca.fit_transform(spikes)
        fig, ax = plt.subplots()
        h, x_edges, y_edges, image = ax.hist2d(spikes_pca[:, 0], spikes_pca[:, 1], bins=(50, 50), cmap=plt.cm.jet)
        selector = SelectFromCollection(ax, h)
        temp_clusters = None
        temp_spike_mat = None
        temp_spike_time = None

        def accept(event):
            global temp_clusters, temp_spike_mat, temp_spike_time
            if event.key == "enter":
                selected_ind = np.squeeze([np.logical_and(np.logical_and(selector.min_point[0] < spikes_pca[:, 0],
                                                                         spikes_pca[:, 0] < selector.max_point[0]),
                                                          np.logical_and(selector.min_point[1] < spikes_pca[:, 1],
                                                                         spikes_pca[:, 1] < selector.max_point[1]))])
                n_cluster = len(np.unique(self.clusters))
                temp_clusters = np.empty(self.clusters.shape)
                for i in range(len(selected_ind)):
                    if selected_ind[i]:
                        temp_clusters[i] = n_cluster
                    else:
                        temp_clusters[i] = self.clusters[i]
                temp_spike_mat = self.spike_mat
                temp_spike_time = self.spike_time
                self.assign_temp(temp_spike_time, temp_spike_mat, temp_clusters)
                self.manualPreparingSorting(self.temp_spike_time, self.temp_spike_mat, self.temp_cluster)
                selector.disconnect()
                ax.set_title("")
                fig.canvas.draw()
                plt.close()

        fig.canvas.mpl_connect("key_press_event", accept)
        ax.set_title("Press enter to accept selected points.")
        plt.show()

    def resortManual(self):
        self.subwindow_resort.setVisible(True)
        try:
            n_clusters = self.number_of_clusters
        except:
            n_clusters = 0

        try:
            self.listResortWidget.close()
            self.resort_button.close()
            self.resort_close_button.close()
        except:
            pass

        try:
            self.listResortWidget = QtWidgets.QListWidget()
            self.listResortWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
            for i in range(n_clusters):
                item = QtWidgets.QListWidgetItem("Cluster %i" % (i + 1))
                self.listResortWidget.addItem(item)
            self.listResortWidget.setCurrentItem(item)
            scroll_bar = QtWidgets.QScrollBar(self)
            scroll_bar.setStyleSheet("background : lightgreen;")
            self.listResortWidget.setVerticalScrollBar(scroll_bar)
            label = QtWidgets.QLabel("Select Clusters : ", self)
            label.setWordWrap(True)

            self.resort_list_layout = QtWidgets.QVBoxLayout()
            self.resort_list_layout.addWidget(label)
            self.resort_list_layout.addWidget(self.listResortWidget)
            self.layout_resort_manual.addLayout(self.resort_list_layout, 0, 0)

            self.resort_button = QtWidgets.QPushButton(text='Resort')
            self.resort_button.pressed.connect(self.onResortManualSorting)
            self.layout_resort_manual.addWidget(self.resort_button)

            self.resort_close_button = QtWidgets.QPushButton(text='Close')
            self.resort_close_button.pressed.connect(self.closeResort)
            self.layout_resort_manual.addWidget(self.resort_close_button)

            self.widget_resort_manual.setLayout(self.layout_resort_manual)
        except Exception as e:
            print('erro is : ', e)

    def onResortManualSorting(self):
        selected = self.listResortWidget.selectedItems()
        selected_clusters = [int(cl.text().strip('Cluster')) - 1 for cl in selected]
        logical = np.array([False for cl in self.clusters])
        for cl in selected_clusters:
            logical = np.array(np.logical_or(logical, self.clusters==cl-1))
        if self.user is None:
            QtWidgets.QMessageBox.critical(self, "Not Signed In", "First sign in to the server!")
            return
        config_sort = self.read_config_sort()
        self.statusBar().showMessage(self.tr("Starting Resort..."))
        self.wait()
        res = self.user.start_resorting(logical)
        # if res['stat']:
        #     self.statusBar().showMessage(self.tr("Resorting Done."), 2500)
        #     res = self.user.get_sorting_result()
        #     if res['stat']:
        #         self.clusters = res['clusters']
        #         self.statusBar().showMessage(self.tr("Clusters Waveforms..."), 2500)
        #         self.wait()
        #         self.updateplotWaveForms(self.spike_mat, self.clusters)
        #         self.wait()
        #         self.update_plotRaw(self.spike_time, self.clusters)
        #         self.wait()
        #         self.updateManualSortingView()
        # else:
        #     self.statusBar().showMessage(self.tr("Sorting got error"))


    def closeResort(self):
        self.subwindow_resort.setVisible(False)

    def assign_temp(self, spikes_time, spikes_mat, clusters):
        self.temp_spike_mat = spikes_mat
        self.temp_spike_time = spikes_time
        self.temp_cluster = clusters

    def loadDefaultProject(self):
            flag_raw = False
            flag_update_raw = False
            res = self.user.get_config_detect()
            if res['stat']:
                self.update_config_detect(res['config'])

            res = self.user.get_config_sort()
            if res['stat']:
                self.update_config_sort(res['config'])

            res = self.user.get_raw_data()
            if res['stat']:
                self.raw = res['raw']
                self.statusBar().showMessage(self.tr("Plotting..."), 2500) 
                self.wait()    
                flag_raw = True

            res = self.user.get_detection_result()
            if res['stat']:
                self.spike_mat = res['spike_mat']
                self.spike_time = res['spike_time']
                self.plotDetectionResult()
                self.plotWaveForms()

            res = self.user.get_sorting_result()
            if res['stat']:
                self.clusters = res['clusters']
                self.updateplotWaveForms(self.spike_mat, self.clusters)
                self.wait()
                flag_update_raw = True
                self.updateManualSortingView()

            if flag_raw:
                if flag_update_raw:
                    self.update_plotRaw(self.spike_time, self.clusters)
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
