@echo off
REM Quick Run Script - Launches the FBR Invoice Checker Bot

echo Starting FBR Invoice Checker Bot...
echo.

cd /d "%~dp0"

python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to run the application
    echo Make sure Python is installed and dependencies are installed
    echo Run install.bat first if you haven't already
    pause
)
