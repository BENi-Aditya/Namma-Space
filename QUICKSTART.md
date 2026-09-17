# Quick Start Guide - Namma Space

**IIT Bombay Techfest 2026-27 - 3D Indoor Navigation System**

---

## 🚀 Get Started in 5 Steps

### Step 1: Run Setup Script (15 minutes)

```bash
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
./setup.sh
```

**This installs everything you need:**
- COLMAP (camera tracking)
- ffmpeg (video processing)
- nerfstudio (3D reconstruction)
- Creates conda environment
- Sets up project structure

### Step 2: Capture Your First Room (3 minutes)

**Using iPhone 15 Pro:**
1. Open Camera app → Video mode
2. Set to **4K at 30fps**
3. Walk slowly through a room (1-2 seconds per step)
4. Record for 2-3 minutes
5. Keep camera steady, capture from multiple heights

**See [`capture_sop.md`](capture_sop.md) for detailed instructions**

### Step 3: Transfer Video to Mac

**Option A - AirDrop (Fastest):**
- Select video in Photos app on iPhone
- Share → AirDrop → Your Mac
- Save to: `data/raw-videos/`

**Option B - USB Cable:**
- Connect iPhone → Open Image Capture app
- Import to `data/raw-videos/`

### Step 4: Process Video (30-90 minutes)

```bash
# Activate conda environment
conda activate namma-space

# Process your video
./process_video.sh data/raw-videos/YOUR_VIDEO.mp4 room1

# This will:
# - Extract frames (10-30 min)
# - Run COLMAP (5-15 min)
# - Train 3D model (15-45 min)
# - Export for web (2-5 min)
```

**☕ Take a break - this takes time!**

### Step 5: View in Browser (2 minutes)

```bash
# Copy model to web viewer
cp exports/models/room1/*.splat web-viewer/public/models/demo.splat

# Install web dependencies (first time only)
cd web-viewer
npm install

# Start viewer
npm run dev
```

**🎉 Open http://localhost:5173 in browser**

---

## 🎮 Navigation Controls

| Control | Action |
|---------|--------|
| **Click screen** | Start navigation (locks pointer) |
| **W** | Move forward |
| **S** | Move backward |
| **A** | Move left |
| **D** | Move right |
| **Mouse** | Look around |
| **ESC** | Exit (unlock pointer) |

---

## 📋 Pre-Submission Checklist (Round 1)

Before Oct 31, 2026 deadline:

### Technical Deliverables
- [ ] 3D model reconstructed successfully
- [ ] Web viewer works (WASD + mouse controls)
- [ ] Deployed to public URL (GitHub Pages/Vercel)
- [ ] Code repository uploaded with README

### Documentation
- [ ] Technical Abstract PDF (max 5 pages)
  - System architecture
  - Pipeline design
  - SOP construction details
  - Technical approach
- [ ] Demo Video (3-5 minutes)
  - Show capture process
  - Display 3D web walkthrough
  - Explain key features

### Testing
- [ ] Frame rate above 30fps
- [ ] Works in Chrome, Firefox, Safari
- [ ] Model loads in under 10 seconds
- [ ] No major visual artifacts

---

## 🆘 Common Issues

### "Conda not found"
**Fix**: Install Miniconda from https://docs.conda.io/en/latest/miniconda.html

### "COLMAP failed"
**Fix**: Check video quality
- Need good lighting
- Move slower
- Ensure 70-80% frame overlap

### "Black screen in browser"
**Fix**: 
1. Check `web-viewer/public/models/demo.splat` exists
2. Open browser console for errors
3. Try different browser

### "Out of memory during training"
**Fix**: Edit `process_video.sh`, change:
```bash
--num-frames-target 300  # Reduce to 200
```

---

## 📂 Project Structure (What Got Created)

```
3D/
├── setup.sh                    ✅ Automated installation
├── process_video.sh            ✅ Video → 3D pipeline
├── capture_sop.md              ✅ iPhone capture guide
├── README.md                   ✅ Full documentation
│
├── data/
│   ├── raw-videos/             📹 Put iPhone videos here
│   └── processed/              🔧 COLMAP output
│
├── exports/
│   └── models/                 🎨 Final .splat files
│
└── web-viewer/                 🌐 React Three.js app
    ├── package.json            ✅ Dependencies
    ├── vite.config.js          ✅ Build config
    ├── public/models/          📦 Place .splat here
    └── src/
        ├── App.jsx             ✅ Main app
        ├── components/
        │   ├── Scene.jsx       ✅ 3D scene
        │   ├── Controls.jsx    ✅ WASD controls
        │   ├── GaussianSplat.jsx ✅ Model loader
        │   └── Instructions.jsx  ✅ UI overlay
```

---

## ⏱️ Timeline & Next Steps

### Today (Sept 8, 2026) ✅
- [x] Project setup complete
- [x] All code written
- [x] Documentation ready

### This Week (Sept 9-15)
- [ ] **Test first capture** - Record a room in your home
- [ ] Run complete pipeline end-to-end
- [ ] Verify web viewer works
- [ ] Time the process

### Next 3 Weeks (Sept 16 - Oct 7)
- [ ] Capture 2-3 rooms for submission
- [ ] Practice to improve quality
- [ ] Start technical abstract
- [ ] Record demo video

### Final Week (Oct 24-31)
- [ ] Polish documentation
- [ ] Deploy to public URL
- [ ] Submit before deadline
- [ ] Upload to Techfest portal

---

## 🎯 Competition Milestones

| Date | Milestone | Status |
|------|-----------|--------|
| **Sept 8** | Project setup | ✅ Done |
| **Sept 15** | First test capture | ⏳ Next |
| **Sept 30** | Practice complete | ⏳ Pending |
| **Oct 31** | Round 1 submission | 📅 Deadline |
| **Nov 10** | Round 1 results | 📅 Wait |
| **Nov 30** | Round 2 submission | 📅 Future |
| **Dec 16-17** | Finals at IIT Bombay | 🏆 Goal |

---

## 💡 Tips for Success

1. **Practice makes perfect** - Do multiple test captures before final submission
2. **Lighting is crucial** - Even lighting = better reconstruction
3. **Move slowly** - Blur ruins everything
4. **Document everything** - Take notes for your technical abstract
5. **Time yourself** - You'll need speed for Round 3 on-site

---

## 📞 Need Help?

1. Check [`README.md`](README.md) for detailed documentation
2. Review [`capture_sop.md`](capture_sop.md) for capture tips
3. Check [Nerfstudio docs](https://docs.nerf.studio/) for technical issues
4. Browser console (F12) for web viewer errors

---

## 🎉 You're Ready!

Everything is set up. Your next action:

```bash
# Start here
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"

# Run setup
./setup.sh

# Then follow Steps 2-5 above
```

**Good luck with IIT Bombay Techfest 2026-27! 🚀**

---

**Created**: September 8, 2026  
**For**: Namma Space Competition Entry
