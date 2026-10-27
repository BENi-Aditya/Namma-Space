#!/usr/bin/env python3
"""Build a standalone static viewer package, with no external symlinks."""
import argparse
import json
import hashlib
import subprocess
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def package(destination):
    source = ROOT / 'apps/viewer'
    if destination.exists():
        raise ValueError('Destination exists; choose a fresh path. Nothing overwritten.')
    data = json.loads((source / 'models.json').read_text())
    assets = {m[k] for m in data['models'] for k in ['splat', 'stl', 'ply_mesh', 'pointcloud', 'obj'] if m.get(k)}
    for asset in assets:
        if not asset.startswith('models/') or '..' in Path(asset).parts or not (source / asset).is_file():
            raise ValueError(f'Missing or unsafe asset: {asset}')
    destination.mkdir(parents=True)
    for name in ['index.html', 'viewer.html', 'studio.css', 'gallery.js', 'models.json', 'THIRD_PARTY_NOTICES.md']:
        shutil.copy2(source / name, destination / name)
    shutil.copytree(source / 'lib', destination / 'lib', symlinks=False)
    for asset in assets:
        target = destination / asset
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / asset, target)
    # Public visitors receive the committed scene defaults, not their old local drafts.
    for name in ['viewer.html', 'gallery.js']:
        path = destination / name
        path.write_text(path.read_text().replace('const PUBLIC_VIEW = false;', 'const PUBLIC_VIEW = true;'))
    hashes = {}
    for asset in assets:
        sha = hashlib.sha256()
        with (destination / asset).open('rb') as stream:
            for block in iter(lambda: stream.read(1024*1024), b''): sha.update(block)
        hashes[asset] = sha.hexdigest()
    for model in data['models']:
        for key in ['splat','stl','ply_mesh','pointcloud','obj']:
            if model.get(key):
                asset = model[key]
                model[key] = asset + '?v=' + hashes[asset][:16]
    (destination / 'models.json').write_text(json.dumps(data,indent=2)+'\n')
    revision = subprocess.run(['git','rev-parse','HEAD'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    (destination / 'deployment.json').write_text(json.dumps({'commit':revision,'assets':hashes},indent=2)+'\n')
    version = hashlib.sha256((destination/'models.json').read_bytes()).hexdigest()[:16]
    for name in ['viewer.html','gallery.js']:
        path=destination/name
        path.write_text(path.read_text().replace("fetch('models.json',", "fetch('models.json?v=" + version + "',"))
    for name in ['index.html','viewer.html']:
        path=destination/name
        path.write_text(path.read_text().replace('href="studio.css"','href="studio.css?v='+revision[:12]+'"').replace('src="gallery.js"','src="gallery.js?v='+revision[:12]+'"'))
    (destination / '.nojekyll').touch()
    print(f'Packaged {len(assets)} referenced assets at {destination}; deploy this directory to a static HTTPS host.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'output/site')
    args = parser.parse_args()
    try:
        package(args.output.resolve())
    except (ValueError, OSError) as error:
        parser.exit(1, f'Packaging stopped: {error}\n')
