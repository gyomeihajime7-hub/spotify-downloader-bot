import os
import logging
import requests
import asyncio
import tempfile
import json
from urllib.parse import quote_plus
from utils.helpers import clean_filename
import random

logger = logging.getLogger(__name__)

class RenderFriendlyDownloader:
    def __init__(self):
        """Render-friendly downloader that works on hosting platforms"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.temp_dir = tempfile.gettempdir()

    async def download_track(self, track_metadata, quality='medium'):
        """Download track using render-friendly methods"""
        try:
            track_name = track_metadata['name']
            artist_name = track_metadata['artists']
            
            logger.info(f"🎵 Starting Render-friendly download: {track_name} by {artist_name}")
            
            # Try Internet Archive first (most reliable on hosting platforms)
            audio_file = await self._download_from_internet_archive(track_name, artist_name, quality)
            if audio_file:
                return audio_file
            
            # Try Free Music Archive
            audio_file = await self._download_from_free_music_archive(track_name, artist_name, quality)
            if audio_file:
                return audio_file
            
            # Try Jamendo
            audio_file = await self._download_from_jamendo(track_name, artist_name, quality)
            if audio_file:
                return audio_file
            
            # No more sources available
            logger.error(f"❌ All download sources failed for: {track_name} by {artist_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error in render-friendly download: {e}")
            return None

    async def _download_from_internet_archive(self, track_name, artist_name, quality):
        """Download from Internet Archive - works well on hosting platforms"""
        try:
            search_query = f"{artist_name} {track_name}".replace(" ", "%20")
            
            # Search Internet Archive for audio files
            search_url = f"https://archive.org/advancedsearch.php?q={search_query}%20AND%20mediatype:audio&fl=identifier,title,creator&rows=10&output=json"
            
            logger.info(f"🔍 Searching Internet Archive: {search_query}")
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.session.get(search_url, timeout=10)
            )
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get('response', {}).get('docs', [])
                
                for doc in docs[:3]:  # Try first 3 results
                    identifier = doc.get('identifier')
                    if identifier:
                        # Try to download the audio file
                        download_url = f"https://archive.org/download/{identifier}/{identifier}.mp3"
                        
                        audio_file = await self._download_audio_file(download_url, f"{artist_name} - {track_name}")
                        if audio_file:
                            logger.info(f"✅ Downloaded from Internet Archive: {identifier}")
                            return audio_file
                            
        except Exception as e:
            logger.warning(f"Internet Archive failed: {e}")
        
        return None

    async def _download_from_free_music_archive(self, track_name, artist_name, quality):
        """Download from Free Music Archive"""
        try:
            # FMA API search
            search_query = f"{artist_name} {track_name}".replace(" ", "+")
            
            logger.info(f"🔍 Searching Free Music Archive: {search_query}")
            
            # This is a simplified approach - in reality, you'd need FMA API key
            # For now, we'll use a demo file
            
            return None
            
        except Exception as e:
            logger.warning(f"Free Music Archive failed: {e}")
        
        return None

    async def _download_from_jamendo(self, track_name, artist_name, quality):
        """Download from Jamendo - open music platform"""
        try:
            search_query = f"{artist_name} {track_name}".replace(" ", "+")
            
            logger.info(f"🔍 Searching Jamendo: {search_query}")
            
            # Jamendo API search (simplified)
            # In production, you'd use their proper API
            
            return None
            
        except Exception as e:
            logger.warning(f"Jamendo failed: {e}")
        
        return None

    async def _download_audio_file(self, url, filename):
        """Download audio file from URL"""
        try:
            logger.info(f"⬇️ Downloading audio from: {url}")
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.session.get(url, timeout=30, stream=True)
            )
            
            if response.status_code == 200:
                # Clean filename
                safe_filename = clean_filename(filename)
                if not safe_filename.endswith('.mp3'):
                    safe_filename += '.mp3'
                
                file_path = os.path.join(self.temp_dir, safe_filename)
                
                # Write file
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Check file size
                file_size = os.path.getsize(file_path)
                if file_size > 1000:  # At least 1KB
                    logger.info(f"✅ Downloaded audio file: {file_size} bytes")
                    return file_path
                else:
                    os.remove(file_path)
                    
        except Exception as e:
            logger.error(f"Download failed: {e}")
        
        return None

