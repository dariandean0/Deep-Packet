#!/usr/bin/env python3
"""
Stage 2 Signal Intelligence
Serves signal.png on port 8002.

Only /signal.png is accessible; all other paths return 404.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

FILES_DIR = Path("/srv/stage2")
PORT = 8002

INDEX_HTML = """\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Signal Intelligence</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: monospace;
               max-width: 640px; margin: 80px auto; padding: 0 20px; }
        h1   { color: #3fb950; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        a    { color: #79c0ff; }
        .box { background: #161b22; border: 1px solid #30363d; padding: 16px;
               border-radius: 6px; margin-top: 20px; }
        img  { max-width: 100%; border: 1px solid #30363d; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Signal Intelligence</h1>
    <div class="box">
        <p>Anomalous signal intercepted at 03:47 UTC. Image attached.</p>
        <p>Download: <a href="/signal.png">signal.png</a></p>
        <p><small>Hint: not everything is visible to the naked eye.</small></p>
        <img src="/signal.png" alt="intercepted signal">
    </div>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    server_version = "nginx/1.22.1"
    sys_version = ""

    def log_message(self, fmt, *args):
        print(f"[stage2] {self.address_string()} - {fmt % args}")

    def do_GET(self):
        if self.path == "/":
            self._send(200, "text/html; charset=utf-8", INDEX_HTML.encode())
        elif self.path == "/signal.png":
            img_file = FILES_DIR / "signal.png"
            data = img_file.read_bytes()
            self._send(200, "image/png", data,
                       extra_headers = {"Content-Disposition": 'attachment; filename="signal.png"'})
        else:
            self._send(404, "text/plain", b"Not Found")

    def _send(self, code, ctype, body, extra_headers = None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    print(f"[stage2] Listening on 0.0.0.0:{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()