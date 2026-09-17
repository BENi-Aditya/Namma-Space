#!/bin/bash
# Namma Space - Video 1 Training Pipeline (10,000 steps)
set -e

cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

export TERM=xterm-256color
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=12
export MKL_NUM_THREADS=12
export PYTORCH_ENABLE_MPS_FALLBACK=1
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"

VIDEO_PATH="/Users/tripathd/Downloads/Manual Library/Projects/3D/namma-space-project/input-videos/1.mp4"
DATA_DIR="namma-space-project/.work/1"
OUTPUT_DIR="namma-space-project/.work/training-fast/1"

echo "=================================================="
echo "🎬 Starting Processing & Training for Video 1"
echo "=================================================="
echo "Video File  : $VIDEO_PATH"
echo "Target Steps: 10,000"
echo "Working Dir : $DATA_DIR"
echo "Threads     : 12 Cores Active"
echo "=================================================="
echo ""

TARGET_FRAMES=${TARGET_FRAMES:-800}

CLEAN_RUN=false
if [ "$1" == "--clean" ] || [ "$1" == "-c" ]; then
    CLEAN_RUN=true
    echo "🧹 Clean flag detected: Wiping previous processed data and training checkpoints..."
    rm -rf "$DATA_DIR" "$OUTPUT_DIR"
fi

# Step 1: Process Video with COLMAP (if not already processed)
if [ ! -f "$DATA_DIR/transforms.json" ] || [ "$CLEAN_RUN" = true ]; then
    echo "🔍 [Step 1/3] Extracting $TARGET_FRAMES high-resolution keyframes & running COLMAP..."
    mkdir -p "$DATA_DIR"
    ns-process-data video \
        --data "$VIDEO_PATH" \
        --output-dir "$DATA_DIR" \
        --num-frames-target "$TARGET_FRAMES" \
        --matching-method sequential \
        --no-gpu \
        --verbose
    echo "✅ [Step 1/3] COLMAP processing completed successfully with high frame density!"
else
    echo "ℹ️ [Step 1/3] Found existing transforms.json with $(python3 -c "import json; print(len(json.load(open('$DATA_DIR/transforms.json')).get('frames', [])))" 2>/dev/null || echo "many") camera frames in $DATA_DIR."
fi

echo ""
echo "🚀 [Step 2/3] Starting Nerfacto Training (10,000 steps)..."
echo "Live metrics will stream below:"
echo ""

LATEST_CKPT_DIR=$(find "$OUTPUT_DIR" -name "nerfstudio_models" -type d 2>/dev/null | tail -1)

if [ -n "$LATEST_CKPT_DIR" ] && [ "$(ls -A "$LATEST_CKPT_DIR" 2>/dev/null)" ]; then
    echo "🔄 Resuming from existing checkpoint directory: $LATEST_CKPT_DIR"
    ns-train nerfacto \
        --data "$DATA_DIR" \
        --output-dir "$OUTPUT_DIR" \
        --load-dir "$LATEST_CKPT_DIR" \
        --viewer.quit-on-train-completion True \
        --max-num-iterations 10000 \
        --machine.device-type cpu \
        --pipeline.datamanager.train-num-rays-per-batch 2048 \
        --pipeline.model.num-nerf-samples-per-ray 32 \
        --pipeline.model.num-proposal-samples-per-ray 64 32 \
        --steps-per-eval-image 500 \
        --steps-per-save 1000 \
        colmap
else
    ns-train nerfacto \
        --data "$DATA_DIR" \
        --output-dir "$OUTPUT_DIR" \
        --viewer.quit-on-train-completion True \
        --max-num-iterations 10000 \
        --machine.device-type cpu \
        --pipeline.datamanager.train-num-rays-per-batch 2048 \
        --pipeline.model.num-nerf-samples-per-ray 32 \
        --pipeline.model.num-proposal-samples-per-ray 64 32 \
        --steps-per-eval-image 500 \
        --steps-per-save 1000 \
        colmap
fi

echo ""
echo "🎉 [Step 3/3] Training complete! Exporting 3D Mesh & STL..."
LATEST_CONFIG=$(find "$OUTPUT_DIR" -name "config.yml" | tail -1)
python export_pipeline.py --config "$LATEST_CONFIG"

echo ""
echo "=================================================="
echo "✅ Video 1 Pipeline Finished!"
echo "You can now view model '1' in your browser:"
echo "   http://localhost:8080/viewer.html?model=1"
echo "=================================================="
