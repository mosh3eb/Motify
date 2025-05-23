# Try Motify Demo

Experience the power of Motify with our interactive demo. Search for tracks and see how easy it is to manage your Spotify music.

## 🎵 Live Demo

<div class="demo-container">
  <div class="search-section">
    <div class="search-box">
      <input type="text" id="search-input" placeholder="Search for tracks..." class="search-input">
      <button id="search-button" class="search-button">
        <span class="demo-icon">🔍</span> Search
      </button>
    </div>
  </div>
  
  <div id="search-results" class="search-results">
    <!-- Search results will appear here -->
  </div>
  
  <div id="preview-player" class="preview-player">
    <!-- Preview player will appear here -->
  </div>
</div>

<script>
// Debug message to verify script loading
console.log('Demo page loaded');
</script>

<script src="../../site/assets/javascripts/demo.js"></script>

## ✨ Demo Features

<div class="grid features" markdown>

### 🔍 Search Tracks
- Search by track name or artist
- View track information
- See album artwork
- Sample tracks available:
  - Shape of You - Ed Sheeran
  - Blinding Lights - The Weeknd
  - Dance Monkey - Tones and I

### 🎵 Preview Music
- Click preview button to see how it works
- View track details
- See album artwork

### ⬇️ Download (Full Version)
- Get the full version to download tracks
- Download entire albums
- Download playlists
- High-quality audio
- Metadata support

</div>

## 🚀 Get the Full Version

```bash
# Install the full version
pip install motify-music

# Start using Motify
motify
```

[Get Started →](installation.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/mosh3eb/motify){ .md-button }

## 💡 Why Choose Motify?

- **Fast & Efficient**: Quick downloads with parallel processing
- **User-Friendly**: Intuitive interface for all users
- **Feature-Rich**: Advanced playlist management and metadata support
- **Open Source**: Free and open-source software

## 📱 Mobile Ready

Try the demo on your mobile device to experience the responsive design!

<style>
.demo-container {
  background: var(--md-card-bg-color);
  border-radius: var(--md-card-radius);
  padding: 2rem;
  margin: 2rem 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.search-section {
  margin-bottom: 2rem;
}

.search-box {
  display: flex;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.search-input {
  flex: 1;
  padding: 0.8rem 1.2rem;
  border: 2px solid var(--md-primary-fg-color);
  border-radius: 25px;
  font-size: 1rem;
  background: var(--md-default-bg-color);
  color: var(--md-default-fg-color);
}

.search-button {
  background: var(--md-primary-fg-color);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.search-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2rem;
}

.track-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--md-default-bg-color);
  border-radius: var(--md-card-radius);
  transition: all 0.3s ease;
}

.track-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.track-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
}

.track-info {
  flex: 1;
}

.track-info h3 {
  margin: 0;
  color: var(--md-primary-fg-color);
}

.track-info p {
  margin: 0.5rem 0 0;
  opacity: 0.8;
}

.track-actions {
  display: flex;
  gap: 0.5rem;
}

.preview-button,
.download-button {
  background: var(--md-primary-fg-color);
  color: white;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.preview-button:hover,
.download-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.preview-player {
  margin-top: 2rem;
  padding: 1rem;
  background: var(--md-default-bg-color);
  border-radius: var(--md-card-radius);
  text-align: center;
}

.preview-audio {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.preview-info {
  margin-top: 1rem;
  color: var(--md-primary-fg-color);
}

.preview-info h4 {
  margin: 0;
  font-size: 1.1rem;
}

.demo-icon {
  font-size: 1.2rem;
}

.demo-message {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--md-primary-fg-color);
  color: white;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-weight: 600;
  animation: slideUp 0.3s ease-out;
  z-index: 1000;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--md-primary-fg-color);
  font-weight: 600;
}

.error {
  text-align: center;
  padding: 2rem;
  color: #ff4444;
  font-weight: 600;
}

@keyframes slideUp {
  from {
    transform: translate(-50%, 100%);
    opacity: 0;
  }
  to {
    transform: translate(-50%, 0);
    opacity: 1;
  }
}

@media screen and (max-width: 480px) {
  .demo-container {
    padding: 1rem;
  }
  
  .search-box {
    flex-direction: column;
  }
  
  .search-button {
    width: 100%;
    justify-content: center;
  }
  
  .track-item {
    flex-direction: column;
    text-align: center;
  }
  
  .track-actions {
    width: 100%;
    justify-content: center;
  }
  
  .preview-audio {
    width: 100%;
  }
}
</style> 