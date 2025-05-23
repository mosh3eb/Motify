# Installation Guide

## Prerequisites

Before installing Motify, ensure you have:

- Python 3.10 or higher installed
- pip (Python package manager)
- A Spotify Developer Account
- Git (optional, for cloning)

## Installation Methods

### 1. Using pip (Recommended)

```bash
pip install motify
```

### 2. From Source

1. Clone the repository:
```bash
git clone https://github.com/mosh3eb/motify.git
cd motify
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
.\venv\Scripts\activate   # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Using Docker

```bash
docker pull mosh3eb/motify
docker run -d \
  -v ${PWD}/downloads:/app/downloads \
  -v ${PWD}/app_config.json:/app/app_config.json \
  mosh3eb/motify
```

## Configuration

1. Create your Spotify Application:
   - Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Note your Client ID and Client Secret
   - Add `http://localhost:8888/callback` to Redirect URIs

2. Configure Motify:
   - Copy `app_config.example.json` to `app_config.json`
   - Add your Spotify credentials
   - Adjust other settings as needed
