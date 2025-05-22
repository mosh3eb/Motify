import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class QueueTab:
    """Tab for managing download queue"""
    
    def __init__(self, parent, download_manager, status_callback):
        self.parent = parent
        self.download_manager = download_manager
        self.status_callback = status_callback
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        
        # Update timer
        self._update_id = None
        self._start_auto_update()
    
    def _create_widgets(self):
        """Create queue tab widgets"""
        # Queue management frame
        queue_frame = ttk.LabelFrame(self.frame, text="Download Queue")
        queue_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Queue controls
        controls_frame = ttk.Frame(queue_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(
            controls_frame,
            text="Start Downloads",
            command=self.start_downloads,
            style="success.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(
            controls_frame,
            text="Stop Downloads",
            command=self.stop_downloads,
            style="danger.TButton"
        )
        self.stop_button.pack(side=tk.LEFT)
        
        self.clear_button = ttk.Button(
            controls_frame,
            text="Clear Completed",
            command=self.clear_completed
        )
        self.clear_button.pack(side=tk.RIGHT)
        
        # Queue statistics
        stats_frame = ttk.Frame(queue_frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.queue_stats_label = ttk.Label(
            stats_frame,
            text="Queued: 0 | Active: 0 | Completed: 0"
        )
        self.queue_stats_label.pack(side=tk.LEFT)
        
        # Queue list
        list_frame = ttk.Frame(queue_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollbar
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create list with columns
        self.queue_tree = ttk.Treeview(
            list_frame,
            yscrollcommand=list_scroll.set,
            columns=("name", "artist", "status", "progress"),
            show="headings"
        )
        
        # Configure scrollbar
        list_scroll.config(command=self.queue_tree.yview)
        
        # Set column headings
        self.queue_tree.heading("name", text="Track")
        self.queue_tree.heading("artist", text="Artist")
        self.queue_tree.heading("status", text="Status")
        self.queue_tree.heading("progress", text="Progress")
        
        # Set column widths
        self.queue_tree.column("name", width=300)
        self.queue_tree.column("artist", width=200)
        self.queue_tree.column("status", width=120)
        self.queue_tree.column("progress", width=100)
        
        self.queue_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add Spotify link section
        link_frame = ttk.LabelFrame(self.frame, text="Add Spotify Link to Queue")
        link_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Link entry
        link_entry_frame = ttk.Frame(link_frame)
        link_entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(link_entry_frame, text="Spotify URL:").pack(side=tk.LEFT)
        
        self.link_entry = ttk.Entry(link_entry_frame)
        self.link_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        add_button = ttk.Button(
            link_entry_frame,
            text="Add to Queue",
            command=self._add_link_to_queue
        )
        add_button.pack(side=tk.RIGHT)
    
    def _start_auto_update(self):
        """Start auto-update timer"""
        self.update_downloads()
        self._update_id = self.frame.after(1000, self._start_auto_update)
    
    def _stop_auto_update(self):
        """Stop auto-update timer"""
        if self._update_id:
            self.frame.after_cancel(self._update_id)
            self._update_id = None
    
    def update_downloads(self):
        """Update queue display with current download status"""
        # Get current download status
        status = self.download_manager.get_download_status()
        
        # Update stats
        self.queue_stats_label.config(
            text=f"Queued: {status['queued']} | Active: {status['active']} | Completed: {status['completed']}"
        )
        
        # Update active downloads in treeview
        current_items = set(self.queue_tree.get_children())
        active_ids = set()
        
        # Update or add active downloads
        for download in status['active_downloads']:
            item_id = download['id']
            active_ids.add(item_id)
            
            # Format progress for display
            progress_text = f"{int(download['progress'])}%"
            
            # Check if item already exists in tree
            if item_id in current_items:
                # Update existing item
                self.queue_tree.item(
                    item_id,
                    values=(
                        download['name'],
                        download['artist'],
                        download['status'].replace('_', ' ').title(),
                        progress_text
                    )
                )
            else:
                # Add new item
                self.queue_tree.insert(
                    "", "end", iid=item_id,
                    values=(
                        download['name'],
                        download['artist'],
                        download['status'].replace('_', ' ').title(),
                        progress_text
                    )
                )
    
    def add_links_to_queue(self, links):
        """Add multiple Spotify links to queue"""
        if not links:
            return
        
        from src.services.spotify_service import SpotifyService
        
        # Create temporary Spotify service if needed
        spotify_service = SpotifyService()
        
        if not spotify_service.authenticated:
            messagebox.showerror(
                "Authentication Error",
                "Spotify API not authenticated. Please provide valid credentials in Settings."
            )
            return
        
        total_tracks = 0
        for link in links:
            try:
                # Process link
                link_type = spotify_service.get_spotify_link_type(link)
                if not link_type:
                    continue
                
                # Extract ID
                content_id = spotify_service.extract_id_from_link(link)
                if not content_id:
                    continue
                
                # Get tracks based on link type
                tracks = spotify_service.get_spotify_content(link)
                if not tracks:
                    continue
                
                # Create collection info
                collection_info = {
                    'id': content_id,
                    'type': link_type,
                    'name': tracks[0]['album'] if link_type == 'track' else f"{link_type.capitalize()} {content_id}"
                }
                
                # Add to queue
                self.download_manager.queue_download(tracks, collection_info)
                total_tracks += len(tracks)
                
            except Exception as e:
                print(f"Error processing link {link}: {e}")
        
        if total_tracks > 0:
            self.status_callback(f"Added {total_tracks} tracks to download queue", 100)
            self.update_downloads()
    
    def _add_link_to_queue(self):
        """Add link from entry field to queue"""
        link = self.link_entry.get().strip()
        
        if not link:
            messagebox.showwarning("Input Error", "Please enter a Spotify link.")
            return
        
        self.add_links_to_queue([link])
        self.link_entry.delete(0, tk.END)
    
    def start_downloads(self):
        """Start processing download queue"""
        # Nothing to do as downloads are processed automatically
        # Just update the status
        status = self.download_manager.get_download_status()
        if status['queued'] > 0:
            self.status_callback(f"Processing {status['queued']} queued downloads", 50)
        else:
            messagebox.showinfo("Queue Empty", "No downloads in queue.")
    
    def stop_downloads(self):
        """Stop all active downloads"""
        self.download_manager.stop_downloads()
        self.status_callback("Downloads stopped", 0)
    
    def clear_completed(self):
        """Clear completed downloads from view"""
        # Since we don't track completed downloads in the treeview,
        # just refresh the active downloads view
        self.update_downloads()
        self.status_callback("Cleared completed downloads", 100) 