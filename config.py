import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load .env file at module import
load_env_file()

@dataclass
class Config:
    """Configuration settings for the playlist downloader"""
    
    # Spotify API credentials (required)
    spotify_client_id: str = os.getenv('SPOTIFY_CLIENT_ID', '')
    spotify_client_secret: str = os.getenv('SPOTIFY_CLIENT_SECRET', '')
    
    # AcoustID API key (optional, for audio fingerprinting)
    acoustid_api_key: str = os.getenv('ACOUSTID_API_KEY', '')
    
    # Download settings
    audio_quality: str = "320k"  # MP3 bitrate
    max_duration: int = 600  # Maximum song duration in seconds (10 minutes)
    min_duration: int = 30   # Minimum song duration in seconds
    
    # Search settings
    max_search_results: int = 5  # How many YouTube results to check per song
    similarity_threshold: float = 0.7  # Minimum similarity for accepting a match
    
    # Rate limiting (seconds between downloads)
    download_delay: float = 2.0
    api_delay: float = 0.5
    
    # File paths
    playlists_file: str = "playlists.txt"
    download_folder: str = "downloads"
    logs_folder: str = "logs"
    
    # Audio fingerprinting settings (disabled for Python 3.13 compatibility)
    enable_fingerprinting: bool = False
    fingerprint_verification: bool = False
    fingerprint_sample_duration: int = 30  # Seconds to analyze
    
    def validate(self) -> bool:
        """Validate that required settings are present"""
        if not self.spotify_client_id or not self.spotify_client_secret:
            return False
        return True
    
    def get_missing_requirements(self) -> list:
        """Get list of missing required settings"""
        missing = []
        if not self.spotify_client_id:
            missing.append("SPOTIFY_CLIENT_ID")
        if not self.spotify_client_secret:
            missing.append("SPOTIFY_CLIENT_SECRET")
        return missing

# Global config instance
config = Config()

# Debug: Print what we loaded
if __name__ == "__main__":
    print("Debug - Environment variables loaded:")
    print(f"SPOTIFY_CLIENT_ID: {'*' * len(config.spotify_client_id) if config.spotify_client_id else 'NOT SET'}")
    print(f"SPOTIFY_CLIENT_SECRET: {'*' * len(config.spotify_client_secret) if config.spotify_client_secret else 'NOT SET'}")
    print(f"ACOUSTID_API_KEY: {'*' * len(config.acoustid_api_key) if config.acoustid_api_key else 'NOT SET'}")
    print(f"Config validation: {config.validate()}")