#!/bin/bash
# COMPETITION QUALITY TRAINING - 1.mp4 -> Gaussian Splatting
# Full pipeline for the best quality React Three.js visualization

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     NAMMA SPACE - Competition Quality Splat Training       ║${NC}"
echo -e "${CYAN}║     Video: 1.mp4 (Highest possible quality target)         ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

CONDA_BASE=$(conda info --base 2>/dev/null)
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate namma-space

export KMP_DUPLICATE_LIB_OK=TRUE
export PYTORCH_ENABLE_MPS_FALLBACK=1
export OMP_NUM_THREADS=8
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"

VIDEO="namma-space-project/input-videos/1.mp4"
WORK_DIR="namma-space-project/.work/1-splat-competition"
TRAIN_DIR="namma-space-project/.work/training-1-splat-competition"

DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VIDEO")
TARGET_FRAMES=350
FPS=$(python3 -c "print(max(0.5, min(10.0, $TARGET_FRAMES / $DURATION)))")

echo -e "${YELLOW}PIPELINE ESTIMATED TIME OF COMPLETION:${NC}"
echo "  Step 1: Frame Extraction (~1-2 minutes)"
echo "  Step 2: COLMAP feature extraction (~5-8 mins) & matching (~10-15 mins)"
echo "  Step 3: COLMAP Sparse Reconstruction (~15-20 minutes)"
echo "  Step 4: Nerfstudio Transforms Gen (~1 minute)"
echo "  Step 5: Splatfacto Training (~45-60 minutes on MPS GPU)"
echo -e "${YELLOW}-> Total Expected Duration: ~1 hr 15 mins to 1 hr 40 mins${NC}"
echo ""

# STEP 1
echo -e "${GREEN}[Step 1/5] Extracting frames at ${FPS} FPS... (ETA: 1-2 mins)${NC}"
IMAGES_DIR="$WORK_DIR/images"

rm -rf "$WORK_DIR"
mkdir -p "$IMAGES_DIR"

ffmpeg -i "$VIDEO" \
    -vf "fps=$FPS,scale=-1:1080" \
    -q:v 2 \
    "$IMAGES_DIR/frame_%05d.png" \
    -y 2>&1 | grep -E "frame=|time=" || true

NUM_FRAMES=$(ls -1 "$IMAGES_DIR"/frame_*.png 2>/dev/null | wc -l)
echo "  Extracted $NUM_FRAMES frames for best quality."

if [ "$NUM_FRAMES" -lt 50 ]; then
    echo -e "${RED}ERROR: Too few frames extracted ($NUM_FRAMES).${NC}"
    exit 1
fi

# STEP 2 & 3
echo -e "${GREEN}[Step 2 & 3/5] COLMAP 3D Reconstruction...${NC}"
COLMAP_DIR="$WORK_DIR/colmap"
SPARSE_DIR="$COLMAP_DIR/sparse/0"

mkdir -p "$COLMAP_DIR" "$SPARSE_DIR"
DB_PATH="$COLMAP_DIR/database.db"

echo "  -> Feature extraction (CPU for stability)... (ETA: 5-8 mins)"
colmap feature_extractor \
    --database_path "$DB_PATH" \
    --image_path "$IMAGES_DIR" \
    --ImageReader.camera_model OPENCV \
    --ImageReader.single_camera 1 \
    --FeatureExtraction.use_gpu 0 \
    2>&1 | grep -E "Processed|Elapsed" || true

echo "  -> Sequential matching (Video mode)... (ETA: 10-15 mins)"
colmap sequential_matcher \
    --database_path "$DB_PATH" \
    --SequentialMatching.overlap 10 \
    --SequentialMatching.quadratic_overlap 1 \
    --FeatureMatching.use_gpu 0 \
    2>&1 | grep -E "Matching|Elapsed" || true

echo "  -> Sparse mapping (3D Reconstruction)... (ETA: 15-20 mins)"
colmap mapper \
    --database_path "$DB_PATH" \
    --image_path "$IMAGES_DIR" \
    --output_path "$SPARSE_DIR/../" \
    --Mapper.ba_global_max_num_iterations 50 \
    --Mapper.ba_global_max_refinements 3 \
    2>&1 | grep -E "Registering|Elapsed" || true

BEST_MODEL=""
BEST_COUNT=0
for model_dir in "$SPARSE_DIR/../"*/; do
    if [ -f "$model_dir/images.bin" ]; then
        COUNT=$(python3 -c "import struct; f=open('${model_dir}images.bin', 'rb'); print(struct.unpack('<Q', f.read(8))[0]); f.close()" 2>/dev/null || echo "0")
        if [ "$COUNT" -gt "$BEST_COUNT" ]; then
            BEST_COUNT=$COUNT
            BEST_MODEL="$model_dir"
        fi
    fi
done

if [ -n "$BEST_MODEL" ] && [ "$(basename "$BEST_MODEL")" != "0" ]; then
    rm -rf "$SPARSE_DIR"
    cp -r "$BEST_MODEL" "$SPARSE_DIR"
fi

echo "  Registered $BEST_COUNT images successfully!"

colmap model_converter --input_path "$SPARSE_DIR" --output_path "$SPARSE_DIR" --output_type TXT >/dev/null 2>&1

# STEP 4
echo -e "${GREEN}[Step 4/5] Generating transforms for Nerfstudio... (ETA: 1 min)${NC}"
ns-process-data images \
    --data "$IMAGES_DIR" \
    --output-dir "$WORK_DIR" \
    --skip-colmap \
    --colmap-model-path colmap/sparse/0 \
    --no-gpu >/dev/null 2>&1

# STEP 5
echo -e "${GREEN}[Step 5/5] Splatfacto Training... (30,000 Iterations for MAX Quality)${NC}"
echo -e "${CYAN}Viewer available at: http://localhost:7007${NC}"
echo -e "${YELLOW}ETA: ~45-60 mins... you can track progress on the viewer and the progress bar below!${NC}"

rm -rf "$TRAIN_DIR"

ns-train splatfacto \
    --data "$WORK_DIR" \
    --output-dir "$TRAIN_DIR" \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 30000 \
    colmap

# STEP 6
echo -e "${GREEN}[Step 6/5] Exporting highest quality Web Model...${NC}"
CONFIG=$(find "$TRAIN_DIR" -name "config.yml" | tail -1)
EXPORT_DIR="namma-space-project/output-models/1"
rm -rf "$EXPORT_DIR"
mkdir -p "$EXPORT_DIR"

ns-export gaussian-splat \
    --load-config "$CONFIG" \
    --output-dir "$EXPORT_DIR"

SPLAT=$(find "$EXPORT_DIR" -name "*.ply" -o -name "*.splat" | head -n 1)
WEB_MODEL="namma-space-project/web-app/public/models/1.splat"
mkdir -p "$(dirname "$WEB_MODEL")"
cp "$SPLAT" "$WEB_MODEL"

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     TRAINING COMPLETE AND EXPORTED TO VIEWER!              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo "Model size: $(du -h $WEB_MODEL | cut -f1)"
