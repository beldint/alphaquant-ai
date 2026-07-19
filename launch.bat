@echo off
echo ============================================================
echo   AlphaQuant AI - Stock Analysis Platform
echo   Windows Launcher
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.11+
    echo Download from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Run launcher
python launch.py
pause

