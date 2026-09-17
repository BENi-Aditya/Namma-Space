# 🚀 NAMMA SPACE - SIMPLE SETUP GUIDE

**IIT Bombay Techfest 2026-27 - 3D Indoor Navigation System**

---

## 📁 Project Structure (Clean & Simple)

```
namma-space-project/
│
├── input-videos/           ← PUT YOUR iPHONE VIDEOS HERE
│   └── (empty - waiting for your video)
│
├── output-models/          ← YOUR 3D MODELS APPEAR HERE
│   └── (will be created after processing)
│
└── web-app/               ← WEB VIEWER (auto-managed)
    └── (React app - don't touch)
```

---

## ⚡ How to Use (3 Simple Steps)

### **Step 1: Record Video on iPhone**
- Open Camera → Video → 4K 30fps
- Walk slowly through a room (2-3 minutes)
- Transfer to Mac (AirDrop)

### **Step 2: Put Video in Folder**
```bash
# Copy your iPhone video here:
cp ~/Downloads/your-video.mp4 "namma-space-project/input-videos/"
```

### **Step 3: Run the Magic Script**
```bash
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
./run.sh
```

**That's it! The script does EVERYTHING:**
- ✅ Processes your video
- ✅ Trains 3D model (30-90 minutes)
- ✅ Launches web viewer automatically
- ✅ Opens browser with your 3D space!

---

## 🎮 Browser Controls (After Script Finishes)

| Control | Action |
|---------|--------|
| **Click screen** | Start navigation |
| **W** | Move forward |
| **S** | Move backward |
| **A** | Move left |
| **D** | Move right |
| **Mouse** | Look around |
| **ESC** | Exit |

---

## 🔧 How It Actually Works (The Backend Magic)

### **Technology Stack:**

#### **1. Nerfstudio (The Brain)**
- **What**: Open-source 3D reconstruction framework
- **GitHub**: https://github.com/nerfstudio-project/nerfstudio
- **What it does**: Converts videos → 3D models
- **Installed when**: You ran `setup.sh`

#### **2. COLMAP (Camera Tracking)**
- **What**: Estimates camera positions from video frames
- **How**: Analyzes each frame, finds matching features, calculates camera path
- **Output**: Camera poses + sparse point cloud

#### **3. Gaussian Splatting (3D Magic)**
- **What**: State-of-the-art 3D reconstruction technique (2023)
- **Paper**: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
- **How it works**:
  - Takes your video frames + camera poses
  - Creates millions of tiny 3D "splats" (like paint splatters)
  - Each splat has color, position, size, rotation
  - Renders photorealistic views from any angle
- **Why it's amazing**: Fast, photorealistic, works great with phone videos

#### **4. React + Three.js (Web Viewer)**
- **What**: Browser-based 3D viewer
- **GitHub**: 
  - Three.js: https://github.com/mrdoob/three.js
  - React Three Fiber: https://github.com/pmndrs/react-three-fiber
  - Gaussian Splats 3D: https://github.com/mkkellogg/GaussianSplats3D
- **What it does**: Displays your 3D model in browser with WASD controls

---

## 🧠 Pipeline Breakdown (What run.sh Does)

```
iPhone Video (4K 30fps, 2-3 min)
         ↓
    [COLMAP Processing]
    - Extracts frames (every few frames)
    - Finds matching points between frames
    - Calculates camera positions
    - Time: 10-30 minutes
         ↓
    Camera Poses + Images
         ↓
    [Gaussian Splatting Training]
    - Nerfstudio "splatfacto" method
    - Creates 3D splats from video
    - Optimizes positions/colors
    - Time: 15-45 minutes
    - You can watch: localhost:7007
         ↓
    3D Model (.splat file, ~200-500MB)
         ↓
    [Export for Web]
    - Converts to web-friendly format
    - Time: 2-5 minutes
         ↓
    Final Model (in output-models/)
         ↓
    [Web Viewer Launch]
    - Copies model to web-app/
    - Starts React dev server
    - Opens browser: localhost:5173
         ↓
    🎉 YOU CAN NAVIGATE YOUR 3D SPACE!
```

---

## 📦 What Got Installed (Backend Tools)

### **1. System Tools (via Homebrew)**
```bash
brew install colmap    # Camera tracking
brew install ffmpeg    # Video processing
```

