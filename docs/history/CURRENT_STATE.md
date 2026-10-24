> Historical document, archived 24 October 2026. Claims and commands may be outdated. See [current audit](../audit/2026-10-24/AUDIT.md) and [current setup](../REPRODUCTION.md).

# Current State Assessment — Phase 0 Audit
**Date:** 2026-09-29  
**Project:** Namma Space — 3D Indoor Navigation System  
**Competition:** IIT Bombay Techfest 2026-27

---

## Executive Summary

The repository contains a **partially working** Gaussian Splatting visualization pipeline but **lacks the spatial intelligence layer** required for the competition. The current architecture is:

```
iPhone video → COLMAP → Gaussian Splatting → Three.js viewer
```

The competition requires:

```
Capture → Reconstruction → Visual+Spatial → Search+Navigation → Web/AR
```

**Critical Gap:** No spatial truth representation, no POI system, no pathfinding, no occupancy grid.

---

## 1. Reconstruction Pipeline

### Status: 🟡 PARTIALLY WORKING

**What Works:**
- ✅ COLMAP integration via Nerfstudio (`ns-process-data video`)
- ✅ Splatfacto training (Gaussian Splatting method)
- ✅ MPS GPU acceleration on M5 Max
- ✅ Export pipeline to .splat, .ply, .obj, .stl formats

**What's Broken/Experimental:**
- 🔴 **COLMAP reliability is the single point of failure**
  - Previous run: 2/810 frames registered (documented failure)
  - Current workaround: reduced to ~300 frames, sequential matching
  - No fallback or verification mechanism
- 🔴 **No ARKit/LiDAR pose pipeline** despite iPhone 15 Pro capability
- 🟡 Training scripts are scattered and inconsistent (7 different training runs in `.work/`)
- 🟡 No automated quality validation or acceptance criteria

**Key Files:**
- [`scripts/pipeline/process_video.sh`](../../scripts/pipeline/process_video.sh) — Main automation (COLMAP + Splatfacto)
- [`scripts/training/train_gpu_viewer_working.py`](../../scripts/training/train_gpu_viewer_working.py) — GPU training with live viewer
- [`scripts/training/train_ultimate_gpu_fast.py`](../../scripts/training/train_ultimate_gpu_fast.py) — Fast training variant
- [`scripts/pipeline/export_pipeline.py`](../../scripts/pipeline/export_pipeline.py) — Multi-format exporter

**Evidence of Past Training Runs:**
```
namma-space-project/.work/
├── 1-competition/          (COLMAP database exists)
├── 1-emergency/            (COLMAP database exists, transforms.json: 148KB)
├── 1-splat-competition/    (COLMAP database exists)
├── training-fast/
├── training-final/
├── training-final-gpu-viewer/
└── training-your-video/
```

**Latest Training Log:**
- Training was running (12-13% complete, ~1270-1300 iterations)
- GPU utilization: 6.7-7.2K rays/sec
- Viewer running at `http://localhost:7007`
- No completion timestamp — training appears interrupted

---

## 2. Web Viewer

### Status: 🟢 WORKING (but minimal)

**What Works:**
- ✅ React 18 + Vite + Three.js stack
- ✅ `@mkkellogg/gaussian-splats-3d` library integration
- ✅ First-person WASD + pointer lock controls
- ✅ Smooth camera movement with damping
- ✅ Loading states and error handling
- ✅ Dev-mode performance stats (FPS counter)

**Architecture:**
- [`web-viewer/src/App.jsx`](../../apps/viewer/src/App.jsx) — Top-level app (18 lines, clean)
- [`web-viewer/src/components/Scene.jsx`](../../apps/viewer/src/components/Scene.jsx) — Canvas + lighting setup
- [`web-viewer/src/components/GaussianSplat.jsx`](../../apps/viewer/src/components/GaussianSplat.jsx) — Splat loader (hardcoded to `/models/demo.splat`)
- [`web-viewer/src/components/Controls.jsx`](../../apps/viewer/src/components/Controls.jsx) — WASD + Space/Shift vertical movement
- [`web-viewer/src/components/Instructions.jsx`](../../apps/viewer/src/components/Instructions.jsx) — UI overlay

