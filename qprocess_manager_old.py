import os
import re
import sys
import uuid
from collections import namedtuple

from PySide6.QtCore import (QAbstractListModel, QObject, QProcess, QRect,
                            QRunnable, Qt, QTimer, Signal, Slot)
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import (QApplication, QLineEdit, QListView, QMainWindow,
                               QPlainTextEdit, QProgressBar, QPushButton,
                               QStyledItemDelegate, QVBoxLayout, QWidget)

# STATUS_COLORS = {
#     QProcess.NotRunning: "#b2df8a",
#     QProcess.Starting: "#fdbf6f",
#     QProcess.Running: "#33a02c",
# }

STATUS_COLORS = {
    QProcess.NotRunning: "#67aade",
    QProcess.Starting: "#fdbf6f",
    QProcess.Running: "#91de67",
}

STATES = {
    QProcess.NotRunning: "Not running",
    QProcess.Starting: "Starting...",
    QProcess.Running: "Running...",
}

DEFAULT_STATE = {"progress": 0, "status": QProcess.Starting}


parsers = namedtuple("parsers", "progress data")
no_parsers = parsers(None, None)

progress_re = re.compile("Total complete: (\d+)%", re.M)

pre = re.compile('\[download\]( +)(\d+.\d+)%', re.M)


def simple_percent_parser(output):
    """
    Matches lines using the progress_re regex,
    returning a single integer for the % progress.
    """
    m = progress_re.search(output)
    if m:
        pc_complete = m.group(1)
        return int(pc_complete)


def youtubedl_percent_parser(output):
    '[download] Destination: The Box Tops - The Letter.webm'
    '[download]  59.7% of 1.86MiB at 53.72KiB/s ETA 00:14'
    '[ffmpeg] Destination: The Box Tops - The Letter.mp3'
    '[ffmpeg] Adding thumbnail to "The Box Tops - The Letter.mp3"'
    m = pre.search(output)
    if m:
        return float(m.group(2))


def extract_vars(l):
    """
    Extracts variables from lines, looking for lines
    containing an equals, and splitting into key=value.
    """
    data = {}
    sdest = "[download] Destination: "
    sfile = "[ffmpeg] Destination: "
    for s in l.splitlines():
        if s.startswith(sdest):
            data['destination'] = s.replace(sdest, '')
        if s.startswith(sfile):
            data['file'] = s.replace(sfile, '')
    return data


def extract_list_vars(l):
    """
    Extracts variables from lines, looking for lines
    containing an equals, and splitting into key=value.
    [download]  59.7% of 1.86MiB at 53.72KiB/s ETA 00:14
    """
    data = {'file': '', 'size': ''}
    sdest = "[download] Destination: "
    sfile = "[ffmpeg] Destination: "
    for s in l.splitlines():
        if s.startswith(sdest):
            data['file'] = s.replace(sdest, '')
        if s.startswith(sfile):
            data['file'] = s.replace(sfile, '')
    return data


