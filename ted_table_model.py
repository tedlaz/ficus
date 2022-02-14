from PySide6 import QtCore as Qc

import ted_process_manager as tpm


class TModel(Qc.QAbstractTableModel):
    """
    columns : list with names of visible columns

    valid column names: pid, state, out, err, log
                        + columns declared in filters

    filters: dictionary with extra columns as key and filter functions as value
    """
    status = Qc.Signal(str)

    def __init__(self, columns: list, filters: dict):
        super().__init__()
        self._columns = columns
        self.pm = tpm.ProcessManager(self._callback, filters)

    def start(self, name, command, params, save_path):
        self.pm.new_process(name, command, params, save_path)

    def rowCount(self, index):
        return self.pm.row_counter

    def columnCount(self, parent):
        return len(self._columns)

    def _callback(self):
        self.layoutChanged.emit()
        self.status.emit(f"{self.pm.row_counter} jobs")

    def headerData(self, col, orientation, role):
        if orientation == Qc.Qt.Horizontal and role == Qc.Qt.DisplayRole:
            return self._columns[col]
        return None

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qc.Qt.DisplayRole:
            data = self.pm.data(index.row())
            return data[self._columns[index.column()]]

        # if role == Qc.Qt.BackgroundRole and index.column() == 3:
        #     key = self.pmdata._keys[index.row()]
        #     return self.pmdata._processes[key].color
