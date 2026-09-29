# Namma Space: 3D Indoor Navigation Project
**Your Guide to Understanding the Technology**

---

## What Is This Project?

**Namma Space** is a system that converts iPhone videos of indoor spaces into interactive 3D models that you can explore on a website. It's like Google Street View, but for indoor spaces like buildings, rooms, and hallways — and you create it just by walking around with your phone's camera.

### The Goal
Create a 3D indoor navigation system for IIT Bombay's Techfest 2026-27 competition where users can:
- Explore buildings virtually in 3D
- Navigate indoor spaces from their browser
- See photorealistic reconstructions (not just flat images)

### What Makes It Cool?
Instead of needing expensive 3D scanners or special equipment, you just:
1. Record a video walking through a space with your iPhone
2. Run some software on your laptop
3. Get a fully interactive 3D model you can explore with keyboard and mouse

---

## How Does It Work? (Simple Version)

Think of it like this:

### Step 1: Recording (You with iPhone)
- Walk through a room/building with your iPhone recording video
- Move slowly and steadily
- Make sure there's good lighting
- **Result:** A video file (like `1.mp4`)

### Step 2: Breaking It Down (Computer Processing)
- Your computer takes that video and extracts individual frames (like snapshots)
- Instead of 4857 frames from your video, it picks ~350 frames (enough detail, not too much)
- Shrinks them from 4K to 1080p (still high quality, but manageable)
- **Result:** Hundreds of individual photos from your video

### Step 3: Understanding the Space (COLMAP)
This is where the magic happens! A program called **COLMAP** looks at all those photos and figures out:
- Where was your camera when you took each photo?
- What direction were you facing?
- How do all these images relate to each other in 3D space?

It's like solving a huge puzzle — finding matching features (edges, corners, textures) across photos to build a 3D understanding of the room.

**Result:** A "sparse point cloud" — thousands of 3D points showing where walls, objects, and features are in space.

### Step 4: Creating the 3D Model (NeRF Training)
Now comes the AI part. A technique called **Neural Radiance Fields (NeRF)** uses:
- All those camera positions
- All those images
- The 3D structure from COLMAP

And it trains an AI model to understand: "If I'm standing at position X looking in direction Y, what should I see?"

The AI learns what the space looks like from EVERY possible angle — even angles you never filmed!

**Result:** A trained model that can generate photorealistic views from any position.

### Step 5: Viewing It (Web Browser)
The final model loads in your web browser using Three.js (a 3D graphics library). You can:
- Move around with WASD keys (like a video game)
- Look around with your mouse
- Explore the space as if you're really there

---

## The Technology Stack (What Software Does What)

### 1. **FFmpeg** (Frame Extraction)
- **What it does:** Converts your video into individual image frames
- **Why it matters:** Videos are continuous, but we need discrete photos to analyze
- **Your setup:** FFmpeg 9.0.1

### 2. **COLMAP** (3D Reconstruction)
- **What it does:** Figures out the 3D structure of your space from 2D photos
- **How it works:**
  - **Feature Extraction:** Finds interesting points in each image (corners, edges, textures)
  - **Feature Matching:** Finds the same points across different images
  - **Camera Pose Estimation:** Calculates where you were standing and which direction you faced for each photo
  - **Sparse Reconstruction:** Creates a 3D point cloud showing the structure
- **Why it's challenging:** Running on CPU (no NVIDIA GPU), so it takes 30-45 minutes
- **Your setup:** COLMAP 4.1.1, CPU-only mode

