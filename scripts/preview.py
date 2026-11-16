"""Loopback-only preview. Serves public assets, never repository or audit files."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote
from public_files import CSP, is_public

ROOT = Path(__file__).resolve().parents[1]

class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_head(self):
        route = unquote(urlsplit(self.path).path)
        if '\x00' in route or '\\' in route or '..' in route.split('/'):
            self.send_error(404)
            return None
        if route in ('/', '/en', '/en/'):
            route = '/en/index.html' if route.startswith('/en') else '/index.html'
        try:
            target = (ROOT / route.lstrip('/')).resolve()
        except (OSError, ValueError):
            self.send_error(404)
            return None
        if not is_public(target):
            self.send_error(404)
            return None
        try:
            stream = target.open('rb')
        except OSError:
            self.send_error(404)
            return None
        self.send_response(200)
        self.send_header('Content-Type', self.guess_type(str(target)))
        self.send_header('Content-Length', str(target.stat().st_size))
        self.end_headers()
        return stream

    def send_error(self, code, message=None, explain=None):
        if code != 404: return super().send_error(code, message, explain)
        page = ROOT / ('en/404.html' if self.path.startswith('/en/') else '404.html')
        if not page.is_file(): return super().send_error(code, message, explain)
        body = page.read_bytes()
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command != 'HEAD': self.wfile.write(body)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Security-Policy', CSP)
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8766)
    port = parser.parse_args().port
    print(f'Local preview: http://127.0.0.1:{port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', port), PreviewHandler).serve_forever()
