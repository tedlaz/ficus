import os
from collections import namedtuple

from PySide6.QtCore import (QAbstractListModel, QObject, QProcess, QRect,
                            QRunnable, Qt, QTimer, Signal, Slot)
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import (QApplication, QLineEdit, QListView, QMainWindow,
                               QPlainTextEdit, QProgressBar, QPushButton,
                               QStyledItemDelegate, QVBoxLayout, QWidget)

STATUS_COLORS = {
    QProcess.NotRunning: "#93cffe",
    QProcess.Starting: "#fdbf6f",
    QProcess.Running: "#91de67",
}

STATES = {
    QProcess.NotRunning: "Not running",
    QProcess.Starting: "Starting...",
    QProcess.Running: "Running...",
}

DEFAULT_STATE = {"progress": 0, "status": QProcess.Starting}
Parsers = namedtuple("parsers", "progress data")
no_parsers = Parsers(None, None)


class JobManager(QAbstractListModel):
    """Abstract List Model Manager
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

    def execute(self, command, arguments, address, download_dir, parsers=no_parsers):
        """
        Execute a command by starting a new process.
        """
        if address in self._jobs:
            return
        os.chdir(download_dir)
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


""" DELEGATE EXAMPLE

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
"""
