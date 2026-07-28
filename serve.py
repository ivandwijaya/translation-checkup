#!/usr/bin/env python3
"""Local viewer server for poe.csv.

Serves the repo folder (like `python -m http.server`) AND accepts saves:
  POST /save   body = full CSV text  ->  writes poe.csv (atomically)

Local use only. The save endpoint exists solely on your machine; GitHub Pages
serves the same index.html as static files with no way to write back.
"""
import http.server, socketserver, os, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8766))
TARGET = os.path.join(ROOT, "poe.csv")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_GET(self):
        # friendly route: /proposal -> proposal.html
        if self.path.rstrip("/") == "/proposal":
            self.path = "/proposal.html"
        return super().do_GET()

    def do_POST(self):
        if self.path != "/save":
            self.send_error(404); return
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(n).decode("utf-8")
            if not data.strip():
                self.send_error(400, "empty body"); return
            # atomic write: temp file in same dir, then replace
            fd, tmp = tempfile.mkstemp(dir=ROOT, suffix=".csv.tmp")
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                f.write(data)
            os.replace(tmp, TARGET)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"saved")
        except Exception as e:
            self.send_error(500, str(e))

    def end_headers(self):
        # never cache during local editing so a refresh shows latest saves
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        if self.command == "POST":
            sys.stderr.write("saved poe.csv\n")

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"POE viewer (editable) -> http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
