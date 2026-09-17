# iPhone 15 Pro Capture SOP (Standard Operating Procedure)
## Namma Space - IIT Bombay Techfest 2026-27

This document provides detailed instructions for capturing indoor spaces using iPhone 15 Pro for optimal 3D reconstruction quality.

---

## Pre-Capture Checklist

### Environment Preparation
- ✅ Clean and organize the space (remove clutter, close cabinet doors)
- ✅ Ensure even lighting throughout (turn on all lights, open blinds evenly)
- ✅ Avoid harsh shadows and direct sunlight through windows
- ✅ Remove or minimize reflective surfaces (mirrors, glass tables)
- ✅ Check for any people/pets that might move during capture

### iPhone Settings
- ✅ Fully charge iPhone or have charger ready (2-3 min video per room)
- ✅ Clear storage space (expect 500MB-2GB per room video)
- ✅ Disable notifications (turn on Do Not Disturb)
- ✅ Lock exposure and focus during capture
- ✅ Clean camera lenses

### Camera App Settings
1. Open **Camera** app
2. Select **Video** mode
3. Tap settings icon (top right)
4. Set resolution: **4K at 30 fps** (recommended)
   - Alternative: **1080p at 60 fps** (for faster processing)
5. Keep **HDR** and **Stabilization** ON
6. Disable **ProRes** (creates huge files, not needed)

---

## Capture Technique

### Movement Pattern

**The "Spiral Scan" Method:**

1. **Start at entrance/doorway**
   - Stand still for 2-3 seconds
   - Record entrance clearly

2. **First pass - Eye level (standing)**
   - Walk slowly along walls (1-2 seconds per step)
   - Keep 1-2 meters from walls
   - Pan camera smoothly left-right while moving forward
   - Stop at corners for 2 seconds, capture 360° view
   - Complete full perimeter

3. **Second pass - High angle**
   - Walk same path at eye level
   - Tilt camera UP 30-45° to capture ceiling
   - Focus on ceiling-wall transitions

4. **Third pass - Low angle**
   - Walk same path at waist height
   - Tilt camera DOWN 30-45° to capture floor
   - Focus on floor-wall transitions

5. **Center capture**
   - Stand in room center
   - Slowly rotate 360° (take 20-30 seconds)
   - Capture at eye level, then high, then low

6. **Detail passes (important areas)**
   - Capture any important features up close
   - Furniture, fixtures, decorative elements
   - Multiple angles for each important object

### Timing Guidelines

| Room Size | Video Duration | Expected Coverage |
|-----------|----------------|-------------------|
| Small (bathroom, closet) | 1-2 minutes | 500-800 frames |
| Medium (bedroom, office) | 2-3 minutes | 1000-1500 frames |
| Large (living room, hall) | 3-5 minutes | 2000-3000 frames |
| Very Large (open floor plan) | 5-7 minutes | 3500-4500 frames |

### Critical Rules

**DO:**
- ✅ Move SLOWLY and steadily (1-2 seconds per meter)
- ✅ Maintain 70-80% overlap between frames
- ✅ Capture from multiple heights (floor, eye, ceiling)
- ✅ Stop at corners and important features
- ✅ Keep camera as level as possible
- ✅ Pan smoothly, avoid jerky movements
- ✅ Ensure even lighting throughout
- ✅ Capture all areas you want navigable

