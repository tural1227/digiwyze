@echo off
title Azure Tower - 3D Dasinmaz Emlak Sistemi
echo ======================================================
echo    AZURE TOWER - 3D DASINMAZ EMLAK SISTEMI
echo ======================================================
echo Server basladilir: http://127.0.0.1:3000
echo Brauzer avtomatik acilir...
echo.

start "" http://127.0.0.1:3000
"C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe" "%~dp0server.py"
pause
