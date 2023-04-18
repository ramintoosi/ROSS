from PyQt5 import QtCore, QtWidgets


class Detected_Mat_Dialog(QtWidgets.QDialog):
    def __init__(self, variables):
        super().__init__()
        self.setFixedSize(400, 227)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30, 160, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(100, 100, 201, 22))
        self.comboBox.addItems(variables)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(80, 50, 301, 21))

        self.setWindowTitle("Select Detected Matrix Data")
        self.label.setText("Select the variable containing detected matrix data:")
