# 🎵 Spotify Playlist Downloader

A powerful Python tool that downloads songs from Spotify playlists by finding them on YouTube and converting them to high-quality MP3 files. Features audio fingerprinting verification for accuracy.

## ✨ Features

- **Batch Playlist Processing**: Download from multiple Spotify playlists at once
- **High-Quality Audio**: Downloads at 320kbps MP3 quality
- **Smart Matching**: Advanced YouTube search algorithms with multiple fallback strategies
- **Audio Fingerprinting**: Optional verification using AcoustID to ensure correct songs
- **Progress Tracking**: Real-time progress bars and detailed logging
- **Resume Support**: Skips already downloaded files
- **Comprehensive Reporting**: Detailed success/failure reports and statistics

## 🚀 Quick Start

### 1. Setup
```bash
# Clone or download all the Python files to a folder
# Run the setup script
python setup.py
```

The setup script will:
- Check system requirements
- Install Python packages
- Help you get API credentials
- Create necessary folders and files

### 2. Get API Credentials

**Spotify API (Required):**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app
3. Copy your Client ID and Client Secret

**AcoustID API (Optional, for fingerprinting):**
1. Go to [AcoustID](https://acoustid.org/new-application)
2. Register for a free API key

### 3. Add Playlists
Edit `playlists.txt` and add your Spotify playlist URLs:
```
https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd
# Add more playlists here
```

### 4. Download
```bash
python main.py
```

Your music will be downloaded to the `downloads/` folder!

## 📁 File Structure

```
spotify-downloader/
├── main.py                 # Main application
├── setup.py               # Setup script
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── models.py             # Data models
├── logger.py             # Logging configuration
├── spotify_extractor.py  # Spotify API handling
├── youtube_downloader.py # YouTube search & download
├── fingerprint_service.py # Audio fingerprinting
├── playlists.txt         # Your playlist URLs (created by setup)
├── .env                  # API credentials (created by setup)
├── downloads/           # Downloaded music files
└── logs/               # Session logs
```

## ⚙️ Configuration

Edit `config.py` to customize settings:

```python
# Audio quality
audio_quality = "320k"  # MP3 bitrate

# Download behavior
max_duration = 600      # Max song length (seconds)
min_duration = 30       # Min song length (seconds)
download_delay = 2.0    # Seconds between downloads

# Matching accuracy
similarity_threshold = 0.7  # How strict the matching should be
max_search_results = 5     # YouTube results to check per song

# Fingerprinting
enable_fingerprinting = True
fingerprint_verification = True
```

## 🔧 System Requirements

### Required Software
- **Python 3.8+**
- **FFmpeg** (for audio processing)
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`

### Optional (for fingerprinting)
- **Chromaprint**
  - macOS: `brew install chromaprint`
  - Ubuntu/Debian: `sudo apt install libchromaprint-tools`
  - Windows: Download from [acoustid.org](https://acoustid.org/chromaprint)

## 📊 How It Works

1. **Playlist Extraction**: Connects to Spotify API and extracts track metadata
2. **Smart Search**: Generates multiple YouTube search queries per track:
   - `"Song Title" "Artist" official audio`
   - `"Song Title" "Artist" lyrics`
   - `Artist Song Title official`
   - Various fallback patterns
3. **Intelligent Matching**: Filters results based on:
   - Duration similarity
   - Title/artist matching
   - Content quality indicators
   - Avoids covers, reactions, tutorials
4. **Download & Convert**: Downloads highest quality audio and converts to 320kbps MP3
5. **Verification** (optional): Uses audio fingerprinting to verify correct song
6. **Report Generation**: Provides detailed success/failure statistics

## 📈 Expected Accuracy

- **Without fingerprinting**: ~75-85% accuracy
- **With fingerprinting**: ~90-95% accuracy
- **Factors affecting accuracy**:
  - Playlist popularity (popular songs = better results)
  - Song availability on YouTube
  - Filename quality from YouTube uploaders

## 🚨 Legal Notice

This tool is for educational purposes and personal use only. Please ensure you:
- Own the music you're downloading or have proper licenses
- Comply with your local copyright laws
- Respect YouTube's Terms of Service
- Use responsibly and don't abuse the APIs

## 🛠️ Troubleshooting

### Common Issues

**"No module named 'spotipy'"**
```bash
pip install -r requirements.txt
```

**"FFmpeg not found"**
- Install FFmpeg (see System Requirements above)
- Make sure it's in your system PATH

**Low success rate**
- Check your internet connection
- Verify playlist URLs are public
- Try running again later (YouTube availability varies)
- Enable fingerprinting for better accuracy

**"Spotify API connection failed"**
- Double-check your Client ID and Client Secret
- Make sure they're correctly set in `.env` file

### Debug Mode
Run with verbose logging to see what's happening:
```bash
python main.py
# Check the logs/ folder for detailed session logs
```

## 🔄 Advanced Usage

### Environment Variables
Set in `.env` file or system environment:
```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
ACOUSTID_API_KEY=your_acoustid_key  # Optional
```

### Batch Processing
Add multiple playlists to `playlists.txt`:
- One URL per line
- Lines starting with `#` are ignored (comments)
- Duplicates across playlists are automatically removed

### Custom Download Location
Modify `config.py`:
```python
download_folder = "/path/to/your/music/folder"
```

## 📝 File Formats

**Output Files**: `Artist - Song Title.mp3`
- **Quality**: 320kbps MP3
- **Metadata**: Title, Artist, Album tags included
- **Naming**: Safe filenames (invalid characters removed)

**Log Files**: `logs/download_session_YYYYMMDD_HHMMSS.log`
- **Content**: Detailed download attempts, errors, statistics
- **Format**: Timestamped entries with log levels

## 🤝 Contributing

Found a bug or want to improve the tool? 
- Check the logs for error details
- Issues commonly arise from YouTube API changes
- Fingerprinting requires additional system libraries

## 📜 License

This project is for educational and personal use. Users are responsible for complying with applicable laws and terms of service.