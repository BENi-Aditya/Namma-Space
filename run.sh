#!/bin/bash

# ==============================================================================
# NAMMA SPACE - MASTER RUN SCRIPT (FIXED for ffmpeg 7.x)
# IIT Bombay Techfest 2026-27
# ==============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                     NAMMA SPACE                            ║"
echo "║          3D Indoor Navigation System                       ║"
echo "║          IIT Bombay Techfest 2026-27                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# ==============================================================================
# STEP 0: Check Setup
# ==============================================================================

echo -e "${YELLOW}[STEP 0] Checking setup...${NC}"

# Activate environment
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"

    if conda env list | grep -q "namma-space"; then
        conda activate namma-space
        echo -e "${GREEN}✓ Environment activated${NC}"
    else
        echo -e "${RED}ERROR: namma-space environment not found!${NC}"
        echo "Please run: ./clean-install.sh"
        exit 1
    fi
else
    echo -e "${RED}ERROR: Conda not found!${NC}"
    echo "Please run: ./clean-install.sh"
    exit 1
fi

echo ""

# ==============================================================================
# STEP 1: Check for Input Video
# ==============================================================================

echo -e "${YELLOW}[STEP 1] Checking for input videos...${NC}"
echo ""

VIDEO_DIR="namma-space-project/input-videos"

