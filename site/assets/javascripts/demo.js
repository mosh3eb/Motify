class MotifyDemo {
    constructor() {
        this.searchInput = document.getElementById('search-input');
        this.searchButton = document.getElementById('search-button');
        this.resultsContainer = document.getElementById('search-results');
        this.previewPlayer = document.getElementById('preview-player');
        this.currentAudio = null;
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.searchButton.addEventListener('click', () => this.searchTracks());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchTracks();
        });
    }

    async searchTracks() {
        const query = this.searchInput.value.trim();
        if (!query) return;

        this.showLoading();
        try {
            const results = await this.searchSpotify(query);
            this.displayResults(results);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        }
    }

    async searchSpotify(query) {
        // Using Spotify's public API endpoint
        const response = await fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(query)}&type=track&limit=5`, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Search failed');
        }

        const data = await response.json();
        return data.tracks.items.map(track => ({
            id: track.id,
            title: track.name,
            artist: track.artists.map(artist => artist.name).join(', '),
            previewUrl: track.preview_url,
            image: track.album.images[0]?.url || 'assets/images/screenshots/main-interface.png'
        }));
    }

    displayResults(results) {
        this.resultsContainer.innerHTML = '';
        if (results.length === 0) {
            this.showError('No tracks found. Try a different search term.');
            return;
        }

        results.forEach(track => {
            const trackElement = this.createTrackElement(track);
            this.resultsContainer.appendChild(trackElement);
        });
    }

    createTrackElement(track) {
        const div = document.createElement('div');
        div.className = 'track-item';
        div.innerHTML = `
            <img src="${track.image}" alt="${track.title}" class="track-image">
            <div class="track-info">
                <h3>${track.title}</h3>
                <p>${track.artist}</p>
            </div>
            <div class="track-actions">
                <button class="preview-button" onclick="motifyDemo.previewTrack('${track.id}', '${track.previewUrl}', '${track.title}')">
                    <span class="demo-icon">▶️</span> Preview
                </button>
                <button class="download-button" onclick="motifyDemo.showUpgradeMessage()">
                    <span class="demo-icon">⬇️</span> Download
                </button>
            </div>
        `;
        return div;
    }

    previewTrack(trackId, previewUrl, title) {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }

        if (!previewUrl) {
            this.showMessage('Preview not available for this track');
            return;
        }

        // Create audio player if it doesn't exist
        if (!this.previewPlayer.querySelector('audio')) {
            const audio = document.createElement('audio');
            audio.controls = true;
            audio.className = 'preview-audio';
            this.previewPlayer.innerHTML = '';
            this.previewPlayer.appendChild(audio);
        }

        const audio = this.previewPlayer.querySelector('audio');
        audio.src = previewUrl;
        audio.play();
        this.currentAudio = audio;

        // Add track info
        const trackInfo = document.createElement('div');
        trackInfo.className = 'preview-info';
        trackInfo.innerHTML = `<h4>Now Playing: ${title}</h4>`;
        this.previewPlayer.appendChild(trackInfo);

        this.showMessage('Playing preview...');
    }

    showUpgradeMessage() {
        this.showMessage('Upgrade to full version to download tracks!');
    }

    showMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'demo-message';
        messageElement.textContent = message;
        document.body.appendChild(messageElement);
        
        setTimeout(() => {
            messageElement.remove();
        }, 2000);
    }

    showLoading() {
        this.resultsContainer.innerHTML = '<div class="loading">Searching...</div>';
    }

    showError(message) {
        this.resultsContainer.innerHTML = `<div class="error">${message}</div>`;
    }
}

// Initialize the demo when the page loads
window.addEventListener('load', () => {
    window.motifyDemo = new MotifyDemo();
}); 