# Training studio verification — 24 October 2026

Implemented local loopback dashboard, persistent serial queue, streamed video uploads, logs, training step progress/ETA, cancellation, live Nerfstudio links/tab, imported checkpoint history, model gallery and persistent display-name editing. Static package includes gallery and viewer, excludes admin and backend.

## Passed

- 12 Python regression tests: local request protection, valid/invalid uploads, durable queued cancellation, rename persistence/stable paths, missing-asset readiness, pose validation, preservation of previous runs, failed-export protection and pipeline ordering with live viewer flags. API/pipeline integration fixtures use mocked compute; they do not prove reconstruction quality.
- Syntax/integrity check: four local models, eleven asset references, JS/Python/shell syntax and vendored imports.
- Real Mac MPS Nerfacto training: 100 iterations on the existing 20-frame reduced dataset. Live viser server bound 127.0.0.1:7017, progress emitted, checkpoint saved and trainer exited automatically. Average reported training iteration 0.1163 seconds on this tiny preset only; not a full-quality timing claim.
- Real export of that checkpoint: 1,024-point PLY, normal estimation and file write passed after initializing PyTorch before Open3D. Initial stock ns-export invocation crashed with signal 11; scripts/pipeline/export_model.py fixes the observed import-order issue and uses the same upstream entrypoint.
- Real browser upload of test/data/tabletop-sample.mp4: accepted, queued, frame extraction, COLMAP feature extraction and matching all passed. Cancel clicked in browser while reconstruction was running; dashboard recorded cancelled and process group stopped. This was intentionally stopped before full training.
- First browser upload exposed Nerfstudio unquoted COLMAP paths with spaces; relative workspace paths fixed it. The original failed diagnostic run remains in history with its log.
- Browser model gallery lists four available local exports; opening 1-emergency renders the existing geometry at the selected model URL. Screenshots saved alongside this record.
- Static artifact generated at output/studio-site-20261024 with ten unique referenced asset files (two manifest references share one file).

## Limits

No new full-resolution room capture has completed the entire upload-to-export path. The final room capture still needs reconstruction and visual review. The Mac route exports NeRF-derived point clouds, not Gaussian splats. No final scene quality, whole-pipeline ETA, or final competition readiness is claimed. Browser automatic-tab behavior also depends on popup permissions; a direct live-viewer button remains available.

The live dashboard is at http://127.0.0.1:8080/admin while its server runs. Run ./start-admin.sh to reopen it in future. Model names persist in the manifest without moving asset or checkpoint directories.
