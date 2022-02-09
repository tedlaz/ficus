# import os

from PySide6 import QtCore as Qc
from PySide6 import QtGui as Qg
from PySide6 import QtWidgets as Qw

# import ted_qprocess as tpr
# from button_delegate import ButtonDelegate
# from qconfig import INI, YOUTUBE_DL_EXE_PATH, output, typoi
# from version import VERSION


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
