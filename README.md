# Motify 🎵

A powerful and modern music downloader and manager application built with Python. Motify allows you to easily download and manage your music collection with a beautiful user interface and seamless Spotify integration.

![Motify Interface](Screen%20Shot%202025-04-14%20at%2000.22.53%20AM.png)

## ✨ Features

- 🎯 Search and download music from multiple sources
- 🎨 Modern and customizable UI with multiple themes
- 📑 Smart playlist management and queue system
- 🎵 High-quality audio downloads with format selection
- 📊 Download history and statistics tracking
- 🎤 Integrated lyrics support
- 🔄 Concurrent download capabilities
- 📱 Desktop notifications
- ⚡ YouTube integration
- 🎯 Duplicate detection and skip functionality

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Spotify Developer Account for API access

### Setup

1. Clone the repository:
```bash
git clone https://github.com/mosh3eb/motify.git
cd motify
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Spotify credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Copy your Client ID and Client Secret

## ⚙️ Configuration

The application can be configured through `app_config.json`:

| Setting | Description | Default |
|---------|------------|---------|
| theme | UI theme selection | cyborg |
| audio_quality | Audio quality (Low/Medium/High) | Medium |
| audio_format | Output audio format | m4a |
| concurrent_downloads | Number of simultaneous downloads | 1 |
| auto_start_queue | Auto-start download queue on launch | false |
| notification_enabled | Enable/disable notifications | true |
| custom_download_folder | Custom download location | downloads |
| skip_existing | Skip already downloaded files | true |

## 🚦 Getting Started

1. Configure your Spotify API credentials in `app_config.json`:
```json
{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
}
```

2. Launch the application:
```bash
python run.py
```

## 📱 Usage

### Main Features
- **Search Tab**: Search for tracks, albums, or artists
- **Queue Tab**: Manage your download queue
- **History Tab**: View download history and statistics
- **Lyrics Tab**: View synchronized lyrics
- **YouTube Tab**: Search and download from YouTube
- **Settings Tab**: Customize application settings

### Keyboard Shortcuts
- `Ctrl/Cmd + F`: Focus search
- `Ctrl/Cmd + Q`: Clear queue
- `Space`: Play/Pause current track preview
- `Esc`: Clear search

## 🏗️ Project Structure

```
src/
├── services/         # Core services (downloader, Spotify)
├── ui/              # User interface components
└── utils/           # Utility functions and configurations
```

## 🛟 Support

If you encounter any issues or have suggestions:
1. Check the existing issues on GitHub
2. Open a new issue with a detailed description
3. Include your system information and logs

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Spotify API for music data
- Python community for amazing libraries
- Contributors and users of Motify

---
Made with ❤️ by Mosh3eb