**DON'T:**
- ❌ Move too fast (causes motion blur)
- ❌ Spin rapidly (causes blur and poor reconstruction)
- ❌ Record only from one height
- ❌ Skip corners or behind furniture
- ❌ Have inconsistent lighting (don't turn lights on/off mid-capture)
- ❌ Have people moving in frame
- ❌ Capture through windows (blowout and reflections)
- ❌ Record with shaky hands (use both hands)

---

## Advanced Techniques

### Using LiDAR (Optional but Recommended)

**Record3D App ($30 on App Store):**
1. Download and install Record3D
2. Open app, select **EXR + RGB** mode
3. Capture same movement pattern as above
4. Export RGB video + depth data
5. Provides depth priors for better reconstruction

**Benefits:**
- Better reconstruction in low-texture areas
- More accurate depth estimation
- Faster convergence during training

### Multi-Room Capture Strategy

For entire apartments/houses:

1. **Capture each room individually** (easier to manage)
2. **Include doorways** in adjacent room captures (for alignment)
3. **Maintain consistent lighting** across all captures
4. **Number videos sequentially** (room1.mp4, room2.mp4, etc.)
5. **Create simple floor plan sketch** (helps with POI placement later)

---

## After Capture

### Immediate Checks

**Review footage on iPhone:**
1. Watch entire video at 2x speed
2. Check for:
   - ❌ Motion blur (too fast movement)
   - ❌ Lighting changes mid-capture
   - ❌ People/pets in frame
   - ❌ Missing coverage of important areas

**If ANY issues found:** Re-capture immediately while setup is fresh

### File Transfer

**Option 1: AirDrop (Recommended for speed)**
```bash
# iPhone -> Mac via AirDrop
# Select video in Photos app
# Share -> AirDrop -> Your Mac
# File appears in Downloads folder
```

**Option 2: USB Cable**
```bash
# Connect iPhone to Mac
# Open Image Capture app
# Select videos
# Import to: namma-space/data/raw-videos/
```

**Option 3: iCloud Photos**
```bash
# Upload to iCloud Photos from iPhone
# Download on Mac from Photos app
# Export to: namma-space/data/raw-videos/
```

### File Organization

```
namma-space/
└── data/
    └── raw-videos/
        ├── home_living_room_2026-09-08.mp4
        ├── home_bedroom_2026-09-08.mp4
        ├── home_kitchen_2026-09-08.mp4
        └── capture_notes.txt          # Notes about each capture
```

**capture_notes.txt format:**
```
home_living_room_2026-09-08.mp4
- Duration: 3m 24s
- Lighting: Natural (windows) + ceiling lights
- Issues: Slight shadow from couch, otherwise good
- POIs: TV area, couch, bookshelf, entrance

home_bedroom_2026-09-08.mp4
- Duration: 2m 15s
- Lighting: All artificial (evening capture)
- Issues: None
- POIs: Bed, desk, closet door, window
```

---

## Troubleshooting Common Issues

### Motion Blur
**Problem:** Video looks blurry when paused  
**Solution:** Move slower, use stabilization, ensure good lighting

### Poor Coverage
**Problem:** COLMAP fails or reconstruction has holes  
**Solution:** Ensure 70-80% overlap, capture from multiple angles, don't skip areas

### Lighting Inconsistencies
**Problem:** Parts of reconstruction are too bright/dark  
**Solution:** Use consistent lighting throughout, avoid windows in frame, enable HDR

### Reflective Surfaces
**Problem:** Mirrors/glass cause artifacts  
**Solution:** Cover mirrors with sheets, minimize glass surfaces in frame

### File Size Too Large
**Problem:** 4K video creates multi-GB files  
**Solution:** Use 1080p 60fps instead (still excellent quality), or compress after capture

---

## Example Capture Timeline

**Medium bedroom (15m²) - Total: ~3 minutes**

| Time | Action |
|------|--------|
| 0:00-0:05 | Start at door, capture entrance |
| 0:05-0:45 | Walk perimeter at eye level (slow, steady) |
| 0:45-1:15 | Walk perimeter with camera tilted up (ceiling) |
| 1:15-1:45 | Walk perimeter with camera tilted down (floor) |
| 1:45-2:15 | Stand in center, rotate 360° slowly (3 heights) |
| 2:15-2:45 | Detail captures (bed, desk, decorations) |
| 2:45-3:00 | Final 360° from entrance |

---

## Quality Checklist

Before processing, verify your capture meets these standards:

- [ ] Video duration appropriate for room size
- [ ] Smooth, steady camera movement throughout
- [ ] Complete 360° coverage of space
- [ ] Multiple heights captured (floor, eye, ceiling)
- [ ] No motion blur visible
- [ ] Even, consistent lighting
- [ ] All important areas captured clearly
- [ ] No people/moving objects in frame
- [ ] Doorways and entrances clearly captured
- [ ] File successfully transferred to Mac

---

## Competition-Specific Notes

### Round 1 (Home Capture - Oct 31, 2026)
- Capture accessible space (home, friend's apartment, etc.)
- Aim for 2-3 rooms minimum for impressive submission
- Ensure good lighting quality for photorealistic result

### Round 3 (On-Site at IIT Bombay - Dec 16, 2026)
- **Time constraint:** Must complete capture + processing in one day
- **Unknown venue:** Practice this SOP multiple times beforehand
- **Bring backup:** Fully charged power bank, extra iPhone if possible
- **Test lighting:** Check venue lighting immediately upon arrival
- **Prioritize coverage:** Better to have complete coverage than perfect detail

---

## Processing Commands (Quick Reference)

After capture, process with these commands:

```bash
# Activate environment
conda activate namma-space

# Process video
ns-process-data video \
  --data data/raw-videos/room1.mp4 \
  --output-dir data/processed/room1

# Train model (opens viewer at localhost:7007)
ns-train splatfacto \
  --data data/processed/room1 \
  --viewer.quit-on-train-completion False

# Export for web
ns-export gaussian-splat \
  --load-config outputs/room1/splatfacto/*/config.yml \
  --output-dir exports/models/room1
```

Expected processing time on MacBook Pro M5 Max:
- Video processing (COLMAP): 10-30 minutes
- Model training: 15-45 minutes
- Export: 2-5 minutes
- **Total:** 30-90 minutes per room

---

## Tips for Competition Success

1. **Practice multiple times** before Round 1 submission
2. **Capture 2-3 test spaces** to understand quality factors
3. **Compare reconstruction quality** between different capture techniques
4. **Document your SOP improvements** for technical abstract
5. **Time yourself** to optimize for Round 3 time constraints
6. **Create checklist** specific to your workflow

---

## Resources

- **Nerfstudio Documentation:** https://docs.nerf.studio/
- **COLMAP Tips:** https://colmap.github.io/faq.html
- **Record3D App:** https://record3d.app/
- **Apple ProRAW/ProRes Guide:** https://support.apple.com/en-us/HT211808

---

**Last Updated:** September 8, 2026  
**Version:** 1.0  
**Author:** Namma Space Team
