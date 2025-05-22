import os
import time
import threading
import json
import concurrent.futures
from queue import Queue, Empty
from datetime import datetime
import re
import hashlib
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import yt_dlp
from yt_dlp.utils import DownloadError
from mutagen.mp4 import MP4, MP4Cover
import requests
import uuid

from src.utils.config import (DOWNLOAD_FOLDER, DOWNLOADED_TRACKS_FILE, HISTORY_FILE,
                             AUDIO_QUALITY_OPTIONS, DEFAULT_AUDIO_FORMAT)

# Import get_app_config function
from src.utils.config import get_app_config

class DownloadFolderHandler(FileSystemEventHandler):
    """Handler for file system events in the downloads folder"""
    
    def __init__(self, download_manager):
        self.download_manager = download_manager
        self._last_processed = {}  # Track last processed events to avoid duplicates
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
            
        # Check if it's an audio file
        if self._is_audio_file(event.src_path):
            # Avoid duplicate processing
            if event.src_path in self._last_processed and time.time() - self._last_processed[event.src_path] < 5:
                return
                
            self._last_processed[event.src_path] = time.time()
            print(f"New file detected: {event.src_path}")
            
            # Add to downloaded tracks
            self._add_to_downloaded_tracks(event.src_path)
    
    def on_deleted(self, event):
        """Handle file deletion events"""
        if event.is_directory:
            return
            
        # Check if it's an audio file
        if self._is_audio_file(event.src_path):
            # Avoid duplicate processing
            if event.src_path in self._last_processed and time.time() - self._last_processed[event.src_path] < 5:
                return
                
            self._last_processed[event.src_path] = time.time()
            print(f"File deleted: {event.src_path}")
            
            # Remove from downloaded tracks
            self._remove_from_downloaded_tracks(event.src_path)
    
    def on_moved(self, event):
        """Handle file move/rename events"""
        if event.is_directory:
            return
            
        # Check if source was an audio file
        if self._is_audio_file(event.src_path):
            # Avoid duplicate processing
            if event.src_path in self._last_processed and time.time() - self._last_processed[event.src_path] < 5:
                return
                
            self._last_processed[event.src_path] = time.time()
            print(f"File moved/renamed: {event.src_path} -> {event.dest_path}")
            
            # Remove old entry
            self._remove_from_downloaded_tracks(event.src_path)
            
            # Add new entry if destination is still an audio file
            if self._is_audio_file(event.dest_path):
                self._add_to_downloaded_tracks(event.dest_path)
    
    def _is_audio_file(self, file_path):
        """Check if the file is an audio file based on extension"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.mp3', '.m4a', '.flac', '.wav', '.opus', '.webm', '.mp4']
    
    def _add_to_downloaded_tracks(self, file_path):
        """Add a file to the downloaded tracks list"""
        try:
            # Load current downloaded tracks
            downloaded_tracks = {}
            if os.path.exists(DOWNLOADED_TRACKS_FILE):
                with open(DOWNLOADED_TRACKS_FILE, 'r') as f:
                    downloaded_tracks = json.load(f)
            
            # Process the file
            file_name = os.path.basename(file_path)
            file_base = os.path.splitext(file_name)[0]
            
            # Try to parse track name and artist
            parts = file_base.split(' - ', 1)
            if len(parts) == 2:
                track_name, artist_name = parts
                key = f"{track_name} - {artist_name}"
            else:
                key = file_base
            
            # Add to downloaded tracks if not already present
            if key not in downloaded_tracks:
                downloaded_tracks[key] = True
                print(f"Added {key} to downloaded tracks (auto)")
                
                # Save updated downloaded tracks
                with open(DOWNLOADED_TRACKS_FILE, 'w') as f:
                    json.dump(downloaded_tracks, f)
            
        except Exception as e:
            print(f"Error adding file to downloaded tracks: {e}")
    
    def _remove_from_downloaded_tracks(self, file_path):
        """Remove a file from the downloaded tracks list"""
        try:
            # Load current downloaded tracks
            if not os.path.exists(DOWNLOADED_TRACKS_FILE):
                return
                
            with open(DOWNLOADED_TRACKS_FILE, 'r') as f:
                downloaded_tracks = json.load(f)
            
            # Process the file
            file_name = os.path.basename(file_path)
            file_base = os.path.splitext(file_name)[0]
            
            # Try to find and remove the entry
            removed = False
            
            # Check direct filename match
            if file_base in downloaded_tracks:
                del downloaded_tracks[file_base]
                removed = True
                print(f"Removed {file_base} from downloaded tracks (auto)")
            
            # Check artist - track format
            parts = file_base.split(' - ', 1)
            if len(parts) == 2:
                track_name, artist_name = parts
                key = f"{track_name} - {artist_name}"
                if key in downloaded_tracks:
                    del downloaded_tracks[key]
                    removed = True
                    print(f"Removed {key} from downloaded tracks (auto)")
            
            # Save updated downloaded tracks if something was removed
            if removed:
                with open(DOWNLOADED_TRACKS_FILE, 'w') as f:
                    json.dump(downloaded_tracks, f)
            
        except Exception as e:
            print(f"Error removing file from downloaded tracks: {e}")

class DownloadManager:
    """Manager for handling track downloads"""
    
    def __init__(self, max_workers=1, notify_callback=None, progress_callback=None, download_progress_callback=None):
        self.max_workers = max_workers
        self.notify_callback = notify_callback
        self.progress_callback = progress_callback
        self.download_progress_callback = download_progress_callback or self._default_download_progress_callback
        self.executor = None
        self.download_queue = Queue()
        self.stop_flag = threading.Event()
        self.download_durations = []
        self.completed_downloads = 0
        self.active_downloads = {}  # Track ID -> download info
        self.download_history = self._load_download_history()
        
        # Check if notifications are working
        self.notifications_work = self._test_notifications()
        
        # Create executor for concurrent downloads
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        # Create worker thread for download queue
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        
        # Set up file system watcher for the downloads folder
        self._setup_file_watcher()
    
    def _setup_file_watcher(self):
        """Set up a file system watcher to monitor the downloads folder"""
        try:
            # Get download folder from config
            config = get_app_config()
            self.download_folder = config.get('custom_download_folder', DOWNLOAD_FOLDER)
            
            # Create event handler for file system events
            event_handler = DownloadFolderHandler(self)
            
            # Create observer to watch the folder
            self.observer = Observer()
            self.observer.schedule(event_handler, self.download_folder, recursive=False)
            self.observer.start()
            
            print(f"File watcher started for folder: {self.download_folder}")
            
        except Exception as e:
            print(f"Error setting up file watcher: {e}")
            self.observer = None
    
    def update_download_folder(self, new_folder):
        """Update the download folder path and restart the watcher"""
        if hasattr(self, 'observer') and self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.download_folder = new_folder
        self._setup_file_watcher()
    
    def stop_downloads(self):
        """Stop all active downloads and file watchers"""
        self.stop_flag.set()
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Stop the file watcher
        if hasattr(self, 'observer') and self.observer:
            self.observer.stop()
            self.observer.join(timeout=1)
            
        self.stop_flag.clear()
    
    def set_max_workers(self, max_workers):
        """Change the number of concurrent downloads"""
        if self.executor:
            self.executor.shutdown(wait=False)
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    def queue_download(self, tracks, collection_info=None):
        """Add tracks to download queue"""
        if not tracks:
            return False
        
        # If collection_info is provided, this is from an album or playlist
        if collection_info:
            # Store collection entry in history
            self._add_collection_to_history(collection_info, len(tracks))
        
        # Add each track to queue
        for track in tracks:
            self.download_queue.put((track, collection_info))
        
        return True
    
    def get_download_status(self):
        """Get current download status"""
        total_queued = self.download_queue.qsize()
        total_active = len(self.active_downloads)
        
        return {
            'queued': total_queued,
            'active': total_active,
            'completed': self.completed_downloads,
            'active_downloads': list(self.active_downloads.values())
        }
    
    def _process_queue(self):
        """Process download queue in background"""
        while True:
            try:
                # Get item from queue
                track, collection_info = self.download_queue.get(timeout=1)
                
                # Skip if stop flag is set
                if self.stop_flag.is_set():
                    self.download_queue.task_done()
                    continue
                
                # Check if already downloaded
                if self.is_track_downloaded(track['name'], track['artist']):
                    print(f"Skipping: {track['name']} by {track['artist']}, already downloaded.")
                    if self.notify_callback:
                        self.notify_callback("Track Already Downloaded", 
                                           f"{track['name']} by {track['artist']} has already been downloaded.")
                    self.completed_downloads += 1
                    if self.progress_callback:
                        self.progress_callback(f"Skipped: {track['name']}", 100)
                    self.download_queue.task_done()
                    continue
                
                # Add to active downloads
                self.active_downloads[track['id']] = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artist'],
                    'status': 'starting',
                    'progress': 0
                }
                
                # Submit download task to executor
                future = self.executor.submit(
                    self._download_track, 
                    track, 
                    collection_info
                )
                future.add_done_callback(
                    lambda f, track_id=track['id']: self._download_complete(f, track_id)
                )
                
                self.download_queue.task_done()
                
            except Empty:
                # Queue is empty, just continue
                pass
            except Exception as e:
                print(f"Error in download queue processing: {e}")
                time.sleep(1)
    
    def _download_complete(self, future, track_id):
        """Handle download completion"""
        try:
            result = future.result()
            if track_id in self.active_downloads:
                del self.active_downloads[track_id]
        except Exception as e:
            print(f"Download failed: {e}")
            if track_id in self.active_downloads:
                self.active_downloads[track_id]['status'] = 'failed'
                self.active_downloads[track_id]['error'] = str(e)
    
    def _download_track(self, track, collection_info=None):
        """
        Download a track and save it to the downloads folder.
        
        Args:
            track (dict): The track to download
            collection_info (dict, optional): The collection the track belongs to
        
        Returns:
            tuple: (success, filepath)
        """
        try:
            is_youtube = track.get('is_youtube', False) or track.get('youtube_url')
            
            if is_youtube:
                # Handle YouTube download
                return self._download_youtube_track(track, collection_info)
            else:
                # Handle Spotify track download
                return self._download_spotify_track(track, collection_info)
        except Exception as e:
            print(f"Error in download_track: {e}")
            import traceback
            traceback.print_exc()
            return False, None
    
    def _download_youtube_track(self, track, collection_info=None):
        """
        Download a track from YouTube.
        
        Args:
            track (dict): The track information
            collection_info (dict, optional): Collection information if part of a collection
            
        Returns:
            tuple: (success, filepath)
        """
        try:
            youtube_url = track.get('youtube_url')
            custom_filename = track.get('custom_filename')
            
            # Fallback to title if available
            if not custom_filename and track.get('video_title'):
                custom_filename = self._create_safe_filename(track.get('video_title'))
            
            print(f"Downloading from YouTube: {youtube_url}")
            print(f"Using filename: {custom_filename or 'auto-generated'}")
            
            # Get download folder from config
            config = get_app_config()
            download_folder = config.get('custom_download_folder', DOWNLOAD_FOLDER)
            
            # Ensure download folder exists
            if not os.path.exists(download_folder):
                try:
                    os.makedirs(download_folder, exist_ok=True)
                    print(f"Created download folder: {download_folder}")
                except Exception as e:
                    print(f"Error creating download folder: {e}")
                    if self.notify_callback:
                        self.notify_callback(f"Error creating download folder: {e}")
                    return False, None
                    
            # Clean up custom filename to avoid issues
            if custom_filename:
                custom_filename = self._create_safe_filename(custom_filename)
                # Remove file extension if present to avoid double extensions
                custom_filename = os.path.splitext(custom_filename)[0]
                print(f"Sanitized filename: {custom_filename}")
            
            # Set up download options with a template that generates a more predictable filename
            if custom_filename:
                # Use our custom filename
                output_template = os.path.join(download_folder, f"{custom_filename}.%(ext)s")
            else:
                # Let yt-dlp generate a safe filename based on the video title
                output_template = os.path.join(download_folder, "%(title)s.%(ext)s")
            
            print(f"Output template: {output_template}")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'restrictfilenames': True,  # Restrict filenames to ASCII, avoiding "&" and spaces in filenames
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '192',
                }],
                'progress_hooks': [lambda d: self._youtube_progress_hook({**d, 'track_id': track.get('id', track.get('youtube_url', str(uuid.uuid4())))})],
                'quiet': False,
                'verbose': True
            }
            
            # Perform the download
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=True)
                    print(f"Download info: {info.get('title')} - ID: {info.get('id')}")
                    
                    # Get the actual downloaded file path from info if available
                    if 'requested_downloads' in info and info['requested_downloads']:
                        for download in info['requested_downloads']:
                            if 'filepath' in download:
                                actual_file_path = download['filepath']
                                if os.path.exists(actual_file_path):
                                    print(f"Found downloaded file from info: {actual_file_path}")
                                    # If the file has a different extension than m4a (e.g., still webm)
                                    # we need to wait for post-processing to complete
                                    if not actual_file_path.lower().endswith('.m4a'):
                                        print("File needs post-processing, will search for final file")
                                        time.sleep(2)  # Give time for post-processing to complete
                                        actual_file_path = None
                                    else:
                                        return self._process_downloaded_file(actual_file_path, info, track)
                    
                    # If we couldn't get the file path from info, try to find it
                    if custom_filename:
                        base_file_path = os.path.join(download_folder, custom_filename)
                    else:
                        # Use the video title as filename
                        title = self._create_safe_filename(info.get('title', 'unknown'))
                        base_file_path = os.path.join(download_folder, title)
                    
                    print(f"Searching for downloaded file with base path: {base_file_path}")
                    
                    # Try to find the actual downloaded file
                    actual_file_path = self._get_actual_file_path(base_file_path)
                    
                    if actual_file_path:
                        return self._process_downloaded_file(actual_file_path, info, track)
                    else:
                        # Last resort: search for the most recently modified audio file
                        print("File not found with expected name, searching for recent files...")
                        
                        # List all files in download directory
                        try:
                            all_files = []
                            for file in os.listdir(download_folder):
                                file_path = os.path.join(download_folder, file)
                                if os.path.isfile(file_path) and file.lower().endswith(('.m4a', '.mp3', '.webm')):
                                    all_files.append((file_path, os.path.getmtime(file_path)))
                            
                            # Sort by modification time, newest first
                            all_files.sort(key=lambda x: x[1], reverse=True)
                            
                            if all_files:
                                # Get the most recently modified file
                                newest_file, _ = all_files[0]
                                print(f"Found most recent file: {newest_file}")
                                return self._process_downloaded_file(newest_file, info, track)
                        except Exception as e:
                            print(f"Error searching for recent files: {e}")
                        
                        # If we get here, we couldn't find the file
                        error_message = f"File not found after download: {base_file_path}"
                        print(error_message)
                        self._print_debug_info(download_folder)
                        
                        if self.notify_callback:
                            self.notify_callback(error_message)
                        return False, None
                    
            except Exception as e:
                error_message = f"Error downloading from YouTube: {str(e)}"
                print(error_message)
                import traceback
                traceback.print_exc()
                if self.notify_callback:
                    self.notify_callback(error_message)
                return False, None
        except Exception as e:
            print(f"Error in _download_youtube_track: {e}")
            import traceback
            traceback.print_exc()
            return False, None
            
    def _process_downloaded_file(self, file_path, info, track):
        """
        Process a downloaded file by embedding metadata
        
        Args:
            file_path (str): Path to the downloaded file
            info (dict): Video info from yt-dlp
            track (dict): Track information
            
        Returns:
            tuple: (success, filepath)
        """
        print(f"Processing downloaded file: {file_path}")
        
        try:
            # Get track_id for progress updates
            track_id = track.get('id', track.get('youtube_url', str(uuid.uuid4())))
            
            # Embed metadata
            yt_track = {
                'name': info.get('title', 'Unknown Title'),
                'artist': info.get('uploader', 'YouTube'),
                'album': info.get('uploader', 'YouTube'),
                'youtube_url': track.get('youtube_url')
            }
            
            # Handle potential file extension issues
            if not os.path.exists(file_path):
                print(f"Warning: File doesn't exist at expected path: {file_path}")
                # Try to find the file again
                base_path = os.path.splitext(file_path)[0]
                file_path = self._get_actual_file_path(base_path)
                if not file_path:
                    # Update progress to show failure
                    print(f"File not found, setting progress to 0% for track ID {track_id}")
                    self._default_download_progress_callback(track_id, 0)
                    return False, None
            
            # Update progress to show we're embedding metadata (90%)
            if self.progress_callback:
                self.progress_callback(f"Embedding metadata: {yt_track['name']}", 90)
            
            # Explicitly update progress to 90%
            print(f"Embedding metadata, setting progress to 90% for track ID {track_id}")
            self._default_download_progress_callback(track_id, 90)
            
            metadata_result = self._embed_youtube_metadata(file_path, yt_track)
            
            # Always update progress to 100% when complete, regardless of metadata embedding success
            if self.progress_callback:
                self.progress_callback(f"Completed: {yt_track['name']}", 100)
            
            # Explicitly update progress to 100%
            print(f"Download complete, setting progress to 100% for track ID {track_id}")
            self._default_download_progress_callback(track_id, 100)
            
            # Add to download history for YouTube tracks too
            try:
                youtube_track = {
                    'id': track_id,
                    'name': yt_track['name'],
                    'artist': yt_track['artist'],
                    'album': yt_track['album'],
                    'youtube_url': track.get('youtube_url')
                }
                self._add_track_to_history(youtube_track, None, file_path)
            except Exception as history_err:
                print(f"Failed to add YouTube track to history: {history_err}")
            
            if metadata_result:
                self.notify("Download Complete", f"{yt_track['name']} has been downloaded.")
                return True, file_path
            else:
                print(f"Failed to embed metadata for {file_path}")
                # Still return True since the file was downloaded
                return True, file_path
        except Exception as e:
            print(f"Error processing downloaded file: {e}")
            import traceback
            traceback.print_exc()
            # Update progress to show failure
            track_id = track.get('id', track.get('youtube_url', str(uuid.uuid4())))
            self._default_download_progress_callback(track_id, 0)
            return False, None
            
    def _print_debug_info(self, download_folder):
        """Print debug information about the download folder"""
        print(f"Debug info for download folder: {download_folder}")
        
        try:
            # Check if folder exists
            if not os.path.exists(download_folder):
                print(f"Download folder doesn't exist: {download_folder}")
                return
                
            # List files in download folder
            print(f"Files in download folder:")
            for file in os.listdir(download_folder):
                file_path = os.path.join(download_folder, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"  - {file} ({size} bytes, modified: {mtime_str})")
        except Exception as e:
            print(f"Error getting debug info: {e}")
    
    def _download_spotify_track(self, track, collection_info=None):
        """
        Download a track from Spotify by searching for it on YouTube.
        
        Args:
            track (dict): The track information
            collection_info (dict, optional): Collection information if part of a collection
            
        Returns:
            tuple: (success, filepath)
        """
        track_name = track['name']
        artist_name = track['artist']
        track_id = track['id']
        
        if self.is_track_downloaded(track_name, artist_name):
            print(f"Skipping: {track_name} by {artist_name}, already downloaded.")
            if self.notify_callback:
                self.notify_callback("Track Already Downloaded", 
                                   f"{track_name} by {artist_name} has already been downloaded.")
            self.completed_downloads += 1
            return True, None
        
        # Update status
        if track_id in self.active_downloads:
            self.active_downloads[track_id]['status'] = 'searching'
        if self.progress_callback:
            self.progress_callback(f"Searching: {track_name} - {artist_name}", 10)
        
        # Get audio quality from config
        audio_quality = AUDIO_QUALITY_OPTIONS.get("Medium", "192")
        audio_format = DEFAULT_AUDIO_FORMAT
        
        # Get download folder from config
        config = get_app_config()
        download_folder = config.get('custom_download_folder', DOWNLOAD_FOLDER)
        
        # Create download folder if it doesn't exist
        if not os.path.exists(download_folder):
            try:
                os.makedirs(download_folder, exist_ok=True)
                print(f"Created download folder: {download_folder}")
            except Exception as e:
                print(f"Error creating download folder: {e}")
                if self.progress_callback:
                    self.progress_callback(f"Error creating download folder: {e}", 0)
                return False, None
        
        # Create search query and file path
        search_query = f"{track_name} {artist_name} audio"
        safe_filename = self._create_safe_filename(f"{track_name} - {artist_name}.{audio_format}")
        output_template = os.path.join(download_folder, safe_filename)
        
        # Check if file already exists
        if os.path.exists(output_template):
            if self.progress_callback:
                self.progress_callback(f"File already exists: {track_name}", 100)
            
            # Mark as downloaded
            self._save_downloaded_track(track_name, artist_name)
            
            # Add to download history
            self._add_track_to_history(track, collection_info, output_template)
            
            # Send notification
            if self.notify_callback:
                self.notify_callback("Download Complete", 
                                  f"{track_name} by {artist_name} has been downloaded.")
            
            # Update counters
            self.completed_downloads += 1
            
            return True, output_template
        
        # Configure yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': audio_quality,
            }],
            'outtmpl': output_template,
            'quiet': True,
            'nocheckcertificate': True,
            'retries': 3,
            'default_search': 'ytsearch',
            'progress_hooks': [
                lambda d: self._progress_hook(d, track_id)
            ],
        }
        
        start_time = time.time()  # Track download start time
        
        try:
            # Update status
            if track_id in self.active_downloads:
                self.active_downloads[track_id]['status'] = 'downloading'
            
            # Perform download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([search_query])
            
            # Calculate download duration
            download_duration = time.time() - start_time
            self.download_durations.append(download_duration)
            
            # Check if download was canceled
            if self.stop_flag.is_set():
                if track_id in self.active_downloads:
                    self.active_downloads[track_id]['status'] = 'canceled'
                return False, None
            
            # Get base filename without extension
            base_filename = os.path.splitext(output_template)[0]
            
            # Try to find the actual downloaded file
            actual_file_path = self._get_actual_file_path(base_filename, audio_format)
            
            if actual_file_path:
                # File found, embed metadata
                if track_id in self.active_downloads:
                    self.active_downloads[track_id]['status'] = 'embedding_metadata'
                if self.progress_callback:
                    self.progress_callback(f"Embedding metadata: {track_name}", 80)
                
                # Embed metadata
                metadata_result = self._embed_metadata(actual_file_path, track)
                
                if metadata_result:
                    # Mark as downloaded
                    self._save_downloaded_track(track_name, artist_name)
                    
                    # Add to download history
                    self._add_track_to_history(track, collection_info, actual_file_path)
                    
                    # Send notification
                    if self.notify_callback:
                        self.notify_callback("Download Complete", 
                                          f"{track_name} by {artist_name} has been downloaded.")
                    
                    # Update counters
                    self.completed_downloads += 1
                    
                    # Update status
                    if self.progress_callback:
                        self.progress_callback(f"Completed: {track_name}", 100)
                    
                    return True, actual_file_path
                else:
                    if track_id in self.active_downloads:
                        self.active_downloads[track_id]['status'] = 'metadata_failed'
                    return False, None
            else:
                # No file found with any extension
                if track_id in self.active_downloads:
                    self.active_downloads[track_id]['status'] = 'file_not_found'
                if self.progress_callback:
                    self.progress_callback(f"File not found: {track_name}", 0)
                print(f"File not found: Tried {base_filename}.* but nothing found. Download folder is {download_folder}")
                print(f"Files in directory: {os.listdir(os.path.dirname(base_filename))}")
                return False, None
                
        except DownloadError as e:
            if track_id in self.active_downloads:
                self.active_downloads[track_id]['status'] = 'failed'
                self.active_downloads[track_id]['error'] = str(e)
            if self.progress_callback:
                self.progress_callback(f"Download failed: {track_name}", 0)
            return False, None
        except Exception as e:
            if track_id in self.active_downloads:
                self.active_downloads[track_id]['status'] = 'error'
                self.active_downloads[track_id]['error'] = str(e)
            if self.progress_callback:
                self.progress_callback(f"Error: {str(e)}", 0)
            return False, None
    
    def _progress_hook(self, d, track_id):
        """Handle download progress updates"""
        if track_id not in self.active_downloads:
            return
        
        if d['status'] == 'downloading':
            # Calculate download progress
            if 'total_bytes' in d and d['total_bytes'] > 0:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 70  # Cap at 70% for download phase
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 70
            else:
                progress = 30  # Default progress if we can't calculate
                
            # Update active download status
            self.active_downloads[track_id]['progress'] = progress
            self.active_downloads[track_id]['status'] = 'downloading'
            
            # Update progress callback if provided
            if self.progress_callback:
                filename = os.path.basename(d['filename'])
                self.progress_callback(f"Downloading: {filename} ({int(progress)}%)", progress)
                
        elif d['status'] == 'finished':
            # Download finished, update for post-processing
            self.active_downloads[track_id]['progress'] = 75
            self.active_downloads[track_id]['status'] = 'post_processing'
            
            if self.progress_callback:
                filename = os.path.basename(d['filename']).split('.')[0]
                self.progress_callback(f"Processing: {filename}", 75)
    
    def _embed_metadata(self, file_path, track):
        """Embed metadata into downloaded file"""
        try:
            audio = MP4(file_path)
            audio['\xa9nam'] = track['name']
            audio['\xa9ART'] = track['artist']
            audio['\xa9alb'] = track['album']
            audio['\xa9day'] = track['release_date']
            
            # Add track number if available
            if 'track_number' in track and track['track_number']:
                audio['trkn'] = [(track['track_number'], 0)]
            
            # Add disc number if available
            if 'disc_number' in track and track['disc_number']:
                audio['disk'] = [(track['disc_number'], 0)]
            
            # Add album art if available
            if 'album_art_url' in track and track['album_art_url']:
                try:
                    cover_data = requests.get(track['album_art_url']).content
                    audio['covr'] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
                except Exception as e:
                    print(f"Failed to add album art: {e}")
            
            audio.save()
            return True
        except Exception as e:
            print(f"Failed to embed metadata: {e}")
            return False
    
    def is_track_downloaded(self, track_name, artist_name):
        """Check if a track is already downloaded"""
        downloaded_tracks = self._load_downloaded_tracks()
        return f"{track_name} - {artist_name}" in downloaded_tracks
    
    def _save_downloaded_track(self, track_name, artist_name):
        """Save a track to the downloaded tracks list"""
        downloaded_tracks = self._load_downloaded_tracks()
        downloaded_tracks[f"{track_name} - {artist_name}"] = True
        with open(DOWNLOADED_TRACKS_FILE, 'w') as f:
            json.dump(downloaded_tracks, f)
    
    def _load_downloaded_tracks(self):
        """Load downloaded tracks list"""
        if os.path.exists(DOWNLOADED_TRACKS_FILE):
            with open(DOWNLOADED_TRACKS_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def _add_track_to_history(self, track, collection_info, file_path):
        """Add a track to download history"""
        history = self._load_download_history()
        
        timestamp = datetime.now().isoformat()
        track_history = {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artist'],
            'album': track['album'],
            'downloaded_at': timestamp,
            'file_path': file_path
        }
        
        # Add collection info if available
        if collection_info:
            track_history['collection'] = {
                'id': collection_info.get('id', ''),
                'name': collection_info.get('name', ''),
                'type': collection_info.get('type', '')
            }
        
        # Add to history
        history['tracks'].append(track_history)
        
        # Save updated history
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    
    def _add_collection_to_history(self, collection_info, track_count):
        """Add a collection entry to history"""
        history = self._load_download_history()
        
        timestamp = datetime.now().isoformat()
        collection_history = {
            'id': collection_info.get('id', ''),
            'name': collection_info.get('name', ''),
            'type': collection_info.get('type', ''),
            'track_count': track_count,
            'downloaded_at': timestamp
        }
        
        # Add to history
        history['collections'].append(collection_history)
        
        # Save updated history
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    
    def _load_download_history(self):
        """Load download history"""
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        
        # Create default history structure
        default_history = {
            'tracks': [],
            'collections': []
        }
        
        # Create history file
        with open(HISTORY_FILE, 'w') as f:
            json.dump(default_history, f, indent=2)
        
        return default_history
    
    def get_download_history(self):
        """Get download history"""
        return self._load_download_history()
    
    def clear_history(self):
        """Clear download history"""
        default_history = {
            'tracks': [],
            'collections': []
        }
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(default_history, f, indent=2)
    
    def sync_downloaded_tracks_with_folder(self):
        """
        Sync downloaded tracks with folder contents.
        This method:
        1. Adds new files found in the download folder to the downloaded_tracks list
        2. Removes entries from downloaded_tracks list if the files no longer exist
        """
        downloaded_tracks = self._load_downloaded_tracks()
        
        # Get download folder from config
        config = get_app_config()
        download_folder = config.get('custom_download_folder', DOWNLOAD_FOLDER)
        
        # Check if folder exists
        if not os.path.exists(download_folder):
            print(f"Download folder not found: {download_folder}")
            return
        
        # Get all music files from the folder
        folder_files = []
        for file_name in os.listdir(download_folder):
            if file_name.lower().endswith(('.m4a', '.mp3', '.webm', '.mp4', '.flac', '.wav', '.opus')):
                folder_files.append(os.path.join(download_folder, file_name))
                file_base = file_name.rsplit('.', 1)[0]
                
                # Skip if already in downloaded tracks
                if file_base in downloaded_tracks:
                    continue
                
                # Try to parse track name and artist
                parts = file_base.split(' - ', 1)
                if len(parts) == 2:
                    track_name, artist_name = parts
                    key = f"{track_name} - {artist_name}"
                    if key not in downloaded_tracks:
                        downloaded_tracks[key] = True
                        print(f"Added {key} to downloaded tracks")
                else:
                    # If can't parse, just add the whole filename
                    if file_base not in downloaded_tracks:
                        downloaded_tracks[file_base] = True
                        print(f"Added {file_base} to downloaded tracks")
        
        # Check for deleted files - go through downloaded_tracks and remove entries 
        # that don't have a corresponding file in the folder
        tracks_to_remove = []
        for track_key in downloaded_tracks:
            # Check if this entry corresponds to a file in the download folder
            found = False
            
            for file_path in folder_files:
                file_name = os.path.basename(file_path)
                file_base = file_name.rsplit('.', 1)[0]
                
                # Check if file matches this track entry
                if file_base == track_key:
                    found = True
                    break
                
                # Check if this is a track_name - artist_name entry
                parts = file_base.split(' - ', 1)
                if len(parts) == 2 and f"{parts[0]} - {parts[1]}" == track_key:
                    found = True
                    break
            
            # If no matching file found, mark for removal
            if not found:
                tracks_to_remove.append(track_key)
                
        # Remove tracks that don't have corresponding files
        for track_key in tracks_to_remove:
            del downloaded_tracks[track_key]
            print(f"Removed {track_key} from downloaded tracks (file no longer exists)")
        
        # Save updated downloaded tracks
        with open(DOWNLOADED_TRACKS_FILE, 'w') as f:
            json.dump(downloaded_tracks, f)
            
        if tracks_to_remove:
            print(f"Removed {len(tracks_to_remove)} tracks that no longer exist in download folder")
            
        return len(tracks_to_remove) > 0  # Return True if any tracks were removed
    
    def queue_youtube_download(self, youtube_url, custom_filename=None):
        """
        Queue a YouTube video for download as audio.
        
        Args:
            youtube_url (str): The YouTube URL to download from
            custom_filename (str, optional): A custom filename for the downloaded audio
        
        Returns:
            bool: True if queued successfully, False otherwise
        """
        try:
            # Validate YouTube URL
            youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
            if not re.match(youtube_pattern, youtube_url):
                error_message = f"Invalid YouTube URL: {youtube_url}"
                print(error_message)
                if self.notify_callback:
                    self.notify_callback(error_message)
                return False
            
            print(f"Processing YouTube URL: {youtube_url}")
            
            # Create a track-like object for the download
            track = {
                'youtube_url': youtube_url,
                'is_youtube': True,
                'custom_filename': custom_filename,
                'download_status': 'queued'
            }
            
            # Try to get video info to verify URL validity
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'skip_download': True}) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    print(f"Video title: {info.get('title')}")
                    track['video_title'] = info.get('title')
                    track['duration'] = info.get('duration')
            except Exception as e:
                error_message = f"Error fetching video info: {str(e)}"
                print(error_message)
                if self.notify_callback:
                    self.notify_callback(error_message)
                return False
            
            # Add track to download queue
            self.download_queue.put((track, None))
            
            print(f"Added YouTube download to queue: {track.get('video_title', youtube_url)}")
            
            # Start processing if not already running
            if not self.worker_thread.is_alive():
                self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
                self.worker_thread.start()
            
            return True
        
        except Exception as e:
            error_message = f"Error queueing YouTube download: {str(e)}"
            print(error_message)
            import traceback
            traceback.print_exc()
            if self.notify_callback:
                self.notify_callback(error_message)
            return False
    
    def _embed_youtube_metadata(self, file_path, track):
        """Embed basic metadata for YouTube downloads
        
        Args:
            file_path (str): Path to the audio file
            track (dict): Track information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
                
            # Get track info
            track_name = track.get('name', 'YouTube Download')
            artist_name = track.get('artist', 'YouTube')
            
            # For M4A files
            if file_path.endswith('.m4a'):
                try:
                    audio = MP4(file_path)
                    
                    # Set basic tags
                    audio['\xa9nam'] = track_name  # Title
                    audio['\xa9ART'] = artist_name  # Artist
                    audio['\xa9alb'] = track.get('album', 'YouTube')  # Album
                    
                    # Save changes
                    audio.save()
                    return True
                except Exception as e:
                    print(f"Error embedding M4A metadata: {e}")
                    return False
            
            # For MP3 files
            elif file_path.endswith('.mp3'):
                try:
                    from mutagen.id3 import ID3, TIT2, TPE1, TALB
                    
                    try:
                        audio = ID3(file_path)
                    except:
                        # Create ID3 tag if it doesn't exist
                        audio = ID3()
                    
                    audio['TIT2'] = TIT2(encoding=3, text=track_name)  # Title
                    audio['TPE1'] = TPE1(encoding=3, text=artist_name)  # Artist
                    audio['TALB'] = TALB(encoding=3, text=track.get('album', 'YouTube'))  # Album
                    
                    # Save changes
                    audio.save(file_path)
                    return True
                except Exception as e:
                    print(f"Error embedding MP3 metadata: {e}")
                    return False
            
            # Unsupported format
            else:
                print(f"Unsupported audio format for metadata embedding: {file_path}")
                return False
                
        except Exception as e:
            print(f"Failed to embed YouTube metadata: {e}")
            return False
    
    def _create_safe_filename(self, text):
        """Create a safe filename from the given text."""
        if not text:
            return ""
        # Replace invalid characters
        sanitized_text = re.sub(r'[<>:"/\\|?*]', '_', text)
        
        # Replace other problematic characters that might cause issues
        sanitized_text = sanitized_text.replace('–', '-')  # Replace en-dash with hyphen
        sanitized_text = sanitized_text.replace('—', '-')  # Replace em-dash with hyphen
        sanitized_text = sanitized_text.replace(''', "'")  # Replace smart quotes
        sanitized_text = sanitized_text.replace(''', "'")  # Replace other smart quote
        sanitized_text = sanitized_text.replace('"', '"')
        sanitized_text = sanitized_text.replace('"', '"')
        sanitized_text = sanitized_text.replace('\n', ' ')
        sanitized_text = sanitized_text.replace('\r', ' ')
        sanitized_text = sanitized_text.replace('\t', ' ')
        
        # Remove trailing dots and spaces
        sanitized_text = sanitized_text.strip(". ")
        
        return sanitized_text

    def _get_actual_file_path(self, base_path, expected_extension=None):
        """
        Find the actual file path regardless of extension differences.
        
        Args:
            base_path: Base path without extension or with expected extension
            expected_extension: Expected file extension (optional)
            
        Returns:
            Actual file path if found, None otherwise
        """
        # First check if the exact path exists
        if os.path.exists(base_path):
            return base_path
            
        # If path doesn't have extension, try various extensions
        if expected_extension and not base_path.endswith(f".{expected_extension}"):
            base_path_with_ext = f"{base_path}.{expected_extension}"
            if os.path.exists(base_path_with_ext):
                return base_path_with_ext
        
        # Get base path without extension
        base_name = os.path.splitext(base_path)[0]
        
        # Try different extensions
        for ext in ['m4a', 'mp3', 'webm', 'mp4', 'flac', 'wav', 'opus']:
            test_path = f"{base_name}.{ext}"
            if os.path.exists(test_path):
                print(f"Found file with different extension: {test_path}")
                return test_path
                
        # If still not found, try looking for similar files in the directory
        dir_path = os.path.dirname(base_path)
        base_filename = os.path.basename(base_name)
        
        if not os.path.exists(dir_path):
            print(f"Directory doesn't exist: {dir_path}")
            return None
            
        try:
            # Look for files with similar names or by using glob pattern
            # First try a glob pattern with wildcard to catch special character variations
            import glob
            
            # Handle case where base_name might already have an extension
            if '.' in os.path.basename(base_name):
                # Remove any existing extensions to avoid double extensions
                clean_base_name = os.path.splitext(base_name)[0]
                base_pattern = os.path.join(dir_path, f"{os.path.basename(clean_base_name)}.*")
            else:
                base_pattern = os.path.join(dir_path, f"{os.path.basename(base_name)}.*")
                
            print(f"Searching for files matching pattern: {base_pattern}")
            matching_files = glob.glob(base_pattern)
            
            # Filter to only audio files and fix potential double extensions
            valid_extensions = ('.mp3', '.m4a', '.webm', '.mp4', '.flac', '.wav', '.opus')
            matching_files = [f for f in matching_files if f.lower().endswith(valid_extensions)]
            
            # Check for duplicate extensions like .m4a.m4a
            for i, file_path in enumerate(matching_files):
                filename = os.path.basename(file_path)
                for ext in valid_extensions:
                    # Check for patterns like ext.ext (e.g., .m4a.m4a)
                    duplicate_ext = f"{ext}{ext}"
                    if duplicate_ext.lower() in filename.lower():
                        # Fix the path with duplicate extension
                        fixed_filename = filename.lower().replace(duplicate_ext.lower(), ext)
                        corrected_path = os.path.join(dir_path, fixed_filename)
                        try:
                            # Rename the file to fix the extension
                            if os.path.exists(file_path) and not os.path.exists(corrected_path):
                                print(f"Fixing duplicate extension: {file_path} → {corrected_path}")
                                os.rename(file_path, corrected_path)
                                matching_files[i] = corrected_path
                            elif os.path.exists(corrected_path):
                                print(f"Fixed filename already exists: {corrected_path}")
                                matching_files[i] = corrected_path
                        except Exception as e:
                            print(f"Failed to fix duplicate extension: {e}")
                            if os.path.exists(file_path):
                                # Just use the original path if rename fails
                                matching_files[i] = file_path
            
            if matching_files:
                newest_file = max(matching_files, key=os.path.getmtime)
                print(f"Found matching file: {newest_file}")
                return newest_file

            # If still not found, try a more aggressive glob with * for each word
            # This helps with special characters that might have been replaced
            parts = os.path.basename(base_name).split()
            if len(parts) > 1:
                # Create a pattern that matches each word with wildcard
                word_pattern = "*".join([f"{part}*" for part in parts if len(part) > 2])
                loose_pattern = os.path.join(dir_path, f"*{word_pattern}*")
                print(f"Trying loose pattern: {loose_pattern}")
                loose_matches = glob.glob(loose_pattern)
                loose_matches = [f for f in loose_matches if f.lower().endswith(valid_extensions)]
                
                # Check for duplicate extensions in loose matches too
                for i, file_path in enumerate(loose_matches):
                    filename = os.path.basename(file_path)
                    for ext in valid_extensions:
                        # Check for patterns like ext.ext (e.g., .m4a.m4a)
                        duplicate_ext = f"{ext}{ext}"
                        if duplicate_ext.lower() in filename.lower():
                            # Fix the path with duplicate extension
                            fixed_filename = filename.lower().replace(duplicate_ext.lower(), ext)
                            corrected_path = os.path.join(dir_path, fixed_filename)
                            try:
                                # Rename the file to fix the extension
                                if os.path.exists(file_path) and not os.path.exists(corrected_path):
                                    print(f"Fixing duplicate extension: {file_path} → {corrected_path}")
                                    os.rename(file_path, corrected_path)
                                    loose_matches[i] = corrected_path
                                elif os.path.exists(corrected_path):
                                    print(f"Fixed filename already exists: {corrected_path}")
                                    loose_matches[i] = corrected_path
                            except Exception as e:
                                print(f"Failed to fix duplicate extension: {e}")
                                if os.path.exists(file_path):
                                    # Just use the original path if rename fails
                                    loose_matches[i] = file_path
                
                if loose_matches:
                    newest_file = max(loose_matches, key=os.path.getmtime)
                    print(f"Found with loose matching: {newest_file}")
                    return newest_file
            
            # Fall back to last modified approach
            files = []
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path):
                    # Check if file has audio extension
                    if file.lower().endswith(valid_extensions):
                        # Get modification time
                        files.append((file_path, os.path.getmtime(file_path)))
            
            # Sort by last modified time (newest first)
            files.sort(key=lambda x: x[1], reverse=True)
            
            # Check first 5 newest files (most likely our download)
            if files:
                print(f"Found {len(files)} potential files, checking newest ones")
                for file_path, _ in files[:5]:
                    print(f"Checking recent file: {file_path}")
                    return file_path
        except Exception as e:
            print(f"Error during file search: {e}")
            
        print(f"File not found: Tried {base_path}.* but nothing found. Download folder is {dir_path}")
        # List all files in the directory for debugging
        try:
            print("Files in directory:")
            for f in os.listdir(dir_path):
                print(f"  - {f}")
        except Exception as e:
            print(f"Error listing directory: {e}")
            
        return None

    def _youtube_progress_hook(self, d):
        """Progress hook for youtube-dl"""
        try:
            # Get track_id
            track_id = d.get('track_id')
            if not track_id:
                return
                
            # Handle different download statuses
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total_bytes > 0:
                    # Cap at 75% during download phase, reserve 25% for post-processing
                    downloaded = d.get('downloaded_bytes', 0)
                    progress = min(75, int(downloaded / total_bytes * 75))
                    print(f"YouTube download progress: {progress}% for track ID {track_id}")
                    self._default_download_progress_callback(track_id, progress)
            
            elif d['status'] == 'finished':
                # Set to 80% when download is finished but processing is still happening
                print(f"YouTube download finished, processing at 80% for track ID {track_id}")
                self._default_download_progress_callback(track_id, 80)
                
            elif d['status'] == 'error':
                # Reset progress on error
                print(f"YouTube download error for track ID {track_id}")
                self._default_download_progress_callback(track_id, 0)
                
        except Exception as e:
            # Ensure progress is reset in case of any errors
            if 'track_id' in d:
                self._default_download_progress_callback(d['track_id'], 0)
            print(f"Error in YouTube progress hook: {e}")
    
    def _test_notifications(self):
        """Test if notifications can be shown without errors"""
        if self.notify_callback:
            try:
                # Try to send a test notification but don't actually display it
                # Remove the silent parameter since it's not supported
                return True
            except Exception as e:
                print(f"Notification error: {e}")
                self.notifications_work = False
                return False
        return False
        
    def notify(self, title, message):
        """Safe wrapper for notification callback"""
        if self.notify_callback and self.notifications_work:
            try:
                self.notify_callback(title, message)
            except Exception as e:
                # If notification fails, disable notifications and log once
                self.notifications_work = False
                print(f"Notification error: {e}")
                # Fallback to console output
                print(f"NOTIFICATION: {title} - {message}")

    def _default_download_progress_callback(self, track_id, progress):
        """Default implementation when no external callback is provided"""
        if track_id in self.active_downloads:
            self.active_downloads[track_id]['progress'] = progress
            if progress == 0:
                self.active_downloads[track_id]['status'] = 'failed'
            elif progress == 100:
                self.active_downloads[track_id]['status'] = 'completed'
            elif progress >= 80:
                self.active_downloads[track_id]['status'] = 'processing'
            else:
                self.active_downloads[track_id]['status'] = 'downloading'