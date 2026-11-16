"""Build static English pages and shared SEO metadata; no runtime translation service."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://hasanyazart.github.io'
TRANSLATIONS = dict(line.split('|', 1) for line in (ROOT / 'scripts/en-translations.txt').read_text(encoding='utf-8').splitlines() if '|' in line)
missing = set()

def translate(text):
    key = text.strip()
    if key in TRANSLATIONS:
        return text.replace(key, TRANSLATIONS[key], 1)
    if ' — ' in key:
        return ' — '.join(translate(piece) for piece in key.split(' — '))
    if any(char in key for char in 'çğıöşüÇĞİÖŞÜ') and key not in ('TÜBİTAK 2209-A', 'Hasan Yazar') and not key.startswith(('telnet ', 'SET ', 'GET ')):
        missing.add(key)
    return text

class EnglishPage(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []

    def handle_decl(self, decl): self.output.append('<!' + decl + '>')
    def handle_comment(self, text): self.output.append('<!--' + text + '-->')
    def handle_data(self, text): self.output.append(escape(translate(text)))
    def handle_endtag(self, tag): self.output.append('</' + tag + '>')
    def handle_startendtag(self, tag, attrs): self.handle_starttag(tag, attrs)
    def handle_starttag(self, tag, attrs):
        info = dict(attrs)
        updated = []
        for key, value in attrs:
            if value is None:
                updated.append(key)
                continue
            if tag == 'html' and key == 'lang': value = 'en'
            elif key in ('alt', 'title', 'aria-label', 'placeholder'):
                value = translate(value)
            elif tag == 'meta' and key == 'content':
                if info.get('property') == 'og:locale': value = 'en_US'
                elif info.get('property') == 'og:url': value = value.replace(BASE + '/', BASE + '/en/', 1)
                elif info.get('name') in ('description', 'twitter:title', 'twitter:description') or info.get('property') in ('og:title', 'og:description'):
                    value = translate(value)
            elif key in ('href', 'src'):
                if info.get('rel') == 'canonical': value = value.replace(BASE + '/', BASE + '/en/', 1)
                elif not urlsplit(value).scheme and not value.startswith('#'):
                    if value.startswith(('assets/', 'style.css', 'site.js')): value = '../' + value
                    elif value.startswith('/assets/') or value in ('/style.css', '/site.js'): pass
                    elif value.startswith('/') and value.endswith('.html') and not value.startswith('/en/') and not info.get('lang') == 'tr': value = '/en' + value
                    elif info.get('class') == 'language-switch': value = '../' + value.removeprefix('en/')
            if info.get('class') == 'language-switch':
                if key == 'lang': value = 'tr'
                if key == 'aria-label': value = 'Türkçe'
            # 404 has its own explicit language links.
            if tag == 'a' and info.get('lang') == 'tr' and info.get('href') == '/404.html' and key == 'aria-current': continue
            updated.append(key + '="' + escape(value, quote=True) + '"')
        if tag == 'a' and info.get('href') == '/en/404.html': updated.append('aria-current="page"')
        self.output.append('<' + tag + (' ' if updated else '') + ' '.join(updated) + '>')

def decorate(page, filename):
    # Regeneration is idempotent: only remove metadata this builder owns.
    page = re.sub(r'<!-- portfolio-meta -->.*?<!-- /portfolio-meta -->', '', page, flags=re.S)
    if filename != '404.html' and 'class="language-switch"' not in page:
        page = page.replace('</nav>', f'<a class="language-switch" href="en/{filename}" lang="en" aria-label="English">EN</a></nav>', 1)
    metadata = ['<!-- portfolio-meta -->',
        '<meta property="og:image" content="' + BASE + '/assets/social-card.png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="Hasan Yazar — Software development &amp; AI">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:image" content="' + BASE + '/assets/social-card.png">']
    if filename != '404.html':
        for lang, route in [('tr', '/' + filename), ('en', '/en/' + filename), ('x-default', '/' + filename)]:
            metadata.append(f'<link rel="alternate" hreflang="{lang}" href="{BASE}{route}">')
    metadata.append('<!-- /portfolio-meta -->')
    return page.replace('</head>', '\n' + '\n'.join(metadata) + '\n</head>')

def main():
    (ROOT / 'en').mkdir(exist_ok=True)
    pages = sorted(ROOT.glob('*.html'))
    for path in pages:
        original = decorate(path.read_text(encoding='utf-8-sig'), path.name)
        path.write_text(original, encoding='utf-8')
        parser = EnglishPage()
        parser.feed(original)
        english = ''.join(parser.output)
        # The language link itself is translated independently of shared text nodes.
        english = re.sub(r'(<a class="language-switch"[^>]*>)EN</a>', r'\1TR</a>', english)
        (ROOT / 'en' / path.name).write_text(english, encoding='utf-8')
    urls = [BASE + prefix + p.name for p in pages if p.name != '404.html' for prefix in ('/', '/en/')]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join('<url><loc>' + url + '</loc></url>' for url in urls) + '\n</urlset>\n', encoding='utf-8')
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + BASE + '/sitemap.xml\n', encoding='utf-8')
    print(json.dumps(sorted(missing), ensure_ascii=False, indent=2))
    print(f'Built {len(pages)} English pages. Missing translations: {len(missing)}')
    if missing: raise SystemExit(1)

if __name__ == '__main__': main()
