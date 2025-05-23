# Playlist Management

Motify provides powerful playlist management features that allow you to organize and download your music efficiently.

## Features

### View Playlists
- Access all your Spotify playlists
- Sort and filter playlists
- Search within playlists
- View playlist details and statistics

### Download Playlists
1. Select a playlist from your library
2. Choose download quality and format
3. Add to download queue
4. Monitor download progress

### Queue Management
- Add multiple playlists to queue
- Reorder download queue
- Pause/resume downloads
- Remove items from queue

## Usage

### Adding Playlists to Queue

```python
from motify_music import SpotifyService

# Initialize service
spotify = SpotifyService()

# Get user playlists
playlists = spotify.get_user_playlists()

# Add playlist to download queue
spotify.add_to_queue(playlist_id="your_playlist_id")
```

### Managing Download Queue

```python
# Get current queue
queue = spotify.get_download_queue()

# Reorder queue
spotify.reorder_queue(queue_item_id="item_id", new_position=0)

# Remove from queue
spotify.remove_from_queue(queue_item_id="item_id")
```

## Configuration

You can configure playlist download behavior in the settings:

- Download quality
- File naming format
- Metadata preferences
- Download location

## Tips

- Use the search feature to quickly find playlists
- Sort playlists by name, date, or size
- Monitor download progress in the queue tab
- Use keyboard shortcuts for faster navigation

## Troubleshooting

If you encounter issues with playlist downloads:

1. Check your internet connection
2. Verify Spotify credentials
3. Ensure sufficient disk space
4. Check download permissions

For more help, visit our [GitHub issues page](https://github.com/mosh3eb/motify/issues). 