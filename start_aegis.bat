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

:: 3. Launch AEGIS server (it now starts instantly; models load in background)
echo [INFO] Starting AEGIS server...
echo [INFO] The server will bind in ~2s. ML models load in background (30-60s).
echo [INFO] Browser opens automatically once everything is ready.
echo ======================================================================
echo.

start "AEGIS Server" cmd /k "cd /d "%~dp0" && python -m uvicorn api:app --host 127.0.0.1 --port 8000"

:: 4. Wait for server to bind (quick TCP check)
echo [INFO] Waiting for server to come online...
:WAIT_BIND
timeout /t 2 /nobreak >nul
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" >nul 2>&1
if errorlevel 1 (
    <nul set /p "=."
    goto WAIT_BIND
)
echo.
echo [OK]  Server is up. Waiting for ML models to finish loading in background...

:: 5. Poll /health until {"status":"ready"} (all 12+12 models loaded)
:WAIT_MODELS
timeout /t 3 /nobreak >nul
python -c "import urllib.request,json; r=json.loads(urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=3).read()); exit(0 if r.get('status')=='ready' else 1)" >nul 2>&1
if errorlevel 1 (
    <nul set /p "=."
    goto WAIT_MODELS
)

:: 6. Open browser — models are ready
echo.
echo [SUCCESS] AEGIS is fully loaded! Opening browser...
start "" "http://localhost:8000"

echo.
echo [INFO] AEGIS is running in the "AEGIS Server" window.
echo [INFO] Close the "AEGIS Server" window to stop AEGIS.
echo.
pause
