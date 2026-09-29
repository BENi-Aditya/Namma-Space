# Namma Space Project - Complete Progress Document
**IIT Bombay Techfest 2026-27 Competition Entry**
**Last Updated:** September 11, 2026, 11:38 AM IST (6:08 AM UTC)

---

## Project Overview

**Objective:** Build an end-to-end 3D indoor navigation system that converts iPhone videos into photorealistic, interactive 3D models with POI search and navigation capabilities.

**Competition Details:**
- Event: IIT Bombay Techfest 2026-27 - "Namma Space" Challenge
- Prize: Full-time job opportunity at Juspay (with AR navigation bonus)
- Round 1 Deadline: October 31, 2026
- Round 3: On-site demo at IIT Bombay (December 16-17, 2026)

**Team:**
- Solo developer ("vibe coder" - limited technical background)
- Infinite time commitment
- Hardware: iPhone 15 Pro (with LiDAR), MacBook Pro M5 Max (36GB RAM, 2TB storage)

---

## Technology Stack Selected

### 3D Reconstruction:
- **Nerfstudio** (Splatfacto method) - Gaussian Splatting implementation
- **COLMAP 4.1.1** - Camera pose estimation (CPU-only, no CUDA)
- **FFmpeg 9.0.1** - Video frame extraction

### Web Viewer:
- **React 18** + **Vite** - Frontend framework
- **Three.js** - 3D rendering engine
- **React Three Fiber** - React integration for Three.js
- **@mkkellogg/gaussian-splats-3d** - Gaussian Splat loader

### Environment:
- **Miniforge3** - ARM64-native conda distribution
- **Python 3.10** in `namma-space` conda environment
- **Node.js** - For web viewer

---

## Project Structure Created

```
3D/
├── setup.sh                          # Initial setup (deprecated)
├── setup-fixed.sh                    # Fixed setup for M5 Max
├── clean-install.sh                  # Clean reinstall script
├── run.sh                            # Original run script (has issues)
├── run-simple.sh                     # Simplified run script (has issues)
├── resume-training.sh               # Resume from COLMAP output ⭐ CURRENT
├── process_video.sh                 # Video processing automation
├── capture_sop.md                   # iPhone capture guide
├── README.md                        # Full documentation
├── QUICKSTART.md                    # Quick start guide
├── HOW-IT-WORKS.md                  # Backend explanation
│
└── namma-space-project/
    ├── input-videos/
    │   └── your-video.mov           # 14.3MB iPhone video (1101 frames)
    ├── output-models/               # Final 3D models (empty - not reached yet)
    ├── .work/
    │   └── your-video/
    │       ├── images/              # 1100 extracted frames ✅
    │       ├── database.db          # COLMAP database ✅
    │       └── sparse/
    │           └── 0/
    │               ├── 0/           # Model 0: 4 images only
    │               └── 1/           # Model 1: 2,214 images ✅
    └── web-app/                     # React Three.js viewer (ready)
        ├── package.json
        ├── src/components/
        │   ├── Scene.jsx
        │   ├── Controls.jsx
        │   ├── GaussianSplat.jsx
        │   └── Instructions.jsx
        └── public/models/           # Where final .splat files go
```

---

## Complete Timeline of Work

### Day 1: September 8, 2026

**Morning (11:24 AM - 12:45 PM IST):**
1. ✅ Created complete project structure
2. ✅ Wrote all documentation (README, QUICKSTART, HOW-IT-WORKS, capture_sop.md)
3. ✅ Built React Three.js web viewer from scratch
4. ✅ Created automated setup scripts
5. ✅ Ran initial `setup.sh` - encountered first errors

**Issues Encountered:**
- ❌ `rawpy` compilation failure (JPEG library linker errors)
- ❌ Qt/COLMAP symlink conflicts
- ❌ Scipy x86_64/ARM64 architecture mismatch

**Solution:** Created `setup-fixed.sh` and `clean-install.sh` to handle M5 Max compatibility

---

### Day 2: September 9, 2026

**Morning (6:19 AM - 12:30 PM IST):**
1. ✅ Completed clean installation with Miniforge (ARM64-native)
2. ✅ Fixed environment setup
3. ✅ User captured video: `your-video.mov` (14.3MB, ~37 seconds at 30fps = 1101 frames)
4. ✅ Created `run-simple.sh` to bypass nerfstudio's broken ffmpeg commands

