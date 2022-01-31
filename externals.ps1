cd external
curl -L -o ffmpg.7z https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z
7z x ffmpg.7z
del ffmpg.7z
ren ffmpeg* ffmpeg
copy ffmpeg/bin/ffmpeg.exe .
copy ffmpeg/bin/ffprobe.exe .
copy C:\Windows\SysWOW64\msvcr100.dll .
7z x msvcr100.zip
curl -L -o youtube-dl.exe https://youtube-dl.org/downloads/latest/youtube-dl.exe
cd ..