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

<div class="grid cards" markdown>

- ![Main Interface](assets/images/screenshots/1.png){ loading=lazy }
  **Main Interface**
  {: .image-caption }

- ![Playlist Management](assets/images/screenshots/2.png){ loading=lazy }
  **Playlist Management**
  {: .image-caption }

- ![Download Queue](assets/images/screenshots/3.png){ loading=lazy }
  **Download Queue**
  {: .image-caption }

- ![Lyrics Support](assets/images/screenshots/4.png){ loading=lazy }
  **Lyrics Support**
  {: .image-caption }

- ![History](assets/images/screenshots/5.png){ loading=lazy }
  **History**
  {: .image-caption }

- ![Settings](assets/images/screenshots/6.png){ loading=lazy }
  **Settings**
  {: .image-caption }

- ![Statistics](assets/images/screenshots/7.png){ loading=lazy }
  **Statistics**
  {: .image-caption }

</div>

<style>
.grid.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    padding: 1rem;
}

.grid.cards > * {
    border: 1px solid rgba(128, 128, 128, 0.1);
    border-radius: 8px;
    padding: 0.5rem;
    text-align: center;
}

.grid.cards img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.image-caption {
    font-size: 1.1em;
    font-weight: 500;
    margin-top: 0.5rem;
}
</style>

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

This project is licensed under the MIT License. See the [LICENSE on GitHub](https://github.com/mosh3eb/motify/blob/main/LICENSE) for details.