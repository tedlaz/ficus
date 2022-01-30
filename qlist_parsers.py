import re

pre = re.compile('\[download\]( +)(\d+.\d+)%', re.M)


def youtubedl_percent_parser(output):
    """
    [download] Destination: The Box Tops - The Letter.webm
    [download]  59.7% of 1.86MiB at 53.72KiB/s ETA 00:14
    """
    m = pre.search(output)
    if m:
        return float(m.group(2))


def extract_list_vars(l):
    """
    Extracts variables from lines
        [download] Destination: The Box Tops - The Letter.webm
        [ffmpeg] Destination: The Box Tops - The Letter.mp3
    """
    data = {'file': '', 'size': ''}
    sdest = "[download] Destination: "
    sfile = "[ffmpeg] Destination: "
    for s in l.splitlines():
        if s.startswith(sdest):
            data['file'] = s.replace(sdest, '')
        if s.startswith(sfile):
            data['file'] = s.replace(sfile, '')
    return data
