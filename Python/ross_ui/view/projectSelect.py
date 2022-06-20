from PyQt5 import QtCore, QtGui, QtWidgets


class Project_Dialog(QtWidgets.QDialog):
    def __init__(self, projects):
        super().__init__()
        self.setFixedSize(400, 227)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30, 160, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(100, 100, 201, 22))
        self.comboBox.addItems(projects)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(80, 50, 301, 21))

        self.setWindowTitle("Open")
        self.label.setText("Select from existing projects:")
