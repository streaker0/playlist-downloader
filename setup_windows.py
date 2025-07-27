#!/usr/bin/env python3
"""
Windows-specific setup script for Spotify Playlist Downloader
Handles Windows-specific issues and provides better guidance
"""

import os
import sys
import subprocess
import winreg
from pathlib import Path

def print_banner():
    print("="*60)
    print("  🎵 Spotify Playlist Downloader - Windows Setup 🎵")
    print("="*60)

def check_windows_version():
    """Check Windows version and warn about potential issues"""
    try:
        import platform
        version = platform.version()
        release = platform.release()
        print(f"✅ Windows {release} detected")
        
        # Warn about path length issues on older Windows
        if int(release) < 10:
            print("⚠️  Warning: Windows versions older than 10 may have path length issues")
            print("   Consider upgrading or using shorter download paths")
        
        return True
    except Exception as e:
        print(f"❌ Could not detect Windows version: {e}")
        return False

def check_long_path_support():
    """Check if long path support is enabled on Windows 10+"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SYSTEM\CurrentControlSet\Control\FileSystem")
        value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
        winreg.CloseKey(key)
        
        if value == 1:
            print("✅ Long path support is enabled")
        else:
            print("⚠️  Long path support is disabled")
            print("   To enable: Run as Administrator and execute:")
            print("   reg add HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1")
            print("   Then restart your computer")
    except Exception:
        print("⚠️  Could not check long path support")

def check_ffmpeg_windows():
    """Check for FFmpeg on Windows with specific guidance"""
    print("\n📦 Checking FFmpeg installation...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=True)
        print("✅ FFmpeg is installed and working")
        return True
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        print("\n🔧 To install FFmpeg on Windows:")
        print("1. Download from: https://www.gyan.dev/ffmpeg/builds/")
        print("2. Choose 'release builds' -> 'ffmpeg-git-essentials.7z'")
        print("3. Extract to C:\\ffmpeg\\")
        print("4. Add C:\\ffmpeg\\bin to your PATH:")
        print("   - Press Win+R, type 'sysdm.cpl', press Enter")
        print("   - Click 'Environment Variables'")
        print("   - Under 'System Variables', find 'Path', click 'Edit'")
        print("   - Click 'New', add 'C:\\ffmpeg\\bin'")
        print("   - Click OK, restart Command Prompt")
        print("\nAlternatively, use Chocolatey: choco install ffmpeg")
        return False
    except subprocess.CalledProcessError:
        print("❌ FFmpeg found but not working properly")
        return False

def install_python_packages_windows():
    """Install Python packages with Windows-specific handling"""
    print("\n📚 Installing Python packages...")
    
    try:
        # Upgrade pip first (common Windows issue)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        # Install packages
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Python packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Package installation failed")
        print("\n🔧 Windows troubleshooting:")
        print("1. Run Command Prompt as Administrator")
        print("2. Try: python -m pip install --user -r requirements.txt")
        print("3. If you have multiple Python versions, use: py -3.8 -m pip install -r requirements.txt")
        return False

def check_windows_defender():
    """Warn about Windows Defender potentially blocking downloads"""
    print("\n🛡️  Windows Defender Notice:")
    print("Windows Defender may flag downloaded files or slow downloads")
    print("Consider adding your download folder to Defender exclusions:")
    print("1. Open Windows Security")
    print("2. Go to Virus & threat protection")
    print("3. Click 'Manage settings' under Virus & threat protection settings")
    print("4. Click 'Add or remove exclusions'")
    print("5. Add your downloads folder")

def create_windows_batch_files():
    """Create Windows-specific batch files"""
    print("\n📝 Creating Windows batch files...")
    
    # Enhanced run.bat
    run_bat_content = '''@echo off
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
pause'''
    
    with open('run.bat', 'w') as f:
        f.write(run_bat_content)
    
    # Create install.bat for easier setup
    install_bat_content = '''@echo off
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
pause'''
    
    with open('install.bat', 'w') as f:
        f.write(install_bat_content)
    
    print("✅ Created run.bat and install.bat")

def main():
    """Main Windows setup function"""
    print_banner()
    
    if not check_windows_version():
        input("Press Enter to continue anyway...")
    
    check_long_path_support()
    
    if not check_ffmpeg_windows():
        print("\n❌ FFmpeg is required. Please install it and run setup again.")
        input("Press Enter to continue with setup (FFmpeg still needed)...")
    
    if not install_python_packages_windows():
        print("\n❌ Failed to install Python packages. Please resolve the errors above.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Continue with regular setup
    from setup import setup_credentials, create_sample_files, test_setup, print_usage_instructions
    
    if not setup_credentials():
        sys.exit(1)
    
    create_sample_files()
    create_windows_batch_files()
    check_windows_defender()
    
    if not test_setup():
        print("\n❌ Setup test failed. Please check the errors above")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print_usage_instructions()
    print("\n💡 Windows-specific tips:")
    print("  - Use install.bat for easy installation")
    print("  - Use run.bat to start the downloader")
    print("  - Check Windows Defender if downloads are slow")
    print("  - Keep download paths short to avoid path length issues")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()