#!/usr/bin/env python3
"""Check supported app integrity without running legacy or compute-heavy scripts."""
import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    app = ROOT / 'apps/viewer'
    data = json.loads((app / 'models.json').read_text())
    ids = [model['id'] for model in data['models']]
    if len(ids) != len(set(ids)) or data.get('latest') not in ids:
        errors.append('Manifest duplicate IDs or invalid default')
    count = 0
    for model in data['models']:
        for key in ['splat', 'pointcloud', 'stl', 'ply_mesh', 'obj']:
            asset = model.get(key)
            if asset:
                count += 1
                if not asset.startswith('models/') or '..' in Path(asset).parts or not (app / asset).is_file():
                    errors.append(f'Missing or unsafe asset: {asset}')
    html = (app / 'index.html').read_text()
    for filename in ['three.module.js', 'gaussian-splats-3d.module.js',
                     'three-addons/controls/OrbitControls.js', 'three-addons/controls/TransformControls.js',
                     'three-addons/loaders/PLYLoader.js', 'three-addons/loaders/STLLoader.js',
                     'three-addons/exporters/STLExporter.js']:
        if not (app / 'lib' / filename).is_file():
            errors.append(f'Missing runtime: {filename}')
    module = re.search(r'<script type="module">(.*?)</script>', html, re.S).group(1)
    # Parse only, no DOM/WebGL execution; browser checks are separate.
    parsed = subprocess.run(['node', '--input-type=module', '--check'], input=module, text=True, capture_output=True)
    if parsed.returncode:
        errors.append(parsed.stderr)
    for p in [ROOT / 'scripts/serve_viewer.py', ROOT / 'scripts/package_viewer.py', ROOT / 'scripts/pipeline/reconstruct.py']:
        ast.parse(p.read_text(), filename=str(p))
    for relative in ['start-viewer.sh', 'scripts/pipeline/process_video.sh']:
        if subprocess.run(['bash', '-n', str(ROOT / relative)], capture_output=True).returncode:
            errors.append(f'Shell syntax error: {relative}')
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'PASS: {len(ids)} manifest models, {count} asset references, vendored imports, JS/Python/shell syntax.')
    print('Not a reconstruction-quality, public-deployment or browser-performance acceptance test.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
