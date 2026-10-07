# Namma Space — Architecture Freeze
**Version:** 1.0  
**Date:** 2026-09-29  
**Status:** FROZEN for Round 1

---

## 1. Core Architectural Principle

**Namma Space is not a Gaussian Splat viewer. It is a spatial engine that uses Gaussian Splatting for photorealistic visualization and an independent geometric-semantic representation for POI discovery and collision-free navigation.**

This separation is the fundamental design principle for all subsequent work.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    NAMMA SPACE ENGINE                    │
└─────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ↓                  ↓                  ↓
  ┌────────────┐    ┌────────────┐    ┌────────────┐
  │  VISUAL    │    │  SPATIAL   │    │  SEMANTIC  │
  │   TRUTH    │    │   TRUTH    │    │   TRUTH    │
  └────────────┘    └────────────┘    └────────────┘
         │                  │                  │
         ↓                  ↓                  ↓
  Gaussian Splat    Occupancy Grid      POI Database
  (.splat file)     (walkable map)      (searchable)
         │                  │                  │
         └──────────────────┼──────────────────┘
                            ↓
                   ┌─────────────────┐
                   │ SPATIAL ENGINE  │
                   └─────────────────┘
                            │
                   ┌────────┴────────┐
                   ↓                 ↓
              ┌─────────┐      ┌──────────┐
              │ SEARCH  │      │   A*     │
              │ (Fuse)  │      │ (Yuka)   │
              └─────────┘      └──────────┘
                   │                 │
                   └────────┬────────┘
                            ↓
                   ┌─────────────────┐
                   │  WEB VIEWER     │
                   │ (Three.js)      │
                   └─────────────────┘
```

---

## 3. Layer Responsibilities

### Layer 1: Capture
**Input:** iPhone 15 Pro (RGB video + LiDAR depth + ARKit poses + IMU)  
**Output:** Frame sequence + camera trajectory + depth maps

**Technology:**
- Primary: ARKit pose tracking (real-time, robust)
- Secondary: COLMAP (refinement/fallback when ARKit unavailable)
- Depth: LiDAR sensor data (iPhone 15 Pro)

**Why Layered Approach:**
- COLMAP documented failure: 2/810 frames registered
- ARKit provides continuous pose even in low-texture environments
- Competition requires "repeat reliably on completely new venue"

### Layer 2: Reconstruction
**Input:** Frames + poses + depth  
**Output:** Visual representation (Gaussian Splat) + Geometric representation (point cloud/mesh)

**Technology:**
- Visual: Splatfacto (Nerfstudio) → .splat file
- Geometry: Dense reconstruction → mesh/point cloud

**Separation Principle:**
- Gaussian Splat is the **visual skin**
- Geometry/depth is the **spatial skeleton**

### Layer 3: Spatial Truth
**Input:** Reconstructed geometry + depth maps  
**Output:** Occupancy grid + navigation mesh + floor extraction

**Components:**
1. **Floor Extraction:** Identify walkable surfaces
2. **Occupancy Grid:** 2D/3D map (free space vs obstacles)
3. **Obstacle Inflation:** Expand obstacles by human clearance radius (~0.5m)
4. **Navigation Mesh:** Yuka.js NavMesh generation

**Grid Representation:**
```
0 = free (walkable)
1 = obstacle (furniture, walls)
2 = wall (structural boundary)
3 = POI (point of interest location)
```

### Layer 4: Semantic Truth
**Input:** RGB frames + OCR + object detection  
**Output:** POI database (searchable, indexed)

**POI Schema:**
```json
{
  "id": "poi_024",
  "name": "Meeting Room 4",
  "category": "room",
  "position": [12.42, 0.0, -7.83],
  "floor": 1,
  "bounding_box": [[x1,y1,z1], [x2,y2,z2]],
  "confidence": 0.94,
  "detected_via": "ocr|manual|object_detection"
}
```

**Technology:**
- Spatial indexing: RBush (R-tree)
- Fuzzy search: Fuse.js
- Detection: OCR (Tesseract) + object detection (optional Round 2)

### Layer 5: Search & Navigation
**Input:** User query + current position + destination POI  
**Output:** Collision-free path (3D coordinates)

**Search Flow:**
```
User: "3 seater sofas"
    ↓
