import os
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


class TedQProcess:
    def __init__(self, pid: str, prg: str, pars: list, callback, _dir, filter_functions={}):
        """
        pid : unique id
        prg        : programm to run
        pars       : parameters list
        callback   : callback function
        dir        : directory to run process
        """
        self._pid = pid
        self._prg = prg
        self._pars = pars
        self._callback = callback
        self._active_directory = _dir
        self.stdout = ''
        self.stderr = ''
        self._real_state = ''
        self.state = ''
        self.filters = {key: val() for key, val in filter_functions.items()}
        self.function_percent = ffu.youtubedl_percent()

    @property
    def percent(self):
        return self.function_percent()

    def start(self):
        # if self.state == 'Finished':
        #     return
        self.state = ''
        if self._active_directory:
            os.chdir(self._active_directory)

        self._qprocess = Qc.QProcess()

        # connections
        self._qprocess.readyReadStandardOutput.connect(self._handle_stdout)
        self._qprocess.readyReadStandardError.connect(self._handle_stderr)
        self._qprocess.stateChanged.connect(self._handle_state)
        self._qprocess.finished.connect(self._handle_finished)

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
        for filter in self.filters.values():
            filter(sdata)
        self.function_percent(sdata)
        self._callback()

    def _handle_stderr(self):
        data = self._qprocess.readAllStandardError()
        sdata = bytes(data).decode(ENCODING, errors='replace')
        self.stderr = ' '.join(sdata.strip().split())
        for filter in self.filters.values():
            filter(sdata)
        if self._real_state != 'Running':
            self.state = 'Error'
        self._callback()

    def _handle_state(self, state):
        self._real_state = PROCESS_STATES[state]
        self.state = self._real_state
        self._callback()

    def _handle_finished(self):
        self._qprocess = None
        self.state = 'Finished'
        self._callback()

    def terminate(self):
        if self._qprocess:
            self._qprocess.close()
            self.state = 'Stopped'
            self._callback()

    @property
    def data(self) -> dict:
        rdic = {
            'pid': self._pid,
            'state': self.state,
            'out': self.stdout,
            'err': self.stderr,
            'log': self.out_err,
        }
        for key, value in self.filters.items():
            rdic[key] = value()
        return rdic
