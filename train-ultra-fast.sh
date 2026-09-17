#!/bin/bash
# ULTRA-FAST TRAINING - Interactive Video Selection & Optimized NeRF Training
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

export TERM=xterm-256color
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=1
export PYTORCH_ENABLE_MPS_FALLBACK=1
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"

echo "=================================================="
echo "🎬 Namma Space - Interactive Video Training Setup"
echo "=================================================="
echo ""

# Scan for video files
VIDEO_DIR="namma-space-project/input-videos"
mkdir -p "$VIDEO_DIR"

VIDEOS=()
while IFS= read -r -d $'\0' file; do
    VIDEOS+=("$file")
done < <(find "$VIDEO_DIR" -type f \( -name "*.mov" -o -name "*.mp4" -o -name "*.m4v" -o -name "*.avi" -o -name "*.MOV" -o -name "*.MP4" \) -print0 2>/dev/null)

if [ ${#VIDEOS[@]} -eq 0 ]; then
    echo "❌ No video files found in: $VIDEO_DIR"
    echo "Please drop your video file (.mov or .mp4) into: $VIDEO_DIR"
    exit 1
fi

echo "📹 Available Input Videos:"
echo "--------------------------------------------------"
for i in "${!VIDEOS[@]}"; do
    VFILE="${VIDEOS[$i]}"
    VNAME=$(basename "$VFILE")
    VSIZE=$(du -h "$VFILE" | cut -f1)
    NUM=$((i + 1))
    if [ $i -eq 0 ]; then
        echo "  [$NUM] $VNAME ($VSIZE) ⭐ (DEFAULT)"
    else
        echo "  [$NUM] $VNAME ($VSIZE)"
    fi
done
echo "--------------------------------------------------"

read -p "Select video to train [1-${#VIDEOS[@]}] (default 1): " CHOICE
CHOICE=${CHOICE:-1}

if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt "${#VIDEOS[@]}" ]; then
    echo "⚠️ Invalid choice '$CHOICE'. Using option 1."
    SELECTED_INDEX=0
else
    SELECTED_INDEX=$((CHOICE - 1))
fi

SELECTED_VIDEO="${VIDEOS[$SELECTED_INDEX]}"
VIDEO_BASENAME=$(basename "$SELECTED_VIDEO")
ROOM_NAME="${VIDEO_BASENAME%.*}"

echo ""
echo "✅ Selected Video: $VIDEO_BASENAME"
echo "📁 Project Name  : $ROOM_NAME"
echo ""

DATA_DIR="namma-space-project/.work/$ROOM_NAME"
OUTPUT_TRAIN_DIR="namma-space-project/.work/training-fast/$ROOM_NAME"

# Check if COLMAP data already exists for this video
if [ ! -d "$DATA_DIR/sparse" ] && [ ! -d "$DATA_DIR/colmap" ]; then
    echo "🔍 COLMAP data not found for $ROOM_NAME. Running frame extraction and COLMAP..."
    ns-process-data video \
        --data "$SELECTED_VIDEO" \
        --output-dir "$DATA_DIR" \
        --num-frames-target 300 \
        --verbose
else
    echo "ℹ️ Using existing COLMAP data in: $DATA_DIR"
fi

echo ""
echo "🚀 Starting Nerfacto Training (3,000 steps)..."
echo ""

ns-train nerfacto \
    --data "$DATA_DIR" \
    --output-dir "$OUTPUT_TRAIN_DIR" \
    --viewer.quit-on-train-completion True \
    --max-num-iterations 3000 \
    --pipeline.datamanager.train-num-rays-per-batch 2048 \
    --pipeline.model.num-nerf-samples-per-ray 32 \
    --pipeline.model.num-proposal-samples-per-ray 64 32 \
    --steps-per-eval-image 500 \
    --steps-per-save 1000 \
    colmap

echo ""
echo "🎉 Training complete! Running 3D Export Pipeline..."
python export_pipeline.py --config "$(find "$OUTPUT_TRAIN_DIR" -name "config.yml" | tail -1)"

echo ""
echo "✅ All done! To view your model:"
echo "   ./view-mesh.sh"
echo ""
