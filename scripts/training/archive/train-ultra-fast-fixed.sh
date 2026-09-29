#!/bin/bash
# ULTRA-FAST TRAINING - CPU FORCED (2-3 hours)
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

export TERM=xterm-256color
export KMP_DUPLICATE_LIB_OK=TRUE
export PYTORCH_ENABLE_MPS_FALLBACK=1
export CUDA_VISIBLE_DEVICES=""
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"

# Ultra-fast nerfacto with CPU enforcement
ns-train nerfacto \
    --data namma-space-project/.work/your-video \
    --output-dir namma-space-project/.work/training-fast \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 3000 \
    --machine.device-type cpu \
    --pipeline.datamanager.train-num-rays-per-batch 2048 \
    --pipeline.model.num-nerf-samples-per-ray 32 \
    --pipeline.model.num-proposal-samples-per-ray 64 32 \
    --steps-per-eval-image 500 \
    --steps-per-save 1000 \
    colmap

echo ""
echo "Training complete! Exporting model..."

# Find the config file
CONFIG=$(find namma-space-project/.work/training-fast -name "config.yml" | head -1)

if [ -f "$CONFIG" ]; then
    echo "✅ Model trained! Config at: $CONFIG"
    echo ""
    echo "To export and view your model, run:"
    echo "  cd namma-space-project/web-app"
    echo "  npm run dev"
    echo ""
    echo "Or export to other formats with:"
    echo "  ns-export gaussian-splat --load-config $CONFIG --output-dir output-models/"
fi