**Afternoon (12:30 PM - 1:30 PM IST):**
5. ✅ Frame extraction succeeded: 1100 frames extracted
6. ⏳ Started COLMAP processing

**Issues Encountered:**
- ❌ FFmpeg 9.0.1 removed `-vsync` flag (nerfstudio uses deprecated syntax)
- ❌ COLMAP GPU crashes ("Abort trap: 6")
- ❌ Wrong COLMAP flags: `--SiftExtraction.gpu_index` doesn't exist
- ❌ Wrong matching flags: `--SiftMatching.use_gpu` doesn't exist

**Solutions Applied:**
- ✅ Manual frame extraction to bypass nerfstudio's ffmpeg
- ✅ Fixed to `--FeatureExtraction.use_gpu 0` (correct flag)
- ✅ Fixed to `--FeatureMatching.use_gpu 0` (correct flag)
- ✅ CPU-only mode for COLMAP

**Late Afternoon/Evening (1:30 PM - 7:00 PM IST):**
7. ✅ COLMAP feature extraction: **1.6 minutes** (1105 frames processed)
8. ⏳ COLMAP matching: **~30 minutes** (silent processing, no output)
9. ⏳ COLMAP sparse reconstruction (mapper): **~17 minutes**

**Night (11:00 PM - 1:00 AM IST):**
10. ✅ COLMAP mapper completed after ~50 minutes total
11. ✅ Created 2 sparse models:
    - Model 0: Only 4 images registered (bad)
    - Model 1: **2,214 images registered** (good!) ⭐
12. ❌ Script incorrectly reported "COLMAP mapper failed" (overly strict error checking)

---

### Day 3: September 10, 2026

**Night (10:12 PM - 11:00 PM IST):**
1. ✅ Created `resume-training.sh` to continue from existing COLMAP output
2. ✅ Script now detects Model 1 with 2,214 images
3. ✅ Converts binary files to text format for nerfstudio
4. ❌ **Current blocker:** `fpsample` architecture mismatch

**Issues Encountered:**
- ❌ `fpsample` compiled for x86_64 instead of ARM64
- ❌ ImportError: "have 'x86_64', need 'arm64'"
- ❌ Pip cache returning wrong architecture wheel

**Attempted Solutions:**
1. ❌ `pip uninstall fpsample -y && pip install fpsample` - still got x86_64
2. ❌ `pip install --no-cache-dir --force-reinstall fpsample` - still got x86_64
3. ⏳ **Next attempt:** `ARCHFLAGS="-arch arm64" pip install --no-binary :all: fpsample`

---

## Current Status (September 11, 2026, 11:38 AM IST)

### ✅ Completed Work:
1. **Environment Setup** - Miniforge, Python 3.10, nerfstudio installed
2. **Video Captured** - 14.3MB, 1101 frames
3. **Frame Extraction** - 1100 frames successfully extracted
4. **COLMAP Processing** - Completed after ~50 minutes:
   - Feature extraction: 1105 files processed
   - Matching: Exhaustive matching complete
   - Sparse reconstruction: 2,214 images registered in Model 1
5. **Web Viewer** - Complete React Three.js app ready
6. **Training** - Completed 3000 steps (2026-09-13_154156, 243MB checkpoint)
7. **Scripts Fixed** - export-model.sh and view-3d-model.sh (OpenMP + config path)

### ⬜ Current Step: Training complete!
Run `./export-model.sh` to generate 3D model files, then `./view-3d-model.sh` for interactive viewer.

### 🔄 Next Steps:
1. Run `./export-model.sh` (PLY point cloud + poisson mesh)
2. Run `./view-3d-model.sh` (interactive viewer at localhost:7007)
3. For STL: open mesh in Blender/MeshLab → Export → STL

---

## All Issues Encountered (Chronological)

### 1. rawpy Compilation Failure
**Error:** JPEG library linker errors during pip install
**Root Cause:** Missing JPEG headers for M5 Max
**Solution:** Installed jpeg-turbo via Homebrew, added to LDFLAGS

### 2. Qt/COLMAP Symlink Conflicts
**Error:** "brew link" conflicts between Qt and COLMAP
**Root Cause:** Multiple Qt versions installed
**Solution:** `brew link --overwrite colmap`

### 3. Scipy x86_64/ARM64 Mismatch
**Error:** scipy module import error, Rosetta translation attempted
**Root Cause:** Using regular Anaconda (x86_64) instead of ARM64
**Solution:** Complete reinstall with Miniforge (ARM64-native)