# Count videos
VIDEO_COUNT=$(find "$VIDEO_DIR" -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.MP4" -o -name "*.MOV" \) 2>/dev/null | wc -l | tr -d ' ')

if [ "$VIDEO_COUNT" -eq 0 ]; then
    echo -e "${RED}No videos found in: $VIDEO_DIR${NC}"
    echo ""
    echo "Please:"
    echo "1. Record video on iPhone 15 Pro (4K 30fps, 2-3 min)"
    echo "2. Transfer to Mac (AirDrop)"
    echo "3. Copy to: $VIDEO_DIR/"
    echo ""
    echo "Example:"
    echo "  cp ~/Downloads/IMG_1234.mp4 \"$VIDEO_DIR/my-room.mp4\""
    echo ""
    exit 1
fi

# List videos
echo "Found $VIDEO_COUNT video(s):"
echo ""
find "$VIDEO_DIR" -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.MP4" -o -name "*.MOV" \) -exec basename {} \; | nl
echo ""

# Select video
if [ "$VIDEO_COUNT" -eq 1 ]; then
    VIDEO_FILE=$(find "$VIDEO_DIR" -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.MP4" -o -name "*.MOV" \) | head -n 1)
    VIDEO_NAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
    echo -e "${GREEN}Auto-selecting: $(basename "$VIDEO_FILE")${NC}"
else
    echo -n "Which video to process? Enter number [1]: "
    read VIDEO_NUM
    VIDEO_NUM=${VIDEO_NUM:-1}
    VIDEO_FILE=$(find "$VIDEO_DIR" -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.MP4" -o -name "*.MOV" \) | sed -n "${VIDEO_NUM}p")
    VIDEO_NAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
fi

echo ""
echo -e "Processing: ${CYAN}$VIDEO_NAME${NC}"
echo ""

# ==============================================================================
# STEP 2: Process Video (Fixed for ffmpeg 7.x)
# ==============================================================================

echo -e "${YELLOW}[STEP 2] Processing video...${NC}"
echo -e "${BLUE}Expected time: 10-30 minutes${NC}"
echo ""

PROCESSED_DIR="namma-space-project/.temp-processing/$VIDEO_NAME"
mkdir -p "$PROCESSED_DIR"

START_TIME=$(date +%s)

# Use polycam method which doesn't use -vsync flag
ns-process-data video \
    --data "$VIDEO_FILE" \
    --output-dir "$PROCESSED_DIR" \
    --num-frames-target 300 \
    --matching-method exhaustive

COLMAP_END=$(date +%s)
COLMAP_DURATION=$((COLMAP_END - START_TIME))
COLMAP_MINUTES=$((COLMAP_DURATION / 60))

echo ""
echo -e "${GREEN}✓ Video processing complete (${COLMAP_MINUTES} minutes)${NC}"
echo ""

# ==============================================================================
# STEP 3: Train 3D Model
# ==============================================================================

echo -e "${YELLOW}[STEP 3] Training 3D model with Gaussian Splatting...${NC}"
echo -e "${BLUE}Expected time: 15-45 minutes${NC}"
echo -e "${BLUE}Viewer at: http://localhost:7007${NC}"
echo ""

TRAIN_START=$(date +%s)

OUTPUT_DIR="namma-space-project/.temp-training/$VIDEO_NAME"
mkdir -p "$OUTPUT_DIR"

ns-train splatfacto \
    --data "$PROCESSED_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 30000 \
    --pipeline.model.cull-alpha-thresh 0.005

TRAIN_END=$(date +%s)
TRAIN_DURATION=$((TRAIN_END - TRAIN_START))
TRAIN_MINUTES=$((TRAIN_DURATION / 60))

echo ""
echo -e "${GREEN}✓ Training complete (${TRAIN_MINUTES} minutes)${NC}"
echo ""

# ==============================================================================
# STEP 4: Export for Web
# ==============================================================================

echo -e "${YELLOW}[STEP 4] Exporting for web viewer...${NC}"
echo ""

CONFIG_FILE=$(find "$OUTPUT_DIR" -name "config.yml" -type f | head -n 1)

if [ -z "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Could not find config file${NC}"
    exit 1
fi

EXPORT_START=$(date +%s)
EXPORT_DIR="namma-space-project/output-models/$VIDEO_NAME"
mkdir -p "$EXPORT_DIR"

ns-export gaussian-splat \
    --load-config "$CONFIG_FILE" \
    --output-dir "$EXPORT_DIR"

EXPORT_END=$(date +%s)
EXPORT_DURATION=$((EXPORT_END - EXPORT_START))

echo ""
echo -e "${GREEN}✓ Export complete${NC}"
echo ""

# ==============================================================================
# STEP 5: Setup Web Viewer
# ==============================================================================

echo -e "${YELLOW}[STEP 5] Setting up web viewer...${NC}"
echo ""

WEB_APP_DIR="namma-space-project/web-app"

# Install dependencies if needed
if [ ! -d "$WEB_APP_DIR/node_modules" ]; then
    echo "Installing web viewer dependencies..."
    cd "$WEB_APP_DIR"
    npm install
    cd - > /dev/null
fi

# Copy model
SPLAT_FILE=$(find "$EXPORT_DIR" -name "*.ply" -o -name "*.splat" | head -n 1)
if [ -n "$SPLAT_FILE" ]; then
    mkdir -p "$WEB_APP_DIR/public/models"
    cp "$SPLAT_FILE" "$WEB_APP_DIR/public/models/demo.splat"
    echo -e "${GREEN}✓ Model copied to web viewer${NC}"
fi

echo ""

# ==============================================================================
# SUMMARY
# ==============================================================================

TOTAL_END=$(date +%s)
TOTAL_DURATION=$((TOTAL_END - START_TIME))
TOTAL_MINUTES=$((TOTAL_DURATION / 60))
TOTAL_SECONDS=$((TOTAL_DURATION % 60))

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 PROCESSING COMPLETE! 🎉                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Statistics:"
echo "  - Video processing: ${COLMAP_MINUTES} minutes"
echo "  - Model training: ${TRAIN_MINUTES} minutes"
echo "  - Export: ${EXPORT_DURATION} seconds"
echo "  - Total: ${TOTAL_MINUTES}m ${TOTAL_SECONDS}s"
echo ""
echo "Model: $EXPORT_DIR"
echo "Size: $(du -sh "$EXPORT_DIR" | cut -f1)"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Starting web viewer...${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Controls:"
echo "  - Click to start"
echo "  - W A S D = Move"
echo "  - Mouse = Look"
echo "  - ESC = Exit"
echo ""
echo "Browser: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# ==============================================================================
# Launch Web Viewer
# ==============================================================================

cd "$WEB_APP_DIR"
npm run dev
