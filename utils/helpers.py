import re
import logging

logger = logging.getLogger(__name__)

def is_spotify_link(url):
    """Check if URL is a valid Spotify link"""
    spotify_patterns = [
        r'https?://open\.spotify\.com/(track|album|playlist)/[a-zA-Z0-9]+',
        r'https?://spotify\.com/(track|album|playlist)/[a-zA-Z0-9]+',
        r'spotify:(track|album|playlist):[a-zA-Z0-9]+',
        r'open\.spotify\.com/(track|album|playlist)/[a-zA-Z0-9]+',
        r'spotify\.com/(track|album|playlist)/[a-zA-Z0-9]+'
    ]
    
    for pattern in spotify_patterns:
        if re.search(pattern, url):
            return True
    return False

def clean_filename(filename):
    """Clean filename for safe file system usage"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'[\s]+', ' ', filename)  # Replace multiple spaces with single space
    filename = filename.strip()
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename or "untitled"

def sanitize_search_query(query):
    """Sanitize search query for web searches"""
    # Remove special characters that might break searches
    query = re.sub(r'[^\w\s\-\(\)]', ' ', query)
    query = re.sub(r'\s+', ' ', query)  # Replace multiple spaces
    return query.strip()

def format_duration(duration_ms):
    """Format duration from milliseconds to MM:SS format"""
    try:
        if not duration_ms:
            return "0:00"
        
        seconds = duration_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        
        return f"{minutes}:{seconds:02d}"
    except:
        return "0:00"

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"
    except:
        return "Unknown"

def extract_artist_from_title(title):
    """Extract artist from title if formatted as 'Artist - Title'"""
    try:
        if ' - ' in title:
            parts = title.split(' - ', 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return None, title
    except:
        return None, title

def validate_url(url):
    """Validate if URL is properly formatted"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def escape_markdown(text):
    """Escape special characters for Telegram markdown"""
    if not text:
        return ""
    
    # Escape markdown special characters
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def truncate_text(text, max_length=100):
    """Truncate text to specified length with ellipsis"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def parse_quality_from_filename(filename):
    """Parse quality information from filename"""
    try:
        filename = filename.lower()
        
        if '320' in filename or 'high' in filename:
            return 'high'
        elif '192' in filename or 'medium' in filename:
            return 'medium'
        elif '128' in filename or 'low' in filename:
            return 'low'
        else:
            return 'medium'  # default
    except:
        return 'medium'

def generate_search_variations(track_name, artist_name):
    """Generate different search query variations"""
    variations = []
    
    # Basic combinations
    variations.append(f"{track_name} {artist_name}")
    variations.append(f"{artist_name} {track_name}")
    variations.append(f'"{track_name}" "{artist_name}"')
    
    # With additional keywords
    variations.append(f"{track_name} {artist_name} official")
    variations.append(f"{track_name} {artist_name} audio")
    variations.append(f"{track_name} {artist_name} mp3")
    
    # Clean versions (remove special characters)
    clean_track = re.sub(r'[^\w\s]', '', track_name)
    clean_artist = re.sub(r'[^\w\s]', '', artist_name)
    
    if clean_track != track_name or clean_artist != artist_name:
        variations.append(f"{clean_track} {clean_artist}")
        variations.append(f"{clean_artist} {clean_track}")
    
    return variations

def is_valid_audio_file(file_path):
    """Check if file is a valid audio file"""
    try:
        import os
        
        if not os.path.exists(file_path):
            return False
        
        # Check file size (should be at least 100KB for a real audio file)
        file_size = os.path.getsize(file_path)
        if file_size < 100000:  # 100KB
            return False
        
        # Check file extension
        valid_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
        file_ext = os.path.splitext(file_path)[1].lower()
        
        return file_ext in valid_extensions
        
    except Exception as e:
        logger.error(f"Error validating audio file: {e}")
        return False

def create_progress_bar(current, total, length=20):
    """Create a simple progress bar string"""
    try:
        if total == 0:
            return "▱" * length
        
        filled = int(length * current / total)
        bar = "▰" * filled + "▱" * (length - filled)
        percentage = int(100 * current / total)
        
        return f"{bar} {percentage}%"
    except:
        return "▱" * length
