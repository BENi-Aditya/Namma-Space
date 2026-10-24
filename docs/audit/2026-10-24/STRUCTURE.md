# Applied structure and mapping

The smallest cleanup separates runnable app source from heavy generated data. No dataset, checkpoint, raw capture, model or experiment was deleted. No history was discarded. Pre-existing Git changes are in git-status-before.txt and original small modified files were copied to ignored .local-backups/2026-10-24.

| Before | Now | Compatibility/dependency handling |
|---|---|---|
| output-models/index.html | apps/viewer/index.html | Old path is a relative symlink |
| output-models/viewer.html duplicate | apps/viewer/index.html | Old viewer.html and new apps/viewer/viewer.html alias the one implementation; original backed up |
| output-models/lib | apps/viewer/lib | Old path aliases canonical vendored runtime; notices added |
| output-models/models.json | apps/viewer/models.json | Old manifest path aliases canonical file, so legacy exporters see it |
| external absolute web-viewer symlink | web-viewer -> apps/viewer | Supported application is now in repository; external original untouched |
| external React sources | experiments/legacy-react-viewer | Snapshot excludes node_modules/dist/large model data; STATUS.md states missing assets and unverified build |
| ARCHITECTURE, CURRENT_STATE, DECISIONS, ROUND-1, Round-1-info, MODELS root docs | docs/history/same names | Markdown relative file links rewritten; dated warning added |
| inert root package-lock.json | docs/history/root-package-lock.json | Root is no longer mistaken for npm app |
| original models and .work data | unchanged physical paths | apps/viewer/models points to original artifacts; packaging dereferences symlinks |
| data/raw-videos, input-videos, processed; exports; models | retained aliases | Existing training paths preserved; no bulk migration of >100 GiB |
| legacy training and setup scripts | retained paths with central warnings | Moving cwd-dependent scripts would not improve reliability this week |
| new submission material | submission/round1 | Single package location; drafts clearly marked |
| new audit and readiness documents | docs/audit/2026-10-24 | Single evidence directory |

Paths that remain fragile in legacy code: hard-coded /Users/tripathd paths, root-relative .work, shell-installed conda assumptions and direct config edits. These are documented, not advertised as supported commands. No new code imports from those scripts. Current supported commands derive repository roots from __file__/BASH_SOURCE.

The .gitignore now covers local backups, credentials, generated models, temporary processing and host bundles; already-tracked artifacts remain tracked unless previously deleted by the owner. Large Gaussian PLY is not pushed through normal Git. The existing source tree has pre-existing deletions of old root mesh/model.obj and model.stl; these are not restored or described as our cleanup.
