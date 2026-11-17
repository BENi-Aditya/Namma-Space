#!/usr/bin/env python3
"""Adaptive, quality-first frame selection for COLMAP/Splatfacto training.

Replaces fixed-FPS or ffmpeg-only frame sampling (see extract-frames.sh) with
an OpenCV pass that analyses the whole video first, then keeps only frames
that are sharp and that show meaningful visual change from the previous kept
frame (via ORB feature matching + homography inlier ratio). This avoids both
redundant near-duplicate frames and large unrecoverable coverage gaps.

Two-stage pipeline:
  1. select_frames_opencv.py <video> <selection.json>   # this script
  2. extract_selected_frames.py <video> <selection.json> <images_dir>

Then run COLMAP / ns-process-data on <images_dir> as usual.
"""
import argparse
import json

import cv2
import numpy as np


def analyse_and_select(video_path, analysis_fps=4.0, max_gap=2.0, min_gap=0.5,
                        min_matches=20, min_inlier_ratio=0.20,
                        min_movement=5.0, max_movement=120.0):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f'Cannot open video: {video_path}')

    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps <= 0 or total <= 0:
        raise RuntimeError(f'Invalid FPS ({fps}) or frame count ({total}) reported for {video_path}')

    orb = cv2.ORB_create(nfeatures=2500)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    step = max(1, round(fps / analysis_fps))

    candidates = []
    print(f'Analysing {video_path} (fps={fps:.3f}, frames={total}, step={step})...', flush=True)
    for frame_no in range(0, total, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ok, frame = cap.read()
        if not ok:
            continue
        small = cv2.resize(frame, (960, 540))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        kp, des = orb.detectAndCompute(gray, None)
        candidates.append({
            'frame': frame_no, 'time': frame_no / fps,
            'sharpness': sharpness, 'features': len(kp),
            'kp': kp, 'des': des,
        })
        if len(candidates) % 200 == 0:
            print('Analysed:', len(candidates), flush=True)
    cap.release()

    if not candidates:
        raise RuntimeError('No frames analysed')

    sharp_values = np.array([c['sharpness'] for c in candidates])
    threshold = max(100.0, float(np.percentile(sharp_values, 10)) * 0.65)

    def compare(a, b):
        result = {'matches': 0, 'inlier_ratio': 0.0, 'movement': 0.0}
        if a['des'] is None or b['des'] is None:
            return result
        pairs = matcher.knnMatch(a['des'], b['des'], k=2)
        good = [p[0] for p in pairs if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]
        result['matches'] = len(good)
        if len(good) < min_matches:
            return result
        pts_a = np.float32([a['kp'][m.queryIdx].pt for m in good])
        pts_b = np.float32([b['kp'][m.trainIdx].pt for m in good])
        _, mask = cv2.findHomography(pts_a, pts_b, cv2.RANSAC, 3.0)
        if mask is None:
            return result
        inliers = mask.ravel().astype(bool)
        result['inlier_ratio'] = float(np.mean(inliers))
        if np.any(inliers):
            distances = np.linalg.norm(pts_a[inliers] - pts_b[inliers], axis=1)
            result['movement'] = float(np.median(distances))
        return result

    def is_good(result):
        return (result['matches'] >= min_matches
                and result['inlier_ratio'] >= min_inlier_ratio
                and min_movement <= result['movement'] <= max_movement)

    selected = [next((c for c in candidates if c['sharpness'] >= threshold), candidates[0])]
    rejected_gaps = []

    print('Selecting frames...', flush=True)
    for i, candidate in enumerate(candidates):
        if candidate['time'] <= selected[-1]['time']:
            continue
        if candidate['sharpness'] < threshold:
            continue
        last = selected[-1]
        gap = candidate['time'] - last['time']
        if gap < min_gap:
            continue
        result = compare(last, candidate)
        if is_good(result):
            candidate.update(result)
            selected.append(candidate)
        elif gap >= max_gap:
            options = [c for c in candidates if last['time'] < c['time'] < candidate['time']
                       and c['sharpness'] >= threshold]
            valid = [(opt, compare(last, opt)) for opt in options]
            valid = [(opt, r) for opt, r in valid if is_good(r)]
            if valid:
                best, best_result = max(valid, key=lambda x: x[0]['sharpness'])
                best.update(best_result)
                selected.append(best)
            else:
                rejected_gaps.append({
                    'start': round(last['time'], 3), 'end': round(candidate['time'], 3),
                    'duration': round(gap, 3), 'reason': 'No sharp candidate passed matching checks',
                })
        if (i + 1) % 300 == 0:
            print(f'Checked {i + 1}/{len(candidates)} | selected {len(selected)}', flush=True)

    last = candidates[-1]
    if last['time'] - selected[-1]['time'] >= min_gap:
        r = compare(selected[-1], last)
        if is_good(r):
            last.update(r)
            selected.append(last)
        else:
            rejected_gaps.append({
                'start': round(selected[-1]['time'], 3), 'end': round(last['time'], 3),
                'duration': round(last['time'] - selected[-1]['time'], 3),
                'reason': 'Final frame failed matching checks',
            })

    clean = [{k: v for k, v in item.items() if k not in ('kp', 'des')} for item in selected]
    gaps = [clean[i]['time'] - clean[i - 1]['time'] for i in range(1, len(clean))]

    return {
        'video': str(video_path), 'video_fps': fps, 'duration': total / fps,
        'analysis_fps': analysis_fps, 'candidate_count': len(candidates),
        'sharpness_threshold': threshold, 'selected_count': len(clean),
        'average_gap': float(np.mean(gaps)) if gaps else 0.0,
        'maximum_gap': float(max(gaps)) if gaps else 0.0,
        'rejected_gaps': rejected_gaps, 'selected': clean,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', help='Source video path')
    parser.add_argument('output', help='Where to write the selection JSON')
    parser.add_argument('--analysis-fps', type=float, default=4.0,
                         help='Sampling rate for the first analysis pass (default: 4)')
    parser.add_argument('--max-gap', type=float, default=2.0, help='Seconds; force-fill gaps larger than this')
    parser.add_argument('--min-gap', type=float, default=0.5, help='Seconds; minimum spacing between kept frames')
    parser.add_argument('--min-matches', type=int, default=20)
    parser.add_argument('--min-inlier-ratio', type=float, default=0.20)
    parser.add_argument('--min-movement', type=float, default=5.0)
    parser.add_argument('--max-movement', type=float, default=120.0)
    args = parser.parse_args()

    report = analyse_and_select(
        args.video, analysis_fps=args.analysis_fps, max_gap=args.max_gap, min_gap=args.min_gap,
        min_matches=args.min_matches, min_inlier_ratio=args.min_inlier_ratio,
        min_movement=args.min_movement, max_movement=args.max_movement,
    )
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print('\nSELECTION COMPLETE')
    print('Candidates:', report['candidate_count'])
    print('Selected:', report['selected_count'])
    print('Average gap:', round(report['average_gap'], 3))
    print('Maximum gap:', round(report['maximum_gap'], 3))
    print('Unresolved gaps:', len(report['rejected_gaps']))
    print('Report:', args.output)


if __name__ == '__main__':
    main()
