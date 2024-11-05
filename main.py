import atexit
import json
import os
import re
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

import requests
import ttkbootstrap as ttk
import yt_dlp
from mutagen.mp4 import MP4, MP4Cover
from plyer import notification
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from yt_dlp.utils import DownloadError

DOWNLOAD_FOLDER = 'downloads'
CREDENTIALS_FILE = 'credentials.json'
DOWNLOADED_TRACKS_FILE = 'downloaded_tracks.json'
THEMES = ['cosmo', 'flatly', 'litera', 'minty', 'lumen',
 'sandstone', 'yeti', 'pulse', 'united', 'morph', 'journal',
  'darkly', 'superhero', 'solar', 'cyborg', 'vapor', 'simplex',
   'cerculean']

playlist_queue = []  
download_durations = []
completed_downloads = 0 
QUEUE_FILE = 'playlist_queue.json'
STATUS_FILE = 'download_status.json'

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return None

credentials = load_credentials()

if credentials: 
    spotify = Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret']
        ),
        requests_timeout=10
    )
else:
    print("Error: No Spotify credentials found.")

def save_playlist_status(playlist_id, status):
    status_data = {}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            status_data = json.load(f)
    
    status_data[playlist_id] = status
    with open(STATUS_FILE, 'w') as f:
        json.dump(status_data, f)

def load_playlist_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_playlist_queue(queue):
    with open('playlist_queue.json', 'w') as f:
        json.dump(queue, f)

def load_playlist_queue():
    if os.path.exists('playlist_queue.json'):
        with open('playlist_queue.json', 'r') as f:
            return json.load(f)
    return []

def populate_queue_listbox():
    queue_listbox.delete(0, tk.END)  
    for playlist_id in playlist_queue:
        queue_listbox.insert(tk.END, playlist_id)

playlist_queue = load_playlist_queue() 
stop_flag = threading.Event() 
completed_downloads = 0

class DownloadFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.m4a'):
            file_name = os.path.basename(event.src_path).split('.m4a')[0]
            try:
                track_name, artist_name = file_name.rsplit(' - ', 1) 
            except ValueError:
                print(f"Could not extract track and artist from: {file_name}")
                return
            
            save_downloaded_track(track_name, artist_name)
            print(f"Added {track_name} - {artist_name} to downloaded_tracks.json")

    def on_deleted(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.m4a'):
            file_name = os.path.basename(event.src_path).split('.m4a')[0]
            downloaded_tracks = load_downloaded_tracks()
            if file_name in downloaded_tracks:
                del downloaded_tracks[file_name]
                with open(DOWNLOADED_TRACKS_FILE, 'w') as f:
                    json.dump(downloaded_tracks, f)
                print(f"Removed {file_name} from downloaded_tracks.json")

observer = Observer()
event_handler = DownloadFolderHandler()
observer.schedule(event_handler, path=DOWNLOAD_FOLDER, recursive=False)
observer.start()

atexit.register(lambda: observer.stop())

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def save_credentials(client_id, client_secret):
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump({'client_id': client_id, 'client_secret': client_secret}, f)

def load_downloaded_tracks():
    if os.path.exists(DOWNLOADED_TRACKS_FILE):
        with open(DOWNLOADED_TRACKS_FILE, 'r') as f:
            return json.load(f)
    return {}

def load_and_resume_downloads():
    load_playlist_queue()
    status_data = load_playlist_status()

    for playlist_id in playlist_queue:
        if status_data.get(playlist_id) == 'completed':
            playlist_queue.remove(playlist_id)
        else:
            print(f"Resuming download for playlist {playlist_id}")

    save_playlist_queue() 

def save_downloaded_track(track_name, artist_name):
    downloaded_tracks = load_downloaded_tracks()
    downloaded_tracks[f"{track_name} - {artist_name}"] = True
    with open(DOWNLOADED_TRACKS_FILE, 'w') as f:
        json.dump(downloaded_tracks, f)

def contains_non_latin(text):
    return bool(re.search('[\u0600-\u06FF\u0400-\u04FF]', text)) 
    
def sync_downloaded_tracks_with_folder(initial_run=True):
    downloaded_tracks = load_downloaded_tracks()
    files_in_folder = os.listdir(DOWNLOAD_FOLDER)

    for file_name in files_in_folder:
        if file_name.endswith('.m4a'):
            file_name = file_name.split('.m4a')[0]
            try:
                if contains_non_latin(file_name):
                    track_name = file_name.strip()
                    artist_name = "Unknown Artist"
                else:
                    match = re.match(r'^(.*?)(?:\s*-\s*|\s*by\s*)(.*)$', file_name)
                    if match:
                        track_name = match.group(1).strip()
                        artist_name = match.group(2).strip()
                    else:
                        track_name = file_name.strip()
                        artist_name = "Unknown Artist"

            except Exception as e:
                print(f"Could not extract track and artist from: {file_name}. Error: {e}")
                continue

            if f"{track_name} - {artist_name}" not in downloaded_tracks:
                downloaded_tracks[f"{track_name} - {artist_name}"] = True
                print(f"Adding {track_name} - {artist_name} to downloaded_tracks.json")

    if initial_run:
        with open(DOWNLOADED_TRACKS_FILE, 'w') as f:
            json.dump(downloaded_tracks, f)
        print("All songs have been loaded into downloaded_tracks.json.")
    else:
        print("Sync completed, but not saving since it's not the initial run.")

sync_downloaded_tracks_with_folder()

def is_track_downloaded(track_name, artist_name):
    downloaded_tracks = load_downloaded_tracks()
    return f"{track_name} - {artist_name}" in downloaded_tracks

def are_all_tracks_downloaded(tracks):
    for track in tracks:
        if not is_track_downloaded(track['name'], track['artist']):
            return False
    return True

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name='Spotify Downloader',
        timeout=5
    )

