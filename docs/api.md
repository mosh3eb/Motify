# API Reference

## Motify Class

### Initialization
```python
from motify import Motify
motify = Motify()
```

### Methods
- `download_track(track_id)`
- `download_playlist(playlist_id)`
- `search(query)`
- `get_history()`

## Config Class

### Initialization
```python
from motify import Config
config = Config(output_dir="/path/to/dir", quality="high")
```

### Options
- `output_dir`: Directory for downloads
- `quality`: Download quality ("high", "medium", "low")

## Example
```python
from motify import Motify, Config
config = Config(output_dir="music", quality="high")
motify = Motify(config)
motify.download_track("track_id")
```

## Services

### SpotifyService

```python
from src.services.spotify_service import SpotifyService

spotify = SpotifyService(client_id, client_secret)
```

#### Methods

- `search(query, type='track')`: Search Spotify
- `get_track(track_id)`: Get track details
- `get_album(album_id)`: Get album details
- `get_artist(artist_id)`: Get artist details

### Downloader

```python
from src.services.downloader import Downloader

downloader = Downloader(config)
```

#### Methods

- `download_track(track_info)`: Download a track
- `download_playlist(playlist_info)`: Download a playlist
- `download_album(album_info)`: Download an album

## User Interface

### MainWindow

```python
from src.ui.main_window import MainWindow

window = MainWindow(config)
```

### Tabs

- SearchTab: Music search interface
- QueueTab: Download queue management
- HistoryTab: Download history
- LyricsTab: Lyrics viewer/editor
- SettingsTab: Application settings

## Configuration

### ConfigManager

```python
from src.utils.config import ConfigManager

config = ConfigManager('app_config.json')
```

#### Properties

- `theme`: UI theme
- `audio_quality`: Download quality
- `audio_format`: Output format
- `concurrent_downloads`: Max simultaneous downloads
- `notification_enabled`: Enable/disable notifications

## Events

### Download Events

- `on_download_start(track_info)`
- `on_download_progress(track_info, progress)`
- `on_download_complete(track_info)`
- `on_download_error(track_info, error)`

### Queue Events

- `on_queue_update(queue_items)`
- `on_queue_complete()`
- `on_queue_error(error)`

## Error Handling

```python
from src.utils.exceptions import (
    DownloadError,
    AuthenticationError,
    ConfigError
)
```
