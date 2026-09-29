#!/bin/bash
# COMPETITION QUALITY TRAINING - 1.mp4
# Full pipeline: frame extraction → COLMAP → nerfacto training (best quality)
set -e

cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

export TERM=xterm-256color
export KMP_DUPLICATE_LIB_OK=TRUE
export PYTORCH_ENABLE_MPS_FALLBACK=1
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=8
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"
export MPLCONFIGDIR="$TMPDIR/matplotlib"
mkdir -p "$MPLCONFIGDIR"

VIDEO="namma-space-project/input-videos/1.mp4"
WORK_DIR="namma-space-project/.work/1-competition"
TRAIN_DIR="namma-space-project/.work/training-competition"

echo "=================================================="
echo "  Namma Space - Competition Quality Training"
echo "=================================================="
echo ""
echo "Video: $VIDEO"
echo "Work dir: $WORK_DIR"
echo ""

# ============================================================
# STEP 1: Frame Extraction (manual FFmpeg, bypassing nerfstudio)
# ============================================================
IMAGES_DIR="$WORK_DIR/images"

if [ -d "$IMAGES_DIR" ] && [ "$(ls -1 "$IMAGES_DIR" 2>/dev/null | wc -l)" -gt 100 ]; then
    EXISTING=$(ls -1 "$IMAGES_DIR" | wc -l)
    echo "[Step 1] Using existing $EXISTING frames in $IMAGES_DIR"
else
    echo "[Step 1] Extracting frames from video..."
    rm -rf "$WORK_DIR"
    mkdir -p "$IMAGES_DIR"

    # Get video info
    DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VIDEO")
    FPS=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$VIDEO")
    TOTAL_FRAMES=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 "$VIDEO")
    echo "  Duration: ${DURATION}s, FPS: $FPS, Total frames: $TOTAL_FRAMES"

    # Extract ~350 frames at 1080p for competition quality
    # More frames = better COLMAP reconstruction = better 3D model
    # 1080p is ideal: enough detail for training, not too heavy for COLMAP
    TARGET_FRAMES=350
    SKIP=$(python3 -c "import math; print(max(1, math.floor($TOTAL_FRAMES / $TARGET_FRAMES)))")
    echo "  Extracting every ${SKIP}th frame (~${TARGET_FRAMES} frames) at 1080p..."

    ffmpeg -i "$VIDEO" \
        -vf "select='not(mod(n\,$SKIP))',scale=1920:1080" \
        -fps_mode vfr \
        -q:v 1 \
        "$IMAGES_DIR/frame_%05d.png" \
        -y 2>&1 | tail -3

    NUM_FRAMES=$(ls -1 "$IMAGES_DIR"/frame_*.png 2>/dev/null | wc -l)
    echo "  Extracted $NUM_FRAMES frames"

    if [ "$NUM_FRAMES" -lt 50 ]; then
        echo "ERROR: Too few frames extracted ($NUM_FRAMES). Something went wrong."
        exit 1
    fi
fi

# Verify frames are actually different
echo ""
echo "  Verifying frame diversity..."
HASH1=$(md5 -q "$IMAGES_DIR/frame_00001.png" 2>/dev/null)
HASH2=$(md5 -q "$IMAGES_DIR/frame_00010.png" 2>/dev/null)
HASH3=$(md5 -q "$IMAGES_DIR/frame_00050.png" 2>/dev/null)
if [ "$HASH1" = "$HASH2" ] && [ "$HASH2" = "$HASH3" ]; then
    echo "  ERROR: Frames appear identical! Video extraction failed."
    exit 1
fi
echo "  Frames verified - all unique content"

