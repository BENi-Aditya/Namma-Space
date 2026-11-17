#!/usr/bin/env python3
"""Supported video -> COLMAP -> Splatfacto -> viewer pipeline. Dry-run by default."""
import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from platform_compat import file_lock, terminate_process
VIEWER = ROOT / 'apps/viewer'
WORK = ROOT / 'namma-space-project/.work'
MIN_FRAME_TARGET = 1001
FRAME_SAMPLING_RATE = 8


def recommend_frame_target(metadata):
    streams = metadata.get('streams', [])
    if not streams:
        raise ValueError('FFprobe found no video stream.')
    stream = streams[0]
    durations = [stream.get('duration'), metadata.get('format', {}).get('duration')]
    duration = next((value for value in durations if value and value != 'N/A'), None)
    if duration is None:
        raise ValueError('FFprobe did not report the video duration.')
    try:
        duration = float(duration)
    except (TypeError, ValueError):
        raise ValueError(f'Invalid video duration reported by FFprobe: {duration}') from None
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f'Invalid video duration reported by FFprobe: {duration}')

    frame_rate = None
    for candidate in (stream.get('avg_frame_rate'), stream.get('r_frame_rate')):
        try:
            parsed_rate = float(Fraction(candidate))
        except (ValueError, ZeroDivisionError, TypeError):
            continue
        if math.isfinite(parsed_rate) and parsed_rate > 0:
            frame_rate = parsed_rate
            break
    if frame_rate is None:
        raise ValueError('FFprobe did not report a valid video frame rate.')
    if not math.isfinite(frame_rate) or frame_rate <= 0:
        raise ValueError(f'Invalid video frame rate reported by FFprobe: {frame_rate}')

    reported_frames = stream.get('nb_frames')
    source_frames = int(reported_frames) if reported_frames and reported_frames != 'N/A' else math.ceil(duration * frame_rate)
    if source_frames <= 0:
        raise ValueError(f'Invalid source frame count reported by FFprobe: {source_frames}')

    target_frames = min(source_frames, max(MIN_FRAME_TARGET, math.ceil(duration * FRAME_SAMPLING_RATE)))
    return {
        'duration_seconds': duration,
        'source_frames': source_frames,
        'target_frames': target_frames,
    }


def inspect_video(video):
    if not shutil.which('ffprobe'):
        return {'duration_seconds': 0.0, 'source_frames': 300, 'target_frames': 300}
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'format=duration:stream=avg_frame_rate,r_frame_rate,nb_frames,duration',
             '-of', 'json', str(video)],
            check=True, capture_output=True, text=True,
        )
        return recommend_frame_target(json.loads(result.stdout))
    except Exception:
        return {'duration_seconds': 0.0, 'source_frames': 300, 'target_frames': 300}


def validate_poses(directory, min_frames=20):
    data = json.loads((directory / 'transforms.json').read_text(encoding='utf-8'))
    frames = data.get('frames', [])
    if len(frames) < min_frames:
        raise ValueError(f'Only {len(frames)} registered frames; need at least {min_frames}. Recapture before training.')
    for frame in frames:
        image = (directory / frame['file_path']).resolve()
        if not image.is_relative_to(directory.resolve()) or not image.is_file():
            raise ValueError(f'Missing or unsafe registered image: {image}')
        matrix = frame.get('transform_matrix', [])
        if len(matrix) != 4 or any(len(row) != 4 for row in matrix):
            raise ValueError('Camera transform must be 4x4')
        if not all(math.isfinite(float(value)) for row in matrix for value in row):
            raise ValueError('Non-finite camera transform')
    return len(frames)


def register_model(viewer, room, ply, method="splatfacto"):
    with (viewer / "models.lock").open("a", encoding='utf-8') as lock:
        with file_lock(lock, exclusive=True):
            return _register_model(viewer, room, ply, method)


