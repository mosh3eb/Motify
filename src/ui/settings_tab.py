import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os

from src.utils.config import (AVAILABLE_THEMES, AUDIO_QUALITY_OPTIONS, 
                            SUPPORTED_AUDIO_FORMATS, DOWNLOAD_FOLDER)

class SettingsTab:
    """Tab for application settings"""
    
    def __init__(self, parent, config, apply_callback):
        self.parent = parent
        self.config = config
        self.apply_callback = apply_callback
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create settings tab widgets"""
        # Spotify API settings
        api_frame = ttk.LabelFrame(self.frame, text="Spotify API Credentials")
        api_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Client ID
        client_id_frame = ttk.Frame(api_frame)
        client_id_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(client_id_frame, text="Client ID:").pack(side=tk.LEFT)
        
        self.client_id_entry = ttk.Entry(client_id_frame)
        self.client_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Client Secret
        client_secret_frame = ttk.Frame(api_frame)
        client_secret_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(client_secret_frame, text="Client Secret:").pack(side=tk.LEFT)
        
        self.client_secret_entry = ttk.Entry(client_secret_frame, show="*")
        self.client_secret_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # API Instructions
        instruction_frame = ttk.Frame(api_frame)
        instruction_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        instructions = (
            "To use Motify, you need to create a Spotify Developer account and application:\n"
            "1. Go to developer.spotify.com/dashboard and log in\n"
            "2. Create an app to get your Client ID and Client Secret\n"
            "3. Enter them above and click Save"
        )
        
        instruction_label = ttk.Label(
            instruction_frame, 
            text=instructions,
            justify=tk.LEFT,
            wraplength=500
        )
        instruction_label.pack(anchor=tk.W)
        
        # Download settings
        download_frame = ttk.LabelFrame(self.frame, text="Download Settings")
        download_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Download folder
        folder_frame = ttk.Frame(download_frame)
        folder_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(folder_frame, text="Download Folder:").pack(side=tk.LEFT)
        
        self.folder_entry = ttk.Entry(folder_frame)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_button = ttk.Button(
            folder_frame,
            text="Browse",
            command=self._browse_folder
        )
        browse_button.pack(side=tk.RIGHT)
        
        # Audio settings
        audio_frame = ttk.Frame(download_frame)
        audio_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Audio quality
        ttk.Label(audio_frame, text="Audio Quality:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.quality_var = tk.StringVar()
        quality_combo = ttk.Combobox(
            audio_frame,
            textvariable=self.quality_var,
            values=list(AUDIO_QUALITY_OPTIONS.keys()),
            state="readonly",
            width=15
        )
        quality_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Audio format
        ttk.Label(audio_frame, text="Audio Format:").grid(row=0, column=2, sticky=tk.W, padx=5)
        
        self.format_var = tk.StringVar()
        format_combo = ttk.Combobox(
            audio_frame,
            textvariable=self.format_var,
            values=SUPPORTED_AUDIO_FORMATS,
            state="readonly",
            width=10
        )
        format_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Concurrent downloads
        ttk.Label(audio_frame, text="Concurrent Downloads:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=10)
        
        self.concurrent_var = tk.IntVar()
        concurrent_spinbox = ttk.Spinbox(
            audio_frame,
            from_=1,
            to=5,
            textvariable=self.concurrent_var,
            width=5
        )
        concurrent_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=10)
        
        # Skip existing
        self.skip_existing_var = tk.BooleanVar()
        skip_existing_check = ttk.Checkbutton(
            audio_frame,
            text="Skip Existing Files",
            variable=self.skip_existing_var
        )
        skip_existing_check.grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # App settings
        app_frame = ttk.LabelFrame(self.frame, text="Application Settings")
        app_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Theme selection
        theme_frame = ttk.Frame(app_frame)
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.theme_var = tk.StringVar(value=self.config.get("theme", "litera"))
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["litera", "darkly", "solar", "superhero", "cyborg", "vapor"],
            state="readonly",
            width=15
        )
        theme_combo.pack(side=tk.LEFT)
        theme_combo.bind("<<ComboboxSelected>>", self._apply_theme)
        
        # Apply theme button
        apply_theme_button = ttk.Button(
            theme_frame,
            text="Apply Theme",
            command=self._apply_theme
        )
        apply_theme_button.pack(side=tk.LEFT, padx=5)
        
        # Other options
        options_frame = ttk.Frame(app_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Auto-start queue
        self.auto_start_var = tk.BooleanVar()
        auto_start_check = ttk.Checkbutton(
            options_frame,
            text="Auto-start Queue",
            variable=self.auto_start_var
        )
        auto_start_check.pack(side=tk.LEFT)
        
        # Notifications
        self.notification_var = tk.BooleanVar()
        notification_check = ttk.Checkbutton(
            options_frame,
            text="Show Notifications",
            variable=self.notification_var
        )
        notification_check.pack(side=tk.LEFT, padx=20)
        
        # Buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        save_button = ttk.Button(
            button_frame,
            text="Save Settings",
            command=self._save_settings,
            style="primary.TButton"
        )
        save_button.pack(side=tk.RIGHT)
        
        reset_button = ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_defaults
        )
        reset_button.pack(side=tk.RIGHT, padx=5)
        
        # Load current settings
        self._load_current_settings()
    
    def _browse_folder(self):
        """Browse for download folder"""
        folder = filedialog.askdirectory(
            title="Select Download Folder",
            initialdir=self.folder_entry.get() or DOWNLOAD_FOLDER
        )
        
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
    
    def _load_current_settings(self):
        """Load current settings into UI"""
        # API credentials
        self.client_id_entry.delete(0, tk.END)
        self.client_id_entry.insert(0, self.config.get('client_id', ''))
        
        self.client_secret_entry.delete(0, tk.END)
        self.client_secret_entry.insert(0, self.config.get('client_secret', ''))
        
        # Download settings
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.config.get('custom_download_folder', DOWNLOAD_FOLDER))
        
        self.quality_var.set(self.config.get('audio_quality', 'Medium'))
        self.format_var.set(self.config.get('audio_format', 'm4a'))
        self.concurrent_var.set(self.config.get('concurrent_downloads', 1))
        self.skip_existing_var.set(self.config.get('skip_existing', True))
        
        # App settings
        self.theme_var.set(self.config.get('theme', 'cyborg'))
        self.auto_start_var.set(self.config.get('auto_start_queue', False))
        self.notification_var.set(self.config.get('notification_enabled', True))
    
    def _save_settings(self):
        """Save settings to config"""
        # Get values from UI
        settings = {
            'client_id': self.client_id_entry.get(),
            'client_secret': self.client_secret_entry.get(),
            'custom_download_folder': self.folder_entry.get(),
            'audio_quality': self.quality_var.get(),
            'audio_format': self.format_var.get(),
            'concurrent_downloads': self.concurrent_var.get(),
            'skip_existing': self.skip_existing_var.get(),
            'theme': self.theme_var.get(),
            'auto_start_queue': self.auto_start_var.get(),
            'notification_enabled': self.notification_var.get()
        }
        
        # Check if download folder has changed
        old_folder = self.config.get('custom_download_folder', 'downloads')
        new_folder = settings['custom_download_folder']
        download_folder_changed = old_folder != new_folder
        
        # Validate settings
        download_folder = settings['custom_download_folder']
        if download_folder and not os.path.exists(download_folder):
            create_folder = messagebox.askyesno(
                "Folder Not Found",
                f"The download folder '{download_folder}' does not exist. Create it?"
            )
            
            if create_folder:
                try:
                    os.makedirs(download_folder, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Folder Error", f"Error creating folder: {e}")
                    return
            else:
                return
        
        # Update config
        self.config.update(settings)
        
        # Tell parent to apply settings
        self.apply_callback(settings)
        
        # Save Spotify credentials to credentials.json and initialize
        from src.services.spotify_service import SpotifyService
        spotify_service = SpotifyService()
        spotify_service.save_credentials(settings['client_id'], settings['client_secret'])
        
        # Update the download folder watcher if needed
        if download_folder_changed:
            # Get the main window to access the download manager
            main_window = self.parent.winfo_toplevel()
            if hasattr(main_window, 'download_manager'):
                try:
                    main_window.download_manager.update_download_folder(new_folder)
                    print(f"Updated download folder watcher to: {new_folder}")
                except Exception as e:
                    print(f"Error updating download folder watcher: {e}")
        
        # Try to authenticate with new credentials
        auth_success = spotify_service.initialize(settings['client_id'], settings['client_secret'])
        if auth_success:
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully. Spotify API authenticated.")
        else:
            messagebox.showwarning("Spotify Authentication Failed", 
                                 "Settings have been saved, but Spotify authentication failed. Please check your credentials.")
    
    def _reset_defaults(self):
        """Reset settings to defaults"""
        confirm = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?"
        )
        
        if confirm:
            from src.utils.config import get_app_config
            default_config = get_app_config()
            
            # Update config
            self.config.update(default_config)
            
            # Reload settings
            self._load_current_settings()
    
    def _save_theme_only(self, theme):
        """Save just the theme setting without re-authenticating Spotify"""
        # Update config
        self.config["theme"] = theme
        
        # Tell parent to apply settings but only pass the theme
        self.apply_callback({"theme": theme})
        
        # Save the config
        from src.utils.config import save_app_config
        save_app_config(self.config)

    def _apply_theme(self, event=None):
        """Apply the selected theme"""
        theme = self.theme_var.get()
        try:
            # Apply theme to application
            self.parent.winfo_toplevel().style.theme_use(theme)
            
            # Save theme to config (without Spotify re-authentication)
            self._save_theme_only(theme)
        except Exception as e:
            messagebox.showerror("Theme Error", f"Error applying theme: {e}") 