class JobManager(QAbstractListModel):
    """
    Manager to handle active jobs and stdout, stderr
    and progress parsers.
    Also functions as a Qt data model for a view
    displaying progress for each process.
    """

    _jobs = {}
    _state = {}
    _parsers = {}
    _linedata = {}

    status = Signal(str)
    result = Signal(str, object)

    def __init__(self):
        super().__init__()

        self.status_timer = QTimer()
        self.status_timer.setInterval(100)
        self.status_timer.timeout.connect(self.notify_status)
        self.status_timer.start()

    def notify_status(self):
        n_jobs = len(self._jobs)
        self.status.emit(f"{n_jobs} jobs")

    def execute(self, command, arguments, address, parsers=no_parsers):
        """
        Execute a command by starting a new process.
        """
        if address in self._jobs:
            return
        os.chdir('C:/Users/tedla/Downloads')
        # job_id = uuid.uuid4().hex
        job_id = address
        # By default, the signals do not have access to any information about
        # the process that sent it. So we use this constructor to annotate
        #  each signal with a job_id.

        def fwd_signal(target):
            return lambda *args: target(job_id, *args)

        self._parsers[job_id] = parsers

        # Set default status to waiting, 0 progress.
        self._state[job_id] = DEFAULT_STATE.copy()

        p = QProcess()
        p.readyReadStandardOutput.connect(fwd_signal(self.handle_output))
        p.readyReadStandardError.connect(fwd_signal(self.handle_output))
        p.stateChanged.connect(fwd_signal(self.handle_state))
        p.finished.connect(fwd_signal(self.done))

        self._jobs[job_id] = p

        self._linedata[job_id] = {}

        p.start(command, arguments)

        self.layoutChanged.emit()

    def handle_output(self, job_id):
        p = self._jobs[job_id]
        stderr = bytes(p.readAllStandardError()).decode("utf8")
        stdout = bytes(p.readAllStandardOutput()).decode("utf8")
        output = stderr + stdout

        parser = self._parsers.get(job_id)

        cleandata = parser.data(output)
        for key, val in cleandata.items():
            if val != '':
                self._linedata[job_id][key] = val

        if parser.progress:
            progress = parser.progress(output)
            if progress:
                self._state[job_id]["progress"] = progress
                self.layoutChanged.emit()

        if parser.data:
            data = parser.data(output)
            if data:
                self.result.emit(job_id, data)

    def handle_state(self, job_id, state):
        self._state[job_id]["status"] = state
        self.layoutChanged.emit()

    def done(self, job_id, exit_code, exit_status):
        """
        Task/worker complete. Remove it from the active workers
        dictionary. We leave it in worker_state, as this is used to
        to display past/complete workers too.
        """
        del self._jobs[job_id]
        self.layoutChanged.emit()

    def cleanup(self):
        """
        Remove any complete/failed workers from worker_state.
        """
        for job_id, s in list(self._state.items()):
            if s["status"] == QProcess.NotRunning:
                del self._state[job_id]
        self.layoutChanged.emit()

    # Model interface
    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the data structure.
            job_ids = list(self._state.keys())
            job_id = job_ids[index.row()]
            return job_id, self._state[job_id], self._linedata[job_id]

    def rowCount(self, index):
        return len(self._state)


class ProgressBarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # data is our status dict, containing progress, id, status
        job_id, data, ldata = index.model().data(index, Qt.DisplayRole)
        if data["progress"] > 0:
            color = QColor(STATUS_COLORS[data["status"]])

            brush = QBrush()
            brush.setColor(color)
            brush.setStyle(Qt.SolidPattern)

            width = option.rect.width() * data["progress"] / 100

            rect = QRect(option.rect)  #  Copy of the rect, so we can modify.
            rect.setWidth(width)

            painter.fillRect(rect, brush)

        pen = QPen()
        pen.setColor(Qt.black)
        painter.drawText(option.rect, Qt.AlignLeft, f"{job_id} : {ldata}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.job = JobManager()

        self.job.status.connect(self.statusBar().showMessage)
        # self.job.result.connect(self.display_result)

        self.progress = QListView()
        self.progress.setModel(self.job)
        delegate = ProgressBarDelegate()
        self.progress.setItemDelegate(delegate)

        self.text = QPlainTextEdit()
        # self.text.setReadOnly(True)

        button = QPushButton("Run a command")
        button.pressed.connect(self.on_button_click)

        clear = QPushButton("Clear")
        clear.pressed.connect(self.job.cleanup)

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.progress)
        layout.addWidget(button)
        layout.addWidget(clear)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        self.show()

    def on_button_click(self):
        text = self.text.toPlainText()
        for line in text.splitlines():
            line = line.strip()
            if line:
                self.run_command(line)
        self.text.setPlainText('')

    def run_command(self, textline):
        address = textline
        if address == '':
            return
        ypath = "C:\\Users\\tedla\prj\\qyoutube-dl\\ffmpeg\\youtube-dl.exe"
        pars = [
            '--ignore-errors',
            '--no-playlist',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '0',
            address
        ]
        self.job.execute(
            ypath,
            pars,
            address,
            parsers=parsers(progress=youtubedl_percent_parser,
                            data=extract_list_vars),
        )

    # end::startJob[]

    def display_result(self, job_id, data):
        self.text.appendPlainText(f"WORKER {job_id}: {data}")


app = QApplication(sys.argv)
window = MainWindow()
app.exec()