def _register_model(viewer, room, ply, method="splatfacto"):
    with ply.open('rb') as stream:
        header = stream.read(16384).split(b'end_header', 1)[0]
    properties = {line.split()[-1]: line.split()[1] for line in header.splitlines() if line.startswith(b'property ') and len(line.split()) == 3}
    coordinates_valid = all(properties.get(axis) in {b'float', b'double', b'float32', b'float64'} for axis in [b'x', b'y', b'z'])
    if method == 'splatfacto':
        valid = all(name in properties for name in [b'x', b'opacity', b'scale_0', b'rot_0'])
    else:
        valid = coordinates_valid
    if not header.startswith(b'ply\n') or not valid:
        raise ValueError('Export is not a valid Gaussian PLY or point-cloud PLY for the selected method')
    manifest = viewer / 'models.json'
    data = json.loads(manifest.read_text(encoding='utf-8'))
    asset = 'splat' if method == 'splatfacto' else 'pointcloud'
    entry = {'id': room, 'name': room, 'method': method,
             asset: f'models/{room}/{ply.name}',
             'defaultAsset': 'gaussian' if method == 'splatfacto' else 'pointcloud',
             'units': 'uncalibrated reconstruction units'}
    data['models'] = [entry] + [m for m in data['models'] if m['id'] != room]
    data['latest'] = room
    temp = manifest.with_suffix('.json.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, manifest)


def run_pipeline(video, room, iterations, execute=False, method="splatfacto", device="cuda", viewer_port=None, num_frames_target=300):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', room):
        raise ValueError('Room ID must contain only letters, digits, underscores or hyphens (max 64).')
    if method == 'splatfacto' and device != 'cuda':
        raise ValueError('Installed Splatfacto/gsplat requires CUDA. Use nerfacto with mps on macOS.')
    video = video.expanduser().resolve()
    if not video.is_file():
        raise ValueError(f'Video not found: {video}')
    processed = WORK / room
    training = WORK / f'training-{room}'
    export = VIEWER / 'models' / room
    manifest = json.loads((VIEWER / 'models.json').read_text(encoding='utf-8'))
    if any(p.exists() for p in [processed, training, export]) or any(m['id'] == room for m in manifest['models']):
        raise ValueError('Room already exists. Choose a new ID; existing data will never be deleted or overwritten.')
    
    target_frames = num_frames_target or 300

    def cli_path(path):
        rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        return rel.replace('\\', '/')

    commands = [
        ['ns-process-data', 'video', '--data', cli_path(video), '--output-dir', cli_path(processed),
         '--num-frames-target', str(target_frames), '--matching-method', 'sequential', '--no-gpu'],
        ['ns-train', method, '--data', cli_path(processed), '--output-dir', cli_path(training),
         '--experiment-name', room, '--max-num-iterations', str(iterations),
         '--machine.device-type', device, '--vis', 'tensorboard', '--logging.local-writer.max-log-size', '0'],
    ]
    if method == 'nerfacto':
        commands[1] += ['--mixed-precision', 'False', '--pipeline.model.implementation', 'torch',
                        '--pipeline.datamanager.train-num-rays-per-batch', '2048']
    if viewer_port:
        commands[1][commands[1].index('tensorboard')] = 'viewer+tensorboard'
        commands[1] += ['--viewer.websocket-host', '127.0.0.1', '--viewer.websocket-port', str(viewer_port), '--viewer.quit-on-train-completion', 'True']
    export_kind = 'gaussian-splat' if method == 'splatfacto' else 'pointcloud'
    for command in commands:
        print(shlex.join(command), flush=True)
    print(f'ns-export {export_kind} --load-config <config from {training}> --output-dir {shlex.quote(str(export))}', flush=True)
    if not execute:
        print('DRY RUN: no files created, no reconstruction or training started. Use --execute after reviewing device, iteration count and output paths.')
        return
    for executable in ['ns-process-data', 'ns-train', 'ns-export', 'ffmpeg', 'colmap']:
        if not shutil.which(executable):
            raise ValueError(f'Missing executable: {executable}; activate the reconstruction environment.')
    check = {'cuda': 'torch.cuda.is_available()', 'mps': 'torch.backends.mps.is_available()', 'cpu': 'True'}[device]
    capability = subprocess.run([sys.executable, '-c', f'import torch; raise SystemExit(0 if {check} else 1)'])
    if capability.returncode:
        raise ValueError(f'{device} is unavailable in this Python environment. No training started.')
    processed.mkdir(parents=True)
    os.environ.setdefault('PYTORCH_ENABLE_MPS_FALLBACK', '1')
    digest = hashlib.sha256()
    with video.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    record = {'video_name': video.name, 'video_sha256': digest.hexdigest(), 'room': room, 'method': method, 'device': device, 'iterations_requested': iterations,
              'target_frames': target_frames,
              'commands': commands, 'state': 'processing'}
    record_file = processed / 'run.json'
    try:
        print("NAMMA_STAGE processing", flush=True)
        subprocess.run(commands[0], check=True, cwd=ROOT)
        record['registered_frames'] = validate_poses(processed)
        print("NAMMA_STAGE training", flush=True)
        subprocess.run(commands[1], check=True, cwd=ROOT)
        configs = list(training.rglob('config.yml'))
        if len(configs) != 1:
            raise ValueError(f'Expected exactly one config from this run; found {len(configs)}. Select manually; no export registered.')
        command = [sys.executable, str(ROOT / 'scripts/pipeline/export_model.py'), export_kind, '--load-config', str(configs[0]), '--output-dir', str(export)]
        if method == 'nerfacto':
            command += ['--num-points', '150000', '--num-rays-per-batch', '2048', '--normal-method', 'open3d']
        record['commands'].append(command)
        print('NAMMA_STAGE exporting', flush=True)
        subprocess.run(command, check=True, cwd=ROOT)
        register_model(VIEWER, room, export / ('splat.ply' if method == 'splatfacto' else 'point_cloud.ply'), method)
        record['state'] = 'exported; browser quality review still required'
    except Exception as error:
        record['state'] = 'failed'
        record['error'] = str(error)
        raise
    finally:
        record_file.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'Export registered. Review http://127.0.0.1:8080/viewer.html?model={room} before selecting it for submission.')


def main():
    parent = os.environ.get('NAMMA_PARENT_PID')
    if parent:
        def watch_parent():
            while True:
                time.sleep(1)
                try:
                    if hasattr(os, 'getppid'):
                        current_parent = os.getppid()
                    else:
                        break
                except Exception:
                    break
                if current_parent != int(parent):
                    if hasattr(os, 'killpg') and hasattr(os, 'getpgrp'):
                        os.killpg(os.getpgrp(), signal.SIGTERM)
                    else:
                        sys.exit(0)
                    return
        threading.Thread(target=watch_parent, daemon=True).start()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('room', help='New unique run/model ID')
    parser.add_argument('--iterations', type=int, default=7000, help='Engineering smoke preset, not a quality guarantee')
    parser.add_argument('--method', choices=['nerfacto', 'splatfacto'], default='nerfacto')
    parser.add_argument('--device', choices=['mps', 'cuda', 'cpu'], default='mps' if sys.platform == 'darwin' else 'cuda')
    parser.add_argument('--viewer-port', type=int)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error('iterations must be positive')
    try:
        run_pipeline(args.video, args.room, args.iterations, args.execute, args.method, args.device, args.viewer_port)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Pipeline stopped: {error}\n')


if __name__ == '__main__':
    main()
