import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import logging
import re

logger = logging.getLogger(__name__)

class SpotifyHandler:
    def __init__(self):
        """Initialize Spotify client"""
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            logger.warning("Spotify credentials not found. Some features may not work.")
            self.spotify = None
        else:
            try:
                credentials = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.spotify = spotipy.Spotify(client_credentials_manager=credentials)
                logger.info("Spotify client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Spotify client: {e}")
                self.spotify = None

    def extract_spotify_id(self, url):
        """Extract Spotify ID and type from URL"""
        patterns = {
            'track': [
                r'open\.spotify\.com/track/([a-zA-Z0-9]+)',
                r'spotify\.com/track/([a-zA-Z0-9]+)',
                r'spotify:track:([a-zA-Z0-9]+)'
            ],
            'album': [
                r'open\.spotify\.com/album/([a-zA-Z0-9]+)',
                r'spotify\.com/album/([a-zA-Z0-9]+)',
                r'spotify:album:([a-zA-Z0-9]+)'
            ],
            'playlist': [
                r'open\.spotify\.com/playlist/([a-zA-Z0-9]+)',
                r'spotify\.com/playlist/([a-zA-Z0-9]+)',
                r'spotify:playlist:([a-zA-Z0-9]+)'
            ]
        }
        
        for content_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, url)
                if match:
                    return content_type, match.group(1)
        
        return None, None

    async def get_metadata(self, spotify_url):
        """Get metadata from Spotify URL"""
        if not self.spotify:
            logger.error("Spotify client not initialized")
            return None
        
        try:
            content_type, spotify_id = self.extract_spotify_id(spotify_url)
            
            if not content_type or not spotify_id:
                logger.error("Invalid Spotify URL")
                return None
            
            if content_type == 'track':
                return await self.get_track_metadata(spotify_id)
            elif content_type == 'album':
                return await self.get_album_metadata(spotify_id)
            elif content_type == 'playlist':
                return await self.get_playlist_metadata(spotify_id)
            
        except Exception as e:
            logger.error(f"Error getting metadata: {e}")
            return None

    async def get_track_metadata(self, track_id):
        """Get track metadata"""
        try:
            track = self.spotify.track(track_id)
            
            if not track:
                logger.error(f"Track not found: {track_id}")
                return None
            
            metadata = {
                'type': 'track',
                'id': track.get('id', ''),
                'name': track.get('name', 'Unknown'),
                'artists': ', '.join([artist.get('name', 'Unknown') for artist in track.get('artists', [])]),
                'album': track.get('album', {}).get('name', 'Unknown'),
                'duration_ms': track.get('duration_ms', 0),
                'release_date': track.get('album', {}).get('release_date', 'Unknown'),
                'popularity': track.get('popularity', 0),
                'preview_url': track.get('preview_url'),
                'external_urls': track.get('external_urls', {}),
                'album_art_url': self._get_best_image(track.get('album', {}).get('images', []))
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting track metadata: {e}")
            return None

    async def get_album_metadata(self, album_id):
        """Get album metadata"""
        try:
            album = self.spotify.album(album_id)
            
            if not album:
                logger.error(f"Album not found: {album_id}")
                return None
            
            # Get all tracks in the album
            tracks = []
            album_tracks = album.get('tracks', {}).get('items', [])
            for track in album_tracks:
                track_metadata = {
                    'id': track.get('id', ''),
                    'name': track.get('name', 'Unknown'),
                    'artists': ', '.join([artist.get('name', 'Unknown') for artist in track.get('artists', [])]),
                    'duration_ms': track.get('duration_ms', 0),
                    'track_number': track.get('track_number', 0)
                }
                tracks.append(track_metadata)
            
            metadata = {
                'type': 'album',
                'id': album.get('id', ''),
                'name': album.get('name', 'Unknown'),
                'artists': ', '.join([artist.get('name', 'Unknown') for artist in album.get('artists', [])]),
                'total_tracks': album.get('total_tracks', 0),
                'release_date': album.get('release_date', 'Unknown'),
                'genres': album.get('genres', []),
                'popularity': album.get('popularity', 0),
                'external_urls': album.get('external_urls', {}),
                'image_url': album.get('images', [{}])[0].get('url') if album.get('images') else None,
                'tracks': tracks
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting album metadata: {e}")
            return None

    async def get_playlist_metadata(self, playlist_id):
        """Get playlist metadata"""
        try:
            playlist = self.spotify.playlist(playlist_id)
            
            if not playlist:
                logger.error(f"Playlist not found: {playlist_id}")
                return None
            
            # Get all tracks in the playlist
            tracks = []
            playlist_tracks = playlist.get('tracks', {}).get('items', [])
            for item in playlist_tracks:
                track = item.get('track')
                if track and track.get('type') == 'track':
                    track_metadata = {
                        'id': track.get('id', ''),
                        'name': track.get('name', 'Unknown'),
                        'artists': ', '.join([artist.get('name', 'Unknown') for artist in track.get('artists', [])]),
                        'album': track.get('album', {}).get('name', 'Unknown'),
                        'duration_ms': track.get('duration_ms', 0),
                        'popularity': track.get('popularity', 0)
                    }
                    tracks.append(track_metadata)
            
            metadata = {
                'type': 'playlist',
                'id': playlist.get('id', ''),
                'name': playlist.get('name', 'Unknown'),
                'description': playlist.get('description', ''),
                'owner': playlist.get('owner', {}).get('display_name', 'Unknown'),
                'total_tracks': len(tracks),
                'followers': playlist.get('followers', {}).get('total', 0),
                'external_urls': playlist.get('external_urls', {}),
                'image_url': playlist.get('images', [{}])[0].get('url') if playlist.get('images') else None,
                'tracks': tracks
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting playlist metadata: {e}")
            return None

    def search_track(self, query, limit=1):
        """Search for track by query"""
        if not self.spotify:
            return None
        
        try:
            results = self.spotify.search(q=query, type='track', limit=limit)
            if results and results.get('tracks', {}).get('items'):
                return results['tracks']['items'][0]
            return None
        except Exception as e:
            logger.error(f"Error searching track: {e}")
            return None

    def _get_best_image(self, images):
        """Get the best quality image from Spotify images array"""
        if not images:
            return None
        
        # Sort images by size (width * height) and return the largest
        try:
            sorted_images = sorted(images, key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
            return sorted_images[0].get('url') if sorted_images else None
        except Exception:
            # Fallback to first image
            return images[0].get('url') if images else None

    async def get_enhanced_metadata_with_deezer(self, spotify_url):
        """Get metadata from Spotify and enhance with Deezer for ultra-fast accuracy"""
        try:
            # Get basic metadata from Spotify
            spotify_metadata = self.get_track_metadata(spotify_url)
            
            if not spotify_metadata:
                return None
            
            # Enhance with Deezer for better accuracy
            try:
                from .deezer_handler import DeezerHandler
                deezer = DeezerHandler()
                
                deezer_result = await deezer.search_track(
                    spotify_metadata['name'], 
                    spotify_metadata['artists']
                )
                
                if deezer_result:
                    # Use Deezer's high-res album cover if available
                    if deezer_result.get('album_cover') and not spotify_metadata.get('album_art_url'):
                        spotify_metadata['album_art_url'] = deezer_result['album_cover']
                    
                    # Store Deezer metadata for enhanced search
                    spotify_metadata['deezer_enhanced'] = {
                        'exact_title': deezer_result['title'],
                        'exact_artist': deezer_result['artist'],
                        'duration': deezer_result['duration'],
                        'album_cover_xl': deezer_result.get('album_cover', '')
                    }
                    
                    logger.info(f"✅ Enhanced with Deezer: {deezer_result['title']} by {deezer_result['artist']}")
                
            except Exception as e:
                logger.warning(f"Deezer enhancement failed: {e}")
            
            return spotify_metadata
            
        except Exception as e:
            logger.error(f"Enhanced metadata error: {e}")
            return self.get_track_metadata(spotify_url)
