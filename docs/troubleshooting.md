# Namma Space - Troubleshooting Guide

**Last Updated:** September 9, 2026

---

## Quick Diagnosis

Run the preflight check first:
```bash
./preflight-check.sh
```

This will identify exactly what's missing or misconfigured.

---

## Common Issues & Solutions

### 1. COLMAP Crashes (Abort trap: 6)

**Symptoms:**
```
./run-simple.sh: line 69: 91621 Abort trap: 6
```

**Root Cause:** GPU acceleration failing on macOS

**Solution:** ✅ FIXED in latest `run-simple.sh`
- Now uses `--FeatureExtraction.use_gpu 0` (correct CPU-only flag)
- If still crashes, check COLMAP version with `colmap -h`

**Manual Fix:**
```bash
# Feature extraction with CPU only
colmap feature_extractor \
    --database_path database.db \
    --image_path images \
    --FeatureExtraction.use_gpu 0
```

---

### 2. FFmpeg Version Errors

**Symptoms:**
```
Unrecognized option 'vsync'
Error splitting the argument list: Option not found
```

**Root Cause:** FFmpeg 9.x removed `-vsync` flag that nerfstudio uses

**Solution:** ✅ FIXED in latest `run-simple.sh`
- Script extracts frames manually without using nerfstudio's video processor
- Bypasses ffmpeg compatibility issues entirely

---

### 3. Conda Environment Not Activating

**Symptoms:**
```
ModuleNotFoundError: No module named 'nerfstudio'
```

**Root Cause:** Environment not properly activated or nerfstudio not installed

**Solution:**
```bash
# Check if environment exists
conda env list | grep namma-space

# If missing, run clean install
./clean-install.sh

# If exists, activate and check
conda activate namma-space
python -c "import nerfstudio; print('✓ Works!')"

# If import fails, reinstall
pip install nerfstudio
```

---

### 4. Wrong COLMAP Flags

**Symptoms:**
```
Failed to parse options - unrecognised option '--SiftExtraction.gpu_index'
```

**Root Cause:** Using wrong flag name for COLMAP 4.1.1

**Solution:** ✅ FIXED in latest `run-simple.sh`

**Correct flags for COLMAP 4.1.1:**
- ✅ `--FeatureExtraction.use_gpu 0` (not `--SiftExtraction.use_gpu`)
- ✅ `--SiftMatching.use_gpu 0` (not `--SiftMatching.gpu_index`)

---

### 5. Video Not Found

**Symptoms:**
```
ERROR: Video not found
Expected: namma-space-project/input-videos/your-video.mov
```

**Solution:**
```bash
# Copy your iPhone video to the correct location
cp ~/Downloads/YOUR_VIDEO.mov "namma-space-project/input-videos/your-video.mov"

# Or any .mp4/.mov file will work
cp ~/Downloads/IMG_1234.mp4 "namma-space-project/input-videos/your-video.mov"
```

---

### 6. Training Takes Too Long / Crashes

**Symptoms:**
- Training runs for hours
- Out of memory errors
- System freezes

**Solutions:**

**Option A: Reduce iterations**
```bash
# Edit run-simple.sh, line 116
--max-num-iterations 20000  # Instead of 30000
```

**Option B: Use CPU training**
```bash
# Add to ns-train command
--pipeline.model.device cpu
```

**Option C: Reduce frame count**
```bash
# Edit run-simple.sh, line 103 (ffmpeg command)
# Change mod(n\,4) to mod(n\,6)
-vf "select='not(mod(n\,6))'"  # ~200 frames instead of 300
```

---

### 7. Web Viewer Shows Black Screen

**Symptoms:**
- Browser opens to localhost:5173
- Screen is black, no 3D model visible

**Solutions:**

**Check 1: Model file exists**
```bash
ls -lh namma-space-project/web-app/public/models/demo.splat
```

**Check 2: Browser console errors**
- Press F12 in browser
- Check Console tab for errors
- Common issue: File too large (>500MB)

**Check 3: Try different browser**
- Chrome/Edge: Best compatibility
- Firefox: Good
- Safari: May have issues

**Manual fix:**
```bash
# Re-copy the model
SPLAT=$(find namma-space-project/output-models -name "*.ply" -o -name "*.splat" | head -n 1)
cp "$SPLAT" namma-space-project/web-app/public/models/demo.splat

# Restart viewer
cd namma-space-project/web-app
npm run dev
```

---

### 8. COLMAP: "No good matches"

**Symptoms:**
```
Insufficient matches for sparse reconstruction
```

**Root Cause:** Not enough visual features in video (blank walls, poor lighting, too fast movement)

**Solutions:**

1. **Re-record video with better technique:**
   - Move slower (1-2 seconds per meter)
   - Better lighting (turn on all lights)
   - More textured surfaces (avoid blank walls)
   - 70-80% frame overlap

2. **Try different camera model:**
```bash
# Edit run-simple.sh, line 131
--ImageReader.camera_model PINHOLE  # Instead of SIMPLE_RADIAL
```

3. **Increase frame count:**
```bash
# Edit run-simple.sh, line 103
-vf "select='not(mod(n\,3))'"  # Extract every 3rd frame instead of 4th
```

---

## Performance Optimization

### Faster Processing

**Reduce COLMAP time (20-30 min → 10-15 min):**
```bash
# Use sequential matching instead of exhaustive
colmap sequential_matcher \
    --database_path database.db
```

**Reduce training time (30-45 min → 15-25 min):**
```bash
# Lower iterations
--max-num-iterations 15000

# Use fewer frames (~150-200)
```

### Better Quality

**Higher quality model (training time: 45-60 min):**
```bash
--max-num-iterations 40000
--pipeline.model.cull-alpha-thresh 0.003
```

**More frames for detail:**
```bash
# Extract every 2nd frame (~500 frames)
-vf "select='not(mod(n\,2))'"
```

---

## System Requirements Check

### Minimum Requirements
- ✅ macOS Sonoma or later
- ✅ 8GB RAM (16GB+ recommended)
- ✅ 10GB free disk space
- ✅ Apple Silicon (M1/M2/M3/M4/M5)

### Verify Your System
```bash
# Check macOS version
sw_vers

# Check RAM
sysctl hw.memsize | awk '{print $2/1024/1024/1024 " GB"}'

# Check disk space
df -h .

# Check processor
sysctl -n machdep.cpu.brand_string
```

---

## Getting Help

### Debug Mode

Run with verbose output:
```bash
# Edit run-simple.sh
# Remove "2>&1 | grep" filters to see full output
# For example, line 107:
colmap feature_extractor ... # (remove the grep at the end)
```

### Check Logs

```bash
# COLMAP logs
cat namma-space-project/.work/your-video/colmap.log

# Nerfstudio logs
cat namma-space-project/.work/training-your-video/*/nerfstudio_models/*/config.yml
```

### Report Issue

If you still have issues, collect this info:
1. Output of `./preflight-check.sh`
2. macOS version: `sw_vers`
3. Error message (full text)
4. Video size: `ls -lh namma-space-project/input-videos/`

---

## Success Checklist

Before running `./run-simple.sh`, verify:
- ✅ `./preflight-check.sh` passes all checks
- ✅ Video is 2-5 minutes long
- ✅ Video has good lighting and movement
- ✅ At least 10GB disk space available
- ✅ No other heavy apps running

Expected timeline: **60-90 minutes total**

---

**Current Status (Sept 9, 2026):**
All known issues are fixed in the latest `run-simple.sh`. The script should run successfully from start to finish without any errors.
