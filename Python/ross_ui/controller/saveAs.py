from PyQt5 import QtWidgets
from view.saveAs import Save_As_Dialog

class SaveAsApp(Save_As_Dialog):
    def __init__(self, user):
        super(SaveAsApp, self).__init__()
        self.user = user
        self.buttonBox.accepted.connect(self.accept_save)
        self.buttonBox.rejected.connect(self.reject)

    def accept_save(self):
        self.project_name = self.lineEdit.text()
        res = self.user.save_project_as(self.project_name)
        if res['stat']:
            super().accept()
        elif res["message"] == 'Project with this name already exists.':
            reply = QtWidgets.QMessageBox.question(self, "Replace Project", "Project with this name already exists. Do you want to replace it?")
            if reply == QtWidgets.QMessageBox.Yes:
                self.user.delete_project(self.project_name)
                res_2 = self.user.save_project_as(self.project_name)
                if res_2['stat']:
                    super().accept()
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", res_2["message"])   
            else:
                pass
        else:
            QtWidgets.QMessageBox.critical(self, "Error", res["message"])
