from PySide6 import QtCore as Qc
from PySide6 import QtWidgets as Qw

from qconfig import FFMPEG_PATH, videoformat


class UploadToYoutubeWidget(Qw.QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.p = None
        layout = Qw.QVBoxLayout(self)

        self.mp3 = Qw.QPlainTextEdit()
        self.mp3.setToolTip("Drag and drop or copy, mp3 and image files here")
        self.mp3.setMaximumHeight(100)
        self.mp3.setAcceptDrops(False)

        layout.addWidget(self.mp3)

        hlay = Qw.QHBoxLayout()
        layout.addLayout(hlay)

        self.cb = Qw.QComboBox()
        self.cb.setMinimumWidth(160)
        for typ in videoformat:
            self.cb.addItem(typ)
        hlay.addWidget(self.cb)

        sp2 = Qw.QSpacerItem(40, 20, Qw.QSizePolicy.Policy.Expanding,
                             Qw.QSizePolicy.Policy.Minimum)
        hlay.addItem(sp2)

        self.bexec = Qw.QPushButton("create video")
        hlay.addWidget(self.bexec)

        self.log = Qw.QPlainTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.bexec.clicked.connect(self.render)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        dropped_txt = event.mimeData().text()
        if dropped_txt.endswith(('.mp3', '.jpg', '.png')):
            self.mp3.appendPlainText(event.mimeData().text())

    def message(self, message):
        self.log.appendPlainText(f"{message}")

    def parse_mp3(self):
        fpaths = {'mp3': '', 'image': '', 'out': ''}
        extension = self.cb.currentText()
        for line in self.mp3.toPlainText().splitlines():
            line = line.strip().replace('file:///', '')
            if line.endswith('.mp3'):
                fpaths['mp3'] = line
                fpaths['out'] = line.replace('.mp3', f'.{extension}')
            if line.endswith(('.jpg', '.png')):
                fpaths['image'] = line

        if not all(fpaths.values()):
            Qw.QMessageBox.critical(
                self,
                "Error",
                "Please insert mp3 and image in order to proceed"
            )
            return fpaths, True
        return fpaths, False

    def render(self):
        fpaths, error = self.parse_mp3()
        if error:
            return

        pars = [
            "-loop",
            "1",
            "-i",
            fpaths['image'],
            "-i",
            fpaths['mp3'],
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-c:a",
            "copy",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            fpaths['out'],
        ]

        self.mp3.setPlainText('')
        if self.p is None:
            self.p = Qc.QProcess()
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)

            self.p.start(FFMPEG_PATH, pars)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

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
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        # self.enable_buttons()
        # self.url.setPlainText('')
        self.p = None
        self.message("youtube-dl update Finished")
