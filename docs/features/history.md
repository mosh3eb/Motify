# Download History

Motify keeps track of your download history, providing detailed statistics and insights about your music collection.

## Features

### History Tracking
- Track all downloaded tracks
- Record download dates and times
- Store download quality and format
- Track download success/failure

### Statistics
- Total downloads
- Download success rate
- Storage usage
- Popular artists and genres
- Download trends over time

### History Management
- Search through download history
- Filter by date, artist, or album
- Export history data
- Clear history entries

## Usage

### Viewing History

```python
from motify_music import HistoryService

# Initialize service
history = HistoryService()

# Get all download history
downloads = history.get_all_downloads()

# Get downloads by date range
recent_downloads = history.get_downloads_by_date(
    start_date="2024-01-01",
    end_date="2024-03-20"
)
```

### Statistics

```python
# Get download statistics
stats = history.get_statistics()

# Get popular artists
top_artists = history.get_top_artists(limit=10)

# Get storage usage
storage = history.get_storage_usage()
```

## Data Visualization

Motify provides visual representations of your download history:

- Download trends over time
- Genre distribution
- Artist popularity
- Storage usage

## Export Options

You can export your download history in various formats:

- CSV
- JSON
- Excel
- PDF Report

## Privacy

- History data is stored locally
- No data is sent to external servers
- You can clear history at any time
- Export data before clearing

## Tips

- Regularly check your download history
- Use filters to find specific downloads
- Export important statistics
- Monitor storage usage

## Troubleshooting

If you encounter issues with history tracking:

1. Check file permissions
2. Verify database integrity
3. Ensure sufficient disk space
4. Check for corrupted entries

For more help, visit our [GitHub issues page](https://github.com/mosh3eb/motify/issues). 