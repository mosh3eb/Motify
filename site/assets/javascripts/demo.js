class MotifyDemo {
    constructor() {
        this.searchInput = document.getElementById('search-input');
        this.searchButton = document.getElementById('search-button');
        this.resultsContainer = document.getElementById('search-results');
        this.previewPlayer = document.getElementById('preview-player');
        this.currentAudio = null;
        
        // Debug log
        console.log('MotifyDemo initialized');
        
        if (!this.searchInput || !this.searchButton || !this.resultsContainer) {
            console.error('Required elements not found:', {
                searchInput: !!this.searchInput,
                searchButton: !!this.searchButton,
                resultsContainer: !!this.resultsContainer
            });
            return;
        }
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        console.log('Setting up event listeners');
        this.searchButton.addEventListener('click', () => {
            console.log('Search button clicked');
            this.searchTracks();
        });
        
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                console.log('Enter key pressed');
                this.searchTracks();
            }
        });
    }

    async searchTracks() {
        const query = this.searchInput.value.trim();
        console.log('Searching for:', query);
        
        if (!query) {
            this.showMessage('Please enter a search term');
            return;
        }

        this.showLoading();
        try {
            // For demo purposes, we'll use mock data instead of the Spotify API
            const mockResults = this.getMockResults(query);
            this.displayResults(mockResults);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        }
    }

    getMockResults(query) {
        // Mock data for demonstration
        return [
            {
                id: '1',
                title: 'Sample Track 1',
                artist: 'Artist 1',
                previewUrl: 'https://p.scdn.co/mp3-preview/1',
                image: 'https://i.scdn.co/image/ab67616d0000b273'
            },
            {
                id: '2',
                title: 'Sample Track 2',
                artist: 'Artist 2',
                previewUrl: 'https://p.scdn.co/mp3-preview/2',
                image: 'https://i.scdn.co/image/ab67616d0000b273'
            }
        ];
    }

    displayResults(results) {
        console.log('Displaying results:', results);
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
        console.log('Previewing track:', { trackId, title });
        
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
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
        audio.play().catch(error => {
            console.error('Error playing audio:', error);
            this.showMessage('Preview not available for this track');
        });
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
        console.log('Showing message:', message);
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
    console.log('Page loaded, initializing MotifyDemo');
    window.motifyDemo = new MotifyDemo();
}); 