### 4. FFmpeg `-vsync` Deprecation
**Error:** "Unrecognized option 'vsync'"
**Root Cause:** FFmpeg 9.x removed `-vsync` flag, nerfstudio code outdated
**Solution:** Manual frame extraction bypassing nerfstudio's video processing

### 5. COLMAP GPU Crashes
**Error:** "Abort trap: 6" during feature extraction
**Root Cause:** COLMAP built without CUDA, macOS GPU issues
**Solution:** Force CPU-only mode with correct flags

### 6. Wrong COLMAP Flag: `--SiftExtraction.gpu_index`
**Error:** "Failed to parse options - unrecognised option"
**Root Cause:** Wrong flag name for COLMAP 4.1.1
**Solution:** Changed to `--FeatureExtraction.use_gpu 0`

### 7. Wrong COLMAP Flag: `--SiftMatching.use_gpu`
**Error:** "Failed to parse options - unrecognised option"
**Root Cause:** Wrong flag name for matching
**Solution:** Changed to `--FeatureMatching.use_gpu 0`

### 8. COLMAP Matching Silent Processing
**Error:** No output for 10-30 minutes, appeared stuck
**Root Cause:** COLMAP doesn't print progress during exhaustive matching
**Solution:** User education - it's normal, just wait

### 9. COLMAP Mapper "Failed" (False Positive)
**Error:** Script reported failure despite 2,214 images registered
**Root Cause:** Overly strict error checking in script
**Solution:** Check for actual output files instead of exit codes

### 10. Only 4 Images in Model 0
**Error:** First model only had 4 registered images
**Root Cause:** COLMAP created multiple models, script used wrong one
**Solution:** Check both models, use Model 1 with 2,214 images

### 11. fpsample x86_64 Architecture (CURRENT ISSUE)
**Error:** "have 'x86_64', need 'arm64'"
**Root Cause:** pip cache returning x86_64 wheel despite ARM64 system
**Attempted Solutions:** 
- `pip uninstall` + reinstall ❌
- `--no-cache-dir --force-reinstall` ❌
**Next Solution:** `ARCHFLAGS="-arch arm64" pip install --no-binary :all:`

---

## Key Commands for New Session

### Environment Activation:
```bash
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
conda activate namma-space
```

### Current Blocker Fix:
```bash
# Fix fpsample architecture issue
pip uninstall fpsample -y
pip cache purge
ARCHFLAGS="-arch arm64" pip install --no-binary :all: --no-cache-dir fpsample
```

### Resume Training:
```bash
./resume-training.sh
```

### Check COLMAP Output:
```bash
# View registered images in Model 1
wc -l namma-space-project/.work/your-video/sparse/0/1/images.txt
# Should show: 2214
```

---

## What Works vs What Doesn't

### ✅ Working:
- Miniforge installation (ARM64-native conda)
- Python 3.10 environment activation
- COLMAP 4.1.1 installation
- FFmpeg 9.0.1 (for frame extraction only)
- Frame extraction from video
- COLMAP feature extraction (CPU-only)
- COLMAP matching (CPU-only)
- COLMAP sparse reconstruction (2,214 images)
- Web viewer code (React + Three.js)
- Node.js and npm

### ❌ Not Working:
- nerfstudio's built-in video processing (ffmpeg incompatibility)
- GPU acceleration for COLMAP (crashes on M5 Max)
- fpsample ARM64 import (current blocker)
- Actual 3D model training (blocked by fpsample)
- Web viewer launch (no model generated yet)

### ⚠️ Workarounds in Place:
- Manual frame extraction instead of `ns-process-data video`
- CPU-only COLMAP instead of GPU
- Correct flag names for COLMAP 4.1.1
- Using Model 1 instead of Model 0

---

## Critical Files

### Must Exist:
- `namma-space-project/input-videos/your-video.mov` ✅
- `namma-space-project/.work/your-video/images/*.png` ✅ (1100 files)
- `namma-space-project/.work/your-video/database.db` ✅
- `namma-space-project/.work/your-video/sparse/0/1/*.bin` ✅
- `namma-space-project/.work/your-video/sparse/0/1/*.txt` ✅

### Will Be Created After Training:
- `namma-space-project/.work/training-your-video/*/config.yml`
- `namma-space-project/output-models/your-video/*.ply` or `*.splat`
- `namma-space-project/web-app/public/models/demo.splat`

