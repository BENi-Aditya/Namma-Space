# Technical Decisions Log
**Project:** Namma Space — 3D Indoor Navigation System  
**Competition:** IIT Bombay Techfest 2026-27

---

## Decision Format

Each decision follows this structure:

```markdown
## [DATE] — Decision Title

**Context:** What situation led to this decision?
**Decision:** What did we decide to do?
**Rationale:** Why did we choose this approach?
**Alternatives Considered:** What other options were evaluated?
**Trade-offs:** What are we gaining/losing?
**Status:** ACTIVE | SUPERSEDED | EXPERIMENT
**Validation:** How will we verify this was the right choice?
```

---

## [2026-09-29] — Architecture Freeze: Separate Visual and Spatial Truth

**Context:** Phase 0 audit revealed that the current architecture treats Gaussian Splatting as the complete solution. The competition requires POI search and collision-free pathfinding, which Gaussian Splats cannot provide.

**Decision:** Adopt a layered architecture with three independent truth representations:
1. **Visual Truth** — Gaussian Splat (.splat file) for photorealism
2. **Spatial Truth** — Occupancy grid + navigation mesh for pathfinding
3. **Semantic Truth** — POI database for search

**Rationale:**
- Gaussian Splats excel at rendering, fail at spatial queries ("Is this point walkable?")
- Industry standard (ROS navigation, Unity NavMesh) separates rendering from navigation
- Competition rubric explicitly tests spatial search (20%) and path calculation (20%)
- Judge will ask: "How do you guarantee the path doesn't hit furniture?" — need obstacle representation

**Alternatives Considered:**
1. **Query splat density for collision detection** — Rejected: splats don't represent physical occupancy
2. **Build everything from scratch** — Rejected: 3 weeks to deadline, high risk
3. **Use only COLMAP geometry** — Rejected: COLMAP already failed (2/810 frames)

**Trade-offs:**
- **Gain:** Robust spatial intelligence, defensible in Q&A, matches competition rubric
- **Lose:** More complex pipeline, must maintain two representations (visual + spatial)

**Status:** ACTIVE (frozen in ARCHITECTURE.md v1.0)

**Validation:**
- [ ] Can answer judge question: "Where is Meeting Room 4?" (semantic)
- [ ] Can answer judge question: "Calculate collision-free route" (spatial)
- [ ] Can explain: "Splat is visual skin, occupancy grid is spatial skeleton"

---

## [2026-09-29] — Use ARKit as Primary Pose Source, COLMAP as Secondary

**Context:** COLMAP documented failure: 2/810 frames registered on competition test video. Competition explicitly states Round 3 will involve "completely new IIT Bombay venue" with on-site reconstruction.

**Decision:** Implement layered pose estimation:
- **Primary:** ARKit camera tracking (real-time, continuous)
- **Secondary:** COLMAP (refinement, fallback, quality validation)
- **Depth:** LiDAR sensor data (iPhone 15 Pro)

**Rationale:**
- ARKit provides continuous pose even in low-texture environments (long corridors, plain walls)
- iPhone 15 Pro already captures ARKit poses — not using them is waste
- COLMAP remains valuable for refinement and loop closure detection
- Reduces single point of failure risk

**Alternatives Considered:**
1. **Fix COLMAP parameters** — Rejected: already tried (reduced frames, sequential matching), still fragile
2. **Use only ARKit** — Rejected: ARKit drift accumulates over time, need COLMAP refinement
3. **Switch to ORB-SLAM** — Rejected: integration effort too high, 3 weeks to deadline

**Trade-offs:**
- **Gain:** Robust pose estimation, higher registration success rate, competition-ready
- **Lose:** More complex pipeline, must fuse two pose sources

**Status:** ACTIVE (deferred to Phase 2: Reliable Pose Pipeline)

**Validation:**
- [ ] Registration success rate ≥80% on new venues
- [ ] Pose continuity: no jumps >0.5m between consecutive frames
- [ ] Can reconstruct long corridors (low-texture test case)

---

## [2026-09-29] — Use Existing Libraries (RBush, Fuse.js, Yuka) Over Custom

**Context:** `web-viewer/package.json` already lists:
- `rbush@4.0.1` — R-tree spatial indexing
- `fuse.js@7.0.0` — Fuzzy search
- `yuka@0.8.1` — Navigation mesh + A* pathfinding

But none are used in current implementation.

**Decision:** Use these existing libraries for spatial intelligence rather than building custom implementations.

**Rationale:**
- **Time constraint:** 3 weeks to Round 1 submission (Oct 31, 2026)
- **Risk reduction:** Well-tested libraries vs untested custom code
- **Performance:** RBush R-tree is O(log n) for spatial queries
- **Maintainability:** Standard libraries have documentation and community support

