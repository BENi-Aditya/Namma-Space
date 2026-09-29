#!/bin/bash
set -e
SPARSE_DIR="namma-space-project/.work/1-splat-competition/colmap/sparse/0"
BEST_COUNT=0
BEST_MODEL=""
for model_dir in "$SPARSE_DIR/../"*/; do
    echo "Checking $model_dir"
    if [ -f "$model_dir/images.bin" ]; then
        COUNT=$(python3 -c "import struct; f=open('${model_dir}images.bin', 'rb'); print(struct.unpack('<Q', f.read(8))[0]); f.close()" 2>/dev/null || echo "0")
        echo "Count: $COUNT"
        if [ "$COUNT" -gt "$BEST_COUNT" ]; then
            BEST_COUNT=$COUNT
            BEST_MODEL="$model_dir"
        fi
    fi
done
echo "Best model: $BEST_MODEL"
