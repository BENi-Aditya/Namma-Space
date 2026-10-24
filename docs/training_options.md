# Training options

Use the supported reconstruction entry point from the repository root. It runs
in dry-run mode unless `--execute` is supplied and refuses to overwrite an
existing run or model ID.

## Splatfacto (Gaussian splats)

Splatfacto requires a working CUDA environment with the installed
Nerfstudio/gsplat dependencies. Replace the video path and run ID with your
local input and a new, unique ID:

```bash
bash scripts/pipeline/process_video.sh path/to/video.mp4 room-splat \
  --method splatfacto --device cuda --iterations 7000
```

Review the printed commands and output paths first. Add `--execute` only when
you are ready to start processing and training:

```bash
bash scripts/pipeline/process_video.sh path/to/video.mp4 room-splat \
  --method splatfacto --device cuda --iterations 7000 --execute
```

## Nerfacto (NeRF)

Nerfacto can use a device supported by the installed PyTorch build. For an
NVIDIA CUDA environment:

```bash
bash scripts/pipeline/process_video.sh path/to/video.mp4 room-nerf \
  --method nerfacto --device cuda --iterations 7000
```

After reviewing the dry-run output, add `--execute` to start the run. Use
`--device mps` only when PyTorch reports MPS available, or `--device cpu` when
slower CPU training is intended.

The pipeline processes the input video and runs COLMAP on CPU, then trains
using the selected device. Its default iteration count is an engineering
smoke preset, not a quality or completion-time guarantee. Training requires
the corresponding Nerfstudio commands and FFmpeg/COLMAP tools to be installed.
The exported model is written to the local `apps/viewer/models/<run-id>/`
directory and registered in the local viewer manifest; generated model assets
are not source files and should not be committed.
