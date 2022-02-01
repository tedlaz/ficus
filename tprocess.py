import os
import re
import uuid
from collections import namedtuple
from unicodedata import name

from PySide6 import QtCore as Qc
from PySide6 import QtGui as Qg

pre = re.compile('\[download\]( +)(\d+.\d+)%', re.M)


def youtubedl_percent_parser(text2parse) -> float:
    """
    [download] Destination: The Box Tops - The Letter.webm
    [download]  59.7% of 1.86MiB at 53.72KiB/s ETA 00:14
    """
    m = pre.search(text2parse)
    if m:
        return float(m.group(2))
    return 0


def filter_text(out, last_info):
    """
    Extracts variables from lines
        [download] Destination: The Box Tops - The Letter.webm
        [ffmpeg] Destination: The Box Tops - The Letter.mp3
    """
    sdest = "[download] Destination: "
    sfile = "[ffmpeg] Destination: "
    for s in out.splitlines():
        if s.startswith(sdest):
            return s.replace(sdest, '')
        if s.startswith(sfile):
            return s.replace(sfile, '')
    return last_info


PROCESS_STATES = {
    Qc.QProcess.ProcessState.NotRunning: 'Not running',
    Qc.QProcess.ProcessState.Starting: 'Starting',
    Qc.QProcess.ProcessState.Running: 'Running',
}

STATUS_COLORS = {
    Qc.QProcess.NotRunning: "#67aade",
    Qc.QProcess.Starting: "#fdbf6f",
    Qc.QProcess.Running: "#91de67",
}

COLORS = {
    True: Qg.QColor("#91de67"),
    False: Qg.QColor("#67aade")
}


def last(lista):
    if len(lista) == 0:
        return ''
    return ' '.join(lista[-1].strip().split())


PData = namedtuple('PData', 'out err state finished percent')


class TProcess:
    def __init__(self, pid, callback, program: str, parameters: list, down_dir: str = ''):
        self.pid = pid
        self._callback = callback
        self._prg = program
        self._pars = parameters
        self._down_dir = down_dir
        self.start()

    def start(self):
        self._info = self._pars[-1:]
        self._std_outs = []
        self._std_errs = []
        self._states = []
        self._finished = []
        self._percent = []
        if self._down_dir != '':
            os.chdir(self._down_dir)
        self._process = Qc.QProcess()
        self._process.readyReadStandardOutput.connect(self.handle_stdout)
        self._process.readyReadStandardError.connect(self.handle_stderr)
        self._process.stateChanged.connect(self.handle_state)
        self._process.finished.connect(self.process_finished)
        self._process.start(self._prg, self._pars)

    def __str__(self):
        return f"Tprocess(name={self.pid}, program={self._prg} {self._pars})"

    @property
    def is_running(self) -> bool:
        if len(self._states) == 0:
            return False
        return self._states[-1] == 'Running'

    @property
    def color(self):
        if len(self.err) > 0:
            return Qg.QColor("#f71010")
        return COLORS[self.is_running]

    def handle_percent(self, std_out_text):
        result = youtubedl_percent_parser(std_out_text)
        if len(self._percent) == 0:
            self._percent.append(result)
        if self._percent[-1] < result:
            self._percent.append(result)

    def terminate(self):
        if self._process:
            self._process.close()
            self._std_errs.append('terminated by user')
            self._callback(self)

    @property
    def out(self):
        return last(self._std_outs)

    @property
    def info(self):
        return self._info

    @property
    def err(self):
        return last(self._std_errs)

    @property
    def state(self):
        return last(self._states)

    @property
    def finished(self):
        len(last(self._finished)) > 0

    @property
    def percent(self):
        if len(self._percent) == 0:
            return 0
        return self._percent[-1]

    def last_data(self):
        # return PData(self.out, self.err, self.state, self.finished, self.percent)
        return (self.percent, self.info)

    def handle_stdout(self):
        data = self._process.readAllStandardOutput()
        sdata = bytes(data).decode("utf8", errors='ignore')
        self._std_outs.append(sdata)
        self._info = filter_text(sdata, self._info)
        self.handle_percent(sdata)
        self._callback(self)

    def handle_stderr(self):
        data = self._process.readAllStandardError()
        sdata = bytes(data).decode("utf8", errors='ignore')
        self._std_errs.append(sdata)
        self._info = f'{self._pars[-1]} error'
        self._percent.append(100)
        self._callback(self)

    def handle_state(self, state):
        state_name = PROCESS_STATES[state]
        self._states.append(state_name)
        self._callback(self)

    def process_finished(self):
        self._process = None
        self._finished.append('finished')
        self._callback(self)


class TProcessManager:

    def __init__(self, callback_function):
        self._keys = []
        self._processes = {}
        self._callback = callback_function
    #     self.download_dir = ''

    # def set_download_dir(self, download_dir):
    #     self.download_dir = download_dir

    @property
    def column_titles(self):
        return ('Status', 'Info')

    @property
    def column_number(self):
        return len(self.column_titles)

    def last_data(self, pid):
        return self._processes[pid].last_data()

    @property
    def row_number(self):
        return len(self._processes)

    def callback(self, pid):
        self._callback(pid)

    def start(self, program: str, parameters: list, down_dir: str):
        pid = uuid.uuid1().hex
        self._keys.append(pid)
        job = TProcess(pid, self.callback, program, parameters, down_dir)
        self._processes[pid] = job

    def terminate(self, index):
        key = self._keys[index]
        self._processes[key].terminate()

    def remove(self, index):
        key = self._keys[index]
        del self._processes[key]
        self._keys.remove(key)
        self._callback(key)

    def restart(self, index):
        key = self._keys[index]
        if not self._processes[key].is_running:
            self._processes[key].start()

    def color(self, index):
        key = self._keys[index]
        return self._processes[key].color


class LModel(Qc.QAbstractListModel):
    def __init__(self, external_callback=None):
        super().__init__()
        self.ex_call = external_callback
        self.pmdata = TProcessManager(self.lmodel_callback)

    def start(self, command, params):
        self.pmdata.start(command, params)

    def rowCount(self, index):
        return self.pmdata.row_number

    def lmodel_callback(self, pid):
        if self.ex_call:
            self.ex_call(pid)
        self.layoutChanged.emit()

    def data(self, index, role):
        if role == Qc.Qt.DisplayRole:
            key = self.pmdata._keys[index.row()]
            data = self.pmdata.last_data(key)
            return f"{data.out} - {data.err} - {data.state} - {data.finished}"


class TModel(Qc.QAbstractTableModel):
    status = Qc.Signal(str)

    def __init__(self, external_callback=None):
        super().__init__()
        self.ex_call = external_callback
        self.pmdata = TProcessManager(self.lmodel_callback)

    def start(self, command, params, save_path):
        self.pmdata.start(command, params, save_path)

    def rowCount(self, index):
        return self.pmdata.row_number

    def columnCount(self, parent):
        return self.pmdata.column_number

    def lmodel_callback(self, pid):
        if self.ex_call:
            self.ex_call(pid)
        self.layoutChanged.emit()
        self.status.emit(f"{self.pmdata.row_number} jobs")

    def headerData(self, col, orientation, role):
        if orientation == Qc.Qt.Horizontal and role == Qc.Qt.DisplayRole:
            return self.pmdata.column_titles[col]
        return None

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qc.Qt.DisplayRole:
            key = self.pmdata._keys[index.row()]
            data = self.pmdata.last_data(key)
            return data[index.column()]

        # if role == Qc.Qt.BackgroundRole and index.column() == 3:
        #     key = self.pmdata._keys[index.row()]
        #     return self.pmdata._processes[key].color
