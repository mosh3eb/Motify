import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import re
import os
import yt_dlp
from mutagen.mp4 import MP4, MP4Cover
import requests
from src.utils.config import get_app_config
import time
import traceback

class YouTubeTab:
    """Tab for downloading from YouTube links directly"""
    
    def __init__(self, parent, download_manager, status_callback):
        self.parent = parent
        self.download_manager = download_manager
        self.status_callback = status_callback
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        
        # Download progress
        self.is_downloading = False
        self.stop_download = False
    
    def _create_widgets(self):
        """Create YouTube tab widgets"""
        # Tab notebook for different views
        self.tab_notebook = ttk.Notebook(self.frame)
        self.tab_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Direct URL tab
        direct_url_frame = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(direct_url_frame, text="Direct URL")
        self._create_direct_url_tab(direct_url_frame)
        
        # Search tab
        search_frame = ttk.Frame(self.tab_notebook)
        self.tab_notebook.add(search_frame, text="Search")
        self._create_search_tab(search_frame)
    
    def _create_direct_url_tab(self, parent):
        """Create the direct URL tab content"""
        # URL input section
        url_frame = ttk.LabelFrame(parent, text="YouTube URL")
        url_frame.pack(padx=10, pady=10, fill=tk.X)
        
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(url_input_frame, text="Video URL:").pack(side=tk.LEFT)
        
        self.url_entry = ttk.Entry(url_input_frame)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.url_entry.bind("<Return>", lambda e: self.fetch_video_info())
        
        fetch_button = ttk.Button(
            url_input_frame,
            text="Fetch Info",
            command=self.fetch_video_info
        )
        fetch_button.pack(side=tk.RIGHT)
        
        # Video info section
        info_frame = ttk.LabelFrame(parent, text="Video Information")
        info_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.info_text = tk.Text(
            info_frame,
            height=5,
            width=50,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.info_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Download options section
        options_frame = ttk.LabelFrame(parent, text="Download Options")
        options_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Format options
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(format_frame, text="Format:").grid(row=0, column=0, sticky=tk.W)
        
        self.format_var = tk.StringVar(value="m4a")
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=["m4a", "mp3", "wav", "flac"],
            state="readonly",
            width=10
        )
        format_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(format_frame, text="Quality:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        
        self.quality_var = tk.StringVar(value="high")
        quality_combo = ttk.Combobox(
            format_frame,
            textvariable=self.quality_var,
            values=["low", "medium", "high", "best"],
            state="readonly",
            width=10
        )
        quality_combo.grid(row=0, column=3, padx=5, sticky=tk.W)
        
        # Metadata options
        metadata_frame = ttk.Frame(options_frame)
        metadata_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Title
        ttk.Label(metadata_frame, text="Title:").grid(row=0, column=0, sticky=tk.W)
        
        self.title_entry = ttk.Entry(metadata_frame)
        self.title_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        # Artist
        ttk.Label(metadata_frame, text="Artist:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        self.artist_entry = ttk.Entry(metadata_frame)
        self.artist_entry.grid(row=1, column=1, padx=5, pady=(5, 0), sticky=tk.EW)
        
        # Album
        ttk.Label(metadata_frame, text="Album:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        
        self.album_entry = ttk.Entry(metadata_frame)
        self.album_entry.grid(row=0, column=3, padx=5, sticky=tk.EW)
        
        # Year
        ttk.Label(metadata_frame, text="Year:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=(5, 0))
        
        self.year_entry = ttk.Entry(metadata_frame, width=10)
        self.year_entry.grid(row=1, column=3, padx=5, pady=(5, 0), sticky=tk.W)
        
        # Configure grid columns
        metadata_frame.columnconfigure(1, weight=1)
        metadata_frame.columnconfigure(3, weight=1)
        
        # Extra options
        extra_frame = ttk.Frame(options_frame)
        extra_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Extract audio only
        self.audio_only_var = tk.BooleanVar(value=True)
        audio_only_check = ttk.Checkbutton(
            extra_frame,
            text="Audio Only",
            variable=self.audio_only_var
        )
        audio_only_check.pack(side=tk.LEFT)
        
        # Embed thumbnail
        self.embed_thumbnail_var = tk.BooleanVar(value=True)
        embed_thumbnail_check = ttk.Checkbutton(
            extra_frame,
            text="Embed Thumbnail",
            variable=self.embed_thumbnail_var
        )
        embed_thumbnail_check.pack(side=tk.LEFT, padx=20)
        
        # Download to custom location
        self.custom_location_var = tk.BooleanVar(value=False)
        custom_location_check = ttk.Checkbutton(
            extra_frame,
            text="Custom Location",
            variable=self.custom_location_var,
            command=self._toggle_location_entry
        )
        custom_location_check.pack(side=tk.LEFT)
        
        # Custom location entry
        location_frame = ttk.Frame(options_frame)
        location_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.location_entry = ttk.Entry(location_frame, state=tk.DISABLED)
        self.location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(
            location_frame,
            text="Browse",
            command=self._browse_location,
            state=tk.DISABLED
        )
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Download section
        download_frame = ttk.Frame(parent)
        download_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.download_button = ttk.Button(
            download_frame,
            text="Download",
            command=self.start_download,
            style="success.TButton",
            state=tk.DISABLED
        )
        self.download_button.pack(side=tk.LEFT)
        
        self.cancel_button = ttk.Button(
            download_frame,
            text="Cancel",
            command=self.cancel_download,
            style="danger.TButton",
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Queue button
        self.queue_button = ttk.Button(
            download_frame,
            text="Add to Queue",
            command=self.add_to_queue,
            state=tk.DISABLED
        )
        self.queue_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Progress bar
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            mode="determinate",
            length=100
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack(pady=(5, 0))
    
    def _create_search_tab(self, parent):
        """Create the search tab content"""
        # Search section
        search_frame = ttk.Frame(parent)
        search_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_youtube())
        
        search_button = ttk.Button(
            search_frame,
            text="Search",
            command=self.search_youtube,
            style="primary.TButton"
        )
        search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Filter options
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.music_only_var = tk.BooleanVar(value=True)
        music_only_check = ttk.Checkbutton(
            filter_frame,
            text="Music Only",
            variable=self.music_only_var
        )
        music_only_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.lyrics_only_var = tk.BooleanVar(value=False)
        lyrics_only_check = ttk.Checkbutton(
            filter_frame,
            text="With Lyrics",
            variable=self.lyrics_only_var
        )
        lyrics_only_check.pack(side=tk.LEFT)
        
        # Results frame with notebook
        results_frame = ttk.LabelFrame(parent, text="Search Results")
        results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Results notebook
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Videos tab
        videos_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(videos_frame, text="Videos")
        
        # Scrollbar for videos list
        videos_scroll = ttk.Scrollbar(videos_frame)
        videos_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Videos listbox
        self.videos_listbox = tk.Listbox(
            videos_frame,
            selectmode=tk.SINGLE,
            yscrollcommand=videos_scroll.set,
            height=10
        )
        self.videos_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.videos_listbox.bind("<<ListboxSelect>>", self.on_video_selected)
        
        videos_scroll.config(command=self.videos_listbox.yview)
        
        # Lyrics tab
        lyrics_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(lyrics_frame, text="Lyrics")
        
        # Lyrics text with scrollbar
        lyrics_scroll = ttk.Scrollbar(lyrics_frame)
        lyrics_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lyrics_text = tk.Text(
            lyrics_frame,
            yscrollcommand=lyrics_scroll.set,
            wrap=tk.WORD,
            height=10,
            width=50
        )
        self.lyrics_text.pack(fill=tk.BOTH, expand=True)
        
        lyrics_scroll.config(command=self.lyrics_text.yview)
        
        # Video details tab
        details_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(details_frame, text="Details")
        
        # Video info
        self.details_text = tk.Text(
            details_frame,
            wrap=tk.WORD,
            height=10,
            width=50
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Actions frame
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.play_button = ttk.Button(
            actions_frame,
            text="Play",
            command=self.play_video,
            state=tk.DISABLED
        )
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.download_search_button = ttk.Button(
            actions_frame,
            text="Download",
            command=self.download_selected,
            style="success.TButton",
            state=tk.DISABLED
        )
        self.download_search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.queue_search_button = ttk.Button(
            actions_frame,
            text="Add to Queue",
            command=self.queue_selected,
            state=tk.DISABLED
        )
        self.queue_search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.view_lyrics_button = ttk.Button(
            actions_frame,
            text="View Lyrics",
            command=self.view_lyrics,
            state=tk.DISABLED
        )
        self.view_lyrics_button.pack(side=tk.LEFT)
        
        # Store search results
        self.search_results = []
    
    def _toggle_location_entry(self):
        """Toggle custom location entry based on checkbox"""
        if self.custom_location_var.get():
            self.location_entry.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.NORMAL)
        else:
            self.location_entry.config(state=tk.DISABLED)
            self.browse_button.config(state=tk.DISABLED)
    
    def _browse_location(self):
        """Browse for custom download location"""
        folder = filedialog.askdirectory(
            title="Select Download Folder"
        )
        
        if folder:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, folder)
    
    def fetch_video_info(self):
        """Fetch video information from YouTube URL"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Input Error", "Please enter a YouTube URL")
            return
        
        # Validate URL
        if not self._is_valid_youtube_url(url):
            messagebox.showwarning("Invalid URL", "Please enter a valid YouTube URL")
            return
        
        # Update status
        self.status_callback("Fetching video information...", 50)
        self.status_label.config(text="Fetching video information...")
        
        # Disable UI during fetch
        self._set_ui_state(tk.DISABLED)
        
        # Start fetch in background thread
        threading.Thread(
            target=self._fetch_video_info_thread,
            args=(url,),
            daemon=True
        ).start()
    
    def _fetch_video_info_thread(self, url):
        """Background thread for fetching video info"""
        try:
            # Configure yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'force_generic_extractor': False
            }
            
            # Extract info
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            # Update UI in main thread
            self.frame.after(0, self._update_video_info, info)
            self.frame.after(0, self.status_callback, "Video information fetched", 100)
            self.frame.after(0, self.status_label.config, {"text": "Video information fetched"})
            
        except Exception as e:
            error_msg = str(e)
            self.frame.after(0, messagebox.showerror, "Error", f"Error fetching video info: {error_msg}")
            self.frame.after(0, self.status_callback, "Error fetching video info", 0)
            self.frame.after(0, self.status_label.config, {"text": "Error fetching video info"})
        
        # Re-enable UI
        self.frame.after(0, self._set_ui_state, tk.NORMAL)
    
    def _update_video_info(self, info):
        """Update UI with fetched video info"""
        if not info:
            return
        
        # Extract info
        title = info.get('title', '')
        uploader = info.get('uploader', '')
        duration = info.get('duration', 0)
        
        # Format duration
        duration_str = self._format_duration(duration)
        
        # Update info text
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"Title: {title}\n")
        self.info_text.insert(tk.END, f"Uploader: {uploader}\n")
        self.info_text.insert(tk.END, f"Duration: {duration_str}")
        self.info_text.config(state=tk.DISABLED)
        
        # Pre-fill metadata fields
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)
        
        self.artist_entry.delete(0, tk.END)
        self.artist_entry.insert(0, uploader)
        
        # Extract year if available
        upload_date = info.get('upload_date', '')
        if upload_date and len(upload_date) >= 4:
            year = upload_date[:4]
            self.year_entry.delete(0, tk.END)
            self.year_entry.insert(0, year)
        
        # Enable download buttons
        self.download_button.config(state=tk.NORMAL)
        self.queue_button.config(state=tk.NORMAL)
    
    def _format_duration(self, seconds):
        """Format duration in seconds to HH:MM:SS"""
        if not seconds:
            return "00:00"
        
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def start_download(self):
        """Start downloading YouTube video"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Input Error", "Please enter a YouTube URL")
            return
        
        if self.is_downloading:
            messagebox.showinfo("Download in Progress", "A download is already in progress")
            return
        
        # Get download options
        audio_format = self.format_var.get()
        quality = self.quality_var.get()
        audio_only = self.audio_only_var.get()
        embed_thumbnail = self.embed_thumbnail_var.get()
        custom_location = self.custom_location_var.get()
        
        # Get custom location if enabled
        download_path = None
        if custom_location:
            download_path = self.location_entry.get().strip()
            if not download_path:
                messagebox.showwarning("Location Error", "Please specify a download location")
                return
            
            if not os.path.exists(download_path):
                try:
                    os.makedirs(download_path)
                except Exception as e:
                    messagebox.showerror("Folder Error", f"Error creating folder: {e}")
                    return
        
        # Get metadata
        metadata = {
            'title': self.title_entry.get().strip(),
            'artist': self.artist_entry.get().strip(),
            'album': self.album_entry.get().strip(),
            'year': self.year_entry.get().strip()
        }
        
        # Map quality to bitrate
        quality_map = {
            'low': '128',
            'medium': '192',
            'high': '256',
            'best': '320'
        }
        bitrate = quality_map.get(quality, '192')
        
        # Update UI
        self.status_callback("Starting download...", 0)
        self.status_label.config(text="Starting download...")
        self.progress_var.set(0)
        
        # Set download state
        self.is_downloading = True
        self.stop_download = False
        
        # Update UI buttons
        self.download_button.config(state=tk.DISABLED)
        self.queue_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        
        # Start download in background thread
        threading.Thread(
            target=self._download_thread,
            args=(url, audio_format, bitrate, audio_only, embed_thumbnail, download_path, metadata),
            daemon=True
        ).start()
    
    def _download_thread(self, url, audio_format, bitrate, audio_only, embed_thumbnail, download_path, metadata):
        """Background thread for downloading"""
        try:
            # Configure postprocessors
            postprocessors = []
            
            if audio_only:
                # Audio extraction postprocessor
                postprocessors.append({
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': bitrate,
                })
            
            if embed_thumbnail:
                # Thumbnail embedding postprocessor
                postprocessors.append({
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False,
                })
            
            # Metadata postprocessor
            postprocessors.append({
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            })
            
            # Set output template
            if metadata['title'] and metadata['artist']:
                # Use custom title and artist if provided
                output_template = f"{metadata['artist']} - {metadata['title']}.%(ext)s"
                # Clean filename
                output_template = output_template.replace('/', '_').replace('\\', '_')
            else:
                # Use default template
                output_template = "%(title)s.%(ext)s"
            
            # Set download path
            if download_path:
                output_template = os.path.join(download_path, output_template)
            else:
                # Use default or custom downloads folder from config
                config = get_app_config()
                download_folder = config.get('custom_download_folder', 'downloads')
                
                # Create folder if it doesn't exist
                if not os.path.exists(download_folder):
                    try:
                        os.makedirs(download_folder, exist_ok=True)
                    except Exception as e:
                        self.frame.after(0, messagebox.showerror, "Folder Error", f"Error creating download folder: {e}")
                        self.frame.after(0, self._reset_download_state)
                        return
                
                output_template = os.path.join(download_folder, output_template)
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best' if audio_only else 'best',
                'outtmpl': output_template,
                'postprocessors': postprocessors,
                'progress_hooks': [self._progress_hook],
                'quiet': False,
                'no_warnings': True,
                'retries': 3,
                'ignoreerrors': False
            }
            
            # Check if download should be stopped
            if self.stop_download:
                self.frame.after(0, self._download_finished, None)
                return
            
            # Perform download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            
            # Apply additional metadata if needed
            if info and audio_only:
                downloaded_file = None
                
                # Try to find the downloaded file
                if 'requested_downloads' in info:
                    for download in info['requested_downloads']:
                        if 'filepath' in download:
                            downloaded_file = download['filepath']
                            if os.path.exists(downloaded_file):
                                break
                            else:
                                print(f"Reported filepath doesn't exist: {downloaded_file}")
                                downloaded_file = None
                
                # If couldn't find path in info, try to determine it from the output template
                if not downloaded_file:
                    # Get base filename without extension
                    if metadata['title'] and metadata['artist']:
                        title = self._sanitize_filename(metadata['title'])
                        artist = self._sanitize_filename(metadata['artist'])
                        base_filename = f"{artist} - {title}"
                    else:
                        base_filename = os.path.splitext(output_template)[0]
                    
                    print(f"Looking for file with base name: {base_filename}")
                    
                    # Get the directory to search in
                    search_dir = download_path if download_path else config.get('custom_download_folder', 'downloads')
                    
                    # First try exact matching with various extensions
                    possible_extensions = [audio_format, 'mp3', 'm4a', 'webm', 'mp4', 'flac', 'wav', 'opus']
                    for ext in possible_extensions:
                        possible_file = os.path.join(search_dir, f"{base_filename}.{ext}")
                        if os.path.exists(possible_file):
                            downloaded_file = possible_file
                            print(f"Found file with extension .{ext}: {possible_file}")
                            break
                    
                    # If still not found, try fuzzy matching
                    if not downloaded_file and os.path.exists(search_dir):
                        # List recently created files in the directory
                        files = []
                        try:
                            for file in os.listdir(search_dir):
                                file_path = os.path.join(search_dir, file)
                                if os.path.isfile(file_path):
                                    # Get last modified time
                                    files.append((file_path, os.path.getmtime(file_path)))
                            
                            # Sort by last modified time (newest first)
                            files.sort(key=lambda x: x[1], reverse=True)
                            
                            # Check first 5 newest files (most likely our download)
                            for file_path, _ in files[:5]:
                                if file_path.endswith(tuple(f'.{ext}' for ext in possible_extensions)):
                                    print(f"Found recently modified audio file: {file_path}")
                                    downloaded_file = file_path
                                    break
                        except Exception as e:
                            print(f"Error during fuzzy file search: {e}")
                
                # Apply metadata if file was found
                if downloaded_file and os.path.exists(downloaded_file):
                    print(f"Applying metadata to found file: {downloaded_file}")
                    try:
                        # Get format from file extension
                        ext = os.path.splitext(downloaded_file)[1][1:].lower()
                        self._apply_metadata(downloaded_file, metadata, ext)
                    except Exception as e:
                        print(f"Error applying metadata: {e}")
                else:
                    print(f"Failed to find downloaded file. Listing directory content:")
                    try:
                        search_dir = download_path if download_path else config.get('custom_download_folder', 'downloads')
                        if os.path.exists(search_dir):
                            print(f"Files in {search_dir}:")
                            for file in os.listdir(search_dir):
                                print(f"  - {file}")
                    except Exception as e:
                        print(f"Error listing directory: {e}")
            
            # Notify completion
            self.frame.after(0, self._download_finished, info)
            
        except Exception as e:
            error_msg = str(e)
            self.frame.after(0, messagebox.showerror, "Download Error", f"Error downloading video: {error_msg}")
            self.frame.after(0, self.status_callback, "Download failed", 0)
            self.frame.after(0, self.status_label.config, {"text": f"Download failed: {error_msg}"})
            self.frame.after(0, self._reset_download_state)
    
    def _progress_hook(self, d):
        """Progress hook for yt-dlp"""
        if self.stop_download:
            # Signal to cancel download
            return
        
        if d['status'] == 'downloading':
            # Calculate progress percentage
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                percentage = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            else:
                percentage = 0
            
            # Get speed
            speed = d.get('speed', 0)
            if speed:
                speed_str = self._format_size(speed) + '/s'
            else:
                speed_str = 'N/A'
            
            # Get ETA
            eta = d.get('eta', 0)
            if eta:
                eta_str = self._format_duration(eta)
            else:
                eta_str = 'N/A'
            
            # Update progress in main thread
            self.frame.after(0, self.progress_var.set, percentage)
            self.frame.after(0, self.status_label.config, 
                          {"text": f"Downloading: {percentage:.1f}% | Speed: {speed_str} | ETA: {eta_str}"})
            self.frame.after(0, self.status_callback, f"Downloading: {percentage:.1f}%", percentage)
            
        elif d['status'] == 'finished':
            # Download finished, show processing message
            self.frame.after(0, self.progress_var.set, 100)
            self.frame.after(0, self.status_label.config, {"text": "Processing downloaded file..."})
            self.frame.after(0, self.status_callback, "Processing downloaded file...", 100)
    
    def _download_finished(self, info):
        """Handle download completion"""
        if self.stop_download:
            self.status_label.config(text="Download canceled")
            self.status_callback("Download canceled", 0)
        elif info:
            self.status_label.config(text="Download completed successfully")
            self.status_callback("Download completed successfully", 100)
            messagebox.showinfo("Download Complete", "Video has been downloaded successfully")
        
        self._reset_download_state()
    
    def _reset_download_state(self):
        """Reset download state"""
        self.is_downloading = False
        self.stop_download = False
        self.download_button.config(state=tk.NORMAL)
        self.queue_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
    
    def _apply_metadata(self, file_path, metadata, format_type):
        """Apply metadata to downloaded file"""
        try:
            if format_type == 'm4a':
                audio = MP4(file_path)
                
                if metadata['title']:
                    audio['\xa9nam'] = metadata['title']
                
                if metadata['artist']:
                    audio['\xa9ART'] = metadata['artist']
                
                if metadata['album']:
                    audio['\xa9alb'] = metadata['album']
                
                if metadata['year']:
                    audio['\xa9day'] = metadata['year']
                
                audio.save()
            
            # Handle other formats if needed
            
        except Exception as e:
            print(f"Error applying metadata: {e}")
    
    def cancel_download(self):
        """Cancel ongoing download"""
        if not self.is_downloading:
            return
        
        self.stop_download = True
        self.status_label.config(text="Canceling download...")
        self.status_callback("Canceling download...", 0)
    
    def add_to_queue(self):
        """Add YouTube video to download queue"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Input Error", "Please enter a YouTube URL")
            return
            
        # Validate URL
        if not self._is_valid_youtube_url(url):
            messagebox.showwarning("Invalid URL", "Please enter a valid YouTube URL")
            return
        
        # Get custom filename if title is provided
        custom_filename = None
        title = self.title_entry.get().strip()
        if title:
            # Remove invalid characters from filename
            import re
            title = re.sub(r'[\\/*?:"<>|]', "", title)
            custom_filename = title
        
        # Add to download queue
        try:
            self.download_manager.queue_youtube_download(url, custom_filename)
            messagebox.showinfo("Added to Queue", "YouTube track added to download queue")
            self.status_callback("YouTube track added to download queue", 100)
        except Exception as e:
            messagebox.showerror("Queue Error", f"Error adding to queue: {str(e)}")
    
    def _set_ui_state(self, state):
        """Set UI elements state"""
        self.url_entry.config(state=state)
        self.title_entry.config(state=state)
        self.artist_entry.config(state=state)
        self.album_entry.config(state=state)
        self.year_entry.config(state=state)
        
        # Handle buttons separately
        btn_state = state if state == tk.DISABLED else tk.NORMAL
        
        if not self.is_downloading:
            self.download_button.config(state=btn_state)
            self.queue_button.config(state=btn_state)
    
    def _is_valid_youtube_url(self, url):
        """Check if URL is a valid YouTube URL"""
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        
        match = re.match(youtube_regex, url)
        return match is not None
    
    def _format_size(self, bytes_):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_ < 1024.0:
                return f"{bytes_:.2f} {unit}"
            bytes_ /= 1024.0
        return f"{bytes_:.2f} PB"

    def search_youtube(self):
        """Search YouTube for videos"""
        query = self.search_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Search Error", "Please enter a search term")
            return
            
        # Update status
        self.status_label.config(text="Searching YouTube...")
        self.progress_var.set(50)
        
        # Clear previous results
        self.videos_listbox.delete(0, tk.END)
        self.lyrics_text.delete(1.0, tk.END)
        self.details_text.delete(1.0, tk.END)
        self.search_results = []
        
        # Disable buttons
        self.play_button.config(state=tk.DISABLED)
        self.download_search_button.config(state=tk.DISABLED)
        self.queue_search_button.config(state=tk.DISABLED)
        self.view_lyrics_button.config(state=tk.DISABLED)
        
        # Start search in background thread
        threading.Thread(
            target=self._search_youtube_thread,
            args=(query,),
            daemon=True
        ).start()
    
    def _search_youtube_thread(self, query):
        """Run YouTube search in background thread"""
        try:
            # Refine search query if needed
            if self.music_only_var.get():
                query += " music"
                
            if self.lyrics_only_var.get():
                query += " lyrics"
                
            # Configure yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': False
            }
            
            # Search YouTube
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get search results
                search_term = f"ytsearch10:{query}"  # Limit to 10 results
                info = ydl.extract_info(search_term, download=False)
                
                if not info or 'entries' not in info or not info['entries']:
                    self.frame.after(0, messagebox.showinfo, "No Results", "No videos found for your search")
                    self.frame.after(0, self.status_label.config, {"text": "No results found"})
                    self.frame.after(0, self.progress_var.set, 0)
                    return
                
                # Process results
                self.search_results = []
                
                for entry in info['entries']:
                    if not entry:
                        continue
                        
                    title = entry.get('title', 'Unknown Title')
                    uploader = entry.get('uploader', 'Unknown Uploader')
                    video_id = entry.get('id')
                    duration = entry.get('duration')
                    
                    if not video_id:
                        continue
                    
                    # Create result entry
                    result = {
                        'title': title,
                        'uploader': uploader,
                        'video_id': video_id,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'duration': duration
                    }
                    
                    self.search_results.append(result)
                    
                    # Format duration
                    duration_str = ""
                    if duration:
                        minutes = int(duration // 60)
                        seconds = int(duration % 60)
                        duration_str = f" ({minutes}:{seconds:02d})"
                    
                    # Add to listbox
                    self.frame.after(0, self.videos_listbox.insert, tk.END, 
                                   f"{title} - {uploader}{duration_str}")
                
                # Update status
                self.frame.after(0, self.status_label.config, {"text": f"Found {len(self.search_results)} results"})
                self.frame.after(0, self.progress_var.set, 100)
                
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            self.frame.after(0, messagebox.showerror, "Search Error", f"Error searching YouTube: {e}")
            self.frame.after(0, self.status_label.config, {"text": "Search error"})
            self.frame.after(0, self.progress_var.set, 0)
    
    def on_video_selected(self, event):
        """Handle video selection from search results"""
        selection = self.videos_listbox.curselection()
        
        if not selection or not self.search_results:
            return
            
        # Get selected video
        index = selection[0]
        if index >= len(self.search_results):
            return
            
        video = self.search_results[index]
        
        # Enable buttons
        self.play_button.config(state=tk.NORMAL)
        self.download_search_button.config(state=tk.NORMAL)
        self.queue_search_button.config(state=tk.NORMAL)
        self.view_lyrics_button.config(state=tk.NORMAL)
        
        # Update details tab
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, f"Title: {video['title']}\n")
        self.details_text.insert(tk.END, f"Channel: {video['uploader']}\n")
        
        if video.get('duration'):
            minutes = int(video['duration'] // 60)
            seconds = int(video['duration'] % 60)
            self.details_text.insert(tk.END, f"Duration: {minutes}:{seconds:02d}\n")
            
        self.details_text.insert(tk.END, f"URL: {video['url']}\n")
        
        # Switch to details tab
        self.results_notebook.select(2)  # Details tab
    
    def play_video(self):
        """Play selected video in web browser"""
        selection = self.videos_listbox.curselection()
        
        if not selection or not self.search_results:
            return
            
        # Get selected video
        index = selection[0]
        if index >= len(self.search_results):
            return
            
        video = self.search_results[index]
        
        # Open URL in web browser
        import webbrowser
        webbrowser.open(video['url'])
    
    def download_selected(self):
        """Download selected video"""
        selection = self.videos_listbox.curselection()
        
        if not selection or not self.search_results:
            return
            
        # Get selected video
        index = selection[0]
        if index >= len(self.search_results):
            return
            
        video = self.search_results[index]
        
        # Copy URL to direct tab
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, video['url'])
        
        # Switch to direct tab and fetch info
        self.tab_notebook.select(0)  # Direct URL tab
        self.fetch_video_info()
    
    def queue_selected(self):
        """Add selected video to download queue"""
        selection = self.videos_listbox.curselection()
        
        if not selection or not self.search_results:
            return
            
        # Get selected video
        index = selection[0]
        if index >= len(self.search_results):
            return
            
        video = self.search_results[index]
        
        # Add to queue
        try:
            self.download_manager.queue_youtube_download(video['url'], video['title'])
            messagebox.showinfo("Added to Queue", f"{video['title']} has been added to the download queue")
            self.status_callback(f"{video['title']} added to download queue", 100)
        except Exception as e:
            messagebox.showerror("Queue Error", f"Error adding to queue: {str(e)}")
    
    def view_lyrics(self):
        """View lyrics for selected video"""
        selection = self.videos_listbox.curselection()
        
        if not selection or not self.search_results:
            return
            
        # Get selected video
        index = selection[0]
        if index >= len(self.search_results):
            return
            
        video = self.search_results[index]
        
        # Clear previous lyrics
        self.lyrics_text.delete(1.0, tk.END)
        self.lyrics_text.insert(tk.END, "Searching for lyrics...\n")
        
        # Switch to lyrics tab
        self.results_notebook.select(1)  # Lyrics tab
        
        # Start search in background thread
        threading.Thread(
            target=self._fetch_lyrics_thread,
            args=(video,),
            daemon=True
        ).start()
    
    def _fetch_lyrics_thread(self, video):
        """Fetch lyrics for video in background thread"""
        try:
            # Get full video info to access description
            ydl_opts = {
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video['url'], download=False)
                
                if not info:
                    self.frame.after(0, self.lyrics_text.delete, 1.0, tk.END)
                    self.frame.after(0, self.lyrics_text.insert, tk.END, "Could not fetch video information")
                    return
                
                # Extract description
                description = info.get('description', '')
                
                # First check if description contains lyrics
                import re
                
                # Check if description looks like lyrics
                if self._is_likely_lyrics(description, video['title'], video['uploader']):
                    # Clean and display lyrics
                    lyrics = self._clean_lyrics(description)
                    
                    self.frame.after(0, self.lyrics_text.delete, 1.0, tk.END)
                    self.frame.after(0, self.lyrics_text.insert, tk.END, 
                                   f"LYRICS FOR: {video['title']}\n\n{lyrics}")
                    return
                
                # If no lyrics in description, try searching online
                self.frame.after(0, self.lyrics_text.delete, 1.0, tk.END)
                self.frame.after(0, self.lyrics_text.insert, tk.END, 
                               "Searching online for lyrics...\n")
                
                # Try to find lyrics through various sources
                lyrics = self._search_lyrics_online(video['title'], video['uploader'])
                
                if lyrics:
                    self.frame.after(0, self.lyrics_text.delete, 1.0, tk.END)
                    self.frame.after(0, self.lyrics_text.insert, tk.END, 
                                   f"LYRICS FOR: {video['title']}\n\n{lyrics}")
                else:
                    self.frame.after(0, self.lyrics_text.delete, 1.0, tk.END)
                    self.frame.after(0, self.lyrics_text.insert, tk.END, 
                                   f"No lyrics found for {video['title']}")
            
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            self.frame.after(0, self.lyrics_text.delete, 1.0, tk.END)
            self.frame.after(0, self.lyrics_text.insert, tk.END, f"Error fetching lyrics: {e}")
    
    def _is_likely_lyrics(self, text, title, uploader):
        """Check if text is likely to be lyrics"""
        if not text or len(text) < 100:
            return False
            
        # Convert to lowercase for comparison
        text_lower = text.lower()
        title_lower = title.lower()
        uploader_lower = uploader.lower()
        
        # Check if text contains title but not uploader repeatedly
        if title_lower not in text_lower:
            return False
            
        # Check for lyrics markers
        lyrics_markers = ['lyrics', 'verse', 'chorus', '[verse]', '[chorus]', 'bridge']
        if any(marker in text_lower for marker in lyrics_markers):
            return True
            
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
        """Clean up lyrics text from descriptions"""
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
        
    def _search_lyrics_online(self, title, artist):
        """Search for lyrics online"""
        # Remove common terms from title that might interfere with lyrics search
        clean_title = re.sub(r'\(.*?\)|\[.*?\]|ft\..*|feat\..*|official.*|video.*|audio.*|lyrics.*', '', title, flags=re.IGNORECASE)
        clean_title = clean_title.strip()
        
        try:
            # Try AZLyrics
            lyrics = self._search_azlyrics(clean_title, artist)
            if lyrics:
                return lyrics
                
            # Try Genius
            lyrics = self._search_genius(clean_title, artist)
            if lyrics:
                return lyrics
            
            # No lyrics found
            return None
            
        except Exception as e:
            print(f"Error searching lyrics: {e}")
            return None
            
    def _search_azlyrics(self, title, artist):
        """Search AZLyrics for lyrics"""
        try:
            # Prepare search query
            artist = re.sub(r'[^a-zA-Z0-9]', '', artist.lower())
            title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
            
            if not artist or not title:
                return None
                
            # Construct AZLyrics URL
            url = f"https://www.azlyrics.com/lyrics/{artist}/{title}.html"
            
            # Fetch page
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code != 200:
                return None
                
            # Parse lyrics
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # AZLyrics has lyrics in a div without class/id but with specific structure
            lyrics_div = soup.find('div', {'class': None, 'id': None}, attrs={'style': None})
            
            if not lyrics_div:
                return None
                
            lyrics = lyrics_div.get_text().strip()
            return lyrics
            
        except Exception as e:
            print(f"Error searching AZLyrics: {e}")
            return None
            
    def _search_genius(self, title, artist):
        """Search Genius for lyrics"""
        try:
            # Prepare search query
            search_query = f"{title} {artist} lyrics"
            search_url = f"https://genius.com/api/search/multi?q={search_query}"
            
            # Fetch search results
            response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code != 200:
                return None
                
            # Parse response
            data = response.json()
            
            sections = data.get('response', {}).get('sections', [])
            
            # Find hits in the songs section
            song_hits = []
            for section in sections:
                if section.get('type') == 'song':
                    song_hits = section.get('hits', [])
                    break
                    
            if not song_hits:
                return None
                
            # Get the first song result
            result = song_hits[0].get('result')
            
            if not result or not result.get('url'):
                return None
                
            # Fetch the song page
            song_url = result.get('url')
            response = requests.get(song_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code != 200:
                return None
                
            # Parse lyrics
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Genius stores lyrics in a div with class 'lyrics'
            lyrics_container = soup.find('div', class_='lyrics')
            
            if not lyrics_container:
                # Try newer Genius format
                lyrics_container = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-6')
                
            if not lyrics_container:
                return None
                
            lyrics = lyrics_container.get_text().strip()
            return lyrics
            
        except Exception as e:
            print(f"Error searching Genius: {e}")
            return None
    
    def _sanitize_filename(self, filename):
        """Sanitize a filename to remove problematic characters"""
        # Replace invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, '_', filename)
        
        # Replace other problematic characters
        filename = filename.replace('–', '-')  # Replace en-dash
        filename = filename.replace('—', '-')  # Replace em-dash
        filename = filename.replace(''', "'")  # Replace smart quotes
        filename = filename.replace(''', "'")
        filename = filename.replace('"', '"')
        filename = filename.replace('"', '"')
        
        return filename 