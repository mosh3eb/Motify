# Motify Documentation

Welcome to the official Motify documentation. This comprehensive guide will help you understand and use all features of Motify effectively.

## 🚀 Quick Navigation

<div class="grid cards" markdown>

-   :fontawesome-solid-rocket: __[Installation Guide](installation.md)__
    
    ---
    
    Detailed installation instructions for different operating systems and environments.

-   :fontawesome-solid-book: __[User Guide](usage.md)__
    
    ---
    
    Complete user guide with step-by-step instructions and best practices.

-   :fontawesome-solid-code: __[API Reference](api.md)__
    
    ---
    
    Technical documentation for developers and advanced users.

-   :fontawesome-solid-wrench: __[Configuration](api/configuration.md)__
    
    ---
    
    Advanced configuration options and customization guide.

</div>

## 📚 Documentation Sections

### User Guides
- [Installation Guide](installation.md) - How to install Motify
- [Quick Start Guide](usage.md) - Get started in minutes
- [User Interface Guide](usage.md#user-interface) - Understanding the GUI
- [Download Guide](usage.md#downloading-music) - How to download music
- [Playlist Management](features/playlist.md) - Working with playlists
- [Download History](features/history.md) - Tracking your downloads
- [Lyrics Support](features/lyrics.md) - Using lyrics features

### Technical Documentation
- [API Overview](api.md) - Introduction to the API
- [Configuration](api/configuration.md) - Advanced configuration
- [Spotify Service](api/spotify.md) - Spotify integration details
- [Download Service](api/downloader.md) - Download functionality
- [Development Guide](contributing.md) - Contributing to Motify
- [Changelog](changelog.md) - Version history and changes

## 🎯 Key Features

### Music Download
- High-quality audio downloads
- Multiple format support (MP3, M4A, FLAC)
- Batch download capabilities
- Download queue management
- Progress tracking and resume support

### Playlist Management
- Spotify playlist integration
- Playlist organization
- Download queue system
- Playlist statistics
- Export/import functionality

### User Interface
- Modern and intuitive design
- Dark/Light theme support
- Responsive layout
- Keyboard shortcuts
- Progress indicators

### Advanced Features
- Lyrics integration
- Download history
- Statistics and analytics
- Custom naming patterns
- Metadata management

## 🔧 Configuration

Learn how to customize Motify to your needs:
- [Basic Configuration](api/configuration.md#basic-configuration)
- [Advanced Settings](api/configuration.md#advanced-settings)
- [Environment Variables](api/configuration.md#environment-variables)
- [File Naming](api/configuration.md#file-naming)

## 💻 Development

Information for developers and contributors:
- [Contributing Guide](contributing.md)
- [Code Style Guide](contributing.md#code-style)
- [Testing Guide](contributing.md#testing)
- [Release Process](contributing.md#releasing)

## 📝 Examples

### Basic Usage
```python
from motify_music import Motify

# Initialize Motify
app = Motify()

# Download a track
app.download_track("spotify:track:track_id")

# Download a playlist
app.download_playlist("spotify:playlist:playlist_id")
```

### Advanced Configuration
```python
from motify_music import Config

# Custom configuration
config = Config({
    "download": {
        "quality": "high",
        "format": "flac",
        "path": "~/Music/Motify"
    }
})

# Initialize with custom config
app = Motify(config=config)
```

## 🤝 Support

Need help? Here's how to get support:
- [GitHub Issues](https://github.com/mosh3eb/motify/issues)
- [Discord Community](https://discord.gg/motify)
- [Email Support](mailto:support@motify.app)

## 📜 License

Motify is licensed under the MIT License. See the [LICENSE](https://github.com/mosh3eb/motify/blob/main/LICENSE) file for details. 