def notify_download_completion(tracks):
    global download_durations
    if are_all_tracks_downloaded(tracks):
        show_notification("Download Complete", "All tracks from the playlist/album have been successfully downloaded.")
        status_label.config(text="All tracks are already downloaded.")
        progress_var.set(100)
        remaining_label.config(text="Tracks remaining: 0 | Estimated time remaining: 0m 0s")

        download_durations.clear()  # Clear download durations for next playlist

        if playlist_queue:
            playlist_queue.pop(0)
            save_playlist_queue()
    else:
        status_label.config(text="Some tracks were not downloaded successfully.")


def authenticate_spotify(client_id, client_secret):
    credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return Spotify(client_credentials_manager=credentials)

def get_playlist_tracks(spotify, playlist_id):
    try:
        results = spotify.playlist_tracks(playlist_id)
        return [get_track(spotify, item['track']['id']) for item in results['items'] if item['track']]
    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
        return []

def get_album_tracks(spotify, album_id):
    try:
        results = spotify.album_tracks(album_id)
        return [{
            'name': item['name'],
            'artist': ', '.join(artist['name'] for artist in item['artists']),
            'album': spotify.album(album_id)['name'],
            'duration_ms': item['duration_ms'],
            'release_date': spotify.album(album_id)['release_date'],
            'artists': item['artists']
        } for item in results['items']]
    except Exception as e:
        print(f"Error fetching album tracks: {e}")
        return []
    
def parse_track_info(file_name):
    try:
        match = re.match(r'^(.*?)\s*(?:\((.*?)\))?\s*-\s*(.*)', file_name)
        if match:
            track_name = match.group(1).strip()
            artist_name = match.group(3).strip() 
            return track_name, artist_name
        else:
            return file_name, "Unknown Artist"
    except Exception as e:
        print(f"Error parsing track info from '{file_name}': {e}")
        return file_name, "Unknown Artist"
        
def embed_metadata(file_path, track):
    try:
        audio = MP4(file_path)
        audio['\xa9nam'] = track['name']
        audio['\xa9ART'] = track['artist']
        audio['\xa9alb'] = track['album']
        audio['\xa9day'] = track['release_date']
        
        if track['album_art_url']:
            cover_data = requests.get(track['album_art_url']).content
            audio['covr'] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
        
        audio.save()
        return True
    except Exception as e:
        print(f"Failed to embed metadata: {e}")
        return False
    finally:
        status_label.config(text=f"Metadata embedding complete for {track['name']}.")
        progress_var.set(100)

def update_progress(progress_var, status_label, step_description, current_step, total_steps,total_tracks):
    # Calculate the progress as a percentage
    progress_percentage = (current_step / total_steps) * 100
    progress_var.set(progress_percentage)
    
    # Update the status label with the current step's description
    status_label.config(text=f"{step_description} - {int(progress_percentage)}% completed")

    # Force the GUI to update immediately
    status_label.update_idletasks()

    update_remaining_tracks(total_tracks, remaining_label)

