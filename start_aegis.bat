@echo off
setlocal
title AEGIS Space Weather and GNSS Forecasting System
cd /d "%~dp0"

echo ======================================================================
echo    AEGIS: Space Weather and GNSS Positioning Error Forecasting System
echo ======================================================================
echo.

:: 1. Verify Python Installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not detected in your PATH.
    echo Please install Python 3.10+ and make sure it is added to PATH.
    echo.
    pause
    exit /b 1
)

:: 2. Check and clean up any previous server instance on port 8000
python -c "import subprocess; out = subprocess.getoutput('netstat -ano'); [subprocess.run(f'taskkill /F /PID {line.split()[-1]}', shell=True, capture_output=True) for line in out.splitlines() if ':8000' in line and 'LISTENING' in line]" >nul 2>&1

:: 3. Launch browser helper in background after short startup delay
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 4; Start-Process 'http://localhost:8000'"

:: 4. Start AEGIS Server (Serving API, Web Dashboard, and Live Ingest Worker)
echo [INFO] Starting AEGIS server, loading 24 ML models, and starting live NOAA ingest...
echo [INFO] Web UI: http://localhost:8000
echo [INFO] To stop AEGIS, press Ctrl+C or close this window.
echo ======================================================================
echo.

python -m uvicorn api:app --host 127.0.0.1 --port 8000

echo.
echo [INFO] AEGIS server has stopped.
pause