Fuse.js semantic matching
    ↓
POI database lookup
    ↓
Destination coordinates [x, y, z]
    ↓
A* pathfinding (Yuka)
    ↓
Path waypoints [[x1,y1,z1], [x2,y2,z2], ...]
```

**Pathfinding Guarantee:**
- A* operates on **obstacle-inflated** navigation graph
- Mathematical guarantee: no path passes within 0.5m of obstacles
- Judge question: "How do you know this route is physically possible?"
- Answer: "Navigation computed from independent geometric representation with human clearance radius."

### Layer 6: Web Viewer
**Input:** .splat file + navigation graph + POI database  
**Output:** Interactive 3D experience

**Technology:**
- Framework: React 18 + Vite
- 3D Engine: Three.js + @react-three/fiber
- Splat Renderer: @mkkellogg/gaussian-splats-3d
- Controls: First-person WASD + pointer lock

**UI Components:**
1. Search bar (top)
2. 3D viewport (main)
3. POI markers (in-world labels)
4. Navigation path (rendered line)
5. Minimap (optional Round 2)
6. Instructions overlay

### Layer 7: AR Navigation (Bonus)
**Status:** Deferred to post-Round 1  
**Rationale:** AR is 10% bonus, desktop navigation is 20% required criterion

---

## 4. Data Flow

### End-to-End Pipeline

```
┌──────────────┐
│ iPhone Video │
└──────┬───────┘
       ↓
┌────────────────────────────┐
│ Frame Extraction (FFmpeg)  │
└──────┬─────────────────────┘
       ↓
┌──────────────────────────────────┐
│ Pose Estimation (ARKit+COLMAP)   │
└──────┬───────────────────────────┘
       ↓
┌──────────────────────────────────┐
│ 3D Reconstruction (Splatfacto)   │
└──────┬───────────────────────────┘
       │
       ├──→ Visual Representation
       │       ↓
       │   .splat file
       │       ↓
       │   Three.js viewer
       │
       └──→ Spatial Representation
               ↓
           Point cloud/mesh
               ↓
           Occupancy grid
               ↓
           Navigation graph
               ↓
           A* pathfinding
