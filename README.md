<div align="center">
  <img src="resources/Cover.jpg" alt="Motify Cover" width="100%">
  
  <br>
  <br>

  # Motify

  <p>A powerful and modern music downloader and manager application built with Python.</p>

  <!-- Release & License -->
  [![Release](https://img.shields.io/github/v/release/mosh3eb/motify?color=1DB954&style=for-the-badge)](https://github.com/mosh3eb/motify/releases)
  [![License](https://img.shields.io/github/license/mosh3eb/motify?color=1DB954&style=for-the-badge)](LICENSE)
  
  <!-- Python & Dependencies -->
  [![Python](https://img.shields.io/badge/python-3.10+-1DB954?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
  [![PyPI](https://img.shields.io/pypi/v/motify?color=1DB954&style=for-the-badge)](https://pypi.org/project/motify/)
  [![PyPI Downloads](https://img.shields.io/pypi/dm/motify?color=1DB954&style=for-the-badge)](https://pypi.org/project/motify/)
  
  <!-- Build & Tests -->
  [![Build Status](https://img.shields.io/github/actions/workflow/status/mosh3eb/motify/release.yml?branch=main&color=1DB954&style=for-the-badge)](https://github.com/mosh3eb/motify/actions)
  [![Code Coverage](https://img.shields.io/codecov/c/github/mosh3eb/motify?color=1DB954&style=for-the-badge)](https://codecov.io/gh/mosh3eb/motify)
  
  <!-- Repository -->
  [![Stars](https://img.shields.io/github/stars/mosh3eb/motify?color=1DB954&style=for-the-badge)](https://github.com/mosh3eb/motify/stargazers)
  [![Issues](https://img.shields.io/github/issues/mosh3eb/motify?color=1DB954&style=for-the-badge)](https://github.com/mosh3eb/motify/issues)
  [![Pull Requests](https://img.shields.io/github/issues-pr/mosh3eb/motify?color=1DB954&style=for-the-badge)](https://github.com/mosh3eb/motify/pulls)
  
  <!-- Social -->
  [![Discord](https://img.shields.io/discord/YOUR_DISCORD_ID?color=1DB954&style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/your-invite)
  [![Twitter Follow](https://img.shields.io/twitter/follow/your_twitter?color=1DB954&style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/your_twitter)
</div>

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
- Git (for cloning the repository)

### Setup Methods

#### Method 1: Direct Download
1. Download the latest release from the [Releases page](https://github.com/mosh3eb/motify/releases)
2. Extract the downloaded zip file
3. Navigate to the extracted directory

#### Method 2: Clone Repository
1. Clone the repository:
```bash
git clone https://github.com/mosh3eb/motify.git
cd motify
```

### Installation Steps

1. Create and activate a virtual environment (recommended):
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Spotify credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Copy your Client ID and Client Secret
   - Add `http://localhost:8888/callback` as a Redirect URI in your Spotify app settings

4. Create a copy of the example configuration:
```bash
cp app_config.example.json app_config.json
```

5. Configure your Spotify API credentials in `app_config.json`

### Running the Application

1. Activate the virtual environment (if not already activated):
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
.\venv\Scripts\activate
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

## 🔧 Deployment

### Local Deployment

1. Follow the installation steps above
2. Configure your settings in `app_config.json`
3. Run the application using `python run.py`

### System-wide Installation (Optional)

#### On macOS
1. Create an application bundle:
```bash
pip install py2app
python setup.py py2app
```
2. Move the created .app file to your Applications folder

#### On Windows
1. Create an executable:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=resources/icon.ico run.py
```
2. The executable will be created in the `dist` directory

#### On Linux
1. Create a desktop entry:
```bash
sudo cp resources/motify.desktop /usr/share/applications/
sudo cp resources/icon.png /usr/share/icons/hicolor/256x256/apps/motify.png
```

### Docker Deployment (Optional)

1. Build the Docker image:
```bash
docker build -t motify .
```

2. Run the container:
```bash
docker run -d \
  -v ${PWD}/downloads:/app/downloads \
  -v ${PWD}/app_config.json:/app/app_config.json \
  -e DISPLAY=${DISPLAY} \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  motify
```

---
Made with ❤️ by Mosh3eb