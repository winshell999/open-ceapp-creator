"""One source runs as a normal website or as a hosted CEAPP.

python3 server.py
The Host's optional http-server adapter replaces only the listening port.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote
import hashlib
import json
import mimetypes
import os
import sqlite3
import threading
import time

ROOT = Path(os.environ.get("CANENGINE_APP_DIR") or Path(__file__).resolve().parent).resolve()
# The only storage adaptation a typical local website needs.
DATA = Path(os.environ.get("CANENGINE_APP_DATA_DIR", str(ROOT / ".local-data")))
DATA.mkdir(parents=True, exist_ok=True)
DB = sqlite3.connect(DATA / "notes.sqlite", check_same_thread=False)
DB.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT)")
DB.commit()
LOCK = threading.Lock()
REQUESTS = 0
MEDIA = DATA / "sample.bin"
if not MEDIA.exists():
    MEDIA.write_bytes(bytes(range(256)) * 4096)


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, code=200):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        global REQUESTS
        path = unquote(urlparse(self.path).path)
        if path == "/health":
            return self.send_json({"ok": True})
        if path == "/api/status":
            with LOCK:
                REQUESTS += 1
                notes = [{"id": row[0], "text": row[1]} for row in DB.execute("SELECT id, text FROM notes ORDER BY id DESC LIMIT 20")]
                return self.send_json({"pid": os.getpid(), "connectionId": str(id(DB)), "requests": REQUESTS, "notes": notes})
        if path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(b"data: ready\n\n")
            self.wfile.flush()
            time.sleep(2)
            self.wfile.write(b"data: done\n\n")
            return
        if path == "/media/sample.bin":
            return self.send_file(MEDIA)
        if path == "/download":
            return self.send_file(MEDIA, attachment=True)
        if path == "/":
            return self.send_file(ROOT / "index.html")
        if path.startswith("/assets/"):
            asset = (ROOT / path.lstrip("/")).resolve()
            if asset.is_relative_to(ROOT / "assets") and asset.is_file():
                return self.send_file(asset)
        self.send_error(404)

    def do_HEAD(self):
        if urlparse(self.path).path == "/media/sample.bin":
            return self.send_file(MEDIA, head=True)
        self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > 10 * 1024 * 1024:
            return self.send_json({"error": "Request too large"}, 413)
        data = self.rfile.read(length)
        if self.path == "/api/upload":
            return self.send_json({"size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        if self.path == "/api/notes":
            try:
                text = str(json.loads(data).get("text", ""))[:1000].strip()
            except (ValueError, AttributeError):
                return self.send_json({"error": "Invalid JSON"}, 400)
            if not text:
                return self.send_json({"error": "Empty note"}, 400)
            with LOCK:
                DB.execute("INSERT INTO notes(text) VALUES (?)", (text,))
                DB.commit()
            return self.send_json({"ok": True})
        self.send_error(404)

    def send_file(self, path, head=False, attachment=False):
        size = path.stat().st_size
        start, end, code = 0, size - 1, 200
        requested = self.headers.get("Range", "")
        if requested.startswith("bytes="):
            try:
                left, right = requested[6:].split("-", 1)
                start = int(left) if left else max(0, size - int(right))
                end = min(size - 1, int(right)) if right and left else size - 1
                if not 0 <= start <= end < size:
                    raise ValueError()
                code = 206
            except ValueError:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
        self.send_response(code)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("ETag", f'"{size}-{path.stat().st_mtime_ns}"')
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        if attachment:
            self.send_header("Content-Disposition", 'attachment; filename="sample.bin"')
        self.end_headers()
        if head:
            return
        with path.open("rb") as source:
            source.seek(start)
            remaining = end - start + 1
            while remaining:
                chunk = source.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)


if __name__ == "__main__":
    # The same entry works in source, compiled and standalone development modes.
    host = os.environ.get("CANENGINE_HOST", "127.0.0.1")
    port = int(os.environ.get("CANENGINE_PORT", "8080"))
    ThreadingHTTPServer((host, port), Handler).serve_forever()
