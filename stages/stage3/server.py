#!/usr/bin/env python3
"""
Stage 3 - Internal Diagnostic Console
Serves a SQLi-vulnerable login portal on port 8003.

Intended solve: bypass login with SQL injection (e.g. username: admin'--)
On success: dashboard reveals Stage 4 binary service
and provides /download/vuln to pull the binary for local analysis.
"""

import sqlite3
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

DB_PATH = "/tmp/stage3.db"
PORT = 8003
VULN_BIN = Path("/opt/ctf/stages/stage4/vuln")

# Database 
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("DELETE FROM users")
    # Strong password - normal login is intentionally unguessable
    conn.execute(
        "INSERT INTO users (username, password) VALUES ('admin', 'Xk9#mQ2@vL7!nR4$')"
    )
    conn.commit()
    conn.close()

def check_login(username: str, password: str) -> bool:
    """Intentionally vulnerable to SQL injection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # VULNERABLE: user input concatenated directly into query
        query = (
            f"SELECT * FROM users "
            f"WHERE username='{username}' AND password='{password}'"
        )
        cur = conn.execute(query)
        row = cur.fetchone()
        conn.close()
        return row is not None
    except sqlite3.OperationalError:
        # Malformed SQL (bad injection attempt) - treat as failed login
        return False

# HTML pages
LOGIN_HTML = """\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Internal Diagnostic Console</title>
    <style>
        * { box-sizing: border-box; }
        body {
            background: #0d1117; color: #c9d1d9; font-family: monospace;
            max-width: 480px; margin: 100px auto; padding: 0 20px;
        }
        h1   { color: #f0883e; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .box {
            background: #161b22; border: 1px solid #30363d;
            padding: 24px; border-radius: 6px; margin-top: 24px;
        }
        label { display: block; margin-bottom: 4px; color: #8b949e; font-size: 0.85em; }
        input[type=text], input[type=password] {
            width: 100%; padding: 8px 10px; margin-bottom: 16px;
            background: #0d1117; border: 1px solid #30363d; color: #c9d1d9;
            border-radius: 4px; font-family: monospace; font-size: 0.95em;
        }
        input[type=text]:focus, input[type=password]:focus {
            outline: none; border-color: #f0883e;
        }
        button {
            width: 100%; padding: 9px; background: #f0883e; color: #0d1117;
            border: none; border-radius: 4px; font-family: monospace;
            font-size: 0.95em; font-weight: bold; cursor: pointer;
        }
        button:hover { background: #d6762c; }
        .err {
            background: #3d1f1f; border: 1px solid #6e2f2f; color: #f85149;
            padding: 10px 14px; border-radius: 4px; margin-bottom: 16px;
            font-size: 0.9em;
        }
        .warn {
            color: #8b949e; font-size: 0.78em; margin-top: 18px;
            border-top: 1px solid #21262d; padding-top: 12px;
        }
    </style>
</head>
<body>
    <h1>&#x26A0; Internal Diagnostic Console</h1>
    <div class="box">
        <p style="color:#8b949e; font-size:0.85em; margin-top:0;">
            RESTRICTED ACCESS — authorised personnel only
        </p>
        {error_block}
        <form method="POST" action="/login">
            <label for="u">Username</label>
            <input id="u" type="text" name="username" autocomplete="off" autofocus>
            <label for="p">Password</label>
            <input id="p" type="password" name="password">
            <button type="submit">Authenticate</button>
        </form>
        <p class="warn">
            Unauthorised access attempts are logged and prosecuted.<br>
            Contact sysadmin if you have lost your credentials.
        </p>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Diagnostic Console — Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        body {
            background: #0d1117; color: #c9d1d9; font-family: monospace;
            max-width: 680px; margin: 60px auto; padding: 0 20px;
        }
        h1   { color: #f0883e; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        h2   { color: #c9d1d9; font-size: 1em; margin: 24px 0 8px; }
        .box {
            background: #161b22; border: 1px solid #30363d;
            padding: 20px 24px; border-radius: 6px; margin-bottom: 16px;
        }
        .ok  { color: #3fb950; }
        .warn { color: #f0883e; }
        table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
        td   { padding: 6px 10px; border-bottom: 1px solid #21262d; }
        td:first-child { color: #8b949e; width: 40%; }
        a    { color: #79c0ff; }
        code { color: #f0883e; background: #0d1117; padding: 2px 6px; border-radius: 3px; }
        .badge {
            display: inline-block; padding: 2px 8px; border-radius: 10px;
            font-size: 0.75em; font-weight: bold;
        }
        .badge-ok   { background: #1a3d2b; color: #3fb950; border: 1px solid #2ea043; }
        .badge-warn { background: #3d2a1a; color: #f0883e; border: 1px solid #d0631a; }
    </style>
</head>
<body>
    <h1>&#x26A0; Internal Diagnostic Console</h1>
    <p class="ok">&#x2713; Authentication successful — session active</p>

    <h2>System Services</h2>
    <div class="box">
        <table>
            <tr>
                <td>Web portal (stage1)</td>
                <td><span class="badge badge-ok">RUNNING</span> &nbsp; port 8001</td>
            </tr>
            <tr>
                <td>SIGINT relay (stage2)</td>
                <td><span class="badge badge-ok">RUNNING</span> &nbsp; port 8002</td>
            </tr>
            <tr>
                <td>Diagnostic console (stage3)</td>
                <td><span class="badge badge-ok">RUNNING</span> &nbsp; port 8003</td>
            </tr>
            <tr>
                <td>Binary analysis service</td>
                <td>
                    <span class="badge badge-warn">EXPOSED</span>
                    &nbsp; port <code>9004</code>
                </td>
            </tr>
        </table>
    </div>

    <h2>Binary Analysis Service</h2>
    <div class="box">
        <p style="margin-top:0;">
            An internal diagnostic binary is exposed on
            <code>localhost:9004</code> via <code>socat</code>.
            This service was flagged during the last audit as
            <span class="warn">unpatched</span>.
        </p>
        <p>Download the binary for local analysis before connecting:</p>
        <p>
            <a href="/download/vuln">&#x2B07; Download vuln (ELF 32-bit)</a>
        </p>
        <p style="color:#8b949e; font-size:0.82em; margin-bottom:0;">
            Hint: check for memory-corruption vulnerabilities.
        </p>
    </div>
</body>
</html>
"""

LOGIN_HTML_ERR = LOGIN_HTML.replace(
    "{error_block}",
    '<div class="err">&#x2717; Invalid credentials.</div>',
)
LOGIN_HTML_OK = LOGIN_HTML.replace("{error_block}", "")

# Request handler
class Handler(BaseHTTPRequestHandler):
    server_version = "Apache/2.4.51"
    sys_version = ""

    def log_message(self, fmt, *args):
        print(f"[stage3] {self.address_string()} - {fmt % args}")

    # GET 
    def do_GET(self):
        if self.path == "/":
            self._send(200, "text/html; charset=utf-8", LOGIN_HTML_OK.encode())
        elif self.path == "/download/vuln":
            if not VULN_BIN.exists():
                self._send(503, "text/plain", b"Binary not yet available.")
                return
            data = VULN_BIN.read_bytes()
            self._send(
                200, "application/octet-stream", data,
                extra_headers = {
                    "Content-Disposition": 'attachment; filename="vuln"',
                },
            )
        else:
            self._send(404, "text/plain", b"Not Found")

    # POST 
    def do_POST(self):
        if self.path != "/login":
            self._send(404, "text/plain", b"Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode(errors = "replace")
        params = parse_qs(body)

        username = params.get("username", [""])[0]
        password = params.get("password", [""])[0]

        print(f"[stage3] login attempt - username={username!r}")

        if check_login(username, password):
            print(f"[stage3] login SUCCESS for username={username!r}")
            self._send(200, "text/html; charset=utf-8", DASHBOARD_HTML.encode())
        else:
            print(f"[stage3] login FAILED for username={username!r}")
            self._send(401, "text/html; charset=utf-8", LOGIN_HTML_ERR.encode())

    # helpers 
    def _send(self, code, ctype, body, extra_headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

# Entry point 
if __name__ == "__main__":
    init_db()
    print(f"[stage3] DB initialised at {DB_PATH}")
    print(f"[stage3] Listening on 0.0.0.0:{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
