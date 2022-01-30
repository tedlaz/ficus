#!/usr/bin/python
import os
import sys

from PySide6 import QtCore as Qc
from PySide6 import QtGui as Qg
from PySide6 import QtWidgets as Qw

import resources
from version import VERSION
from widget_mp3jpg2video import UploadToYoutubeWidget
from widget_youtube import DownloadWidget


class MainWindow(Qw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'Ficus (version : {VERSION})')
        self.tab1 = Qw.QTabWidget(self)
        self.setCentralWidget(self.tab1)
        self.downwidget = DownloadWidget()
        self.upwidget = UploadToYoutubeWidget()
        self.tab1.addTab(self.downwidget, "Download")
        self.tab1.addTab(self.upwidget, "mp3 + image To Video")

        self.downwidget.job.status.connect(self.statusBar().showMessage)
        self.show()


def main():
    Qc.QCoreApplication.setAttribute(Qc.Qt.AA_EnableHighDpiScaling)
    Qc.QCoreApplication.setAttribute(Qc.Qt.AA_UseHighDpiPixmaps)
    app = Qw.QApplication(sys.argv)
    app.setWindowIcon(Qg.QIcon(':/icons/ficus.png'))
    ui = MainWindow()
    app.exec()


if __name__ == '__main__':
    main()
