"""One allowlist for both local preview and deployable static output."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ASSET_SUFFIXES = {'.svg', '.png', '.jpg', '.webp', '.woff2', '.pdf'}
PUBLIC_ROOT_FILES = {'style.css', 'site.js', 'robots.txt', 'sitemap.xml'}
CSP = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-src 'none'; frame-ancestors 'none'"
def is_public(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT) or not resolved.is_file(): return False
    relative = resolved.relative_to(ROOT)
    if any(part.startswith('.') for part in relative.parts): return False
    return ((len(relative.parts) == 1 and (relative.suffix == '.html' or relative.name in PUBLIC_ROOT_FILES))
            or (len(relative.parts) == 2 and relative.parts[0] == 'en' and relative.suffix == '.html')
            or (relative.parts[0] == 'assets' and relative.suffix in ASSET_SUFFIXES))
def public_files():
    candidates = list(ROOT.glob('*')) + list((ROOT / 'en').glob('*.html')) + list((ROOT / 'assets').rglob('*'))
    return sorted({path for path in candidates if is_public(path)})
