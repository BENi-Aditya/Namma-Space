# 🏛️ Namma Space — 3D Indoor Navigation System

> **IIT Bombay Techfest 2026-27 Entry**  
> An end-to-end spatial computing pipeline transforming smartphone video captures into photorealistic, interactive 3D web environments with real-time indoor navigation — *Google Maps for Indoors*.

---

## 🎯 Competition Objectives & Milestones

- **Round 1 (Due Oct 31, 2026):** High-fidelity 3D reconstruction + interactive Three.js web viewer with free roaming (WASD + mouse).
- **Round 2 (Due Nov 30, 2026):** Point of Interest (POI) spatial search, navigation mesh generation, and pathfinding.
- **Round 3 (Dec 16–17, 2026):** On-site capture, live demo & presentation at IIT Bombay.

---

## 🏗️ Repository Architecture

```
3D/
├── 📚 docs/                       # Comprehensive guides, technical specs & SOPs
│   ├── README.md                  # Documentation index
│   ├── quickstart.md              # 5-minute setup and walkthrough
│   ├── capture_sop.md             # iPhone 15 Pro video capture SOP
│   ├── how_it_works.md            # Gaussian Splatting & COLMAP architecture
│   ├── training_options.md        # Training presets & Apple Silicon flags
│   ├── troubleshooting.md         # Troubleshooting & error resolution
│   ├── competition_guide.md       # Competition roadmap & submission checklist
│   ├── competition_guide.html     # Interactive HTML competition guide
│   ├── competition_problem_statement.pdf # Official Techfest problem statement
│   └── project_context.md         # Full project history & development logs
│
├── ⚙️ scripts/                    # Automation and pipeline scripts
│   ├── README.md                  # Scripts reference guide
│   ├── setup/                     # Environment configuration & prerequisite installers
│   │   ├── setup.sh               # Standard automated environment setup
│   │   ├── setup-fixed.sh         # Apple Silicon (M-series / M5 Max) optimized setup
│   │   ├── clean-install.sh       # Clean conda reinstall script
│   │   └── preflight-check.sh     # System diagnostics & hardware checks
│   ├── pipeline/                  # End-to-end processing & export tools
│   │   ├── process_video.sh       # Video → COLMAP → Training → Export pipeline
│   │   ├── extract-frames.sh      # FFmpeg frame extraction utility
│   │   ├── export_pipeline.py     # Multi-format exporter (.splat, .ply, .obj, .stl)
│   │   ├── export-model.sh        # Gaussian Splat exporter helper
│   │   ├── run.sh / run-simple.sh # Interactive pipeline launchers
│   │   ├── view-3d-model.sh       # Model viewer launcher
│   │   ├── view-mesh.sh           # Mesh visualizer launcher
│   │   └── start-tensorboard.sh   # Live training metrics dashboard
│   ├── training/                  # Dedicated training runners
│   │   ├── train_gpu_viewer_working.py # GPU trainer with real-time interactive viewer
│   │   ├── train_ultimate_gpu_fast.py  # High-throughput optimized trainer
│   │   ├── train-competition.sh   # Full-resolution competition runner
│   │   ├── train-1-competition.sh # Dedicated room 1 competition preset
│   │   ├── start-training-cli.sh  # Optimized CLI runner
│   │   ├── resume-training.sh     # Checkpoint training resume
│   │   └── archive/               # Historical / experimental training presets
│   └── tests/                     # Validation & diagnostic test scripts
│
├── 🌐 web-viewer/                 # React 18 + Three.js 3D Web Viewer Application
│   ├── src/components/
│   │   ├── Scene.jsx              # Main 3D scene & canvas
│   │   ├── Controls.jsx           # First-person WASD + pointer lock navigation
│   │   ├── GaussianSplat.jsx      # Gaussian splat renderer
│   │   └── Instructions.jsx       # Interactive UI overlay
│   └── public/models/             # Web-ready .splat 3D models
│
├── 📁 data/                       # Input videos and intermediate work artifacts
│   ├── raw-videos/                # Raw iPhone 15 Pro video files (.mp4, .mov)
│   └── processed/                 # COLMAP databases and sparse point clouds
│
├── 📦 exports/                    # Production 3D models, point clouds & navmeshes
│
└── 📊 logs/                       # Training execution logs (e.g. training.log)
```

---

## ⚡ Quick Start

### 1. Environment Setup
```bash
# Set up conda environment and dependencies (Apple Silicon M5 Max optimized)
./scripts/setup/setup-fixed.sh

# Activate conda environment
conda activate namma-space

# Verify setup
./scripts/setup/preflight-check.sh
```

### 2. Capture Video
Follow the [Capture SOP](docs/capture_sop.md):
- Record 4K 30fps video using iPhone 15 Pro
- Walk steadily (1–2 sec/meter) with 70–80% frame overlap
- Place the recording in `data/raw-videos/your_room.mp4`

### 3. Process Video & Train Model
```bash
# Run automated pipeline (COLMAP + Splatfacto + Export)
./scripts/pipeline/process_video.sh data/raw-videos/your_room.mp4 your_room

# Or run with the real-time interactive viewer
python scripts/training/train_gpu_viewer_working.py
```

### 4. Launch Web Navigation Viewer
```bash
# Copy exported splat model to web viewer
cp exports/models/your_room/*.splat web-viewer/public/models/demo.splat

# Start the Vite development server
cd web-viewer
npm install
npm run dev

# Open http://localhost:5173 in browser
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Capture** | iPhone 15 Pro (4K 30fps + LiDAR) | Spatial video capture |
| **Camera Poses** | COLMAP 4.1.1 | Feature extraction & sparse SfM reconstruction |
| **Frame Extraction** | FFmpeg 9.0.1 | High-quality frame extraction at keyframe intervals |
| **3D Reconstruction** | Nerfstudio + Splatfacto | 3D Gaussian Splatting with MPS/CUDA acceleration |
| **Web Rendering** | React 18 + Three.js + Vite | Real-time interactive browser experience (60fps) |
| **Splat Loader** | `@mkkellogg/gaussian-splats-3d` | Efficient point cloud & splat rendering |
| **Pathfinding (R2)** | Yuka.js + Recast Navigation | Navmesh generation & shortest-path calculation |
| **Spatial Index (R2)**| RBush + Fuse.js | Real-time Point of Interest (POI) search |

---

## 📖 Key Documentation

- 🚀 [**Quickstart Guide**](docs/quickstart.md) — Step-by-step 5-minute setup
- 📱 [**Capture SOP**](docs/capture_sop.md) — iPhone camera recording standard operating procedure
- ⚙️ [**How It Works**](docs/how_it_works.md) — Technical pipeline architecture & mathematical foundations
- 🎛️ [**Training Options**](docs/training_options.md) — Hyperparameter tuning & performance presets
- 🔧 [**Troubleshooting Guide**](docs/troubleshooting.md) — Fixes for COLMAP mismatches, OOM errors, and web glitches
- 🏆 [**Competition Strategy**](docs/competition_guide.md) — IIT Bombay Techfest roadmap and submission criteria
- 📜 [**Problem Statement (PDF)**](docs/competition_problem_statement.pdf) — Official challenge specifications

---

## 👥 Team & License

- **Developer:** Solo developer for IIT Bombay Techfest 2026-27
- **Hardware:** MacBook Pro M5 Max (36GB Unified Memory) + iPhone 15 Pro
- **License:** MIT License
