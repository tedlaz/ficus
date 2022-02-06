from datetime import datetime

VERSION = datetime.now().isoformat().replace(
    '-', '').replace('T', '.').replace(':', '')[2:13]

with open('version.py', 'w', encoding='utf8') as f:
    f.write(f"\nVERSION = '{VERSION}'\n")
