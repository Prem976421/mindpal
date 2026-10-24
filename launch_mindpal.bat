@echo off
title MindPal Launcher
cd /d "%~dp0"

echo Checking if MindPal is running...
powershell -Command "try { $res = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/' -UseBasicParsing -TimeoutSec 1; exit 0 } catch { exit 1 }"
if %ERRORLEVEL% EQU 0 (
    echo MindPal is already active! Opening in your browser...
    start http://localhost:8000
    exit /b
)

echo Starting MindPal Local Server...
start "" pythonw main.py
timeout /t 2 /nobreak >nul
start http://localhost:8000
exit /b
