# Record3D Capture Protocol for iPhone 15 Pro
**Version:** 1.0  
**Date:** 2026-09-29  
**For:** Namma Space 3D Indoor Navigation

---

## Overview

Record3D is an iOS app that captures:
- ✅ RGB video (up to 1080p @ 60fps)
- ✅ ARKit camera poses (6DOF tracking)
- ✅ LiDAR depth maps (iPhone 12 Pro+)
- ✅ IMU data (accelerometer + gyroscope)

Export format: `.r3d` file containing all synchronized data.

---

## Setup

### 1. Install Record3D App

**iOS App Store:**
- Search: "Record3D"
- Developer: Marek Simonik
- Free tier: Unlimited recording, USB export
- Pro tier ($20): WiFi streaming, higher quality

**For Competition:** Free tier is sufficient.

### 2. iPhone 15 Pro Settings

**Before capturing:**
1. Settings → Record3D
2. Enable "LiDAR" (must be ON)
3. Set quality: "High" (1080p)
4. Frame rate: 30 fps (matches existing videos)
5. Enable "Export ARKit poses"

---

## Capture Workflow

### Pre-Capture Checklist
- [ ] iPhone fully charged (>80%)
- [ ] Good lighting (avoid direct sunlight, dark shadows)
- [ ] Clear space (remove people, moving objects)
- [ ] Record3D app settings verified

### Capture Procedure

**Same as existing SOP** (`docs/capture_sop.md`):

1. **Start Recording**
   - Open Record3D
   - Tap red record button
   - Hold iPhone at eye level (~1.6m)

2. **Spiral Scan Pattern**
   - **Pass 1 (Eye Level):** Walk perimeter, camera rotating inward
   - **Pass 2 (Low Level):** Walk perimeter at ~1m height
   - **Pass 3 (High Level):** Walk perimeter at ~2m height (if reachable)
   - Move slowly: 1-2 seconds per step
   - Smooth motion (no jerky movements)

3. **Stop Recording**
   - Tap stop button
   - App automatically saves `.r3d` file

### Target Metrics (Same as Before)
- Duration: 30-60 seconds per pass
- Total frames: 250-400 frames
- Coverage: All walls, corners, POI locations
- Tracking quality: ARKit shows "Normal" or "Limited" (not "Not Available")

---

## Export to Mac

### Via USB Cable (Free Tier)

1. Connect iPhone to Mac via Lightning/USB-C cable
2. Open Record3D app on iPhone
3. Tap the recording you want to export
4. Tap "Export" → "Export via USB"
5. On Mac:
   ```bash
   # Record3D will appear as mounted volume
   # Copy .r3d file to project
   cp /Volumes/Record3D/*.r3d data/raw-captures/
   ```

### Via WiFi (Pro Only)
- Not needed for competition
- Useful for live streaming to Mac during capture

---

## File Structure

### .r3d File Contents

```
recording.r3d
├── metadata.json          # Recording settings, device info
├── rgbd/
│   ├── 0000.jpg          # RGB frame 0
│   ├── 0000.depth        # LiDAR depth map 0
│   ├── 0001.jpg
│   ├── 0001.depth
│   └── ...
├── poses/
│   └── arkit_poses.json  # Camera pose per frame (4x4 matrix)
└── intrinsics.json       # Camera calibration
```

---

## Integration with Pipeline

### Conversion to Nerfstudio Format

```bash
# Extract .r3d to standard format
python experiments/spatial-engine-v2/capture/r3d_to_nerfstudio.py \
  --r3d data/raw-captures/recording.r3d \
  --output data/processed/my-room/
```

Output:
```
data/processed/my-room/
├── images/               # Extracted RGB frames
│   ├── frame_0000.jpg
│   ├── frame_0001.jpg
│   └── ...
├── depths/               # LiDAR depth maps (optional)
│   ├── frame_0000.npy
│   └── ...
├── transforms.json       # Nerfstudio format (ARKit poses)
└── metadata.json         # Capture quality metrics
```

### Advantages Over Standard Video

| Feature | Standard Video | Record3D |
|---------|---------------|----------|
| RGB frames | ✅ | ✅ |
| Camera poses | ❌ (needs COLMAP) | ✅ (ARKit) |
| Depth maps | ❌ | ✅ (LiDAR) |
| Pose reliability | 🟡 (COLMAP fragile) | ✅ (ARKit robust) |
| Low-texture handling | ❌ (COLMAP fails) | ✅ (ARKit IMU fusion) |
| Registration rate | 0.25% (documented) | ~95% (expected) |

---

## Quality Validation

### Automatic Checks

After export, run quality validation:
```bash
python scripts/validation/validate_capture.py \
  --transforms data/processed/my-room/transforms.json
```

Checks:
- Frame count: 250-400 ✅
- Pose continuity: <0.5m jumps ✅
- Depth coverage: ≥80% valid pixels ✅
- Tracking confidence: ≥90% "Normal" ✅
- Frame overlap: ≥60% (feature matching) ✅

### Manual Review

Record3D app shows live tracking quality:
- 🟢 Green: "Normal" tracking (good)
- 🟡 Yellow: "Limited" tracking (acceptable)
- 🔴 Red: "Not Available" (bad, re-capture)

If you see red during capture → stop and re-capture that section.

---

## Comparison: Record3D vs Enhanced COLMAP

### When to Use Record3D
- ✅ New captures (best quality)
- ✅ Low-texture environments (long corridors)
- ✅ Need ground truth poses for validation
- ✅ Want LiDAR depth for spatial truth layer

### When to Use Enhanced COLMAP
- ✅ Existing videos (already captured)
- ✅ No iPhone available (backup method)
- ✅ Need loop closure detection (COLMAP better)
- ✅ Higher resolution than Record3D (4K vs 1080p)

### Hybrid Approach (Recommended)
1. Use Record3D for primary capture (robust ARKit poses)
2. Run COLMAP on same frames (detect loop closures)
3. Fuse both: ARKit continuous tracking + COLMAP drift correction
4. Result: Best of both worlds

---

## Troubleshooting

### "LiDAR not available"
- Check: iPhone model (need 12 Pro or newer)
- Check: Record3D app settings → LiDAR enabled

### "Tracking quality poor"
- More lighting (avoid dark areas)
- Add visual features (posters, furniture)
- Slower movement (give ARKit time to track)

### "Export takes too long"
- Normal: ~1 minute per 30 seconds of recording
- Use USB cable (faster than WiFi)

### "File size too large"
- 1 minute recording ≈ 200-300 MB
- Acceptable (LiDAR depth is large)
- Can downsample frames after export if needed

---

## Next Steps

1. **Capture Test Scene:**
   - Use Record3D to capture 30-second test (your desk/room)
   - Export .r3d file to Mac
   - Verify all data present

2. **Build Parser:**
   - Implement `r3d_to_nerfstudio.py` converter
   - Test on sample .r3d file
   - Validate output format

3. **Compare with COLMAP:**
   - Run enhanced COLMAP on same frames
   - Compare pose quality (alignment error)
   - Document which is better for what scenarios

4. **Update SOP:**
   - Merge Record3D workflow into `docs/capture_sop.md`
   - Add quality validation steps
   - Document acceptance criteria

---

**Status:** Ready to implement  
**Blocker:** Need to capture test .r3d file with iPhone

---

*This protocol ensures we can capture ARKit+LiDAR data per ARCHITECTURE.md Layer 1 requirements.*
