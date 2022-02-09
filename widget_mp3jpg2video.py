from PySide6 import QtCore as Qc
from PySide6 import QtGui as Qg
from PySide6 import QtWidgets as Qw

import ted_qprocess as tpr
from button_delegate import ButtonDelegate
from qconfig import FFMPEG_PATH, videoformat


class UploadToYoutubeWidget(Qw.QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = Qw.QVBoxLayout(self)

        self.jobs = tpr.TModel({'state': 'state', 'message': 'out_err'})

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

        self.log = Qw.QTableView()
        self.log.setModel(self.jobs)
        self.log.setAlternatingRowColors(True)
        self.log.setSelectionMode(Qw.QAbstractItemView.NoSelection)
        self.log.setContextMenuPolicy(Qc.Qt.CustomContextMenu)
        self.log.customContextMenuRequested.connect(self.on_context)
        self.log.setColumnWidth(0, 60)
        self.log.setColumnWidth(1, 200)
        # self.runinfo.setShowGrid(False)
        self.log.horizontalHeader().setStretchLastSection(True)
        self.log.resizeRowsToContents()
        layout.addWidget(self.log)

        self.bexec.clicked.connect(self.render)

    def on_context(self, point):
        acre = Qg.QAction(
            'stop',
            self,
            statusTip='stop job',
            triggered=self.terminate
        )
        arestart = Qg.QAction(
            'restart',
            self,
            statusTip='restart job',
            triggered=self.restart
        )
        arem = Qg.QAction(
            'remove',
            self,
            statusTip='remove job',
            triggered=self.remove
        )
        aremfin = Qg.QAction(
            'remove all finished',
            self,
            statusTip='remove finished jobs',
            triggered=self.remove_finished
        )

        menu = Qw.QMenu("Menu", self)
        menu.addAction(acre)
        menu.addAction(arestart)
        menu.addAction(arem)
        menu.addAction(aremfin)
        menu.exec(self.log.mapToGlobal(point))

    def terminate(self):
        idx = self.log.currentIndex().row()
        # print(idx)
        if idx < 0:
            return
        self.jobs.pm.terminate_process(idx)

    def remove(self):
        idx = self.log.currentIndex().row()
        if idx < 0:
            return
        self.jobs.pm.remove_process(idx)

    def remove_finished(self):
        self.jobs.pm.remove_finished()

    def restart(self):
        idx = self.log.currentIndex().row()
        if idx < 0:
            return
        self.jobs.pm.restart_process(idx)

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
        # fpaths = {'mp3': '', 'image': '', 'out': ''}
        image_paths = []
        mp3_files = []
        fpaths = []
        extension = self.cb.currentText()
        for line in self.mp3.toPlainText().splitlines():
            line = line.strip().replace('file:///', '')
            if line.endswith('.mp3'):
                # fpaths['mp3'] = line
                # fpaths['out'] = line.replace('.mp3', f'.{extension}')
                mp3_files.append(line)
            if line.endswith(('.jpg', '.png')):
                image_paths.append(line)
                # fpaths['image'] = line

        if (image_paths == []) or (mp3_files == []):
            Qw.QMessageBox.critical(
                self,
                "Error",
                "Please provide mp3 and image files in order to proceed"
            )
            return fpaths, True

        for mp3 in mp3_files:
            fpaths.append({'mp3': mp3, 'image': image_paths[0], 'out': mp3.replace(
                '.mp3', f'.{extension}')})
        return fpaths, False

    def render(self):
        fpaths, error = self.parse_mp3()
        if error:
            return
        for fpath in fpaths:
            pars = [
                "-loop",
                "1",
                "-i",
                fpath['image'],
                "-i",
                fpath['mp3'],
                "-c:v",
                "libx264",
                "-tune",
                "stillimage",
                "-c:a",
                "copy",
                "-pix_fmt",
                "yuv420p",
                "-shortest",
                fpath['out'],
            ]
            self.jobs.start(FFMPEG_PATH, pars, '')
        # pars = [
        #     "-r",
        #     "1",
        #     "-loop",
        #     "1",
        #     "-y",
        #     "-i",
        #     fpaths['image'],
        #     "-i",
        #     fpaths['mp3'],
        #     "-c:a",
        #     "copy",
        #     "-r",
        #     "1",
        #     "-vcodec",
        #     "libx264",
        #     "-shortest",
        #     fpaths['out'],
        # ]

        self.mp3.setPlainText('')

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    # def handle_stdout(self):
    #     data = self.p.readAllStandardOutput()
    #     stdout = bytes(data).decode("utf8", errors='ignore')
    #     self.message(stdout)

    # def handle_stderr(self):
    #     data = self.p.readAllStandardError()
    #     stderr = bytes(data).decode("utf8", errors='ignore')
    #     self.message(stderr)

    # def handle_state(self, state):
    #     states = {
    #         Qc.QProcess.ProcessState.NotRunning: 'Not running',
    #         Qc.QProcess.ProcessState.Starting: 'Starting',
    #         Qc.QProcess.ProcessState.Running: 'Running',
    #     }
    #     state_name = states[state]
    #     self.message(f"State changed: {state_name}")

    # def process_finished(self):
    #     self.message("Process finished.")
    #     self.p = None
    #     self.message("youtube-dl update Finished")
