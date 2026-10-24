# Spatial Engine V2 — Experiment Directory

This directory contains experiments and implementations for the layered spatial intelligence architecture described in [`ARCHITECTURE.md`](../../docs/history/ARCHITECTURE.md).

---

## Purpose

Separate visual representation (Gaussian Splat) from spatial truth (occupancy grid, navigation mesh, POI database) to enable:
1. Semantic POI search ("Meeting Room 4")
2. Collision-free pathfinding (A*)
3. Robust spatial queries

**Rule:** Do not destroy the working `web-viewer/` pipeline. Build and validate here first.

---

## Directory Structure

```
experiments/spatial-engine-v2/
├── capture/           # ARKit pose extraction, capture quality validation
├── reconstruction/    # Hybrid pose pipeline (ARKit + COLMAP fusion)
├── spatial-truth/     # Occupancy grid, floor extraction, obstacle inflation
├── navigation/        # A* integration, NavMesh generation
├── docs/              # Experiment logs, results, validation reports
└── README.md          # This file
```

---

## Experiment Tracking

All experiments must be logged in [`docs/experiments.log`](docs/experiments.log) with:
- Date
- Hypothesis
- Method
- Results
- Conclusion
- Next action

**No vague conclusions.** Every experiment must produce measurable data.

---

## Phase Mapping

This directory supports work in:
- **Phase 1:** Capture SOP validation (measurable quality checks)
- **Phase 2:** Reliable Pose Pipeline (ARKit extraction, hybrid fusion)
- **Phase 3:** Reconstruction Benchmark (pose source comparison)
- **Phase 4:** Web Viewer (spatial-aware version)

---

## Current Status

**Created:** 2026-09-29  
**Phase:** 0 (audit complete, scaffold created)  
**Next Step:** Phase 1 begins after .splat deployment to existing viewer

---

See [`ARCHITECTURE.md`](../../docs/history/ARCHITECTURE.md) for full system design.
