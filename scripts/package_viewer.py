#!/usr/bin/env python3
"""Build a standalone static viewer package, with no external symlinks."""
import argparse
import json
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
    for name in ['index.html', 'models.json', 'THIRD_PARTY_NOTICES.md']:
        shutil.copy2(source / name, destination / name)
    shutil.copytree(source / 'lib', destination / 'lib', symlinks=False)
    for asset in assets:
        target = destination / asset
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / asset, target)
    print(f'Packaged {len(assets)} referenced assets at {destination}; deploy this directory to a static HTTPS host.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'output/site')
    args = parser.parse_args()
    try:
        package(args.output.resolve())
    except (ValueError, OSError) as error:
        parser.exit(1, f'Packaging stopped: {error}\n')
