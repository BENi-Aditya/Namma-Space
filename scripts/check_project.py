#!/usr/bin/env python3
"""Check supported app integrity without running legacy or compute-heavy scripts."""
import ast
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from platform_compat import resolve_asset_path


def main():
    errors = []
    app = ROOT / 'apps/viewer'
    data = json.loads((app / 'models.json').read_text(encoding='utf-8'))
    ids = [model['id'] for model in data['models']]
    if len(ids) != len(set(ids)) or data.get('latest') not in ids:
        errors.append('Manifest duplicate IDs or invalid default')
    count = 0
    for model in data['models']:
        for key in ['splat', 'pointcloud', 'stl', 'ply_mesh', 'obj']:
            asset = model.get(key)
            if asset:
                count += 1
                resolved_asset = resolve_asset_path(app, asset)
                if not asset.startswith('models/') or '..' in Path(asset).parts or not resolved_asset.is_file():
                    errors.append(f'Missing or unsafe asset: {asset}')
    html = (app / 'viewer.html').read_text(encoding='utf-8')
    for filename in ['three.module.js', 'gaussian-splats-3d.module.js',
                     'three-addons/controls/OrbitControls.js', 'three-addons/controls/TransformControls.js',
                     'three-addons/loaders/PLYLoader.js', 'three-addons/loaders/STLLoader.js',
                     'three-addons/exporters/STLExporter.js']:
        if not (app / 'lib' / filename).is_file():
            errors.append(f'Missing runtime: {filename}')
    
    node_cmd = shutil.which('node')
    if node_cmd:
        module = re.search(r'<script type="module">(.*?)</script>', html, re.S).group(1)
        parsed = subprocess.run([node_cmd, '--input-type=module', '--check'], input=module, text=True, capture_output=True)
        if parsed.returncode:
            errors.append(parsed.stderr)
        for name in ['admin.js', 'gallery.js']:
            result = subprocess.run([node_cmd, '--check', str(app / name)], capture_output=True, text=True)
            if result.returncode:
                errors.append(result.stderr)
    
    for p in [ROOT / 'scripts/admin_server.py', ROOT / 'scripts/serve_viewer.py', ROOT / 'scripts/package_viewer.py', ROOT / 'scripts/pipeline/reconstruct.py', ROOT / 'scripts/pipeline/export_model.py']:
        ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
    
    bash_cmd = shutil.which('bash')
    if bash_cmd and not bash_cmd.lower().endswith('windowsapps\\bash.exe'):
        for relative in ['start-admin.sh', 'start-viewer.sh', 'scripts/pipeline/process_video.sh']:
            if subprocess.run([bash_cmd, '-n', str(ROOT / relative)], capture_output=True).returncode:
                errors.append(f'Shell syntax error: {relative}')
                
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'PASS: {len(ids)} manifest models, {count} asset references, vendored imports, JS/Python/shell syntax.')
    print('Not a reconstruction-quality, public-deployment or browser-performance acceptance test.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
