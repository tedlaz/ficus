"""Implementing filter functions with closures"""
import re

pre = re.compile('\[download\]( +)(\d+.\d+)%', re.M)


def youtubedl_percent():
    biggest_value = 0.0

    def inner_function(text2parse: str = '', reset=False):
        nonlocal biggest_value
        if reset:
            biggest_value = 0.0
        m = pre.search(text2parse)
        value = 0

        if m:
            value = float(m.group(2))

        if biggest_value < value:
            biggest_value = value
        return biggest_value

    return inner_function


def ffmpeg():
    value = ''

    def inner_function(text2parse: str = '', reset=False):
        nonlocal value
        if reset:
            value = ''
        if text2parse.startswith('frame='):
            value = text2parse

        return value

    return inner_function


def filter_text_down_ffmpeg():
    last_val = ''

    def inner_function(new_val: str = '', reset=False):
        nonlocal last_val
        if reset:
            last_val = ''
        sdest = "[download] Destination: "
        sfile = "[ffmpeg] Destination: "
        for s in new_val.splitlines():
            if s.startswith(sdest):
                last_val = s.replace(sdest, '')
            if s.startswith(sfile):
                last_val = s.replace(sfile, '')
        return last_val
    return inner_function


def test_biggest():
    biggest_value = 0.0

    def replace(value: float = 0.0, reset=False):
        nonlocal biggest_value
        if reset:
            biggest_value = 0.0
        if biggest_value < value:
            biggest_value = float(value)
        return biggest_value

    return replace
