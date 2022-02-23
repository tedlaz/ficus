import os

from version import VERSION

application_path = os.path.dirname(__file__)
external_dir = os.path.join(application_path, 'external')

ffmpeg = "ffmpeg.exe"
ffprobe = "ffprobe.exe"
msvcr100 = "msvcr100.dll"
youtube_dl = "youtube-dl.exe"
ffmpeg_source = f"{external_dir}\\{ffmpeg}"
ffprobe_source = f"{external_dir}\\{ffprobe}"
msvcr100_source = f"{external_dir}\\{msvcr100}"
youtube_dl_source = f"{external_dir}\\{youtube_dl}"

text = (f"""

#define MyAppName "ficus"
#define MyAppVersion "{VERSION}"
#define MyAppPublisher "Ted Lazaros"
#define MyAppURL "https://github.com/tedlaz/ficus"
#define MyAppExeName "ficus.exe"
"""

        """
[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{F80FDFBC-6D33-45A4-B24D-D8F1D274B11E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={%USERPROFILE}\\{#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=.
OutputBaseFilename=setup_ficus.{#MyAppVersion}
SetupIconFile=.\\ficus_setup.ico
UninstallDisplayIcon={app}\\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: .\\{#MyAppExeName}; DestDir: "{app}"; Flags: ignoreversion
"""

        f"""
Source: {ffmpeg_source}; DestDir: "{{app}}"; Flags: ignoreversion
Source: {ffprobe_source}; DestDir: "{{app}}"; Flags: ignoreversion
Source: {msvcr100_source}; DestDir: "{{app}}"; Flags: ignoreversion
Source: {youtube_dl_source}; DestDir: "{{app}}"; Flags: ignoreversion
"""

        """
[Icons]
Name: "{autoprograms}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\\ficus.ini"
"""
        )

if __name__ == '__main__':
    with open('installer.iss', 'w') as f:
        f.write(text)
