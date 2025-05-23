# Motify Documentation

Welcome to the Motify documentation! This guide will help you understand and utilize all the features of Motify effectively.

## Quick Navigation

- [Installation Guide](installation.md)
- [User Guide](usage.md)
- [API Reference](api.md)
- [Configuration](api/configuration.md)

## Documentation Sections

### User Guides
- **Installation**: Detailed instructions for setting up Motify on different platforms.
- **User Interface**: Explore the modern, intuitive GUI and its features.
- **Playlist Management**: Learn how to manage and download playlists efficiently.
- **Download History**: Track your downloads and view statistics.

### Technical Documentation
- **API Overview**: Understand the core components and how they interact.
- **Configuration**: Customize Motify to suit your needs.
- **Advanced Usage**: Tips and tricks for power users.

## Key Features

- **Music Download**: Download high-quality audio from Spotify.
- **Playlist Management**: Organize and download entire playlists with ease.
- **User Interface**: Modern, responsive design for a seamless experience.
- **Advanced Features**: Lyrics integration, download history, and more.

## Examples

### Basic Usage
```python
from motify import Motify

# Initialize Motify
motify = Motify()

# Download a track
motify.download_track("track_id")
```

### Advanced Configuration
```python
from motify import Motify, Config

# Custom configuration
config = Config(
    output_dir="custom/path",
    quality="high"
)

# Initialize with custom config
motify = Motify(config)
```

## Support

For issues, feature requests, or contributions, visit our [GitHub repository](https://github.com/mosh3eb/motify).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. 