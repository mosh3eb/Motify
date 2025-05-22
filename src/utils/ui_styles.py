import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import os

class UIStyles:
    """Class to manage and apply custom UI styles throughout the application"""
    
    def __init__(self, style, theme="darkly"):
        self.style = style
        self.theme = theme
        self.configure_styles()
        
    def configure_styles(self):
        """Configure custom styles for the application"""
        # Define colors based on current theme
        is_dark = self.theme in ["darkly", "solar", "superhero", "cyborg", "vapor"]
        
        # Common padding and margins
        self.padding = {"padx": 10, "pady": 10}
        self.small_padding = {"padx": 5, "pady": 5}
        
        # Button styles
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('primary.TButton', font=('Helvetica', 10, 'bold'))
        self.style.configure('success.TButton', font=('Helvetica', 10, 'bold'))
        self.style.configure('danger.TButton', font=('Helvetica', 10, 'bold'))
        
        # Entry styles with rounded borders and padding
        self.style.configure('TEntry', padding=5)
        
        # Label styles
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Info.TLabel', font=('Helvetica', 9), foreground='gray')
        
        # Frame styles
        self.style.configure('Card.TFrame', relief='raised', borderwidth=1)
        
        # LabelFrame styles
        self.style.configure('TLabelframe', font=('Helvetica', 11, 'bold'))
        self.style.configure('TLabelframe.Label', font=('Helvetica', 11, 'bold'))
        
        # Notebook styles
        self.style.configure('TNotebook', padding=2)
        self.style.configure('TNotebook.Tab', font=('Helvetica', 10, 'bold'), padding=[10, 5])
        
        # Progressbar styles
        self.style.configure('TProgressbar', thickness=6)
        
        # Avoid configuring separator styles - causes duplication errors
        # self.style.configure('TSeparator', background='gray')
    
    def apply_to_window(self, window):
        """Apply additional window-specific styles"""
        window.title("Motify Music Downloader")
        
        # Set window icon if available
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "resources", "motify_icon.png")
        if os.path.exists(icon_path):
            icon = ImageTk.PhotoImage(Image.open(icon_path))
            window.iconphoto(True, icon)
        
        # Center window on screen
        window_width = 900
        window_height = 650
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        window.minsize(width=800, height=600)
    
    def create_rounded_button(self, parent, text, command, style=None, **kwargs):
        """Create a rounded button with optional icon"""
        if style:
            button = ttk.Button(parent, text=text, command=command, style=style, **kwargs)
        else:
            button = ttk.Button(parent, text=text, command=command, **kwargs)
        return button
    
    def create_search_entry(self, parent, callback=None, placeholder="Search...", **kwargs):
        """Create a stylized search entry with placeholder text"""
        frame = ttk.Frame(parent)
        
        # Create the entry with placeholder
        var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=var, **kwargs)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        var.set(placeholder)
        entry.bind("<FocusIn>", lambda e: var.set("") if var.get() == placeholder else None)
        entry.bind("<FocusOut>", lambda e: var.set(placeholder) if var.get() == "" else None)
        
        if callback:
            entry.bind("<Return>", lambda e: callback())
        
        # Create a search button
        search_button = ttk.Button(frame, text="🔍", width=3)
        if callback:
            search_button.config(command=callback)
        search_button.pack(side=tk.RIGHT)
        
        return frame, entry, search_button

    def create_help_button(self, parent, help_text):
        """Create a small help button with a tooltip"""
        button = ttk.Button(parent, text="?", width=2)
        
        # Create tooltip functionality
        tooltip = tk.Toplevel(parent)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.attributes("-topmost", True)
        
        tooltip_label = ttk.Label(tooltip, text=help_text, wraplength=250, 
                                 justify=tk.LEFT, padding=5)
        tooltip_label.pack()
        
        def show_tooltip(event):
            x, y = event.widget.winfo_rootx(), event.widget.winfo_rooty() + event.widget.winfo_height()
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
            
        def hide_tooltip(event):
            tooltip.withdraw()
            
        button.bind("<Enter>", show_tooltip)
        button.bind("<Leave>", hide_tooltip)
        
        return button
        
    def create_status_bar(self, parent, **kwargs):
        """Create a styled status bar with progress indicator"""
        frame = ttk.Frame(parent, **kwargs)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            frame, 
            variable=self.progress_var,
            mode="determinate",
            length=150
        )
        progress_bar.pack(side=tk.RIGHT, padx=5)
        
        def update_status(text, progress=None):
            self.status_var.set(text)
            if progress is not None:
                self.progress_var.set(progress)
                
        return frame, update_status 