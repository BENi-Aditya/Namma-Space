# Publish the local model library

Vercel publishes the static viewer after every push to `main` through its GitHub integration. GitHub Actions independently verifies the public build. The public build contains all manifest-listed exports and their saved camera, rotation, position, scale and crop. The training admin panel and source videos are not part of the hosted site.

## On this Mac

Publishing hooks are installed with `./setup-publishing.sh` (already run on this checkout). After training/exporting a new model or editing an existing one:

1. In the local viewer, press **Save Position & Lock**. Wait for **LOCKED // SAVED TO DISK**. Unsaved edits are intentionally not published.
2. Commit and push:

```bash
git add -A
git commit -m "Update model library"
git push origin main
```

The pre-commit hook automatically stages `apps/viewer/models.json` and snapshots every referenced model asset, including otherwise ignored new exports. It does not stage unrelated source edits. The hook needs Python 3.10+. If skipped, run `python3 scripts/release_assets.py snapshot --stage` before committing. A fresh clone needs `./setup-publishing.sh` once. Do not use `--no-verify` for model releases.

A commit alone is local. Push triggers the Vercel production deployment; the previous live version remains available until a deployment succeeds. Check the Vercel project Deployments tab for publication status; GitHub Actions reports independent build checks. The public `deployment.json` identifies the exact deployed commit and SHA-256 of every asset.

## What stays synchronized

- Model list/names and saved view settings are tracked in `apps/viewer/models.json`.
- Exported models are compressed into content-addressed parts (at most 40 MiB each) under `deployment/assets/`. This avoids putting a >100 MiB file into a single Git blob. Raw captures, checkpoints and training logs remain local.
- The deployment restores original files byte-for-byte and checks their SHA-256. Missing/corrupt assets stop the build instead of silently publishing an incomplete library.
- Changed asset and manifest URLs receive content versions so browsers request the new data.
- Public visitors load committed defaults, ignoring old browser-only alignment drafts. Owner editing/saving controls stay local. Camera navigation is still available publicly.

Public WebGL results use the same renderer, scene data and saved settings as local. Different viewport aspect ratios, screen sizes and graphics hardware can affect framing and performance; they do not change saved transforms/crop. The full Gaussian download is large, so the first load can take longer on slower connections.

## Fresh checkout or another computer

```bash
python3 scripts/release_assets.py restore
./setup-publishing.sh
./start-admin.sh
```

To preview the exact public build locally:

```bash
python3 scripts/package_viewer.py --output output/public-preview
python3 -m http.server 8090 --directory output/public-preview
```

Choose a new output folder if it already exists. The public package is read-only; use the normal local admin/viewer server to save defaults, then commit/push again.

## Storage limits

The initial four-model release is approximately 226 MiB unpacked and 172 MiB compressed. Versioned assets make each deployed commit reproducible, but repeated new reconstructions grow Git history. As the collection grows, monitor Vercel storage/bandwidth usage and move large asset archives to object storage if needed. Existing model parts are reused when only crop/camera settings change.
