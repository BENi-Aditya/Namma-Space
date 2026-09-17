#!/bin/bash
# FASTEST CPU BACKUP - 4-6 hours with reduced settings
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

export TERM=xterm-256color
export KMP_DUPLICATE_LIB_OK=TRUE
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"

# Reduced iterations + smaller model
ns-train nerfacto \
    --data namma-space-project/.work/your-video \
    --output-dir namma-space-project/.work/training-your-video-fast \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 5000 \
    --machine.device-type cpu \
    --pipeline.model.num-nerf-samples-per-ray 24 \
    --pipeline.model.num-proposal-samples-per-ray 128,64 \
    colmap
