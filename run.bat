@echo off
title Spotify Playlist Downloader
echo Starting Spotify Playlist Downloader...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if setup has been run
if not exist .env (
    echo No .env file found. Running setup first...
    python setup_windows.py
    if errorlevel 1 (
        echo Setup failed. Please check the errors above.
        pause
        exit /b 1
    )
    echo.
)

REM Check playlists file
if not exist playlists.txt (
    echo playlists.txt not found. Creating sample file...
    echo # Add your Spotify playlist URLs here, one per line > playlists.txt
    echo # Example: >> playlists.txt
    echo # https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M >> playlists.txt
    echo.
    echo Please edit playlists.txt and add your Spotify playlist URLs
    notepad playlists.txt
    echo Press any key when you've added your playlist URLs...
    pause
)

REM Start downloader
echo Starting download process...
python main.py

echo.
echo Download completed! Check the downloads folder.
echo Press any key to exit...
pause