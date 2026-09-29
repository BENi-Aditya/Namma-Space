# ⚙️ Namma Space - Scripts Directory

This directory houses all automation scripts for environment setup, video preprocessing, 3D model training, multi-format export, and testing.

---

## 📂 Folder Structure

```
scripts/
├── setup/          # Environment configuration & prerequisite installers
├── pipeline/       # End-to-end data processing & export utilities
├── training/       # Core 3D Gaussian Splatting & NeRF training runners
│   └── archive/    # Archived/experimental variations
└── tests/          # Diagnostic tests and bash script verifications
```

---

## 1. 🛠️ Setup Scripts (`scripts/setup/`)

| Script | Purpose | When to Use |
| :--- | :--- | :--- |
| `setup.sh` | Standard automated environment setup for conda, COLMAP, and Nerfstudio | Initial setup on standard Unix environments |
| `setup-fixed.sh` | Optimized setup tailored for Apple Silicon (M-series / M5 Max) | First-time setup on macOS Apple Silicon |
| `clean-install.sh` | Completely removes and rebuilds conda environment & dependencies | Resolving corrupted environments or linker conflicts |
| `preflight-check.sh` | Diagnostics script checking GPU/Metal, COLMAP, ffmpeg, and Python paths | Run before starting long training sessions |

---

## 2. 🔄 Pipeline Scripts (`scripts/pipeline/`)

| Script | Purpose | Usage |
| :--- | :--- | :--- |
| `process_video.sh` | Automated end-to-end pipeline: video extraction → COLMAP → training → export | `./scripts/pipeline/process_video.sh <video_path> [room_name]` |
| `extract-frames.sh` | FFmpeg frame extraction with customized FPS / target frame count | `./scripts/pipeline/extract-frames.sh` |
| `run.sh` / `run-simple.sh` | Interactive CLI menu for running steps individually or end-to-end | `./scripts/pipeline/run-simple.sh` |
| `export_pipeline.py` | Multi-format 3D exporter (.splat, .ply, .obj, .stl pointclouds & meshes) | `python scripts/pipeline/export_pipeline.py` |
| `export-model.sh` | Quick exporter script for trained Gaussian Splatting models | `./scripts/pipeline/export-model.sh` |
| `view-3d-model.sh` | Launches viewer for exported `.splat` files | `./scripts/pipeline/view-3d-model.sh` |
| `view-mesh.sh` | Launches viewer for exported 3D mesh files | `./scripts/pipeline/view-mesh.sh` |
| `start-tensorboard.sh` | Starts TensorBoard metrics server at `http://localhost:6006` | `./scripts/pipeline/start-tensorboard.sh` |

---

## 3. 🎯 Training Scripts (`scripts/training/`)

| Script | Engine / Method | Features |
| :--- | :--- | :--- |
| `train_gpu_viewer_working.py` | PyTorch / Splatfacto | GPU-accelerated trainer with real-time interactive web viewer |
| `train_ultimate_gpu_fast.py` | PyTorch / Splatfacto | Highly optimized high-throughput trainer for fast iterations |
| `train-competition.sh` | Nerfstudio CLI | Full-resolution training tuned for competition submission |
| `train-1-competition.sh` | Nerfstudio CLI | Dedicated single-room competition preset (video 1) |
| `start-training-cli.sh` | Nerfstudio CLI | Production CLI trainer with optimized parameters |
| `start-training-final.sh` | Nerfstudio CLI | Final milestone runner with full dataset |
| `resume-training.sh` | Nerfstudio CLI | Safely resumes interrupted training from checkpoints |
| `train-now.sh` | Nerfstudio CLI | Instant trigger script for immediate training |
| `emergency-train.sh` | Nerfstudio CLI | Fallback low-memory preset for tight deadlines |

### Archived Training Presets (`scripts/training/archive/`)
Historical training presets and legacy scripts are stored in `scripts/training/archive/` (e.g. `train-ultra-fast.sh`, `train-fastest-cpu.sh`, `train-super-fast.sh`).

---

## 4. 🧪 Test & Diagnostic Scripts (`scripts/tests/`)

Contains test scripts for COLMAP sparse extraction, path matching, segmentation tests, and shell snippet verifications.

---

## 💡 Quick Tips

Always ensure your Conda environment is active before running pipeline or training scripts:
```bash
conda activate namma-space
```
