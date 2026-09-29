#!/bin/bash
set -e
CONDA_BASE=$(conda info --base 2>/dev/null)
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate namma-space
WORK_DIR="namma-space-project/.work/1-splat-competition"
IMAGES_DIR="$WORK_DIR/images"
ns-process-data images \
    --data "$IMAGES_DIR" \
    --output-dir "$WORK_DIR" \
    --skip-colmap \
    --colmap-model-path colmap/sparse/0 \
    --no-gpu >/dev/null 2>&1
echo "Passed ns-process"
