# Installation Guide

This guide provides detailed instructions for installing Motify on different operating systems and environments.

## System Requirements

- Python 3.10 or higher
- 100MB free disk space
- Internet connection
- Spotify account

## Quick Install

The simplest way to install Motify is using pip:

```bash
pip install motify-music
```

## Detailed Installation

### Windows

1. Install Python 3.10 or higher:
   - Download from [python.org](https://www.python.org/downloads/)
   - Check "Add Python to PATH" during installation

2. Open Command Prompt and install Motify:
   ```bash
   pip install motify-music
   ```

3. Verify installation:
   ```bash
   motify --version
   ```

### macOS

1. Install Python using Homebrew:
   ```bash
   brew install python@3.10
   ```

2. Install Motify:
   ```bash
   pip3 install motify-music
   ```

3. Verify installation:
   ```bash
   motify --version
   ```

### Linux

1. Install Python 3.10:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.10 python3-pip

   # Fedora
   sudo dnf install python3.10 python3-pip

   # Arch Linux
   sudo pacman -S python python-pip
   ```

2. Install Motify:
   ```bash
   pip3 install motify-music
   ```

3. Verify installation:
   ```bash
   motify --version
   ```

## Development Installation

For developers who want to contribute to Motify:

1. Clone the repository:
   ```bash
   git clone https://github.com/mosh3eb/motify.git
   cd motify
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Docker Installation

You can also run Motify using Docker:

1. Pull the Docker image:
   ```bash
   docker pull mosh3eb/motify
   ```

2. Run the container:
   ```bash
   docker run -it --rm \
     -v ~/Music:/music \
     -v ~/.config/motify:/config \
     mosh3eb/motify
   ```

## Configuration

After installation, you need to configure Motify:

1. Run Motify for the first time:
   ```bash
   motify
   ```

2. Follow the setup wizard to:
   - Configure Spotify credentials
   - Set download location
   - Choose default settings

## Troubleshooting

### Common Issues

1. **Python not found**
   - Ensure Python is in your PATH
   - Try using `python3` instead of `python`

2. **Permission errors**
   - Use `sudo` on Linux/macOS
   - Run as administrator on Windows

3. **Dependencies missing**
   - Update pip: `pip install --upgrade pip`
   - Install system dependencies

### Getting Help

If you encounter issues:
- Check the [FAQ](faq.md)
- Visit [GitHub Issues](https://github.com/mosh3eb/motify/issues)
- Join our [Discord Community](https://discord.gg/motify)

## Next Steps

After installation:
1. [Configure Spotify credentials](usage.md#configuration)
2. [Learn the basics](usage.md#quick-start)
3. [Explore features](features/playlist.md)