**Key Configuration:**
- Camera: `position: [0, 1.6, 5]`, `fov: 75`
- Speed: `5.0 units/sec`
- Damping: `0.9`
- Viewer settings: `integerBasedSort`, `halfPrecisionCovariancesOnGPU`, `antialiased`

**Dependencies (Round 2 Ready):**
```json
{
  "@mkkellogg/gaussian-splats-3d": "^0.5.0",
  "rbush": "^4.0.1",           // R-tree for spatial indexing ✅
  "fuse.js": "^7.0.0",         // Fuzzy search ✅
  "yuka": "^0.8.1"             // Pathfinding / NavMesh ✅
}
```

**What's Missing (Competition Critical):**
- 🔴 No search bar UI
- 🔴 No POI display or markers
- 🔴 No navigation path rendering
- 🔴 No minimap or floor plan overlay
- 🔴 No spatial indexing implementation (RBush installed but unused)
- 🔴 No semantic search (Fuse.js installed but unused)
- 🔴 No A* pathfinding (Yuka installed but unused)
- 🔴 **Hardcoded model path** — `/models/demo.splat` does not exist

**Critical Issue:**
```bash
$ ls web-viewer/public/models/
# Empty — no .splat file deployed to viewer
```

---

## 3. Data & Artifacts

### Status: 🟡 PARTIALLY COMPLETE

**Input Videos:**
```
data/raw-videos/
├── 1.mp4          (772.7 MB)
├── your-video.mov (13.7 MB)
└── .gitkeep
```

**Processed COLMAP Data:**
- ✅ 3 COLMAP databases found
- ✅ `transforms.json` exists (148KB in `1-emergency/`)
- ✅ Camera poses extracted

**Exported Models:**
```
namma-space-project/output-models/
├── mesh/
│   ├── model.obj       (10.5 MB)
│   ├── model.stl       (2.7 MB)
│   └── model_mesh.ply  (5.5 MB)
├── pointcloud/
│   └── point_cloud.ply (2.6 MB)
└── viewer.html         (59.5 KB — Nerfstudio viewer)
```

**What's Missing:**
- 🔴 **No .splat files found in the repository**
- 🔴 No symlink between `exports/` and web viewer
- 🔴 No depth maps extracted
- 🔴 No occupancy grid / navigation mesh
- 🔴 No POI database

---

## 4. Documentation

### Status: 🟢 COMPREHENSIVE (but outdated)

**Existing Documentation:**
1. ✅ [`README.md`](../../README.md) — Project overview, tech stack, quick start
2. ✅ [`docs/quickstart.md`](../quickstart.md) — 5-minute setup guide
3. ✅ [`docs/capture_sop.md`](../capture_sop.md) — iPhone capture protocol ("Spiral Scan" method)
4. ✅ [`docs/how_it_works.md`](../how_it_works.md) — COLMAP + Gaussian Splatting architecture
5. ✅ [`docs/training_options.md`](../training_options.md) — Hyperparameter reference
6. ✅ [`docs/troubleshooting.md`](../troubleshooting.md) — Error resolution guide
7. ✅ [`docs/competition_guide.md`](../competition_guide.md) — Competition roadmap
8. ✅ [`docs/project_context.md`](../project_context.md) — Development history
9. ✅ [`docs/competition_problem_statement.pdf`](../competition_problem_statement.pdf) — Official rules

**Capture SOP Details:**
- "Spiral Scan" method: eye level → low level → high level passes
- 4K @ 30fps recommended
- 1-2 sec/step movement speed
- 70-80% frame overlap target
- 🟡 **Not measurable or testable** — no quality metrics, no coverage validation

