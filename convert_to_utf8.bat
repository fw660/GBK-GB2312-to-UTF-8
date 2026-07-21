@echo off
title Encoding Converter
echo ========================================
echo   Batch Encoding Converter
echo   GB2312 to UTF-8 with BOM
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

python -c "import chardet" >nul 2>&1
if errorlevel 1 (
    echo Installing chardet...
    pip install chardet -q
)

echo.
echo Usage:
echo   1. Put this script in project root
echo   2. Double click to run
echo   3. Or drag folder onto this script
echo.

set "TARGET_DIR=%~1"
if "%TARGET_DIR%"=="" (
    set /p TARGET_DIR="Enter directory path (default: current): "
    if "%TARGET_DIR%"=="" set "TARGET_DIR=."
)

echo.
echo Target: %TARGET_DIR%
echo.

set /p CONFIRM="Convert all C/H files? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Cancelled
    pause
    exit /b 0
)

echo.
echo Converting...
echo.

python "%~dp0convert_encoding.py" "%TARGET_DIR%" --backup

echo.
if errorlevel 1 (
    echo Done with some failures
) else (
    echo All files converted successfully!
)

echo.
echo Original files backed up as .bak
echo.
pause
