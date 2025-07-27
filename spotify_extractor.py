import re
import time
from typing import List, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from models import Track, PlaylistInfo
from logger import setup_logging

logger = setup_logging().getChild(__name__)

class SpotifyExtractor:
    """Extracts tracks from Spotify playlists"""
    
    def __init__(self, client_id: str, client_secret: str):
        try:
            self.sp = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
            )
            # Test the connection
            self.sp.user('spotify')
            logger.info("Spotify API connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Spotify API: {e}")
            raise
    
    def extract_playlist(self, url: str) -> tuple[PlaylistInfo, List[Track]]:
        """Extract tracks from Spotify playlist URL"""
        playlist_id = self._extract_playlist_id(url)
        if not playlist_id:
            raise ValueError(f"Invalid Spotify playlist URL: {url}")
        
        try:
            # Get playlist info
            playlist_info = self.sp.playlist(playlist_id, fields="name,tracks.total")
            playlist = PlaylistInfo(
                name=playlist_info['name'],
                url=url,
                platform='spotify',
                track_count=playlist_info['tracks']['total']
            )
            
            logger.info(f"Extracting playlist: {playlist.name} ({playlist.track_count} tracks)")
            
            # Extract tracks
            tracks = []
            results = self.sp.playlist_tracks(playlist_id)
            
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['type'] == 'track':
                        track = self._parse_track(item['track'], playlist.name)
                        if track:
                            tracks.append(track)
                
                # Get next page
                results = self.sp.next(results) if results['next'] else None
                
                # Rate limiting
                time.sleep(0.1)
            
            logger.info(f"Extracted {len(tracks)} valid tracks from {playlist.name}")
            return playlist, tracks
            
        except Exception as e:
            logger.error(f"Failed to extract playlist {url}: {e}")
            raise
    
    def extract_multiple_playlists(self, urls: List[str]) -> tuple[List[PlaylistInfo], List[Track]]:
        """Extract tracks from multiple Spotify playlists"""
        all_playlists = []
        all_tracks = []
        
        for i, url in enumerate(urls, 1):
            try:
                logger.info(f"Processing playlist {i}/{len(urls)}")
                playlist_info, tracks = self.extract_playlist(url)
                all_playlists.append(playlist_info)
                all_tracks.extend(tracks)
                
                # Rate limiting between playlists
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to process playlist {url}: {e}")
                continue
        
        # Remove duplicates based on spotify_id
        unique_tracks = []
        seen_ids = set()
        
        for track in all_tracks:
            if track.spotify_id not in seen_ids:
                unique_tracks.append(track)
                seen_ids.add(track.spotify_id)
        
        logger.info(f"Extracted {len(unique_tracks)} unique tracks from {len(all_playlists)} playlists")
        return all_playlists, unique_tracks
    
    def _extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from Spotify URL"""
        patterns = [
            r'playlist/([a-zA-Z0-9]+)',
            r'playlist:([a-zA-Z0-9]+)',
            r'open\.spotify\.com/playlist/([a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_track(self, track_data: dict, playlist_name: str) -> Optional[Track]:
        """Parse Spotify track data into Track object"""
        try:
            # Skip if track is None or unavailable
            if not track_data or not track_data.get('available_markets'):
                return None
            
            # Get artists
            artists = [artist['name'] for artist in track_data.get('artists', [])]
            if not artists:
                return None
            
            artist_str = ', '.join(artists)
            
            # Create track object
            track = Track(
                title=track_data['name'],
                artist=artist_str,
                album=track_data.get('album', {}).get('name', ''),
                duration_ms=track_data.get('duration_ms', 0),
                isrc=track_data.get('external_ids', {}).get('isrc', ''),
                spotify_id=track_data['id'],
                playlist_name=playlist_name
            )
            
            return track
            
        except Exception as e:
            logger.warning(f"Failed to parse track: {e}")
            return None
    
    def search_track(self, query: str, limit: int = 10) -> List[Track]:
        """Search for tracks on Spotify"""
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for item in results['tracks']['items']:
                track = self._parse_track(item, '')
                if track:
                    tracks.append(track)
            
            return tracks
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []