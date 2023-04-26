from PyQt5 import QtCore, QtWidgets


class Signin_Dialog(QtWidgets.QDialog):
    def __init__(self, server):
        super().__init__()
        self.url = server
        self.setFixedSize(300, 150)

        l_label = QtWidgets.QVBoxLayout()
        l_line = QtWidgets.QVBoxLayout()
        l_push = QtWidgets.QHBoxLayout()
        l1 = QtWidgets.QHBoxLayout()
        l2 = QtWidgets.QVBoxLayout()

        self.label_u = QtWidgets.QLabel("Username")
        self.label_p = QtWidgets.QLabel("Password")

        l_label.addWidget(self.label_u)
        l_label.addWidget(self.label_p)

        self.textEdit_username = QtWidgets.QLineEdit()
        self.textEdit_password = QtWidgets.QLineEdit()
        self.textEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)

        l_line.addWidget(self.textEdit_username)
        l_line.addWidget(self.textEdit_password)

        l1.addLayout(l_label)
        l1.addLayout(l_line)

        self.pushButton_in = QtWidgets.QPushButton("Sign In")
        self.pushButton_up = QtWidgets.QPushButton("Sign Up")

        l_push.addWidget(self.pushButton_in)
        l_push.addWidget(self.pushButton_up)

        l2.addLayout(l1)
        l2.addLayout(l_push)

        self.setLayout(l2)

        self.setWindowTitle('Authentication')
