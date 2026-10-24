# Supported reproduction and setup

## Viewing existing exports

Use Python 3.10+ and run `./start-viewer.sh` from the repository; the launcher also works from another working directory. It serves apps/viewer only on 127.0.0.1. No conda, Node or GPU is needed to serve files. Rendering requires a WebGL2 desktop browser with sufficient memory. IMG_2008 is about 154 MiB on disk; download size and load latency matter. Neither 60 fps nor a fixed load time has been established.

On a fresh clone, restore the model archive (not yet published) into namma-space-project/output-models/models with the relative paths in apps/viewer/models.json. Run `python3 scripts/check_project.py` to identify missing models. The source repository by itself cannot reproduce the externally trained IMG_2008 asset: its source capture/config/checkpoint and contributor details remain missing. A source sample is in test/data/your-video.mov locally; its hash is documented in test/assets.json. It is the older baseline input, not the IMG_2008 source.

## Reconstruction environment

The existing environment is Python 3.10, torch 2.3.1, nerfstudio 1.1.5, gsplat 1.4.0, numpy 2.2.6. A freeze of its installed packages is in config/environment-observed.txt. This is an observation, not a validated clean-install lock. Existing setup scripts can reinstall/delete environments or use machine-specific paths; do not use them as unattended bootstrap scripts.

For a new machine, create a separate Python 3.10 environment and install Nerfstudio 1.1.5 and a platform-compatible PyTorch distribution, plus ffmpeg and COLMAP. Consult upstream installation instructions for the target OS. No clean install was tested here. Preserve the working local conda environment rather than upgrading its numerical stack before the deadline. Verify:

```bash
conda activate namma-space
python -c "import torch; print(torch.__version__, torch.backends.mps.is_available(), torch.cuda.is_available())"
ns-process-data video --help
ns-train nerfacto --help
ns-export pointcloud --help
ffmpeg -version
colmap -h
```

These CLI options were checked against the installed Nerfstudio source/help. CUDA Splatfacto is separate from MPS NeRF. Do not infer that a CUDA-only rasterizer runs on Metal from torch's MPS availability.

## New video to viewer

```bash
python scripts/pipeline/reconstruct.py test/data/tabletop-sample.mp4 room-20261025 --method nerfacto --device mps --iterations 7000
# Executes COLMAP, training and point-cloud export only when explicitly requested:
python scripts/pipeline/reconstruct.py test/data/tabletop-sample.mp4 room-20261025 --method nerfacto --device mps --iterations 7000 --execute
```

The wrapper `bash scripts/pipeline/process_video.sh ...` accepts the same arguments. Input paths resolve from the caller's working directory; output paths resolve from the repository. Choose a new run ID. Existing datasets/training outputs are never automatically deleted or reused. A failed run is preserved with run.json so it can be diagnosed. The runner uses sequential CPU COLMAP matching and targets 300 frames, then checks at least 20 finite camera matrices and all referenced RGB files. Twenty is a conservative engineering guard, not an official rule or sufficient visual-quality test. Inspect room coverage and pose continuity before committing to a long training run.

The MPS route uses Nerfacto's torch implementation, mixed precision disabled and 2048 rays/batch. These are starting settings, not a fastest/best benchmark. Increase quality only after a measured trial. The final NeRF export is point_cloud.ply, not a Gaussian model. The runner atomically registers an export after basic schema checks; browser inspection is still required. CUDA hosts can explicitly select `--method splatfacto --device cuda`, which exports splat.ply. That complete route was not executed here.

## Bounded Mac compatibility test

A 10-step test passed using 20 evenly spaced posed frames from 1-emergency resized to 320x180, in `.work/mac-smoke-20261024`. This reused existing poses and did not test fresh video extraction/COLMAP. Its log reports average training iteration 0.2678 s under that tiny configuration. It is not a throughput prediction for full-resolution training or a reconstruction quality result. See audit verification for the exact command and observed checkpoint. Never submit this smoke model as a trained room.

## Portable hosting bundle

`python3 scripts/package_viewer.py` copies only the viewer runtime, notices, manifest and referenced model assets to output/site, dereferencing model symlinks. It refuses an existing destination; use `--output output/site-v2` for another build. Deploy that directory to an HTTPS static host that accepts a 161 MB asset. Test every URL signed out, preferably on a second computer and network. The deployment URL and asset distribution remain external actions. Do not serve the repository root, .work or raw videos publicly.

A small video-only diagnostic excerpt is included in Git at test/data/tabletop-sample.mp4. It is a tabletop object capture; obtain a proper indoor-room sample for the final reconstruction evidence. The full original remains local.
