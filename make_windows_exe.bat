python create_version.py
pyside6-rcc.exe .\resources.qrc -o resources.py
python create_nsi_installer.py
pyinstaller -F -w -i ficus.ico ficus.py
copy .\dist\ficus.exe .
rd /S /Q dist
rd /S /Q build
del ficus.spec
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
