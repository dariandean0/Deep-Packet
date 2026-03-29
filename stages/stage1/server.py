"""
Stage 1 Network Analysis Portal
Serves capture.pcap on port 8001.

Only /capture.pcap is accessible; all other paths return 404.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

FILES_DIR = Path("/srv/stage1")
PORT = 8001

INDEX_HTML = """\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Network Analysis Portal</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: monospace;
               max-width: 640px; margin: 80px auto; padding: 0 20px; }
        h1   { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        a    { color: #79c0ff; }
        .box { background: #161b22; border: 1px solid #30363d; padding: 16px;
               border-radius: 6px; margin-top: 20px; }
        code { color: #f0883e; }
    </style>
</head>
<body>
    <h1>Network Analysis Portal</h1>
    <div class="box">
        <p>Anomalous traffic was captured during the breach window.</p>
        <p>Download and analyze: <a href="/capture.pcap">capture.pcap</a></p>
        <p><small>Hint: look for unusual POST requests and their payloads.</small></p>
    </div>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "Apache/2.4.51"
    sys_version = ""

    def log_message(self, fmt, *args):
        print(f"[stage1] {self.address_string()} - {fmt % args}")

    def do_GET(self):
        if self.path == "/":
            self._send(200, "text/html; charset = utf-8", INDEX_HTML.encode())
        elif self.path == "/capture.pcap":
            pcap_file = FILES_DIR / "capture.pcap"
            if not pcap_file.exists():
                self._send(503, "text/plain", b"Challenge artifact not yet generated.")
                return
            data = pcap_file.read_bytes()
            self._send(200, "application/vnd.tcpdump.pcap", data,
                       extra_headers={"Content-Disposition": 'attachment; filename = "capture.pcap"'})
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
    print(f"[stage1] Listening on 0.0.0.0:{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()