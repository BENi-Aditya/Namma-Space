#!/bin/bash

# ==============================================================================
# NAMMA SPACE - RESUME FROM COLMAP
# Continues from existing COLMAP output
# ==============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║            NAMMA SPACE - Resume Training                   ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Activate environment
CONDA_BASE=$(conda info --base 2>/dev/null)
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate namma-space

VIDEO_NAME="your-video"
WORK_DIR="namma-space-project/.work/$VIDEO_NAME"

echo -e "${YELLOW}Checking existing work...${NC}"
echo ""

# Check if COLMAP output exists
if [ ! -d "$WORK_DIR/sparse" ]; then
    echo -e "${RED}✗ No COLMAP output found${NC}"
    echo "Run: ./run-simple.sh"
    exit 1
fi

echo -e "${GREEN}✓ Found COLMAP sparse reconstruction${NC}"

cd "$WORK_DIR"

# COLMAP created sparse/0/0 and sparse/0/1 - check which has more images
MODEL_0_IMGS=$(wc -l < sparse/0/0/images.txt 2>/dev/null || echo "0")
MODEL_1_IMGS=$(wc -l < sparse/0/1/images.txt 2>/dev/null || echo "0")

echo "  Model 0: $MODEL_0_IMGS images"
echo "  Model 1: $MODEL_1_IMGS images"

# Use the model with more images
if [ "$MODEL_1_IMGS" -gt "$MODEL_0_IMGS" ]; then
    BEST_MODEL="1"
    NUM_IMAGES="$MODEL_1_IMGS"
else
    BEST_MODEL="0"
    NUM_IMAGES="$MODEL_0_IMGS"
fi

echo "  Using model $BEST_MODEL with $NUM_IMAGES images"

# Convert to text if needed
if [ ! -f "sparse/0/$BEST_MODEL/cameras.txt" ]; then
    echo "Converting model to text format..."
    colmap model_converter \
        --input_path "sparse/0/$BEST_MODEL" \
        --output_path "sparse/0/$BEST_MODEL" \
        --output_type TXT \
        2>&1 | grep -v "^I" || true
fi

# Check if conversion succeeded
if [ -f "sparse/0/$BEST_MODEL/cameras.txt" ]; then
    echo -e "${GREEN}✓ COLMAP reconstruction valid${NC}"

    # Nerfstudio expects files in sparse/0/, not sparse/0/X/
    # Create symlinks to the best model
    rm -f sparse/0/cameras.txt sparse/0/images.txt sparse/0/points3D.txt
    ln -sf "$BEST_MODEL/cameras.txt" sparse/0/cameras.txt
    ln -sf "$BEST_MODEL/images.txt" sparse/0/images.txt
    ln -sf "$BEST_MODEL/points3D.txt" sparse/0/points3D.txt
else
    echo -e "${RED}✗ Could not convert model${NC}"
    exit 1
fi

cd - > /dev/null

echo ""
echo -e "${YELLOW}Starting Nerfstudio training...${NC}"
echo -e "${CYAN}Viewer at: http://localhost:7007${NC}"
echo -e "${CYAN}This will take 30-45 minutes${NC}"
echo ""

START_TIME=$(date +%s)

TRAIN_DIR="namma-space-project/.work/training-$VIDEO_NAME"
rm -rf "$TRAIN_DIR"

# Fix OpenMP conflict
export KMP_DUPLICATE_LIB_OK=TRUE

# Fix PyTorch cache permissions
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"

# Train
ns-train splatfacto \
    --data "$WORK_DIR" \
    --output-dir "$TRAIN_DIR" \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 30000 \
    colmap

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))

echo ""
echo -e "${GREEN}✓ Training complete (${MINUTES} min)${NC}"
echo ""

# Export
echo -e "${YELLOW}Exporting model...${NC}"

CONFIG=$(find "$TRAIN_DIR" -name "config.yml" | head -n 1)
EXPORT_DIR="namma-space-project/output-models/$VIDEO_NAME"
rm -rf "$EXPORT_DIR"

ns-export gaussian-splat \
    --load-config "$CONFIG" \
    --output-dir "$EXPORT_DIR"

# Copy to web viewer
SPLAT=$(find "$EXPORT_DIR" -name "*.ply" -o -name "*.splat" | head -n 1)
cp "$SPLAT" namma-space-project/web-app/public/models/demo.splat

MODEL_SIZE=$(du -h "$SPLAT" | cut -f1)

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    SUCCESS! 🎉                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Model: $MODEL_SIZE"
echo "Location: $EXPORT_DIR"
echo ""
echo -e "${CYAN}Opening web viewer...${NC}"
echo ""

cd namma-space-project/web-app
[ ! -d "node_modules" ] && npm install
npm run dev
