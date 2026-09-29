#!/bin/bash
# EMERGENCY: Skip COLMAP, use nerfstudio's built-in processing
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
WORK_DIR="namma-space-project/.work/1-emergency"
TRAIN_DIR="namma-space-project/.work/training-emergency"

echo "=========================================="
echo "  EMERGENCY: Nerfstudio native processing"
echo "=========================================="
echo ""

# Let nerfstudio handle EVERYTHING - it has better COLMAP integration
rm -rf "$WORK_DIR" "$TRAIN_DIR"

echo "Running nerfstudio ns-process-data with relaxed settings..."
ns-process-data video \
    --data "$VIDEO" \
    --output-dir "$WORK_DIR" \
    --num-frames-target 250 \
    --matching-method exhaustive \
    --no-gpu \
    --num-downscales 2 \
    --verbose

echo ""
echo "Starting training..."
ns-train nerfacto \
    --data "$WORK_DIR" \
    --output-dir "$TRAIN_DIR" \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 15000 \
    --machine.device-type cpu \
    --pipeline.datamanager.train-num-rays-per-batch 4096 \
    --pipeline.model.num-nerf-samples-per-ray 64 \
    --pipeline.model.num-proposal-samples-per-ray 128 64 \
    --steps-per-eval-image 1000 \
    --steps-per-save 2500 \
    colmap

echo ""
echo "Training complete!"
CONFIG=$(find "$TRAIN_DIR" -name "config.yml" | tail -1)
echo "Config: $CONFIG"
