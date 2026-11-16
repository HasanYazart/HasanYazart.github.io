"""Local HTTP probes only; never scans external hosts."""
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from preview import PreviewHandler
from pathlib import Path
from public_files import public_files

class QuietHandler(PreviewHandler):
    def log_message(self, *_): pass

server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f'http://127.0.0.1:{server.server_port}'
try:
    root = Path(__file__).resolve().parents[1]
    routes = ['/', '/en/', '/en'] + ['/' + path.relative_to(root).as_posix() for path in public_files()]
    for route in routes:
        with urlopen(base + route, timeout=5) as response:
            assert response.status == 200
            assert response.headers['X-Content-Type-Options'] == 'nosniff'
            assert response.headers['X-Frame-Options'] == 'DENY'
            assert "frame-ancestors 'none'" in response.headers['Content-Security-Policy']
    for filename in ('Hasan_Yazar_CV.pdf', 'Hasan_Yazar_CV_EN.pdf'):
        with urlopen(base + '/assets/cv/' + filename, timeout=5) as response:
            assert response.status == 200
            assert response.headers.get_content_type() == 'application/pdf'
            assert response.read() == (root / 'assets' / 'cv' / filename).read_bytes()
    blocked = ('/.git/config', '/.env', '/scripts/preview.py', '/assets/', '/../site.js', '/%2e%2e/site.js', '/assets/../../site.js', '/%2e%2e%5csite.js', '/missing.html', '/%00.html', '/REVIEW.md', '/_headers', '/assets/projects/SOURCES.md', '/en/missing/page')
    for route in blocked:
        try:
            urlopen(base + route, timeout=5)
            raise AssertionError(f'Unexpected public route: {route}')
        except HTTPError as error:
            assert error.code == 404
            assert error.headers['X-Content-Type-Options'] == 'nosniff'
            assert b'<!doctype html>' in error.read().lower()
    with urlopen(base + '/?q=%3Cscript%3Ealert(12345)%3C/script%3E', timeout=5) as response:
        assert b'alert(12345)' not in response.read()
    with urlopen(Request(base + '/index.html', method='HEAD'), timeout=5) as response:
        assert response.status == 200 and response.read() == b''
    try:
        urlopen(Request(base + '/', data=b'test', method='POST'), timeout=5)
        raise AssertionError('Unexpected POST support')
    except HTTPError as error:
        assert error.code == 501
    print(f'PASS: {len(routes)} public routes, 2 exact PDF downloads, full security headers, {len(blocked)} private/invalid routes, custom 404, query reflection, HEAD and POST behavior.')
finally:
    server.shutdown()
    server.server_close()
    thread.join()
