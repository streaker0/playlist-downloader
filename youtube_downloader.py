import os
import re
import time
import tempfile
import subprocess
import json
from typing import List, Optional, Tuple
from models import Track, DownloadResult, DownloadStatus
from config import config
from logger import setup_logging

logger = setup_logging().getChild(__name__)

class YouTubeDownloader:
    """Handles searching and downloading from YouTube using yt-dlp (more reliable than pytube)"""
    
    def __init__(self, download_path: str):
        self.download_path = download_path
        self.failed_downloads = []
        
        # Create download directory
        os.makedirs(download_path, exist_ok=True)
        logger.info(f"Download directory: {download_path}")
        
        # Check if yt-dlp is available
        self.has_ytdlp = self._check_ytdlp()
        if not self.has_ytdlp:
            logger.error("yt-dlp not found - install with: pip install yt-dlp")
            raise RuntimeError("yt-dlp is required but not installed")
    
    def _check_ytdlp(self) -> bool:
        """Check if yt-dlp is available"""
        try:
            subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def download_track(self, track: Track) -> DownloadResult:
        """Search for track on YouTube and download best match"""
        start_time = time.time()
        
        logger.info(f"Downloading: {track}")
        
        try:
            # Check if file already exists
            expected_path = os.path.join(self.download_path, track.to_filename())
            if os.path.exists(expected_path):
                logger.info(f"File already exists: {track.to_filename()}")
                return DownloadResult(
                    track=track,
                    status=DownloadStatus.SUCCESS,
                    file_path=expected_path,
                    download_time=time.time() - start_time
                )
            
            # Generate search queries
            search_queries = self._generate_search_queries(track)
            
            # Try each query until we find a good match
            for query in search_queries:
                try:
                    video_info = self._search_youtube(query)
                    if video_info:
                        file_path = self._download_video(video_info, track)
                        if file_path:
                            return DownloadResult(
                                track=track,
                                status=DownloadStatus.SUCCESS,
                                file_path=file_path,
                                youtube_url=video_info.get('webpage_url', ''),
                                download_time=time.time() - start_time
                            )
                except Exception as e:
                    logger.warning(f"Search failed for query '{query}': {e}")
                    continue
            
            # If we get here, all searches failed
            self.failed_downloads.append(str(track))
            return DownloadResult(
                track=track,
                status=DownloadStatus.FAILED,
                error_message="No suitable video found",
                download_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Download failed for {track}: {e}")
            self.failed_downloads.append(str(track))
            return DownloadResult(
                track=track,
                status=DownloadStatus.FAILED,
                error_message=str(e),
                download_time=time.time() - start_time
            )
    
    def _generate_search_queries(self, track: Track) -> List[str]:
        """Generate multiple search queries with different strategies"""
        queries = []
        
        # Clean up track info
        clean_title = self._clean_search_text(track.title)
        clean_artist = self._clean_search_text(track.artist)
        
        # Primary searches (most specific)
        queries.extend([
            f'"{clean_title}" "{clean_artist}" official audio',
            f'"{clean_title}" "{clean_artist}" lyrics',
            f'"{clean_title}" "{clean_artist}" official music video',
            f'{clean_artist} {clean_title} official',
        ])
        
        # Fallback searches (less specific)
        queries.extend([
            f'{clean_artist} {clean_title}',
            f'{clean_title} {clean_artist}',
            f'{clean_title} by {clean_artist}',
        ])
        
        return queries[:3]  # Limit to top 3 to avoid rate limiting
    
    def _clean_search_text(self, text: str) -> str:
        """Clean text for better search results"""
        # Remove common problematic patterns
        patterns_to_remove = [
            r'\(feat\..*?\)',
            r'\(ft\..*?\)',
            r'\(featuring.*?\)',
            r'\(remix\)',
            r'\(remaster\)',
            r'\(live\)',
            r'\(acoustic\)',
            r'\[.*?\]',
            r'\(.*?version.*?\)',
        ]
        
        cleaned = text
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up whitespace and special characters
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _search_youtube(self, query: str) -> Optional[dict]:
        """Search YouTube using yt-dlp"""
        try:
            logger.debug(f"Searching: {query}")
            
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--default-search', 'ytsearch5:',  # Search YouTube, get top 5
                '--quiet',
                query
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse results
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video_info = json.loads(line)
                        videos.append(video_info)
                    except json.JSONDecodeError:
                        continue
            
            # Find best match
            for video in videos:
                if self._is_good_match(video):
                    return video
            
            return None
            
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp search failed: {e}")
            return None
    
    def _is_good_match(self, video_info: dict) -> bool:
        """Determine if video is a good match for the track"""
        title = video_info.get('title', '').lower()
        duration = video_info.get('duration', 0)
        
        # Duration checks
        if duration > config.max_duration or duration < config.min_duration:
            return False
        
        # Avoid obviously bad content
        avoid_indicators = [
            'reaction', 'review', 'cover', 'karaoke', 'instrumental',
            'tutorial', 'how to', 'lesson', 'behind the scenes'
        ]
        
        if any(indicator in title for indicator in avoid_indicators):
            return False
        
        # Prefer official content
        official_indicators = [
            'official', 'vevo', 'records', 'music', 'audio only', 'lyrics'
        ]
        
        has_official = any(indicator in title for indicator in official_indicators)
        
        return True  # Accept if it passes basic checks
    
    def _download_video(self, video_info: dict, track: Track) -> Optional[str]:
        """Download video using yt-dlp"""
        try:
            video_url = video_info['webpage_url']
            final_path = os.path.join(self.download_path, track.to_filename())
            
            logger.debug(f"Downloading: {video_info.get('title', 'Unknown')}")
            
            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '320K',
                '--output', final_path.replace('.mp3', '.%(ext)s'),
                '--quiet',
                '--no-warnings',
                video_url
            ]
            
            # Add metadata
            cmd.extend([
                '--add-metadata',
                '--metadata-from-title', '%(artist)s - %(title)s'
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Check if file was created
            if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                logger.info(f"Downloaded: {track.to_filename()}")
                return final_path
            else:
                logger.error(f"Download failed - file not created or empty")
                return None
            
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp download failed: {e}")
            return None
    
    def get_failed_downloads(self) -> List[str]:
        """Get list of tracks that failed to download"""
        return self.failed_downloads.copy()
    
    def clear_failed_downloads(self):
        """Clear the failed downloads list"""
        self.failed_downloads.clear()