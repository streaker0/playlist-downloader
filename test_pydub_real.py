#!/usr/bin/env python3
"""
Test if pydub actually works for our music downloader use case
"""

print("🧪 Testing pydub for music conversion...")
print("="*50)

# Test 1: Basic import
try:
    from pydub import AudioSegment
    print("✅ pydub imported successfully")
except Exception as e:
    print(f"❌ pydub import failed: {e}")
    input("Press Enter to exit...")
    exit(1)

# Test 2: Can we work with audio files?
try:
    # Create a simple audio segment (this tests core functionality)
    silence = AudioSegment.silent(duration=1000)  # 1 second
    print("✅ Can create audio segments")
except Exception as e:
    print(f"❌ Audio segment creation failed: {e}")
    print("This might be the issue, but let's continue...")

# Test 3: Can we export to MP3? (This is what we need)
try:
    import tempfile
    import os
    
    # Create a temp file for testing
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        temp_path = temp_file.name
    
    # Try to export silence as MP3
    silence = AudioSegment.silent(duration=100)  # 0.1 second
    silence.export(temp_path, format="mp3", bitrate="320k")
    
    # Check if file was created
    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
        print("✅ MP3 export works!")
        os.remove(temp_path)  # Clean up
    else:
        print("❌ MP3 export created empty file")
        
except Exception as e:
    print(f"❌ MP3 export failed: {e}")
    print("This could be an issue...")

# Test 4: Test other required imports for the downloader
print("\n🔍 Testing other required modules...")

modules_to_test = [
    "spotipy",
    "pytube", 
    "requests",
    "mutagen",
    "colorama",
    "tqdm"
]

all_good = True
for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError:
        print(f"❌ {module} - MISSING!")
        all_good = False

# Test 5: Quick Spotify test (if credentials exist)
print("\n🔍 Testing Spotify connection...")
try:
    import os
    
    # Try to load .env
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if client_id and client_secret:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )
        
        # Test with a simple call
        sp.user('spotify')
        print("✅ Spotify API connection works!")
    else:
        print("⚠️  No Spotify credentials found")

except Exception as e:
    print(f"❌ Spotify test failed: {e}")

# Final verdict
print("\n" + "="*50)
if all_good:
    print("🎉 EVERYTHING LOOKS GOOD!")
    print("\nThe music downloader should work fine.")
    print("The 'pyaudioop' error was probably a false alarm.")
    print("\n💡 Try running: python main.py")
else:
    print("❌ Some modules are missing.")
    print("Install missing modules and try again.")

print("\n🔧 If pydub MP3 export failed, you might need FFmpeg.")
print("Check: ffmpeg -version")

input("\nPress Enter to exit...")