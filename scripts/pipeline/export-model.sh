#!/bin/bash
# 3D Export Script - Interactive Model Selection & STL / OBJ Mesh Export
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

export TERM=xterm-256color
export CUDA_VISIBLE_DEVICES=""
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=1

python export_pipeline.py "$@"
