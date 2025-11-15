@echo off
echo ================================================================
echo Building FBR Invoice Checker EXE File
echo ================================================================
echo.

echo [1/3] Cleaning previous build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist InvoiceChecker.spec del /q InvoiceChecker.spec

echo [2/3] Building executable (this may take 5-10 minutes)...
echo Please wait...
echo.

pyinstaller --name=InvoiceChecker ^
    --onefile ^
    --windowed ^
    --add-data="license_config.json;." ^
    --add-data="version.txt;." ^
    --hidden-import=tkinter ^
    --hidden-import=openpyxl ^
    --hidden-import=selenium ^
    --hidden-import=playwright ^
    --hidden-import=undetected_chromedriver ^
    --hidden-import=requests ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.ImageTk ^
    --collect-all=openpyxl ^
    --noupx ^
    main.py

echo.
echo [3/3] Checking build result...
if exist dist\InvoiceChecker.exe (
    echo.
    echo ================================================================
    echo SUCCESS! EXE file created successfully!
    echo ================================================================
    echo.
    echo Location: %cd%\dist\InvoiceChecker.exe
    echo.
    dir dist\InvoiceChecker.exe
    echo.
    echo You can now distribute the InvoiceChecker.exe file!
    echo Make sure to include:
    echo   - license_config.json
    echo   - version.txt
    echo   - Any other required files
    echo.
) else (
    echo.
    echo ================================================================
    echo ERROR: Build failed!
    echo ================================================================
    echo Please check the error messages above.
)

pause
