@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Build Student Roster v1.4.2 - Windows ARM64

echo ================================================
echo Student Roster v1.4.2 - Windows ARM64
echo ================================================
echo.

if not exist ".venv\Scripts\python.exe" (
 echo ERROR: .venv was not found.
 pause
 exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto :fail

python -m pip install --upgrade pyinstaller customtkinter pillow
if errorlevel 1 goto :fail

python -c "import playwright" >nul 2>&1
if errorlevel 1 python -m pip install playwright
if errorlevel 1 goto :fail

python -m playwright install chromium
if errorlevel 1 goto :fail

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Student Roster.spec" del /q "Student Roster.spec"

echo.
echo Building application...
python -m PyInstaller --noconfirm --clean --onedir --windowed ^
 --name "Student Roster" --icon "app_icon.ico" ^
 --add-data "app_icon.png;." --add-data "app_icon.ico;." ^
 --collect-all playwright --collect-all customtkinter roster_gui.py
if errorlevel 1 goto :fail

set "PW_SRC=%LOCALAPPDATA%\ms-playwright"
set "PW_DST=%CD%\dist\Student Roster\ms-playwright"

if not exist "%PW_SRC%" (
 echo ERROR: Playwright browser source folder was not found:
 echo %PW_SRC%
 goto :fail
)

echo.
echo Copying Playwright browser components...
mkdir "%PW_DST%" >nul 2>&1

for /d %%D in ("%PW_SRC%\chromium-*" "%PW_SRC%\chromium_headless_shell-*" "%PW_SRC%\ffmpeg-*" "%PW_SRC%\winldd-*") do (
 if exist "%%~fD" (
  echo   Copying %%~nxD...
  xcopy "%%~fD" "%PW_DST%\%%~nxD\" /E /I /H /Y /Q >nul
  if errorlevel 1 goto :fail
 )
)

echo.
echo Verifying bundled Chromium...
set "CHROME_FOUND="

for /f "delims=" %%F in ('dir /s /b "%PW_DST%\chrome.exe" 2^>nul') do (
 set "CHROME_FOUND=%%F"
 goto :chrome_found
)

:chrome_found
if not defined CHROME_FOUND (
 echo ERROR: chrome.exe was not found anywhere under:
 echo %PW_DST%
 goto :fail
)

echo Chromium verified:
echo !CHROME_FOUND!

if not exist "dist\Student Roster\Student Roster.exe" (
 echo ERROR: Student Roster.exe was not created.
 goto :fail
)

echo.
echo ================================================
echo SUCCESS - Student Roster v1.4.2
echo.
echo Application:
echo %CD%\dist\Student Roster\Student Roster.exe
echo.
echo Bundled Chromium:
echo !CHROME_FOUND!
echo ================================================
pause
exit /b 0

:fail
echo.
echo ================================================
echo BUILD FAILED
echo ================================================
pause
exit /b 1
