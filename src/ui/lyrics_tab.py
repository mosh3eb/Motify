import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import requests
import re
import os
import time
from datetime import datetime
import yt_dlp
from bs4 import BeautifulSoup

class LyricsTab:
    """Tab for fetching and displaying song lyrics"""
    
    def __init__(self, parent, spotify_service, status_callback):
        self.parent = parent
        self.spotify_service = spotify_service
        self.status_callback = status_callback
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        
        # Store current track
        self.current_track = None
        
        # Synced lyrics variables
        self.synced_lyrics = []
        self.is_synced = False
        self.sync_running = False
        self.current_position = 0
        self.sync_thread = None
    
    def _create_widgets(self):
        """Create lyrics tab widgets"""
        # Search section
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(search_frame, text="Track Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.title_entry = ttk.Entry(search_frame)
        self.title_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.title_entry.bind("<Return>", lambda e: self.search_lyrics())
        
        ttk.Label(search_frame, text="Artist:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        
        self.artist_entry = ttk.Entry(search_frame)
        self.artist_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=(5, 0))
        self.artist_entry.bind("<Return>", lambda e: self.search_lyrics())
        
        search_button = ttk.Button(
            search_frame,
            text="Search Lyrics",
            command=self.search_lyrics,
            style="primary.TButton"
        )
        search_button.grid(row=0, column=2, rowspan=2, padx=5, pady=5)
        
        # Configure grid columns
        search_frame.columnconfigure(1, weight=1)
        
        # Spotify track section
        spotify_frame = ttk.LabelFrame(self.frame, text="Get Track from Spotify")
        spotify_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        ttk.Label(spotify_frame, text="Spotify URL:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.spotify_entry = ttk.Entry(spotify_frame)
        self.spotify_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=10)
        self.spotify_entry.bind("<Return>", lambda e: self.get_spotify_track())
        
        spotify_button = ttk.Button(
            spotify_frame,
            text="Get Track Info",
            command=self.get_spotify_track
        )
        spotify_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Configure grid columns
        spotify_frame.columnconfigure(1, weight=1)
        
        # YouTube section
        youtube_frame = ttk.LabelFrame(self.frame, text="Get Lyrics from YouTube")
        youtube_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        ttk.Label(youtube_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.youtube_entry = ttk.Entry(youtube_frame)
        self.youtube_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=10)
        self.youtube_entry.bind("<Return>", lambda e: self.get_youtube_track())
        
        youtube_button = ttk.Button(
            youtube_frame,
            text="Get Lyrics",
            command=self.get_youtube_track
        )
        youtube_button.grid(row=0, column=2, padx=5, pady=10)
        
        # Configure grid columns
        youtube_frame.columnconfigure(1, weight=1)
        
        # Lyrics display
        lyrics_frame = ttk.LabelFrame(self.frame, text="Lyrics")
        lyrics_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Lyrics text with scrollbar
        lyrics_text_frame = ttk.Frame(lyrics_frame)
        lyrics_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        lyrics_scroll = ttk.Scrollbar(lyrics_text_frame)
        lyrics_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lyrics_text = tk.Text(
            lyrics_text_frame,
            yscrollcommand=lyrics_scroll.set,
            wrap=tk.WORD,
            height=20,
            width=50
        )
        self.lyrics_text.pack(fill=tk.BOTH, expand=True)
        
        lyrics_scroll.config(command=self.lyrics_text.yview)
        
        # Lyrics actions
        actions_frame = ttk.Frame(lyrics_frame)
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        copy_button = ttk.Button(
            actions_frame,
            text="Copy Lyrics",
            command=self.copy_lyrics
        )
        copy_button.pack(side=tk.LEFT, padx=(0, 5))
        
        save_button = ttk.Button(
            actions_frame,
            text="Save as LRC",
            command=self.save_lyrics
        )
        save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_button = ttk.Button(
            actions_frame,
            text="Clear",
            command=self.clear_lyrics
        )
        clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # New buttons for synced lyrics
        load_lrc_button = ttk.Button(
            actions_frame,
            text="Load LRC",
            command=self.load_lrc_file
        )
        load_lrc_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.sync_button = ttk.Button(
            actions_frame,
            text="Start Sync",
            command=self.toggle_sync,
            style="success.TButton"
        )
        self.sync_button.pack(side=tk.LEFT)
        
        # Sync position slider
        sync_frame = ttk.Frame(lyrics_frame)
        sync_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(sync_frame, text="Position:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.position_var = tk.DoubleVar(value=0)
        self.position_slider = ttk.Scale(
            sync_frame,
            from_=0,
            to=300,  # 5 minutes default
            variable=self.position_var,
            command=self.update_position
        )
        self.position_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.time_label = ttk.Label(sync_frame, text="0:00")
        self.time_label.pack(side=tk.LEFT, padx=5)
        
        # Credits
        credits_label = ttk.Label(
            self.frame,
            text="Lyrics powered by AZLyrics, Genius, MusixMatch and YouTube",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        credits_label.pack(pady=(0, 10))
        
    def update_position(self, value=None):
        """Update the position display when slider is moved"""
        position = self.position_var.get()
        self.current_position = position
        minutes = int(position // 60)
        seconds = int(position % 60)
        self.time_label.config(text=f"{minutes}:{seconds:02d}")
        
        # If synced lyrics are available, highlight current line
        if self.is_synced and not self.sync_running:
            self.highlight_current_lyric(position)
    
    def highlight_current_lyric(self, position):
        """Highlight the current lyric based on position"""
        if not self.synced_lyrics:
            return
            
        # Find the current lyric line
        current_line = None
        next_line = None
        
        for i, (time_sec, text) in enumerate(self.synced_lyrics):
            if time_sec <= position:
                current_line = i
            if time_sec > position and next_line is None:
                next_line = i
                break
        
        if current_line is not None:
            # Clear previous highlights
            self.lyrics_text.tag_remove("current", "1.0", tk.END)
            
            # Highlight current line
            line_start = f"{current_line + 1}.0"
            line_end = f"{current_line + 2}.0"
            self.lyrics_text.tag_add("current", line_start, line_end)
            self.lyrics_text.tag_config("current", background="lightblue")
            
            # Ensure the line is visible
            self.lyrics_text.see(line_start)
    
    def toggle_sync(self):
        """Toggle synced lyrics playback"""
        if not self.is_synced:
            messagebox.showinfo("Synced Lyrics", "You need to load an LRC file first")
            return
            
        if self.sync_running:
            # Stop synced playback
            self.sync_running = False
            self.sync_button.config(text="Start Sync", style="success.TButton")
            if self.sync_thread and self.sync_thread.is_alive():
                self.sync_thread = None
        else:
            # Start synced playback
            self.sync_running = True
            self.sync_button.config(text="Stop Sync", style="danger.TButton")
            
            # Reset position if needed
            if self.current_position > 0:
                response = messagebox.askyesno("Resume Playback", 
                                             f"Resume from current position ({int(self.current_position // 60)}:{int(self.current_position % 60):02d})?\n\nSelect No to start from beginning.")
                if not response:
                    self.current_position = 0
                    self.position_var.set(0)
                    self.update_position()
            
            # Start synced playback thread
            self.sync_thread = threading.Thread(target=self.run_sync, daemon=True)
            self.sync_thread.start()
    
    def run_sync(self):
        """Run the synced lyrics playback"""
        start_time = time.time() - self.current_position
        
        try:
            while self.sync_running:
                # Calculate current position
                elapsed = time.time() - start_time
                self.current_position = elapsed
                
                # Update UI
                self.frame.after(0, self.position_var.set, elapsed)
                self.frame.after(0, self.update_position)
                self.frame.after(0, self.highlight_current_lyric, elapsed)
                
                # Sleep briefly
                time.sleep(0.1)
                
                # Check if reached the end
                if self.synced_lyrics and elapsed > self.synced_lyrics[-1][0] + 10:
                    # Stop 10 seconds after last lyric
                    self.frame.after(0, self.sync_button.invoke)
                    break
                    
        except Exception as e:
            print(f"Error in sync thread: {e}")
            self.frame.after(0, self.sync_button.invoke)
    
    def load_lrc_file(self):
        """Load and parse an LRC file"""
        file_path = filedialog.askopenfilename(
            title="Select LRC File",
            filetypes=[("LRC Files", "*.lrc"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            self.status_callback("Loading LRC file...", 50)
            
            # Clear previous content
            self.clear_lyrics()
            self.synced_lyrics = []
            
            # Parse LRC file
            with open(file_path, 'r', encoding='utf-8') as f:
                lrc_content = f.read()
                
            # Extract title and artist if available
            title_match = re.search(r'\[ti:(.*?)\]', lrc_content)
            artist_match = re.search(r'\[ar:(.*?)\]', lrc_content)
            
            if title_match:
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, title_match.group(1).strip())
                
            if artist_match:
                self.artist_entry.delete(0, tk.END)
                self.artist_entry.insert(0, artist_match.group(1).strip())
            
            # Parse time tags and lyrics
            lines = lrc_content.split('\n')
            plain_lyrics = []
            
            for line in lines:
                # Skip metadata or empty lines
                if not line or line.startswith('[') and (':' in line) and not re.match(r'\[\d', line):
                    continue
                    
                # Extract time tags and lyrics
                time_tags = re.findall(r'\[(\d+:\d+\.\d+)\]', line)
                
                if time_tags:
                    # Get the lyric text (everything after the last time tag)
                    lyric_text = re.sub(r'\[\d+:\d+\.\d+\]', '', line).strip()
                    
                    # Convert time tags to seconds
                    for time_tag in time_tags:
                        minutes, seconds = time_tag.split(':')
                        time_seconds = int(minutes) * 60 + float(seconds)
                        self.synced_lyrics.append((time_seconds, lyric_text))
                    
                    plain_lyrics.append(lyric_text)
                else:
                    # Line without time tags
                    plain_lyrics.append(line.strip())
            
            # Sort synced lyrics by time
            self.synced_lyrics.sort(key=lambda x: x[0])
            
            # Display plain lyrics in text widget
            for i, lyric in enumerate(plain_lyrics):
                self.lyrics_text.config(state=tk.NORMAL)
                self.lyrics_text.insert(tk.END, f"{lyric}\n")
            
            # Mark as synced lyrics
            self.is_synced = True
            self.status_callback("LRC file loaded", 100)
            
            # Update max time for slider
            if self.synced_lyrics:
                max_time = max(time for time, _ in self.synced_lyrics) + 30  # add buffer
                self.position_slider.config(to=max_time)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load LRC file: {e}")
            self.status_callback("Failed to load LRC file", 0)
    
    def search_lyrics(self):
        """Search for lyrics based on title and artist"""
        title = self.title_entry.get().strip()
        artist = self.artist_entry.get().strip()
        
        if not title:
            messagebox.showwarning("Input Error", "Please enter a track title")
            return
        
        # Clear previous lyrics
        self.clear_lyrics()
        
        # Update status
        self.status_callback("Searching for lyrics...", 50)
        
        # Create a dictionary to represent the current track
        self.current_track = {
            'name': title,
            'artist': artist
        }
        
        # Start search in background thread
        threading.Thread(
            target=self._fetch_lyrics,
            args=(title, artist),
            daemon=True
        ).start()
    
    def get_spotify_track(self):
        """Get track information from Spotify URL"""
        spotify_url = self.spotify_entry.get().strip()
        
        if not spotify_url:
            messagebox.showwarning("Input Error", "Please enter a Spotify URL")
            return
        
        if not self.spotify_service.authenticated:
            messagebox.showerror(
                "Authentication Error",
                "Spotify API not authenticated. Please provide valid credentials in Settings."
            )
            return
        
        # Update status
        self.status_callback("Fetching track from Spotify...", 50)
        
        try:
            # Get track info from Spotify
            link_type = self.spotify_service.get_spotify_link_type(spotify_url)
            
            if link_type != 'track':
                messagebox.showwarning(
                    "Invalid Link",
                    "Please provide a Spotify track link. Album and playlist links are not supported."
                )
                self.status_callback("Invalid Spotify link", 0)
                return
            
            track_id = self.spotify_service.extract_id_from_link(spotify_url)
            if not track_id:
                self.status_callback("Could not extract track ID", 0)
                return
            
            track = self.spotify_service.get_track(track_id)
            if not track:
                self.status_callback("Could not fetch track", 0)
                return
            
            # Update track info fields
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, track['name'])
            
            self.artist_entry.delete(0, tk.END)
            self.artist_entry.insert(0, track['artist'])
            
            # Set current track
            self.current_track = track
            
            # Update status
            self.status_callback(f"Loaded: {track['name']} by {track['artist']}", 100)
            
            # Automatically search for lyrics
            self.search_lyrics()
            
        except Exception as e:
            messagebox.showerror("Spotify Error", f"Error fetching track: {e}")
            self.status_callback("Error fetching track", 0)
    
    def get_youtube_track(self):
        """Get lyrics for a YouTube video"""
        youtube_url = self.youtube_entry.get().strip()
        
        if not youtube_url:
            messagebox.showwarning("Input Error", "Please enter a YouTube URL")
            return
            
        # Check if URL is valid
        if not re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+', youtube_url):
            messagebox.showwarning("Invalid URL", "Please enter a valid YouTube URL")
            return
            
        # Update status
        self.status_callback("Fetching info from YouTube...", 50)
        
        # Start in background thread
        threading.Thread(
            target=self._process_youtube_url,
            args=(youtube_url,),
            daemon=True
        ).start()
    
    def _process_youtube_url(self, url):
        """Process YouTube URL in background thread"""
        try:
            # Configure yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            # Get video info
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    self.frame.after(0, messagebox.showwarning, "Error", "Could not fetch video information")
                    self.frame.after(0, self.status_callback, "Failed to fetch video info", 0)
                    return
                
                # Get video details
                title = info.get('title', '')
                uploader = info.get('uploader', '')
                description = info.get('description', '')
                
                # Update UI in main thread
                self.frame.after(0, self._update_youtube_track_info, title, uploader, description)
                
        except Exception as e:
            print(f"Error processing YouTube URL: {e}")
            self.frame.after(0, messagebox.showerror, "Error", f"Failed to process YouTube URL: {e}")
            self.frame.after(0, self.status_callback, "Error processing YouTube URL", 0)
    
    def _update_youtube_track_info(self, title, uploader, description):
        """Update track info with YouTube data"""
        if title:
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, title)
            
        if uploader:
            self.artist_entry.delete(0, tk.END)
            self.artist_entry.insert(0, uploader)
            
        # Create track object
        self.current_track = {
            'name': title,
            'artist': uploader,
            'album': 'YouTube Video',
            'youtube_url': self.youtube_entry.get().strip()
        }
        
        # Check if description has lyrics
        if description and self._is_likely_lyrics(description, title, uploader):
            lyrics = self._clean_lyrics(description)
            self._update_lyrics_text(lyrics)
            self.status_callback("Lyrics found in video description", 100)
        else:
            # If no lyrics in description, search for lyrics
            self.search_lyrics()
    
    def _fetch_lyrics(self, title, artist):
        """Fetch lyrics from various sources in background thread"""
        try:
            # Reset synced lyrics state
            self.is_synced = False
            self.synced_lyrics = []
            
            # Try different lyrics sources
            lyrics = self._fetch_from_azlyrics(title, artist)
            
            if not lyrics:
                lyrics = self._fetch_from_genius(title, artist)
            
            if not lyrics:
                lyrics = self._fetch_from_musixmatch(title, artist)
                
            if not lyrics:
                # Try searching YouTube for lyrics
                lyrics = self._fetch_from_youtube(title, artist)
            
            # Update UI in main thread
            self.frame.after(0, self._update_lyrics_text, lyrics)
            
            if lyrics:
                self.frame.after(0, self.status_callback, "Lyrics found", 100)
            else:
                self.frame.after(0, self.status_callback, "Lyrics not found", 0)
                self.frame.after(0, messagebox.showinfo, "Lyrics Not Found", 
                               f"Could not find lyrics for {title} by {artist}")
            
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            self.frame.after(0, self.status_callback, "Error fetching lyrics", 0)
    
    def _update_lyrics_text(self, lyrics):
        """Update lyrics text widget with fetched lyrics"""
        if not lyrics:
            return
        
        # Enable text widget for editing
        self.lyrics_text.config(state=tk.NORMAL)
        
        # Clear existing content
        self.lyrics_text.delete(1.0, tk.END)
        
        # Insert lyrics
        self.lyrics_text.insert(tk.END, lyrics)
        
        # Disable editing
        self.lyrics_text.config(state=tk.DISABLED)
        
        # Scroll to top
        self.lyrics_text.see("1.0")
        
    def _fetch_from_azlyrics(self, title, artist):
        """Fetch lyrics from AZLyrics"""
        try:
            # Format artist and title for URL
            artist = artist.lower().replace(' ', '').replace('.', '')
            title = title.lower().replace(' ', '').replace('.', '')
            
            # Build AZLyrics URL
            url = f"https://www.azlyrics.com/lyrics/{artist}/{title}.html"
            
            # Make request
            response = requests.get(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code != 200:
                return None
            
            # Extract lyrics using regex
            content = response.text
            lyrics_match = re.search(r'<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->(.*?)<!-- MxM banner -->', content, re.DOTALL)
            
            if not lyrics_match:
                return None
            
            lyrics = lyrics_match.group(1).strip()
            lyrics = re.sub(r'<[^>]+>', '', lyrics)  # Remove HTML tags
            lyrics = lyrics.replace('\r', '').strip()
            
            return lyrics
            
        except Exception as e:
            print(f"AZLyrics error: {e}")
            return None
    
    def _fetch_from_genius(self, title, artist):
        """Fetch lyrics from Genius"""
        try:
            # Format search query
            search_query = f"{title} {artist}"
            
            # Search for song
            search_url = "https://genius.com/api/search/multi"
            response = requests.get(
                search_url,
                params={'q': search_query},
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code != 200:
                return None
            
            # Parse response
            data = response.json()
            
            # Find first song hit
            song_hit = None
            for section in data.get('response', {}).get('sections', []):
                if section.get('type') == 'song':
                    hits = section.get('hits', [])
                    if hits:
                        song_hit = hits[0].get('result')
                        break
            
            if not song_hit:
                return None
            
            # Get song URL
            song_url = song_hit.get('url')
            
            if not song_url:
                return None
            
            # Fetch song page
            response = requests.get(
                song_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code != 200:
                return None
            
            # Extract lyrics
            content = response.text
            lyrics_match = re.search(r'<div class="lyrics">(.+?)</div>', content, re.DOTALL)
            
            if not lyrics_match:
                # Try alternative pattern
                lyrics_match = re.search(r'<div data-lyrics-container.*?>(.+?)</div>', content, re.DOTALL)
            
            if not lyrics_match:
                return None
            
            lyrics = lyrics_match.group(1).strip()
            lyrics = re.sub(r'<[^>]+>', '', lyrics)  # Remove HTML tags
            lyrics = lyrics.replace('\r', '').strip()
            
            return lyrics
            
        except Exception as e:
            print(f"Genius error: {e}")
            return None
    
    def _fetch_from_musixmatch(self, title, artist):
        """Fetch lyrics from MusixMatch"""
        try:
            # Format search query
            search_query = f"{title} {artist}"
            
            # Search for song
            search_url = "https://www.musixmatch.com/search"
            response = requests.get(
                search_url,
                params={'q': search_query},
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code != 200:
                return None
            
            # Parse response to find song URL
            content = response.text
            url_match = re.search(r'<a class="title" href="(.*?)"', content)
            
            if not url_match:
                return None
            
            song_path = url_match.group(1)
            song_url = f"https://www.musixmatch.com{song_path}"
            
            # Fetch song page
            response = requests.get(
                song_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code != 200:
                return None
            
            # Extract lyrics
            content = response.text
            lyrics_blocks = re.findall(r'<span class="lyrics__content__ok">(.*?)</span>', content, re.DOTALL)
            
            if not lyrics_blocks:
                return None
            
            lyrics = '\n'.join(lyrics_blocks)
            lyrics = re.sub(r'<[^>]+>', '', lyrics)  # Remove HTML tags
            lyrics = lyrics.replace('\r', '').strip()
            
            return lyrics
            
        except Exception as e:
            print(f"MusixMatch error: {e}")
            return None
    
    def _fetch_from_youtube(self, title, artist):
        """Fetch lyrics from YouTube video descriptions and comments"""
        try:
            self.status_callback(f"Searching YouTube for lyrics...", 50)
            
            # Search for lyrics video
            search_query = f"{title} {artist} lyrics"
            
            # Configure yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': False,
                'max_downloads': 3
            }
            
            # Search YouTube
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get search results
                info = ydl.extract_info(f"ytsearch3:{search_query}", download=False)
                
                if not info or 'entries' not in info or not info['entries']:
                    return None
                
                # Try each result
                for entry in info['entries']:
                    video_id = entry.get('id')
                    if not video_id:
                        continue
                    
                    # Get full info for the video
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    # Get detailed info for this video
                    video_info = ydl.extract_info(video_url, download=False)
                    
                    if not video_info:
                        continue
                    
                    description = video_info.get('description', '')
                    
                    # Check if description looks like lyrics
                    if self._is_likely_lyrics(description, title, artist):
                        # Clean up the lyrics
                        lyrics = self._clean_lyrics(description)
                        
                        # Found lyrics
                        return lyrics
                    
                    # Try to find lyrics in comments (requires selenium or similar, simplified here)
                    # This would need a full implementation with Selenium for real usage
                    
            return None
                
        except Exception as e:
            print(f"Error fetching lyrics from YouTube: {e}")
            return None
            
    def _is_likely_lyrics(self, text, title, artist):
        """Check if text is likely to be lyrics"""
        if not text or len(text) < 100:
            return False
            
        # Convert to lowercase for comparison
        text_lower = text.lower()
        title_lower = title.lower()
        artist_lower = artist.lower()
        
        # Check if text contains title and artist
        if title_lower not in text_lower and artist_lower not in text_lower:
            return False
            
        # Check for lyrics markers
        lyrics_markers = ['lyrics', 'verse', 'chorus', '[verse]', '[chorus]', 'bridge']
        if not any(marker in text_lower for marker in lyrics_markers):
            # Check common lyrics patterns (lines with few words, many line breaks)
            lines = text.split('\n')
            if len(lines) < 10:
                return False
                
            # Count short lines (lyrics are typically short lines)
            short_lines = [line for line in lines if 1 <= len(line.split()) <= 10]
            if len(short_lines) < len(lines) * 0.5:  # At least 50% should be short lines
                return False
                
        return True
        
    def _clean_lyrics(self, text):
        """Clean up lyrics text from YouTube"""
        # Remove common non-lyrics content
        lines = text.split('\n')
        cleaned_lines = []
        
        skip_markers = ['subscribe', 'http', 'www.', '.com', 'copyright', 'lyrics provided by', 
                       'captions', 'subtitles', '@', '#']
        
        section_active = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines at the beginning
            if not line and not cleaned_lines:
                continue
                
            # Skip lines with skip markers
            if any(marker in line.lower() for marker in skip_markers):
                continue
                
            # Try to detect start of lyrics section
            if not section_active and ('lyrics' in line.lower() or '[' in line):
                section_active = True
                
            # Add line if we're in the lyrics section or haven't figured it out yet
            if section_active or len(cleaned_lines) < 2:
                cleaned_lines.append(line)
                
        return '\n'.join(cleaned_lines)
    
    def copy_lyrics(self):
        """Copy lyrics to clipboard"""
        lyrics = self.lyrics_text.get(1.0, tk.END).strip()
        if not lyrics:
            messagebox.showinfo("Copy", "No lyrics to copy")
            return
        
        self.frame.clipboard_clear()
        self.frame.clipboard_append(lyrics)
        self.status_callback("Lyrics copied to clipboard", 100)
    
    def save_lyrics(self):
        """Save lyrics as LRC file"""
        if not self.current_track:
            messagebox.showwarning("Save Error", "No track information available")
            return
        
        lyrics = self.lyrics_text.get(1.0, tk.END).strip()
        if not lyrics:
            messagebox.showinfo("Save", "No lyrics to save")
            return
        
        # Default filename
        default_filename = f"{self.current_track['name']} - {self.current_track['artist']}.lrc"
        default_filename = re.sub(r'[<>:"/\\|?*]', '_', default_filename)  # Remove invalid chars
        
        file_path = filedialog.asksaveasfilename(
            title="Save Lyrics",
            defaultextension=".lrc",
            initialfile=default_filename,
            filetypes=[("LRC Files", "*.lrc"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # If we have synced lyrics, save those with timestamps
            if self.is_synced and self.synced_lyrics:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Write metadata
                    f.write(f"[ti:{self.current_track['name']}]\n")
                    f.write(f"[ar:{self.current_track['artist']}]\n")
                    f.write(f"[al:{self.current_track.get('album', 'Unknown Album')}]\n")
                    f.write(f"[by:Motify App]\n")
                    f.write(f"[re:Motify App]\n")
                    f.write(f"[ve:1.0]\n\n")
                    
                    # Sort by time and write lyrics with timestamps
                    sorted_lyrics = sorted(self.synced_lyrics, key=lambda x: x[0])
                    for time_sec, text in sorted_lyrics:
                        minutes = int(time_sec // 60)
                        seconds = time_sec % 60
                        f.write(f"[{minutes:02d}:{seconds:06.3f}]{text}\n")
            else:
                # For regular lyrics, just create a simple LRC with metadata
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Write metadata
                    f.write(f"[ti:{self.current_track['name']}]\n")
                    f.write(f"[ar:{self.current_track['artist']}]\n")
                    f.write(f"[al:{self.current_track.get('album', 'Unknown Album')}]\n")
                    f.write(f"[by:Motify App]\n")
                    f.write(f"[re:Motify App]\n")
                    f.write(f"[ve:1.0]\n\n")
                    
                    # Write plain lyrics
                    for line in lyrics.split('\n'):
                        if line.strip():
                            f.write(f"{line}\n")
            
            self.status_callback(f"Lyrics saved to {os.path.basename(file_path)}", 100)
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save lyrics: {e}")
            self.status_callback("Failed to save lyrics", 0)
    
    def clear_lyrics(self):
        """Clear lyrics display"""
        self.lyrics_text.config(state=tk.NORMAL)
        self.lyrics_text.delete(1.0, tk.END)
        self.lyrics_text.config(state=tk.DISABLED)
        
        # Reset synced lyrics
        self.synced_lyrics = []
        self.is_synced = False
        
        # Reset position
        self.current_position = 0
        self.position_var.set(0)
        self.update_position()
        
        # Reset sync button
        self.sync_running = False
        self.sync_button.config(text="Start Sync", style="success.TButton")
        
        # Stop sync thread if running
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread = None 