**Alternatives Considered:**
1. **Custom A* implementation** — Rejected: Yuka already provides this + NavMesh
2. **Three.js Raycaster for collision** — Rejected: too slow for pathfinding, no graph structure
3. **Server-side pathfinding** — Rejected: adds latency, complicates deployment

**Trade-offs:**
- **Gain:** Fast implementation, low risk, proven performance
- **Lose:** Less control over algorithms, library size (Yuka is ~100KB)

**Status:** ACTIVE

**Validation:**
- [ ] POI search returns results in <500ms (Fuse.js)
- [ ] Spatial queries <100ms (RBush)
- [ ] Path calculation <200ms for typical room (Yuka A*)

---

## [2026-09-29] — Defer AR Navigation to Post-Round 1

**Context:** Competition rubric:
- **Required:** Desktop web navigation (20% of Round 3 score)
- **Bonus:** AR navigation (10% bonus)

Current status: Desktop viewer works (WASD controls), AR not started.

**Decision:** Focus all effort on desktop navigation for Round 1. Defer AR to Round 2/3 preparation phase.

**Rationale:**
- Desktop navigation is **required** and worth 2× the points of AR
- AR requires phone localization (scan-to-model alignment) — complex, high-risk
- Desktop demo works in browser immediately, no iPhone needed for judges
- Can demo full system (search, pathfinding) on desktop first
- AR can reuse spatial truth layer (occupancy grid, POI database) once built

**Alternatives Considered:**
1. **Build AR first, desktop later** — Rejected: backwards, riskier
2. **Build both in parallel** — Rejected: not enough time, would compromise both

