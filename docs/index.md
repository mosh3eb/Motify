# Welcome to Motify Docs

Motify is a modern, open-source Spotify music downloader and manager with a beautiful GUI, advanced playlist features, and high-quality audio support.

---

## 🚀 What Makes Motify Special?
- **Modern, intuitive interface** with dark mode and custom theming
- **Playlist management** and download queue
- **Lyrics integration** and download history
- **Fast, reliable, and open-source**

---

## 📖 Quick Navigation
- [Installation Guide](installation.md)
- [User Guide](usage.md)
- [Features](features.md)
- [API Reference](api.md)
- [Troubleshooting & FAQ](troubleshooting.md)
- [Contributing](contributing.md)

---

> **Tip:** Use the sidebar or search to quickly find what you need!

---

## 🖼️ Screenshots
![Motify UI](assets/screenshots/ui-dark.png)

---

## 💡 Why use Motify?
Motify is designed for music lovers who want a seamless, powerful, and beautiful way to manage and download their Spotify music collections. Whether you're a casual listener or a power user, Motify has you covered.

---

## 🛠️ Get Started
- [Installation Guide](installation.md)
- [User Guide](usage.md)

---

## 🤝 Community & Support
- [GitHub Issues](https://github.com/mosh3eb/motify/issues)
- [Discord](https://discord.gg/motify)

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