"""Package only public files. No scripts, reports, repository metadata or secrets."""
from shutil import copy2
from public_files import ROOT, public_files
output = ROOT / 'dist'
if output.exists() and any(output.iterdir()):
    raise SystemExit('dist must be empty; use a clean checkout or a new output directory.')
output.mkdir(exist_ok=True)
for source in public_files():
    destination = output / source.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    copy2(source, destination)
copy2(ROOT / '_headers', output / '_headers')
(output / '.nojekyll').touch()
print(f'Packaged {len(public_files())} public files into dist.')
