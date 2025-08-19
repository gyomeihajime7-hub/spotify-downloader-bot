import random
import logging

logger = logging.getLogger(__name__)

class DemoSongs:
    def __init__(self):
        """Initialize with verified working demo tracks (tested Aug 18, 2025)"""
        self.popular_tracks = [
            {
                'name': 'Never Gonna Give You Up',
                'artist': 'Rick Astley',
                'spotify_url': 'https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC'
            },
            {
                'name': 'Shape of You',
                'artist': 'Ed Sheeran',
                'spotify_url': 'https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3'
            },
            {
                'name': 'bad guy',
                'artist': 'Billie Eilish',
                'spotify_url': 'https://open.spotify.com/track/2Fxmhks0bxGSBdJ92vM42m'
            },
            {
                'name': 'Circles',
                'artist': 'Post Malone',
                'spotify_url': 'https://open.spotify.com/track/21jGcNKet2qwijlDFuPiPb'
            },
            {
                'name': 'Someone Like You',
                'artist': 'Adele',
                'spotify_url': 'https://open.spotify.com/track/1zwMYTA5nlNjZxYrvBB2pV'
            },
            {
                'name': 'Bohemian Rhapsody',
                'artist': 'Queen',
                'spotify_url': 'https://open.spotify.com/track/3z8h0TU7ReDPLIbEnYhWZb'
            },
            {
                'name': 'Imagine',
                'artist': 'John Lennon',
                'spotify_url': 'https://open.spotify.com/track/7pKfPomDEeI4TPT6EOYjn9'
            },
            {
                'name': 'Sweet Child O Mine',
                'artist': 'Guns N Roses',
                'spotify_url': 'https://open.spotify.com/track/7o2CTH4ctstm8TNelqjb51'
            },
            {
                'name': 'Stairway to Heaven',
                'artist': 'Led Zeppelin',
                'spotify_url': 'https://open.spotify.com/track/5CQ30WqJwcep0pYcV4AMNc'
            },
            {
                'name': 'Hotel California',
                'artist': 'Eagles',
                'spotify_url': 'https://open.spotify.com/track/40riOy7x9W7GXjyGp4pjAv'
            },
            {
                'name': 'Smells Like Teen Spirit',
                'artist': 'Nirvana',
                'spotify_url': 'https://open.spotify.com/track/5ghIJDpPoe3CfHMGu71E6T'
            },
            {
                'name': 'Yesterday',
                'artist': 'The Beatles',
                'spotify_url': 'https://open.spotify.com/track/3BQHpFgAp4l80e1XslIjNI'
            }
        ]

    def get_random_tracks(self, count=6):
        """Get random tracks for demo"""
        try:
            if count > len(self.popular_tracks):
                count = len(self.popular_tracks)
            
            return random.sample(self.popular_tracks, count)
            
        except Exception as e:
            logger.error(f"Error getting random tracks: {e}")
            return self.popular_tracks[:count]

    def get_track_by_index(self, index):
        """Get track by index"""
        try:
            if 0 <= index < len(self.popular_tracks):
                return self.popular_tracks[index]
            return None
        except Exception as e:
            logger.error(f"Error getting track by index: {e}")
            return None

    def add_custom_track(self, name, artist, spotify_url):
        """Add a custom track to the demo list"""
        try:
            custom_track = {
                'name': name,
                'artist': artist,
                'spotify_url': spotify_url
            }
            self.popular_tracks.append(custom_track)
            logger.info(f"Added custom track: {name} by {artist}")
            return True
        except Exception as e:
            logger.error(f"Error adding custom track: {e}")
            return False

    def search_demo_tracks(self, query):
        """Search demo tracks by name or artist"""
        try:
            query = query.lower()
            results = []
            
            for track in self.popular_tracks:
                if (query in track['name'].lower() or 
                    query in track['artist'].lower()):
                    results.append(track)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching demo tracks: {e}")
            return []

    def get_all_tracks(self):
        """Get all available demo tracks"""
        return self.popular_tracks.copy()

    def get_tracks_by_artist(self, artist):
        """Get tracks by a specific artist"""
        try:
            artist = artist.lower()
            results = []
            
            for track in self.popular_tracks:
                if artist in track['artist'].lower():
                    results.append(track)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting tracks by artist: {e}")
            return []