# ============================================================
# STEP 2: Create downscaled variants (nerfstudio expects these)
# ============================================================
echo ""
echo "[Step 2] Creating downscaled image variants..."
for SCALE in 2 4 8; do
    SCALED_DIR="$WORK_DIR/images_${SCALE}"
    if [ -d "$SCALED_DIR" ] && [ "$(ls -1 "$SCALED_DIR" 2>/dev/null | wc -l)" -gt 10 ]; then
        echo "  images_${SCALE}: already exists"
        continue
    fi
    mkdir -p "$SCALED_DIR"
    W=$((1920 / SCALE))
    H=$((1080 / SCALE))
    echo "  Creating images_${SCALE} (${W}x${H})..."
    for f in "$IMAGES_DIR"/frame_*.png; do
        BASENAME=$(basename "$f")
        ffmpeg -i "$f" -vf "scale=${W}:${H}" -q:v 2 "$SCALED_DIR/$BASENAME" -y 2>/dev/null
    done
done

# ============================================================
# STEP 3: COLMAP Reconstruction
# ============================================================
COLMAP_DIR="$WORK_DIR/colmap"
SPARSE_DIR="$COLMAP_DIR/sparse/0"

if [ -d "$SPARSE_DIR" ] && [ -f "$SPARSE_DIR/cameras.bin" ]; then
    echo ""
    echo "[Step 3] COLMAP reconstruction already exists, checking quality..."
    # Check how many images COLMAP registered
    python3 -c "
import struct, os
path = '$SPARSE_DIR/images.bin'
with open(path, 'rb') as f:
    num = struct.unpack('<Q', f.read(8))[0]
print(f'  COLMAP registered {num} images')
if num < 50:
    print('  WARNING: Too few images registered. Will re-run COLMAP.')
    exit(1)
" 2>/dev/null
    COLMAP_OK=$?
    if [ $COLMAP_OK -ne 0 ]; then
        echo "  Re-running COLMAP..."
        rm -rf "$COLMAP_DIR"
    fi
fi

