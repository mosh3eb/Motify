# Installation Guide

Motify supports Windows, macOS, Linux, and Docker. Follow the steps below for your platform.

## Prerequisites
- Python 3.10+
- Internet connection
- Spotify account

## Windows
1. Download and install [Python 3.10+](https://www.python.org/downloads/windows/)
2. Open Command Prompt and run:
   ```sh
   pip install motify-music
   ```
3. Launch Motify:
   ```sh
   motify
   ```

## macOS
1. Install [Homebrew](https://brew.sh/) (if not installed)
2. Install Python 3.10+:
   ```sh
   brew install python@3.10
   ```
3. Install Motify:
   ```sh
   pip3 install motify-music
   ```
4. Launch Motify:
   ```sh
   motify
   ```

## Linux
1. Install Python 3.10+ using your package manager
2. Install Motify:
   ```sh
   pip3 install motify-music
   ```
3. Launch Motify:
   ```sh
   motify
   ```

## Docker
1. Pull the image:
   ```sh
   docker pull mosh3eb/motify
   ```
2. Run the container:
   ```sh
   docker run -it --rm mosh3eb/motify
   ```

## Troubleshooting
- If you encounter issues, see [Troubleshooting & FAQ](troubleshooting.md) or open a [GitHub Issue](https://github.com/mosh3eb/motify/issues).

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

## Next Steps

After installation:
1. [Configure Spotify credentials](usage.md#configuration)
2. [Learn the basics](usage.md#quick-start)
3. [Explore features](features/playlist.md)
