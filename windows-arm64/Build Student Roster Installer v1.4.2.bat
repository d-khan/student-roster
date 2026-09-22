@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Build Student Roster v1.4.2 Installer

echo ==================================================
echo Student Roster v1.4.2 - Build Windows Installer
echo ==================================================
echo.

REM First build the tested application.
call "Build Student Roster ARM64 v1.4.2.bat"
if errorlevel 1 goto :fail

set "APPDIR=%CD%\dist\Student Roster"
set "ISS=%CD%\StudentRosterInstaller.iss"
set "OUTDIR=%CD%\installer"

if not exist "%APPDIR%\Student Roster.exe" (
  echo ERROR: Student Roster.exe was not found.
  goto :fail
)

REM Locate Inno Setup. Prefer v7, then fall back to v6.
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"

if not defined ISCC (
  if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)
if not defined ISCC (
  if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if not defined ISCC (
  echo.
  echo ERROR: Inno Setup 7 or 6 was not found.
  echo Expected ISCC.exe under Program Files.
  echo.
  pause
  exit /b 2
)

echo Found Inno Setup compiler:
echo %ISCC%
echo.

if exist "%OUTDIR%" rmdir /s /q "%OUTDIR%"
mkdir "%OUTDIR%"

echo Building one-click installer...
"%ISCC%" "%ISS%"
if errorlevel 1 goto :fail

if not exist "%OUTDIR%\StudentRoster-Setup-1.4.2.exe" (
  echo ERROR: Installer EXE was not created.
  goto :fail
)

echo.
echo ==================================================
echo SUCCESS
echo.
echo Give ONLY this file to the end user:
echo %OUTDIR%\StudentRoster-Setup-1.4.2.exe
echo ==================================================
pause
exit /b 0

:fail
echo.
echo ==================================================
echo INSTALLER BUILD FAILED
echo ==================================================
pause
exit /b 1