def download_track(track, progress_var, status_label, stop_flag, total_tracks, remaining_label):
    global completed_downloads, download_durations
    track_name = track['name']
    artist_name = track['artist']

    if is_track_downloaded(track_name, artist_name):
        status_label.config(text=f"Skipping: {track_name} by {artist_name}, already downloaded.")
        show_notification("Track Already Downloaded", f"{track_name} by {artist_name} has already been downloaded.")
        completed_downloads += 1
        update_remaining_tracks(total_tracks, remaining_label)
        return None

    yt_search = f"{track_name} {artist_name}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, f"{track_name} - {artist_name}.%(ext)s"),
        'quiet': True,
        'nocheckcertificate': True,
        'http_chunk_size': 0,
        'retries': 3,
        'default_search': 'ytsearch',
    }

    start_time = time.time()  # Track download start time

    try:
        status_label.config(text=f"Downloading: {track_name} - {artist_name}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_search])

        # Stop the timer once download completes
        download_duration = time.time() - start_time
        download_durations.append(download_duration)  # Store this duration

        if stop_flag.is_set():
            status_label.config(text="Download canceled.")
            return

        downloaded_file = os.path.join(DOWNLOAD_FOLDER, f"{track_name} - {artist_name}.m4a")
        if os.path.exists(downloaded_file):
            status_label.config(text=f"Embedding metadata for {track_name}...")
            if embed_metadata(downloaded_file, track):
                save_downloaded_track(track_name, artist_name)
                show_notification("Download Complete", f"{track_name} by {artist_name} has been downloaded.")
                completed_downloads += 1
                update_remaining_tracks(total_tracks, remaining_label)
            return downloaded_file
        else:
            status_label.config(text=f"File not found after download: {track_name} - {artist_name}.")
            return None
    except yt_dlp.utils.DownloadError as e:
        status_label.config(text=f"Download failed for {track_name} by {artist_name}: {e}")
        return None
    except Exception as e:
        status_label.config(text=f"Error: {e}")
        return None


def update_remaining_tracks(total_tracks, remaining_label):
    global completed_downloads, download_durations
    
    remaining_tracks = total_tracks - completed_downloads
    if remaining_tracks <= 0:
        remaining_tracks = 0
        estimated_remaining_time = 0
    else:
        # Calculate average download time
        if download_durations:
            avg_download_time = sum(download_durations) / len(download_durations)
            estimated_remaining_time = avg_download_time * remaining_tracks
        else:
            estimated_remaining_time = 0

    # Convert remaining time to minutes and seconds
    minutes, seconds = divmod(int(estimated_remaining_time), 60)
    remaining_label.config(text=f"Tracks remaining: {remaining_tracks} | Estimated time remaining: {minutes}m {seconds}s")

    
def download_album(spotify, album_id, progress_var, status_label, stop_flag, remaining_label):
    tracks = get_album_tracks(spotify, album_id)
    total_tracks = len(tracks)
    
    if not tracks:
        status_label.config(text="No tracks found in the album.")
        return

    for track in tracks:
        if stop_flag.is_set():
            break
        download_track(track, progress_var, status_label, stop_flag, total_tracks, remaining_label)

    notify_download_completion(tracks)

def download_playlist(client_id, client_secret, playlist_id, progress_var, status_label, stop_flag, remaining_label):
    spotify = authenticate_spotify(client_id, client_secret)
    tracks = get_playlist_tracks(spotify, playlist_id)
    
    if not tracks:
        status_label.config(text="No tracks found in the playlist.")
        return

    total_tracks = len(tracks)
    for track in tracks:
        if stop_flag.is_set():
            break
        download_track(track, progress_var, status_label, stop_flag, total_tracks, remaining_label)


def get_spotify_link_type(link):
    if 'album' in link:
        return 'album'
    elif 'track' in link:
        return 'track'
    elif 'playlist' in link:
        return 'playlist'
    else:
        return None

def extract_id_from_link(link):
    # Handle links with query parameters
    if '?si=' in link:
        link = link.split('?si=')[0]  # Remove any query params
    
    # Use regex to find the ID in the URL
    match = re.search(r'(album|playlist|track)/([a-zA-Z0-9]{22})', link)
    if match:
        return match.group(2)  # Return the ID
    return None  # If no match found


def is_valid_playlist_id(playlist_id):
    return bool(re.match(r'^[0-9A-Za-z]{22}$', playlist_id))

def get_spotify_content(spotify, link):
    link_type = get_spotify_link_type(link)
    content_id = extract_id_from_link(link)
    
    if link_type == 'playlist' and not is_valid_playlist_id(content_id):
        print(f"Invalid playlist ID: {content_id}")
        return []

    if link_type == 'playlist':
        return get_playlist_tracks(spotify, content_id)
    elif link_type == 'album':
        return get_album_tracks(spotify, content_id)
    elif link_type == 'track':
        return [get_track(spotify, content_id)]
    else:
        print(f"Unsupported link type: {link_type}")
        return None

def get_album_tracks(spotify, album_id):
    tracks = []
    results = spotify.album_tracks(album_id)
    for item in results['items']:
        tracks.append({
            'name': item['name'],
            'artist': ', '.join(artist['name'] for artist in item['artists']),
            'album': spotify.album(album_id)['name'],
            'album_art_url': spotify.album(album_id)['images'][0]['url'] if spotify.album(album_id)['images'] else '',
            'duration_ms': item['duration_ms'],
            'release_date': spotify.album(album_id)['release_date'],
            'artists': item['artists']
        })
    return tracks

def get_track(spotify, track_id):
    try:
        track = spotify.track(track_id)
        return {
            'name': track['name'],
            'artist': ', '.join(artist['name'] for artist in track['artists']),
            'album': track['album']['name'],
            'duration_ms': track['duration_ms'],
            'release_date': track['album']['release_date'],
            'artists': track['artists']
        }
    except Exception as e:
        print(f"Error fetching track: {e}")
        return None

playlist_queue = []
stop_flag = threading.Event()

def add_playlist_to_queue():
    playlist_id = playlist_id_entry.get()
    if playlist_id:
        playlist_queue.append(playlist_id)
        save_playlist_queue(playlist_queue)
        populate_queue_listbox() 
        playlist_id_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter a Playlist ID or Link.")


def remove_selected_from_queue():
    selected_index = queue_listbox.curselection()
    if selected_index:
        playlist_queue.pop(selected_index[0]) 
        queue_listbox.delete(selected_index) 
    else:
        messagebox.showwarning("Selection Error", "Please select a playlist to remove.")

def start_queue_download(client_id, client_secret, progress_var, status_label, remaining_label):
    try:
        # Step 1: Authenticate with Spotify
        update_progress(progress_var, status_label, "Authenticating with Spotify", 1, 5, total_tracks=1)
        spotify = authenticate_spotify(client_id, client_secret)
        
        # Step 2: Fetch Playlist Data
        update_progress(progress_var, status_label, "Fetching Playlist Data", 2, 5, total_tracks=1)
        playlist_id = playlist_id_entry.get()
        tracks = get_playlist_tracks(spotify, playlist_id)
        total_tracks = len(tracks)
        
        if total_tracks == 0:
            status_label.config(text="No tracks found in the playlist.")
            return
        if not playlist_queue:
            status_label.config(text="Download queue is empty.")
            return
        # Step 3: Check for Previously Downloaded Tracks
        _queue_download(spotify, progress_var, status_label, remaining_label)
        update_progress(progress_var, status_label, "Checking for Previously Downloaded Tracks", 3, 5, total_tracks)
        if are_all_tracks_downloaded(tracks):
            status_label.config(text="All tracks already downloaded.")
            return

        # Step 4: Download Tracks
        completed_downloads = 0
        for track in tracks:
            if stop_flag.is_set():  # Stop if the cancel button is pressed
                status_label.config(text="Download canceled.")
                return
            
            # Update progress for each track download
            update_progress(progress_var, status_label, f"Downloading {track['name']} by {track['artist']}", 4, 5, total_tracks)
            download_track(track, progress_var, status_label, stop_flag, total_tracks, remaining_label)
            completed_downloads += 1
            
            # Update remaining_label after each track download
            update_remaining_tracks(total_tracks, remaining_label)

        # Step 5: Finalizing Download and Saving Data
        update_progress(progress_var, status_label, "Finalizing and Saving Data", 5, 5, total_tracks)
        save_playlist_queue()
        status_label.config(text="Download complete!")
        progress_var.set(100)
        remaining_label.config(text="Tracks remaining: 0")

    except Exception as e:
        status_label.config(text=f"Error during download: {e}")

def _queue_download(spotify, progress_var, status_label, remaining_label):
    global completed_downloads
    completed_downloads = 0  # Reset completed downloads count

    # Process each playlist link in the queue
    while playlist_queue:
        current_playlist = playlist_queue.pop(0)  # Get the next playlist from the queue
        tracks = get_spotify_content(spotify, current_playlist)
        
        if not tracks:
            status_label.config(text=f"Invalid Spotify link: {current_playlist}")
            continue  # Skip to the next playlist if invalid

        total_tracks = len(tracks)

        for track in tracks:
            if stop_flag.is_set():
                break  # Stop if the cancel button is pressed
            
            # Download the track
            download_track(track, progress_var, status_label, stop_flag, total_tracks, remaining_label)
            completed_downloads += 1
            
            # Update remaining label after each track download
            update_remaining_tracks(total_tracks, remaining_label)

        notify_download_completion(tracks)  # Notify user for each completed playlist

    status_label.config(text="All playlists in the queue have been downloaded.")


def cancel_download():
    stop_flag.set()     
    messagebox.showinfo("Cancel", "Canceling the download...")

def on_exit():
    save_playlist_queue(playlist_queue) 
    observer.stop()
    root.quit()     

def apply_theme(theme_name):
    root.style.theme_use(theme_name)
    save_credentials(client_id_entry.get(), client_secret_entry.get())  

root = ttk.Window(themename='cyborg')  
root.title("Motify")
root.geometry("281x739")

credentials_frame = ttk.LabelFrame(root, text="Spotify Credentials")
credentials_frame.pack(pady=10, padx=10, fill=tk.X)

ttk.Label(credentials_frame, text="Client ID:").pack(anchor=tk.W, padx=10)
client_id_entry = ttk.Entry(credentials_frame)
client_id_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

ttk.Label(credentials_frame, text="Client Secret:").pack(anchor=tk.W, padx=10)
client_secret_entry = ttk.Entry(credentials_frame, show='*')
client_secret_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

playlist_frame = ttk.LabelFrame(root, text="Playlist Input")
playlist_frame.pack(pady=10, padx=10, fill=tk.X)

ttk.Label(playlist_frame, text="Playlist ID or Link:").pack(anchor=tk.W, padx=10, pady=(20, 0))
playlist_id_entry = ttk.Entry(playlist_frame)
playlist_id_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

add_to_queue_button = ttk.Button(playlist_frame, text="Add to Queue", command=add_playlist_to_queue)
add_to_queue_button.pack(pady=5)

remove_from_queue_button = ttk.Button(playlist_frame, text="Remove from Queue", command=remove_selected_from_queue)
remove_from_queue_button.pack(pady=(0, 10), padx=10) 

ttk.Label(root, text="Download Queue:").pack(anchor=tk.W, padx=10)
queue_listbox = tk.Listbox(root, height=6)
queue_listbox.pack(fill=tk.X, padx=10, pady=5)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, padx=10, fill=tk.X)

