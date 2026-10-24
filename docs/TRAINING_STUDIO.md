# Local training studio

Run `./start-admin.sh` from the repository. The page opens automatically at http://127.0.0.1:8080/admin. No per-video terminal commands are needed. Existing prerequisites must be installed; this Mac already has the reconstruction environment. Override its interpreter with NAMMA_PYTHON if necessary.

## Workflow

1. Record a slow, steady room walkthrough with overlapping views, well-lit textured surfaces, and movement between viewpoints. Avoid motion blur, pure rotation, mirrors and moving people. Capture the whole room from several positions.
2. Enter a model name and choose Preview, Balanced or Extended. Start with Preview to judge coverage before spending longer on a new video.
3. Drop the video to upload and start automatically, or use the chooser followed by Upload & start training. Multiple videos are queued in upload-completion order; only one training runs at a time.
4. Watch processing, training and export. The live terminal is preserved on disk. The training ETA is estimated from actual progress and excludes export; processing has no reliable ETA.
5. The optional live-viewer tab is reserved when you start upload to comply with browser popup restrictions. If blocked, click Open live Nerfstudio when available. Nerfstudio runs only during training and closes automatically before export.
6. When complete, Explore exported model opens that scene directly. Model library opens the gallery at any time. Rename updates the local manifest display name; stable IDs, filenames and checkpoint references stay intact.

## What the Mac creates

The installed Mac route uses Nerfacto with PyTorch on MPS. It exports a colored point cloud for the browser. It does not convert NeRF into Gaussian splats, and the point cloud will not reproduce the live NeRF image perfectly. More iterations cannot fix poor camera coverage. Current Gaussian exports remain viewable. A bounded 100-step live-viewer check and a 1,024-point export succeeded on this Mac; those checks are not final-scene quality evidence.

Workspace-relative paths avoid Nerfstudio's unquoted COLMAP commands failing on the space in this repository's parent folder.

The export wrapper initializes PyTorch before Open3D because the stock ns-export import order caused a native crash in the installed environment. It calls the same Nerfstudio exporter, with a smaller 2,048-ray export batch to limit memory use.

## Storage and recovery

Uploaded input, job JSON and logs: `namma-space-project/.work/admin/`. Processed data: `.work/capture-<id>/`; checkpoints: `.work/training-capture-<id>/`; exported assets: `apps/viewer/models/capture-<id>/` through the existing models alias. Existing runs are never overwritten. Only successful, validated exports enter the model manifest.

Cancel stops the job's process group, including COLMAP/trainer children, and preserves partial data. Closing the server also stops active compute; the pipeline watches its parent to stop if the server unexpectedly dies. After restart, unfinished jobs are marked interrupted. To try again, upload the video again; the new run receives a new ID. There is no checkpoint-resume button yet. Historical checkpoint discovery runs at server startup.

The application binds to 127.0.0.1, validates Host and requires a per-session token on mutations. Do not expose this local admin server to the internet. Static packages include the gallery and viewer, but not the admin UI or training backend. Renaming requires the local admin server; a deployed static gallery is read-only.

## Submission field

According to the supplied competition brief (pages 3 and 5), paste a **Google Drive folder link** into Enter submission link. Enable **Anyone with the link / Viewer** for the folder and its contents. Include:

- Technical abstract PDF, at most five pages.
- A document linking to the working public web viewer.
- A 3–5 minute demonstration video.
- Repository/code, reproduction/setup instructions and sample capture in the test directory.
- Consolidate additional links into one master PDF or Google Doc.

Use Team ID TM-C2093A5006E. Round 1 date: 31 October 2026; no cutoff timezone is specified in the supplied PDF. A localhost URL cannot be opened by judges. Record the better room video, train and visually review it, deploy the static viewer, replace draft placeholders and test every shared link in a signed-out browser before submission. Existing submission PDFs remain drafts.
