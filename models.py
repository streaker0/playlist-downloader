from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    SUCCESS = "success"
    FAILED = "failed"
    VERIFIED = "verified"
    VERIFICATION_FAILED = "verification_failed"

@dataclass
class Track:
    """Represents a music track"""
    title: str
    artist: str
    album: str = ""
    duration_ms: int = 0
    isrc: str = ""
    spotify_id: str = ""
    playlist_name: str = ""
    
    def __str__(self):
        return f"{self.artist} - {self.title}"
    
    def to_filename(self) -> str:
        """Generate a safe filename for this track (Windows-compatible)"""
        import re
        safe_name = f"{self.artist} - {self.title}"
        # Remove invalid filename characters for Windows
        safe_name = re.sub(r'[<>:"/\\|?*]', '', safe_name)
        # Remove trailing periods and spaces (Windows restriction)
        safe_name = safe_name.strip('. ')
        # Limit length for Windows path limitations
        if len(safe_name) > 150:
            safe_name = safe_name[:150]
        return safe_name + ".mp3"

@dataclass
class FingerprintMatch:
    """Represents a fingerprint identification result"""
    title: str
    artist: str
    album: str = ""
    confidence: float = 0.0
    match_source: str = ""  # 'acoustid', 'shazam', 'local'
    musicbrainz_id: str = ""
    
    def matches_track(self, track: Track, threshold: float = 0.7) -> bool:
        """Check if this fingerprint match corresponds to the expected track"""
        title_similarity = self._text_similarity(self.title, track.title)
        artist_similarity = self._text_similarity(self.artist, track.artist)
        
        return title_similarity >= threshold and artist_similarity >= threshold
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

@dataclass
class DownloadResult:
    """Represents the result of a download attempt"""
    track: Track
    status: DownloadStatus
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    fingerprint_match: Optional[FingerprintMatch] = None
    youtube_url: Optional[str] = None
    download_time: float = 0.0
    
    @property
    def is_success(self) -> bool:
        return self.status in [DownloadStatus.SUCCESS, DownloadStatus.VERIFIED]
    
    @property
    def needs_verification(self) -> bool:
        return self.status == DownloadStatus.SUCCESS and self.file_path is not None

@dataclass
class PlaylistInfo:
    """Information about a playlist"""
    name: str
    url: str
    platform: str  # 'spotify', 'tidal', etc.
    track_count: int = 0
    
    def __str__(self):
        return f"{self.name} ({self.track_count} tracks)"

@dataclass
class SessionStats:
    """Statistics for a download session"""
    total_tracks: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    verified_downloads: int = 0
    verification_failures: int = 0
    skipped_tracks: int = 0
    total_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        if self.total_tracks == 0:
            return 0.0
        return (self.successful_downloads / self.total_tracks) * 100
    
    @property
    def verification_rate(self) -> float:
        if self.successful_downloads == 0:
            return 0.0
        return (self.verified_downloads / self.successful_downloads) * 100
    
    def summary(self) -> str:
        return (
            f"Session Summary:\n"
            f"  Total tracks: {self.total_tracks}\n"
            f"  Successful: {self.successful_downloads} ({self.success_rate:.1f}%)\n"
            f"  Failed: {self.failed_downloads}\n"
            f"  Verified: {self.verified_downloads} ({self.verification_rate:.1f}%)\n"
            f"  Total time: {self.total_time:.1f}s"
        )