**What's Missing:**
- 🔴 `ARCHITECTURE.md` (frozen architecture document)
- 🔴 `PIPELINE.md` (end-to-end pipeline specification)
- 🔴 `DECISIONS.md` (technical decision log)
- 🔴 `REPRODUCTION.md` (exact reproduction instructions)
- 🔴 `EXPERIMENTS.md` (experiment tracking log)

---

## 5. Setup & Environment

### Status: 🟢 WORKING

**Conda Environment:**
- Name: `namma-space`
- Base: Nerfstudio + dependencies
- GPU: MPS (Apple Silicon M5 Max)
- PyTorch: MPS backend enabled

**Setup Scripts:**
- [`scripts/setup/setup.sh`](../../scripts/setup/setup.sh) — Standard setup
- [`scripts/setup/setup-fixed.sh`](../../scripts/setup/setup-fixed.sh) — M5 Max optimized
- [`scripts/setup/preflight-check.sh`](../../scripts/setup/preflight-check.sh) — Hardware diagnostics
- [`scripts/setup/clean-install.sh`](../../scripts/setup/clean-install.sh) — Clean reinstall

**Hardware:**
- MacBook Pro M5 Max (36GB unified memory)
- iPhone 15 Pro (LiDAR + ARKit)

---

## 6. Critical Findings

### 🔴 **Single Point of Failure: COLMAP**

The documented 2/810 frame registration failure proves the current pipeline is **not robust**. The competition explicitly states:

> "Round 3: You'll be assigned a completely new IIT Bombay venue, collect data according to your SOP, reconstruct it, annotate POIs and deploy the platform on-site."

**Current risk:** The system might completely fail on a new venue.

**Mitigation:** Must implement layered pose estimation (ARKit primary, COLMAP secondary).

### 🔴 **No Spatial Intelligence Layer**

The current architecture treats Gaussian Splatting as the complete solution. But:

- **Gaussian Splats answer:** "What does this place look like?"
- **Spatial truth answers:** "Where can I walk? Where is Meeting Room 4?"

**Competition judges will ask:**
1. "Can I search 'Meeting Room 4'?" — ❌ No POI system
2. "Can you calculate a collision-free route?" — ❌ No pathfinding
3. "How do you guarantee the path doesn't hit furniture?" — ❌ No obstacle representation

### 🔴 **Round 1 Submission Not Ready**

**Required for Oct 31, 2026:**
- Technical Abstract PDF (≤5 pages)
- Working web viewer link
- 3-5 min demo video
- Code repo + sample data + setup instructions

**Current blockers:**
1. No .splat file deployed to web viewer
2. Web viewer references non-existent `/models/demo.splat`
3. No end-to-end reproduction instructions
4. No measurable capture quality validation

---

## 7. What Works vs. What Doesn't

| Component | Status | Notes |
|-----------|--------|-------|
| iPhone capture | 🟢 WORKING | SOP exists, 2 videos captured |
| COLMAP pose estimation | 🔴 FRAGILE | 2/810 failure documented |
| Splatfacto training | 🟢 WORKING | MPS GPU acceleration confirmed |
| Model export (.ply, .obj, .stl) | 🟢 WORKING | Multiple formats available |
| .splat export | 🔴 MISSING | No .splat files found |
| Web viewer code | 🟢 WORKING | React + Three.js functional |
| Web viewer deployment | 🔴 BROKEN | No model file to load |
| WASD controls | 🟢 WORKING | Smooth first-person navigation |
| POI system | 🔴 NOT STARTED | No database, no UI, no search |
| Spatial search | 🔴 NOT STARTED | Fuse.js installed but unused |
| Pathfinding | 🔴 NOT STARTED | Yuka installed but unused |
| Occupancy grid | 🔴 NOT STARTED | No geometry extraction |
| Navigation mesh | 🔴 NOT STARTED | No mesh generation |
| ARKit/LiDAR capture | 🔴 NOT STARTED | iPhone capable but unused |
| Capture quality validation | 🔴 MISSING | No metrics, no automation |
| Documentation | 🟢 COMPREHENSIVE | 9 docs, but missing architecture freeze |

