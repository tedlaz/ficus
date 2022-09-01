python create_version.py
pyside6-rcc.exe .\resources.qrc -o resources_rc.py
python create_inno_installer.py
pyinstaller -F -w -i ficus.ico ficus.py
copy .\dist\ficus.exe .
rd /S /Q dist
rd /S /Q build
del ficus.spec
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
