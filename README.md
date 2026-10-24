# Namma Space

Smartphone captures to indoor 3D reconstruction and browser exploration, for IIT Bombay Techfest 2026-27. Team ID: **TM-C2093A5006E** (provided by team owner; portal registration not independently checked).

**Current state: local prototype, not submission-ready.** Existing splats and mesh/point-cloud outputs load locally. A bounded NeRF training test passed on this Mac's MPS GPU. A fresh complete capture-to-export run, convincing indoor reconstruction quality, public deployment, final video and portal submission remain outstanding. No measured FPS, metric scale, collision detection, POI search or AR capability is claimed.

## Training studio — one command

```bash
./start-admin.sh
```

Opens http://127.0.0.1:8080/admin automatically. This Mac's existing `namma-space` environment is detected without a separate activation command. Choose a name and training budget, then drop a video or select it and click **Upload & start training**. The studio runs frame extraction, COLMAP, pose validation, Mac NeRF training and point-cloud export. Jobs run one at a time. The page shows live logs, stages, measured training ETA, cancellation and persistent history. Keep the server running; closing its terminal stops active training.

The checked **Open live training** option reserves a browser tab during upload and navigates it to Nerfstudio when ready. Allow popups for localhost, or use **Open live Nerfstudio**. That viewer closes when training finishes so export can start. Exported scenes appear in the **Model library**; **Rename** persists their display name in `apps/viewer/models.json`, keeping stable asset IDs and checkpoint paths intact.

Preview / Balanced / Extended request 1,000 / 7,000 / 15,000 steps. These are compute budgets, not quality guarantees. Processing and export have no reliable ETA; the training estimate appears after measured steps. Failed/cancelled runs preserve input and partial outputs. Restarted incomplete runs are marked interrupted, never silently resumed. Previous checkpoint folders appear separately with honest checkpoint/export status.

Use `./start-admin.sh --port 8081` if the port is occupied. `NAMMA_PYTHON=/absolute/path/to/python ./start-admin.sh` selects another installed training environment. Inputs, jobs and logs stay under ignored `namma-space-project/.work/admin/`. This is a loopback-only local tool; deploy only the packaged static viewer publicly. See [studio guide](docs/TRAINING_STUDIO.md).

## Run the existing demo

Requires Python 3.10+ and a desktop WebGL2 browser. No npm install is needed for the supported static viewer.

```bash
./start-viewer.sh
# Open http://127.0.0.1:8080/
# If occupied, choose another port:
./start-viewer.sh --port 8081
```

Select a model, drag to orbit, use WASD to move, Space/E up and Q/C down. **Enter walkthrough** requests first-person mouse look; Escape releases it. Some embedded browsers block pointer lock: use an ordinary desktop browser, or the drag/WASD fallback. **Reset view** recovers the overview. **Editor** exposes the preserved alignment, crop and asset controls. Save Position & Lock stores camera, alignment, crop and display settings with the model in models.json. The same default opens through the local viewer or admin library and travels with the next static package. It is not a calibrated scene setup. Geometry is in uncalibrated model units. No obstacle avoidance is implemented.

Models are local generated artifacts, not normal Git source. The default IMG_2008 export is 161,370,667 bytes and contains 650,682 Gaussian vertices. The manifest lists four local scenes. A fresh clone lists only the older tracked models whose assets are present. Direct viewer links also handle missing preferred exports. For the Gaussian demo, restore the original artifacts under `namma-space-project/output-models/models/`; do not expect a Gaussian asset to arrive through Git. See [reproduction](docs/REPRODUCTION.md) and [asset provenance](test/README.md).

## Reconstruct

The supported entry point is dry-run by default and refuses existing run IDs:

```bash
conda activate namma-space
python scripts/pipeline/reconstruct.py test/data/tabletop-sample.mp4 room-new --method nerfacto --device mps --iterations 7000
# Review commands, available memory and intended compute budget; then add --execute.
```

This Mac supports MPS NeRF training. The installed Splatfacto/gsplat implementation uses CUDA kernels, so Gaussian training through that stack needs CUDA; passing mps does not convert it to Metal. The Mac route exports a colored point cloud from NeRF, which is a useful fallback but is not equivalent to a photorealistic NeRF renderer or a Gaussian export. Existing Gaussian exports can be viewed on the Mac without training. See [exact setup and limitations](docs/REPRODUCTION.md).

## Project map

```text
apps/viewer/             supported static app, manifest, vendored rendering libraries
scripts/pipeline/        supported reconstruct.py + process_video.sh wrapper; legacy exporters
scripts/serve_viewer.py  localhost preview; never kills another process
scripts/package_viewer.py standalone static deployment bundle
scripts/setup/          historical installers (review before running)
scripts/training/       historical presets; many delete outputs, not supported entry points
experiments/            preserved React/capture/spatial-engine experiments
namma-space-project/    original videos, .work datasets/checkpoints, output-models artifacts
exports/                relative alias to output-models (no duplicate heavy data)
data/                   relative aliases to original videos and processed data
models/                 compatibility alias to local generated model directory
web-viewer/             compatibility alias to apps/viewer
logs/                   local training logs
 test/                  regression tests, source sample, provenance and asset hashes
 docs/                  current capture SOP and reproduction guide
 docs/history/          dated prior plans and architecture, preserved with warnings
 docs/audit/2026-10-24/  evidence, requirements, mapping, execution plan and test results
 submission/round1/     abstract, organized master links document and demo storyboard
```

## Verify and package

```bash
python3 -m unittest discover -s test -v
python3 scripts/check_project.py
python3 scripts/package_viewer.py
# Deploy output/site to a static HTTPS host; no symlinks remain in that bundle.
```

The packaged viewer includes large generated assets and is ignored by Git. Hosting is not configured. Do not publish private captures or claim source ownership until provenance is confirmed. Rendering dependency licences are included in [third-party notices](apps/viewer/THIRD_PARTY_NOTICES.md); no project-wide MIT licence is asserted.

## Round 1 delivery

The [official brief](docs/competition_problem_statement.pdf), pages 3 and 5-6, specifies **31 October 2026**, with no published cutoff time/timezone in that document. Submit via the Techfest portal a Google Drive folder accessible to anyone with the link: technical abstract PDF (max 5 pages), organized viewer-link document, 3-5 minute demo video, code/setup instructions and sample data inside a test directory. POIs and desktop pathfinding are Round 2; AR is bonus. Prior plans incorrectly mixed these scopes.

Start with the [audit](docs/audit/2026-10-24/AUDIT.md), [requirement checklist](docs/audit/2026-10-24/REQUIREMENTS.md), [execution plan](docs/audit/2026-10-24/PLAN.md), and [verification record](docs/audit/2026-10-24/VERIFICATION.md). The PDFs in submission/round1 are review drafts until missing links, provenance and quality checks are resolved.

A small video-only diagnostic excerpt is included in Git at test/data/tabletop-sample.mp4. It is a tabletop object capture; obtain a proper indoor-room sample for the final reconstruction evidence. The full original remains local.
