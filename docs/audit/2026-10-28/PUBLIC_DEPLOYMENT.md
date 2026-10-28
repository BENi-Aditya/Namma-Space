# Public deployment verification — 28 October 2026 (India)

Production URL: https://namma-space-omega.vercel.app/
Provider: Vercel, existing Hobby workspace. Git repository: BENi-Aditya/Namma-Space. Production branch: main.

- Git push automatically created production deployment dpl_AKty5C91dd6pbEjtAnQhU2FQZgQW for commit 44b24ebae8c5adf6015f2e75f2b128395906f8bf. State READY; stable production alias assigned.
- Unauthenticated requests to models.json and deployment.json returned HTTP 200 without login or redirects.
- All four public model entries match local IDs and saved viewState values exactly.
- All ten unique exported assets are publicly available with expected Content-Length. The public deployment SHA-256 index matches the committed release asset index for every file.
- Release restoration into a separate local directory reproduced the original bytes, verified with SHA-256.
- 17 Python tests passed, as did viewer integrity/syntax and saved-view JavaScript checks. The cloud build ran its own integrity/saved-view checks.
- The local pre-commit hook ran successfully during deployment commits, capturing model exports and saved model settings. Unchanged parts were reused.
- Public build disables owner editing controls and browser-only saved-state fallback. It preserves the committed camera, crop, transform and asset selection.
- Initial GitHub Pages attempt was withdrawn in favor of Vercel at the user's request. No change was made to the separate personal site's custom-domain setting.

Commit/push again after Save Position & Lock or a completed new export. Vercel retains the last successful production release while the next commit builds. Scene appearance still depends on screen aspect ratio and graphics hardware; this deployment does not improve reconstruction quality or complete the remaining competition deliverables.
