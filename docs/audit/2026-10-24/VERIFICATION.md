# Verification and progress record - 24 October 2026

## Completed changes

- Recorded initial inventory and dirty Git state; backed up edited small source files in ignored .local-backups/2026-10-24.
- Moved supported static app into apps/viewer, retained relative compatibility aliases, archived historical root plans and preserved external React source as an experiment. Physical data/checkpoints/models remain in place.
- Replaced process-killing launcher with a localhost-only server that refuses occupied ports. Added portable packaging with referenced assets, vendor notices and no external symlinks.
- Added supported dry-run pipeline with unique-run protection, exact config selection, pose/image guards, explicit Mac NeRF versus CUDA splat methods and atomic manifest registration after valid export.
- Added first-person mouse look, hold-and-drag fallback, reset, uncluttered default interface, serialized model loading and failure feedback. Removed unsupported metric dimension labels.
- Updated README, reproduction, script guidance, provenance hashes, dated requirement checklist, execution plan and structure mapping.
- Created and visually checked a 4-page abstract review draft and a 1-page organized master-links review draft, plus a 4-minute video storyboard.

## Passed / observed

| Check | Evidence and limits |
|---|---|
| Five safe regression tests | python3 -m unittest discover -s test -v: all pass. Covers run preservation, invalid poses/images and failed export registration; no training simulated as a quality result |
| Supported source and asset integrity | scripts/check_project.py passes: 4 model IDs, 11 asset references (10 distinct files), runtime imports, JS module syntax, Python AST and supported shell syntax |
| Local browser rendering | Existing 650,682-Gaussian PLY renders in the in-app browser, and switching to 1-emergency STL then back works. Initial Gaussian view fragmented; mesh fallback also lacks convincing room structure |
| First-person fallback | Embedded browser rejects pointer lock; status activates hold-and-drag look. Drag visibly changes view. Escape/reset and model selection were exercised. WASD key was dispatched; no sustained desktop-browser FPS or floor-level walkthrough acceptance claimed |
| Mac GPU hardware | system_profiler reports Apple M5 Max, 32 GPU cores. Outside sandbox: torch MPS built/available true and tensor allocation on mps:0 succeeds |
| Mac NeRF training smoke | 20 preposed images, resized 320x180, 10 iterations. Training completed and wrote .work/mac-smoke-20261024/training/mac-smoke/nerfacto/2026-10-24_152256/nerfstudio_models/step-000000009.ckpt. Log: mac-smoke-log.txt. Tiny-config average iteration reported 0.2678 s; not a full-quality ETA |
| Original datasets | 1-emergency has 252 posed frames; 2-run has 306; all referenced RGB files exist. This does not establish coverage, correctness or room fidelity |
| Real source sample | Copied baseline 36.7 s / 1280x720 / 30 fps clip into test/data; SHA in test/assets.json. It includes original audio and is not publicly distributed without owner review |
| Portable static bundle | output/site generated with 10 distinct referenced assets, roughly 226 MiB; a refreshed final package and symlink/hash check are recorded below when complete |
| PDFs | pypdf: abstract 4 pages, links 1 page; all final pages rendered and visually checked after spacing adjustment. Both remain visibly labeled drafts |
| Remote repository baseline | git ls-remote confirms requested Namma-Space/main starts at 2c97f21, same as local base. GitHub CLI reports not authenticated; Git transport publication is attempted separately |

## Exact Mac smoke command

Executed from repository root using the existing conda environment PATH, PYTORCH_ENABLE_MPS_FALLBACK=1 and a writable temporary Matplotlib cache:

```bash
ns-train nerfacto --data namma-space-project/.work/mac-smoke-20261024/input --output-dir namma-space-project/.work/mac-smoke-20261024/training --experiment-name mac-smoke --max-num-iterations 10 --machine.device-type mps --mixed-precision False --vis tensorboard --pipeline.model.implementation torch --pipeline.datamanager.train-num-rays-per-batch 256 --pipeline.model.num-nerf-samples-per-ray 16 --pipeline.model.num-proposal-samples-per-ray 32 16 nerfstudio-data --downscale-factor 1
```

Data preparation used every twelfth frame (first 20) from existing 1-emergency transforms, scaled RGB to 320x180 and scaled intrinsics consistently; no fresh camera estimation was performed. No original capture/config/checkpoint was modified.

## Failed or limited checks

- Initial in-sandbox server bind failed (permission restriction); allowed localhost servers were then started outside the sandbox. Initial sandbox GPU query returned false; direct unsandboxed MPS allocation/training supersedes it.
- Embedded-browser pointer lock is blocked. Drag-look fallback was added and visually exercised. Full pointer-lock behavior in a standalone Chrome/Firefox/Safari remains unverified.
- Initial PDF rendering produced font-cache errors; rerendering with a temporary writable Fontconfig cache succeeded. Final PDF pages were inspected.
- GitHub CLI is not signed in. Remote read is public; it does not prove write authentication. See publication result below.

## Not run / remaining blockers

Fresh video -> COLMAP -> complete quality training -> export -> deployed browser was not run. No clean environment installation, full-resolution Mac speed benchmark, holdout fidelity evaluation, calibrated scale, timed FPS test, second-device test, public HTTPS deployment, final narration/screen recording, public sample clearance, Drive permissions or portal submission has passed. No CUDA Gaussian training was attempted; installed gsplat rasterization is CUDA-based. Source/config/ownership for IMG_2008 is missing.

This project is NOT yet Round 1 submission-ready. The next critical action is selecting a traceable own-room capture and establishing a recognizable reconstruction before recording/deploying. See PLAN.md for priorities and definitions of done.

## Final diagnostic sample

Added test/data/tabletop-sample.mp4: 8 s, 640x360, 598,152 bytes. ffprobe confirms one video stream and no audio; metadata stripped. Four evenly spaced frames inspected. This real derivative is included for pipeline diagnostics; it does not establish the mandatory full indoor-room capture. Full original clip remains local/ignored.

## Final package check

output/site-final refreshed to the final app source. Ten distinct model files match SHA-256 hashes of their source assets; no symlinks remain anywhere in the bundle. Source checks pass. Five regression tests now pass, including double-precision XYZ export registration as a point cloud without claiming Gaussian splats. Git diff --check passes. Large model exports, raw full audio capture, local backups, reconstruction checkpoints and deployment bundles are excluded from new Git additions.

## Launcher / HTTP checks

The running updated viewer returned HTTP 200 for 13 distinct app/runtime/model URLs. Starting a second server on occupied port 8766 exited with a clear error and left the original server running. Launcher --help and the supported pipeline dry run work from /tmp with absolute input paths, confirming outputs resolve from repository location. A Git check-ignore call using a path beneath the models symlink was rejected by Git (pathspec beyond symbolic link); ignore status was subsequently enforced by reviewing the actual staged file set.

## Publication

Reviewed changes are staged for the owner-requested Namma-Space repository. Full original captures/audio, checkpoints, local backups, generated deployment bundle and the >100 MB Gaussian asset are not staged. The small video-only diagnostic excerpt is staged. Publication result will be appended after the Git transport attempt.

## Staging correction

Review caught output/site-final in the staged set because the initial ignore matched only output/site. The final bundle was unstaged without deleting it, and output/ is now ignored as a whole. No generated bundle was committed or transmitted by that initial staging. Binary document/model attributes avoid treating PDFs/PLY as text diffs; vendored/history formatting is preserved. The saved smoke log has ANSI terminal controls and trailing spaces normalized for readable review.
