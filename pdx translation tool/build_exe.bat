@echo off
REM Build script for PDX Mod Translator
REM This script builds the application into a standalone .exe file

echo ========================================
echo PDX Mod Translator - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Step 1: Installing build dependencies...
pip install pyinstaller

echo.
echo Step 2: Building executable...
pyinstaller build_exe.spec --clean

if errorlevel 1 (
    echo.
    echo Error: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The executable file is located at:
echo dist\PDX_Mod_Translator.exe
echo.
pause
