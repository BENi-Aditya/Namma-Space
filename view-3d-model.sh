#!/bin/bash
# Interactive 3D Viewer - loads trained Nerfstudio model with run selection
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
source /Users/tripathd/miniforge3/etc/profile.d/conda.sh
conda activate namma-space

export TERM=xterm-256color
export CUDA_VISIBLE_DEVICES=""
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=1

echo "=================================================="
echo "🎮 Namma Space - Interactive NeRF Viewer"
echo "=================================================="
echo ""

# Scan for all config.yml files in .work
CONFIGS=()
while IFS= read -r -d $'\0' file; do
    CONFIGS+=("$file")
done < <(find "namma-space-project/.work" -name "config.yml" -print0 2>/dev/null)

if [ ${#CONFIGS[@]} -eq 0 ]; then
    echo "❌ No trained models found in namma-space-project/.work/"
    exit 1
fi

echo "📦 Available Trained Models:"
echo "--------------------------------------------------"
for i in "${!CONFIGS[@]}"; do
    CFG="${CONFIGS[$i]}"
    # Extract details: .work/<run_dir>/<name>/<method>/<timestamp>/config.yml
    PARTS=$(dirname "$CFG")
    TS=$(basename "$PARTS")
    METHOD=$(basename "$(dirname "$PARTS")")
    NAME=$(basename "$(dirname "$(dirname "$PARTS")")")
    NUM=$((i + 1))
    if [ $i -eq 0 ]; then
        echo "  [$NUM] $NAME ($METHOD | $TS) ⭐ (DEFAULT)"
    else
        echo "  [$NUM] $NAME ($METHOD | $TS)"
    fi
done
echo "--------------------------------------------------"

read -p "Select model to view [1-${#CONFIGS[@]}] (default 1): " CHOICE
CHOICE=${CHOICE:-1}

if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt "${#CONFIGS[@]}" ]; then
    SELECTED_INDEX=0
else
    SELECTED_INDEX=$((CHOICE - 1))
fi

CONFIG="${CONFIGS[$SELECTED_INDEX]}"
echo ""
echo "🚀 Loading model: $CONFIG"
echo "⏳ Loading dataset and weights (takes ~15-20s)..."
echo "🌐 Browser will automatically open when ready at: http://localhost:7007"
echo ""

# Wait until port 7007 is active, then open browser
(
  for i in {1..60}; do
    if nc -z 127.0.0.1 7007 2>/dev/null; then
      sleep 1
      open "http://localhost:7007"
      break
    fi
    sleep 1
  done
) &

ns-viewer --load-config "$CONFIG" --viewer.websocket-port 7007
