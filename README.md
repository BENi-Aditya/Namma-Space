# Namma Space - 3D Indoor Navigation System

**IIT Bombay Techfest 2026-27 Competition Entry**

## Project Overview

This project builds an end-to-end system that converts smartphone captures of indoor spaces into interactive 3D web experiences with navigation capabilities - essentially "Google Maps for indoors."

## Competition Goals

- **Round 1** (Due: Oct 31, 2026): 3D reconstruction + web viewer with free roaming
- **Round 2** (Due: Nov 30, 2026): POI labeling + desktop pathfinding navigation
- **Round 3** (Dec 16-17, 2026): On-site capture and live demo at IIT Bombay

**Prize**: Full-time job opportunity at Juspay (with AR navigation bonus)

## Quick Start

### 1. Setup Environment

```bash
# Run automated setup script
./setup.sh

# This installs:
# - COLMAP (camera pose estimation)
# - ffmpeg (video processing)
# - nerfstudio (3D reconstruction)
# - Creates conda environment 'namma-space'
# - Creates project structure
```

### 2. Capture Your First Space

Follow the detailed instructions in [`capture_sop.md`](capture_sop.md):

1. Use iPhone 15 Pro Camera app (4K 30fps)
2. Record 2-3 minute video walking slowly through space
3. Move at 1-2 seconds per meter
4. Capture from multiple heights
5. Ensure 70-80% frame overlap

### 3. Process Video

```bash
# Activate conda environment
conda activate namma-space

# Process video and train model (30-90 minutes)
./process_video.sh data/raw-videos/your_room.mp4 your_room

# This will:
# - Extract frames
# - Run COLMAP for camera poses
# - Train Gaussian Splatting model
# - Export for web viewer
```

### 4. View in Browser

```bash
# Copy model to web viewer
cp exports/models/your_room/*.splat web-viewer/public/models/demo.splat

# Install web viewer dependencies (first time only)
cd web-viewer
npm install

# Start development server
npm run dev

# Open browser to http://localhost:5173
```

## Project Structure