```

---

## 5. Technology Stack (Frozen)

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Capture** | iPhone 15 Pro | iOS 18 | LiDAR + ARKit poses |
| **Pose (Primary)** | ARKit | iOS 18 | Real-time tracking |
| **Pose (Secondary)** | COLMAP | 4.1.1 | Refinement/fallback |
| **Frame Extraction** | FFmpeg | 9.0.1 | Keyframe extraction |
| **3D Reconstruction** | Nerfstudio | 1.x | Splatfacto training |
| **Visual Renderer** | @mkkellogg/gaussian-splats-3d | 0.5.0 | .splat → Three.js |
| **Web Framework** | React | 18.3.1 | UI components |
| **3D Engine** | Three.js | 0.167.0 | WebGL rendering |
| **Build Tool** | Vite | 5.3.4 | Dev server + bundler |
| **Spatial Index** | RBush | 4.0.1 | R-tree for POIs |
| **Search** | Fuse.js | 7.0.0 | Fuzzy semantic search |
| **Navigation** | Yuka | 0.8.1 | NavMesh + A* |
| **Hardware** | MacBook Pro M5 Max | 36GB | Training workstation |

---

## 6. File Format Specifications

### .splat File
- **Purpose:** Visual representation for Three.js viewer
- **Format:** Binary Gaussian Splat (compressed)
- **Size:** ~50-200 MB per room
- **Viewer:** `@mkkellogg/gaussian-splats-3d`

### transforms.json
- **Purpose:** Camera poses + metadata
- **Format:** JSON (Nerfstudio schema)
- **Content:** Per-frame camera matrix, intrinsics, file paths
- **Source:** COLMAP → Nerfstudio conversion

### occupancy_grid.json
- **Purpose:** Walkable space representation
- **Format:** JSON grid or PNG heightmap
- **Resolution:** 0.1m per cell (10cm grid)
- **Values:** 0=free, 1=obstacle, 2=wall, 3=POI

### poi_database.json
- **Purpose:** Searchable location index
- **Format:** JSON array of POI objects
- **Schema:** See Layer 4 above
- **Indexing:** RBush spatial tree + Fuse.js text index

### nav_mesh.json
- **Purpose:** Yuka navigation mesh
- **Format:** Yuka NavMesh export
- **Content:** Polygons, edges, connectivity

---

## 7. Operating Rules (from ROUND-1.md)

1. **Work phase-by-phase** — Don't skip ahead to Round 2 features before Round 1 deliverables work
2. **Don't destroy the working pipeline** — Preserve `web-viewer/` as-is; build spatial-engine version separately
3. **Separate visual truth from spatial truth** — Never run pathfinding directly on Gaussian Splat
4. **Measurable decisions** — "Because it looks better" is not a technical justification
5. **Log every experiment** — Create `experiments/` for all architectural trials
6. **Round 1 deliverables first** — Technical Abstract, working demo, video, code
7. **Don't build navigation on splats** — See Rule 3
8. **COLMAP is not the sole answer** — Must implement ARKit fallback
9. **POI search is not hardcoded** — Must use semantic database + search library
10. **Keep the team (user) informed** — Document decisions in DECISIONS.md

---

## 8. Interfaces Between Layers

### Capture → Reconstruction
```json
{
  "frames": ["frame_0001.jpg", "frame_0002.jpg", ...],
  "poses": "transforms.json",
  "depth_maps": ["depth_0001.png", ...],
  "method": "arkit|colmap|hybrid"
}
```

### Reconstruction → Spatial Truth
```json
{
  "point_cloud": "dense_cloud.ply",
  "mesh": "mesh.obj",
  "splat": "model.splat",
  "bounds": {"min": [-10, -1, -10], "max": [10, 3, 10]}
}
```

### Spatial Truth → Navigation
```json
{
  "occupancy_grid": "occupancy.json",
  "nav_mesh": "navmesh.json",
  "walkable_bounds": {"min": [x, y, z], "max": [x, y, z]}
}
```

### Semantic Truth → Search
```json
{
  "pois": "poi_database.json",
  "spatial_index": "rbush_index.json",
  "search_index": "fuse_index.json"
}
```

---

## 9. Quality Gates

### Capture Acceptance Criteria
- [ ] Frame extraction: ≥250 frames, ≤400 frames
- [ ] Frame overlap: ≥60% consecutive overlap
- [ ] Pose continuity: <0.5m jumps between frames
- [ ] Depth coverage: ≥80% of frames have valid depth
- [ ] Tracking confidence: ARKit "high" or "medium" on ≥90% frames

### Reconstruction Acceptance Criteria
- [ ] Pose registration: ≥80% frames successfully registered
- [ ] Visual quality: No major artifacts, ghosting, or holes
- [ ] Splat file size: <300 MB per room
- [ ] Training convergence: PSNR ≥28 dB, SSIM ≥0.85
- [ ] Export successful: .splat file loads in Three.js viewer

### Spatial Truth Acceptance Criteria
- [ ] Floor extraction: Continuous walkable surface detected
- [ ] Occupancy grid: ≥95% cells correctly classified
- [ ] Navigation mesh: Valid paths exist between all reachable areas
- [ ] Obstacle inflation: 0.5m clearance enforced

### Web Viewer Acceptance Criteria
- [ ] Load time: <10 seconds on desktop
- [ ] Frame rate: ≥30 FPS on MacBook Pro M5 Max
- [ ] Controls: WASD + pointer lock functional
- [ ] Search: POI query returns results in <500ms
- [ ] Navigation: Path renders correctly in 3D scene

---

## 10. What We're NOT Building (Yet)

### Explicitly Deferred to Round 2
- ❌ AR navigation (bonus feature, 10%)
- ❌ Automatic object detection (can use manual POI tagging)
- ❌ Multi-floor support (single floor for Round 1)
- ❌ Real-time relocalization (viewer starts at fixed position)
- ❌ Semantic segmentation (can use simple geometry-based detection)

### Explicitly Out of Scope
- ❌ Dynamic objects (people, moving furniture)
- ❌ Outdoor navigation
- ❌ Multi-user collaboration
- ❌ Voice search
- ❌ Accessibility features (screen reader, etc.)

---

## 11. Round 1 Deliverable Architecture

### Technical Abstract Structure (5 pages max)
1. **Introduction** (0.5 pages) — Problem statement, approach summary
2. **Capture System** (1 page) — ARKit + COLMAP, SOP, iPhone 15 Pro
3. **Reconstruction Pipeline** (1.5 pages) — Splatfacto, training, visual quality
4. **Spatial Intelligence** (1.5 pages) — Occupancy grid, A*, POI search
5. **Web Viewer** (0.5 pages) — Three.js, WASD, search UI

### Demo Video Structure (3-5 min)
1. **Intro** (30 sec) — Team, project name, competition
2. **Capture** (60 sec) — iPhone capture in action, SOP demonstration
3. **Reconstruction** (45 sec) — Training visualization, resulting model
4. **Web Viewer** (90 sec) — Live navigation, POI search, path calculation
5. **Technical Q&A** (45 sec) — Architecture explanation, key decisions

### Code Repository Structure
```
3D/
├── README.md                    (Setup + quick start)
├── ARCHITECTURE.md              (This document)
├── CURRENT_STATE.md             (Phase 0 audit)
├── DECISIONS.md                 (Technical decision log)
├── docs/                        (Comprehensive guides)
├── scripts/                     (Automation)
├── web-viewer/                  (Working viewer)
├── experiments/spatial-engine-v2/ (New architecture)
├── data/sample/                 (Demo room data)
└── round1-submission/           (Submission package)
```

---

## 12. Architecture Freeze Rationale

### Why This Architecture?

**Separation of Visual and Spatial Truth:**
- Gaussian Splats excel at photorealism, fail at spatial queries
- Judges will test pathfinding, not just visual quality
- Industry standard (ROS, Unity NavMesh) separates rendering from navigation

**Layered Pose Estimation:**
- COLMAP failure documented (2/810 frames)
- Competition requires "repeat reliably on new venue"
- ARKit provides continuous tracking even in low-texture corridors

**Existing Libraries Over Custom:**
- RBush, Fuse.js, Yuka already installed in package.json
- 3 weeks to Round 1 submission — no time for custom implementations
- Well-tested libraries reduce risk

**Web-First, AR-Later:**
- Desktop navigation is 20% of rubric
- AR is 10% bonus
- Browser demo works immediately, no iPhone required for judges

---

## 13. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| COLMAP fails on new venue | ARKit primary pose source |
| Splat file too large for web | Progressive loading, compression |
| A* too slow for real-time | Pre-compute navigation graph, limit search depth |
| POI detection inaccurate | Start with manual tagging, automate in Round 2 |
| Web viewer frame rate drops | Reduce splat resolution, optimize render settings |
| Training doesn't converge | Use proven hyperparameters from working runs |

---

## 14. Success Metrics

### Round 1 Submission (Oct 31, 2026)
- [ ] Technical Abstract submitted (PDF, ≤5 pages)
- [ ] Web viewer deployed and accessible via URL
- [ ] Demo video uploaded (3-5 min)
- [ ] Code repository public with README + sample data
- [ ] End-to-end reproduction: video → deployed viewer in <4 hours

### Technical Acceptance
- [ ] Judge can search for a POI and see result
- [ ] Judge can click destination and see rendered path
- [ ] Path visibly avoids obstacles (not straight line through walls)
- [ ] System can explain how spatial truth is separated from visual
- [ ] Capture SOP can be repeated on new venue

---

## 15. Authority and Change Control

**This document is FROZEN** for Phase 1-6 work (Round 1 submission).

Changes require:
1. Documented justification in DECISIONS.md
2. Experiment validation in `experiments/`
3. User (team lead) approval

**Allowed without re-freeze:**
- Implementation details (variable names, file organization)
- Performance optimizations (if architecture unchanged)
- Bug fixes
- Documentation clarifications

**Requires re-freeze:**
- Changing technology stack (e.g., replacing Yuka with custom A*)
- Adding/removing layers
- Changing data formats
- Modifying layer responsibilities

---

**Frozen on:** 2026-09-29  
**Next review:** After Round 1 submission (post Oct 31, 2026)

---

*This architecture is designed to score well on the IIT Bombay Techfest rubric while remaining achievable in 3 weeks with existing technology.*
