#!/bin/bash
# Namma Space - 3D CAD Studio Web Viewer Launcher
cd "$(dirname "$0")/namma-space-project/output-models"

PORT=8080
URL="http://localhost:$PORT/viewer.html"

echo "=================================================="
echo "🌟 Launching Namma Space - 3D CAD Studio (Dark Theme)"
echo "🌐 URL: $URL"
echo "=================================================="

(sleep 1 && open "$URL") &
python3 -m http.server $PORT
