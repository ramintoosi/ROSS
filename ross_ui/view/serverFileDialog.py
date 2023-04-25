from PyQt5 import QtWidgets


class ServerFileDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 300)

        self.layout_out = QtWidgets.QVBoxLayout()
        self.layout_file_but = QtWidgets.QHBoxLayout()

        self.line_address = QtWidgets.QLineEdit()
        self.line_address.setEnabled(False)
        self.layout_out.addWidget(self.line_address)

        self.list_folder = QtWidgets.QListWidget()
        self.layout_out.addWidget(self.list_folder)

        self.layout_out.addWidget(QtWidgets.QLabel('For mat files enter the variable name (if more than one variable '
                                                   'is stored).'))

        self.line_varname = QtWidgets.QLineEdit()
        self.layout_out.addWidget(self.line_varname)

        self.push_open = QtWidgets.QPushButton('Open')
        self.push_cancel = QtWidgets.QPushButton('Cancel')
        self.layout_file_but.addWidget(self.push_open)
        self.layout_file_but.addWidget(self.push_cancel)
        self.layout_out.addLayout(self.layout_file_but)

        self.setLayout(self.layout_out)

        self.setWindowTitle("Server File Dialog")
