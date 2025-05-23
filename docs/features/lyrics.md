# Lyrics Support

Motify provides comprehensive lyrics support, allowing you to view and save lyrics for your favorite songs.

## Features

### Lyrics Display
- Real-time lyrics display
- Synchronized with music playback
- Multiple language support
- Timestamp support

### Lyrics Management
- Save lyrics with downloaded tracks
- Search lyrics database
- Edit and update lyrics
- Export lyrics in various formats

### Integration
- Automatic lyrics fetching
- Manual lyrics search
- Lyrics editing interface
- Batch lyrics processing

## Usage

### Fetching Lyrics

```python
from motify_music import LyricsService

# Initialize service
lyrics = LyricsService()

# Get lyrics for a track
track_lyrics = lyrics.get_lyrics(
    track_name="Song Name",
    artist="Artist Name"
)

# Save lyrics with track
lyrics.save_lyrics(
    track_path="path/to/track.mp3",
    lyrics=track_lyrics
)
```

### Managing Lyrics

```python
# Search lyrics database
results = lyrics.search_lyrics("search term")

# Update lyrics
lyrics.update_lyrics(
    track_id="track_id",
    new_lyrics="updated lyrics"
)

# Export lyrics
lyrics.export_lyrics(
    track_id="track_id",
    format="txt"
)
```

## Lyrics Sources

Motify supports multiple lyrics sources:

- Genius
- Musixmatch
- Local database
- Custom sources

## Format Support

Lyrics can be saved in various formats:

- Plain text
- LRC (synchronized lyrics)
- JSON
- HTML

## Features

### Synchronized Lyrics
- Display lyrics in sync with music
- Support for LRC format
- Manual timestamp adjustment
- Export synchronized lyrics

### Batch Processing
- Process multiple tracks
- Update lyrics in bulk
- Export multiple lyrics files
- Convert between formats

## Tips

- Use the search feature to find lyrics
- Check multiple sources for accuracy
- Save lyrics with downloaded tracks
- Export lyrics for backup

## Troubleshooting

If you encounter issues with lyrics:

1. Check internet connection
2. Verify track metadata
3. Try alternative sources
4. Check file permissions

For more help, visit our [GitHub issues page](https://github.com/mosh3eb/motify/issues). 