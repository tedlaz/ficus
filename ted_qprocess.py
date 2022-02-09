import os
import time
import uuid

from PySide6 import QtCore as Qc
from PySide6 import QtGui as Qg

import filter_functions as ffu
from qconfig import TPROCESS_INI

# ENCODING = 'WINDOWS-1253'
ENCODING = TPROCESS_INI['encoding'][0]


PROCESS_STATES = {
    Qc.QProcess.ProcessState.NotRunning: 'Not running',
    Qc.QProcess.ProcessState.Starting: 'Starting',
    Qc.QProcess.ProcessState.Running: 'Running',
}

MY_STATES_COLORS = {
    'Starting': Qg.QColor(TPROCESS_INI['starting'][0]),
    'Running': Qg.QColor(TPROCESS_INI['running'][0]),
    'Not Running': Qg.QColor(TPROCESS_INI['notrunning'][0]),
    'Error': Qg.QColor(TPROCESS_INI['error'][0]),
    'Stopped': Qg.QColor(TPROCESS_INI['stopped'][0]),
    'Finished': Qg.QColor(TPROCESS_INI['finished'][0]),
}


def last_element_as_text(a_list):
    if len(a_list) == 0:
        return ''
    return ' '.join(a_list[-1].strip().split())


class TedQProcess:
    def __init__(self, process_id: str, prg: str, pars: list, callback, _dir):
        """
        process_id : unique id
        prg        : programm to run
        pars       : parameters list
        callback   : callback function
        dir        : directory to run process
        """
        self._pid = process_id
        self._prg = prg
        self._pars = pars
        self._callback = callback
        self._active_directory = _dir
        self.stdout = ''
        self.stderr = ''
        self.state = ''
        self.filename = ''
        self.percent = 0

    def start(self):
        if self._active_directory:
            os.chdir(self._active_directory)
        self.percent = 0

        self._qprocess = Qc.QProcess()

        # connections
        self._qprocess.readyReadStandardOutput.connect(self._handle_stdout)
        self._qprocess.readyReadStandardError.connect(self._handle_stderr)
        self._qprocess.stateChanged.connect(self._handle_state)
        self._qprocess.finished.connect(self._process_finished)

        self._qprocess.start(self._prg, self._pars)

    @property
    def out_err(self):
        return ' '.join((self.stdout, self.stderr))

    @property
    def is_running(self):
        return self._qprocess != None

    @property
    def color(self):
        return MY_STATES_COLORS[self.state]

    def _handle_stdout(self):
        data = self._qprocess.readAllStandardOutput()
        sdata = bytes(data).decode(ENCODING, errors='replace')
        self.stdout = ' '.join(sdata.strip().split())
        self.filename = ffu.filter_text(sdata, self.filename)
        self.percent = ffu.youtubedl_percent_parser(sdata, self.percent)
        self._callback()

    def _handle_stderr(self):
        data = self._qprocess.readAllStandardError()
        sdata = bytes(data).decode(ENCODING, errors='replace')
        self.stderr = ' '.join(sdata.strip().split())
        self._callback()

    def _handle_state(self, state):
        self.state = PROCESS_STATES[state]
        self._callback()

    def _process_finished(self):
        self._qprocess = None
        self.state = 'Finished'
        self._callback()

    def terminate(self):
        if self._qprocess:
            self._qprocess.close()
            self.state = 'Stopped'
            self._callback()

    @property
    def data(self):
        return {
            'state': self.state,
            'out': self.stdout,
            'err': self.stderr,
            'filename': self.filename,
            'percent': self.percent,
            'out_err': self.out_err,
        }


class ProcessManager:
    """Create and manage TedProcesses
    """

    def __init__(self, callback, columns):
        self._keys = []  # index of keys
        self._ted_qprocesses = {}
        self._callback = callback
        # self._column_names = columns['column_names']
        self._columns = columns

    @property
    def row_counter(self):
        return len(self._keys)

    @property
    def column_counter(self):
        return len(self._columns)

    def column_name(self, column_index):
        return list(self._columns.keys())[column_index]

    def data(self, row_index):
        tprocess = self.get_process_by_index(row_index)
        ddata = tprocess.data
        final = []
        for actual_field in self._columns.values():
            final.append(ddata.get(actual_field, ''))
        return final

    def _is_valid_index(self, index):
        if index >= len(self._keys):
            return False
        if index < 0:
            return False
        return True

    def get_process_by_index(self, index):
        if not self._is_valid_index(index):
            return None
        pid = self._keys[index]
        return self._ted_qprocesses[pid]

    def new_process(self, prg: str, pars, run_dir):
        pid = uuid.uuid1().hex
        job = TedQProcess(pid, prg, pars, self._callback, run_dir)
        self._keys.append(pid)
        self._ted_qprocesses[pid] = job
        job.start()

    def terminate_process(self, index):
        tprocess = self.get_process_by_index(index)
        if tprocess:
            tprocess.terminate()

    def remove_process(self, index):
        if not self._is_valid_index(index):
            return
        self.terminate_process((index))
        pid = self._keys[index]
        del self._ted_qprocesses[pid]
        self._keys.remove(pid)
        self._callback()

    def remove_finished(self):
        for_delete = []
        for pid in self._keys:
            tprocess = self._ted_qprocesses[pid]
            if not tprocess.is_running:
                for_delete.append(pid)
        for pid in for_delete:
            del self._ted_qprocesses[pid]
            self._keys.remove(pid)
        self._callback()

    def restart_process(self, index):
        tprocess = self.get_process_by_index(index)
        if tprocess:
            if tprocess._qprocess:
                tprocess.terminate()
            tprocess.start()


class TModel(Qc.QAbstractTableModel):
    """
    columns: name, filter
    """
    status = Qc.Signal(str)

    def __init__(self, fields: dict):
        super().__init__()
        self.pm = ProcessManager(self.lmodel_callback, fields)

    def start(self, command, params, save_path):
        self.pm.new_process(command, params, save_path)

    def rowCount(self, index):
        return self.pm.row_counter

    def columnCount(self, parent):
        return self.pm.column_counter

    def lmodel_callback(self):
        self.layoutChanged.emit()
        self.status.emit(f"{self.pm.row_counter} jobs")

    def headerData(self, col, orientation, role):
        if orientation == Qc.Qt.Horizontal and role == Qc.Qt.DisplayRole:
            return self.pm.column_name(col)
        return None

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qc.Qt.DisplayRole:
            data = self.pm.data(index.row())
            return data[index.column()]

        # if role == Qc.Qt.BackgroundRole and index.column() == 3:
        #     key = self.pmdata._keys[index.row()]
        #     return self.pmdata._processes[key].color
