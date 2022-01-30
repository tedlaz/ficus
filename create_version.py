from datetime import date

VERSION = date.today().isoformat().replace('-', '')[2:]

with open('version.py', 'w', encoding='utf8') as f:
    f.write(f"\nVERSION = '{VERSION}'\n")
