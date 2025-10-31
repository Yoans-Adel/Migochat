@echo off@echo off

REM Simple Ngrok Starterecho ========================================

REM Run from project root: ngrok\start.batecho Starting ngrok tunnel

echo ========================================

echo ========================================echo.

echo Starting Ngrok Tunnel

echo ========================================cd /d "%~dp0"

echo.

REM Get auth token from .env

REM Run Python scriptfor /f "tokens=1,2 delims==" %%a in ('type ..\.env ^| findstr "NGROK_AUTH_TOKEN"') do set TOKEN=%%b

python ngrok\start.py

if "%TOKEN%"=="" (

pause    echo ERROR: NGROK_AUTH_TOKEN not found in .env

    pause
    exit /b 1
)

echo Configuring auth token...
ngrok.exe config add-authtoken %TOKEN% >nul 2>&1

echo Starting tunnel on port 8000...
echo Check http://127.0.0.1:4040 for your public URL
echo.
echo ========================================
echo.

ngrok.exe http 8000

pause
