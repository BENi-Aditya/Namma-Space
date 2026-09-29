#!/bin/bash
# FINAL TRAINING - Bypass network requirement
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
echo "  Starting Training (Competition Quality)"
echo "=========================================="
echo ""
echo "Data: 252 frames from 1.mp4"
echo "Method: nerfacto"
echo "Iterations: 15,000"
echo "Viewer: http://localhost:7007"
echo ""
echo "Estimated time: 8-12 hours"
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
    --pipeline.model.disable-scene-contraction False \
    --pipeline.model.use-appearance-embedding False \
    --steps-per-eval-image 1000 \
    --steps-per-save 2500 \
    --logging.local-writer.max-log-size 10 \
    --vis tensorboard \
    colmap

echo ""
echo "=========================================="
echo "  Training Complete!"
echo "=========================================="
CONFIG=$(find "$TRAIN_DIR" -name "config.yml" | tail -1)
echo "Model config: $CONFIG"
echo ""
echo "To view the trained model:"
echo "  ns-viewer --load-config \"$CONFIG\""
echo ""
