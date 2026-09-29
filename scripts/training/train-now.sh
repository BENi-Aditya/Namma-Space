#!/bin/bash
# MINIMAL TRAINING - Just make it work!
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

WORK_DIR="namma-space-project/.work/1-emergency"
TRAIN_DIR="namma-space-project/.work/training-final"

echo "=========================================="
echo "  TRAINING STARTED"
echo "=========================================="
echo "Data: $WORK_DIR (252 frames)"
echo "Output: $TRAIN_DIR"
echo "Iterations: 15,000"
echo ""

rm -rf "$TRAIN_DIR"

# Minimal command - just the essentials
ns-train nerfacto \
    --data "$WORK_DIR" \
    --output-dir "$TRAIN_DIR" \
    --max-num-iterations 15000 \
    --machine.device-type cpu \
    --steps-per-save 2500 \
    colmap

echo ""
echo "=========================================="
echo "  TRAINING COMPLETE"
echo "=========================================="
CONFIG=$(find "$TRAIN_DIR" -name "config.yml" | tail -1)
echo "Model: $CONFIG"
