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
echo Make a new story project.
echo.
"%RS%python\python.exe" -m rongpat new --ask
echo.
pause
