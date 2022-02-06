import os

from PySide6 import QtCore as Qc
from PySide6 import QtGui as Qg
from PySide6 import QtWidgets as Qw

import ted_qprocess as tpr
from qconfig import INI, YOUTUBE_DL_EXE_PATH, output, typoi
from version import VERSION


class ProgressBarDelegate(Qw.QStyledItemDelegate):
    def paint(self, painter, option, index):
        cdata = index.model().data(index, Qc.Qt.DisplayRole)
        data = index.model().pm.get_process_by_index(index.row()).percent
        color = Qg.QColor(
            index.model().pm.get_process_by_index(index.row()).color)
        width = option.rect.width() * data / 100
        rect = Qc.QRect(option.rect)
        rect.setWidth(width)
        brush = Qg.QBrush()
        brush.setColor(color)
        brush.setStyle(Qc.Qt.SolidPattern)
        painter.fillRect(rect, brush)
        pen = Qg.QPen()
        pen.setColor(Qc.Qt.black)
        painter.drawText(option.rect, Qc.Qt.AlignLeft, cdata)


class DownloadWidget(Qw.QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle(f'qYoutube-dl (version : {VERSION})')

        self.jobs = tpr.TModel()

        self.setMinimumHeight(400)
        self.setMinimumWidth(600)
        self.clipboard = ''

        # Widgets
        self.url = Qw.QPlainTextEdit(self)
        self.url.setMaximumHeight(100)
        self.url.setAcceptDrops(False)

        self.save_path = Qw.QLineEdit(self)
        self.save_path.setReadOnly(True)
        save_path = INI.value("save_path", defaultValue='')
        self.save_path.setText(str(save_path))
        if not os.path.exists(save_path):
            self.save_path.setText('')

        self.bpath = Qw.QToolButton(self)
        self.bpath.setText('...')
        self.bpath.setToolTip('Set save path')

        self.cb = Qw.QComboBox()
        for typ in typoi:
            self.cb.addItem(typ)

        self.cboutput = Qw.QComboBox()
        for out in output:
            self.cboutput.addItem(out)

        self.chkthubnails = Qw.QCheckBox("thubnails")

        self.chckmetadata = Qw.QCheckBox("metadata")

        self.bupdateyutubedl = Qw.QPushButton('update', self)
        self.bupdateyutubedl.setFocusPolicy(Qc.Qt.FocusPolicy.NoFocus)

        self.bopen_dir = Qw.QPushButton('open dir', self)
        self.bopen_dir.setFocusPolicy(Qc.Qt.FocusPolicy.NoFocus)

        self.bexec = Qw.QPushButton('Go', self)
        self.bexec.setFocusPolicy(Qc.Qt.FocusPolicy.NoFocus)

        self.runinfo = Qw.QTableView()
        self.runinfo.setModel(self.jobs)
        self.runinfo.setAlternatingRowColors(True)
        self.runinfo.setSelectionMode(Qw.QAbstractItemView.NoSelection)
        self.runinfo.setContextMenuPolicy(Qc.Qt.CustomContextMenu)
        self.runinfo.customContextMenuRequested.connect(self.on_context)
        self.runinfo.setColumnWidth(0, 60)
        self.runinfo.setColumnWidth(1, 200)
        # self.runinfo.setShowGrid(False)
        self.runinfo.horizontalHeader().setStretchLastSection(True)
        self.runinfo.resizeRowsToContents()

        delegate = ProgressBarDelegate()
        self.runinfo.setItemDelegateForColumn(2, delegate)

        # Layouts
        vlayout = Qw.QVBoxLayout(self)
        vlayout.addWidget(self.url)

        path_layout = Qw.QHBoxLayout()
        vlayout.addLayout(path_layout)
        path_layout.addWidget(Qw.QLabel('Save Path :'))
        path_layout.addWidget(self.save_path)
        path_layout.addWidget(self.bpath)

        button_layout = Qw.QHBoxLayout()
        vlayout.addLayout(button_layout)
        button_layout.addWidget(self.cb)
        button_layout.addWidget(self.cboutput)
        button_layout.addWidget(self.chkthubnails)
        button_layout.addWidget(self.chckmetadata)
        button_layout.addWidget(self.bupdateyutubedl)
        button_layout.addWidget(self.bopen_dir)
        sp2 = Qw.QSpacerItem(40, 20, Qw.QSizePolicy.Policy.Expanding,
                             Qw.QSizePolicy.Policy.Minimum)
        button_layout.addItem(sp2)
        button_layout.addWidget(self.bexec)

        vlayout.addWidget(self.runinfo)

        self.initialize_settings()

        # Tooltips

        self.url.setToolTip('Enter a url or a list of urls')
        self.save_path.setToolTip('Set save path')
        self.bpath.setToolTip('Set save path')
        self.cb.setToolTip('Set file format (video, mp3)')
        self.cboutput.setToolTip(
            'Best option is "title"')
        # self.chkthubnails.setToolTip('Download thubnails')
        self.chckmetadata.setToolTip(
            'Download metadata \n Be warned: Sometimes blocks downloading')
        self.bexec.setToolTip('Download')
        self.bupdateyutubedl.setToolTip('Update youtube-dl.exe')
        # Connections
        self.bpath.clicked.connect(self.update_path)
        self.bupdateyutubedl.clicked.connect(self.update_youtube_dl)
        self.bopen_dir.clicked.connect(self.open_dir)
        self.bexec.clicked.connect(self.on_bexec_clicked)

    def open_dir(self):
        if self.check_before_run():
            os.startfile(self.save_path.text())

    def on_context(self, point):
        acre = Qg.QAction(
            'stop',
            self,
            statusTip='stop job',
            triggered=self.terminate
        )
        arestart = Qg.QAction(
            'restart',
            self,
            statusTip='restart job',
            triggered=self.restart
        )
        arem = Qg.QAction(
            'remove',
            self,
            statusTip='remove job',
            triggered=self.remove
        )
        aremfin = Qg.QAction(
            'remove all finished',
            self,
            statusTip='remove finished jobs',
            triggered=self.remove_finished
        )

        menu = Qw.QMenu("Menu", self)
        menu.addAction(acre)
        menu.addAction(arestart)
        menu.addAction(arem)
        menu.addAction(aremfin)
        menu.exec(self.runinfo.mapToGlobal(point))

    def terminate(self):
        idx = self.runinfo.currentIndex().row()
        # print(idx)
        if idx < 0:
            return
        self.jobs.pm.terminate_process(idx)

    def remove(self):
        idx = self.runinfo.currentIndex().row()
        if idx < 0:
            return
        self.jobs.pm.remove_process(idx)

    def remove_finished(self):
        self.jobs.pm.remove_finished()

    def restart(self):
        idx = self.runinfo.currentIndex().row()
        if idx < 0:
            return
        self.jobs.pm.restart_process(idx)

    def initialize_settings(self):
        isthubnails = INI.value("thubnails")
        bisthubnails = True if isthubnails == 'true' else False
        self.chkthubnails.setChecked(bisthubnails)

        ismetadata = INI.value("metadata")
        bismetadata = True if ismetadata == 'true' else False
        self.chckmetadata.setChecked(bismetadata)
        self.cb.setCurrentText(INI.value("typoi"))
        self.cboutput.setCurrentText(INI.value("output"))
        self.cboutput.setToolTip('Filename format')

    def update_settings_on_run(self):
        INI.setValue("thubnails", self.chkthubnails.isChecked())
        INI.setValue("metadata", self.chckmetadata.isChecked())
        INI.setValue("typoi", self.cb.currentText())
        INI.setValue("output", self.cboutput.currentText())

    def update_path(self):
        old = self.save_path.text()
        opt = Qw.QFileDialog.Option.DontResolveSymlinks | Qw.QFileDialog.Option.ShowDirsOnly
        path = Qw.QFileDialog.getExistingDirectory(self, 'path', old, opt)
        if path:
            self.save_path.setText(path)
            INI.setValue("save_path", path)

    def update_youtube_dl(self):
        result = os.popen(
            f'{YOUTUBE_DL_EXE_PATH} --update --no-check-certificate')
        final = result.read()
        Qw.QMessageBox.information(
            self, "youtube-dl update Finished", final.strip())

    def disable_buttons(self):
        self.bexec.setEnabled(False)
        self.bupdateyutubedl.setEnabled(False)

    def enable_buttons(self):
        self.bexec.setEnabled(True)
        self.bupdateyutubedl.setEnabled(True)

    def check_before_run(self):

        if not YOUTUBE_DL_EXE_PATH:
            self.message("youtube-dl.exe not set.")
            return False
        if not YOUTUBE_DL_EXE_PATH.endswith('youtube-dl.exe'):
            self.message("exe path must point to youtube-dl.exe")
            return False
        if not os.path.exists(YOUTUBE_DL_EXE_PATH):
            self.message("youtube-dl.exe not found.")
            return False
        if not self.save_path.text():
            Qw.QMessageBox.critical(
                self, "Error", "Save path not set.")
            return False
        return True

    def create_parameters(self):
        cbtypos = self.cb.currentText()
        cboutput = self.cboutput.currentText()
        params = []
        for out in output[cboutput]:
            params.append(out)
        for par in typoi[cbtypos]:
            params.append(par)
        if self.chkthubnails.isChecked():
            params.append('--embed-thumbnail')
            params.append("--postprocessor-args")
            params.append("-id3v2_version 3")
        if self.chckmetadata.isChecked():
            params.append('--add-metadata')
        return params

    def on_bexec_clicked(self):
        self.update_settings_on_run()
        if not self.check_before_run():
            return
        url_text = self.url.toPlainText()
        for line in url_text.splitlines():
            line = line.strip()
            if line:
                self.run_command(line)
        self.url.setPlainText('')

    def run_command(self, url):
        # url = url1
        if url == '':
            return
        pars = self.create_parameters()
        pars.append(url)
        self.jobs.start(YOUTUBE_DL_EXE_PATH, pars, self.save_path.text())

    def message(self, s):
        Qw.QMessageBox.information(self, "info", f'{s}')

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.url.appendPlainText(event.mimeData().text())
