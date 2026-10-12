import http.server
import socketserver
import os
import sys

# Force UTF-8 on Windows stdout/stderr
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def guess_type(self, path):
        if path.endswith('.glb'):
            return 'model/gltf-binary'
        if path.endswith('.gltf'):
            return 'model/gltf+json'
        if path.endswith('.wasm'):
            return 'application/wasm'
        return super().guess_type(path)

class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    server_address = ('127.0.0.1', PORT)
    with ThreadingServer(server_address, CORSHTTPRequestHandler) as httpd:
        print("==========================================================")
        print("  TORRE GARTEN - 3D DASINMAZ EMLAK SISTEMI")
        print(f"  Unvan: http://127.0.0.1:{PORT}/")
        print("  Multi-threaded Python server aktivdir.")
        print("==========================================================")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer dayandirildi.")
