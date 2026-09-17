#!/bin/bash
# Namma Space - Interactive Training Launcher
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

export TERM=xterm-256color
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=1
export PYTORCH_ENABLE_MPS_FALLBACK=1
mkdir -p "$TMPDIR/torch_cache"
export TORCH_HOME="$TMPDIR/torch_cache"

VIDEO_DIR="namma-space-project/input-videos"
mkdir -p "$VIDEO_DIR"

VIDEOS=()
while IFS= read -r -d $'\0' file; do
    VIDEOS+=("$file")
done < <(find "$VIDEO_DIR" -type f \( -name "*.mov" -o -name "*.mp4" -o -name "*.m4v" -o -name "*.avi" -o -name "*.MOV" -o -name "*.MP4" \) -print0 2>/dev/null)

if [ ${#VIDEOS[@]} -eq 0 ]; then
    echo "❌ No video files found in $VIDEO_DIR"
    exit 1
fi

echo "📹 Available Videos for Training:"
echo "--------------------------------------------------"
for i in "${!VIDEOS[@]}"; do
    VFILE="${VIDEOS[$i]}"
    VNAME=$(basename "$VFILE")
    VSIZE=$(du -h "$VFILE" | cut -f1)
    NUM=$((i + 1))
    echo "  [$NUM] $VNAME ($VSIZE)"
done
echo "--------------------------------------------------"

read -p "Select video [1-${#VIDEOS[@]}] (default 1): " CHOICE
CHOICE=${CHOICE:-1}

if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt "${#VIDEOS[@]}" ]; then
    SELECTED_INDEX=0
else
    SELECTED_INDEX=$((CHOICE - 1))
fi

SELECTED_VIDEO="${VIDEOS[$SELECTED_INDEX]}"
VIDEO_BASENAME=$(basename "$SELECTED_VIDEO")
ROOM_NAME="${VIDEO_BASENAME%.*}"

echo ""
echo "🚀 Training model for: $ROOM_NAME"
./train-ultra-fast.sh
