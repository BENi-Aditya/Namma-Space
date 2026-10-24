> Historical document, archived 24 October 2026. Claims and commands may be outdated. See [current audit](../audit/2026-10-24/AUDIT.md) and [current setup](../REPRODUCTION.md).

# 🏛️ Namma Space — 3D Models & Web Viewer Guide

This document describes the 3D model architecture, storage layout, and web viewer usage for **Namma Space (IIT Bombay Techfest 2026-27)**.

---

## 📂 1. Directory Structure

All trained 3D models and viewer assets are organized cleanly in the workspace:

```text
/Users/tripathd/Downloads/Manual Library/Projects/3D/
├── models/                                      # 🌟 Canonical symlink to all models
│   ├── IMG_2008/                               # [NEW] 3D Gaussian Splatting model
│   │   └── splat.ply                           # 154 MB full-color Gaussian Splat (650k splats)
│   ├── 1-emergency/                            # Emergency Run NeRF model
│   │   ├── mesh/
│   │   │   ├── model.stl                       # 3D printable STL mesh (7.0 MB)
│   │   │   ├── model_mesh.ply                  # Surface mesh PLY (9.0 MB)
│   │   │   └── model.obj                       # Wavefront OBJ mesh (17.9 MB)
│   │   └── pointcloud/
│   │       ├── point_cloud.ply                 # Dense point cloud (3.9 MB)
│   │       └── sparse_point_cloud.ply          # COLMAP sparse point cloud (3.1 MB)
│   ├── your-video/                             # Baseline NeRF model
│   │   ├── mesh/
│   │   │   ├── model.stl                       # 3D printable STL mesh (2.7 MB)
│   │   │   ├── model_mesh.ply                  # Surface mesh PLY (5.5 MB)
│   │   │   └── model.obj                       # Wavefront OBJ mesh (10.5 MB)
│   │   └── pointcloud/
│   │       └── point_cloud.ply                 # Dense point cloud (2.6 MB)
│   └── 2-run/                                  # 2.MOV Run model
│       └── pointcloud/
│           └── sparse_point_cloud.ply          # COLMAP point cloud (11.4 MB)
│
├── start-viewer.sh                             # 🚀 ONE-CLICK WEB VIEWER LAUNCHER
│
├── web-viewer/                                 # 🌐 Web Viewer application & source
│   ├── index.html                              # New CAD Studio & Gaussian Splat viewer
│   ├── vite.config.js                          # Vite configuration
│   └── public/models/                          # Symlinked to output-models/models
│
└── namma-space-project/
    └── output-models/
        ├── index.html                          # New CAD Studio & Gaussian Splat viewer
        ├── viewer.html                         # Backward-compatible viewer entrypoint
        ├── models.json                         # Central model registry & manifest
        ├── lib/                                # Self-contained offline Three.js & Splat libraries
        └── models/                             # Physical model storage directory
```

---

## 📦 2. Available Models in the Web Viewer

| Model ID | Display Name | Method / Pipeline | Formats Available | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`IMG_2008`** | `IMG_2008 (Gaussian Splats)` | **`splatfacto`** (Gaussian Splatting) | `.ply` (Gaussian Splat) | **Trained with friend on GPU**. 650,682 splats. Full photorealistic color reproduction. |
| **`1-emergency`** | `1.mov (Emergency NeRF)` | **`nerfacto`** (NeRF 10,000 steps) | `.stl`, `.ply`, `.obj`, point cloud | High-density 10k step NeRF reconstruction. Printable STL and dense point cloud. |
| **`your-video`** | `Your Video (Baseline NeRF)` | **`nerfacto`** (NeRF 2,999 steps) | `.stl`, `.ply`, `.obj`, point cloud | Baseline NeRF run. Printable STL surface mesh. |
| **`2-run`** | `2.MOV (Point Cloud)` | **`colmap`** feature matching | `.ply` (Point cloud) | Feature point cloud extracted from `2.MOV` with sequential matching. |

---

## 🚀 3. How to Start the Web Viewer Anytime

### Method 1: One-Click Terminal Launcher (Recommended)
From anywhere in the project root:
```bash
./start-viewer.sh
```
This script will:
1. Clean up any stale port listeners automatically.
2. Serve the new unified CAD Studio & Gaussian Splat viewer.
3. Automatically launch your browser at **`http://localhost:8080`**.
4. Load `IMG_2008` (Gaussian Splat) as the default model, with all other models ready in the dropdown.

### Method 2: Vite Development Server
If you are developing or editing the web viewer UI:
```bash
cd web-viewer
npm run dev
```
And open **`http://localhost:5173`**.

---

## 🎮 4. How to Use the Web Viewer

1. **Switch Models**: Use the dropdown in the top bar to instantly switch between `IMG_2008`, `1-emergency`, `your-video`, and `2-run`.
2. **Switch Asset Formats**: For NeRF models, toggle between **STL**, **Surface Mesh PLY**, and **Point Cloud**. For Gaussian Splat models, the full-color **Gaussian Splats** mode is active.
3. **Navigation & Controls**:
   - **Rotate / Orbit**: Left-click + drag
   - **Pan**: Right-click + drag (or Shift + Left-click + drag)
   - **Zoom**: Scroll wheel
   - **WASD Fly-Through**: Press `W`, `A`, `S`, `D` with `Space` (up) and `Shift` (down) to fly inside the room.
4. **Studio Alignment Tools**:
   - **Gizmo Modes**: Select `Translate`, `Rotate`, or `Scale` in the left toolbar to position models.
   - **Slice & Crop**: Expand the **Cropping / Sectioning** panel to clip along X, Y, or Z axes.
   - **Snap to Floor**: Click **Snap to Floor** to automatically place the lowest vertex at `Y = 0`.
   - **Export STL**: Click **Export Aligned STL** to save a 3D-printable model after alignment.

---

## ➕ 5. Adding New Models in the Future

When you train a new model (e.g. `3-run`):
1. Create a folder in `models/<new-id>/`:
   ```bash
   mkdir -p models/my-new-model/mesh
   ```
2. Copy your exported `.ply`, `.stl`, or `.splat` file into that folder.
3. Add an entry to `namma-space-project/output-models/models.json`:
   ```json
   {
     "id": "my-new-model",
     "name": "My New Model Name",
     "method": "splatfacto",
     "step": "10,000 steps",
     "timestamp": "2026-10-12",
     "splat": "models/my-new-model/splat.ply",
     "defaultAsset": "gaussian"
   }
   ```
4. Reload the web viewer — the new model will appear automatically in the dropdown!
