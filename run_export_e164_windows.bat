@echo off
setlocal

REM ==== CONFIG ====
set PYTHON_MIN_VERSION=3.8
set PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe
set PYTHON_INSTALLER=python-installer.exe
set SCRIPT_DIR=%~dp0
set SCRIPT=%SCRIPT_DIR%export_e164.py
REM ===============

echo Checking for Python...

REM Try python
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    goto :run_script
)

REM Try py launcher
py -3 --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    set USE_PY_LAUNCHER=1
    goto :run_script
)

echo Python not found. Downloading installer...
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_INSTALLER_URL%' -OutFile '%SCRIPT_DIR%%PYTHON_INSTALLER%'"

if NOT EXIST "%SCRIPT_DIR%%PYTHON_INSTALLER%" (
    echo Failed to download Python installer.
    pause
    exit /b 1
)

echo Installing Python silently (this may take a few minutes)...
"%SCRIPT_DIR%%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo Re-checking Python...
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    goto :run_script
)

py -3 --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    set USE_PY_LAUNCHER=1
    goto :run_script
)

echo Python installation seems to have failed. Please install Python manually from https://www.python.org/downloads/
pause
exit /b 1

:run_script
echo Running export_e164.py...
if defined USE_PY_LAUNCHER (
    py -3 "%SCRIPT%" %*
) else (
    python "%SCRIPT%" %*
)

endlocal