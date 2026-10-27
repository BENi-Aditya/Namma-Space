#!/usr/bin/env python3
"""Version exact viewer assets as compressed, size-bounded Git files; restore in CI."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
KEYS = ('splat', 'pointcloud', 'stl', 'ply_mesh', 'obj')
CHUNK_SIZE = 40 * 1024 * 1024

def references(data):
    paths = sorted({model[key] for model in data['models'] for key in KEYS if model.get(key)})
    for path in paths:
        if not path.startswith('models/') or '..' in Path(path).parts or Path(path).is_absolute():
            raise ValueError(f'Unsafe model asset: {path}')
    return paths

def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            result.update(block)
    return result.hexdigest()

def chunk_paths(store, entry):
    if not re.fullmatch('[a-f0-9]{64}', entry['sha256']): raise ValueError('Invalid asset hash')
    for index, part in enumerate(entry['chunks']):
        if part != f"{entry['sha256']}.{index:03d}.gzpart": raise ValueError('Invalid chunk path')
        path = store/'chunks'/part
        if not path.is_file(): raise ValueError(f'Missing release chunk: {part}')
        yield path

def snapshot(root=ROOT, stage=False):
    app = root/'apps/viewer'; store = root/'deployment/assets'; store.mkdir(parents=True,exist_ok=True)
    manifest = json.loads((app/'models.json').read_text())
    index_path = store/'index.json'
    old = json.loads(index_path.read_text())['assets'] if index_path.exists() else {}
    assets = {}
    for relative in references(manifest):
        path = app/relative
        if not path.is_file():
            if relative not in old: raise ValueError(f'Export not found: {relative}. Restore it before committing.')
            list(chunk_paths(store,old[relative]))
            assets[relative] = old[relative]
            continue
        sha = digest(path)
        previous = old.get(relative)
        if previous and previous['sha256']==sha and all((store/'chunks'/p).is_file() for p in previous['chunks']):
            assets[relative] = previous
            continue
        print(f'Preparing public model asset: {relative}',flush=True)
        (store/'chunks').mkdir(exist_ok=True)
        with tempfile.TemporaryFile() as compressed:
            with gzip.GzipFile(filename='',fileobj=compressed,mode='wb',mtime=0,compresslevel=6) as stream:
                with path.open('rb') as source: shutil.copyfileobj(source,stream,1024*1024)
            compressed.seek(0); parts=[]
            for number, data in enumerate(iter(lambda:compressed.read(CHUNK_SIZE),b'')):
                name=f'{sha}.{number:03d}.gzpart'; target=store/'chunks'/name
                if not target.exists(): target.write_bytes(data)
                parts.append(name)
        assets[relative]={'sha256':sha,'bytes':path.stat().st_size,'chunks':parts}
    index_path.write_text(json.dumps({'version':1,'assets':assets},indent=2)+'\n')
    if stage:
        # Include only the public manifest and its exact assets, not unrelated working changes.
        subprocess.run(['git','add','--','apps/viewer/models.json','deployment/assets'],cwd=root,check=True)
    print(f'Release snapshot ready: {len(assets)} assets. Saved view settings are in models.json.')

def restore(root=ROOT, destination=None):
    app=root/'apps/viewer';store=root/'deployment/assets'
    manifest=json.loads((app/'models.json').read_text())
    assets=json.loads((store/'index.json').read_text())['assets']
    output=Path(destination) if destination else app
    for relative in references(manifest):
        if relative not in assets: raise ValueError(f'{relative} is absent from the release snapshot. Run scripts/release_assets.py snapshot, commit and push.')
        entry=assets[relative];target=output/relative
        if target.is_file() and digest(target)==entry['sha256']:continue
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryFile() as compressed:
            for part in chunk_paths(store,entry):
                with part.open('rb') as stream:shutil.copyfileobj(stream,compressed)
            compressed.seek(0)
            pending=target.with_name(target.name+'.restoring')
            try:
                with gzip.GzipFile(fileobj=compressed,mode='rb') as stream,pending.open('wb') as dest:
                    shutil.copyfileobj(stream,dest,1024*1024)
                if pending.stat().st_size!=entry['bytes'] or digest(pending)!=entry['sha256']:
                    raise ValueError(f'Release asset checksum mismatch: {relative}')
                pending.replace(target)
            finally:pending.unlink(missing_ok=True)
    print('Release assets restored and SHA-256 verified.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['snapshot','restore'])
    parser.add_argument('--stage',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        if args.action=='snapshot':snapshot(stage=args.stage)
        else:restore(destination=args.output)
    except (ValueError,OSError,KeyError) as exc:parser.exit(1,f'Release blocked: {exc}\n')
if __name__=='__main__':main()
