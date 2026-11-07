@echo off
chcp 65001 >nul
setlocal
title Rongpat Studio
set "RS=%~dp0"
set "PATH=%RS%python;%RS%python\Library\bin;%RS%python\Library\mingw-w64\bin;%RS%python\Scripts;%PATH%"
set "PYTHONPATH=%RS%engine"
set "PYTHONUTF8=1"
set "PYTHONNOUSERSITE=1"
set "PYTHONIOENCODING=utf-8"
echo.
echo   ===  RONGPAT STUDIO  ===
echo.
echo Quick low-resolution test video. Use this while you are still fixing things.
echo (Tip: drag a project folder onto this file to skip the question.)
echo.
if "%~1"=="" ( "%RS%python\python.exe" -m rongpat make --ask --preview --ask-shots ) else ( "%RS%python\python.exe" -m rongpat make "%~1" --preview )
echo.
pause
