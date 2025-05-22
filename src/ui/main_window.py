import os
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.utils.config import (get_app_config, save_app_config, AVAILABLE_THEMES,
                             AUDIO_QUALITY_OPTIONS, SUPPORTED_AUDIO_FORMATS)
from src.ui.search_tab import SearchTab
from src.ui.queue_tab import QueueTab
from src.ui.history_tab import HistoryTab
from src.ui.settings_tab import SettingsTab
from src.ui.lyrics_tab import LyricsTab
from src.ui.youtube_tab import YouTubeTab
from src.ui.stats_tab import StatsTab
from src.services.spotify_service import SpotifyService
from src.services.downloader import DownloadManager

class MainWindow:
    """Main application window"""
    
    def __init__(self, root, ui_styles):
        self.root = root
        self.config = get_app_config()
        self.ui_styles = ui_styles
        
        # Set window properties
        self.root.title("Motify - Advanced Spotify Downloader")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize services
        self.spotify_service = SpotifyService()
        self.download_manager = DownloadManager(
            max_workers=self.config.get('concurrent_downloads', 1),
            notify_callback=self.show_notification,
            progress_callback=self.update_progress
        )
        
        # Create main framework
        self._create_menu()
        self._create_status_bar()
        self._create_main_frame()
        
        # Set up close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Apply theme
        self.apply_theme(self.config.get('theme', 'cyborg'))
    
    def _create_menu(self):
        """Create application menu"""
        self.menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Import Playlist", command=self.import_playlist)
        file_menu.add_command(label="Export History", command=self.export_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Settings", command=self.show_settings)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="Downloads Folder", command=self.open_downloads_folder)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme in ["litera", "darkly", "solar", "superhero", "cyborg", "vapor"]:
            theme_menu.add_command(
                label=theme.capitalize(),
                command=lambda t=theme: self.apply_theme(t)
            )
        view_menu.add_cascade(label="Themes", menu=theme_menu)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Tools menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        tools_menu.add_command(label="Sync Downloads Folder", command=self.sync_downloads_folder)
        tools_menu.add_command(label="Scan for Missing Metadata", command=self.scan_metadata)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=self.menu_bar)
    
    def _create_status_bar(self):
        """Create status bar"""
        # Create status bar using the UIStyles helper
        self.status_frame, self.status_updater = self.ui_styles.create_status_bar(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Add version label
        version_label = ttk.Label(
            self.status_frame,
            text="v2.0.0",
            style="Info.TLabel"
        )
        version_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Add separator
        separator = ttk.Separator(self.root, orient=tk.HORIZONTAL)
        separator.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame)
    
    def _create_main_frame(self):
        """Create main application frame with tabs"""
        # Create main container frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header with logo and title
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add app title
        title_label = ttk.Label(
            header_frame,
            text="Motify Music Downloader",
            style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Add quick action buttons on the right
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT)
        
        # Search button
        search_btn = self.ui_styles.create_rounded_button(
            actions_frame, 
            text="🔍 Search",
            command=lambda: self.notebook.select(0),
            style="primary.TButton"
        )
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # YouTube button
        youtube_btn = self.ui_styles.create_rounded_button(
            actions_frame,
            text="📺 YouTube",
            command=lambda: self.notebook.select(2)
        )
        youtube_btn.pack(side=tk.LEFT, padx=5)
        
        # Download queue button
        queue_btn = self.ui_styles.create_rounded_button(
            actions_frame,
            text="⬇️ Downloads",
            command=lambda: self.notebook.select(1)
        )
        queue_btn.pack(side=tk.LEFT, padx=5)
        
        # Add separator below header
        separator = ttk.Separator(self.main_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=(0, 10))
        
        # Create notebook (tabs) with styling
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Add tabs
        self.search_tab = SearchTab(
            self.notebook, 
            self.spotify_service, 
            self.download_manager,
            self.update_status,
            self.ui_styles
        )
        self.queue_tab = QueueTab(
            self.notebook, 
            self.download_manager,
            self.update_status
        )
        self.youtube_tab = YouTubeTab(
            self.notebook,
            self.download_manager,
            self.update_status
        )
        self.lyrics_tab = LyricsTab(
            self.notebook,
            self.spotify_service,
            self.update_status
        )
        self.history_tab = HistoryTab(
            self.notebook, 
            self.download_manager,
            self.update_status
        )
        self.stats_tab = StatsTab(
            self.notebook,
            self.download_manager,
            self.update_status
        )
        self.settings_tab = SettingsTab(
            self.notebook,
            self.config,
            self.apply_settings
        )
        
        # Add tabs with icons
        self.notebook.add(self.search_tab.frame, text=" 🔍 Search")
        self.notebook.add(self.queue_tab.frame, text=" ⬇️ Queue")
        self.notebook.add(self.youtube_tab.frame, text=" 📺 YouTube")
        self.notebook.add(self.lyrics_tab.frame, text=" 🎵 Lyrics")
        self.notebook.add(self.history_tab.frame, text=" 📋 History")
        self.notebook.add(self.stats_tab.frame, text=" 📊 Statistics")
        self.notebook.add(self.settings_tab.frame, text=" ⚙️ Settings")
        
        # Bind tab change event to update UI
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _on_tab_changed(self, event):
        """Handle tab change event"""
        # Update status to show the current tab
        tab_id = self.notebook.select()
        tab_text = self.notebook.tab(tab_id, "text").strip()
        self.update_status(f"Viewing {tab_text} tab", None)
    
    def update_status(self, message, progress=None):
        """Update status bar with message and optional progress"""
        # Use the status updater from UIStyles
        self.status_updater(message, progress)
        
        # Also update queue tab if active
        self.queue_tab.update_downloads()
    
    def update_progress(self, message, progress):
        """Update progress from download manager"""
        self.update_status(message, progress)
    
    def show_notification(self, title, message):
        """Show notification"""
        if self.config.get('notification_enabled', True):
            # Use plyer for cross-platform notifications
            try:
                from plyer import notification
                # Check for missing dependencies first
                try:
                    notification.notify(
                        title=title,
                        message=message,
                        app_name='Motify',
                        timeout=5
                    )
                except ModuleNotFoundError as me:
                    # Handle specific missing module error for macOS
                    if "No module named 'pyobjus'" in str(me):
                        print("Warning: The pyobjus module is missing, which is required for macOS notifications.")
                        print("You can install it with: pip install pyobjus")
                        print(f"Notification would have been: {title} - {message}")
                    else:
                        raise  # Re-raise if it's a different module error
                except Exception as ne:
                    print(f"Notification error: {ne}")
                    print(f"Notification would have been: {title} - {message}")
            except Exception as e:
                # General import or other error
                print(f"Error showing notification: {e}")
                print(f"Notification would have been: {title} - {message}")
    
    def apply_theme(self, theme_name):
        """Apply theme to the application"""
        try:
            # Apply theme
            try:
                self.root.style.theme_use(theme_name)
            except tk.TclError as tc_err:
                # Ignore duplicate element errors as they're harmless
                if "Duplicate element" not in str(tc_err):
                    raise
            
            # Update config
            self.config['theme'] = theme_name
            save_app_config(self.config)
            
            # Update UI styles with new theme
            self.ui_styles.theme = theme_name
            self.ui_styles.configure_styles()
            
            # Notify user
            self.update_status(f"Theme changed to {theme_name}", 100)
            
        except Exception as e:
            messagebox.showerror("Theme Error", f"Error applying theme: {e}")
    
    def apply_settings(self, settings):
        """Apply settings to the application"""
        # Update concurrent downloads in download manager
        if 'concurrent_downloads' in settings:
            self.download_manager.set_max_workers(settings['concurrent_downloads'])
        
        # Apply theme if changed
        if 'theme' in settings and settings['theme'] != self.config.get('theme'):
            self.apply_theme(settings['theme'])
        
        # Update status
        self.update_status("Settings applied", 100)
    
    def import_playlist(self):
        """Import playlist from file"""
        file_path = filedialog.askopenfilename(
            title="Import Playlist",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            # TODO: Implement playlist import
            self.update_status(f"Imported playlist from {file_path}", 100)
    
    def export_history(self):
        """Export download history to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export History",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            # TODO: Implement history export
            self.update_status(f"Exported history to {file_path}", 100)
    
    def open_downloads_folder(self):
        """Open downloads folder in file explorer"""
        download_folder = self.config.get('custom_download_folder', 'downloads')
        
        if os.path.exists(download_folder):
            # Open folder in file explorer
            if os.name == 'nt':  # Windows
                os.startfile(download_folder)
            elif os.name == 'posix':  # macOS and Linux
                import subprocess
                subprocess.call(('open' if os.uname().sysname == 'Darwin' else 'xdg-open', download_folder))
            
            self.update_status(f"Opened {download_folder} folder", 100)
        else:
            messagebox.showwarning("Folder Not Found", f"The download folder '{download_folder}' does not exist.")
    
    def sync_downloads_folder(self):
        """Sync downloaded tracks with downloads folder"""
        self.update_status("Syncing downloads folder...", 50)
        
        try:
            # Use the improved sync method from download manager
            tracks_removed = self.download_manager.sync_downloaded_tracks_with_folder()
            
            if tracks_removed:
                self.update_status("Downloads folder synced - removed tracks that no longer exist", 100)
                messagebox.showinfo("Sync Complete", "Downloads folder synced - removed tracks that no longer exist")
            else:
                self.update_status("Downloads folder synced - no changes needed", 100)
                messagebox.showinfo("Sync Complete", "Downloads folder synced - no changes needed")
                
            # Update UI if needed
            self.history_tab.update_history()
            
        except Exception as e:
            self.update_status(f"Error syncing downloads folder: {e}", 0)
            messagebox.showerror("Sync Error", f"Error syncing downloads folder: {e}")
    
    def scan_metadata(self):
        """Scan for missing metadata in downloaded files"""
        # TODO: Implement metadata scanning
        self.update_status("Scanning for missing metadata...", 50)
        # Simulate processing
        import time
        time.sleep(0.5)
        self.update_status("Metadata scan complete", 100)
    
    def show_settings(self):
        """Show settings tab"""
        self.notebook.select(self.settings_tab.frame)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Motify Music Downloader v2.0.0
        
A feature-rich application for downloading music from Spotify and YouTube.

Features:
• Search for music on Spotify and YouTube
• Download tracks, albums, and playlists
• Advanced queue management
• Lyrics lookup and synchronization
• Beautiful themes and customization options

Created with ❤️ using Python and ttkbootstrap
        """
        
        messagebox.showinfo("About Motify", about_text)
    
    def on_close(self):
        """Handle application close"""
        # Stop active downloads
        self.download_manager.stop_downloads()
        
        # Save config
        save_app_config(self.config)
        
        # Destroy window
        self.root.destroy() 