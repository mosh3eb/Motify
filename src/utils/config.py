import os
import json

# Application constants
APP_NAME = "Motify"
APP_VERSION = "2.0.0"
DEFAULT_THEME = "cyborg"
AVAILABLE_THEMES = ['cosmo', 'flatly', 'litera', 'minty', 'lumen',
                   'sandstone', 'yeti', 'pulse', 'united', 'morph', 'journal',
                   'darkly', 'superhero', 'solar', 'cyborg', 'vapor', 'simplex',
                   'cerculean']

# File paths
DOWNLOAD_FOLDER = 'downloads'
CREDENTIALS_FILE = 'credentials.json'
DOWNLOADED_TRACKS_FILE = 'downloaded_tracks.json'
QUEUE_FILE = 'playlist_queue.json'
STATUS_FILE = 'download_status.json'
CONFIG_FILE = 'app_config.json'
HISTORY_FILE = 'download_history.json'

# Audio quality options
AUDIO_QUALITY_OPTIONS = {
    "Low": "128",
    "Medium": "192",
    "High": "256",
    "Very High": "320"
}

DEFAULT_AUDIO_QUALITY = "Medium"
DEFAULT_AUDIO_FORMAT = "m4a"
SUPPORTED_AUDIO_FORMATS = ["m4a", "mp3", "flac", "wav"]

# Create necessary directories
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def get_app_config():
    """Load application configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    # Default configuration
    default_config = {
        "theme": DEFAULT_THEME,
        "audio_quality": DEFAULT_AUDIO_QUALITY,
        "audio_format": DEFAULT_AUDIO_FORMAT,
        "concurrent_downloads": 1,
        "auto_start_queue": False,
        "notification_enabled": True,
        "custom_download_folder": DOWNLOAD_FOLDER,
        "skip_existing": True
    }
    
    # Create default config file
    with open(CONFIG_FILE, 'w') as f:
        json.dump(default_config, f, indent=4)
    
    return default_config

def save_app_config(config):
    """Save application configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4) 