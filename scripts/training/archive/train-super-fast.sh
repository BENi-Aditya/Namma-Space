#!/bin/bash
# SUPER-FAST - 1 hour completion!
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

export TERM=xterm-256color
export KMP_DUPLICATE_LIB_OK=TRUE
export PYTORCH_ENABLE_MPS_FALLBACK=1
export CUDA_VISIBLE_DEVICES=""
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"

ns-train nerfacto \
    --data namma-space-project/.work/your-video \
    --output-dir namma-space-project/.work/training-super-fast \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 1500 \
    --machine.device-type cpu \
    --pipeline.datamanager.train-num-rays-per-batch 4096 \
    --pipeline.model.num-nerf-samples-per-ray 24 \
    --pipeline.model.num-proposal-samples-per-ray 48 24 \
    --steps-per-eval-image 1000 \
    --steps-per-save 1500 \
    colmap

echo "✅ Training complete!"
CONFIG=$(find namma-space-project/.work/training-super-fast -name "config.yml" | head -1)
echo "Config: $CONFIG"
