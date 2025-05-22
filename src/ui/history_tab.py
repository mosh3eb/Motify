import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from datetime import datetime

class HistoryTab:
    """Tab for viewing download history"""
    
    def __init__(self, parent, download_manager, status_callback):
        self.parent = parent
        self.download_manager = download_manager
        self.status_callback = status_callback
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create history tab widgets"""
        # Track history section
        tracks_frame = ttk.LabelFrame(self.frame, text="Downloaded Tracks")
        tracks_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Track controls
        track_controls = ttk.Frame(tracks_frame)
        track_controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(track_controls, text="Track History:").pack(side=tk.LEFT)
        
        refresh_button = ttk.Button(
            track_controls, 
            text="Refresh",
            command=self.refresh_history
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # Track list with scrollbar
        track_list_frame = ttk.Frame(tracks_frame)
        track_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        track_scroll = ttk.Scrollbar(track_list_frame)
        track_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.track_tree = ttk.Treeview(
            track_list_frame,
            yscrollcommand=track_scroll.set,
            columns=("name", "artist", "album", "date"),
            show="headings"
        )
        
        track_scroll.config(command=self.track_tree.yview)
        
        # Configure columns
        self.track_tree.heading("name", text="Track")
        self.track_tree.heading("artist", text="Artist")
        self.track_tree.heading("album", text="Album")
        self.track_tree.heading("date", text="Downloaded")
        
        self.track_tree.column("name", width=250)
        self.track_tree.column("artist", width=200)
        self.track_tree.column("album", width=200)
        self.track_tree.column("date", width=150)
        
        self.track_tree.pack(fill=tk.BOTH, expand=True)
        
        # Track context menu
        self.track_context_menu = tk.Menu(self.track_tree, tearoff=0)
        self.track_context_menu.add_command(label="Open Folder", command=self._open_track_folder)
        self.track_context_menu.add_command(label="Play Track", command=self._play_track)
        
        self.track_tree.bind("<Button-3>", self._show_track_context_menu)
        self.track_tree.bind("<Double-1>", self._play_track)
        
        # Collection history section
        collections_frame = ttk.LabelFrame(self.frame, text="Downloaded Collections")
        collections_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Collection list with scrollbar
        coll_list_frame = ttk.Frame(collections_frame)
        coll_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        coll_scroll = ttk.Scrollbar(coll_list_frame)
        coll_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.collection_tree = ttk.Treeview(
            coll_list_frame,
            yscrollcommand=coll_scroll.set,
            columns=("name", "type", "tracks", "date"),
            show="headings",
            height=6
        )
        
        coll_scroll.config(command=self.collection_tree.yview)
        
        # Configure columns
        self.collection_tree.heading("name", text="Name")
        self.collection_tree.heading("type", text="Type")
        self.collection_tree.heading("tracks", text="Tracks")
        self.collection_tree.heading("date", text="Downloaded")
        
        self.collection_tree.column("name", width=250)
        self.collection_tree.column("type", width=100)
        self.collection_tree.column("tracks", width=100)
        self.collection_tree.column("date", width=150)
        
        self.collection_tree.pack(fill=tk.BOTH, expand=True)
        
        # Export/clear controls
        history_controls = ttk.Frame(self.frame)
        history_controls.pack(fill=tk.X, padx=10, pady=10)
        
        export_button = ttk.Button(
            history_controls,
            text="Export History",
            command=self._export_history
        )
        export_button.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_button = ttk.Button(
            history_controls,
            text="Clear History",
            command=self._clear_history,
            style="danger.TButton"
        )
        clear_button.pack(side=tk.LEFT)
        
        # Initial data load
        self.refresh_history()
    
    def refresh_history(self):
        """Refresh history data from download manager"""
        # Clear existing data
        for item in self.track_tree.get_children():
            self.track_tree.delete(item)
        
        for item in self.collection_tree.get_children():
            self.collection_tree.delete(item)
        
        # Get history data
        history = self.download_manager.get_download_history()
        
        # Populate tracks
        for i, track in enumerate(history['tracks']):
            # Format date
            try:
                date = datetime.fromisoformat(track['downloaded_at'])
                date_str = date.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = "Unknown"
            
            self.track_tree.insert(
                "", "end", 
                iid=f"track_{i}",
                values=(
                    track['name'],
                    track['artist'],
                    track['album'],
                    date_str
                ),
                tags=("track", track.get('file_path', ''))
            )
        
        # Populate collections
        for i, collection in enumerate(history['collections']):
            # Format date
            try:
                date = datetime.fromisoformat(collection['downloaded_at'])
                date_str = date.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = "Unknown"
            
            self.collection_tree.insert(
                "", "end", 
                iid=f"coll_{i}",
                values=(
                    collection.get('name', 'Unknown'),
                    collection.get('type', 'Unknown').title(),
                    collection.get('track_count', 0),
                    date_str
                ),
                tags=("collection", collection.get('id', ''))
            )
        
        self.status_callback("History refreshed", 100)
    
    def _show_track_context_menu(self, event):
        """Show context menu for track"""
        # Select row under mouse
        iid = self.track_tree.identify_row(event.y)
        if iid:
            # Select this item
            self.track_tree.selection_set(iid)
            # Show context menu
            self.track_context_menu.post(event.x_root, event.y_root)
    
    def _open_track_folder(self):
        """Open folder containing selected track"""
        selected = self.track_tree.selection()
        if not selected:
            return
        
        # Get file path from tags
        item_id = selected[0]
        tags = self.track_tree.item(item_id, "tags")
        
        if tags and len(tags) > 1:
            file_path = tags[1]
            if file_path and os.path.exists(file_path):
                folder = os.path.dirname(file_path)
                
                # Open folder in platform-specific way
                import subprocess, platform
                
                if platform.system() == "Windows":
                    os.startfile(folder)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", folder])
                else:  # Linux
                    subprocess.Popen(["xdg-open", folder])
            else:
                messagebox.showwarning("File Not Found", "The file does not exist or has been moved.")
    
    def _play_track(self, event=None):
        """Play selected track with default player"""
        if event:  # If called from event, get selected item
            iid = self.track_tree.identify_row(event.y)
            if iid:
                self.track_tree.selection_set(iid)
        
        selected = self.track_tree.selection()
        if not selected:
            return
        
        # Get file path from tags
        item_id = selected[0]
        tags = self.track_tree.item(item_id, "tags")
        
        if tags and len(tags) > 1:
            file_path = tags[1]
            if file_path and os.path.exists(file_path):
                # Play file with default player
                import subprocess, platform
                
                if platform.system() == "Windows":
                    os.startfile(file_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", file_path])
                else:  # Linux
                    subprocess.Popen(["xdg-open", file_path])
            else:
                messagebox.showwarning("File Not Found", "The file does not exist or has been moved.")
    
    def _export_history(self):
        """Export download history to file"""
        filepath = filedialog.asksaveasfilename(
            title="Export History",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            # Get history
            history = self.download_manager.get_download_history()
            
            # Write to file
            import json
            with open(filepath, 'w') as f:
                json.dump(history, f, indent=2)
            
            self.status_callback(f"History exported to {filepath}", 100)
            messagebox.showinfo("Export Complete", f"History has been exported to {filepath}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting history: {e}")
    
    def _clear_history(self):
        """Clear download history"""
        confirm = messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to clear the download history?\n\n"
            "This will not delete any downloaded files, only the history records."
        )
        
        if confirm:
            try:
                self.download_manager.clear_history()
                self.refresh_history()
                self.status_callback("History cleared", 100)
            except Exception as e:
                messagebox.showerror("Clear Error", f"Error clearing history: {e}") 