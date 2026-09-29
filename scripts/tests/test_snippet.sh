#!/bin/bash
set -e
SPARSE_DIR="namma-space-project/.work/1-splat-competition/colmap/sparse/0"
BEST_MODEL="namma-space-project/.work/1-splat-competition/colmap/sparse/1/"
echo "Best model is $BEST_MODEL"
if [ -n "$BEST_MODEL" ] && [ "$(basename "$BEST_MODEL")" != "0" ]; then
    echo "removing $SPARSE_DIR"
    rm -rf "$SPARSE_DIR"
    echo "copying $BEST_MODEL to $SPARSE_DIR"
    cp -r "$BEST_MODEL" "$SPARSE_DIR"
fi
