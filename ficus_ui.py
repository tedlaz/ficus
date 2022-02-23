# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ficus.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPlainTextEdit, QSizePolicy,
    QStatusBar, QTabWidget, QToolButton, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(524, 578)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_download = QWidget()
        self.tab_download.setObjectName(u"tab_download")
        self.tabWidget.addTab(self.tab_download, "")
        self.tab_mp3 = QWidget()
        self.tab_mp3.setObjectName(u"tab_mp3")
        self.verticalLayout_2 = QVBoxLayout(self.tab_mp3)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame1_top = QFrame(self.tab_mp3)
        self.frame1_top.setObjectName(u"frame1_top")
        self.frame1_top.setMaximumSize(QSize(16777215, 150))
        self.frame1_top.setFrameShape(QFrame.StyledPanel)
        self.frame1_top.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame1_top)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.plainTextEdit = QPlainTextEdit(self.frame1_top)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.horizontalLayout_2.addWidget(self.plainTextEdit)


        self.verticalLayout_2.addWidget(self.frame1_top)

        self.frame2_middle = QFrame(self.tab_mp3)
        self.frame2_middle.setObjectName(u"frame2_middle")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame2_middle.sizePolicy().hasHeightForWidth())
        self.frame2_middle.setSizePolicy(sizePolicy)
        self.frame2_middle.setMinimumSize(QSize(0, 50))
        self.frame2_middle.setFrameShape(QFrame.StyledPanel)
        self.frame2_middle.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame2_middle)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame2_middle)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.label)

        self.ln_save_path = QLineEdit(self.frame2_middle)
        self.ln_save_path.setObjectName(u"ln_save_path")

        self.horizontalLayout.addWidget(self.ln_save_path)

        self.btn_open_save_path = QToolButton(self.frame2_middle)
        self.btn_open_save_path.setObjectName(u"btn_open_save_path")

        self.horizontalLayout.addWidget(self.btn_open_save_path)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout_2.addWidget(self.frame2_middle, 0, Qt.AlignTop)

        self.frame3_bottom = QFrame(self.tab_mp3)
        self.frame3_bottom.setObjectName(u"frame3_bottom")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame3_bottom.sizePolicy().hasHeightForWidth())
        self.frame3_bottom.setSizePolicy(sizePolicy2)
        self.frame3_bottom.setFrameShape(QFrame.StyledPanel)
        self.frame3_bottom.setFrameShadow(QFrame.Raised)

        self.verticalLayout_2.addWidget(self.frame3_bottom)

        self.tabWidget.addTab(self.tab_mp3, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_download), QCoreApplication.translate("MainWindow", u"Download", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Save Path : ", None))
        self.btn_open_save_path.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_mp3), QCoreApplication.translate("MainWindow", u"mp3, image to video", None))
    # retranslateUi

