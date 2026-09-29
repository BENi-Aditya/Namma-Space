#!/bin/bash
# FAST GPU TRAINING - 2-3 hours instead of 20-30 hours
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

# Environment setup
export TERM=xterm-256color
export KMP_DUPLICATE_LIB_OK=TRUE
export PYTORCH_ENABLE_MPS_FALLBACK=1
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"

# Use instant-ngp method (10x faster than nerfacto)
ns-train instant-ngp \
    --data namma-space-project/.work/your-video \
    --output-dir namma-space-project/.work/training-your-video-fast \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 10000 \
    --pipeline.model.predict-normals False \
    colmap
