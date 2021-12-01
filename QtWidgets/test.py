import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication, qApp, QMainWindow, QDialog


class MyWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        uic.loadUi('test.ui', self)
        a = print('123')
        self.OkButton.clicked.connect(qApp.exit)


if __name__ == '__main__':
    APP = QApplication(sys.argv)
    WINDOW_OBJ = MyWindow()
    WINDOW_OBJ.show()

    sys.exit(APP.exec_())
