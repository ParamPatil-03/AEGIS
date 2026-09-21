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
echo [INFO] Cleaning up any previous server on port 8000...
python -c "import subprocess; out = subprocess.getoutput('netstat -ano'); [subprocess.run(f'taskkill /F /PID {line.split()[-1]}', shell=True, capture_output=True) for line in out.splitlines() if ':8000' in line and 'LISTENING' in line]" >nul 2>&1
timeout /t 1 /nobreak >nul

:: 3. Launch AEGIS server in background (separate window stays open)
echo [INFO] Starting AEGIS server (loading 24 ML models + live NOAA ingest)...
echo [INFO] This may take 30-60 seconds for models to load. Please wait...
echo [INFO] Web UI will open automatically when ready: http://localhost:8000
echo ======================================================================
echo.

start "AEGIS Server" cmd /k "cd /d "%~dp0" && python -m uvicorn api:app --host 127.0.0.1 --port 8000"

:: 4. Wait for server to actually be ready by polling port 8000
echo [INFO] Waiting for server to become ready...
:WAIT_LOOP
timeout /t 2 /nobreak >nul
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=2)" >nul 2>&1
if errorlevel 1 (
    <nul set /p "=."
    goto WAIT_LOOP
)

:: 5. Server is up — open browser
echo.
echo [SUCCESS] AEGIS is ready! Opening browser...
start "" "http://localhost:8000"

echo.
echo [INFO] AEGIS is running in the "AEGIS Server" window.
echo [INFO] Close the "AEGIS Server" window to stop AEGIS.
echo.
pause
