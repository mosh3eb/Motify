// Debug message to verify script loading
console.log('Demo.js script loaded');

class MotifyDemo {
    constructor() {
        console.log('Initializing MotifyDemo');
        
        // Get DOM elements
        this.searchInput = document.getElementById('search-input');
        this.searchButton = document.getElementById('search-button');
        this.resultsContainer = document.getElementById('search-results');
        this.previewPlayer = document.getElementById('preview-player');
        this.currentAudio = null;
        
        // Debug log element existence
        console.log('DOM Elements:', {
            searchInput: !!this.searchInput,
            searchButton: !!this.searchButton,
            resultsContainer: !!this.resultsContainer,
            previewPlayer: !!this.previewPlayer
        });
        
        if (!this.searchInput || !this.searchButton || !this.resultsContainer) {
            console.error('Required elements not found');
            return;
        }
        
        this.setupEventListeners();
        console.log('MotifyDemo initialized successfully');
    }

    setupEventListeners() {
        console.log('Setting up event listeners');
        
        // Search button click
        this.searchButton.addEventListener('click', () => {
            console.log('Search button clicked');
            this.searchTracks();
        });
        
        // Enter key press
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                console.log('Enter key pressed');
                this.searchTracks();
            }
        });
        
        console.log('Event listeners set up successfully');
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
            const results = this.getSampleTracks(query);
            console.log('Search results:', results);
            this.displayResults(results);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        }
    }

    getSampleTracks(query) {
        console.log('Getting sample tracks for query:', query);
        
        // Sample tracks that match the search query
        const allTracks = [
            {
                id: '1',
                title: 'Shape of You',
                artist: 'Ed Sheeran',
                previewUrl: 'https://p.scdn.co/mp3-preview/1',
                image: 'https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96'
            },
            {
                id: '2',
                title: 'Blinding Lights',
                artist: 'The Weeknd',
                previewUrl: 'https://p.scdn.co/mp3-preview/2',
                image: 'https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36'
            },
            {
                id: '3',
                title: 'Dance Monkey',
                artist: 'Tones and I',
                previewUrl: 'https://p.scdn.co/mp3-preview/3',
                image: 'https://i.scdn.co/image/ab67616d0000b2732e8ed79e177ff6011076f5f5'
            }
        ];

        // Filter tracks based on search query
        const filteredTracks = allTracks.filter(track => 
            track.title.toLowerCase().includes(query.toLowerCase()) ||
            track.artist.toLowerCase().includes(query.toLowerCase())
        );
        
        console.log('Filtered tracks:', filteredTracks);
        return filteredTracks;
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
        
        console.log('Results displayed successfully');
    }

    createTrackElement(track) {
        console.log('Creating track element:', track);
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
        console.log('Previewing track:', { trackId, title, previewUrl });
        
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
        console.log('Showing upgrade message');
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
        console.log('Showing loading state');
        this.resultsContainer.innerHTML = '<div class="loading">Searching...</div>';
    }

    showError(message) {
        console.log('Showing error:', message);
        this.resultsContainer.innerHTML = `<div class="error">${message}</div>`;
    }
}

// Initialize the demo when the page loads
window.addEventListener('load', () => {
    console.log('Page loaded, initializing MotifyDemo');
    window.motifyDemo = new MotifyDemo();
}); 