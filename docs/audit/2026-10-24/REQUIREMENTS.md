# Round 1 requirements and submission checklist

Source of truth: docs/competition_problem_statement.pdf, page 3 (Round 1), page 5 (eligibility, licensing, organized links), page 6 (timeline). Status assessed 24 October 2026. The supplied brief confirms 31 October; no time/timezone is given. A public event listing corroborated the date, but the authenticated Techfest portal and email updates were not checked. https://unstop.com/competitions/namma-space-techfest-iit-bombay-1749529/amp . No criterion weights are given for Round 1; finale percentages must not be reused.

VERIFIED COMPLETE means evidence for that row only, not overall readiness. Estimates are focused working time; training/download/upload time is separate.

| Official requirement | Status | Evidence / remaining work | Priority; estimate; dependency | Risk if unfinished |
|---|---|---|---|---|
| Round 1 submission date | VERIFIED COMPLETE | PDF p6: 31 October 2026. Cutoff hour/timezone and changes still require portal check | P0; 15 min; portal access | Late entry |
| Registered team, student eligibility, <=4 members | NEEDS VERIFICATION | Owner provided Team ID TM-C2093A5006E; institutional IDs, roster and portal registration not independently inspected. Registration date in brief: 30 September | P0; 15-30 min; owner | Ineligible entry |
| Own accessible indoor capture following defined SOP | PARTIALLY COMPLETE | docs/capture_sop.md; three original videos. test/data/your-video.mov exists locally. IMG_2008 source capture/ownership unclear | P0; 1-2 h; owner/capture access | Cannot substantiate original dataset |
| SOP construction and pipeline design | PARTIALLY COMPLETE | Capture guide + supported reconstruct.py + reproduction guide; no fresh complete run. Existing poses: 252 and 306 frames with RGB references present | P1; 2-4 h + compute; approved capture | Pipeline soundness unproven |
| 3D model building | PARTIALLY COMPLETE | Binary PLY header confirms 650,682 Gaussian vertices; NeRF mesh/cloud outputs; browser rendering observed. Initial splat overview fragmented; no calibrated geometry or fidelity evaluation | P1; 3-6 h + training; capture/config | Weak visual-quality criterion |
| Fluid free-roaming WASD and mouse | PARTIALLY COMPLETE | WASD code, orbit rendering and first-person mouse handler present; model switching observed locally. Embedded browser rejects pointer lock; full desktop-browser test and sustained movement/performance still needed | P1; 1-2 h; desktop browser | Walkthrough may fail for judge |
| Technical abstract PDF, max 5 pages: architecture, pipeline, SOP, approach | PARTIALLY COMPLETE | submission/round1/Technical_Abstract_DRAFT.pdf generated as 4-page review draft, including credits/limitations; final evidence/provenance and URLs pending | P1; 1 h; quality review | Mandatory deliverable incomplete |
| POC + working web viewer link in a document | BLOCKED | Additional_Links_and_Prototypes_DRAFT.pdf organizes repo and missing viewer link. output/site is a local portable bundle; no public deployment URL supplied | P1; 1-2 h; hosting access/approved assets | Judges cannot open demo |
| 3-5 minute demonstration video: scope, capture, web walkthrough | NOT STARTED | Storyboard prepared; original source clips are not the required narrated demonstration | P1; 2-4 h; stable model/viewer, screen recording | Mandatory deliverable absent |
| Code repository/folder with reconstruction setup | PARTIALLY COMPLETE | Requested GitHub URL known; updated source and docs prepared, publication tracked in VERIFICATION. Clean setup and complete fresh reconstruction unverified | P1; 1-3 h; GitHub auth/environment | Judges cannot reproduce |
| Sample data inside test directory | PARTIALLY COMPLETE | Full 36.7 s source clip copied locally; an 8-second video-only, metadata-stripped tabletop excerpt is included in Git, hashes in test/assets.json. Final indoor-room sample/source relationship remains unverified | P1; 30-60 min; owner sample clearance | Submitted code package lacks sample |
| Single organized master PDF/Google Doc for additional links | PARTIALLY COMPLETE | Organized draft PDF includes repo, placeholder clearly marked missing for live viewer and optional supplemental URLs | P1; 20 min; final URL | Loose links not reviewed |
| Drive folder anyone-with-link viewable, submit folder URL via Techfest portal | BLOCKED | No connected Drive destination or portal submission evidence; final package not complete | P1; 30-60 min; owner account access | No valid submission |
| Originality, third-party licence compliance and abstract credits | PARTIALLY COMPLETE | Vendored MIT licence texts and THIRD_PARTY_NOTICES.md; abstract names external stack. Model contributor/ownership not confirmed | P0; 30-60 min; owner/friend | Attribution/ownership dispute |

Round 1 judging categories are SOP & Pipeline Soundness, Visual Quality & Model Fidelity, Web Viewer Performance, Documentation & Video Clarity (PDF p3). All remain NEEDS VERIFICATION as judging outcomes; do not attach invented scores or weights. POI tagging, search and obstacle-aware desktop pathfinding are explicitly Round 2. AR is bonus, not a Round 1 blocker.

## Final release gate

- [ ] Portal deadline/cutoff and Team ID confirmed by owner.
- [ ] Own source capture linked by hash to exact configuration and export; contributors credited.
- [ ] One room has recognizable walls/floor/objects and a usable starting viewpoint.
- [ ] Ordinary desktop browser: WASD, mouse look, Escape, reset, loading/error states pass.
- [ ] Real load time and frame-time observations recorded with browser/hardware/model size; no invented FPS.
- [ ] Final abstract <=5 pages; limitations and credits accurate.
- [ ] Working HTTPS viewer and public repository/code folder in master links document.
- [ ] Reviewed sample capture actually included inside submitted test/data.
- [ ] 3-5 minute narrated demonstration plays and shows capture plus browser walkthrough.
- [ ] Drive signed-out permissions checked; final folder URL submitted and receipt retained.

Do not describe the entry as submission-ready until these gates are complete.
