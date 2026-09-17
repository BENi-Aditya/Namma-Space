#!/bin/bash
# Instant 3D Mesh & STL Web Viewer with Interactive Model Picker
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D/namma-space-project/output-models"

PORT=8080
echo "=================================================="
echo "🌟 Namma Space - 3D Studio Model Viewer"
echo "=================================================="
echo ""

# Scan for models in models/ directory
MODEL_DIRS=()
if [ -d "models" ]; then
    for d in models/*; do
        if [ -d "$d" ]; then
            MODEL_DIRS+=("$(basename "$d")")
        fi
    done
fi

SELECTED_MODEL=""
if [ ${#MODEL_DIRS[@]} -gt 1 ]; then
    echo "📦 Available Exported 3D Models:"
    echo "--------------------------------------------------"
    for i in "${!MODEL_DIRS[@]}"; do
        MNAME="${MODEL_DIRS[$i]}"
        NUM=$((i + 1))
        if [ $i -eq 0 ]; then
            echo "  [$NUM] $MNAME ⭐ (LATEST)"
        else
            echo "  [$NUM] $MNAME"
        fi
    done
    echo "--------------------------------------------------"
    read -p "Select model to view [1-${#MODEL_DIRS[@]}] (default 1): " CHOICE
    CHOICE=${CHOICE:-1}
    if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt "${#MODEL_DIRS[@]}" ]; then
        SELECTED_MODEL="${MODEL_DIRS[0]}"
    else
        SELECTED_MODEL="${MODEL_DIRS[$((CHOICE - 1))]}"
    fi
elif [ ${#MODEL_DIRS[@]} -eq 1 ]; then
    SELECTED_MODEL="${MODEL_DIRS[0]}"
fi

URL="http://localhost:$PORT/viewer.html"
if [ -n "$SELECTED_MODEL" ]; then
    URL="http://localhost:$PORT/viewer.html?model=$SELECTED_MODEL"
    echo "✅ Selected Model: $SELECTED_MODEL"
fi

echo "🌐 Opening 3D Studio at: $URL"
echo ""

(sleep 1 && open "$URL") &

python3 -m http.server $PORT
