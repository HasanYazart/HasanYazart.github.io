"""Offline structural/security regression checks. Run: python scripts/check_site.py."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.refs, self.aria = path, set(), [], []
        self.stack = []
        self.h1 = self.titles = 0
        self.csp = None
        self.feed(path.read_text(encoding='utf-8'))
        assert not self.stack, f'{path.name}: unclosed tags {self.stack}'

    def handle_starttag(self, tag, attrs):
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append(tag)
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'{self.path.name}: duplicate ID'
            self.ids.add(attrs['id'])
        self.h1 += tag == 'h1'
        self.titles += tag == 'title'
        assert not any(key.startswith('on') for key in attrs), f'{self.path.name}: inline handler'
        assert 'style' not in attrs, f'{self.path.name}: inline style conflicts with CSP'
        if tag == 'script':
            assert attrs.get('src') in ('site.js', '../site.js', '/site.js'), f'{self.path.name}: unexpected script'
            assert 'defer' in attrs
        if tag == 'img':
            assert attrs.get('alt'), f'{self.path.name}: missing alt'
            assert 'width' in attrs and 'height' in attrs
        if attrs.get('target') == '_blank':
            assert {'noopener', 'noreferrer'} <= set(attrs.get('rel', '').split())
        for key in ('href', 'src'):
            if attrs.get(key): self.refs.append(attrs[key])
        for key in ('aria-controls', 'aria-labelledby', 'aria-describedby'):
            self.aria.extend(attrs.get(key, '').split())
        if attrs.get('http-equiv', '').lower() == 'content-security-policy':
            self.csp = attrs['content']

    def handle_endtag(self, tag):
        assert self.stack and self.stack[-1] == tag, f'{self.path.name}: misplaced closing {tag} after {self.stack}'
        self.stack.pop()

pages = {p.relative_to(ROOT).as_posix(): Page(p) for p in [*ROOT.glob('*.html'), *(ROOT / 'en').glob('*.html')]}
for name, page in pages.items():
    assert page.h1 == page.titles == 1, f'{name}: title/H1 count'
    assert page.csp and "script-src 'self'" in page.csp and "object-src 'none'" in page.csp
    assert 'unsafe-inline' not in page.csp and 'unsafe-eval' not in page.csp
    assert set(page.aria) <= page.ids, f'{name}: broken ARIA reference'
    for ref in page.refs:
        parts = urlsplit(ref)
        assert parts.scheme in ('', 'https', 'mailto', 'data'), f'{name}: unsafe URL'
        if parts.scheme: continue
        target = ((ROOT if parts.path.startswith('/') else page.path.parent) / unquote(parts.path).lstrip('/')).resolve() if parts.path else page.path
        assert target.is_relative_to(ROOT) and target.is_file(), f'{name}: broken link {ref}'
        key = target.relative_to(ROOT).as_posix()
        if parts.fragment and key in pages:
            assert unquote(parts.fragment) in pages[key].ids, f'{name}: broken fragment {ref}'
for path in (ROOT / 'assets').rglob('*.svg'):
    svg = ET.parse(path)
    for element in svg.iter():
        assert element.tag.split('}')[-1] not in ('script', 'foreignObject')
        assert not any(key.startswith('on') for key in element.attrib)
js = (ROOT / 'site.js').read_text(encoding='utf-8')
for pattern in (r'\b(?:eval|Function)\s*\(', r'\.innerHTML\s*=', r'document\.write\s*\(', r'\.outerHTML\s*='):
    assert not re.search(pattern, js), f'Unsafe DOM sink: {pattern}'
print(f'PASS: {len(pages)} pages; local links/fragments, IDs, ARIA, image text, CSP, script policy, SVG and DOM-sink checks.')

home = (ROOT / 'index.html').read_text(encoding='utf-8')
about = (ROOT / 'about.html').read_text(encoding='utf-8')
assert '2209' not in home + about and 'TÜBİTAK' not in home + about
assert '2209-A' in (ROOT / 'projects.html').read_text(encoding='utf-8')
assert all('brand-mark' not in page.path.read_text(encoding='utf-8') for page in pages.values())
assert all(label not in home for label in ('FIG. 01', 'SYSTEM ARCHITECTURE', '3D SİSTEM GÖRÜNÜMÜ', 'hero-facts'))
contact = pages['contact.html']
assert 'eposta' in contact.ids
assert any(url.startswith('https://mail.google.com/mail/') and 'to=tt41468%40gmail.com' in url for url in contact.refs)
assert any(url.startswith('https://outlook.live.com/mail/') and 'to=tt41468%40gmail.com' in url for url in contact.refs)
for name, page in pages.items():
    if name not in ('contact.html', 'en/contact.html'):
        assert not any(url.startswith('mailto:') for url in page.refs), f'{name}: email bypasses visible alternatives'
print('PASS: HTML nesting, requested content removals, project retention and visible email alternatives.')
for name in pages:
    if '/' in name or name == '404.html': continue
    english = (ROOT / 'en' / name).read_text(encoding='utf-8')
    turkish = (ROOT / name).read_text(encoding='utf-8')
    assert '<html lang="en">' in english
    assert f'href="../{name}" lang="tr"' in english, f'{name}: English return link'
    assert f'href="en/{name}" lang="en"' in turkish, f'{name}: Turkish language link'
    assert 'hreflang="en"' in turkish and 'hreflang="tr"' in english
assert (ROOT / 'assets/social-card.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
print('PASS: paired language routes, language metadata and PNG social card.')
