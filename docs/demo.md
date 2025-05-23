# Motify Demo

Experience the power of Motify with our interactive demo. Try out the core features and see how easy it is to download and manage your Spotify music.

## 🎵 Live Demo

<div class="demo-container">
  <div class="demo-player">
    <div class="demo-track">
      <img src="../assets/images/screenshots/main-interface.png" alt="Demo Track" class="demo-track-image">
      <div class="demo-track-info">
        <h3>Sample Track</h3>
        <p>Artist Name</p>
      </div>
    </div>
    <div class="demo-controls">
      <button class="demo-button" onclick="showDemoMessage('Downloading...')">
        <span class="demo-icon">⬇️</span> Download
      </button>
      <button class="demo-button" onclick="showDemoMessage('Added to queue!')">
        <span class="demo-icon">➕</span> Queue
      </button>
    </div>
  </div>
</div>

## ✨ Key Features

<div class="grid features" markdown>

### 🎯 Easy Download
- One-click download
- Batch processing
- High-quality audio
- Metadata support

### 🎨 Beautiful Interface
- Modern design
- Dark/Light themes
- Responsive layout
- Intuitive controls

### 📱 Playlist Support
- Import playlists
- Queue management
- Download history
- Progress tracking

</div>

## 🚀 Try It Now

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

<script>
function showDemoMessage(message) {
  const demoContainer = document.querySelector('.demo-container');
  const messageElement = document.createElement('div');
  messageElement.className = 'demo-message';
  messageElement.textContent = message;
  
  demoContainer.appendChild(messageElement);
  
  setTimeout(() => {
    messageElement.remove();
  }, 2000);
}
</script>

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

.demo-player {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.demo-track {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  max-width: 400px;
}

.demo-track-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
}

.demo-track-info {
  flex: 1;
}

.demo-track-info h3 {
  margin: 0;
  color: var(--md-primary-fg-color);
}

.demo-track-info p {
  margin: 0.5rem 0 0;
  opacity: 0.8;
}

.demo-controls {
  display: flex;
  gap: 1rem;
}

.demo-button {
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

.demo-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
  
  .demo-track {
    flex-direction: column;
    text-align: center;
  }
  
  .demo-controls {
    flex-direction: column;
    width: 100%;
  }
  
  .demo-button {
    width: 100%;
    justify-content: center;
  }
}
</style> 