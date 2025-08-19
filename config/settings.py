import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Optional API Keys
JAMENDO_CLIENT_ID = os.getenv('JAMENDO_CLIENT_ID', 'your_default_jamendo_key')
SOUNDCLOUD_CLIENT_ID = os.getenv('SOUNDCLOUD_CLIENT_ID', 'your_default_soundcloud_key')

# Server Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 8080
FLASK_DEBUG = False

# Download Configuration
MAX_PLAYLIST_SIZE = 50  # Maximum number of tracks to download from a playlist
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size
DOWNLOAD_TIMEOUT = 30  # seconds

# Quality Settings
QUALITY_SETTINGS = {
    'high': {
        'bitrate': 320,
        'format': 'mp3',
        'description': 'High Quality (320kbps)'
    },
    'medium': {
        'bitrate': 192,
        'format': 'mp3',
        'description': 'Medium Quality (192kbps)'
    },
    'low': {
        'bitrate': 128,
        'format': 'mp3',
        'description': 'Low Quality (128kbps)'
    }
}

# Audio Sources Configuration
AUDIO_SOURCES = {
    'freemusicarchive': {
        'enabled': True,
        'base_url': 'https://freemusicarchive.org',
        'priority': 1
    },
    'jamendo': {
        'enabled': True,
        'base_url': 'https://api.jamendo.com/v3.0',
        'priority': 2
    },
    'archive_org': {
        'enabled': True,
        'base_url': 'https://archive.org',
        'priority': 3
    },
    'soundcloud_alternative': {
        'enabled': True,
        'priority': 4
    }
}

# Message Templates
MESSAGES = {
    'welcome': """
🎵 *Welcome to Spotify Music Downloader Bot!* 🎵

Hey there! I'm your personal music assistant! 🤖✨

*What can I do?*
• 📱 Download songs from Spotify links
• 📀 Process entire albums and playlists
• 🎛️ Choose audio quality before download
• 🎧 Find music from multiple sources

*How to use:*
1️⃣ Send me any Spotify link (song/album/playlist)
2️⃣ Choose your preferred audio quality
3️⃣ Get your music instantly! 🚀

Ready to discover some music? Try the demo below! 👇
    """,
    
    'help': """
🆘 *Help & Instructions* 🆘

*Supported Links:*
• 🎵 Spotify Songs: `open.spotify.com/track/...`
• 📀 Spotify Albums: `open.spotify.com/album/...`
• 📋 Spotify Playlists: `open.spotify.com/playlist/...`

*How it works:*
1️⃣ Send me a Spotify link
2️⃣ I'll extract the metadata
3️⃣ Choose your preferred quality
4️⃣ I'll find and download the audio
5️⃣ Enjoy your music! 🎊

*Quality Options:*
• 🔥 High Quality (320kbps)
• ⚡ Medium Quality (192kbps)
• 📱 Low Quality (128kbps)

*Tips:*
• Use /start to return to main menu
• Try demo songs to test the bot
• Be patient for large playlists! ⏳

Need more help? Just ask! 😊
    """,
    
    'invalid_link': """
🤔 That doesn't look like a Spotify link!

Please send me a valid Spotify link:
• 🎵 Song: `open.spotify.com/track/...`
• 📀 Album: `open.spotify.com/album/...`
• 📋 Playlist: `open.spotify.com/playlist/...`

Or try our demo songs! 👇
    """,
    
    'processing': "🔍 *Analyzing Spotify link...*",
    'downloading': "⬬ *Downloading...*",
    'success': "✅ *Download Complete!*",
    'error': "❌ *Error occurred*",
    'cancelled': "❌ Operation cancelled."
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

# Rate Limiting
RATE_LIMITS = {
    'downloads_per_user_per_hour': 20,
    'downloads_per_user_per_day': 100,
    'max_concurrent_downloads': 3
}

# File Cleanup
CLEANUP_SETTINGS = {
    'auto_cleanup': True,
    'cleanup_delay': 300,  # 5 minutes
    'max_temp_files': 100
}

# Error Messages
ERROR_MESSAGES = {
    'spotify_api_error': "❌ Error accessing Spotify API. Please try again later.",
    'download_failed': "❌ Download failed. The track might not be available from our sources.",
    'invalid_quality': "❌ Invalid quality selection. Please choose from available options.",
    'file_too_large': "❌ File is too large to send via Telegram.",
    'rate_limit_exceeded': "❌ You've reached the download limit. Please try again later.",
    'server_error': "❌ Server error. Please try again later.",
    'maintenance': "🔧 Bot is under maintenance. Please try again later."
}

# Feature Flags
FEATURES = {
    'demo_songs': True,
    'playlist_download': True,
    'album_download': True,
    'quality_selection': True,
    'progress_indicators': True,
    'file_cleanup': True,
    'rate_limiting': True
}

def get_env_var(var_name, default=None, required=False):
    """Get environment variable with validation"""
    value = os.getenv(var_name, default)
    
    if required and not value:
        raise ValueError(f"Required environment variable {var_name} is not set")
    
    return value

def validate_config():
    """Validate configuration settings"""
    required_vars = ['TELEGRAM_BOT_TOKEN']
    
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Required environment variable {var} is not set")
    
    # Validate optional but recommended variables
    recommended_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']
    missing_recommended = []
    
    for var in recommended_vars:
        if not os.getenv(var):
            missing_recommended.append(var)
    
    if missing_recommended:
        print(f"Warning: Recommended environment variables not set: {', '.join(missing_recommended)}")
    
    return True
