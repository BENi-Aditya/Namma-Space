#!/bin/bash
set -e

# Train Nerfacto (NeRF) which WORKS on MPS
CONDA_BASE=$(conda info --base 2>/dev/null)
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate namma-space

export KMP_DUPLICATE_LIB_OK=TRUE
export PYTORCH_ENABLE_MPS_FALLBACK=1
export OMP_NUM_THREADS=8

DATA_DIR="namma-space-project/.work/1-emergency"
OUTPUT_DIR="namma-space-project/.work/training-nerfacto-emergency"
EXPORT_DIR="exports/models/emergency-pointcloud"

echo "=========================================="
echo "Training Nerfacto (NeRF) on 1-emergency"
echo "Works on Apple Silicon MPS!"
echo "=========================================="
echo "Data: $DATA_DIR"
echo "Output: $OUTPUT_DIR"
echo "Iterations: 10,000 (faster)"
echo ""

# Train with nerfacto (NeRF - works on MPS)
ns-train nerfacto \
    --data "$DATA_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --max-num-iterations 10000 \
    --viewer.quit-on-train-completion True \
    --machine.device-type mps \
    --machine.num-devices 1

echo ""
echo "=========================================="
echo "Training complete. Exporting point cloud..."
echo "=========================================="

# Find the latest config
CONFIG=$(find "$OUTPUT_DIR" -name "config.yml" -type f | sort -r | head -n 1)

if [ -z "$CONFIG" ]; then
    echo "ERROR: No config.yml found"
    exit 1
fi

echo "Using config: $CONFIG"

# Export to point cloud
mkdir -p "$EXPORT_DIR"
ns-export pointcloud \
    --load-config "$CONFIG" \
    --output-dir "$EXPORT_DIR" \
    --num-points 1000000 \
    --remove-outliers True

echo ""
echo "=========================================="
echo "Export complete!"
echo "=========================================="
ls -lh "$EXPORT_DIR"/*.ply

echo ""
echo "Point cloud exported to: $EXPORT_DIR/point_cloud.ply"
echo ""
echo "You can view it with:"
echo "  - CloudCompare (free)"
echo "  - MeshLab (free)"
echo "  - Or modify web viewer to load .ply instead of .splat"
