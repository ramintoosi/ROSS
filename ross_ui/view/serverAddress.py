from PyQt5 import QtCore, QtWidgets


class Server_Dialog(QtWidgets.QDialog):
    def __init__(self, server_text):
        super().__init__()
        self.setFixedSize(400, 227)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30, 160, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(80, 50, 141, 21))

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(80, 100, 221, 31))

        self.setWindowTitle("Server Address")
        self.label.setText("Enter Server Address:")
        self.lineEdit.setText(server_text)
