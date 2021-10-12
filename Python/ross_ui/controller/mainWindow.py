from view.mainWindow import MainWindow
from PyQt5 import QtCore, QtWidgets, QtGui
from controller.signin import SigninApp as signin_form
from controller.serverAddress import ServerApp as server_form
from controller.rawSelect import RawSelectApp as raw_form
from controller.projectSelect import projectSelectApp as project_form
from controller.saveAs import SaveAsApp as save_as_form
from controller.hdf5 import HDF5Plot
import sys, os
import scipy.io as sio
import numpy as np
from nptdms import TdmsFile
import time
import sklearn.decomposition as decom
import pyqtgraph.opengl as gl
from controller.multiline import MultiLine
import pyqtgraph

icon_path = './view/icons/'

class MainApp(MainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        # initial values for software options
        self.url = 'http://127.0.0.1:5000/'
        self.user = None
        self.user_name = None
        self.current_project = None

        self.startDetection.pressed.connect(self.onDetect)
        self.startSorting.pressed.connect(self.onSort)

    def onUserAccount(self):
        if self.user == None:
            self.open_signin_dialog()

    def onImportRaw(self):
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(self,
            self.tr("Open file"),
            os.getcwd(),
            self.tr("Raw Files(*.mat *.csv *.tdms)")
        )
        # Return if user did not select a file.
        if not filename:
            return

        if not os.path.isfile(filename):
            raise NoSuchFileError(filename)
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
            # print(type(tdms_file))
            i = 0
            for group in tdms_file.groups():
                df = tdms_file.object(group).as_dataframe()

                # print(df.head())
                variables = list(df.keys())

                print(df.keys())
                print(df.shape)
                i = i + 1
                print(i)

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
        print(config_sort)
        self.statusBar().showMessage(self.tr("Sorting Started..."))
        self.wait()
        res = self.user.start_sorting(config_sort)
        if res['stat']:
            self.statusBar().showMessage(self.tr("Sorting Done."), 2500)
            res = self.user.get_sorting_result()
            if res['stat']:
                pass
                # self.spike_mat = res['spike_mat']
                # self.spike_time = res['spike_time']
                # self.statusBar().showMessage(self.tr("Plotting..."), 2500)
                # self.wait()
                # self.plotDetectionResult()
                # self.plotWaveForms()
        
    def plotRaw(self):
        curve = HDF5Plot()
        curve.setHDF5(self.raw)
        self.widget_raw.clear()
        # self.widget_raw.removeItem(self.widget_raw.)
        self.widget_raw.addItem(curve)
        self.widget_raw.setXRange(0,10000)
        self.widget_raw.showGrid(x=True, y=True)
        self.widget_raw.setMouseEnabled(y=False)

    def plotWaveForms(self):

        print(np.shape(self.spike_mat))
        self.widget_waveform.clear()
        x = np.empty(np.shape(self.spike_mat))
        x[:] = np.arange(np.shape(self.spike_mat)[1])[np.newaxis, :]
        # lines = MultiLine(x, self.spike_mat)
        # self.widget_waveform.addItem(lines)
        self.widget_waveform.showGrid(x=True, y=True)

        # self.widget_waveform.disableAutoRange()
        # for i in range(len(self.spike_mat)):
        #     self.widget_waveform.plot(self.spike_mat[i, :])
        # self.widget_waveform.autoPixelRange()


        self.widget_waveform.enableAutoRange(False, False)
        if np.shape(self.spike_mat)[0] > 200:
            # spike_mat = np.random.choice(self.spike_mat, size=2000, replace=False)
            ind = np.arange(self.spike_mat.shape[0])
            np.random.shuffle(ind)
            spike_mat = self.spike_mat[ind[:200], :]
        else:
            spike_mat = self.spike_mat
        for i in range(len(spike_mat)):
            self.widget_waveform.addItem(pyqtgraph.PlotCurveItem(x[i, :], spike_mat[i, :]))
        self.widget_waveform.autoRange()

    def plotDetectionResult(self):
        pca = decom.PCA(n_components=2)
        pca_spikes = pca.fit_transform(self.spike_mat)
        print(pca_spikes.shape)
        hist, xedges, yedges = np.histogram2d(pca_spikes[:, 0], pca_spikes[:, 1], bins=100)
        # self.plot_clusters.setImage(hist[0])
        xcenters = (xedges[:-1] + xedges[1:]) / 2

        ycenters = (yedges[:-1] + yedges[1:]) / 2

        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.setSize(100, 100)
        gx.translate(0, 50, 50)
        self.plot_clusters.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.setSize(100, 100)
        gy.translate(50, 0, 50)
        self.plot_clusters.addItem(gy)
        gz = gl.GLGridItem()
        gz.setSize(100, 100)
        gz.translate(50, 50, 0)
        self.plot_clusters.addItem(gz)

        # regular grid of starting positions
        pos = np.mgrid[0:100, 0:100, 0:1].reshape(3, 100, 100).transpose(1, 2, 0)
        # pos = np.mgrid[list(xcenters), list(ycenters), 0:1].reshape(3, 100, 100).transpose(1, 2, 0)
        # fixed widths, random heights
        # pos = np.meshgrid(xcenters, ycenters)
        size = np.empty((100, 100, 3))
        size[..., 0:2] = 1
        size[..., 2] = 100*(hist-np.amin(hist))/(np.amax(hist)-np.amin(hist))#hist#np.random.normal(size=(10, 10))
        # size[0:10, 0:10,2] = 100

        bg = gl.GLBarGraphItem(pos, size)
        # roi = pyqtgraph.CircleROI([80, 50], [20, 20], pen=(4, 9))

        # def update(roi):
        #     img1b.setImage(roi.getArrayRegion(arr, img1a), levels=(0, arr.max()))
        #     v1b.autoRange()

        # roi.sigRegionChanged.connect(update)

        # self.plot_clusters.addItem(roi)

        # update(roi)
        
        self.plot_clusters.addItem(bg)
        # w.setImage(h[0])
        # self.plot_clusters.addItem(hist)
        # curve = HDF5Plot()
        # curve.setHDF5(self.detection_result)
        # self.plot_clusters.clear()
        # self.widget_raw.removeItem(self.widget_raw.)
        # self.plot_clusters.addItem(curve)
        # self.widget_raw.setXRange(0, 10000)
        # self.widget_raw.showGrid(x=True, y=True)
        # self.widget_raw.setMouseEnabled(y=False)

    def onRefresh(self):
        pass

    def onToggleStatusBar(self):
        """Toggles the visibility of the status bar."""
        self.statusBar().setVisible(self.statusbarAct.isChecked())

    def onClusters(self):
        """Toggles the visibility of the clusters."""
        self.subwindow_clusters.setVisible(self.clustersAct.isChecked())  

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

    def wait(self, duration=2.0):
        QtWidgets.QApplication.processEvents()
        time.sleep(duration)

    def loadDefaultProject(self):      
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
                self.plotRaw()

            res = self.user.get_detection_result()
            if res['stat']:
                self.spike_mat = res['spike_mat']
                self.spike_time = res['spike_time']
                self.plotDetectionResult()
                self.plotWaveForms()
            

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
