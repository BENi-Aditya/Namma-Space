# Deadline-aware execution plan

Planning date: 24 October 2026, Asia/Kolkata. Official date: 31 October 2026; hour/timezone unknown. Internal target: finish upload and signed-out verification by 30 October, leaving 31 October for recovery. This is an engineering schedule, not a guarantee of qualification.

| Tier / task | Definition of done | Dependencies | Effort | Verification / target |
|---|---|---|---|---|
| P0 - verify deadline, eligibility and account | Portal date/cutoff, roster, student eligibility, Team ID confirmed | Owner portal | 15-30 min | Portal evidence; 24 Oct |
| P0 - capture suitability and export provenance | Own indoor-room capture selected and coverage checked; exact source/config/checkpoint/contributor identified, or replace external model with own traceable reconstruction | Owner/friend files | 30-90 min | Hash-linked run record; 24-25 Oct |
| P0 - preserve data and isolate supported source | Backups, mapping, canonical static viewer and relative compatibility links | Local files | Completed this turn | Audit inventory + source checks |
| P0 - local GPU compatibility | MPS allocation and bounded NeRF training save checkpoint | Existing conda environment | Completed 10-step smoke | Log + step-9 checkpoint; no quality claim |
| P1 - one reliable room | Fresh own capture has continuous poses and an export showing recognizable room structure; archive exact commands, env and hashes | SOP, Mac, source capture | 2-4 h human + measured compute | Check pose coverage and side-by-side input/export; 25-26 Oct |
| P1 - complete supported pipeline | Video -> poses -> train -> export -> manifest -> browser succeeds for one new ID | Previous item | 1-3 h + compute | Real run.json and replayable commands; 26 Oct |
| P1 - walkthrough acceptance | Usable indoor starting viewpoint, WASD/mouse look/Esc/reset, fallback and errors validated in ordinary desktop browser | Model and browser | 1-2 h | Sustained walkthrough recorded; 26 Oct |
| P1 - clean clone and assets | Source clone + documented model/sample distribution runs on second machine | GitHub auth; reviewed assets | 1-2 h | Fresh setup/asset checks and browser; 27 Oct |
| P1 - deploy | Signed-out HTTPS URL loads default and fallback assets on second network | Hosting account; cleared assets | 1-2 h + upload | Signed-out browser test; 27 Oct |
| P1 - final abstract/master doc | <=5-page abstract accurately reflects demonstrated system; all links live in organized master document | Verified results/URLs/credits | 1-2 h | Render PDF, count pages, click links; 28 Oct |
| P1 - video | 3-5 min narrative shows scope, actual SOP/capture and browser roaming | Stable demo, capture shots | 2-4 h | Playback duration and clarity; 28-29 Oct |
| P1 - final submission | Drive anyone-with-link access and portal receipt | Complete package; owner account | 30-60 min | Signed-out download, portal receipt; 30 Oct |
| P2 - improve model and UX | Fix the largest visible hole/floaters; set repeatable indoor start; measure load/frame time | P1 reliability | 2-6 h + trial compute | A/B screenshot and timed trial, no invented metrics |
| P2 - strengthen SOP evidence | Show path diagram, difficult surfaces and coverage failure/retry examples | Capture evidence | 1-2 h | Side-by-side capture/reconstruction explanation |
| P3 - extra models / advanced capture | Only when all mandatory gates pass | Time margin | Variable | Keep isolated; do not destabilize demo |

Do not spend Round 1 time implementing POIs, search, navmeshes, collision pathfinding or AR. These have later-round value, but no requirement in the Round 1 deliverable list.

## Smallest honest end-to-end demonstration

One permission-cleared indoor room, captured with a repeatable overlapping path and no manual 3D modelling. Show original video, sampled images/registered poses, actual reconstruction run/config and export, then a public zero-install viewer with a clear entry view, sustained WASD/mouse exploration, Escape and reset. The Mac NeRF point-cloud export is an honest fallback but may score poorly for photorealism; do not relabel it as a Gaussian reconstruction. Existing IMG_2008 can be used only after ownership/source/visual walkthrough are established.

## Mac training decision

MPS allocation and 10-step torch Nerfacto test pass. Installed Splatfacto/gsplat is CUDA-based. First measure a 200-500 step NeRF trial at low resolution with a separate ID, inspect quality and memory, then choose a bounded higher-resolution run. Increasing iterations cannot fix wrong poses or missing coverage. Compare actual reconstructed room detail rather than choosing the largest iteration count. Current tiny smoke timing cannot justify a full-training ETA. A new Metal Gaussian trainer would add installation/conversion risk and is deferred unless the NeRF fallback cannot meet quality needs and there is sufficient time. No cloud or friend's GPU job is scheduled; user prefers Mac-only now.

## External actions versus autonomous work

Owner: confirm registration/cutoff, clear source capture/audio for public sharing, identify IMG_2008 provenance/contributors, provide hosting/Drive access and record/narrate final demonstration or supply recordings. GitHub credentials may need normal sign-in. Local code fixes, artifact packaging, documentation/PDF preparation, source validation and safe tests are agent work. Keep raw captures and private identifiers out of public commits until reviewed; Team ID alone was explicitly supplied for competition use.
