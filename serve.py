import http.server
import socketserver
import os
import json
import time
import threading
import webbrowser
from urllib.parse import urlparse, parse_qs

PORT = 8000
DIRECTORY = "site"
LIVERELOAD_PORT = 35729

class LiveReloadHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        self.last_modified = time.time()

    def do_GET(self):
        if self.path.startswith('/livereload'):
            self.handle_livereload()
        else:
            super().do_GET()

    def handle_livereload(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'command': 'reload',
            'path': '/',
            'liveCSS': True
        }
        self.wfile.write(json.dumps(response).encode())

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

def inject_livereload_script(html_content):
    script = f"""
    <script>
        (function() {{
            var script = document.createElement('script');
            script.src = 'http://localhost:{LIVERELOAD_PORT}/livereload.js';
            document.head.appendChild(script);
        }})();
    </script>
    """
    return html_content.replace(b'</head>', script.encode() + b'</head>')

class LiveReloadServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_livereload_server():
    with LiveReloadServer(("", LIVERELOAD_PORT), LiveReloadHandler) as httpd:
        print(f"LiveReload server running at http://localhost:{LIVERELOAD_PORT}")
        httpd.serve_forever()

def main():
    # Start LiveReload server in a separate thread
    livereload_thread = threading.Thread(target=start_livereload_server, daemon=True)
    livereload_thread.start()

    # Start main server
    with socketserver.TCPServer(("", PORT), LiveReloadHandler) as httpd:
        print(f"Serving documentation at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        
        # Open browser automatically
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    main() 