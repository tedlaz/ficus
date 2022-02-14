import os

from PySide6 import QtCore as Qc
from PySide6 import QtGui as Qg
from PySide6 import QtWidgets as Qw

import image_resize as imre
# import ted_qprocess as tpr
import ted_table_model as ttm
from filter_functions import ffmpeg
from qconfig import FFMPEG_PATH, INI, VIDEOSIZES, videoformat


class UploadToYoutubeWidget(Qw.QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = Qw.QVBoxLayout(self)

        self.jobs = ttm.TModel(
            ['state', 'pid', 'ffmpeg info'],
            {'ffmpeg info': ffmpeg})

        self.mp3 = Qw.QPlainTextEdit()
        self.mp3.setToolTip("Drag and drop or copy, mp3 and image files here")
        self.mp3.setMaximumHeight(100)
        self.mp3.setAcceptDrops(False)
        layout.addWidget(self.mp3)

        path_layout = Qw.QHBoxLayout()
        layout.addLayout(path_layout)

        hlay = Qw.QHBoxLayout()
        layout.addLayout(hlay)

        self.cb = Qw.QComboBox()
        self.cb.setToolTip('Type of video')
        # self.cb.setMinimumWidth(100)
        for typ in videoformat:
            self.cb.addItem(typ)
        self.cb.setCurrentText(INI.value("video_type", defaultValue='avi'))
        hlay.addWidget(self.cb)

        self.save_path = Qw.QLineEdit(self)
        self.save_path.setToolTip('Video save path')
        self.save_path.setReadOnly(True)
        save_path = INI.value("save_video_path", defaultValue='')
        self.save_path.setText(str(save_path))
        if not os.path.exists(save_path):
            self.save_path.setText('')

        self.vsize = Qw.QComboBox()
        self.vsize.setToolTip('Video size')
        for vsize in VIDEOSIZES.keys():
            self.vsize.addItem(vsize)
        self.vsize.setCurrentText(
            INI.value("video_size", defaultValue='360p(640x360)'))
        hlay.addWidget(self.vsize)

        self.bpath = Qw.QToolButton(self)
        self.bpath.setText('...')
        self.bpath.setToolTip('Select video save path')

        path_layout.addWidget(Qw.QLabel('Video save path :'))
        path_layout.addWidget(self.save_path)
        path_layout.addWidget(self.bpath)

        # sp2 = Qw.QSpacerItem(40, 20, Qw.QSizePolicy.Policy.Expanding,
        #                      Qw.QSizePolicy.Policy.Minimum)
        # hlay.addItem(sp2)

        self.color_label = Qw.QLabel()
        # self.color_label.setLineWidth(2)
        self.color_label.setToolTip('Image background color')
        # frame_style = Qw.QFrame.Sunken | Qw.QFrame.Panel
        # self.color_label.setFrameStyle(frame_style)
        self.color_label.setMinimumWidth(50)
        self.set_color2color_label()
        self.color_button = Qw.QToolButton()
        self.color_button.setText('...')
        self.color_button.setToolTip('Set background color')

        self.bopen_dir = Qw.QPushButton('open dir', self)
        self.bopen_dir.setFocusPolicy(Qc.Qt.FocusPolicy.NoFocus)
        self.bopen_dir.clicked.connect(self.open_dir)

        hlay.addWidget(self.color_label)
        hlay.addWidget(self.color_button)
        hlay.addWidget(self.bopen_dir)

        sp2 = Qw.QSpacerItem(40, 20, Qw.QSizePolicy.Policy.Expanding,
                             Qw.QSizePolicy.Policy.Minimum)
        hlay.addItem(sp2)
        self.bexec = Qw.QPushButton("create videos")
        hlay.addWidget(self.bexec)

        self.log = Qw.QTableView()
        self.log.setStyleSheet(
            "QHeaderView::section { color: blue; }")
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
        self.bpath.clicked.connect(self.update_path)
        self.color_button.clicked.connect(self.set_color)

    def open_dir(self):
        os.startfile(self.save_path.text())

    def update_settings_on_run(self):
        INI.setValue("video_type", self.cb.currentText())
        INI.setValue("video_size", self.vsize.currentText())

    def set_color2color_label(self):
        color_name = INI.value("video_background_color", defaultValue='black')
        # self.color_label.setFrameShape(Qw.QFrame.Box)
        # self.color_label.setText(color_name)
        color = Qg.QColor(color_name)
        self.color_label.setPalette(Qg.QPalette(color))
        self.color_label.setAutoFillBackground(True)

    def set_color(self):
        old = INI.value("video_background_color", defaultValue='black')
        color = Qw.QColorDialog.getColor(old, self, "Select Color")

        if color.isValid():
            # self.color_label.setText(color.name())
            self.color_label.setPalette(Qg.QPalette(color))
            self.color_label.setAutoFillBackground(True)
            INI.setValue("video_background_color", color.name())

    def update_path(self):
        old = self.save_path.text()
        opt = Qw.QFileDialog.Option.DontResolveSymlinks | Qw.QFileDialog.Option.ShowDirsOnly
        path = Qw.QFileDialog.getExistingDirectory(self, 'path', old, opt)
        if path:
            self.save_path.setText(path)
            INI.setValue("save_video_path", path)

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
        ftext = dropped_txt.split('\n')
        for line in ftext:
            if line.lower().endswith(('.mp3', '.jpg', '.png')):
                self.mp3.appendPlainText(line.replace('file:///', ''))

    def message(self, message):
        self.log.appendPlainText(f"{message}")

    def parse_mp3(self):
        image_paths = []
        mp3_files = []
        fpaths = []
        extension = self.cb.currentText()
        for line in self.mp3.toPlainText().splitlines():
            line = line.strip().replace('file:///', '')
            if line.endswith('.mp3'):
                mp3_files.append(line)
            if line.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_paths.append(self.resize_image(line))

        if (image_paths == []) or (mp3_files == []):
            Qw.QMessageBox.critical(
                self,
                "Error",
                "Please provide at least one mp3 file and one image file in order to proceed"
            )
            return fpaths, True

        if not self.save_path.text():
            Qw.QMessageBox.critical(
                self, "Error", "Video save path not set.")
            return fpaths, True

        for i, mp3 in enumerate(mp3_files):
            vid_name = (os.path.basename(mp3).replace('.mp3', f'.{extension}'))
            vpath = os.path.join(self.save_path.text(), vid_name)
            img = image_paths[i] if len(image_paths) > i else image_paths[-1]
            fpaths.append({'mp3': mp3, 'image': img, 'out': vpath})

        return fpaths, False

    def resize_image(self, img_path: str):
        size_index = self.vsize.currentText()
        color = INI.value("video_background_color", defaultValue='black')
        return imre.resize(img_path, self.save_path.text(), VIDEOSIZES[size_index], color)

    def render(self):
        self.update_settings_on_run()
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
            self.jobs.start(fpath['out'], FFMPEG_PATH, pars, '')
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