---

## 8. Repository Organization Assessment

**Well-Organized:**
- ✅ Clear directory structure (`scripts/`, `web-viewer/`, `docs/`, `data/`)
- ✅ Separation of concerns (setup, pipeline, training, testing)
- ✅ Comprehensive README with tech stack table

**Needs Improvement:**
- 🟡 Multiple scattered training runs (7 dirs in `.work/`)
- 🟡 No clear "current working" vs "experimental" markers
- 🟡 `exports/` symlink unclear (points to `namma-space-project/output-models/`)
- 🟡 No experiment tracking log

---

## 9. Round 1 Readiness Score

| Criterion | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Capture | 20% | 15% | SOP exists, but not measurable |
| Reconstruction | 20% | 12% | Works but COLMAP fragile |
| Web Viewer UX | 20% | 8% | Code works, but no deployed model |
| Spatial Search & Path | 20% | 0% | Not started |
| Technical Abstract | 20% | 5% | Material exists, needs synthesis |
| **TOTAL** | **100%** | **40%** | **Not submission-ready** |

**Estimated work to Round 1 submission:** 3-4 weeks of focused effort.

---

## 10. Recommended Immediate Actions

### Phase 1 (Week 1): Fix the Working Pipeline
1. **Export .splat file** from existing trained model
2. **Deploy to web viewer** — make demo actually work
3. **Document exact reproduction** — REPRODUCTION.md
4. **Validate end-to-end** — fresh video → deployed viewer

### Phase 2 (Week 2): Capture Robustness
1. **Extract ARKit poses** from iPhone 15 Pro video
2. **Compare COLMAP vs ARKit** pose quality
3. **Implement hybrid approach** (ARKit primary, COLMAP refinement)
4. **Create measurable SOP** — coverage %, pose continuity, tracking confidence

### Phase 3 (Week 3): Spatial Engine Foundation
1. **Generate occupancy grid** from depth/geometry
2. **Extract floor plan** and walkable regions
3. **Implement obstacle inflation** (human clearance radius)
4. **Build navigation graph** for A*

### Phase 4 (Week 4): Round 1 Deliverables
1. **Create POI database** schema and mock data
2. **Build search UI** (text input → spatial lookup)
3. **Render navigation paths** in Three.js
4. **Record demo video** — capture → reconstruction → navigation
5. **Write Technical Abstract** — 5 pages max

---

## Appendix: Key File Inventory

### Reconstruction Pipeline
- `scripts/pipeline/process_video.sh` (100 lines)
- `scripts/pipeline/export_pipeline.py`
- `scripts/training/train_gpu_viewer_working.py` (100+ lines, Nerfacto)
- `scripts/training/train_ultimate_gpu_fast.py`

### Web Viewer
- `web-viewer/src/App.jsx` (18 lines)
- `web-viewer/src/components/Scene.jsx` (81 lines)
- `web-viewer/src/components/GaussianSplat.jsx` (69 lines)
- `web-viewer/src/components/Controls.jsx` (139 lines)
- `web-viewer/package.json` (34 lines)

### Training Outputs
- `namma-space-project/.work/` (7 training run directories)
- `namma-space-project/output-models/` (mesh, pointcloud, viewer.html)
- `logs/training.log` (last run at ~13% completion)

### Documentation
- `README.md`, `docs/*.md` (9 documents)
- `ROUND-1.md` (2260 lines — master execution plan)
- `Round-1-info.md` (858 lines — strategic analysis)

---

**Next Step:** Read `ARCHITECTURE.md` once created to understand the frozen architecture for Phase 1 implementation.

---

*Generated by Phase 0 Audit — 2026-09-29*
