@echo off
title Spotify Playlist Downloader - Installation
echo Installing Spotify Playlist Downloader...
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Run Windows setup
python setup_windows.py

echo.
echo Setup complete! You can now run the downloader with run.bat
pause