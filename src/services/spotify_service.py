import re
import json
import os
import requests
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from src.utils.config import CREDENTIALS_FILE

class SpotifyService:
    """Service for interacting with Spotify API"""
    
    def __init__(self):
        self.spotify = None
        self.authenticated = False
        self._load_credentials()
    
    def _load_credentials(self):
        """Load saved credentials and initialize Spotify client"""
        try:
            if os.path.exists(CREDENTIALS_FILE):
                with open(CREDENTIALS_FILE, 'r') as f:
                    credentials = json.load(f)
                    
                if credentials and 'client_id' in credentials and 'client_secret' in credentials:
                    if credentials['client_id'] and credentials['client_secret']:
                        success = self.initialize(credentials['client_id'], credentials['client_secret'])
                        if success:
                            print("Successfully authenticated with Spotify API")
                        else:
                            print("Failed to authenticate with Spotify API using saved credentials")
                    else:
                        print("Spotify credentials are empty")
                else:
                    print("Spotify credentials file is invalid")
            else:
                print(f"Credentials file not found: {CREDENTIALS_FILE}")
        except Exception as e:
            print(f"Error loading Spotify credentials: {e}")
            self.authenticated = False
    
    def initialize(self, client_id, client_secret):
        """Initialize Spotify client with credentials"""
        try:
            self.spotify = Spotify(
                auth_manager=SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                ),
                requests_timeout=10
            )
            self.authenticated = True
            return True
        except Exception as e:
            print(f"Spotify authentication error: {e}")
            self.authenticated = False
            return False
    
    def save_credentials(self, client_id, client_secret):
        """Save Spotify API credentials"""
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump({'client_id': client_id, 'client_secret': client_secret}, f)
    
    def get_playlist_tracks(self, playlist_id):
        """Get tracks from a playlist"""
        if not self.authenticated:
            raise Exception("Spotify client not authenticated")
        
        tracks = []
        try:
            results = self.spotify.playlist_tracks(playlist_id)
            
            # Get initial batch of tracks
            for item in results['items']:
                if item['track']:
                    track_info = self._extract_track_info(item['track'])
                    if track_info:
                        tracks.append(track_info)
            
            # Handle pagination for large playlists
            while results['next']:
                results = self.spotify.next(results)
                for item in results['items']:
                    if item['track']:
                        track_info = self._extract_track_info(item['track'])
                        if track_info:
                            tracks.append(track_info)
            
            return tracks
        except Exception as e:
            print(f"Error fetching playlist tracks: {e}")
            return []
    
    def get_album_tracks(self, album_id):
        """Get tracks from an album"""
        if not self.authenticated:
            raise Exception("Spotify client not authenticated")
        
        tracks = []
        try:
            # Get album details first
            album = self.spotify.album(album_id)
            album_name = album['name']
            release_date = album['release_date']
            album_art_url = album['images'][0]['url'] if album['images'] else ''
            
            # Get album tracks
            results = self.spotify.album_tracks(album_id)
            
            # Get initial batch of tracks
            for item in results['items']:
                track_info = {
                    'name': item['name'],
                    'artist': ', '.join(artist['name'] for artist in item['artists']),
                    'album': album_name,
                    'album_art_url': album_art_url,
                    'duration_ms': item['duration_ms'],
                    'release_date': release_date,
                    'artists': item['artists'],
                    'track_number': item['track_number'],
                    'disc_number': item['disc_number'],
                    'is_explicit': item.get('explicit', False)
                }
                tracks.append(track_info)
            
            # Handle pagination
            while results['next']:
                results = self.spotify.next(results)
                for item in results['items']:
                    track_info = {
                        'name': item['name'],
                        'artist': ', '.join(artist['name'] for artist in item['artists']),
                        'album': album_name,
                        'album_art_url': album_art_url,
                        'duration_ms': item['duration_ms'],
                        'release_date': release_date,
                        'artists': item['artists'],
                        'track_number': item['track_number'],
                        'disc_number': item['disc_number'],
                        'is_explicit': item.get('explicit', False)
                    }
                    tracks.append(track_info)
            
            return tracks
        except Exception as e:
            print(f"Error fetching album tracks: {e}")
            return []
    
    def get_track(self, track_id):
        """Get a single track details"""
        if not self.authenticated:
            raise Exception("Spotify client not authenticated")
        
        try:
            track = self.spotify.track(track_id)
            return self._extract_track_info(track)
        except Exception as e:
            print(f"Error fetching track: {e}")
            return None
    
    def search_tracks(self, query, limit=10):
        """Search for tracks by query"""
        if not self.authenticated:
            raise Exception("Spotify client not authenticated")
        
        try:
            results = self.spotify.search(q=query, type='track', limit=limit)
            tracks = []
            
            for item in results['tracks']['items']:
                track_info = self._extract_track_info(item)
                if track_info:
                    tracks.append(track_info)
                    
            return tracks
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []
    
    def search_albums(self, query, limit=10):
        """Search for albums by query"""
        if not self.authenticated:
            raise Exception("Spotify client not authenticated")
        
        try:
            results = self.spotify.search(q=query, type='album', limit=limit)
            albums = []
            
            for item in results['albums']['items']:
                album_info = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': ', '.join(artist['name'] for artist in item['artists']),
                    'album_art_url': item['images'][0]['url'] if item['images'] else '',
                    'release_date': item['release_date'],
                    'total_tracks': item['total_tracks']
                }
                albums.append(album_info)
                    
            return albums
        except Exception as e:
            print(f"Error searching albums: {e}")
            return []
    
    def search_playlists(self, query, limit=10):
        """Search for playlists by query"""
        if not self.authenticated:
            raise Exception("Spotify client not authenticated")
        
        try:
            results = self.spotify.search(q=query, type='playlist', limit=limit)
            playlists = []
            
            for item in results['playlists']['items']:
                playlist_info = {
                    'id': item['id'],
                    'name': item['name'],
                    'owner': item['owner']['display_name'],
                    'image_url': item['images'][0]['url'] if item['images'] else '',
                    'total_tracks': item['tracks']['total']
                }
                playlists.append(playlist_info)
                    
            return playlists
        except Exception as e:
            print(f"Error searching playlists: {e}")
            return []
    
    def get_spotify_link_type(self, link):
        """Determine the type of Spotify link"""
        if 'album' in link:
            return 'album'
        elif 'track' in link:
            return 'track'
        elif 'playlist' in link:
            return 'playlist'
        else:
            return None
    
    def extract_id_from_link(self, link):
        """Extract the Spotify ID from a link"""
        # Handle links with query parameters
        if '?si=' in link:
            link = link.split('?si=')[0]  # Remove any query params
        
        # Use regex to find the ID in the URL
        match = re.search(r'(album|playlist|track)/([a-zA-Z0-9]{22})', link)
        if match:
            return match.group(2)  # Return the ID
        return None  # If no match found
    
    def is_valid_spotify_id(self, id_str):
        """Check if a string is a valid Spotify ID"""
        return bool(re.match(r'^[0-9A-Za-z]{22}$', id_str))
    
    def get_spotify_content(self, link):
        """Get content based on Spotify link type"""
        if not self.authenticated:
            raise Exception("Spotify client not authenticated")
        
        link_type = self.get_spotify_link_type(link)
        content_id = self.extract_id_from_link(link)
        
        if not content_id:
            print(f"Invalid Spotify link: {link}")
            return []
        
        if link_type == 'playlist':
            if not self.is_valid_spotify_id(content_id):
                print(f"Invalid playlist ID: {content_id}")
                return []
            return self.get_playlist_tracks(content_id)
        
        elif link_type == 'album':
            if not self.is_valid_spotify_id(content_id):
                print(f"Invalid album ID: {content_id}")
                return []
            return self.get_album_tracks(content_id)
        
        elif link_type == 'track':
            if not self.is_valid_spotify_id(content_id):
                print(f"Invalid track ID: {content_id}")
                return []
            track = self.get_track(content_id)
            return [track] if track else []
        
        else:
            print(f"Unsupported link type for: {link}")
            return []
    
    def _extract_track_info(self, track):
        """Extract relevant track information from Spotify API response"""
        if not track:
            return None
        
        try:
            return {
                'id': track['id'],
                'name': track['name'],
                'artist': ', '.join(artist['name'] for artist in track['artists']),
                'album': track['album']['name'],
                'album_art_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                'duration_ms': track['duration_ms'],
                'release_date': track['album']['release_date'],
                'artists': track['artists'],
                'track_number': track.get('track_number', 0),
                'disc_number': track.get('disc_number', 0),
                'is_explicit': track.get('explicit', False),
                'isrc': track.get('external_ids', {}).get('isrc', '')
            }
        except Exception as e:
            print(f"Error extracting track info: {e}")
            return None 