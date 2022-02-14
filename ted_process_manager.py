import uuid

from ted_qprocess import TedQProcess


class ProcessManager:
    """Create and manage TedProcesses
    """

    def __init__(self, callback, filter_dict):
        self._keys = []  # index of keys: ['key1', 'key2', ...]
        self._qprocesses = {}  # {'key1': process1, 'key2': process2, ...}
        self._callback = callback
        self._filters = filter_dict

    def new_process(self, name: str, prg: str, pars: list, run_dir: str):
        pid = name
        if name in self._keys:
            return
        new_job = TedQProcess(
            pid, prg, pars, self._callback, run_dir, self._filters)
        self._keys.append(pid)
        self._qprocesses[pid] = new_job
        new_job.start()

    @property
    def row_counter(self):
        return len(self._keys)

    def data(self, row_index):
        return self.get_process_by_index(row_index).data

    def get_process_by_index(self, index) -> TedQProcess:
        try:
            pid = self._keys[index]
        except IndexError:
            raise IndexError
        return self._qprocesses[pid]

    def terminate_process(self, index):
        tprocess = self.get_process_by_index(index)
        if tprocess:
            tprocess.terminate()

    def remove_process(self, index):
        self.terminate_process((index))
        pid = self._keys[index]
        del self._qprocesses[pid]
        self._keys.remove(pid)
        self._callback()

    def remove_finished(self):
        for_delete = []
        for pid in self._keys:
            tprocess = self._qprocesses[pid]
            if not tprocess.is_running:
                for_delete.append(pid)
        for pid in for_delete:
            del self._qprocesses[pid]
            self._keys.remove(pid)
        self._callback()

    def restart_process(self, index):
        tprocess = self.get_process_by_index(index)
        if tprocess:
            if tprocess._qprocess:
                tprocess.terminate()
            tprocess.start()