### Scripts (Ordered by Evolution):
1. `setup.sh` - Original (deprecated, has issues)
2. `setup-fixed.sh` - Fixed for M5 Max (deprecated)
3. `clean-install.sh` - Clean reinstall (use this for setup)
4. `run.sh` - Full pipeline (deprecated, has issues)
5. `run-simple.sh` - Simplified pipeline (deprecated, has issues)
6. **`resume-training.sh`** - **Use this now** ⭐

---

## Expected Final Timeline

### Already Completed (~51 minutes):
- ✅ Frame extraction: 5 min
- ✅ COLMAP feature extraction: 1.6 min
- ✅ COLMAP matching: ~30 min
- ✅ COLMAP mapper: ~17 min
- **Total:** ~51 minutes of COLMAP processing saved

### Remaining Work (~45 minutes):
1. Fix fpsample: ~5 min
2. Nerfstudio training: 30-45 min
3. Export: 5 min
4. Launch viewer: 1 min
- **Total:** ~45 minutes after fpsample fix

### Final Deliverable:
- Interactive 3D model in browser
- WASD + mouse navigation
- Photorealistic Gaussian Splatting reconstruction
- Model size: ~200-500MB

---

## Known Good Configuration

### System:
- macOS (Darwin 27.0.0)
- MacBook Pro M5 Max
- 36GB RAM, 2TB storage
- ARM64 architecture

### Software Versions:
- Miniforge3 (ARM64)
- Python 3.10.x
- COLMAP 4.1.1 (without CUDA)
- FFmpeg 9.0.1
- Node.js (latest)
- nerfstudio (latest from pip)

### COLMAP Flags (Verified Working):
```bash
# Feature extraction
colmap feature_extractor \
    --database_path database.db \
    --image_path images \
    --ImageReader.single_camera 1 \
    --ImageReader.camera_model SIMPLE_RADIAL \
    --FeatureExtraction.use_gpu 0

# Matching
colmap exhaustive_matcher \
    --database_path database.db \
    --FeatureMatching.use_gpu 0

# Mapper
colmap mapper \
    --database_path database.db \
    --image_path images \
    --output_path sparse/0

# Converter
colmap model_converter \
    --input_path sparse/0/1 \
    --output_path sparse/0/1 \
    --output_type TXT
```

---

## What to Tell in New Chat

**Short version:**
"Working on IIT Bombay Techfest 3D reconstruction project. Have completed COLMAP processing (50 min, 2,214 images registered). Blocked on fpsample ARM64 import error. Need to force ARM64 compilation, then run nerfstudio training."

**Medium version:**
"Building 3D indoor navigation system for competition using iPhone 15 Pro video → Gaussian Splatting. On M5 Max MacBook. Completed frame extraction (1100 frames) and COLMAP sparse reconstruction (2,214 images in 50 min). Web viewer ready. Currently blocked on fpsample package importing x86_64 version despite ARM64 system. Once fixed, need to run ./resume-training.sh for 30-45 min nerfstudio training, then 3D model will be ready."

**What to attach:**
- This progress document
- `resume-training.sh` script
- Error output showing fpsample architecture mismatch
- Directory listing of `namma-space-project/.work/your-video/`

---

## Success Criteria

### Round 1 (Oct 31, 2026):
- [ ] 3D model successfully generated
- [ ] Web viewer loads model
- [ ] WASD + mouse navigation works
- [ ] Model is photorealistic
- [ ] Frame rate above 30fps
- [ ] Technical abstract written (5 pages)
- [ ] Demo video recorded (3-5 min)
- [ ] Deployed to public URL

### Current Progress: ~75% Complete
- ✅ Environment setup
- ✅ Video capture
- ✅ Frame extraction
- ✅ COLMAP processing
- ✅ Web viewer code
- ⏳ Training (blocked)
- ⏳ Export (blocked)
- ⏳ Launch (blocked)

---

## Contact/References

- Competition: IIT Bombay Techfest 2026-27 "Namma Space"
- Nerfstudio docs: https://docs.nerf.studio/
- COLMAP docs: https://colmap.github.io/
- Project location: `/Users/tripathd/Downloads/Manual Library/Projects/3D`
- Conda env: `namma-space`
- Video: `your-video.mov` (14.3MB)

---

**End of Progress Document**
**Status:** 75% complete, blocked on fpsample ARM64 compilation
**Next Action:** Fix fpsample, then run `./resume-training.sh`
**Estimated Time to Completion:** ~1 hour after fpsample fix
