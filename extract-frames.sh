#!/bin/bash

# ==============================================================================
# NAMMA SPACE - MANUAL FRAME EXTRACTION WORKAROUND
# Works with ffmpeg 7.x/8.x/9.x
# ==============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         NAMMA SPACE - Frame Extraction Fix                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Activate environment
eval "$(conda shell.bash hook)"
conda activate namma-space

# Find video
VIDEO_DIR="namma-space-project/input-videos"
VIDEO_FILE=$(find "$VIDEO_DIR" -type f \( -name "*.mp4" -o -name "*.mov" -o -name "*.MP4" -o -name "*.MOV" \) | head -n 1)

if [ -z "$VIDEO_FILE" ]; then
    echo -e "${RED}No video found!${NC}"
    exit 1
fi

VIDEO_NAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
PROCESSED_DIR="namma-space-project/.temp-processing/$VIDEO_NAME"

echo -e "${YELLOW}Processing: $VIDEO_NAME${NC}"
echo ""

# Create directories
mkdir -p "$PROCESSED_DIR/images"

# Extract frames manually (works with any ffmpeg version)
echo -e "${YELLOW}Extracting frames (300 frames)...${NC}"

ffmpeg -i "$VIDEO_FILE" \
    -vf "select='not(mod(n\,3))',scale=iw:ih" \
    -frames:v 300 \
    -q:v 2 \
    "$PROCESSED_DIR/images/frame_%05d.png" \
    -y

echo -e "${GREEN}✓ Frames extracted${NC}"
echo ""

# Create transforms.json manually
echo -e "${YELLOW}Creating transforms.json...${NC}"

FRAME_COUNT=$(ls "$PROCESSED_DIR/images"/*.png 2>/dev/null | wc -l | tr -d ' ')

cat > "$PROCESSED_DIR/transforms.json" << EOF
{
  "camera_model": "OPENCV",
  "fl_x": 1000.0,
  "fl_y": 1000.0,
  "cx": 960.0,
  "cy": 540.0,
  "w": 1920,
  "h": 1080,
  "k1": 0.0,
  "k2": 0.0,
  "p1": 0.0,
  "p2": 0.0,
  "frames": []
}
EOF

echo -e "${GREEN}✓ transforms.json created${NC}"
echo ""

# Run COLMAP
echo -e "${YELLOW}Running COLMAP (this takes 10-20 minutes)...${NC}"
echo ""

cd "$PROCESSED_DIR"

# COLMAP feature extraction
colmap feature_extractor \
    --database_path database.db \
    --image_path images \
    --ImageReader.single_camera 1 \
    --ImageReader.camera_model OPENCV

echo -e "${GREEN}✓ Features extracted${NC}"

# COLMAP matching
colmap exhaustive_matcher \
    --database_path database.db

echo -e "${GREEN}✓ Feature matching complete${NC}"

# Create sparse directory
mkdir -p sparse/0

# COLMAP mapper
colmap mapper \
    --database_path database.db \
    --image_path images \
    --output_path sparse/0

echo -e "${GREEN}✓ COLMAP mapping complete${NC}"

# Convert to text format
colmap model_converter \
    --input_path sparse/0 \
    --output_path sparse/0 \
    --output_type TXT

echo -e "${GREEN}✓ Model converted${NC}"

cd - > /dev/null

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            Frame Extraction Complete! ✓                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Extracted: $FRAME_COUNT frames"
echo "Location: $PROCESSED_DIR"
echo ""
echo -e "${YELLOW}Now run training:${NC}"
echo ""
echo "  ./train-model.sh"
echo ""
