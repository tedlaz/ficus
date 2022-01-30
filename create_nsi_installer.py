import os

from version import VERSION

application_path = os.path.dirname(__file__)
external_dir = os.path.join(application_path, 'external')


app_name = 'ficus'
executable_file = "ficus.exe"
ffmpeg = "ffmpeg.exe"
ffprobe = "ffprobe.exe"
msvcr100 = "msvcr100.dll"
youtube_dl = "youtube-dl.exe"
ini_file = "ficus.ini"
ffmpeg_source = f"{external_dir}\\{ffmpeg}"
ffprobe_source = f"{external_dir}\\{ffprobe}"
msvcr100_source = f"{external_dir}\\{msvcr100}"
youtube_dl_source = f"{external_dir}\\{youtube_dl}"
# ini_file_source = f"{external_dir}\\{ini_file}"
installer_name = f'setup_{app_name}'
installer_executable = f"{installer_name}.v{VERSION}.exe"
default_install_dir = app_name
registry_key = app_name


text = f"""
SetCompressor /SOLID lzma
Name "{app_name}"
OutFile "{installer_executable}"
RequestExecutionLevel admin
Unicode True
InstallDir $PROGRAMFILES\\{default_install_dir}
InstallDirRegKey HKLM "Software\\NSIS_{registry_key}" "Install_Dir"

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

Section "{app_name} (required)"
  SectionIn RO
  SetOutPath "$INSTDIR"
  File "{executable_file}"
  File "{ffmpeg_source}"
  File "{ffprobe_source}"
  File "{msvcr100_source}"
  File "{youtube_dl_source}"
  WriteRegStr HKLM SOFTWARE\\NSIS_{registry_key} "Install_Dir" "$INSTDIR"

  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" "DisplayName" "{app_name}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" "UninstallString" "$INSTDIR\\uninstall.exe"

  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" "NoModify" 1
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" "NoRepair" 1
  WriteUninstaller "$INSTDIR\\uninstall.exe"

SectionEnd

Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\\{app_name}"
  CreateShortcut "$SMPROGRAMS\\{app_name}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
  CreateShortcut "$SMPROGRAMS\\{app_name}\\{app_name} (MakeNSISW).lnk" "$INSTDIR\\{executable_file}"

SectionEnd


Section "Uninstall"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
  DeleteRegKey HKLM SOFTWARE\\NSIS_{app_name}

  ; Remove files and uninstaller
  Delete $INSTDIR\\{executable_file}
  Delete $INSTDIR\\{ffmpeg}
  Delete $INSTDIR\\{ffprobe}
  Delete $INSTDIR\\{msvcr100}
  Delete $INSTDIR\\{youtube_dl}
  Delete $INSTDIR\\{ini_file}
  Delete $INSTDIR\\uninstall.exe

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\\{executable_file}\\*.lnk"

  ; Remove directories
  RMDir "$SMPROGRAMS\\{app_name}"
  RMDir "$INSTDIR"

SectionEnd
"""

if __name__ == '__main__':
    with open('installer.nsi', 'w') as f:
        f.write(text)
