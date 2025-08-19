import os
import logging
import asyncio
import tempfile
import subprocess
from utils.helpers import clean_filename

logger = logging.getLogger(__name__)

class SimpleYouTubeDownloader:
    def __init__(self):
        """Simple YouTube downloader using yt-dlp"""
        self.temp_dir = tempfile.gettempdir()
        
        # Quality settings for yt-dlp
        self.quality_settings = {
            'high': 'bestaudio[ext=m4a]/best[ext=mp4]/best',
            'medium': 'worstaudio[abr>=128]/worst[ext=mp4]/worst',
            'low': 'worstaudio/worst'
        }

    async def search_and_download_with_deezer(self, track_name, artist_name, quality='medium'):
        """Use Deezer API for ultra-fast accurate search, then download from YouTube"""
        try:
            from .deezer_handler import DeezerHandler
            
            # Step 1: Lightning-fast Deezer search for exact track info
            logger.info(f"🎵 Using Deezer for ultra-fast search: {track_name} by {artist_name}")
            deezer = DeezerHandler()
            
            deezer_result = await deezer.search_track(track_name, artist_name)
            
            if deezer_result:
                # Use Deezer's exact metadata for precise YouTube search
                exact_title = deezer_result['title']
                exact_artist = deezer_result['artist']
                
                logger.info(f"✅ Deezer found exact match: '{exact_title}' by '{exact_artist}'")
                
                # Step 2: Search YouTube with Deezer's exact metadata
                precise_queries = [
                    f'"{exact_title}" "{exact_artist}" official audio',
                    f'"{exact_title}" "{exact_artist}" official',
                    f'"{exact_title}" by "{exact_artist}"',
                    f"{exact_artist} - {exact_title}",
                    f"{exact_title} {exact_artist} official"
                ]
                
                for query in precise_queries:
                    video_url = await self._search_youtube(query)
                    if video_url:
                        logger.info(f"🚀 Found with Deezer-enhanced search: {query[:50]}...")
                        audio_file = await self._download_audio(video_url, exact_title, exact_artist, quality)
                        return audio_file
            
            # Fallback to original method if Deezer fails
            return await self.search_and_download(track_name, artist_name, quality)
            
        except Exception as e:
            logger.error(f"Deezer-enhanced search error: {e}")
            # Fallback to original method
            return await self.search_and_download(track_name, artist_name, quality)

    async def search_and_download(self, track_name, artist_name, quality='medium'):
        """Search YouTube and download exact match - improved accuracy"""
        try:
            # More precise search queries for exact matches
            search_queries = [
                f'"{track_name}" "{artist_name}" official audio',
                f'"{track_name}" "{artist_name}" official',
                f'"{track_name}" by "{artist_name}"',
                f"{artist_name} - {track_name} official audio",
                f"{artist_name} {track_name} lyrics",
                f"{track_name} {artist_name} music video"
            ]
            
            logger.info(f"🔍 Searching for exact match: {track_name} by {artist_name}")
            
            # Try each search query systematically
            for i, query in enumerate(search_queries):
                video_url = await self._search_youtube(query)
                if video_url:
                    logger.info(f"✅ Found with query #{i+1}: {query[:50]}...")
                    break
                logger.info(f"❌ No results with query #{i+1}")
                
            if not video_url:
                # Final attempt with simpler search
                simple_query = f"{track_name} {artist_name}"
                video_url = await self._search_youtube(simple_query)
                
            if not video_url:
                logger.warning(f"No exact match found for: {track_name} by {artist_name}")
                return None
            
            # Download the audio
            audio_file = await self._download_audio(video_url, track_name, artist_name, quality)
            return audio_file
            
        except Exception as e:
            logger.error(f"Search/download error: {e}")
            return None

    async def _search_youtube(self, query):
        """Search YouTube for the query and return the first video URL - optimized for speed"""
        try:
            # Optimized yt-dlp command for faster search
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--playlist-end', '1',
                '--no-check-certificate',  # Skip SSL checks for speed
                '--socket-timeout', '10',   # 10 second timeout
                '--no-warnings',            # Reduce output noise
                f'ytsearch1:{query}'
            ]
            
            # Set timeout for the entire process
            try:
                process = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    ),
                    timeout=15  # 15 second timeout for search
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=15
                )
                
                if process.returncode == 0 and stdout:
                    import json
                    video_info = json.loads(stdout.decode().strip())
                    video_url = video_info.get('webpage_url') or video_info.get('url')
                    video_title = video_info.get('title', 'Unknown')[:50]  # Truncate long titles
                    logger.info(f"Found: {video_title} - {video_url}")
                    return video_url
                else:
                    logger.warning(f"Search failed for: {query}")
                    return None
                    
            except asyncio.TimeoutError:
                logger.warning(f"Search timeout for: {query}")
                return None
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            return None

    async def _download_audio(self, video_url, track_name, artist_name, quality):
        """Download audio from YouTube video URL - optimized for speed"""
        try:
            # Generate clean filename
            filename = clean_filename(f"{artist_name} - {track_name}")
            output_path = os.path.join(self.temp_dir, f"{filename}.%(ext)s")
            
            # Quality settings for faster downloads
            quality_settings = {
                'high': ['--audio-quality', '320K'],
                'medium': ['--audio-quality', '192K'], 
                'low': ['--audio-quality', '128K']
            }
            
            # Optimized yt-dlp command for faster downloads
            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--no-playlist',
                '--no-check-certificate',      # Skip SSL checks
                '--socket-timeout', '15',       # 15 second socket timeout
                '--retries', '2',               # Only 2 retries
                '--fragment-retries', '2',      # 2 fragment retries
                '--no-warnings',                # Reduce output
                '--output', output_path,
                video_url
            ] + quality_settings.get(quality, ['--audio-quality', '192K'])
            
            logger.info(f"⬇️ Downloading audio from YouTube...")
            # User sees: "📤 Uploading your song..." during this process
            
            # Execute with timeout
            try:
                process = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    ),
                    timeout=5
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=45  # 45 second download timeout
                )
                
                if process.returncode == 0:
                    # Find the downloaded file quickly
                    expected_file = output_path.replace('.%(ext)s', '.mp3')
                    if os.path.exists(expected_file):
                        file_size = os.path.getsize(expected_file)
                        logger.info(f"Downloaded: {filename}.mp3 ({file_size // 1024}KB)")
                        return expected_file
                    else:
                        # Quick scan for the file
                        for file in os.listdir(self.temp_dir):
                            if filename[:20] in file and file.endswith('.mp3'):
                                full_path = os.path.join(self.temp_dir, file)
                                logger.info(f"Found: {file}")
                                return full_path
                        
                    logger.error(f"File not found after download")
                    return None
                else:
                    error_msg = stderr.decode()[:100] if stderr else "Unknown error"
                    logger.error(f"Download failed: {error_msg}")
                    return None
                    
            except asyncio.TimeoutError:
                logger.error(f"Download timeout for: {filename}")
                return None
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None

    async def download_track(self, track_metadata, quality='medium'):
        """Main method to download a track (compatible with existing interface)"""
        try:
            track_name = track_metadata.get('name', 'Unknown Track')
            artists = track_metadata.get('artists', 'Unknown Artist')
            
            # Clean up artist names (remove extra info)
            artist_name = artists.split(',')[0].strip()  # Use first artist only
            
            logger.info(f"Starting download: {track_name} by {artist_name}")
        # This will show as "🎵 Please wait, your music is being processed..." in Telegram
            
            audio_file = await self.search_and_download(track_name, artist_name, quality)
            
            if audio_file and os.path.exists(audio_file):
                return audio_file
            else:
                logger.error(f"Failed to download: {track_name} by {artist_name}")
                return None
                
        except Exception as e:
            logger.error(f"Track download error: {e}")
            return None