import os
import tempfile
from typing import Optional
from models import FingerprintMatch, Track
from config import config
from logger import setup_logging

logger = setup_logging().getChild(__name__)

class FingerprintService:
    """Service for audio fingerprinting and verification"""
    
    def __init__(self, acoustid_api_key: Optional[str] = None):
        self.acoustid_api_key = acoustid_api_key
        self.enabled = config.enable_fingerprinting and bool(acoustid_api_key)
        
        if self.enabled:
            try:
                import acoustid
                import chromaprint
                self.acoustid = acoustid
                self.chromaprint = chromaprint
                logger.info("Audio fingerprinting enabled")
            except ImportError:
                logger.warning("Fingerprinting libraries not available. Install with: pip install acoustid chromaprint")
                self.enabled = False
        else:
            logger.info("Audio fingerprinting disabled")
    
    def identify_track(self, audio_path: str) -> Optional[FingerprintMatch]:
        """Identify track using audio fingerprinting"""
        if not self.enabled:
            return None
        
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None
        
        try:
            logger.debug(f"Fingerprinting: {os.path.basename(audio_path)}")
            
            # Generate fingerprint
            fingerprint, duration = self._generate_fingerprint(audio_path)
            if not fingerprint:
                return None
            
            # Query AcoustID
            results = self.acoustid.match(
                self.acoustid_api_key,
                fingerprint,
                duration,
                meta='recordings+releasegroups+compress'
            )
            
            # Process results
            best_match = self._process_results(results)
            
            if best_match:
                logger.debug(f"Identified: {best_match.artist} - {best_match.title} (confidence: {best_match.confidence:.2f})")
            else:
                logger.debug("No fingerprint match found")
            
            return best_match
            
        except Exception as e:
            logger.error(f"Fingerprint identification failed: {e}")
            return None
    
    def verify_download(self, audio_path: str, expected_track: Track) -> bool:
        """Verify that downloaded file matches expected track"""
        if not config.fingerprint_verification or not self.enabled:
            return True  # Skip verification if disabled
        
        logger.debug(f"Verifying: {os.path.basename(audio_path)}")
        
        match = self.identify_track(audio_path)
        if not match:
            logger.warning(f"Could not identify downloaded file: {os.path.basename(audio_path)}")
            return False  # Conservative approach - reject if we can't identify
        
        # Check if the match corresponds to expected track
        is_match = match.matches_track(expected_track, threshold=0.7)
        
        if is_match:
            logger.debug(f"Verification passed: {match.artist} - {match.title}")
        else:
            logger.warning(f"Verification failed: Expected '{expected_track}', got '{match.artist} - {match.title}'")
        
        return is_match
    
    def _generate_fingerprint(self, audio_path: str) -> tuple[Optional[str], int]:
        """Generate chromaprint fingerprint from audio file"""
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            
            # Take sample from middle of track (most distinctive)
            sample_duration_ms = config.fingerprint_sample_duration * 1000
            if len(audio) > sample_duration_ms:
                start_time = (len(audio) - sample_duration_ms) // 2
                audio = audio[start_time:start_time + sample_duration_ms]
            
            # Convert to format suitable for chromaprint
            audio = audio.set_channels(1).set_frame_rate(11025)
            
            # Export to temporary raw file
            with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as temp_file:
                temp_path = temp_file.name
                audio.export(temp_path, format='raw')
            
            try:
                # Generate fingerprint
                with open(temp_path, 'rb') as f:
                    raw_audio = f.read()
                
                fingerprint_raw = self.chromaprint.fingerprint(
                    raw_audio,
                    sample_rate=11025,
                    channels=1
                )
                
                if fingerprint_raw and len(fingerprint_raw) >= 2:
                    fingerprint = fingerprint_raw[1]  # Get the fingerprint data
                    duration = len(audio) // 1000  # Duration in seconds
                    return fingerprint, duration
                else:
                    return None, 0
                
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {e}")
            return None, 0
    
    def _process_results(self, results) -> Optional[FingerprintMatch]:
        """Process AcoustID results and return best match"""
        best_match = None
        best_score = 0
        
        try:
            for score, recording_id, title, artist in results:
                if score > best_score and score > 0.7:  # Minimum confidence threshold
                    best_match = FingerprintMatch(
                        title=title or 'Unknown',
                        artist=artist or 'Unknown',
                        confidence=score,
                        match_source='acoustid',
                        musicbrainz_id=recording_id
                    )
                    best_score = score
        except Exception as e:
            logger.error(f"Error processing fingerprint results: {e}")
        
        return best_match