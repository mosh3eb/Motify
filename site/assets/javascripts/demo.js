class MotifyDemo {
    constructor() {
        this.searchInput = document.getElementById('search-input');
        this.searchButton = document.getElementById('search-button');
        this.resultsContainer = document.getElementById('search-results');
        this.previewPlayer = document.getElementById('preview-player');
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
            // Simulate API call with sample data
            const results = await this.mockSearchAPI(query);
            this.displayResults(results);
        } catch (error) {
            this.showError('Search failed. Please try again.');
        }
    }

    mockSearchAPI(query) {
        // Simulate API delay
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve([
                    {
                        id: '1',
                        title: 'Sample Track 1',
                        artist: 'Artist 1',
                        previewUrl: 'https://p.scdn.co/mp3-preview/1',
                        image: 'assets/images/screenshots/main-interface.png'
                    },
                    {
                        id: '2',
                        title: 'Sample Track 2',
                        artist: 'Artist 2',
                        previewUrl: 'https://p.scdn.co/mp3-preview/2',
                        image: 'assets/images/screenshots/main-interface.png'
                    },
                    {
                        id: '3',
                        title: 'Sample Track 3',
                        artist: 'Artist 3',
                        previewUrl: 'https://p.scdn.co/mp3-preview/3',
                        image: 'assets/images/screenshots/main-interface.png'
                    }
                ]);
            }, 1000);
        });
    }

    displayResults(results) {
        this.resultsContainer.innerHTML = '';
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
                <button class="preview-button" onclick="motifyDemo.previewTrack('${track.id}')">
                    <span class="demo-icon">▶️</span> Preview
                </button>
                <button class="download-button" onclick="motifyDemo.showUpgradeMessage()">
                    <span class="demo-icon">⬇️</span> Download
                </button>
            </div>
        `;
        return div;
    }

    previewTrack(trackId) {
        // In the full version, this would play the actual preview
        this.showMessage('Playing preview... (Demo Mode)');
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