### **2. Python Environment (via Conda)**
```bash
conda create -n namma-space python=3.10
conda activate namma-space
```

### **3. AI/ML Libraries (via pip)**
```bash
pip install torch torchvision    # PyTorch (ML framework)
pip install nerfstudio            # 3D reconstruction
```

### **4. Web Stack (via npm)**
```bash
npm install react @react-three/fiber three
npm install @mkkellogg/gaussian-splats-3d
```

---

## 🎯 Which Git Repos Are We Using?

### **Cloned/Installed:**

1. **Nerfstudio** ✅
   - Repo: https://github.com/nerfstudio-project/nerfstudio
   - Installed via: `pip install nerfstudio`
   - Used for: Video → 3D model training

2. **COLMAP** ✅
   - Repo: https://github.com/colmap/colmap
   - Installed via: `brew install colmap`
   - Used for: Camera pose estimation

3. **Gaussian Splats 3D** ✅
   - Repo: https://github.com/mkkellogg/GaussianSplats3D
   - Installed via: `npm install @mkkellogg/gaussian-splats-3d`
   - Used for: Loading .splat files in browser

4. **React Three Fiber** ✅
   - Repo: https://github.com/pmndrs/react-three-fiber
   - Installed via: `npm install @react-three/fiber`
   - Used for: React + Three.js integration

### **Not Cloned (Just Using as Library):**
- Everything is installed as a package/binary
- No manual git clones needed
- All managed by package managers (brew/pip/npm)

---

## 💡 Why This Stack?

| Technology | Why We Chose It |
|------------|-----------------|
| **Nerfstudio** | Industry standard, best documentation, Apple Silicon support |
| **Gaussian Splatting** | Newest tech (2023), photorealistic, fast training |
| **React + Three.js** | Web standard, works everywhere, no installation |
| **iPhone 15 Pro** | Has LiDAR, excellent camera, everyone has one |

---

## 🔍 Where Are Files Stored?

```
After running run.sh:

namma-space-project/
│
├── input-videos/
│   └── your-room.mp4              ← Your iPhone video
│
├── output-models/
│   └── your-room/
│       └── splat.splat           ← Final 3D model (200-500MB)
│
├── .temp-processing/              ← Intermediate files
│   └── your-room/
│       ├── images/                ← Extracted frames
│       └── colmap/                ← Camera poses
│
├── .temp-training/                ← Training output
│   └── your-room/
│       └── splatfacto/
│           └── config.yml         ← Model config
│
└── web-app/
    └── public/models/
        └── demo.splat            ← Copy of model for viewer
```

---

## 🚨 Common Questions

### **Q: Do I need to download anything manually?**
**A:** No! `setup.sh` installed everything. Just run `./run.sh`

### **Q: Where does the AI training happen?**
**A:** On your MacBook M5 Max GPU. That's why it takes 30-90 minutes.

### **Q: Is this using cloud/internet?**
**A:** No! Everything runs locally on your Mac.

### **Q: What if I want to process multiple rooms?**
**A:** Put multiple videos in `input-videos/`, run `./run.sh` multiple times. It will ask which video to process.

### **Q: Can I delete temp files?**
**A:** Yes, delete `.temp-processing/` and `.temp-training/` folders. Keep `output-models/`!

---

## 🎯 Your Actual Next Step

```bash
# 1. Record video with iPhone (2-3 minutes)
# 2. AirDrop to Mac
# 3. Copy to input folder:
cp ~/Downloads/IMG_1234.mp4 "/Users/tripathd/Downloads/Manual Library/Projects/3D/namma-space-project/input-videos/my-room.mp4"

# 4. Run the magic:
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
./run.sh

# 5. Wait 30-90 minutes (go get coffee ☕)
# 6. Browser opens automatically with your 3D space! 🎉
```

---

## 📊 Expected Timeline

| Step | Time | What's Happening |
|------|------|------------------|
| Video capture | 3 min | iPhone recording |
| File transfer | 2 min | AirDrop to Mac |
| COLMAP | 10-30 min | Camera tracking |
| Training | 15-45 min | 3D model creation |
| Export | 2-5 min | Web format conversion |
| **Total** | **30-90 min** | **Fully automated** |

---

**That's it! One script, one folder, everything automated.** 🚀

Now go record your first room! 📹
