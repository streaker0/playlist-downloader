#!/usr/bin/env python3
"""
Spotify Playlist Downloader
Downloads songs from Spotify playlists via YouTube with audio fingerprint verification
"""

import os
import sys
import time
from typing import List
from tqdm import tqdm

from config import config
from logger import setup_logging
from models import Track, DownloadResult, SessionStats, DownloadStatus
from spotify_extractor import SpotifyExtractor
from youtube_downloader import YouTubeDownloader
from fingerprint_service import FingerprintService

logger = setup_logging()

class PlaylistDownloadService:
    """Main service for downloading playlists"""
    
    def __init__(self):
        self.stats = SessionStats()
        
        # Validate configuration
        if not config.validate():
            missing = config.get_missing_requirements()
            logger.error(f"Missing required configuration: {', '.join(missing)}")
            logger.error("Please set the following environment variables:")
            for item in missing:
                logger.error(f"  export {item}='your_value_here'")
            sys.exit(1)
        
        # Initialize services
        try:
            self.spotify = SpotifyExtractor(
                config.spotify_client_id,
                config.spotify_client_secret
            )
            
            self.downloader = YouTubeDownloader(config.download_folder)
            
            self.fingerprint_service = FingerprintService(config.acoustid_api_key)
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            sys.exit(1)
    
    def run(self):
        """Main entry point for the download service"""
        logger.info("=== Spotify Playlist Downloader ===")
        
        try:
            # Read playlist URLs
            playlist_urls = self._read_playlist_urls()
            if not playlist_urls:
                logger.error("No playlist URLs found")
                return
            
            # Extract tracks from playlists
            logger.info("Extracting tracks from playlists...")
            playlists, tracks = self.spotify.extract_multiple_playlists(playlist_urls)
            
            if not tracks:
                logger.error("No tracks found in playlists")
                return
            
            self.stats.total_tracks = len(tracks)
            logger.info(f"Found {len(tracks)} unique tracks across {len(playlists)} playlists")
            
            # Log playlist summary
            for playlist in playlists:
                logger.info(f"  - {playlist}")
            
            # Download tracks
            self._download_tracks(tracks)
            
            # Generate final report
            self._generate_final_report()
            
        except KeyboardInterrupt:
            logger.info("Download interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            logger.info("Session completed")
    
    def _read_playlist_urls(self) -> List[str]:
        """Read playlist URLs from file"""
        if not os.path.exists(config.playlists_file):
            logger.error(f"Playlists file not found: {config.playlists_file}")
            logger.info("Please create a 'playlists.txt' file with one Spotify playlist URL per line")
            return []
        
        try:
            with open(config.playlists_file, 'r', encoding='utf-8') as f:
                urls = []
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):  # Allow comments
                        if 'spotify.com/playlist/' in line:
                            urls.append(line)
                        else:
                            logger.warning(f"Invalid URL on line {line_num}: {line}")
                
                logger.info(f"Loaded {len(urls)} playlist URLs")
                return urls
                
        except Exception as e:
            logger.error(f"Failed to read playlists file: {e}")
            return []
    
    def _download_tracks(self, tracks: List[Track]):
        """Download all tracks with progress tracking"""
        logger.info(f"Starting download of {len(tracks)} tracks...")
        
        start_time = time.time()
        failed_tracks = []
        
        # Create progress bar
        with tqdm(total=len(tracks), desc="Downloading", unit="track") as pbar:
            for i, track in enumerate(tracks, 1):
                try:
                    # Update progress bar description
                    pbar.set_description(f"Downloading: {track.artist[:20]}...")
                    
                    # Download track
                    result = self.downloader.download_track(track)
                    
                    # Update statistics
                    if result.is_success:
                        self.stats.successful_downloads += 1
                        
                        # Verify download if enabled
                        if result.file_path and config.fingerprint_verification:
                            if self.fingerprint_service.verify_download(result.file_path, track):
                                self.stats.verified_downloads += 1
                                result.status = DownloadStatus.VERIFIED
                            else:
                                self.stats.verification_failures += 1
                                result.status = DownloadStatus.VERIFICATION_FAILED
                                # Optionally remove failed verification files
                                # os.remove(result.file_path)
                    else:
                        self.stats.failed_downloads += 1
                        failed_tracks.append(track)
                    
                    # Rate limiting
                    if config.download_delay > 0:
                        time.sleep(config.download_delay)
                    
                    # Update progress
                    pbar.update(1)
                    pbar.set_postfix({
                        'Success': self.stats.successful_downloads,
                        'Failed': self.stats.failed_downloads,
                        'Rate': f"{self.stats.success_rate:.1f}%"
                    })
                    
                except Exception as e:
                    logger.error(f"Unexpected error downloading {track}: {e}")
                    self.stats.failed_downloads += 1
                    failed_tracks.append(track)
                    pbar.update(1)
        
        self.stats.total_time = time.time() - start_time
        
        # Save failed downloads
        if failed_tracks:
            self._save_failed_downloads(failed_tracks)
    
    def _save_failed_downloads(self, failed_tracks: List[Track]):
        """Save failed downloads to file for retry"""
        failed_file = os.path.join(config.download_folder, 'failed_downloads.txt')
        
        try:
            with open(failed_file, 'w', encoding='utf-8') as f:
                f.write("# Failed Downloads - You can manually search for these\n")
                f.write("# Format: Artist - Title (Playlist)\n\n")
                
                for track in failed_tracks:
                    f.write(f"{track.artist} - {track.title}")
                    if track.playlist_name:
                        f.write(f" (from {track.playlist_name})")
                    f.write("\n")
            
            logger.info(f"Failed downloads saved to: {failed_file}")
            
        except Exception as e:
            logger.error(f"Failed to save failed downloads list: {e}")
    
    def _generate_final_report(self):
        """Generate and display final download report"""
        logger.info("\n" + "="*50)
        logger.info("DOWNLOAD COMPLETE")
        logger.info("="*50)
        
        # Print statistics
        print(self.stats.summary())
        
        # Additional insights
        if self.stats.total_tracks > 0:
            avg_time_per_track = self.stats.total_time / self.stats.total_tracks
            logger.info(f"Average time per track: {avg_time_per_track:.1f}s")
        
        if self.stats.verification_failures > 0:
            logger.warning(f"⚠️  {self.stats.verification_failures} downloads failed verification")
            logger.info("These files may be incorrect versions or covers")
        
        # Show download location
        logger.info(f"Downloads saved to: {os.path.abspath(config.download_folder)}")
        
        # Recommendations
        if self.stats.success_rate < 70:
            logger.warning("Low success rate detected. Consider:")
            logger.info("  - Checking your internet connection")
            logger.info("  - Verifying playlist URLs are public")
            logger.info("  - Running again later (YouTube availability varies)")

def main():
    """Main entry point"""
    try:
        service = PlaylistDownloadService()
        service.run()
    except KeyboardInterrupt:
        print("\nDownload cancelled by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()