"""Local offline shell. User field values are never sent to this server."""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = {
    '/': ('index.html', 'text/html; charset=utf-8'),
    '/assets/app.js': ('assets/app.js', 'application/javascript; charset=utf-8'),
    '/assets/ceapp-i18n.js': ('assets/ceapp-i18n.js', 'application/javascript; charset=utf-8'),
    '/assets/styles.css': ('assets/styles.css', 'text/css; charset=utf-8'),
    '/assets/form-config.json': ('assets/form-config.json', 'application/json; charset=utf-8'),
    '/assets/icon.svg': ('assets/icon.svg', 'image/svg+xml'),
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, code, body, mime='text/plain; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'private, no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            self.respond(200, b'{"ok":true}', 'application/json')
        elif self.path in FILES:
            filename, mime = FILES[self.path]
            self.respond(200, (ROOT / filename).read_bytes(), mime)
        else:
            self.respond(404, b'Not found')

    def do_POST(self):
        self.respond(405, b'Method not allowed')


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', int(os.environ['CANENGINE_PORT'])), Handler).serve_forever()
