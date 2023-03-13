"""Implementing filter functions with closures"""
import re

pre = re.compile(r"\[download\]( +)(\d+.\d+)%", re.M)


def youtubedl_percent():
    biggest_value = 0.0

    def inner_function(text2parse: str = "", reset=False):
        nonlocal biggest_value
        if reset:
            biggest_value = 0.0
        found = pre.search(text2parse)
        value = 0

        if found:
            value = float(found.group(2))

        if biggest_value < value:
            biggest_value = value
        return biggest_value

    return inner_function


def ffmpeg():
    value = ""

    def inner_function(text2parse: str = "", reset=False):
        nonlocal value
        if reset:
            value = ""
        if text2parse.startswith("frame="):
            value = text2parse

        return value

    return inner_function


def filter_text_down_ffmpeg():
    last_val = ""

    def inner_function(new_val: str = "", reset=False):
        nonlocal last_val
        if reset:
            last_val = ""
        sdest = "[download] Destination: "
        sfile = "[ffmpeg] Destination: "
        for str_line in new_val.splitlines():
            if str_line.startswith(sdest):
                last_val = str_line.replace(sdest, "")
            if str_line.startswith(sfile):
                last_val = str_line.replace(sfile, "")
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
