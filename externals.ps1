mkdir ex1
cd ex1
curl -L -o ffmpg.7z https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z
7z e ffmpg.7z  *.exe -r
copy C:\Windows\SysWOW64\msvcr100.dll .
curl -L -o youtube-dl.exe https://youtube-dl.org/downloads/latest/youtube-dl.exe
cd ..