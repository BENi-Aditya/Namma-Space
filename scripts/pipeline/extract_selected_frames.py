#!/usr/bin/env python3
"""Extract the full-resolution frames chosen by select_frames_opencv.py.

Usage:
    python scripts/pipeline/extract_selected_frames.py <video> <selection.json> <images_dir>

Writes one frame_NNNNN.jpg per selected entry (in selection order) plus a
manifest.json recording which source frame/timestamp each file came from.
"""
import argparse
import json
import os

import cv2


def extract(video_path, selection_path, output_dir, jpeg_quality=95):
    with open(selection_path, encoding='utf-8') as f:
        data = json.load(f)
    selected = data['selected']

    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f'Cannot open video: {video_path}')

    manifest = []
    print(f'Extracting {len(selected)} full-resolution frames to {output_dir}...', flush=True)
    for i, item in enumerate(selected):
        frame_no = item['frame']
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f'Failed to read frame {frame_no} ({video_path} may be shorter than expected)')
        filename = f'frame_{i + 1:05d}.jpg'
        cv2.imwrite(os.path.join(output_dir, filename), frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
        manifest.append({'filename': filename, 'source_frame': frame_no, 'timestamp': item['time']})
        if (i + 1) % 100 == 0:
            print(f'Extracted {i + 1}/{len(selected)}', flush=True)
    cap.release()

    manifest_path = os.path.join(output_dir, 'manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print('\nEXTRACTION COMPLETE')
    print('Frames written:', len(manifest))
    print('Output dir:', output_dir)
    print('Manifest:', manifest_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', help='Source video path (same one passed to select_frames_opencv.py)')
    parser.add_argument('selection', help='selection.json produced by select_frames_opencv.py')
    parser.add_argument('output_dir', help='Directory to write frame_NNNNN.jpg + manifest.json into')
    parser.add_argument('--jpeg-quality', type=int, default=95)
    args = parser.parse_args()
    extract(args.video, args.selection, args.output_dir, jpeg_quality=args.jpeg_quality)


if __name__ == '__main__':
    main()
