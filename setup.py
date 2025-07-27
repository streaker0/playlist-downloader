#!/usr/bin/env python3
"""
Core setup functions for Spotify Playlist Downloader
Used by platform-specific setup scripts
"""

import os
from pathlib import Path

def setup_credentials():
    """Help user set up API credentials"""
    print("\n🔑 Setting up API credentials...")
    
    env_file = Path('.env')
    env_content = []
    
    # Spotify credentials
    print("\n--- Spotify API Setup ---")
    print("1. Go to https://developer.spotify.com/dashboard/")
    print("2. Log in with your Spotify account")
    print("3. Click 'Create App'")
    print("4. Fill in app name and description (anything is fine)")
    print("5. Copy your Client ID and Client Secret")
    
    spotify_client_id = input("\nEnter your Spotify Client ID: ").strip()
    spotify_client_secret = input("Enter your Spotify Client Secret: ").strip()
    
    if spotify_client_id and spotify_client_secret:
        env_content.append(f"SPOTIFY_CLIENT_ID={spotify_client_id}")
        env_content.append(f"SPOTIFY_CLIENT_SECRET={spotify_client_secret}")
        print("✅ Spotify credentials saved")
    else:
        print("❌ Spotify credentials are required")
        return False
    
    # AcoustID credentials (optional)
    print("\n--- AcoustID API Setup (Optional) ---")
    print("AcoustID enables audio fingerprinting for better accuracy")
    print("1. Go to https://acoustid.org/new-application")
    print("2. Register for a free API key")
    
    acoustid_key = input("Enter your AcoustID API key (or press Enter to skip): ").strip()
    if acoustid_key:
        env_content.append(f"ACOUSTID_API_KEY={acoustid_key}")
        print("✅ AcoustID key saved")
    else:
        print("⚠️  Skipping AcoustID (fingerprinting disabled)")
    
    # Save to .env file
    try:
        with open(env_file, 'w') as f:
            f.write('\n'.join(env_content) + '\n')
        print(f"✅ Credentials saved to {env_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to save credentials: {e}")
        return False

def create_sample_files():
    """Create sample configuration files"""
    print("\n📁 Creating sample files...")
    
    # Create playlists.txt
    playlists_file = Path('playlists.txt')
    if not playlists_file.exists():
        with open(playlists_file, 'w') as f:
            f.write("# Add your Spotify playlist URLs here, one per line\n")
            f.write("# Example:\n")
            f.write("# https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M\n")
            f.write("# https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd\n")
        print("✅ Created playlists.txt")
    
    # Create downloads directory
    downloads_dir = Path('downloads')
    downloads_dir.mkdir(exist_ok=True)
    print("✅ Created downloads directory")
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    print("✅ Created logs directory")

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def test_setup():
    """Test the setup"""
    print("\n🧪 Testing setup...")
    
    load_env_file()
    
    # Test imports
    try:
        import spotipy
        import pytube
        import pydub
        print("✅ Core packages imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test Spotify connection
    try:
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ Spotify credentials not found")
            return False
        
        from spotipy.oauth2 import SpotifyClientCredentials
        import spotipy
        
        sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )
        # Test with a simple API call
        sp.user('spotify')
        print("✅ Spotify API connection successful")
        
    except Exception as e:
        print(f"❌ Spotify connection failed: {e}")
        return False
    
    print("✅ Setup test completed successfully!")
    return True

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("  🎉 Setup Complete! 🎉")
    print("="*60)
    print("\nHow to use:")
    print("1. Add Spotify playlist URLs to 'playlists.txt'")
    print("2. Run: python main.py (or use run.bat on Windows)")
    print("3. Your music will be downloaded to the 'downloads' folder")
    print("\nFiles created:")
    print("  - playlists.txt    (add your playlist URLs here)")
    print("  - .env            (your API credentials)")
    print("  - downloads/      (music files will go here)")
    print("  - logs/           (session logs)")
    print("\nFor help, check the logs/ folder or run with -v for verbose output")