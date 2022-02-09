import sys

from PySide6 import QtCore, QtGui, QtWidgets


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.resize(300, 300)

        # Model/View
        entries = ['one', 'two', 'three']
        model = QtGui.QStandardItemModel()
        delegate = ButtonDelegate()
        self.listView = QtWidgets.QListView(self)
        self.listView.setModel(model)
        self.listView.setItemDelegate(delegate)

        for i in entries:
            item = QtGui.QStandardItem(i)
            model.appendRow(item)

        # Layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.listView)
        self.setLayout(main_layout)

        # Connections
        delegate.delegateButtonPressed.connect(self.on_delegate_button_pressed)

    def on_delegate_button_pressed(self, index):

        print('"{}" delegate button pressed'.format(
            index.data(QtCore.Qt.DisplayRole)))


class ButtonDelegate(QtWidgets.QStyledItemDelegate):
    delegateButtonPressed = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self):
        super(ButtonDelegate, self).__init__()
        self.button = QtWidgets.QPushButton()
        self.button.setIcon(self.button.style().standardIcon(
            QtWidgets.QStyle.SP_BrowserReload))
        # self.button = DelegateButton()

    # def sizeHint(self, option, index):
    #     size = super(ButtonDelegate, self).sizeHint(option, index)
    #     size.setHeight(50)
    #     return size

    def editorEvent(self, event, model, option, index):

        # Launch app when launch button clicked
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            click_pos = event.pos()
            rect_button = self.rect_button

            if rect_button.contains(click_pos):
                self.delegateButtonPressed.emit(index)
                return True
            else:
                return False
        else:
            return False

    def paint(self, painter, option, index):
        spacing = 5
        icon_size = 20

        # Item BG #########################################
        painter.save()
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.setBrush(QtGui.QColor('green'))
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            painter.setBrush(QtGui.QColor('gray'))
        else:
            painter.setBrush(QtGui.QColor('white'))
        painter.drawRect(option.rect)
        painter.restore()

        # Item Text ########################################
        rect_text = option.rect
        QtWidgets.QApplication.style().drawItemText(
            painter,
            rect_text,
            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft,
            QtWidgets.QApplication.palette(),
            True,
            index.data(QtCore.Qt.DisplayRole)
        )

        # Custom Button ######################################
        self.rect_button = QtCore.QRect(
            option.rect.right() - icon_size - spacing,
            option.rect.bottom() - int(option.rect.height() / 2) - int(icon_size / 2),
            icon_size,
            icon_size
        )

        option = QtWidgets.QStyleOptionButton()
        option.initFrom(self.button)
        option.rect = self.rect_button
        # Button interactive logic
        if self.button.isDown():
            option.state = QtWidgets.QStyle.State_Sunken
        else:
            pass
        if self.button.isDefault():
            option.features = option.features or QtWidgets.QStyleOptionButton.DefaultButton
        option.icon = self.button.icon()
        option.iconSize = QtCore.QSize(icon_size, icon_size)

        painter.save()
        self.button.style().drawControl(
            QtWidgets.QStyle.CE_PushButton, option, painter, self.button)
        painter.restore()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
