import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class SearchTab:
    """Tab for searching Spotify content"""
    
    def __init__(self, parent, spotify_service, download_manager, status_callback, ui_styles):
        self.parent = parent
        self.spotify_service = spotify_service
        self.download_manager = download_manager
        self.status_callback = status_callback
        self.ui_styles = ui_styles
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create search tab widgets"""
        # Top container for search options
        top_container = ttk.Frame(self.frame)
        top_container.pack(padx=15, pady=10, fill=tk.X)
        
        # Create two columns for search and direct link
        search_col = ttk.Frame(top_container)
        search_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        link_col = ttk.Frame(top_container)
        link_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Search section
        search_frame = ttk.LabelFrame(search_col, text="Search Spotify", padding=10)
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search entry with placeholder
        search_entry_frame, self.search_entry, _ = self.ui_styles.create_search_entry(
            search_frame,
            placeholder="Enter artist, album or track name...",
            callback=self.perform_search
        )
        search_entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search type
        self.search_type = tk.StringVar(value="tracks")
        search_type_frame = ttk.Frame(search_frame)
        search_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create styled radio buttons
        for text, value in [("Tracks", "tracks"), ("Albums", "albums"), ("Playlists", "playlists")]:
            radio = ttk.Radiobutton(
                search_type_frame, 
                text=text, 
                variable=self.search_type, 
                value=value,
                style="TRadiobutton"
            )
            radio.pack(side=tk.LEFT, padx=(0, 15))
        
        # Search button
        search_button = self.ui_styles.create_rounded_button(
            search_frame, 
            text="🔍 Search",
            command=self.perform_search,
            width=15
        )
        search_button.pack(anchor=tk.E)
        
        # Direct link frame
        link_frame = ttk.LabelFrame(link_col, text="Spotify Direct Link", padding=10)
        link_frame.pack(fill=tk.BOTH, expand=True)
        
        # Link label
        ttk.Label(
            link_frame, 
            text="Enter Spotify URL:",
            style="Subtitle.TLabel"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Link entry
        self.link_entry = ttk.Entry(link_frame)
        self.link_entry.pack(fill=tk.X, pady=(0, 10))
        self.link_entry.bind("<Return>", lambda e: self.process_link())
        
        # Help text
        help_text = ttk.Label(
            link_frame,
            text="Supports tracks, albums and playlists",
            style="Small.TLabel"
        )
        help_text.pack(anchor=tk.W, pady=(0, 10))
        
        # Link button
        link_button = self.ui_styles.create_rounded_button(
            link_frame, 
            text="📥 Download Link",
            command=self.process_link,
            width=15
        )
        link_button.pack(anchor=tk.E)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Search Results", padding=10)
        results_frame.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbar
        self.tree_frame = ttk.Frame(results_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbar
        tree_scroll = ttk.Scrollbar(self.tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview with improved styling
        self.results_tree = ttk.Treeview(
            self.tree_frame,
            yscrollcommand=tree_scroll.set,
            columns=("name", "artist", "type", "info"),
            show="headings",
            style="Results.Treeview"
        )
        
        # Configure scrollbar
        tree_scroll.config(command=self.results_tree.yview)
        
        # Set column headings
        self.results_tree.heading("name", text="Name")
        self.results_tree.heading("artist", text="Artist/Owner")
        self.results_tree.heading("type", text="Type")
        self.results_tree.heading("info", text="Info")
        
        # Set column widths
        self.results_tree.column("name", width=300, minwidth=200)
        self.results_tree.column("artist", width=200, minwidth=150)
        self.results_tree.column("type", width=80, minwidth=80)
        self.results_tree.column("info", width=150, minwidth=100)
        
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event
        self.results_tree.bind("<Double-1>", self.on_result_double_click)
        
        # Right-click context menu
        self.context_menu = tk.Menu(self.results_tree, tearoff=0)
        self.context_menu.add_command(label="Download", command=self.download_selected)
        self.context_menu.add_command(label="Add to Queue", command=self.queue_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Spotify ID", command=self.copy_id)
        
        # Bind right-click event
        self.results_tree.bind("<Button-3>", self.show_context_menu)
        
        # Action buttons in a button bar
        button_frame = ttk.Frame(results_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.download_button = self.ui_styles.create_rounded_button(
            button_frame,
            text="⬇️ Download Selected",
            command=self.download_selected,
            state="disabled",
            style="success.TButton"
        )
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.queue_button = self.ui_styles.create_rounded_button(
            button_frame,
            text="➕ Add to Queue",
            command=self.queue_selected,
            state="disabled"
        )
        self.queue_button.pack(side=tk.LEFT)
        
        # Help button
        help_button = self.ui_styles.create_help_button(
            button_frame,
            help_text="Double-click any item to download immediately.\nRight-click for more options."
        )
        help_button.pack(side=tk.RIGHT)
        
        # Enable buttons when selection is made
        self.results_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
    
    def perform_search(self):
        """Perform search on Spotify"""
        query = self.search_entry.get().strip()
        search_type = self.search_type.get()
        
        if not query:
            messagebox.showwarning("Search Error", "Please enter a search query.")
            return
        
        if not self.spotify_service.authenticated:
            messagebox.showerror("Authentication Error", 
                              "Spotify API not authenticated. Please provide valid credentials in Settings.")
            return
        
        # Clear previous results
        self.clear_results()
        
        # Update status
        self.status_callback(f"Searching for {search_type}...", 50)
        
        try:
            # Perform search based on type
            results = []
            if search_type == "tracks":
                results = self.spotify_service.search_tracks(query)
                for track in results:
                    self.results_tree.insert(
                        "", "end", 
                        values=(
                            track['name'], 
                            track['artist'], 
                            "Track", 
                            track['album']
                        ),
                        tags=("track", track['id'])
                    )
            
            elif search_type == "albums":
                results = self.spotify_service.search_albums(query)
                for album in results:
                    self.results_tree.insert(
                        "", "end", 
                        values=(
                            album['name'], 
                            album['artist'], 
                            "Album", 
                            f"{album['total_tracks']} tracks"
                        ),
                        tags=("album", album['id'])
                    )
            
            elif search_type == "playlists":
                results = self.spotify_service.search_playlists(query)
                for playlist in results:
                    self.results_tree.insert(
                        "", "end", 
                        values=(
                            playlist['name'], 
                            playlist['owner'], 
                            "Playlist", 
                            f"{playlist['total_tracks']} tracks"
                        ),
                        tags=("playlist", playlist['id'])
                    )
            
            # Update status
            if results:
                self.status_callback(f"Found {len(results)} {search_type}", 100)
            else:
                self.status_callback(f"No {search_type} found for '{query}'", 0)
                
        except Exception as e:
            messagebox.showerror("Search Error", f"Error performing search: {e}")
            self.status_callback("Search failed", 0)
    
    def process_link(self):
        """Process Spotify link"""
        link = self.link_entry.get().strip()
        
        if not link:
            messagebox.showwarning("Link Error", "Please enter a Spotify link.")
            return
        
        if not self.spotify_service.authenticated:
            messagebox.showerror("Authentication Error", 
                              "Spotify API not authenticated. Please provide valid credentials in Settings.")
            return
        
        # Validate link format
        link_type = self.spotify_service.get_spotify_link_type(link)
        if not link_type:
            messagebox.showerror("Link Error", 
                              "Invalid Spotify link. Please provide a track, album, or playlist URL.")
            return
        
        # Extract Spotify ID
        spotify_id = self.spotify_service.extract_id_from_link(link)
        if not spotify_id:
            messagebox.showerror("Link Error", 
                              "Could not extract Spotify ID from link.")
            return
        
        # Ask user what to do with the link
        action = messagebox.askyesnocancel(
            "Process Link", 
            f"Found {link_type}. What would you like to do?\n\n"
            "Yes: Download Now\n"
            "No: Add to Download Queue\n"
            "Cancel: Do Nothing"
        )
        
        if action is None:  # User canceled
            return
        
        # Update status
        self.status_callback(f"Processing {link_type} link...", 50)
        
        try:
            # Get content based on link type
            tracks = self.spotify_service.get_spotify_content(link)
            
            if not tracks:
                messagebox.showwarning("Content Error", 
                                     f"No tracks found in the {link_type}.")
                self.status_callback("No tracks found", 0)
                return
            
            # Create collection info
            collection_info = {
                'id': spotify_id,
                'type': link_type,
                'name': tracks[0]['album'] if link_type == 'track' else f"{link_type.capitalize()} {spotify_id}"
            }
            
            if action:  # User clicked Yes - download now
                self.download_manager.queue_download(tracks, collection_info)
                self.status_callback(f"Downloading {len(tracks)} tracks from {link_type}", 100)
            else:  # User clicked No - add to queue
                self.download_manager.queue_download(tracks, collection_info)
                self.status_callback(f"Added {len(tracks)} tracks to download queue", 100)
                
            # Clear link entry
            self.link_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Processing Error", f"Error processing link: {e}")
            self.status_callback("Link processing failed", 0)
    
    def clear_results(self):
        """Clear search results"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Disable action buttons
        self.download_button.config(state="disabled")
        self.queue_button.config(state="disabled")
    
    def on_tree_select(self, event):
        """Handle tree selection event"""
        selected = self.results_tree.selection()
        
        if selected:
            self.download_button.config(state="normal")
            self.queue_button.config(state="normal")
        else:
            self.download_button.config(state="disabled")
            self.queue_button.config(state="disabled")
    
    def on_result_double_click(self, event):
        """Handle double-click on result"""
        selected = self.results_tree.selection()
        
        if selected:
            # Get item info
            item = selected[0]
            tags = self.results_tree.item(item, "tags")
            
            if tags:
                item_type = tags[0]
                item_id = tags[1]
                
                # Process based on type
                if item_type == "track":
                    self.download_track(item_id)
                elif item_type == "album":
                    self.download_album(item_id)
                elif item_type == "playlist":
                    self.download_playlist(item_id)
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        # Select row under mouse
        iid = self.results_tree.identify_row(event.y)
        if iid:
            # Select this item
            self.results_tree.selection_set(iid)
            # Show context menu
            self.context_menu.post(event.x_root, event.y_root)
    
    def download_selected(self):
        """Download selected item"""
        selected = self.results_tree.selection()
        
        if not selected:
            return
        
        # Get item info
        item = selected[0]
        tags = self.results_tree.item(item, "tags")
        
        if tags:
            item_type = tags[0]
            item_id = tags[1]
            
            # Process based on type
            if item_type == "track":
                self.download_track(item_id)
            elif item_type == "album":
                self.download_album(item_id)
            elif item_type == "playlist":
                self.download_playlist(item_id)
    
    def queue_selected(self):
        """Add selected item to download queue"""
        selected = self.results_tree.selection()
        
        if not selected:
            return
        
        # Get item info
        item = selected[0]
        tags = self.results_tree.item(item, "tags")
        
        if tags:
            item_type = tags[0]
            item_id = tags[1]
            
            # Process based on type
            if item_type == "track":
                self.queue_track(item_id)
            elif item_type == "album":
                self.queue_album(item_id)
            elif item_type == "playlist":
                self.queue_playlist(item_id)
    
    def download_track(self, track_id):
        """Download a track"""
        try:
            track = self.spotify_service.get_track(track_id)
            if track:
                # Create collection info
                collection_info = {
                    'id': track_id,
                    'type': 'track',
                    'name': track['name']
                }
                
                self.download_manager.queue_download([track], collection_info)
                self.status_callback(f"Downloading track: {track['name']}", 50)
            else:
                messagebox.showerror("Download Error", "Could not fetch track information.")
                
        except Exception as e:
            messagebox.showerror("Download Error", f"Error downloading track: {e}")
    
    def download_album(self, album_id):
        """Download an album"""
        try:
            tracks = self.spotify_service.get_album_tracks(album_id)
            if tracks:
                # Create collection info
                collection_info = {
                    'id': album_id,
                    'type': 'album',
                    'name': tracks[0]['album']
                }
                
                self.download_manager.queue_download(tracks, collection_info)
                self.status_callback(f"Downloading album: {tracks[0]['album']} ({len(tracks)} tracks)", 50)
            else:
                messagebox.showerror("Download Error", "Could not fetch album tracks.")
                
        except Exception as e:
            messagebox.showerror("Download Error", f"Error downloading album: {e}")
    
    def download_playlist(self, playlist_id):
        """Download a playlist"""
        try:
            tracks = self.spotify_service.get_playlist_tracks(playlist_id)
            if tracks:
                # Create collection info
                collection_info = {
                    'id': playlist_id,
                    'type': 'playlist',
                    'name': f"Playlist {playlist_id}"
                }
                
                self.download_manager.queue_download(tracks, collection_info)
                self.status_callback(f"Downloading playlist: {len(tracks)} tracks", 50)
            else:
                messagebox.showerror("Download Error", "Could not fetch playlist tracks.")
                
        except Exception as e:
            messagebox.showerror("Download Error", f"Error downloading playlist: {e}")
    
    def queue_track(self, track_id):
        """Add track to download queue"""
        try:
            track = self.spotify_service.get_track(track_id)
            if track:
                # Create collection info
                collection_info = {
                    'id': track_id,
                    'type': 'track',
                    'name': track['name']
                }
                
                self.download_manager.queue_download([track], collection_info)
                self.status_callback(f"Added track to queue: {track['name']}", 100)
            else:
                messagebox.showerror("Queue Error", "Could not fetch track information.")
                
        except Exception as e:
            messagebox.showerror("Queue Error", f"Error adding track to queue: {e}")
    
    def queue_album(self, album_id):
        """Add album to download queue"""
        try:
            tracks = self.spotify_service.get_album_tracks(album_id)
            if tracks:
                # Create collection info
                collection_info = {
                    'id': album_id,
                    'type': 'album',
                    'name': tracks[0]['album']
                }
                
                self.download_manager.queue_download(tracks, collection_info)
                self.status_callback(f"Added album to queue: {tracks[0]['album']} ({len(tracks)} tracks)", 100)
            else:
                messagebox.showerror("Queue Error", "Could not fetch album tracks.")
                
        except Exception as e:
            messagebox.showerror("Queue Error", f"Error adding album to queue: {e}")
    
    def queue_playlist(self, playlist_id):
        """Add playlist to download queue"""
        try:
            tracks = self.spotify_service.get_playlist_tracks(playlist_id)
            if tracks:
                # Create collection info
                collection_info = {
                    'id': playlist_id,
                    'type': 'playlist',
                    'name': f"Playlist {playlist_id}"
                }
                
                self.download_manager.queue_download(tracks, collection_info)
                self.status_callback(f"Added playlist to queue: {len(tracks)} tracks", 100)
            else:
                messagebox.showerror("Queue Error", "Could not fetch playlist tracks.")
                
        except Exception as e:
            messagebox.showerror("Queue Error", f"Error adding playlist to queue: {e}")
    
    def copy_id(self):
        """Copy Spotify ID to clipboard"""
        selected = self.results_tree.selection()
        
        if not selected:
            return
        
        # Get item info
        item = selected[0]
        tags = self.results_tree.item(item, "tags")
        
        if tags and len(tags) > 1:
            item_id = tags[1]
            
            # Copy to clipboard
            self.frame.clipboard_clear()
            self.frame.clipboard_append(item_id)
            
            self.status_callback(f"Copied ID to clipboard: {item_id}", 100) 