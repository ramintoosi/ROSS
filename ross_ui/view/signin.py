from PyQt5 import QtCore, QtWidgets


class Signin_Dialog(QtWidgets.QDialog):
    def __init__(self, server):
        super().__init__()
        self.url = server
        self.setFixedSize(400, 300)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 60, 121, 21))
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(50, 130, 121, 20))

        self.textEdit_username = QtWidgets.QLineEdit(self)
        self.textEdit_username.setGeometry(QtCore.QRect(145, 55, 141, 31))

        self.textEdit_password = QtWidgets.QLineEdit(self)
        self.textEdit_password.setGeometry(QtCore.QRect(145, 125, 141, 31))
        self.textEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.label_res = QtWidgets.QLabel(self)
        self.label_res.setGeometry(QtCore.QRect(50, 180, 361, 16))

        self.pushButton_in = QtWidgets.QPushButton(self)
        self.pushButton_in.setGeometry(QtCore.QRect(130, 220, 121, 31))

        self.pushButton_up = QtWidgets.QPushButton(self)
        self.pushButton_up.setGeometry(QtCore.QRect(260, 220, 111, 31))

        self.setWindowTitle("Sign In/Up")
        self.label.setText("Username")
        self.label_2.setText("Password")
        self.label_res.setText("")
        self.pushButton_in.setText("Sign In")
        self.pushButton_up.setText("Sign Up")
