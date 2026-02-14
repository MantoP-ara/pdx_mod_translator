#!/bin/bash
# Build script for PDX Mod Translator
# This script builds the application into a standalone executable

echo "========================================"
echo "PDX Mod Translator - Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

echo "Step 1: Installing build dependencies..."
pip3 install pyinstaller

echo ""
echo "Step 2: Building executable..."
pyinstaller build_exe.spec --clean

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Build failed!"
    exit 1
fi

echo ""
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo ""
echo "The executable file is located at:"
echo "dist/PDX_Mod_Translator"
echo ""
