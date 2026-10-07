#!/bin/bash
#
# Test Enhanced COLMAP Pipeline
# ===============================
#
# Quick test on your-video.mov (36 seconds, 1101 frames)
# to validate enhanced settings before running on large 1.mp4
#

set -e

VIDEO="data/raw-videos/your-video.mov"
TEST_DIR="experiments/spatial-engine-v2/test-runs/colmap-enhanced-test"
FRAMES_DIR="$TEST_DIR/frames"
WORKSPACE="$TEST_DIR/colmap_workspace"

echo "====================================="
echo "Enhanced COLMAP Test Run"
echo "====================================="
echo "Video: $VIDEO"
echo "Test Dir: $TEST_DIR"
echo ""

# Step 1: Extract frames
echo "📹 Step 1: Extracting frames..."
mkdir -p "$FRAMES_DIR"

ffmpeg -i "$VIDEO" \
    -vf "fps=10" \
    -q:v 2 \
    "$FRAMES_DIR/frame_%04d.jpg" \
    -y 2>&1 | grep -E "(frame=|Duration:|Stream)"

FRAME_COUNT=$(ls -1 "$FRAMES_DIR"/*.jpg 2>/dev/null | wc -l)
echo "✅ Extracted $FRAME_COUNT frames"
echo ""

# Step 2: Run enhanced COLMAP
echo "🔍 Step 2: Running enhanced COLMAP pipeline..."
python experiments/spatial-engine-v2/capture/enhanced_colmap_pipeline.py \
    --images "$FRAMES_DIR" \
    --workspace "$WORKSPACE" \
    --overlap 10

# Step 3: Summary
echo ""
echo "====================================="
echo "Test Complete"
echo "====================================="
echo "Results: $WORKSPACE/enhanced_colmap_results.json"
echo ""

if [ -f "$WORKSPACE/enhanced_colmap_results.json" ]; then
    echo "📊 Quick Summary:"
    cat "$WORKSPACE/enhanced_colmap_results.json"
fi
