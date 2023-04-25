from PyQt5 import QtWidgets

from model.api import API
from view.signin import Signin_Dialog


class SigninApp(Signin_Dialog):
    def __init__(self, server):
        super(SigninApp, self).__init__(server)
        self.pushButton_in.pressed.connect(self.accept_in)
        self.pushButton_up.pressed.connect(self.accept_up)

    def accept_in(self):
        username = self.textEdit_username.text()
        password = self.textEdit_password.text()
        self.user = API(self.url)
        res = self.user.sign_in(username, password)
        if res['stat']:
            super().accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Error", res["message"])

    def accept_up(self):
        username = self.textEdit_username.text()
        password = self.textEdit_password.text()
        self.user = API(self.url)
        res = self.user.sign_up(username, password)
        if res['stat']:
            self.label_res.setStyleSheet("color: green")
            QtWidgets.QMessageBox.information(self, "Account Created", res["message"])
        else:
            self.label_res.setStyleSheet("color: red")
            # self.label_res.setText(res['message'])
            QtWidgets.QMessageBox.critical(self, "Error", res["message"])
