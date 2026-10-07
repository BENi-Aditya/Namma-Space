#!/bin/bash
set -e

# Use the already-prepared 1-emergency dataset for training
CONDA_BASE=$(conda info --base 2>/dev/null)
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate namma-space

export KMP_DUPLICATE_LIB_OK=TRUE
export PYTORCH_ENABLE_MPS_FALLBACK=1
export OMP_NUM_THREADS=8
export TORCH_COMPILE_DISABLE=1

DATA_DIR="namma-space-project/.work/1-emergency"
OUTPUT_DIR="namma-space-project/.work/training-splatfacto-emergency"
EXPORT_DIR="exports/models/emergency"

echo "=========================================="
echo "Training Splatfacto on 1-emergency dataset"
echo "=========================================="
echo "Data: $DATA_DIR"
echo "Output: $OUTPUT_DIR"
echo "Iterations: 15,000 (faster training)"
echo ""

# Train with splatfacto (MPS GPU for Apple Silicon)
ns-train splatfacto \
    --data "$DATA_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --max-num-iterations 15000 \
    --pipeline.model.cull-alpha-thresh 0.005 \
    --viewer.quit-on-train-completion True \
    --machine.device-type mps \
    --machine.num-devices 1

echo ""
echo "=========================================="
echo "Training complete. Exporting .splat file..."
echo "=========================================="

# Find the latest config
CONFIG=$(find "$OUTPUT_DIR" -name "config.yml" -type f | sort -r | head -n 1)

if [ -z "$CONFIG" ]; then
    echo "ERROR: No config.yml found"
    exit 1
fi

echo "Using config: $CONFIG"

# Export to .splat
mkdir -p "$EXPORT_DIR"
ns-export gaussian-splat \
    --load-config "$CONFIG" \
    --output-dir "$EXPORT_DIR"

echo ""
echo "=========================================="
echo "Export complete!"
echo "=========================================="
ls -lh "$EXPORT_DIR"/*.splat

echo ""
echo "Next step: Copy the .splat file to web viewer:"
echo "  cp $EXPORT_DIR/*.splat web-viewer/public/models/demo.splat"
