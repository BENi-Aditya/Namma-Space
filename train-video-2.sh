#!/bin/bash
set -e

echo "=================================================="
echo "🚀 Namma Space - 2.MOV High-Quality Fast GPU Pipeline"
echo "=================================================="
echo "Video: namma-space-project/input-videos/2.MOV"
echo "Training Device: Apple Silicon Metal GPU (MPS)"
echo "Target: High quality + Fast Training"
echo "=================================================="
echo ""

CONDA_BASE=$(conda info --base 2>/dev/null || echo "/Users/tripathd/miniforge3")
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate namma-space

export QT_QPA_PLATFORM=offscreen
export KMP_DUPLICATE_LIB_OK=TRUE
export PYTORCH_ENABLE_MPS_FALLBACK=1
export OMP_NUM_THREADS=8

DATA_DIR="namma-space-project/.work/2-run"
OUTPUT_DIR="namma-space-project/.work/training-2"
EXPORT_BASE="namma-space-project/output-models/models/2-run"
VIDEO_PATH="/Users/tripathd/Downloads/Manual Library/Projects/3D/namma-space-project/input-videos/2.MOV"

mkdir -p "$DATA_DIR/colmap"
mkdir -p "$OUTPUT_DIR"
mkdir -p "$EXPORT_BASE/mesh"
mkdir -p "$EXPORT_BASE/pointcloud"

# Step 1: COLMAP Structure from Motion & Feature Matching
echo "📸 [1/3] Running COLMAP Feature Extraction & Matching..."
ns-process-data video \
    --data "$VIDEO_PATH" \
    --output-dir "$DATA_DIR" \
    --num-frames-target 300 \
    --matching-method sequential \
    --camera-type perspective \
    --skip-image-processing \
    --no-gpu \
    --num-downscales 2

echo ""
echo "🔥 [2/3] Starting Apple Silicon Metal GPU NeRF Training (10,000 steps)..."
ns-train nerfacto \
    --data "$DATA_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --max-num-iterations 10000 \
    --viewer.quit-on-train-completion True \
    --machine.device-type mps \
    --machine.num-devices 1

echo ""
echo "📦 [3/3] Training finished. Exporting 3D Models & Point Clouds..."

CONFIG=$(find "$OUTPUT_DIR" -name "config.yml" -type f | sort -r | head -n 1)
if [ -z "$CONFIG" ]; then
    echo "❌ Error: config.yml not found in $OUTPUT_DIR"
    exit 1
fi
echo "Using config: $CONFIG"

# Export Dense Point Cloud
echo "Exporting dense point cloud (1M points)..."
ns-export pointcloud \
    --load-config "$CONFIG" \
    --output-dir "$EXPORT_BASE/pointcloud" \
    --num-points 1000000 \
    --remove-outliers True

# Export Mesh
echo "Exporting Poisson 3D Surface Mesh..."
ns-export poisson-mesh \
    --load-config "$CONFIG" \
    --output-dir "$EXPORT_BASE/mesh" \
    --target-num-faces 150000 \
    --remove-outliers True || true

# Copy/convert for web viewer compatibility
if [ -f "$EXPORT_BASE/mesh/poisson_mesh.ply" ]; then
    cp "$EXPORT_BASE/mesh/poisson_mesh.ply" "$EXPORT_BASE/mesh/model_mesh.ply"
elif [ -f "$EXPORT_BASE/mesh/mesh.ply" ]; then
    cp "$EXPORT_BASE/mesh/mesh.ply" "$EXPORT_BASE/mesh/model_mesh.ply"
elif [ -f "$EXPORT_BASE/pointcloud/point_cloud.ply" ]; then
    cp "$EXPORT_BASE/pointcloud/point_cloud.ply" "$EXPORT_BASE/mesh/model_mesh.ply"
fi

# Convert PLY to STL using python
python3 - << 'PYEOF'
import trimesh
import os

mesh_path = "namma-space-project/output-models/models/2-run/mesh/model_mesh.ply"
stl_path = "namma-space-project/output-models/models/2-run/mesh/model.stl"

if os.path.exists(mesh_path):
    try:
        mesh = trimesh.load(mesh_path)
        if isinstance(mesh, trimesh.Trimesh):
            mesh.export(stl_path)
            print(f"✅ Generated STL: {stl_path}")
    except Exception as e:
        print(f"STL conversion notice: {e}")
PYEOF

# Update models.json
python3 - << 'PYEOF'
import json
import os
from datetime import datetime

models_json_path = "namma-space-project/output-models/models.json"
try:
    with open(models_json_path, "r") as f:
        data = json.load(f)
except Exception:
    data = {"models": [], "latest": "2-run"}

new_entry = {
    "id": "2-run",
    "name": "2.MOV (Trained Today)",
    "method": "nerfacto",
    "step": "10,000 steps",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "stl": "models/2-run/mesh/model.stl",
    "ply_mesh": "models/2-run/mesh/model_mesh.ply",
    "pointcloud": "models/2-run/pointcloud/point_cloud.ply",
    "obj": "models/2-run/mesh/model.obj"
}

# Prepend or update
data["models"] = [m for m in data.get("models", []) if m["id"] != "2-run"]
data["models"].insert(0, new_entry)
data["latest"] = "2-run"

with open(models_json_path, "w") as f:
    json.dump(data, f, indent=2)

print("✅ Updated models.json with 2.MOV!")
PYEOF

echo ""
echo "=================================================="
echo "🎉 2.MOV Training & Export Fully Complete!"
echo "🌐 Web Viewer: http://localhost:8080/viewer.html?model=2-run"
echo "=================================================="
