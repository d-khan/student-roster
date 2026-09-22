@echo off
setlocal

cd /d "%~dp0"

echo ==================================================
echo Student Roster 1.4.2 - Windows x64 Build
echo Intel / AMD 64-bit
echo Playwright 1.63.0
echo ==================================================
echo.

REM --------------------------------------------------
REM Activate virtual environment
REM --------------------------------------------------

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

REM --------------------------------------------------
REM Locate Playwright browsers
REM --------------------------------------------------

set "PW_BROWSERS=%LOCALAPPDATA%\ms-playwright"

if not exist "%PW_BROWSERS%\chromium-1243" (
    echo ERROR: Chromium 1243 was not found.
    echo Expected:
    echo %PW_BROWSERS%\chromium-1243
    pause
    exit /b 1
)

echo Chromium found.
echo.

REM --------------------------------------------------
REM Clean previous build
REM --------------------------------------------------

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM --------------------------------------------------
REM Build Student Roster
REM --------------------------------------------------

python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --onedir ^
    --name "Student Roster" ^
    --icon "app_icon.ico" ^
    --add-data "app_icon.png;." ^
    --add-data "%PW_BROWSERS%;ms-playwright" ^
    --collect-all customtkinter ^
    --collect-all playwright ^
    roster_gui.py

if errorlevel 1 (
    echo.
    echo ==================================================
    echo BUILD FAILED
    echo ==================================================
    pause
    exit /b 1
)

echo.
echo ==================================================
echo SUCCESS - Student Roster v1.4.2
echo ==================================================
echo.
echo Application:
echo dist\Student Roster\Student Roster.exe
echo.
pause