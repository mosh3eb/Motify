# Configuration

Motify provides a flexible configuration system that allows you to customize various aspects of the application.

## Configuration File

The configuration is stored in `app_config.json` in your home directory:

```json
{
    "spotify": {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "redirect_uri": "http://localhost:8888/callback"
    },
    "download": {
        "quality": "best",
        "format": "mp3",
        "path": "~/Music/Motify",
        "naming": "{artist} - {title}"
    },
    "interface": {
        "theme": "dark",
        "language": "en",
        "notifications": true
    }
}
```

## Configuration Options

### Spotify Settings

| Option | Type | Description |
|--------|------|-------------|
| client_id | string | Your Spotify API client ID |
| client_secret | string | Your Spotify API client secret |
| redirect_uri | string | OAuth redirect URI |

### Download Settings

| Option | Type | Description |
|--------|------|-------------|
| quality | string | Audio quality (best, high, medium, low) |
| format | string | Audio format (mp3, m4a, flac) |
| path | string | Download directory path |
| naming | string | File naming pattern |

### Interface Settings

| Option | Type | Description |
|--------|------|-------------|
| theme | string | UI theme (dark, light) |
| language | string | Interface language |
| notifications | boolean | Enable/disable notifications |

## Usage

### Loading Configuration

```python
from motify_music import Config

# Load configuration
config = Config()

# Get specific setting
download_path = config.get("download.path")

# Update setting
config.set("download.quality", "high")
```

### Default Configuration

```python
# Get default configuration
defaults = config.get_defaults()

# Reset to defaults
config.reset_to_defaults()
```

## Environment Variables

You can override configuration using environment variables:

```bash
export MOTIFY_SPOTIFY_CLIENT_ID="your_client_id"
export MOTIFY_DOWNLOAD_PATH="~/Custom/Music"
```

## Configuration Methods

### File-based Configuration

```python
# Save configuration
config.save()

# Load configuration
config.load()

# Check if configuration exists
if config.exists():
    # Load existing config
    config.load()
else:
    # Create new config
    config.create_default()
```

### Runtime Configuration

```python
# Update multiple settings
config.update({
    "download.quality": "high",
    "interface.theme": "dark"
})

# Get all settings
all_settings = config.get_all()

# Validate configuration
config.validate()
```

## Best Practices

1. Keep sensitive data (API keys) secure
2. Use environment variables for sensitive data
3. Backup your configuration
4. Validate configuration before use

## Troubleshooting

If you encounter configuration issues:

1. Check file permissions
2. Verify JSON syntax
3. Ensure required fields are present
4. Check environment variables

For more help, visit our [GitHub issues page](https://github.com/mosh3eb/motify/issues). 