### 3. **Nerfstudio** (AI Training Framework)
- **What it does:** Provides tools to train NeRF (Neural Radiance Fields) models
- **Two methods available:**
  - **Splatfacto:** Uses Gaussian Splatting (requires GPU, doesn't work on your Mac)
  - **Nerfacto:** Uses Neural Radiance Fields (works on CPU, what we're using)
- **Training process:**
  - Iterates 15,000 times (for competition quality)
  - Each iteration: AI guesses what a view should look like → compares to real photo → adjusts
  - Gets better and better at predicting what you'd see from any angle
- **Your setup:** Nerfstudio with nerfacto method, Python 3.10

### 4. **PyTorch** (AI Framework)
- **What it does:** The deep learning library that powers the neural network training
- **Your setup:** PyTorch 2.14.0, CPU-only (no MPS/Metal GPU support despite M5 Max)
- **Why CPU-only:** PyTorch says MPS is available but it doesn't actually work on your system

### 5. **Three.js** (Web Viewer)
- **What it does:** Renders the final 3D model in your web browser
- **Uses:** WebGL (hardware-accelerated 3D graphics in browsers)
- **Controls:** Keyboard (WASD) + Mouse (look around)

---

## The Problem You Were Facing

### What Went Wrong?
When you tried training on your new competition video (`1.mp4`), COLMAP only recognized **2 out of 810 frames**. 

### Why Did This Happen?
Your video was:
- **4K resolution** (3840 × 2160 pixels) — each frame is 5-6 MB
- **~4,900 frames** total
- The script extracted **810 frames at full 4K** → **4.6 GB of images**

**COLMAP couldn't handle it.** Too much data, too high resolution. It's like trying to solve an impossible jigsaw puzzle with 10,000 pieces when you only have time for 300.

### The Solution
The new script (`train-competition.sh`) fixes this by:
1. **Fewer frames:** ~350 frames instead of 810
2. **Lower resolution:** 1080p instead of 4K (still high quality!)
3. **Smarter matching:** Sequential matching (optimized for videos) instead of exhaustive matching
4. **Better settings:** 15,000 training iterations with high quality settings

---

## The Pipeline (Step-by-Step Process)

```
[iPhone Video]
      ↓
[FFmpeg Frame Extraction] → 350 frames @ 1080p
      ↓
[COLMAP Feature Extraction] → Find interesting points in each image
      ↓
[COLMAP Feature Matching] → Match points across images
      ↓
[COLMAP Camera Estimation] → Figure out camera positions
      ↓
[COLMAP Reconstruction] → Build 3D point cloud
      ↓
[Nerfstudio Processing] → Convert to training format
      ↓
[NeRF Training (15,000 iterations)] → Train AI model (8-12 hours)
      ↓
[Export Model] → Final .ckpt file
      ↓
[Web Viewer] → Interactive 3D in browser
```

---

## Key Concepts Explained

### What Is a Neural Radiance Field (NeRF)?

Imagine teaching an AI to answer this question:  
**"If I'm standing at position (X, Y, Z) looking in direction (θ, φ), what color should I see?"**

A NeRF is a neural network that learns this function:
- **Input:** 3D position + viewing direction
- **Output:** Color (RGB) + density (is there something here?)

After training, it can generate photorealistic images from ANY viewpoint — even ones you never filmed!

### What Is Gaussian Splatting?

An alternative to NeRF that represents the scene as millions of tiny 3D "splats" (like paint splatters). Each splat has:
- Position
- Color
- Size
- Orientation

**Pros:** Faster rendering, smoother real-time performance  
**Cons:** Requires GPU (doesn't work on your Mac's CPU)

### CPU vs GPU Training

**GPU (Graphics Processing Unit):**
- Specialized for parallel math operations
- 100-1000x faster for AI training
- Your Mac has Metal GPU (M5 Max) but PyTorch/gsplat can't use it

**CPU (Central Processing Unit):**
- General-purpose computing
- Slower for AI training but still works
- Your M5 Max CPU is powerful (ARM64, 8 cores)
- Training takes 8-12 hours instead of 30-60 minutes

---

## Your Hardware & Software Setup

### Hardware
- **Computer:** MacBook Pro M5 Max
- **RAM:** 36 GB
- **CPU:** Apple Silicon ARM64, 8 performance cores
- **GPU:** Metal GPU (not usable for this project)
- **Camera:** iPhone 15 Pro (4K HEVC video)

### Software
- **OS:** macOS 27 (Darwin 27.0.0)
- **Python:** 3.10 (Miniforge3, ARM64-native)
- **Conda Environment:** `namma-space`
- **FFmpeg:** 9.0.1
- **COLMAP:** 4.1.1
- **PyTorch:** 2.14.0 (CPU-only)
- **Nerfstudio:** Latest version with nerfacto support

### Why These Choices?
- **Python 3.10:** Best compatibility with Nerfstudio
- **ARM64-native:** Uses your Mac's native architecture (not Intel emulation)
- **CPU-only:** Because GPU acceleration doesn't work on your system

---

## Timeline & Expectations

### For Your Competition Video (`1.mp4`):

**Phase 1: Frame Extraction**  
- **Time:** ~2 minutes
- **Result:** 350 frames at 1080p in `namma-space-project/.work/1-competition/images/`

**Phase 2: COLMAP Reconstruction**  
- **Time:** 30-45 minutes
- **Result:** Camera poses and 3D point cloud
- **What you'll see:** Progress messages showing images being registered

**Phase 3: NeRF Training**  
- **Time:** 8-12 hours
- **Iterations:** 15,000
- **Speed:** ~20-30 steps per minute on CPU
- **Monitoring:** View progress at http://localhost:7007

**Total Time:** ~9-13 hours from start to finish

### Quality Settings (Competition Mode)
- **Frames:** 350 (high detail)
- **Resolution:** 1080p (optimal quality/performance)
- **Iterations:** 15,000 (professional quality)
- **Ray batch size:** 4,096 (more rays = better quality)
- **Samples per ray:** 64 (more samples = smoother rendering)

---

## How to Learn More

### 1. Understanding NeRF
**Best Resource:** 
- Original paper: "NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis" (Mildenhall et al., 2020)
- YouTube: Search "NeRF explained" — 3Blue1Brown style explanations
- Website: https://www.matthewtancik.com/nerf

**What to focus on:**
- Volume rendering
- Ray marching
- Neural networks for 3D

### 2. Understanding COLMAP
**Resources:**
- Official docs: https://colmap.github.io/
- YouTube: "Structure from Motion explained"
- Key concepts: Feature matching, bundle adjustment, sparse reconstruction

**What to focus on:**
- How cameras capture 3D → 2D projections
- Triangulation (finding 3D points from 2D matches)
- SIFT features (Scale-Invariant Feature Transform)

### 3. Understanding Gaussian Splatting
**Resources:**
- Paper: "3D Gaussian Splatting for Real-Time Radiance Field Rendering" (2023)
- Website: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
- GitHub: https://github.com/graphdeco-inria/gaussian-splatting

### 4. Nerfstudio Documentation
**Official Docs:** https://docs.nerf.studio/
- Installation guides
- Method comparisons (nerfacto vs splatfacto vs others)
- Training tips
- Export options

### 5. Computer Vision Basics
**Free Course:** 
- Stanford CS231n: Convolutional Neural Networks for Visual Recognition
- YouTube lecture series available

**Key Topics:**
- Camera models
- Image features
- 3D geometry
- Neural networks

### 6. Three.js (Web 3D)
**Official Site:** https://threejs.org/
- Examples and documentation
- Learn WebGL basics
- 3D rendering in browsers

---

## Troubleshooting Quick Reference

### Problem: COLMAP registers too few images
**Solution:** 
- Use fewer frames (~300-400)
- Lower resolution (1080p)
- Better lighting when recording
- Slower camera movement

### Problem: Training is too slow
**Current:** 8-12 hours on CPU  
**Options:**
- Reduce iterations (10,000 instead of 15,000)
- Reduce ray batch size (3,072 instead of 4,096)
- Use fewer frames (250 instead of 350)

### Problem: Model quality is poor
**Solutions:**
- More frames (400 instead of 350)
- More iterations (20,000 instead of 15,000)
- Better video recording technique
- Check COLMAP registered most frames

### Problem: Web viewer shows black screen
**Causes:**
- Model file too large (>500 MB)
- Browser compatibility (use Chrome)
- File didn't copy correctly

---

## Competition Tips

### Recording the Best Video
1. **Lighting:** Turn on ALL lights, open curtains
2. **Speed:** Walk SLOWLY (1-2 seconds per meter)
3. **Coverage:** Walk every path, look in every direction
4. **Overlap:** Keep 70-80% of frame overlapping between shots
5. **Stability:** Hold phone steady, smooth movements
6. **Duration:** 2-5 minutes is ideal

### Getting Best Quality
1. **More frames:** 350-400 frames
2. **More iterations:** 15,000-20,000
3. **Good COLMAP reconstruction:** Make sure 80%+ of frames are registered
4. **Monitor training:** Watch PSNR score increase (higher = better)

### Presenting Your Model
1. **Web viewer:** Interactive navigation in browser
2. **Screenshots:** Capture key views
3. **Video flythrough:** Record screen while navigating
4. **Comparison:** Before/after, or your video vs 3D model

---

## Files & Directories Explained

```
namma-space-project/
├── input-videos/
│   └── 1.mp4                          # Your competition video (772 MB)
│
├── .work/
│   ├── 1-competition/                 # New processing directory
│   │   ├── images/                    # Extracted frames (1080p)
│   │   ├── images_2/                  # Half resolution
│   │   ├── images_4/                  # Quarter resolution
│   │   ├── images_8/                  # Eighth resolution
│   │   ├── colmap/                    # COLMAP reconstruction
│   │   │   ├── database.db           # Feature database
│   │   │   └── sparse/0/             # 3D reconstruction
│   │   ├── transforms.json           # Nerfstudio format
│   │   └── sparse_pc.ply             # Point cloud
│   │
│   └── training-competition/         # Training outputs
│       └── 1-competition/
│           └── nerfacto/
│               └── 2026-09-22_*/
│                   ├── config.yml    # Model configuration
│                   └── nerfstudio_models/
│                       └── step-*.ckpt  # Trained models
│
└── web-app/                          # Browser viewer
    ├── public/models/
    │   └── demo.splat               # Final model for viewing
    └── src/                         # React + Three.js code
```

---

## The Math (For the Curious)

### Volume Rendering Equation (NeRF)
The color you see from a ray is:

```
C(r) = ∫ T(t) · σ(t) · c(t) dt
```

Where:
- `C(r)` = final color along ray `r`
- `T(t)` = accumulated transmittance (how much light made it this far)
- `σ(t)` = volume density (is there something here?)
- `c(t)` = color at this point
- `t` = distance along ray

**In plain English:**  
"The color you see is the sum of all the colors along the ray, weighted by how dense each point is and how much light could reach it."

### Camera Projection (COLMAP)
Converting 3D world point to 2D image:

```
[u, v, 1]ᵀ = K · [R | t] · [X, Y, Z, 1]ᵀ
```

Where:
- `[u, v]` = pixel coordinates
- `K` = camera intrinsics (focal length, principal point)
- `[R | t]` = camera rotation and translation (where you're standing and looking)
- `[X, Y, Z]` = 3D world point

**In plain English:**  
"To find where a 3D point appears in your photo, multiply it by your camera's properties and your position/direction."

---

## Next Steps

### Immediate Actions
1. **Run the training script:**
   ```bash
   ./train-competition.sh
   ```

2. **Monitor progress:**
   - Open http://localhost:7007 once training starts
   - Watch iteration count and PSNR score

3. **Wait patiently:**
   - Let it run overnight (8-12 hours)
   - Don't close laptop lid (set "Prevent sleep" in System Preferences)

### After Training
1. **View the model:**
   ```bash
   ns-viewer --load-config <path-to-config.yml>
   ```

2. **Export for web:**
   - Model is already in training directory
   - Copy to web-app for browser viewing

3. **Practice presenting:**
   - Navigate smoothly
   - Show key areas
   - Explain the technology

---

## Glossary

**3D Reconstruction:** Building a 3D model from 2D images  
**Bundle Adjustment:** Optimizing camera poses and 3D points together  
**Camera Intrinsics:** Internal camera properties (focal length, principal point)  
**Camera Extrinsics:** Camera position and orientation in 3D space  
**COLMAP:** Structure-from-Motion software for 3D reconstruction  
**Feature Matching:** Finding the same visual features across multiple images  
**Gaussian Splatting:** 3D representation using oriented ellipsoids  
**Neural Radiance Field (NeRF):** AI model that learns 3D scenes  
**Point Cloud:** Set of 3D points representing a surface  
**PSNR:** Peak Signal-to-Noise Ratio (quality metric, higher = better)  
**Ray Marching:** Stepping along a ray to sample a 3D volume  
**SIFT:** Scale-Invariant Feature Transform (feature detection algorithm)  
**Sparse Reconstruction:** Initial 3D structure with relatively few points  
**Structure from Motion (SfM):** Computing 3D structure from camera motion  
**Volume Rendering:** Rendering technique for semi-transparent 3D volumes  

---

## Final Notes

This project combines:
- **Computer Vision** (understanding images and 3D space)
- **Machine Learning** (training neural networks)
- **Graphics** (rendering 3D scenes)
- **Web Development** (making it interactive in browsers)

You're essentially teaching a computer to understand a 3D space just by looking at it from different angles — then letting it show you views you never filmed!

**Good luck with Techfest 2026-27!** 🚀

---

*Last Updated: September 22, 2026*  
*Project: Namma Space - 3D Indoor Navigation*  
*Competition: IIT Bombay Techfest 2026-27*
