import os

from PyQt5 import QtWidgets

from model.api import API
from view.serverFileDialog import ServerFileDialog


class ServerFileDialogApp(ServerFileDialog):
    def __init__(self, api: API):
        super(ServerFileDialogApp, self).__init__()
        self.api = api
        self.root = None

        self.list_folder.itemDoubleClicked.connect(self.itemDoubleClicked)

        self.request_dir()

    def request_dir(self):
        self.list_folder.clear()
        dir_dict = self.api.browse(self.root)
        if dir_dict is not None:
            self.line_address.setText(dir_dict['root'])

            item = QtWidgets.QListWidgetItem('..')
            item.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
            self.list_folder.addItem(item)

            for folder_name in dir_dict['folders']:
                item = QtWidgets.QListWidgetItem(folder_name)
                item.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
                self.list_folder.addItem(item)
            for filename in dir_dict['files']:
                item = QtWidgets.QListWidgetItem(filename)
                item.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
                self.list_folder.addItem(item)
        else:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Server Error')

    def itemDoubleClicked(self, item: QtWidgets.QListWidgetItem):
        name = item.text()
        isfolder = item.icon().name() == 'folder'
        if isfolder:
            self.root = os.path.join(self.line_address.text(), name)
            self.request_dir()
        else:
            ret = self.api.post_raw_data(raw_data_path=os.path.join(self.line_address.text(), name),
                                         mode=1,
                                         varname=self.line_varname.text())
            if ret['stat']:
                QtWidgets.QMessageBox.information(self, 'Info', 'File successfully added.')
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', ret['message'])
