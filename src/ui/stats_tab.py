import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import json
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')  # Set backend
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.dates as mdates

class StatsTab:
    """Tab for displaying download statistics and analytics"""
    
    def __init__(self, parent, download_manager, status_callback):
        self.parent = parent
        self.download_manager = download_manager
        self.status_callback = status_callback
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        
        # Refresh stats
        self.refresh_stats()
    
    def _create_widgets(self):
        """Create statistics tab widgets"""
        # Summary stats section
        summary_frame = ttk.LabelFrame(self.frame, text="Summary")
        summary_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Stats grid
        stats_grid = ttk.Frame(summary_frame)
        stats_grid.pack(padx=10, pady=10, fill=tk.X)
        
        # Total downloads
        ttk.Label(stats_grid, text="Total Downloads:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.total_downloads_label = ttk.Label(stats_grid, text="0")
        self.total_downloads_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Last 7 days
        ttk.Label(stats_grid, text="Last 7 Days:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10), pady=5)
        self.last_7_days_label = ttk.Label(stats_grid, text="0")
        self.last_7_days_label.grid(row=0, column=3, sticky=tk.W, pady=5)
        
        # Total albums
        ttk.Label(stats_grid, text="Albums Downloaded:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.albums_label = ttk.Label(stats_grid, text="0")
        self.albums_label.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Total playlists
        ttk.Label(stats_grid, text="Playlists Downloaded:").grid(row=1, column=2, sticky=tk.W, padx=(20, 10), pady=5)
        self.playlists_label = ttk.Label(stats_grid, text="0")
        self.playlists_label.grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # Total space
        ttk.Label(stats_grid, text="Total Storage Used:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.storage_label = ttk.Label(stats_grid, text="0 MB")
        self.storage_label.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Average quality
        ttk.Label(stats_grid, text="Avg. Track Duration:").grid(row=2, column=2, sticky=tk.W, padx=(20, 10), pady=5)
        self.avg_duration_label = ttk.Label(stats_grid, text="0:00")
        self.avg_duration_label.grid(row=2, column=3, sticky=tk.W, pady=5)
        
        # Most active day
        ttk.Label(stats_grid, text="Most Active Day:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.most_active_day_label = ttk.Label(stats_grid, text="N/A")
        self.most_active_day_label.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Last download
        ttk.Label(stats_grid, text="Last Download:").grid(row=3, column=2, sticky=tk.W, padx=(20, 10), pady=5)
        self.last_download_label = ttk.Label(stats_grid, text="Never")
        self.last_download_label.grid(row=3, column=3, sticky=tk.W, pady=5)
        
        # Chart tabs
        chart_notebook = ttk.Notebook(self.frame)
        chart_notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Downloads by day chart
        daily_chart_frame = ttk.Frame(chart_notebook)
        chart_notebook.add(daily_chart_frame, text="Daily Downloads")
        self._create_daily_chart(daily_chart_frame)
        
        # Artist distribution chart
        artist_chart_frame = ttk.Frame(chart_notebook)
        chart_notebook.add(artist_chart_frame, text="Artists")
        self._create_artist_chart(artist_chart_frame)
        
        # Controls
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        refresh_button = ttk.Button(
            controls_frame,
            text="Refresh Stats",
            command=self.refresh_stats
        )
        refresh_button.pack(side=tk.LEFT)
        
        export_button = ttk.Button(
            controls_frame,
            text="Export Stats",
            command=self.export_stats
        )
        export_button.pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_daily_chart(self, parent):
        """Create daily downloads chart"""
        # Create figure and axis
        self.daily_fig = Figure(figsize=(8, 4), dpi=100)
        self.daily_ax = self.daily_fig.add_subplot(111)
        
        # Configure initial appearance
        self.daily_ax.set_title("Downloads by Day")
        self.daily_ax.set_xlabel("Date")
        self.daily_ax.set_ylabel("Number of Downloads")
        self.daily_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Create canvas
        self.daily_canvas = FigureCanvasTkAgg(self.daily_fig, master=parent)
        self.daily_canvas.draw()
        self.daily_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.daily_canvas, toolbar_frame)
        toolbar.update()
    
    def _create_artist_chart(self, parent):
        """Create artist distribution chart"""
        # Create figure and axis
        self.artist_fig = Figure(figsize=(8, 4), dpi=100)
        self.artist_ax = self.artist_fig.add_subplot(111)
        
        # Configure initial appearance
        self.artist_ax.set_title("Top Artists")
        self.artist_ax.set_ylabel("Number of Tracks")
        self.artist_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Create canvas
        self.artist_canvas = FigureCanvasTkAgg(self.artist_fig, master=parent)
        self.artist_canvas.draw()
        self.artist_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.artist_canvas, toolbar_frame)
        toolbar.update()
    
    def refresh_stats(self):
        """Refresh all statistics"""
        self.status_callback("Calculating statistics...", 50)
        
        try:
            # Get download history
            history = self.download_manager.get_download_history()
            
            # Parse data
            download_data = self._parse_history_data(history)
            
            # Update summary stats
            self._update_summary_stats(download_data)
            
            # Update charts
            self._update_daily_chart(download_data)
            self._update_artist_chart(download_data)
            
            self.status_callback("Statistics updated", 100)
            
        except Exception as e:
            print(f"Error refreshing stats: {e}")
            self.status_callback("Error refreshing statistics", 0)
    
    def _parse_history_data(self, history):
        """Parse download history into usable data"""
        tracks = history.get('tracks', [])
        collections = history.get('collections', [])
        
        # Initialize data structure
        data = {
            'total_tracks': len(tracks),
            'tracks_by_date': {},
            'artists': {},
            'albums': set(),
            'playlists': set(),
            'total_size': 0,
            'durations': [],
            'last_download': None
        }
        
        # Count albums and playlists
        for collection in collections:
            collection_type = collection.get('type', '')
            collection_id = collection.get('id', '')
            
            if collection_type == 'album' and collection_id:
                data['albums'].add(collection_id)
            elif collection_type == 'playlist' and collection_id:
                data['playlists'].add(collection_id)
        
        # Process track data
        for track in tracks:
            # Get download date
            download_date_str = track.get('downloaded_at', '')
            if download_date_str:
                try:
                    download_date = datetime.fromisoformat(download_date_str)
                    date_key = download_date.strftime('%Y-%m-%d')
                    
                    # Count by date
                    if date_key in data['tracks_by_date']:
                        data['tracks_by_date'][date_key] += 1
                    else:
                        data['tracks_by_date'][date_key] = 1
                    
                    # Track last download
                    if data['last_download'] is None or download_date > data['last_download']:
                        data['last_download'] = download_date
                        
                except Exception as e:
                    print(f"Error parsing date: {e}")
            
            # Count by artist
            artist = track.get('artist', '')
            if artist:
                if artist in data['artists']:
                    data['artists'][artist] += 1
                else:
                    data['artists'][artist] = 1
            
            # Calculate file size if available
            file_path = track.get('file_path', '')
            if file_path and os.path.exists(file_path):
                data['total_size'] += os.path.getsize(file_path)
            
            # Track duration if available
            duration_ms = track.get('duration_ms', 0)
            if duration_ms:
                data['durations'].append(duration_ms)
        
        return data
    
    def _update_summary_stats(self, data):
        """Update summary statistics labels"""
        # Total downloads
        self.total_downloads_label.config(text=str(data['total_tracks']))
        
        # Last 7 days
        last_7_days = 0
        today = datetime.now().date()
        for date_str, count in data['tracks_by_date'].items():
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if (today - date).days <= 7:
                    last_7_days += count
            except Exception:
                pass
        self.last_7_days_label.config(text=str(last_7_days))
        
        # Albums and playlists
        self.albums_label.config(text=str(len(data['albums'])))
        self.playlists_label.config(text=str(len(data['playlists'])))
        
        # Storage used
        storage_mb = data['total_size'] / (1024 * 1024)
        if storage_mb > 1024:
            self.storage_label.config(text=f"{storage_mb / 1024:.2f} GB")
        else:
            self.storage_label.config(text=f"{storage_mb:.2f} MB")
        
        # Average duration
        if data['durations']:
            avg_duration_ms = sum(data['durations']) / len(data['durations'])
            avg_duration_s = avg_duration_ms / 1000
            minutes, seconds = divmod(int(avg_duration_s), 60)
            self.avg_duration_label.config(text=f"{minutes}:{seconds:02d}")
        else:
            self.avg_duration_label.config(text="0:00")
        
        # Most active day
        most_active_day = max(data['tracks_by_date'].items(), key=lambda x: x[1], default=(None, 0))
        if most_active_day[0]:
            try:
                date = datetime.strptime(most_active_day[0], '%Y-%m-%d')
                self.most_active_day_label.config(text=f"{date.strftime('%b %d, %Y')} ({most_active_day[1]})")
            except Exception:
                self.most_active_day_label.config(text="N/A")
        else:
            self.most_active_day_label.config(text="N/A")
        
        # Last download
        if data['last_download']:
            self.last_download_label.config(text=data['last_download'].strftime('%b %d, %Y %H:%M'))
        else:
            self.last_download_label.config(text="Never")
    
    def _update_daily_chart(self, data):
        """Update daily downloads chart"""
        # Clear previous data
        self.daily_ax.clear()
        
        # Get date range for last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Prepare data
        dates = []
        counts = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            count = data['tracks_by_date'].get(date_str, 0)
            
            dates.append(current_date)
            counts.append(count)
            
            current_date += timedelta(days=1)
        
        # Plot data
        self.daily_ax.bar(dates, counts, width=0.8, color='#3498db', alpha=0.7)
        
        # Configure appearance
        self.daily_ax.set_title("Downloads by Day (Last 30 Days)")
        self.daily_ax.set_xlabel("Date")
        self.daily_ax.set_ylabel("Number of Downloads")
        
        # Format x-axis dates
        self.daily_ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        self.daily_ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        
        # Rotate x-axis labels
        plt = self.daily_fig.canvas
        plt.draw()
        self.daily_ax.tick_params(axis='x', rotation=45)
        
        # Add grid
        self.daily_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Ensure tight layout
        self.daily_fig.tight_layout()
        
        # Redraw
        self.daily_canvas.draw()
    
    def _update_artist_chart(self, data):
        """Update artist distribution chart"""
        # Clear previous data
        self.artist_ax.clear()
        
        # Get top 10 artists by track count
        sorted_artists = sorted(data['artists'].items(), key=lambda x: x[1], reverse=True)
        top_artists = sorted_artists[:10]
        
        if not top_artists:
            # No data to show
            self.artist_ax.set_title("No Artist Data Available")
            self.artist_canvas.draw()
            return
        
        # Extract data
        artist_names = [artist[0][:20] + '...' if len(artist[0]) > 20 else artist[0] for artist in top_artists]
        track_counts = [artist[1] for artist in top_artists]
        
        # Reverse order for horizontal bar chart
        artist_names.reverse()
        track_counts.reverse()
        
        # Plot data
        bars = self.artist_ax.barh(artist_names, track_counts, color='#2ecc71', alpha=0.7)
        
        # Add count labels
        for bar in bars:
            width = bar.get_width()
            self.artist_ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, str(int(width)),
                              ha='left', va='center')
        
        # Configure appearance
        self.artist_ax.set_title("Top 10 Artists by Tracks")
        self.artist_ax.set_xlabel("Number of Tracks")
        
        # Add grid
        self.artist_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Ensure tight layout
        self.artist_fig.tight_layout()
        
        # Redraw
        self.artist_canvas.draw()
    
    def export_stats(self):
        """Export statistics to CSV format"""
        from tkinter import filedialog
        import csv
        from datetime import datetime
        
        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            title="Export Statistics",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            # Get download history
            history = self.download_manager.get_download_history()
            tracks = history.get('tracks', [])
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Track Name', 'Artist', 'Album', 'Downloaded Date', 
                    'Duration (ms)', 'Collection Type', 'Collection Name'
                ])
                
                # Write track data
                for track in tracks:
                    # Format data
                    track_name = track.get('name', '')
                    artist = track.get('artist', '')
                    album = track.get('album', '')
                    date = track.get('downloaded_at', '')
                    duration = track.get('duration_ms', '')
                    
                    # Get collection info if available
                    collection_type = ''
                    collection_name = ''
                    if 'collection' in track:
                        collection_type = track['collection'].get('type', '')
                        collection_name = track['collection'].get('name', '')
                    
                    # Write row
                    writer.writerow([
                        track_name, artist, album, date, 
                        duration, collection_type, collection_name
                    ])
            
            self.status_callback(f"Statistics exported to {filepath}", 100)
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Export Error", f"Error exporting statistics: {e}")
            self.status_callback("Error exporting statistics", 0) 