**Trade-offs:**
- **Gain:** Higher quality desktop navigation, lower risk, meets requirements
- **Lose:** No AR demo for Round 1 (but it's optional)

**Status:** ACTIVE

**Validation:**
- [ ] Desktop navigation complete and polished by Oct 31, 2026
- [ ] Can add AR in Phase 7 (post-Round 1) reusing spatial layer

---

## [2026-09-29] — Create `experiments/spatial-engine-v2/` for New Architecture

**Context:** Current `web-viewer/` is a working Gaussian Splat viewer. ROUND-1.md Rule 2: "Don't destroy the working pipeline."

**Decision:** Build spatial intelligence layer in separate `experiments/spatial-engine-v2/` directory. Preserve `web-viewer/` as-is until new version proven.

**Rationale:**
- Current viewer is the only working demo — cannot risk breaking it
- Allows A/B comparison (old vs new architecture)
- Can fall back to working viewer if new approach fails
- Clean separation for code review and judging

**Directory Structure:**
```
experiments/spatial-engine-v2/
├── capture/           # ARKit extraction scripts
├── reconstruction/    # Hybrid pose pipeline
├── spatial-truth/     # Occupancy grid generation
├── navigation/        # A* + NavMesh integration
└── docs/              # Experiment logs
```

**Alternatives Considered:**
1. **Modify `web-viewer/` directly** — Rejected: too risky, violates Rule 2
2. **Create new top-level directory** — Rejected: `experiments/` keeps it organized
3. **Branch in git** — Rejected: still need file separation, not just git branching

**Trade-offs:**
- **Gain:** Safe experimentation, can revert easily, clear comparison
- **Lose:** Some code duplication initially

**Status:** ACTIVE

**Validation:**
- [x] Directory created: `experiments/spatial-engine-v2/`
- [ ] New viewer surpasses old in functionality by end of Phase 4

---

## [2026-09-29] — Measurable Capture SOP Over Subjective Guidelines

**Context:** Current `docs/capture_sop.md` says:
- "Walk slowly (1-2 sec/step)"
- "Good lighting"
- "70-80% overlap"

But no way to verify these were achieved.

**Decision:** Define measurable capture acceptance criteria:
1. Frame extraction: 250-400 frames
2. Frame overlap: ≥60% consecutive overlap (measurable via feature matching)
3. Pose continuity: <0.5m jumps between frames
4. Depth coverage: ≥80% frames have valid LiDAR depth
5. Tracking confidence: ARKit "high" or "medium" on ≥90% frames

**Rationale:**
- Competition requires "repeat reliably on new venue" — need quantitative validation
- Judge will ask: "How do you know your capture is sufficient?"
- Automated quality checks catch bad captures before wasting training time
- ROUND-1.md Rule 5: "No vague conclusions without evidence"

**Alternatives Considered:**
1. **Keep subjective SOP** — Rejected: not defensible in technical Q&A
2. **Use training quality as proxy** — Rejected: training takes 1 hour, want fast validation

**Trade-offs:**
- **Gain:** Measurable, automatable, repeatable, defensible
- **Lose:** Must implement quality validation scripts

**Status:** ACTIVE (implementation in Phase 1)

**Validation:**
- [ ] Quality check script runs in <1 minute
- [ ] Can reject bad captures before training
- [ ] Can explain metrics to judge in Q&A

---

## [2026-09-29] — Fix Immediate Web Viewer Blocker: Deploy .splat File

**Context:** Phase 0 audit found:
- Web viewer code works (React + Three.js functional)
- But `web-viewer/public/models/demo.splat` does not exist
- Viewer hardcodes this path and will fail to load

This is the **highest priority blocker** for Round 1 demo.

**Decision:** Phase 1 first task is to export .splat file from existing trained model and deploy to web viewer.

**Rationale:**
- Trained models exist in `namma-space-project/output-models/`
- Nerfstudio has .splat export capability
- This unblocks end-to-end testing of current pipeline
- Allows demo video recording to proceed

**Alternatives Considered:**
1. **Train new model first** — Rejected: existing model should work, why waste 1 hour?
2. **Use .ply viewer instead** — Rejected: already committed to .splat + Three.js

**Trade-offs:**
- **Gain:** Working demo immediately, can record video, validates pipeline
- **Lose:** None — this is pure unblocking

**Status:** ACTIVE (next immediate action)

**Validation:**
- [ ] `web-viewer/public/models/demo.splat` exists and loads
- [ ] Can navigate scene with WASD controls
- [ ] Frame rate ≥30 FPS on MacBook Pro M5 Max

---

---

## [2026-09-29] — iPhone LiDAR Integration Strategy: Multi-Pronged Approach

**Context:** Existing videos (1.mp4, your-video.mov) were captured with standard Camera app and contain no ARKit metadata. Need to integrate iPhone 15 Pro LiDAR per ARCHITECTURE.md Layer 1 requirements.

**Decision:** Implement three parallel tracks:

1. **Short-term:** Enhanced COLMAP pipeline for existing videos
   - Sequential matching (not exhaustive) 
   - Higher feature density (8192 vs 4096)
   - GPU acceleration
   - Target: ≥80% registration rate (vs current 0.25%)

2. **Medium-term:** Record3D app for new captures
   - Off-the-shelf iOS app with ARKit + LiDAR export
   - Exports .r3d files with synchronized RGB + poses + depth
   - Build `r3d_to_nerfstudio.py` parser
   - No custom iOS development required

3. **Long-term:** Custom iOS app if needed
   - Only if Record3D has limitations
   - Deferred until Round 2

**Rationale:**
- Cannot extract ARKit data from existing videos (wasn't recorded)
- Enhanced COLMAP fixes immediate blocker without new captures
- Record3D provides proper ARKit integration without Swift development
- Progressive approach reduces risk, each track has value independently
- Can test hybrid fusion once both COLMAP and ARKit poses available

**Alternatives Considered:**
1. **Build custom iOS app first** — Rejected: high effort, delays testing
2. **Wait for new ARKit captures only** — Rejected: wastes existing video data
3. **Only use COLMAP** — Rejected: documented fragility, doesn't meet architecture goal
4. **Try to extract IMU data from video metadata** — Rejected: insufficient for pose reconstruction

**Trade-offs:**
- **Gain:** Pragmatic solution, unblocks work immediately, meets architecture eventually
- **Lose:** Some complexity maintaining two capture methods during transition

**Status:** ACTIVE (implementation started 2026-09-29)

**Validation:**
- [x] Experiment log created with findings
- [x] Enhanced COLMAP pipeline implemented (`enhanced_colmap_pipeline.py`)
- [x] Record3D capture protocol documented
- [x] R3D parser implemented (`r3d_to_nerfstudio.py`)
- [ ] Enhanced COLMAP tested on your-video.mov (target ≥80% registration)
- [ ] Record3D capture test (need to capture sample .r3d file)
- [ ] Comparison: COLMAP vs ARKit pose quality

**Files Created:**
- `experiments/spatial-engine-v2/docs/experiments.log` — Experiment tracking
- `experiments/spatial-engine-v2/docs/RECORD3D_CAPTURE.md` — Capture protocol
- `experiments/spatial-engine-v2/capture/enhanced_colmap_pipeline.py` — Improved COLMAP
- `experiments/spatial-engine-v2/capture/r3d_to_nerfstudio.py` — R3D parser
- `experiments/spatial-engine-v2/test-runs/test_enhanced_colmap.sh` — Test script

---

## Template for Future Decisions

## [YYYY-MM-DD] — Decision Title

**Context:**

**Decision:**

**Rationale:**

**Alternatives Considered:**

**Trade-offs:**

**Status:** ACTIVE | SUPERSEDED | EXPERIMENT

**Validation:**

---

**Last Updated:** 2026-09-29 20:10 UTC  
**Next Review:** After enhanced COLMAP test results, or Record3D test capture