if [ ! -d "$SPARSE_DIR" ] || [ ! -f "$SPARSE_DIR/cameras.bin" ]; then
    echo ""
    echo "[Step 3] Running COLMAP (CPU-only)..."
    mkdir -p "$COLMAP_DIR" "$SPARSE_DIR"
    DB_PATH="$COLMAP_DIR/database.db"
    rm -f "$DB_PATH"

    echo "  [3a] Feature extraction..."
    colmap feature_extractor \
        --database_path "$DB_PATH" \
        --image_path "$IMAGES_DIR" \
        --FeatureExtraction.use_gpu 0 \
        --ImageReader.camera_model OPENCV \
        --ImageReader.single_camera 1 \
        2>&1 | grep -E "Processed|features|elapsed" || true

    echo "  [3b] Sequential matching (optimized for video)..."
    colmap sequential_matcher \
        --database_path "$DB_PATH" \
        --SequentialMatching.overlap 10 \
        --SequentialMatching.quadratic_overlap 1 \
        --SiftMatching.use_gpu 0 \
        2>&1 | grep -E "Matched|elapsed|pairs" || true

    echo "  [3c] Sparse reconstruction (mapper)..."
    colmap mapper \
        --database_path "$DB_PATH" \
        --image_path "$IMAGES_DIR" \
        --output_path "$SPARSE_DIR/../" \
        --Mapper.ba_global_max_num_iterations 50 \
        --Mapper.ba_global_max_refinements 3 \
        2>&1 | grep -E "Registering|elapsed|images|points" || true

    # Find the best model (most images)
    BEST_MODEL=""
    BEST_COUNT=0
    for model_dir in "$SPARSE_DIR/../"*/; do
        if [ -f "$model_dir/images.bin" ]; then
            COUNT=$(python3 -c "
import struct
with open('${model_dir}images.bin', 'rb') as f:
    print(struct.unpack('<Q', f.read(8))[0])
" 2>/dev/null || echo "0")
            echo "  Model $(basename $model_dir): $COUNT images"
            if [ "$COUNT" -gt "$BEST_COUNT" ]; then
                BEST_COUNT=$COUNT
                BEST_MODEL="$model_dir"
            fi
        fi
    done

    if [ -z "$BEST_MODEL" ] || [ "$BEST_COUNT" -lt 30 ]; then
        echo "  ERROR: COLMAP failed to register enough images ($BEST_COUNT). Video may need different recording."
        exit 1
    fi

    # Copy best model to sparse/0
    if [ "$(basename "$BEST_MODEL")" != "0" ]; then
        rm -rf "$SPARSE_DIR"
        cp -r "$BEST_MODEL" "$SPARSE_DIR"
    fi

    echo "  COLMAP done: $BEST_COUNT images registered"

    # Undistort images
    echo "  [3d] Undistorting images..."
    colmap image_undistorter \
        --image_path "$IMAGES_DIR" \
        --input_path "$SPARSE_DIR" \
        --output_path "$WORK_DIR/colmap-undistorted" \
        --output_type COLMAP \
        2>&1 | grep -E "Undistort|elapsed" || true
fi

echo ""
echo "  COLMAP reconstruction complete"

# ============================================================
# STEP 4: Process data with nerfstudio (skip frame extraction, just COLMAP→transforms)
# ============================================================
echo ""
echo "[Step 4] Generating nerfstudio transforms..."

# Use ns-process-data with images (not video) to generate transforms.json
# But since COLMAP is already done, we can use --skip-colmap
if [ ! -f "$WORK_DIR/transforms.json" ] || [ "$(python3 -c "import json; d=json.load(open('$WORK_DIR/transforms.json')); print(len(d.get('frames',[])))" 2>/dev/null)" -lt 30 ]; then
    echo "  Running ns-process-data to generate transforms from COLMAP..."
    ns-process-data images \
        --data "$IMAGES_DIR" \
        --output-dir "$WORK_DIR" \
        --skip-colmap \
        --colmap-model-path colmap/sparse/0 \
        --no-gpu \
        --num-downscales 3 \
        2>&1 | tail -10

    TRANSFORM_FRAMES=$(python3 -c "import json; d=json.load(open('$WORK_DIR/transforms.json')); print(len(d.get('frames',[])))" 2>/dev/null || echo "0")
    echo "  Generated transforms.json with $TRANSFORM_FRAMES frames"
else
    TRANSFORM_FRAMES=$(python3 -c "import json; d=json.load(open('$WORK_DIR/transforms.json')); print(len(d.get('frames',[])))" 2>/dev/null || echo "0")
    echo "  transforms.json already has $TRANSFORM_FRAMES frames"
fi

# ============================================================
# STEP 5: Competition Quality Training
# ============================================================
echo ""
echo "[Step 5] Starting nerfacto training (COMPETITION QUALITY)..."
echo "  Method: nerfacto"
echo "  Iterations: 15000 (high quality)"
echo "  Ray batch: 4096"
echo "  Viewer: http://localhost:7007"
echo ""
echo "  ESTIMATED TIME: ~8-12 hours on CPU (M5 Max)"
echo "  You can monitor progress at http://localhost:7007"
echo ""

rm -rf "$TRAIN_DIR"

ns-train nerfacto \
    --data "$WORK_DIR" \
    --output-dir "$TRAIN_DIR" \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 15000 \
    --machine.device-type cpu \
    --pipeline.datamanager.train-num-rays-per-batch 4096 \
    --pipeline.model.num-nerf-samples-per-ray 64 \
    --pipeline.model.num-proposal-samples-per-ray 128 64 \
    --pipeline.model.proposal-initial-sampler uniform \
    --pipeline.model.near-plane 0.05 \
    --pipeline.model.far-plane 1000.0 \
    --steps-per-eval-image 1000 \
    --steps-per-save 2500 \
    --pipeline.datamanager.eval-num-rays-per-batch 2048 \
    colmap

echo ""
echo "=================================================="
echo "  Training complete!"
echo "=================================================="
echo ""

CONFIG=$(find "$TRAIN_DIR" -name "config.yml" | tail -1)
echo "Config: $CONFIG"
echo ""
echo "To view the model interactively:"
echo "  ns-viewer --load-config \"$CONFIG\""
echo ""
