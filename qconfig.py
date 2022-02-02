import os
import sys

from PySide6.QtCore import QSettings

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    app_path = sys.executable
    frozen_dir_name = os.path.dirname(app_path)
    YOUTUBE_DL_EXE_PATH = os.path.join(frozen_dir_name, 'youtube-dl.exe')
    FFMPEG_PATH = os.path.join(frozen_dir_name, 'ffmpeg.exe')
    INI_PATH = os.path.join(frozen_dir_name, 'ficus.ini')
else:
    app_path = os.path.dirname(__file__)
    YOUTUBE_DL_EXE_PATH = os.path.join(app_path, 'external', 'youtube-dl.exe')
    FFMPEG_PATH = os.path.join(app_path, 'external', 'ffmpeg.exe')
    INI_PATH = os.path.join(app_path, 'ficus.ini')

initial_ini = """[General]
save_path=
thubnails=true
metadata=false
typoi=mp3
output=title
encoding=WINDOWS-1253
videoformat=avi mp4 mkv

[Typoi]
video=
mp3=--ignore-errors --no-playlist --extract-audio --audio-format mp3 --audio-quality 0

[Output]
default=
title=--output %(title)s.%(ext)s
title-artist=--output %(title)s-%(artist)s.%(ext)s
artist-title=--output %(artist)s-%(title)s.%(ext)s
"""

if not os.path.isfile(INI_PATH):
    with open(INI_PATH, 'w', encoding='utf8') as fil:
        fil.write(initial_ini)

INI = QSettings('ficus.ini', QSettings.IniFormat)


def ini2dic(mainkey):
    """
    returns dictionary: {keyval1: [a1, a2, ...], keyval2: [b1, ..]}
    """
    fdict = {}
    INI.beginGroup(mainkey)
    for key in INI.allKeys():
        fdict[key] = INI.value(key).split()
    INI.endGroup()
    return fdict


typoi = ini2dic('typoi')
output = ini2dic('output')
videoformat = INI.value('videoformat').split()
