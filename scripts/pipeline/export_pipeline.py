#!/usr/bin/env python3
"""
3D Export Pipeline for Namma Space
Extracts Point Cloud from trained Nerfstudio model, reconstructs 3D Mesh, and exports STL / OBJ / PLY.
Supports interactive model selection and multi-model manifest generation.
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
import numpy as np

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

def get_ns_export_bin():
    # Try alongside python binary
    candidate = Path(sys.executable).parent / "ns-export"
    if candidate.exists():
        return str(candidate)
    which_bin = shutil.which("ns-export")
    if which_bin:
        return which_bin
    return "ns-export"

def scan_trained_models(base_dir: Path):
    """Scan base directory for all trained Nerfstudio runs containing config.yml."""
    models = []
    if not base_dir.exists():
        return models

    for config_path in base_dir.rglob("config.yml"):
        rel_parts = config_path.relative_to(base_dir).parts
        parent_dir = config_path.parent
        timestamp = parent_dir.name
        method = parent_dir.parent.name if len(rel_parts) >= 3 else "nerf"
        model_name = parent_dir.parent.parent.name if len(rel_parts) >= 4 else "model"
        
        # Check for checkpoint step
        step = "unknown"
        ckpt_dir = parent_dir / "nerfstudio_models"
        if ckpt_dir.exists():
            ckpts = sorted(ckpt_dir.glob("step-*.ckpt"))
            if ckpts:
                step = ckpts[-1].stem.replace("step-", "").lstrip("0") or "0"

        mtime = config_path.stat().st_mtime
        models.append({
            "name": model_name,
            "method": method,
            "timestamp": timestamp,
            "step": step,
            "config_path": config_path,
            "mtime": mtime,
            "display": f"{model_name} [{method} | step {step} | {timestamp}]"
        })

    models.sort(key=lambda x: x["mtime"], reverse=True)
    return models

def select_model_interactive(models):
    """Present a clean numbered CLI menu to choose which model to export."""
    if not models:
        print("❌ No trained models found in namma-space-project/.work/")
        sys.exit(1)

    print("\n📦 Available Trained Models:")
    print("═" * 60)
    for i, m in enumerate(models, 1):
        latest_tag = " ⭐ (LATEST)" if i == 1 else ""
        print(f"  [{i}] {m['display']}{latest_tag}")
    print("═" * 60)

    while True:
        try:
            choice = input(f"Select model to export [1-{len(models)}] (default: 1): ").strip()
            if not choice:
                return models[0]
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]
            print(f"Please enter a number between 1 and {len(models)}.")
        except (ValueError, KeyboardInterrupt):
            print("\nExiting.")
            sys.exit(0)

def export_pointcloud(config_path: Path, output_dir: Path, num_points: int = 150000):
    print(f"\n📦 Step 1: Extracting Dense Point Cloud ({num_points:,} points)...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ns_export_bin = get_ns_export_bin()
    cmd = [
        ns_export_bin,
        "pointcloud",
        "--load-config", str(config_path),
        "--output-dir", str(output_dir),
        "--num-points", str(num_points),
        "--normal-method", "open3d",
        "--remove-outliers", "True"
    ]
    
    env = os.environ.copy()
    env["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    env["OMP_NUM_THREADS"] = "1"
    
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print("❌ Point cloud export failed.")
        return None
        
    pcd_file = output_dir / "point_cloud.ply"
    if not pcd_file.exists():
        plys = list(output_dir.glob("*.ply"))
        if plys:
            pcd_file = plys[0]
        else:
            print("❌ Point cloud file not found.")
            return None
            
    print(f"✅ Point cloud exported to: {pcd_file}")
    return pcd_file

def generate_mesh_and_stl(pcd_path: Path, mesh_dir: Path):
    print("\n🔨 Step 2: Reconstructing 3D Surface Mesh & Generating STL...")
    mesh_dir.mkdir(parents=True, exist_ok=True)
    
    import open3d as o3d
    
    pcd = o3d.io.read_point_cloud(str(pcd_path))
    num_pts = len(pcd.points)
    print(f"   Loaded point cloud with {num_pts:,} points.")
    
    if num_pts == 0:
        print("❌ Point cloud is empty.")
        return
        
    if not pcd.has_normals():
        print("   Estimating surface normals...")
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    pcd.orient_normals_consistent_tangent_plane(10)
    
    # Statistical Outlier Removal
    pcd_clean, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    
    # Compute point distances for Ball Pivoting radii
    distances = pcd_clean.compute_nearest_neighbor_distance()
    avg_dist = float(np.mean(distances))
    print(f"   Average point spacing: {avg_dist:.5f}")
    
    radii = [avg_dist * 1.5, avg_dist * 2.5, avg_dist * 4.0, avg_dist * 8.0]
    print("   Running Ball Pivoting reconstruction...")
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        pcd_clean, o3d.utility.DoubleVector(radii)
    )
    
    # Clean geometry
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    
    stl_path = mesh_dir / "model.stl"
    obj_path = mesh_dir / "model.obj"
    ply_mesh_path = mesh_dir / "model_mesh.ply"
    
    o3d.io.write_triangle_mesh(str(stl_path), mesh)
    o3d.io.write_triangle_mesh(str(obj_path), mesh)
    o3d.io.write_triangle_mesh(str(ply_mesh_path), mesh)
    
    print(f"✅ Exported STL Mesh : {stl_path} ({len(mesh.triangles):,} triangles)")
    print(f"✅ Exported OBJ Mesh : {obj_path}")
    print(f"✅ Exported PLY Mesh : {ply_mesh_path}")

def update_manifest(output_base: Path, model_info: dict):
    """Update models.json manifest with all available exported models."""
    manifest_file = output_base / "models.json"
    data = {"models": []}
    if manifest_file.exists():
        try:
            with open(manifest_file, "r") as f:
                data = json.load(f)
        except Exception:
            data = {"models": []}
            
    entry_id = model_info["name"]
    new_entry = {
        "id": entry_id,
        "name": model_info["name"].replace("-", " ").title(),
        "method": model_info["method"],
        "step": model_info["step"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stl": f"models/{entry_id}/mesh/model.stl",
        "ply_mesh": f"models/{entry_id}/mesh/model_mesh.ply",
        "pointcloud": f"models/{entry_id}/pointcloud/point_cloud.ply",
        "obj": f"models/{entry_id}/mesh/model.obj"
    }
    
    models_list = [m for m in data.get("models", []) if m.get("id") != entry_id]
    models_list.insert(0, new_entry)
    data["models"] = models_list
    data["latest"] = entry_id
    
    with open(manifest_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"📋 Updated web manifest: {manifest_file}")

def main():
    parser = argparse.ArgumentParser(description="Export 3D Nerfstudio model to STL/OBJ/PLY")
    parser.add_argument("--config", type=str, default=None, help="Path to config.yml")
    parser.add_argument("--output-base", type=str, default="/Users/tripathd/Downloads/Manual Library/Projects/3D/namma-space-project/output-models")
    parser.add_argument("--num-points", type=int, default=150000)
    parser.add_argument("--non-interactive", action="store_true", help="Don't prompt for model selection")
    args = parser.parse_args()
    
    base_work_dir = Path("/Users/tripathd/Downloads/Manual Library/Projects/3D/namma-space-project/.work")
    output_base = Path(args.output_base)
    
    selected_model = None
    if args.config:
        cfg_path = Path(args.config)
        if not cfg_path.exists():
            print(f"❌ Specified config file not found: {cfg_path}")
            sys.exit(1)
        selected_model = {
            "name": cfg_path.parent.parent.parent.name if len(cfg_path.parts) >= 4 else "model",
            "method": cfg_path.parent.parent.name if len(cfg_path.parts) >= 3 else "nerf",
            "timestamp": cfg_path.parent.name,
            "step": "latest",
            "config_path": cfg_path
        }
    else:
        trained_models = scan_trained_models(base_work_dir)
        if not trained_models:
            print(f"❌ No trained models found in {base_work_dir}")
            sys.exit(1)
        if args.non_interactive:
            selected_model = trained_models[0]
        else:
            selected_model = select_model_interactive(trained_models)
            
    print(f"\n🚀 Exporting 3D assets for: {selected_model['name']} ({selected_model['method']})")
    
    model_dir_name = selected_model["name"]
    model_output_dir = output_base / "models" / model_dir_name
    
    pcd_dir = model_output_dir / "pointcloud"
    mesh_dir = model_output_dir / "mesh"
    
    root_pcd_dir = output_base / "pointcloud"
    root_mesh_dir = output_base / "mesh"
    
    pcd_file = pcd_dir / "point_cloud.ply"
    if not pcd_file.exists():
        # Check if existing in root
        existing_root_pcd = root_pcd_dir / "point_cloud.ply"
        if existing_root_pcd.exists():
            pcd_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(existing_root_pcd, pcd_file)
            print(f"ℹ️ Reusing existing point cloud for {model_dir_name}")
        else:
            pcd_file = export_pointcloud(selected_model["config_path"], pcd_dir, args.num_points)
            if not pcd_file:
                sys.exit(1)
    else:
        print(f"ℹ️ Found existing point cloud: {pcd_file}")
        
    generate_mesh_and_stl(pcd_file, mesh_dir)
    
    # Copy/mirror to root directories for default viewer loading
    root_pcd_dir.mkdir(parents=True, exist_ok=True)
    root_mesh_dir.mkdir(parents=True, exist_ok=True)
    for f in pcd_dir.glob("*.ply"):
        shutil.copy2(f, root_pcd_dir / f.name)
    for f in mesh_dir.glob("*.*"):
        shutil.copy2(f, root_mesh_dir / f.name)
        
    update_manifest(output_base, selected_model)
    
    print("\n" + "═" * 60)
    print("🎉 All 3D Exports Successfully Generated!")
    print("📁 Output Locations:")
    print(f"  • 3D Printable STL : {mesh_dir / 'model.stl'}")
    print(f"  • OBJ Mesh         : {mesh_dir / 'model.obj'}")
    print(f"  • PLY Mesh         : {mesh_dir / 'model_mesh.ply'}")
    print(f"  • Point Cloud      : {pcd_dir / 'point_cloud.ply'}")
    print("═" * 60)

if __name__ == "__main__":
    main()
