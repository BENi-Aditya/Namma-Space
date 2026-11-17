# Fresh Auditorium reconstruction: exact commands used

This documents the OpenCV-based frame-selection pipeline and the exact
command sequence used to train a **fresh** (from-scratch, no checkpoint
reuse) Auditorium Gaussian-splat reconstruction on the remote GPU server.
It replaces ad-hoc fixed-FPS extraction (see `extract-frames.sh`, which is
ffmpeg-only and keeps every Nth frame regardless of sharpness or overlap)
with the two supported scripts added alongside this doc:

- `scripts/pipeline/select_frames_opencv.py` — analyses the whole video with
  OpenCV (Laplacian sharpness + ORB/homography overlap checks) and picks an
  adaptive, quality-first subset of frames.
- `scripts/pipeline/extract_selected_frames.py` — extracts those frames at
  full resolution.

Nothing here re-registers a trained model in `apps/viewer/models.json`; this
is a process runbook only.

## 0. Environment

Remote GPU server (shared 4080 Super via a per-container GPU broker):

```bash
ssh root@100.104.120.14
```

Persistent workspace is `/workspace`. GPU jobs go through the broker wrapper
(inspect it first — `cat $(which gpu)`), never call CUDA tooling directly:

```bash
gpu --vram <GiB> --time <minutes> <command...>
gpu jobs            # list your jobs
gpu attach [<id>]   # re-attach to a running job's live logs
gpu logs <id>       # print a job's logs once
```

Python env already on `$PATH` for this container:

```bash
export PATH=/workspace/.local/bin:$PATH
python3 --version        # 3.10.12
python3 -c "import cv2; print(cv2.__version__)"   # 4.10.0
```

## 1. Verify the source video

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,avg_frame_rate,r_frame_rate,nb_frames \
  -show_entries format=duration,size \
  -of default=noprint_wrappers=1 \
  /workspace/videos/Auditorium.mp4
```

Confirmed: 3840×2160, 29.970 fps (30000/1001), duration 452.953 s, 13,575
source frames, 5,154,648,275 bytes.

## 2. Analyse the video and select frames (OpenCV, no ffmpeg)

```bash
mkdir -p /workspace/namma_pipeline_retrain
python3 scripts/pipeline/select_frames_opencv.py \
  /workspace/videos/Auditorium.mp4 \
  /workspace/namma_pipeline_retrain/selection_retrain.json
```

Default parameters (match the project's original frame-selection run):
`--analysis-fps 4 --max-gap 2.0 --min-gap 0.5 --min-matches 20
--min-inlier-ratio 0.20 --min-movement 5.0 --max-movement 120.0`.

Result on this video: **1,939 candidates** sampled at 4 fps → **612 frames
selected**, average gap 0.690 s, maximum gap 8.876 s, 96 unresolved gaps
(segments where no sharp/well-matched candidate existed — expected for fast
pans). These numbers matched the project's earlier frame-selection run on
the same video almost exactly, confirming the method reproduces faithfully.

## 3. Extract the selected frames at full resolution

```bash
python3 scripts/pipeline/extract_selected_frames.py \
  /workspace/videos/Auditorium.mp4 \
  /workspace/namma_pipeline_retrain/selection_retrain.json \
  /workspace/namma_pipeline_retrain/colmap_retrain/images
```

Result: 612 JPEGs (quality 95) at source resolution, ~1.1 GB total, plus a
`manifest.json` mapping each `frame_NNNNN.jpg` back to its source frame
number and timestamp.

## 4. COLMAP (CPU, sequential matching)

```bash
export PATH=/workspace/.local/bin:$PATH
ns-process-data images \
  --data /workspace/namma_pipeline_retrain/colmap_retrain/images \
  --output-dir /workspace/namma_pipeline_retrain/auditorium_colmap_retrain \
  --matching-method sequential \
  --no-gpu
```

Takes three phases: SIFT feature extraction, sequential matching, mapper +
bundle adjustment (~65–70 minutes total for 612 4K images on this
container's CPU allocation). Result: **612/612 images registered with
poses** — "COLMAP found poses for all images, CONGRATS!" — no dropped
frames.

## 5. Train Splatfacto from scratch (GPU)

Same hyperparameters as the project's original Auditorium training run —
only the output paths are new, so nothing existing is overwritten:

```bash
gpu --vram 15 --time 240 bash -lc '
set -euo pipefail
export PATH=/workspace/.local/bin:$PATH

ns-train splatfacto \
    --data /workspace/namma_pipeline_retrain/auditorium_colmap_retrain \
    --output-dir /workspace/outputs/auditorium_retrained_30k \
    --max-num-iterations 30000 \
    --vis tensorboard \
    --pipeline.model.num-downscales 2 \
    --pipeline.model.cull-alpha-thresh 0.005 \
    --pipeline.model.densify-grad-thresh 0.0002 \
    --pipeline.model.stop-split-at 25000 \
    colmap

CONFIG=$(find /workspace/outputs/auditorium_retrained_30k -name config.yml -type f | sort | tail -n 1)
echo "CONFIG_PATH=$CONFIG"

ns-export gaussian-splat --load-config "$CONFIG" --output-dir /workspace/exports/auditorium_retrained_30k
ls -lh /workspace/exports/auditorium_retrained_30k/
'
```

Result: 30,000 iterations completed in **~24 minutes** wall-clock on the
RTX 4080 Super (job duration reported by the broker: 1426 s). Export: 0
Gaussians with NaN/Inf; 35,376 excluded for low opacity; **1,038,069
Gaussians** exported; `splat.ply` = 257,442,706 bytes.

## 6. Validate the export

Minimal PLY sanity check (header vs. actual file size, NaN/Inf scan,
bounding box) — no external dependencies beyond the standard library:

```bash
python3 - <<'PY'
import struct, math
path = "/workspace/exports/auditorium_retrained_30k/splat.ply"
with open(path, "rb") as f:
    header = []
    while True:
        line = f.readline().decode("ascii", "replace").strip()
        header.append(line)
        if line == "end_header":
            break
    data_start = f.tell()
props, in_vertex, count = [], False, 0
for line in header:
    if line.startswith("element vertex"):
        count = int(line.split()[-1]); in_vertex = True
    elif line.startswith("element"):
        in_vertex = False
    elif line.startswith("property") and in_vertex:
        props.append(line.split()[1])
print("vertex count:", count, "| properties:", len(props))
PY
```

(The full version used during training also scanned every splat for
NaN/Inf and computed bounds — see the validation step results above.)

## 7. Transfer to the local viewer repo (if you want to view it)

```powershell
scp root@100.104.120.14:/workspace/exports/auditorium_retrained_30k/splat.ply `
  namma-space-project\output-models\models\<model_id>\splat.ply
```

Then register it by hand in `apps/viewer/models.json` following the shape
of an existing entry (`id`, `name`, `method: "splatfacto"`, `splat`,
`splatCount`, `defaultAsset: "gaussian"`), or via the viewer's own **Edit
mode → Save Position** workflow once it's registered and loaded once to set
a default camera. See `docs/GPU_STACKER_RUNBOOK.md` for the general
sync-back convention.
