import tkinter as tk
import ttkbootstrap as ttk
import os
import json

from src.ui.main_window import MainWindow
from src.utils.config import DEFAULT_THEME, CONFIG_FILE, get_app_config
from src.utils.ui_styles import UIStyles

def main():
    """Main application entry point"""
    # Load configuration and get theme
    config = get_app_config()
    theme = config.get("theme", DEFAULT_THEME)
    
    # Create root window with bootstrap theme
    root = ttk.Window(themename=theme)
    
    # Apply UI styles
    style = ttk.Style()
    ui_styles = UIStyles(style, theme)
    ui_styles.apply_to_window(root)
    
    # Create main application window
    app = MainWindow(root, ui_styles)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main() 