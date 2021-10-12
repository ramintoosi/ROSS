from controller.mainWindow import MainApp
from PyQt5 import QtWidgets
import sys


def main():
    """Main routine."""

    # Create application and main window.
    app = QtWidgets.QApplication(sys.argv)
    # print(QtWidgets.QStyleFactory.keys())
    # app.setStyle('Fusion')
    window = MainApp()
    window.show()


    # Run execution loop.
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())