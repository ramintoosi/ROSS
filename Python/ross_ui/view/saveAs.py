from PyQt5 import QtCore, QtGui, QtWidgets


class Save_As_Dialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 260)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30, 180, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
    
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(80, 50, 141, 21))

        self.label_res = QtWidgets.QLabel(self)
        self.label_res.setGeometry(QtCore.QRect(50, 170, 361, 16))

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(80, 100, 221, 31))

        self.setWindowTitle("Save As...")
        self.label.setText("Enter Project Name:")
