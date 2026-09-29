#!/bin/bash
set -e
SPARSE_DIR="namma-space-project/.work/1-splat-competition/colmap/sparse/0"
BEST_MODEL="namma-space-project/.work/1-splat-competition/colmap/sparse/1/"
echo "Starting test_cp_exact.sh"
rm -rf "$SPARSE_DIR"
cp -r "$BEST_MODEL" "$SPARSE_DIR"
echo "Finished!"
