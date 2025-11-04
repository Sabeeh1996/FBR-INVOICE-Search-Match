@echo off
REM FBR Invoice Checker Bot - Installation Script for Windows
REM This script automates the installation process

echo ========================================
echo FBR Invoice Checker Bot - Setup
echo ========================================
echo.

REM Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python found

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYVER=%%i
echo    Version: %PYVER%
echo.

REM Upgrade pip
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip
echo ✓ pip upgraded
echo.

REM Install dependencies
echo [3/5] Installing required packages...
echo    - selenium
echo    - webdriver-manager
echo    - openpyxl
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ All packages installed
echo.

REM Create logs directory
echo [4/5] Creating logs directory...
if not exist "logs" mkdir logs
echo ✓ Logs directory created
echo.

REM Create sample Excel file
echo [5/5] Creating sample Excel file...
python create_sample_excel.py
echo.

REM Check if Chrome is installed
echo ========================================
echo Checking Chrome browser...
echo ========================================
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Chrome browser not detected
    echo Please install Google Chrome from https://www.google.com/chrome/
    echo.
) else (
    echo ✓ Chrome browser found
    echo.
)

echo ========================================
echo Installation Complete! 🎉
echo ========================================
echo.
echo Next steps:
echo 1. Read QUICKSTART.md for configuration guide
echo 2. Update FBR selectors in fbr_checker.py (IMPORTANT!)
echo 3. Run: python main.py
echo.
echo Press any key to start the application now...
pause >nul

python main.py
