# Installation Guide

<div class="install-options" markdown>

## 🚀 Quick Install

```bash
pip install motify-music
```

## 🐳 Docker Install

```bash
docker pull mosh3eb/motify
docker run -d -p 8000:8000 mosh3eb/motify
```

## 📦 From Source

```bash
git clone https://github.com/mosh3eb/motify.git
cd motify
pip install -e .
```

</div>

## System Requirements

<div class="requirements-grid" markdown>

### 💻 Hardware
- 2GB RAM minimum
- 1GB free disk space
- Internet connection

### 🔧 Software
- Python 3.8 or higher
- pip package manager
- FFmpeg (for audio processing)

### 📱 Supported Platforms
- Windows 10/11
- macOS 10.15+
- Linux (most distributions)

</div>

## Detailed Instructions

### Step 1: Prerequisites

<div class="install-step" markdown>
1. Install Python 3.8 or higher from [python.org](https://python.org)
2. Install FFmpeg:
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt install ffmpeg

   # Windows
   choco install ffmpeg
   ```
3. Verify installations:
   ```bash
   python --version
   ffmpeg -version
   ```
</div>

### Step 2: Install Motify

<div class="install-step" markdown>
1. Install using pip:
   ```bash
   pip install motify-music
   ```
2. Verify installation:
   ```bash
   motify --version
   ```
</div>

### Step 3: Configuration

<div class="install-step" markdown>
1. Run Motify first time:
   ```bash
   motify
   ```
2. Follow the setup wizard
3. Configure Spotify credentials
4. Set download preferences
</div>

## Troubleshooting

<div class="troubleshooting" markdown>

??? question "Installation fails with dependency error"
    Make sure pip is up to date:
    ```bash
    pip install --upgrade pip
    ```
    Then try installing again.

??? question "FFmpeg not found"
    Ensure FFmpeg is in your system PATH or specify its location in settings.

??? question "Spotify authentication fails"
    Check your credentials and ensure you have a valid Spotify account.

</div>
