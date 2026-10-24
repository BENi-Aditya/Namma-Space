# Namma Space audit - 24 October 2026

## Initial findings, before implementation

The supplied official brief (pages 3, 5-6) confirms Round 1 on 31 October 2026, with no cutoff time/timezone. Registration closed 30 September; Team ID and registration are unverified. Current portal changes cannot be authenticated here. Round 1 comprises SOP, own indoor capture, reconstruction and free roaming. POIs/pathfinding belong to Round 2; AR is bonus. Old CURRENT_STATE.md incorrectly imports finale weights and Round 2 gaps into Round 1 readiness.

Existing work is reusable: static Three.js CAD viewer loads a 650,682-Gaussian binary PLY; local browser rendering was observed. Initial overview is fragmented and not demonstrably a photorealistic indoor walkthrough. Library code and all four manifest assets exist locally. Mesh/point-cloud fallback artifacts exist. No timed performance benchmark or fresh reconstruction has passed.

Critical defects: launcher kills arbitrary port-8080 process; pipeline paths depend on working directory, selects first rather than this run's config, exports without manifest registration, and suggests copying nonexistent .splat output. External absolute web-viewer symlink makes checkout nonportable. index.html/viewer.html are duplicated. Viewer labels uncalibrated reconstruction units as metres. Existing splat provenance says trained by a friend but source capture/checkpoint are absent from this workspace.

Data: input videos 1.mp4 (~773 MiB), 2.MOV (~391 MiB), your-video.mov (14,331,095 bytes; 36.7 s; H.264 1280x720/30 fps). 1-emergency has 252 posed frames; 2-run has 306; referenced RGB files all exist. Poses existing does not establish geometry quality. .work/2-run alone is ~102 GiB. Checkpoints exist at steps 2000, 2999, 6000, 8000 and 9999 for NeRF runs. Splatfacto configs are present but no corresponding local splat checkpoints found.

Environment: installed conda environment has torch 2.3.1, nerfstudio 1.1.5, gsplat 1.4.0 and numpy 2.2.6. CUDA and MPS both report false in this execution environment. Training is not authorized as a blind expensive experiment; preserve outputs and use CUDA only after capability checks. No new training started.

Legacy risk: many scripts delete training directories. extract-frames.sh writes empty poses with invented intrinsics before COLMAP. train_gpu_viewer_working.py actually selects nerfacto, disables viewer, deletes its output, and still advertises a viewer URL. Legacy scripts are evidence/history, not supported reproduction entry points.

No mandatory abstract PDF, master links document, demo video, deployed URL or real sample data under a test directory was found initially. Old README claims 60 fps, reliable MPS splatting and MIT project licensing without sufficient evidence.

## Preservation and structural decision

Preserve pre-existing dirty Git state (git-status-before.txt), every dataset/checkpoint/model and experiment. Back up edited small source files in ignored .local-backups/2026-10-24. Move supported static app code into apps/viewer, retain compatibility aliases from old export routes. Keep heavy artifacts in place; exports/models remains the stable alias. Snapshot external React source into experiments/legacy-react-viewer without altering the external original. Archive older planning documents under docs/history; rewrite local Markdown links. Keep historical training scripts in place and mark unsafe scripts clearly instead of moving cwd-dependent scripts. New test/ contains an actual existing source clip, with provenance and hashes, not synthetic captures.

## Initial requirement assessment

See REQUIREMENTS.md for evidence-backed current statuses and PLAN.md for prioritized closure. This initial assessment precedes code changes; final verification is recorded separately in VERIFICATION.md.

## Updated hardware finding

The initial sandbox GPU result was misleading. Outside the sandbox, torch reports MPS built/available true and a one-element MPS tensor allocation succeeds; system_profiler identifies Apple M5 Max with 32 GPU cores. A new, isolated 10-step torch Nerfacto test completed on MPS and saved a step-9 checkpoint. Installed Splatfacto still calls CUDA gsplat rasterization; no Metal Gaussian training was established. Initial no-MPS observation is superseded by this direct allocation/training evidence.

Owner supplied Team ID TM-C2093A5006E and requested publishing changes to https://github.com/BENi-Aditya/Namma-Space. Its main HEAD matches the starting local commit 2c97f21. Owner prefers Mac-only training for now; no friend's GPU access is needed for the current plan.

## Capture spot-check finding

Representative frame at 8 seconds in your-video.mov shows a laptop on a tabletop. At 10 seconds, 2.MOV shows a laptop/bench outdoors, while 1.mp4 shows an indoor wall/ceiling. These spot checks are not a full content review, but the baseline sample and outdoor run must not be described as a verified indoor room reconstruction. This makes capture suitability a P0 issue: select a connected own-room capture with textured corners/furniture and verify coverage before longer training.