status_label = ttk.Label(root, text="Status: Ready")
status_label.pack(pady=5)

remaining_label = ttk.Label(root, text="Tracks remaining: 0")
remaining_label.pack(pady=5)

button_frame = ttk.Frame(root)
button_frame.pack(pady=5, padx=10)

start_download_button = ttk.Button(button_frame, text="Start Download", command=lambda: start_queue_download(client_id_entry.get(), client_secret_entry.get(), progress_var, status_label, remaining_label))
start_download_button.grid(row=0, column=0, padx=5)

cancel_download_button = ttk.Button(button_frame, text="Cancel", command=cancel_download)
cancel_download_button.grid(row=0, column=1, padx=5)

theme_label = ttk.Label(root, text="Choose Theme:")
theme_label.pack(anchor=tk.W, padx=10)

theme_combobox = ttk.Combobox(root, values=THEMES)
theme_combobox.set(THEMES[0])
theme_combobox.pack(fill=tk.X, padx=10, pady=5)
theme_combobox.bind('<<ComboboxSelected>>', lambda e: apply_theme(theme_combobox.get()))

credentials = load_credentials()
if credentials:
    client_id_entry.insert(0, credentials['client_id'])
    client_secret_entry.insert(0, credentials['client_secret'])


root.protocol("WM_DELETE_WINDOW", on_exit)

playlist_queue = load_playlist_queue() 
populate_queue_listbox()
root.mainloop()