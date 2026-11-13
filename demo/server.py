"""Lightweight local demo server for Data Ingestion project."""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).resolve().parent


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # Enable CORS and disable aggressive caching for local demo
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()


def run_server(port=PORT):
    for p in [port, 8080, 8888, 5000]:
        try:
            with socketserver.TCPServer(("", p), CustomHandler) as httpd:
                url = f"http://localhost:{p}"
                print("\n" + "=" * 60)
                print(f"🚀 DEMO SERVER ĐANG CHẠY TẠI: {url}")
                print(f"📁 Thư mục phục vụ: {DIRECTORY}")
                print("👉 Nhấn Ctrl+C để dừng server.")
                print("=" * 60 + "\n")
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
                httpd.serve_forever()
        except OSError:
            continue


if __name__ == "__main__":
    run_server()
