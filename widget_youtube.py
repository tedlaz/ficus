import os

from PySide6 import QtCore as Qc
from PySide6 import QtGui as Qg
from PySide6 import QtWidgets as Qw

from qconfig import INI, YOUTUBE_DL_EXE_PATH, output, typoi
from qlist_parsers import extract_list_vars, youtubedl_percent_parser
from qlist_process_manager import STATUS_COLORS, JobManager, Parsers
from version import VERSION


class ProgressBarDelegate(Qw.QStyledItemDelegate):
    def paint(self, painter, option, index):
        # data is our status dict, containing progress, id, status
        job_id, data, ldata = index.model().data(index, Qc.Qt.DisplayRole)
        if data["progress"] == 0 and data['status'] == Qc.QProcess.NotRunning:
            color = "#fad2d6"
            width = option.rect.width()
            rect = Qc.QRect(option.rect)
            rect.setWidth(width)
            brush = Qg.QBrush()
            brush.setColor(color)
            brush.setStyle(Qc.Qt.SolidPattern)
            painter.fillRect(rect, brush)

        if data["progress"] > 0:
            color = Qg.QColor(STATUS_COLORS[data["status"]])
            width = option.rect.width() * data["progress"] / 100

            #  Copy of the rect, so we can modify.
            rect = Qc.QRect(option.rect)
            rect.setWidth(width)

            brush = Qg.QBrush()
            brush.setColor(color)
            brush.setStyle(Qc.Qt.SolidPattern)

            painter.fillRect(rect, brush)

        pen = Qg.QPen()
        pen.setColor(Qc.Qt.black)
        data = ldata.get('file', job_id)
        painter.drawText(option.rect, Qc.Qt.AlignLeft, data)


class DownloadWidget(Qw.QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle(f'qYoutube-dl (version : {VERSION})')
        self.p = None
        self.update_log = ''

        self.job = JobManager()

        self.setMinimumHeight(200)
        self.setMinimumWidth(400)
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

        self.bexec = Qw.QPushButton('Go', self)
        self.bexec.setFocusPolicy(Qc.Qt.FocusPolicy.NoFocus)

        self.runinfo = Qw.QListView()
        self.runinfo.setModel(self.job)
        # self.runinfo.setModelColumn(1)
        delegate = ProgressBarDelegate()
        self.runinfo.setItemDelegate(delegate)

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
        self.bexec.clicked.connect(self.on_bexec_clicked)

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
        params = ['--update', '--no-check-certificate']
        self.disable_buttons()
        self.start_process(params)

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
            self.message("Save path not set.")
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
        # print(YOUTUBE_DL_EXE_PATH, pars, url)
        self.job.execute(
            YOUTUBE_DL_EXE_PATH,
            pars,
            url,
            self.save_path.text(),
            parsers=Parsers(progress=youtubedl_percent_parser,
                            data=extract_list_vars),
        )

    def on_bexec_clicked_old(self):
        self.update_settings_on_run()
        if not self.check_before_run():
            return
        os.chdir(self.save_path.text())
        params = self.create_parameters()
        self.message(f"youtub-dl parameters: {params}")
        self.start_process(params)

    def message(self, s):
        self.update_log += f'{s}\n'
        # self.statusBar().showMessage(s)

    def start_process(self, pars):
        if self.p is None:
            self.disable_buttons()
            self.p = Qc.QProcess()

            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)

            self.p.start(YOUTUBE_DL_EXE_PATH, pars)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8", errors='ignore')
        self.message(stdout)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8", errors='ignore')
        self.message(stderr)

    def handle_state(self, state):
        states = {
            Qc.QProcess.ProcessState.NotRunning: 'Not running',
            Qc.QProcess.ProcessState.Starting: 'Starting',
            Qc.QProcess.ProcessState.Running: 'Running',
        }
        state_name = states[state]
        # self.message(f"State changed: {state_name}")

    def process_finished(self):
        # self.message("Process finished.")
        self.enable_buttons()
        self.url.setPlainText('')
        self.p = None
        Qw.QMessageBox.information(
            self, "youtube-dl update Finished", self.update_log)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.url.appendPlainText(event.mimeData().text())