```
3D/
├── setup.sh                 # Automated environment setup
├── process_video.sh         # Video → 3D model pipeline
├── capture_sop.md           # iPhone capture instructions
│
├── data/
│   ├── raw-videos/          # iPhone videos
│   └── processed/           # COLMAP output
│
├── exports/
│   ├── models/              # Trained .splat files
│   └── navmeshes/           # Navigation meshes (Round 2)
│
└── web-viewer/              # React Three.js viewer
    ├── public/models/       # Place .splat files here
    └── src/components/
        ├── Scene.jsx        # Main 3D scene
        ├── Controls.jsx     # WASD navigation
        ├── GaussianSplat.jsx # Model loader
        └── Instructions.jsx  # UI overlay
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Capture** | iPhone 15 Pro Camera | Video recording |
| **Reconstruction** | Nerfstudio + Splatfacto | 3D model training |
| **Preprocessing** | COLMAP | Camera pose estimation |
| **Web Viewer** | React + Three.js | Interactive 3D display |
| **3D Format** | Gaussian Splatting | Photorealistic rendering |
| **Navigation (R2)** | Yuka.js | Pathfinding |
| **POI Search (R2)** | rbush + fuse.js | Spatial indexing |

## Current Status

**Round 1 Components (COMPLETED):**
- ✅ Automated setup script
- ✅ iPhone capture SOP documentation
- ✅ Video processing automation
- ✅ Web viewer with WASD controls
- ✅ Gaussian Splat loader
- ✅ First-person navigation

**Round 2 Components (TODO):**
- ⏳ POI marker system
- ⏳ Search functionality
- ⏳ Navigation mesh generation
- ⏳ Pathfinding algorithm
- ⏳ Path visualization

**Round 3 Components (TODO):**
- ⏳ AR navigation (bonus)
- ⏳ On-site capture workflow
- ⏳ Presentation materials

## Hardware Requirements

- **iPhone 15 Pro** (with LiDAR sensor)
- **MacBook Pro M5 Max** (36GB RAM, 2TB storage)
- Processing time: 30-90 minutes per room

## Key Features

### Current (Round 1)
- 📹 iPhone 15 Pro video capture pipeline
- 🎨 Photorealistic 3D reconstruction (Gaussian Splatting)
- 🕹️ First-person WASD + mouse navigation
- 🌐 Web-based viewer (no installation required)
- ⚡ Real-time rendering (60fps on desktop)

### Planned (Round 2)
- 🔍 POI search and labeling
- 🗺️ Navigation mesh pathfinding
- 📍 Click-to-navigate functionality
- 🧭 Minimap overlay

### Bonus (Round 3)
- 📱 AR navigation on iPhone
- 🎯 Live camera guidance
- 🔄 Real-time position tracking

## Documentation

- **[Setup Instructions](setup.sh)** - Automated environment setup
- **[Capture SOP](capture_sop.md)** - Detailed iPhone capture guide
- **[Processing Pipeline](process_video.sh)** - Video → 3D automation
- **[Web Viewer README](web-viewer/README.md)** - React app documentation
- **[Implementation Plan](.claude/plans/technical-backfround-i-peaceful-puzzle.md)** - Full technical plan

## Usage Examples

### Process Multiple Rooms

```bash
# Process entire apartment
./process_video.sh data/raw-videos/living_room.mp4 living_room
./process_video.sh data/raw-videos/bedroom.mp4 bedroom
./process_video.sh data/raw-videos/kitchen.mp4 kitchen
```

### Combine Models (Advanced)

```bash
# Merge multiple rooms into single scene (Round 2)
# TODO: Implementation pending
```

## Troubleshooting

### COLMAP Fails

**Problem**: Camera pose estimation fails  
**Solution**: Ensure video has:
- Good lighting (no extreme shadows)
- 70-80% frame overlap
- Textured surfaces (not blank walls)
- Slow, steady movement

### Training Crashes

**Problem**: Out of memory during training  
**Solution**: 
- Reduce `--num-frames-target` in process_video.sh
- Close other applications
- Use lower resolution video input

### Web Viewer Black Screen

**Problem**: Model doesn't load in browser  
**Solution**:
- Check `public/models/demo.splat` exists
- Verify file path in GaussianSplat.jsx
- Check browser console for errors

## Competition Timeline

| Date | Milestone |
|------|-----------|
| Sep 8, 2026 | ✅ Project kickoff, environment setup |
| Sep 15, 2026 | ⏳ First test capture and reconstruction |
| Sep 30, 2026 | ⏳ Round 1 submission preparation |
| Oct 31, 2026 | 📅 **Round 1 deadline** |
| Nov 10, 2026 | 📅 Round 1 results |
| Nov 30, 2026 | 📅 **Round 2 deadline** |
| Dec 7, 2026 | 📅 Finalists announced |
| Dec 16, 2026 | 📅 **Round 3 on-site (Day 1)** |
| Dec 17, 2026 | 📅 **Round 3 presentation (Day 2)** |

## Resources

- **Nerfstudio Documentation**: https://docs.nerf.studio/
- **Three.js Documentation**: https://threejs.org/docs/
- **React Three Fiber**: https://docs.pmnd.rs/react-three-fiber
- **Gaussian Splatting Paper**: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
- **Competition Details**: [PDF document.pdf](PDF%20document.pdf)

## Team

- **Solo Developer**: Vibe coder with infinite time commitment
- **Hardware**: iPhone 15 Pro + MacBook Pro M5 Max
- **Approach**: Clone existing projects and adapt

## License

MIT License - Educational project for IIT Bombay Techfest 2026-27

---

**Current Progress**: Round 1 infrastructure complete, ready for first capture  
**Next Step**: Record test room video and run first reconstruction  
**Last Updated**: September 8, 2026
