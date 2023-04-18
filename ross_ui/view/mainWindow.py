from PyQt5 import QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QMdiArea, QSizePolicy
from pyqtgraph import PlotWidget

from view.PCAManualWidget import PCAManualWidget

icon_path = './view/icons/'

__version__ = "1.0.0"


# -----------------------------------------------------------------------------
#  Main window class.
# -----------------------------------------------------------------------------
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.AppTitle = self.tr("ROSS")
        self.AppVersion = __version__
        self.is_first_time = True
        # Setup main window.
        self.setWindowTitle(self.AppTitle)
        # self.setWindowIcon(QtGui.QIcon.fromTheme('utilities-system-monitor'))
        # self.w = 1280
        # self.h = 720
        # self.resize(self.w, self.h)

        # for test
        c1 = {'index': 0}
        c2 = {'index': 1}
        c3 = {'index': 2}
        c4 = {'index': 3}
        c5 = {'index': 4}

        self.clusters = [c1, c2, c3, c4, c5]

        self.mdiArea = QMdiArea(self)
        self.mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)

        self.createActions()
        self.createSubWindows()

        self.createToolbars()
        self.createMenubar()
        self.createStatusbar()
        self.installEventFilter(self)

    def createActions(self):
        """Create actions used in menu bar and tool bars."""

        # Action for opening a new connections file.
        self.openAct = QtWidgets.QAction(self.tr("&Open..."), self)
        self.openAct.setShortcut(QtGui.QKeySequence.Open)
        self.openAct.setStatusTip(self.tr("Open an existing project"))
        self.openAct.setIcon(QtGui.QIcon(icon_path + "Folder.png"))
        self.openAct.setEnabled(False)
        self.openAct.triggered.connect(self.onOpen)
        self.openAct.setIconVisibleInMenu(True)

        self.closeAct = QtWidgets.QAction(self.tr("&Close"), self)
        self.closeAct.setShortcuts(QtGui.QKeySequence.Close)
        self.closeAct.setStatusTip(self.tr("Close the current project"))
        self.closeAct.setIcon(QtGui.QIcon(icon_path + "Close.png"))
        self.closeAct.setEnabled(False)

        self.saveAct = QtWidgets.QAction(self.tr("&Save"), self)
        self.saveAct.setShortcut(QtGui.QKeySequence.Save)
        self.saveAct.setStatusTip(self.tr("Save"))
        self.saveAct.setIcon(QtGui.QIcon(icon_path + "Save.png"))
        self.saveAct.setEnabled(False)
        self.saveAct.triggered.connect(self.onSave)

        self.saveAsAct = QtWidgets.QAction(self.tr("&Save As..."), self)
        self.saveAsAct.setShortcut(QtGui.QKeySequence.SaveAs)
        self.saveAsAct.setStatusTip(self.tr("Save as..."))
        self.saveAsAct.setIcon(QtGui.QIcon(icon_path + "SaveAs.png"))
        self.saveAsAct.setEnabled(False)
        self.saveAsAct.triggered.connect(self.onSaveAs)

        self.importRawAct = QtWidgets.QAction(self.tr("&Raw Data"), self)
        self.importRawAct.setStatusTip(self.tr("Import Raw Data"))
        self.importRawAct.setIcon(QtGui.QIcon(icon_path + "Import.png"))
        self.importRawAct.triggered.connect(self.onImportRaw)

        self.importDetectedAct = QtWidgets.QAction(self.tr("&Detection Result"), self)
        self.importDetectedAct.setStatusTip(self.tr("Import Detection Result"))
        self.importDetectedAct.setIcon(QtGui.QIcon(icon_path + "Import.png"))
        self.importDetectedAct.triggered.connect(self.onImportDetected)

        self.importSortedAct = QtWidgets.QAction(self.tr("&Sorting Result"), self)
        self.importSortedAct.setStatusTip(self.tr("Import Sorting Result"))
        self.importSortedAct.setIcon(QtGui.QIcon(icon_path + "Import.png"))
        self.importSortedAct.triggered.connect(self.onImportSorted)

        self.exportRawAct = QtWidgets.QAction(self.tr("&Raw Data"), self)
        self.exportRawAct.setStatusTip(self.tr("Export Raw Data"))
        self.exportRawAct.setIcon(QtGui.QIcon(icon_path + "Export.png"))
        # self.exportRawAct.triggered.connect(self.onExportRaw)

        self.exportDetectedAct = QtWidgets.QAction(self.tr("&Detection Result"), self)
        self.exportDetectedAct.setStatusTip(self.tr("Export Detection Result"))
        self.exportDetectedAct.setIcon(QtGui.QIcon(icon_path + "Export.png"))
        # self.exportDetectedAct.triggered.connect(self.onExportDetected)

        self.exportSortedAct = QtWidgets.QAction(self.tr("&Sorting Result"), self)
        self.exportSortedAct.setStatusTip(self.tr("Export Sorting Result"))
        self.exportSortedAct.setIcon(QtGui.QIcon(icon_path + "Export.png"))
        # self.exportSortedAct.triggered.connect(self.onExportSorted)

        self.mergeAct = QtWidgets.QAction(self.tr("&Merge"), self)
        self.mergeAct.setStatusTip(self.tr("Merge the selected clusters"))
        self.mergeAct.setIcon(QtGui.QIcon(icon_path + "Merge.png"))
        # self.exportAct.triggered.connect(self.onMerge)

        self.removeAct = QtWidgets.QAction(self.tr("&Remove"), self)
        self.removeAct.setStatusTip(self.tr("Remove the selected clusters"))
        self.removeAct.setIcon(QtGui.QIcon(icon_path + "Remove.png"))
        # self.removeAct.triggered.connect(self.onRemove)

        self.resortAct = QtWidgets.QAction(self.tr("&Resort"), self)
        self.resortAct.setStatusTip(self.tr("Resort the selected clusters"))
        self.resortAct.setIcon(QtGui.QIcon(icon_path + "Resort.png"))
        # self.resortAct.triggered.connect(self.onRsort)

        self.denoiseAct = QtWidgets.QAction(self.tr("&Denoise"), self)
        self.denoiseAct.setStatusTip(self.tr("Open denoise tool"))
        self.denoiseAct.setIcon(QtGui.QIcon(icon_path + "Denoise.png"))
        # self.denoiseAct.triggered.connect(self.onDenoise)

        self.assignAct = QtWidgets.QAction(self.tr("&Assign to Nearest"), self)
        self.assignAct.setStatusTip(self.tr("Open Assign to Nearest tool"))
        self.assignAct.setIcon(QtGui.QIcon(icon_path + "Assign.png"))
        # self.assignAct.triggered.connect(self.onAssign)

        self.groupAct = QtWidgets.QAction(self.tr("&PCA Group"), self)
        self.groupAct.setStatusTip(self.tr("Open PCA Group tool"))
        self.groupAct.setIcon(QtGui.QIcon(icon_path + 'Group.png'))
        # self.groupAct.triggered.connect(self.onGroup)

        self.pcaRemoveAct = QtWidgets.QAction(self.tr("&PCA Remove"), self)
        self.pcaRemoveAct.setStatusTip(self.tr("Open PCA Remove tool"))
        self.pcaRemoveAct.setIcon(QtGui.QIcon(icon_path + 'RemovePCA.png'))
        # self.pcaRemoveAct.triggered.connect(self.onPcaRemove)

        self.undoAct = QtWidgets.QAction(self.tr("&Undo"), self)
        self.undoAct.setStatusTip(self.tr("Undo"))
        self.undoAct.setIcon(QtGui.QIcon(icon_path + 'Undo.png'))
        self.undoAct.setShortcut(QtGui.QKeySequence.Undo)
        # self.undoAct.triggered.connect(self.onUndo)

        self.clustersListAct = []
        for c in self.clusters:
            temp = QtWidgets.QAction("Cluster " + str(c['index'] + 1), self)
            temp.setCheckable(True)
            self.clustersListAct.append(temp)

        # Action for refreshing readable items.
        self.refreshAct = QtWidgets.QAction(self.tr("&Refresh"), self)
        self.refreshAct.setShortcut(QtGui.QKeySequence.Refresh)
        self.refreshAct.setStatusTip(self.tr("Refresh by reading data from file"))
        self.refreshAct.setIcon(QtGui.QIcon(icon_path + 'Refresh.png'))
        self.refreshAct.triggered.connect(self.onRefresh)

        # Action for toggling status bar.
        self.statusbarAct = QtWidgets.QAction(self.tr("&Statusbar"), self)
        self.statusbarAct.setCheckable(True)
        self.statusbarAct.setChecked(True)
        self.statusbarAct.setStatusTip(self.tr("Show or hide the statusbar in the current window"))
        self.statusbarAct.toggled.connect(self.onToggleStatusBar)

        # Actions for toggling subwindows
        # self.clustersAct = QtWidgets.QAction(self.tr("&Clusters"), self)
        # self.clustersAct.setCheckable(True)
        # self.clustersAct.setChecked(True)
        # self.clustersAct.setStatusTip(self.tr("Show or hide the clusters window"))
        # self.clustersAct.triggered.connect(self.onPlotClusters)

        self.waveformsAct = QtWidgets.QAction(self.tr("&Waveforms"), self)
        self.waveformsAct.setCheckable(True)
        self.waveformsAct.setChecked(True)
        self.waveformsAct.setStatusTip(self.tr("Show or hide the waveforms window"))
        self.waveformsAct.triggered.connect(self.onWaveforms)

        self.rawDataAct = QtWidgets.QAction(self.tr("&Raw Data"), self)
        self.rawDataAct.setCheckable(True)
        self.rawDataAct.setChecked(True)
        self.rawDataAct.setStatusTip(self.tr("Show or hide the raw data window"))
        self.rawDataAct.triggered.connect(self.onRawData)

        self.settingsAct = QtWidgets.QAction(self.tr("&Settings"), self)
        self.settingsAct.setCheckable(True)
        self.settingsAct.setChecked(True)
        self.settingsAct.setStatusTip(self.tr("Show or hide the settings window"))
        self.settingsAct.triggered.connect(self.onSettings)

        # Actions to show about dialog.
        self.aboutAct = QtWidgets.QAction(self.tr("&About"), self)
        self.aboutAct.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F1))
        self.aboutAct.triggered.connect(self.onAbout)

        # run actions
        self.detectAct = QtWidgets.QAction(self.tr("&Detection"), self)
        self.detectAct.setStatusTip(self.tr("Start Detection"))
        self.detectAct.setIcon(QtGui.QIcon(icon_path + 'Detect.png'))
        self.detectAct.triggered.connect(self.onDetect)

        self.sortAct = QtWidgets.QAction(self.tr("&Sort"), self)
        self.sortAct.setStatusTip(self.tr("Start Automatic Sorting"))
        self.sortAct.setIcon(QtGui.QIcon(icon_path + 'Sort.png'))
        self.sortAct.triggered.connect(self.onSort)

        # self.batchAct = QtWidgets.QAction(self.tr("&Batch Sorting"), self)
        # self.batchAct.setStatusTip(self.tr("Start Batch sorting"))
        # self.batchAct.setIcon(QtGui.QIcon(icon_path + 'Batch.png'))
        # self.batchAct.triggered.connect(self.onBatch)

        # log in action
        self.logInAct = QtWidgets.QAction(QtGui.QIcon(icon_path + 'unverified.png'), self.tr("&Sign In/Up"), self)
        self.logInAct.setStatusTip(self.tr("Sign In"))
        self.logInAct.triggered.connect(self.open_signin_dialog)

        # log out action
        self.logOutAct = QtWidgets.QAction(QtGui.QIcon(icon_path + 'signout.png'), self.tr("&Sign Out"), self)
        self.logOutAct.setStatusTip(self.tr("Sign Out"))
        self.logOutAct.triggered.connect(self.onSignOut)
        self.logOutAct.setEnabled(False)

        self.accountButton = QtWidgets.QPushButton(QtGui.QIcon(icon_path + 'unverified.png'), None, self)
        self.accountButton.setStatusTip(self.tr("Sign In/Up"))
        self.accountButton.clicked.connect(self.onUserAccount)
        self.accountButton.setFlat(True)

        # server address act
        self.serverAddressAct = QtWidgets.QAction(QtGui.QIcon(icon_path + 'server.png'), self.tr("&Server Address"),
                                                  self)
        self.serverAddressAct.triggered.connect(self.open_server_dialog)

        # mode act
        self.plotAct = QtWidgets.QAction(self.tr("&Mode"), self)
        # self.plotAct.setCheckable(True)
        # self.plotAct.setChecked(False)
        self.plotAct.setStatusTip(self.tr("Plotting Clusters"))
        self.plotAct.triggered.connect(self.onVisPlot)

        self.detect3dAct = QtWidgets.QAction(self.tr("&Detection Histogram 3D"))
        # self.detect3dAct.setCheckable(True)
        # self.detect3dAct.setChecked(False)
        self.detect3dAct.setStatusTip(self.tr("Plotting 3D histogram of detection result"))
        self.detect3dAct.triggered.connect(self.onDetect3D)

        self.clusterwaveAct = QtWidgets.QAction(self.tr("&Plotting Clusters Waveforms"))
        # self.clusterwaveAct.setCheckable(True)
        # self.clusterwaveAct.setChecked(False)
        self.clusterwaveAct.setStatusTip(self.tr("Plotting Waveforms of Each Cluster"))

        self.clusterwaveAct.triggered.connect(self.onPlotClusterWave)
        # self.clusterwaveAct.triggered.connect(self.updateplotWaveForms)

        self.livetimeAct = QtWidgets.QAction(self.tr("&Plotting LiveTime"))
        # self.livetimeAct.setCheckable(True)
        # self.livetimeAct.setChecked(False)
        self.livetimeAct.setStatusTip(self.tr("Plotting Histogram of LiveTime"))
        self.livetimeAct.triggered.connect(self.onPlotLiveTime)

        self.isiAct = QtWidgets.QAction(self.tr("&Plotting ISI Histogram"))
        # self.isiAct.setCheckable(True)
        # self.isiAct.setChecked(False)
        self.isiAct.setStatusTip(self.tr("Plotting Inter Spike Interval Histogram"))
        self.isiAct.triggered.connect(self.onPlotIsi)

        self.plot3dAct = QtWidgets.QAction(self.tr("&3D Plot"))
        # self.plot3dAct.setCheckable(True)
        # self.plot3dAct.setChecked(False)
        self.plot3dAct.setStatusTip(self.tr("Plotting 3D plots"))
        self.plot3dAct.triggered.connect(self.onPlot3d)

    def createToolbars(self):
        """Create tool bars and setup their behaviors (floating or static)."""
        self.toolbar = self.addToolBar(self.tr("Toolbar"))
        # self.toolbar.addAction(self.serverAddressAct)
        # self.toolbar.addSeparator()
        #
        # self.toolbar.addAction(self.openAct)
        # self.toolbar.addAction(self.saveAct)
        # self.toolbar.addSeparator()
        #
        # self.toolbar.addAction(self.importRawAct)
        # self.toolbar.addAction(self.importDetectedAct)
        # self.toolbar.addAction(self.importSortedAct)
        # self.toolbar.addAction(self.exportRawAct)
        # self.toolbar.addAction(self.exportDetectedAct)
        # self.toolbar.addAction(self.exportSortedAct)
        # self.toolbar.addSeparator()
        #
        # self.toolbar.addAction(self.mergeAct)
        # self.toolbar.addAction(self.removeAct)
        # self.toolbar.addAction(self.resortAct)
        # self.toolbar.addAction(self.denoiseAct)
        # self.toolbar.addAction(self.assignAct)
        # self.toolbar.addAction(self.groupAct)
        # self.toolbar.addAction(self.pcaRemoveAct)
        # self.toolbar.addAction(self.undoAct)
        # self.toolbar.addSeparator()
        #
        # self.toolbar.addAction(self.detectAct)
        # self.toolbar.addAction(self.sortAct)
        # self.toolbar.addAction(self.batchAct)
        # self.toolbar.addSeparator()
        # self.toolbar.addAction(self.refreshAct)
        # self.toolbar.addSeparator()
        spacerWidget = QtWidgets.QWidget()
        spacerWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        spacerWidget.setVisible(True)
        self.toolbar.addWidget(spacerWidget)
        # self.toolbar.addAction(self.serverAddressAct)
        self.toolbar.addWidget(self.accountButton)

        # Create action for toggling the tool bar here.
        self.toolbarAct = self.toolbar.toggleViewAction()  # Get predefined action from toolbar.
        self.toolbarAct.setStatusTip(self.tr("Show or hide the toolbar in the current window"))
        self.addToolBarBreak()
        self.toolbar_clusters = QtWidgets.QToolBar('Clusters Indices')

    def createMenubar(self):
        """Create menu bar with entries."""

        # Menu entry for file actions.
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        # self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.closeAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.importMenu = self.fileMenu.addMenu(self.tr("&Import"))
        self.importMenu.addActions((self.importRawAct, self.importDetectedAct, self.importSortedAct))
        self.exportMenu = self.fileMenu.addMenu(self.tr("&Export"))
        self.exportMenu.addActions((self.exportRawAct, self.exportDetectedAct, self.exportSortedAct))

        # ------------------- tool from menu ------------------
        # Menu entry for tool acions
        # self.toolMenu = self.menuBar().addMenu(self.tr("&Tools"))
        # self.toolMenu.addActions((self.mergeAct, self.removeAct, self.resortAct, self.denoiseAct, self.assignAct,
        #                           self.groupAct, self.pcaRemoveAct, self.undoAct))

        # run menu
        self.runMenu = self.menuBar().addMenu(self.tr("&Run"))
        self.runMenu.addAction(self.detectAct)
        self.runMenu.addAction(self.sortAct)
        # self.runMenu.addAction(self.batchAct)

        # Menu entry for view actions.
        self.viewMenu = self.menuBar().addMenu(self.tr("&View"))
        self.viewMenu.addAction(self.refreshAct)
        self.viewMenu.addSeparator()

        self.viewMenu.addAction(self.waveformsAct)
        self.viewMenu.addAction(self.rawDataAct)
        self.viewMenu.addAction(self.settingsAct)
        self.viewMenu.addSeparator()

        self.viewMenu.addAction(self.toolbar.toggleViewAction())
        self.viewMenu.addAction(self.statusbarAct)

        # Menu entry for visualization
        self.visMenu = self.menuBar().addMenu(self.tr("&Visualization"))
        self.visMenu.addAction(self.detect3dAct)
        self.visMenu.addAction(self.clusterwaveAct)
        self.visMenu.addAction(self.livetimeAct)
        self.visMenu.addAction(self.isiAct)
        self.visMenu.addAction(self.plot3dAct)

        # Menu entry for options
        self.optionMenu = self.menuBar().addMenu(self.tr("&Options"))
        self.optionMenu.addAction(self.serverAddressAct)
        self.optionMenu.addAction(self.logInAct)
        self.optionMenu.addAction(self.logOutAct)

        # Menu entry for help actions.
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAct)

    def createStatusbar(self):
        """Create status bar and content."""
        self.statusBar()
        self.statusBar().showMessage(self.tr("Ready."))

    def showEvent(self, event):
        if self.isVisible() and self.is_first_time:
            desktop_size = QtWidgets.QDesktopWidget().screenGeometry()
            self.w = desktop_size.width()
            self.h = desktop_size.height()
            self.resize(self.w, self.h)
            self.w_mdi = self.mdiArea.geometry().width()
            self.h_mdi = self.mdiArea.geometry().height() - self.toolbar.height() / 2 - self.statusBar().height() - self.toolbar_clusters.height() / 2
            self.resize(800, 600)
            self.showMaximized()
            self.align_subwindows()
            self.is_first_time = False

    def align_subwindows(self):

        self.subwindow_waveforms.setGeometry(0, 0, int(self.w_mdi * 3 / 8), int(self.h_mdi * (2.65) / 3))
        self.subwindow_pca_clusters.setGeometry(int(self.w_mdi * 3 / 8), 0, int(self.w_mdi * (2.35) / 8),
                                                int(self.h_mdi * (2.65) / 3))
        self.subwindow_pca_clusters.setVisible(True)
        self.subwindow_pca_histograms.setGeometry(int(self.w_mdi * 5.35 / 8), 0, int(self.w_mdi * (2.35) / 8),
                                                  int(self.h_mdi * (2.65) / 3))
        self.subwindow_pca_histograms.setVisible(True)

        self.subwindow_raw.setGeometry(0, int(self.h_mdi * (2.65) / 3), int(self.w_mdi * 5 / 8),
                                       int(self.h_mdi * (1.26) / 3))
        self.subwindow_settings.setGeometry(int(self.w_mdi * 5 / 8), int(self.h_mdi * (2.65) / 3),
                                            int(self.w_mdi * (2.7) / 8), int(self.h_mdi * (1.26) / 3))

        self.subwindow_detect3d.setGeometry(0, 0, int(self.w_mdi / 2), int(self.h_mdi * 2 / 3))
        self.subwindow_detect3d.setVisible(False)

        self.subwindow_3d.setGeometry(0, 0, int(self.w_mdi / 2), int(self.h_mdi * 2 / 3))
        self.subwindow_3d.setVisible(False)

        self.subwindow_pca_manual.setVisible(False)

        self.subwindow_assign.setGeometry(int(self.w_mdi / 2), int(self.h_mdi / 2), int(self.w_mdi / 4),
                                          int(self.h_mdi * 1 / 3))
        self.subwindow_assign.setVisible(False)

        self.mdiArea.activateNextSubWindow()

    def createSubWindows(self):
        # waveforms subwindow
        self.widget_waveform = PlotWidget()

        # clusters subwindow
        self.plot_histogram_pca = pg.GraphicsLayoutWidget()
        self.plot_clusters_pca = pg.GraphicsLayoutWidget()

        # self.widget_clusters = QtWidgets.QWidget()#PlotWidget()
        # layout_sub_clusters3d = QtWidgets.QGridLayout()
        # layout_sub_clusters = pg.ViewBox()
        # layout_sub_clusters.addWidget(axisWidget)
        # layout_sub_clusters.addWidget(self.plot_clusters)
        # self.widget_clusters.setLayout(layout_sub_clusters)
        # self.widget_clusters.se

        # raw data
        self.widget_raw = PlotWidget()

        # raw data revised
        # self.widget_raw = PlotWidget()

        # settings
        self.widget_settings = QtWidgets.QWidget()
        self.tabs_settings = QtWidgets.QTabWidget(self.widget_settings)
        self.detectSettingWidget = QtWidgets.QWidget()

        # detect3d
        self.widget_detect3d = QtWidgets.QWidget()
        layout_detect3d = QtWidgets.QVBoxLayout(self.widget_detect3d)
        self.plot_detect3d = gl.GLViewWidget()
        self.plot_detect3d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_detect3d.setCameraPosition(distance=250)
        self.closeButton3dDet = QtWidgets.QPushButton(text='Close')
        layout_detect3d.addWidget(self.closeButton3dDet)
        layout_detect3d.addWidget(self.plot_detect3d)
        self.widget_detect3d.setLayout(layout_detect3d)

        # Plot Clusters Waveform
        # self.widget_clusterwaveform =  pyqtgraph.widgets.MultiPlotWidget.MultiPlotWidget()

        # Plot Live Time
        # self.widget_livetime = QtWidgets.QWidget()

        # Plot ISI
        # self.widget_isi = QtWidgets.QWidget()

        # 3D Plot
        self.widget_3d = QtWidgets.QWidget()
        self.plot_3d = gl.GLViewWidget()
        self.plot_3d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout_plot_3d = QtWidgets.QGridLayout()
        layout_plot_pca_manual = QtWidgets.QGridLayout()

        self.axis1ComboBox = QtWidgets.QComboBox()
        self.axis1ComboBox.addItem("PCA1")
        self.axis1ComboBox.addItem("PCA2")
        self.axis1ComboBox.addItem("PCA3")
        self.axis1ComboBox.addItem("time")
        self.axis1ComboBox.addItem("p2p")
        self.axis1ComboBox.addItem("duty")
        self.axis1ComboBox.setCurrentIndex(0)

        self.axis2ComboBox = QtWidgets.QComboBox()
        self.axis2ComboBox.addItem("PCA1")
        self.axis2ComboBox.addItem("PCA2")
        self.axis2ComboBox.addItem("PCA3")
        self.axis2ComboBox.addItem("time")
        self.axis2ComboBox.addItem("p2p")
        self.axis2ComboBox.addItem("duty")
        self.axis2ComboBox.setCurrentIndex(1)

        self.axis3ComboBox = QtWidgets.QComboBox()
        self.axis3ComboBox.addItem("PCA1")
        self.axis3ComboBox.addItem("PCA2")
        self.axis3ComboBox.addItem("PCA3")
        self.axis3ComboBox.addItem("time")
        self.axis3ComboBox.addItem("p2p")
        self.axis3ComboBox.addItem("duty")
        self.axis3ComboBox.setCurrentIndex(2)

        self.closeButton3d = QtWidgets.QPushButton(text='Close')

        self.plotButton = QtWidgets.QPushButton(text='Plot')

        axisWidget = QtWidgets.QWidget()
        axisWidget_pca_manual = QtWidgets.QWidget()

        axisLayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('axis 1')
        axisLayout.addWidget(label)
        axisLayout.addWidget(self.axis1ComboBox)
        label = QtWidgets.QLabel('axis 2')
        axisLayout.addWidget(label)
        axisLayout.addWidget(self.axis2ComboBox)
        label = QtWidgets.QLabel('axis 3')
        axisLayout.addWidget(label)
        axisLayout.addWidget(self.axis3ComboBox)
        axisLayout.addStretch(5)
        axisLayout.addWidget(self.plotButton)
        axisLayout.addWidget(self.closeButton3d)
        axisWidget.setLayout(axisLayout)

        axisLayout_pca_button = QtWidgets.QHBoxLayout()
        axisLayout_pca_main = QtWidgets.QVBoxLayout()
        self.resetBottonPCAManual = QtWidgets.QPushButton(text='Reset')
        self.doneBottonPCAManual = QtWidgets.QPushButton(text='Done')
        self.closeBottonPCAManual = QtWidgets.QPushButton(text='Close')

        self.label_pca_manual = QtWidgets.QLabel()

        axisLayout_pca_button.addWidget(self.resetBottonPCAManual)
        axisLayout_pca_button.addWidget(self.doneBottonPCAManual)
        axisLayout_pca_button.addWidget(self.closeBottonPCAManual)

        axisLayout_pca_main.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        axisLayout_pca_main.addWidget(self.label_pca_manual)
        axisLayout_pca_main.addLayout(axisLayout_pca_button)

        axisWidget_pca_manual.setLayout(axisLayout_pca_main)

        layout_plot_3d.addWidget(axisWidget)
        layout_plot_3d.addWidget(self.plot_3d)
        self.widget_3d.setLayout(layout_plot_3d)

        self.painter = QPainter()
        layout_plot_pca_manual.addWidget(axisWidget_pca_manual)
        # layout_plot_pca_manual.addWidget(self.painter)
        self.widget_pca_manual = PCAManualWidget(self.label_pca_manual)
        # self.widget_pca_manual = QtWidgets.QWidget()
        self.widget_pca_manual.setLayout(layout_plot_pca_manual)

        # detection settings
        self.filterType = QtWidgets.QComboBox()
        self.filterType.addItems(["butterworth"])
        self.filterType.resize(self.filterType.sizeHint())
        self.filterOrder = QtWidgets.QSpinBox()
        self.passFreq = QtWidgets.QLineEdit()
        self.passFreq.setValidator(QtGui.QIntValidator())
        self.stopFreq = QtWidgets.QLineEdit()
        self.stopFreq.setValidator(QtGui.QIntValidator())
        self.samplingRate = QtWidgets.QSpinBox()
        self.samplingRate.setMaximum(10000000)
        self.thresholdMethod = QtWidgets.QComboBox()
        self.thresholdMethod.addItems(['median', 'wavelet', 'plexon'])
        self.signalSideThresholding = QtWidgets.QComboBox()
        self.signalSideThresholding.addItems(['positive', 'negative', 'both'])
        self.preThreshold = QtWidgets.QLineEdit()
        self.preThreshold.setValidator(QtGui.QIntValidator())
        self.postThreshold = QtWidgets.QLineEdit()
        self.postThreshold.setValidator(QtGui.QIntValidator())
        self.deadTime = QtWidgets.QLineEdit()
        self.deadTime.setValidator(QtGui.QIntValidator())
        # self.startDetection = QtWidgets.QToolButton()
        # self.startDetection.setDefaultAction(self.detectAct)
        self.startDetection = QtWidgets.QPushButton(text="Start Detection")

        layoutDetection = QtWidgets.QGridLayout()

        filterTypeLayout = QtWidgets.QHBoxLayout()
        filterTypeLayout.addWidget(QtWidgets.QLabel('Filter Type'))
        filterTypeLayout.addWidget(self.filterType)
        layoutDetection.addLayout(filterTypeLayout, 0, 0)

        # layoutDetection.setColumnStretch(0, 1)
        filterOrderLayout = QtWidgets.QHBoxLayout()
        filterOrderLayout.addWidget(QtWidgets.QLabel('Filter Order'))
        filterOrderLayout.addWidget(self.filterOrder)
        layoutDetection.addLayout(filterOrderLayout, 0, 1)

        passFreqLayout = QtWidgets.QHBoxLayout()
        passFreqLayout.addWidget(QtWidgets.QLabel('Pass Frequency'))
        passFreqLayout.addWidget(self.passFreq)
        layoutDetection.addLayout(passFreqLayout, 1, 0)

        stopFreqLayout = QtWidgets.QHBoxLayout()
        stopFreqLayout.addWidget(QtWidgets.QLabel('Stop Frequency'))
        stopFreqLayout.addWidget(self.stopFreq)
        layoutDetection.addLayout(stopFreqLayout, 1, 1)

        samplingRateLayout = QtWidgets.QHBoxLayout()
        samplingRateLayout.addWidget(QtWidgets.QLabel('Sampling Rate'))
        samplingRateLayout.addWidget(self.samplingRate)
        layoutDetection.addLayout(samplingRateLayout, 2, 0)

        thresholdMethodLayout = QtWidgets.QHBoxLayout()
        thresholdMethodLayout.addWidget(QtWidgets.QLabel('Threshold Method'))
        thresholdMethodLayout.addWidget(self.thresholdMethod)
        layoutDetection.addLayout(thresholdMethodLayout, 2, 1)

        signalSideLayout = QtWidgets.QHBoxLayout()
        signalSideLayout.addWidget(QtWidgets.QLabel('Signal Side'))
        signalSideLayout.addWidget(self.signalSideThresholding)
        layoutDetection.addLayout(signalSideLayout, 3, 0)

        preThresholdLayout = QtWidgets.QHBoxLayout()
        preThresholdLayout.addWidget(QtWidgets.QLabel('Pre-Threshold'))
        preThresholdLayout.addWidget(self.preThreshold)
        layoutDetection.addLayout(preThresholdLayout, 3, 1)

        postThresholdLayout = QtWidgets.QHBoxLayout()
        postThresholdLayout.addWidget(QtWidgets.QLabel('Post-Threshold'))
        postThresholdLayout.addWidget(self.postThreshold)
        layoutDetection.addLayout(postThresholdLayout, 4, 0)

        deadTimeLayout = QtWidgets.QHBoxLayout()
        deadTimeLayout.addWidget(QtWidgets.QLabel('Dead Time'))
        deadTimeLayout.addWidget(self.deadTime)
        layoutDetection.addLayout(deadTimeLayout, 4, 1, QtCore.Qt.AlignRight)

        layoutDetection.addWidget(self.startDetection, 5, 0)

        self.detectSettingWidget.setLayout(layoutDetection)

        self.sortingSettingWidget = QtWidgets.QWidget()

        self.tabs_sorting = QtWidgets.QTabWidget(self.sortingSettingWidget)

        self.alignmentSettingsWidget = QtWidgets.QWidget()
        layoutAlignment = QtWidgets.QGridLayout()

        self.maxShift = QtWidgets.QSpinBox()
        self.maxShift.setMaximum(10000000)
        self.numPeaks = QtWidgets.QSpinBox()
        self.histogramBins = QtWidgets.QSpinBox()
        self.compareMode = QtWidgets.QComboBox()
        self.compareMode.addItems(['magnitude', 'index'])

        maxShiftLayout = QtWidgets.QHBoxLayout()
        maxShiftLayout.addWidget(QtWidgets.QLabel('Max Shift'))
        maxShiftLayout.addWidget(self.maxShift)
        layoutAlignment.addLayout(maxShiftLayout, 0, 0)

        numPeaksLayout = QtWidgets.QHBoxLayout()
        numPeaksLayout.addWidget(QtWidgets.QLabel('Number of Peaks'))
        numPeaksLayout.addWidget(self.numPeaks)
        layoutAlignment.addLayout(numPeaksLayout, 1, 0)

        histogramBinsLayout = QtWidgets.QHBoxLayout()
        histogramBinsLayout.addWidget(QtWidgets.QLabel('Histogram Bins'))
        histogramBinsLayout.addWidget(self.histogramBins)
        layoutAlignment.addLayout(histogramBinsLayout, 2, 0)

        compareModeLayout = QtWidgets.QHBoxLayout()
        compareModeLayout.addWidget(QtWidgets.QLabel('Comparison Mode'))
        compareModeLayout.addWidget(self.compareMode)
        layoutAlignment.addLayout(compareModeLayout, 3, 0)

        self.alignmentSettingsWidget.setLayout(layoutAlignment)

        ############################################################################################
        self.filteringSettingsWidget = QtWidgets.QWidget()
        layoutFiltering = QtWidgets.QGridLayout()

        self.maxStd = QtWidgets.QLineEdit()
        self.maxStd.setValidator(QtGui.QIntValidator())
        self.maxMean = QtWidgets.QLineEdit()
        self.maxMean.setValidator(QtGui.QIntValidator())
        self.maxOutliers = QtWidgets.QLineEdit()
        self.maxOutliers.setValidator(QtGui.QIntValidator())
        # self.maxStd.setMaximumWidth(150)
        # self.maxMean.setMaximumWidth(150)
        # self.maxOutliers.setMaximumWidth(150)

        maxStdLayout = QtWidgets.QHBoxLayout()
        maxStdLayout.addWidget(QtWidgets.QLabel('Max std'))
        maxStdLayout.addWidget(self.maxStd)
        # maxStdLayout.addSpacerItem(QtWidgets.QSpacerItem(1, 1, hPolicy=QSizePolicy.Expanding))
        layoutFiltering.addLayout(maxStdLayout, 0, 0)

        maxMeanLayout = QtWidgets.QHBoxLayout()
        maxMeanLayout.addWidget(QtWidgets.QLabel('Max Mean'))
        maxMeanLayout.addWidget(self.maxMean)
        # maxMeanLayout.addSpacerItem(QtWidgets.QSpacerItem(1, 1, hPolicy=QSizePolicy.Expanding))
        layoutFiltering.addLayout(maxMeanLayout, 1, 0)

        maxOutliersLayout = QtWidgets.QHBoxLayout()
        l = QtWidgets.QLabel('Max Percent of Outliers')
        # l.setMaximumWidth(200)
        maxOutliersLayout.addWidget(l)
        maxOutliersLayout.addWidget(self.maxOutliers)
        # maxOutliersLayout.addSpacerItem(QtWidgets.QSpacerItem(1, 1, hPolicy=QSizePolicy.Expanding))
        layoutFiltering.addLayout(maxOutliersLayout, 2, 0)

        self.filteringSettingsWidget.setLayout(layoutFiltering)

        #########################################################################################################
        self.sortSettingsWidget = QtWidgets.QWidget()
        layoutSorting = QtWidgets.QGridLayout()

        self.alignment = QtWidgets.QCheckBox(text='Alignment')
        self.filtering = QtWidgets.QCheckBox(text='Statistical Filtering')
        self.nu = QtWidgets.QLineEdit()
        self.nu.setValidator(QtGui.QIntValidator())
        self.maxIter = QtWidgets.QSpinBox()
        self.pcaNum = QtWidgets.QSpinBox()
        self.gMax = QtWidgets.QSpinBox()
        self.gMin = QtWidgets.QSpinBox()
        self.uLim = QtWidgets.QLineEdit()
        self.uLim.setValidator(QtGui.QIntValidator())
        self.n = QtWidgets.QLineEdit()
        self.n.setValidator(QtGui.QIntValidator())
        # self.randomSeed = QtWidgets.QLineEdit()
        # self.randomSeed.setValidator(QtGui.QIntValidator())
        self.sortingType = QtWidgets.QComboBox()
        self.sortingType.addItems(['t dist', 'skew-t dist', 'GMM', 'K-means'])

        self.error = QtWidgets.QLineEdit()
        self.error.setValidator(QtGui.QIntValidator())
        self.tol = QtWidgets.QLineEdit()
        self.tol.setValidator(QtGui.QIntValidator())
        self.alpha = QtWidgets.QLineEdit()
        self.alpha.setValidator(QtGui.QIntValidator())
        self.combination = QtWidgets.QCheckBox(text='combination')
        self.custom_templates = QtWidgets.QCheckBox(text='custom templates')
        self.matching_mode = QtWidgets.QComboBox()
        self.matching_mode.addItems(['Euclidean', 'Chi-squared', 'Correlation'])

        layoutSorting.addWidget(self.alignment, 3, 0)
        layoutSorting.addWidget(self.filtering, 3, 1)

        nuLayout = QtWidgets.QHBoxLayout()
        nuLayout.addWidget(QtWidgets.QLabel('nu'), stretch=1)
        nuLayout.addWidget(self.nu, stretch=0)
        layoutSorting.addLayout(nuLayout, 0, 0)

        maxIterLayout = QtWidgets.QHBoxLayout()
        maxIterLayout.addWidget(QtWidgets.QLabel('Max Iterations'))
        maxIterLayout.addWidget(self.maxIter)
        layoutSorting.addLayout(maxIterLayout, 0, 1)

        pcaNumLayout = QtWidgets.QHBoxLayout()
        pcaNumLayout.addWidget(QtWidgets.QLabel('PCA num'))
        pcaNumLayout.addWidget(self.pcaNum)
        layoutSorting.addLayout(pcaNumLayout, 0, 2)

        gMaxLayout = QtWidgets.QHBoxLayout()
        gMaxLayout.addWidget(QtWidgets.QLabel('g max'))
        gMaxLayout.addWidget(self.gMax)
        layoutSorting.addLayout(gMaxLayout, 0, 3)

        gMinLayout = QtWidgets.QHBoxLayout()
        gMinLayout.addWidget(QtWidgets.QLabel('g min'))
        gMinLayout.addWidget(self.gMin)
        layoutSorting.addLayout(gMinLayout, 0, 4)

        uLimLayout = QtWidgets.QHBoxLayout()
        uLimLayout.addWidget(QtWidgets.QLabel('u lim'), stretch=1)
        uLimLayout.addWidget(self.uLim, stretch=0)
        layoutSorting.addLayout(uLimLayout, 1, 0)

        nLayout = QtWidgets.QHBoxLayout()
        nLayout.addWidget(QtWidgets.QLabel('N'), stretch=1)
        nLayout.addWidget(self.n, stretch=0)
        layoutSorting.addLayout(nLayout, 1, 1)

        # randomSeedLayout = QtWidgets.QHBoxLayout()
        # randomSeedLayout.addWidget(QtWidgets.QLabel('Random Seed'), stretch=1)
        # randomSeedLayout.addWidget(self.randomSeed, stretch=0)
        # layoutSorting.addLayout(randomSeedLayout, 1, 2)

        sortingTypeLayout = QtWidgets.QHBoxLayout()
        sortingTypeLayout.addWidget(QtWidgets.QLabel('Sorting Type'))
        sortingTypeLayout.addWidget(self.sortingType)
        layoutSorting.addLayout(sortingTypeLayout, 1, 2)

        errorLayout = QtWidgets.QHBoxLayout()
        errorLayout.addWidget(QtWidgets.QLabel('error'))
        errorLayout.addWidget(self.error)
        layoutSorting.addLayout(errorLayout, 1, 3)

        tolLayout = QtWidgets.QHBoxLayout()
        tolLayout.addWidget(QtWidgets.QLabel('tol'))
        tolLayout.addWidget(self.tol)
        layoutSorting.addLayout(tolLayout, 1, 4)

        alphaLayout = QtWidgets.QHBoxLayout()
        alphaLayout.addWidget(QtWidgets.QLabel('alpha'))
        alphaLayout.addWidget(self.alpha)
        layoutSorting.addLayout(alphaLayout, 2, 0)

        layoutSorting.addWidget(self.combination, 2, 3)

        layoutSorting.addWidget(self.custom_templates, 2, 2)

        matching_modeLayout = QtWidgets.QHBoxLayout()
        matching_modeLayout.addWidget(QtWidgets.QLabel('matching mode'))
        matching_modeLayout.addWidget(self.matching_mode)
        layoutSorting.addLayout(matching_modeLayout, 2, 1)

        self.sortSettingsWidget.setLayout(layoutSorting)

        ############################################################################################################

        self.tabs_sorting.addTab(self.alignmentSettingsWidget, "Alignment")
        self.tabs_sorting.addTab(self.filteringSettingsWidget, "Statistical Filtering")
        self.tabs_sorting.addTab(self.sortSettingsWidget, "Sorting")
        layout_sort_settings = QtWidgets.QVBoxLayout()
        layout_sort_settings.addWidget(self.tabs_sorting)

        self.startSorting = QtWidgets.QPushButton(text="Start Sorting")
        layout_sort_settings.addWidget(self.startSorting)
        self.sortingSettingWidget.setLayout(layout_sort_settings)

        self.manualSettingWidget = QtWidgets.QWidget()
        self.layout_manual_sorting = QtWidgets.QGridLayout()
        self.manualActWidget = QtWidgets.QListWidget()
        manual_act_list_layout = QtWidgets.QVBoxLayout()
        actLabel = QtWidgets.QLabel("Select Action : ", self)
        actLabel.setWordWrap(True)
        manual_act_list_layout.addWidget(actLabel)
        merge = QtWidgets.QListWidgetItem("Merge")
        self.manualActWidget.addItem(merge)
        remove = QtWidgets.QListWidgetItem("Remove")
        self.manualActWidget.addItem(remove)
        assign = QtWidgets.QListWidgetItem("Assign to nearest")
        self.manualActWidget.addItem(assign)
        pca_group = QtWidgets.QListWidgetItem("PCA Group")
        self.manualActWidget.addItem(pca_group)
        pca_remove = QtWidgets.QListWidgetItem("PCA Remove")
        self.manualActWidget.addItem(pca_remove)
        resort = QtWidgets.QListWidgetItem('Resort')
        self.manualActWidget.addItem(resort)
        self.manualActWidget.setCurrentItem(merge)
        scroll_bar = QtWidgets.QScrollBar(self)
        scroll_bar.setStyleSheet("background : lightgreen;")
        self.manualActWidget.setVerticalScrollBar(scroll_bar)
        manual_act_list_layout.addWidget(self.manualActWidget)
        self.layout_manual_sorting.addLayout(manual_act_list_layout, 0, 0)
        hlayout = QtWidgets.QHBoxLayout()
        self.actManual = QtWidgets.QPushButton(text='Act')
        hlayout.addWidget(self.actManual)
        self.plotManual = QtWidgets.QPushButton(text='Plot')
        hlayout.addWidget(self.plotManual)
        self.undoManual = QtWidgets.QPushButton(text='Undo')
        hlayout.addWidget(self.undoManual)
        self.resetManual = QtWidgets.QPushButton(text='Reset')
        hlayout.addWidget(self.resetManual)
        self.saveManual = QtWidgets.QPushButton(text='Save')
        hlayout.addWidget(self.saveManual)

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        scroll_bar_manual = QtWidgets.QScrollBar(self)
        scroll_bar_manual.setStyleSheet("background : lightgreen;")
        self.listWidget.setVerticalScrollBar(scroll_bar_manual)
        self.listWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        label = QtWidgets.QLabel("Select Clusters : ", self)
        label.setWordWrap(True)
        self.cluster_list_layout = QtWidgets.QVBoxLayout()
        self.cluster_list_layout.addWidget(label)
        self.cluster_list_layout.addWidget(self.listWidget)

        self.layout_manual_sorting.addLayout(self.cluster_list_layout, 0, 1)
        self.layout_manual_sorting.addLayout(hlayout, 1, 0)
        self.manualSettingWidget.setLayout(self.layout_manual_sorting)

        self.tabs_settings.addTab(self.detectSettingWidget, "Detection")
        self.tabs_settings.addTab(self.sortingSettingWidget, "Automatic Sorting")
        self.tabs_settings.addTab(self.manualSettingWidget, "Manual Sorting")

        layout_settings = QtWidgets.QHBoxLayout()
        layout_settings.addWidget(self.tabs_settings)
        self.widget_settings.setLayout(layout_settings)

        self.widget_assign_manual = QtWidgets.QWidget()
        self.layout_assign_manual = QtWidgets.QGridLayout()

        self.listSourceWidget = QtWidgets.QListWidget()

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
        self.listTargetsWidget.setVerticalScrollBar(scroll_bar)
        label2 = QtWidgets.QLabel("Targets : ", self)
        label2.setWordWrap(True)
        self.targets_list_layout = QtWidgets.QVBoxLayout()
        self.targets_list_layout.addWidget(label2)
        self.targets_list_layout.addWidget(self.listTargetsWidget)
        self.layout_assign_manual.addLayout(self.targets_list_layout, 0, 1)

        self.assign_button = QtWidgets.QPushButton(text='Assign')
        self.layout_assign_manual.addWidget(self.assign_button)
        self.assign_close_button = QtWidgets.QPushButton(text='Close')
        self.layout_assign_manual.addWidget(self.assign_close_button)
        self.widget_assign_manual.setLayout(self.layout_assign_manual)

        desktop_size = QtWidgets.QDesktopWidget().screenGeometry()
        w = desktop_size.width()
        h = desktop_size.height()
        self.widget_settings.setMaximumSize(int(w * (2.65) / 8), int(h / 3))

        self.mdiArea.addSubWindow(self.widget_waveform).setWindowTitle("Waveforms")
        self.mdiArea.addSubWindow(self.plot_histogram_pca).setWindowTitle("2D PCA Histogram")
        # self.mdiArea.addSubWindow(self.widget_clusters).setWindowTitle("Clusters")
        self.mdiArea.addSubWindow(self.widget_raw).setWindowTitle("Raw Data")
        self.mdiArea.addSubWindow(self.widget_settings).setWindowTitle("Settings")
        # self.mdiArea.addSubWindow(self.widget_visualizations).setWindowTitle("Visualizations")
        self.mdiArea.addSubWindow(self.widget_detect3d).setWindowTitle("DetectionResult 3D Hist")
        # self.mdiArea.addSubWindow(self.widget_clusters).setWindowTitle("Waveforms")
        # self.mdiArea.addSubWindow(self.widget_clusterwaveform).setWindowTitle("Plot Clusters Waveforms")
        # self.mdiArea.addSubWindow(self.widget_livetime).setWindowTitle("Live Time")
        # self.mdiArea.addSubWindow(self.widget_isi).setWindowTitle("ISI")
        self.mdiArea.addSubWindow(self.widget_3d).setWindowTitle("3D Plot")
        self.mdiArea.addSubWindow(self.widget_assign_manual).setWindowTitle("Assign to Nearest")

        self.mdiArea.addSubWindow(self.widget_pca_manual).setWindowTitle('PCA MANUAL')
        self.mdiArea.addSubWindow(self.plot_clusters_pca).setWindowTitle("2D PCA Clusters")

        subwindow_list = self.mdiArea.subWindowList()
        self.subwindow_waveforms = subwindow_list[0]
        self.subwindow_pca_histograms = subwindow_list[1]
        self.subwindow_raw = subwindow_list[2]
        self.subwindow_settings = subwindow_list[3]
        # self.subwindow_visualization = subwindow_list[4]
        self.subwindow_detect3d = subwindow_list[4]
        self.subwindow_3d = subwindow_list[5]
        self.subwindow_assign = subwindow_list[6]
        self.subwindow_pca_manual = subwindow_list[7]
        self.subwindow_pca_clusters = subwindow_list[8]
        # self.subwindow_clusterwave = subwindow_list[5]
        # self.subwindow_livetime = subwindow_list[6]
        # self.subwindow_isi = subwindow_list[7]

        for subwindow in subwindow_list:
            subwindow.setWindowFlags(
                QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowFullscreenButtonHint | QtCore.Qt.WindowTitleHint)
