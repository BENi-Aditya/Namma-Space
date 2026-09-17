#!/bin/bash

# Namma Space - Video Processing Automation Script
# Automates the video → 3D model pipeline

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if conda environment is activated
if [[ "$CONDA_DEFAULT_ENV" != "namma-space" ]]; then
    echo -e "${RED}Error: Please activate the conda environment first:${NC}"
    echo "conda activate namma-space"
    exit 1
fi

# Check arguments
if [ "$#" -lt 1 ]; then
    echo "Usage: ./process_video.sh <video_file> [room_name]"
    echo ""
    echo "Example:"
    echo "  ./process_video.sh data/raw-videos/living_room.mp4 living_room"
    echo ""
    echo "If room_name is not provided, it will be extracted from the filename."
    exit 1
fi

VIDEO_FILE="$1"
ROOM_NAME="${2:-$(basename "$VIDEO_FILE" .mp4)}"

# Check if video file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo -e "${RED}Error: Video file not found: $VIDEO_FILE${NC}"
    exit 1
fi

echo "=================================================="
echo "Namma Space - Video Processing Pipeline"
echo "=================================================="
echo ""
echo "Video: $VIDEO_FILE"
echo "Room: $ROOM_NAME"
echo ""

# Create output directories
PROCESSED_DIR="data/processed/$ROOM_NAME"
EXPORT_DIR="exports/models/$ROOM_NAME"

mkdir -p "$PROCESSED_DIR"
mkdir -p "$EXPORT_DIR"

# Step 1: Process video with COLMAP
echo -e "${YELLOW}[1/3] Processing video and running COLMAP...${NC}"
echo "This will extract frames and estimate camera poses."
echo "Expected time: 10-30 minutes"
echo ""

START_TIME=$(date +%s)

ns-process-data video \
    --data "$VIDEO_FILE" \
    --output-dir "$PROCESSED_DIR" \
    --num-frames-target 300 \
    --verbose

COLMAP_END=$(date +%s)
COLMAP_DURATION=$((COLMAP_END - START_TIME))

echo -e "${GREEN}✓ Video processing complete (${COLMAP_DURATION}s)${NC}"
echo ""

# Step 2: Train Gaussian Splatting model
echo -e "${YELLOW}[2/3] Training Gaussian Splatting model...${NC}"
echo "This will train the 3D reconstruction model."
echo "Expected time: 15-45 minutes"
echo "Viewer will open at http://localhost:7007"
echo ""

TRAIN_START=$(date +%s)

ns-train splatfacto \
    --data "$PROCESSED_DIR" \
    --output-dir "outputs/$ROOM_NAME" \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 30000 \
    --pipeline.model.cull-alpha-thresh 0.005 \
    --pipeline.model.continue-cull-post-densification False

TRAIN_END=$(date +%s)
TRAIN_DURATION=$((TRAIN_END - TRAIN_START))

echo -e "${GREEN}✓ Training complete (${TRAIN_DURATION}s)${NC}"
echo ""

# Find the latest config file
CONFIG_FILE=$(find "outputs/$ROOM_NAME/splatfacto" -name "config.yml" | head -n 1)

if [ -z "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Could not find config file${NC}"
    exit 1
fi

echo "Config file: $CONFIG_FILE"
echo ""

# Step 3: Export for web
echo -e "${YELLOW}[3/3] Exporting model for web viewer...${NC}"

EXPORT_START=$(date +%s)

ns-export gaussian-splat \
    --load-config "$CONFIG_FILE" \
    --output-dir "$EXPORT_DIR"

EXPORT_END=$(date +%s)
EXPORT_DURATION=$((EXPORT_END - EXPORT_START))

echo -e "${GREEN}✓ Export complete (${EXPORT_DURATION}s)${NC}"
echo ""

# Calculate total time
TOTAL_DURATION=$((EXPORT_END - START_TIME))
TOTAL_MINUTES=$((TOTAL_DURATION / 60))
TOTAL_SECONDS=$((TOTAL_DURATION % 60))

# Summary
echo "=================================================="
echo -e "${GREEN}Processing Complete!${NC}"
echo "=================================================="
echo ""
echo "Processing Statistics:"
echo "  - COLMAP processing: ${COLMAP_DURATION}s"
echo "  - Model training: ${TRAIN_DURATION}s"
echo "  - Export: ${EXPORT_DURATION}s"
echo "  - Total time: ${TOTAL_MINUTES}m ${TOTAL_SECONDS}s"
echo ""
echo "Output files:"
echo "  - Processed data: $PROCESSED_DIR"
echo "  - Trained model: outputs/$ROOM_NAME"
echo "  - Web export: $EXPORT_DIR"
echo ""
echo "Model file for web viewer:"
ls -lh "$EXPORT_DIR"/*.ply 2>/dev/null || ls -lh "$EXPORT_DIR"/*.splat 2>/dev/null
echo ""
echo "Next steps:"
echo "1. Copy model to web viewer:"
echo "   cp $EXPORT_DIR/*.splat web-viewer/public/models/${ROOM_NAME}.splat"
echo ""
echo "2. Start web viewer:"
echo "   cd web-viewer && npm run dev"
echo ""
echo "3. Open browser to http://localhost:5173"
echo ""
