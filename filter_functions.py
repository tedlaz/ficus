import re

pre = re.compile('\[download\]( +)(\d+.\d+)%', re.M)


def youtubedl_percent_parser(text2parse, previus) -> float:
    """
    [download] Destination: The Box Tops - The Letter.webm
    [download]  59.7% of 1.86MiB at 53.72KiB/s ETA 00:14
    """
    value = 0
    m = pre.search(text2parse)
    if m:
        value = float(m.group(2))
    if previus > value:
        return previus
    return value


def filter_text(out, last_info):
    """
    Extracts variables from lines
        [download] Destination: The Box Tops - The Letter.webm
        [ffmpeg] Destination: The Box Tops - The Letter.mp3
    """
    sdest = "[download] Destination: "
    sfile = "[ffmpeg] Destination: "
    for s in out.splitlines():
        if s.startswith(sdest):
            return s.replace(sdest, '')
        if s.startswith(sfile):
            return s.replace(sfile, '')
    return last_info
