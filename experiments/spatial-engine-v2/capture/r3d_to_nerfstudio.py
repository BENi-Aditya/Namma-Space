#!/usr/bin/env python3
"""
Record3D to Nerfstudio Converter
=================================

Extracts ARKit poses, RGB frames, and LiDAR depth from .r3d files
and converts to Nerfstudio transforms.json format.

Usage:
    python r3d_to_nerfstudio.py --r3d recording.r3d --output processed/

Author: Namma Space Team
Date: 2026-09-29
"""

import argparse
import json
import zipfile
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import shutil
from PIL import Image


class R3DParser:
    """Parser for Record3D .r3d files."""

    def __init__(self, r3d_path: Path):
        self.r3d_path = r3d_path
        self.temp_dir = Path("/tmp/r3d_extract")

        if not r3d_path.exists():
            raise FileNotFoundError(f"R3D file not found: {r3d_path}")

    def extract_archive(self):
        """Extract .r3d zip archive to temp directory."""
        print(f"📦 Extracting {self.r3d_path.name}...")

        # Clean temp directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True)

        # .r3d files are zip archives
        try:
            with zipfile.ZipFile(self.r3d_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            print("✅ Extraction complete")
        except zipfile.BadZipFile:
            raise ValueError(f"Invalid .r3d file (not a zip archive): {self.r3d_path}")

    def load_metadata(self) -> Dict[str, Any]:
        """Load recording metadata."""
        metadata_path = self.temp_dir / "metadata.json"

        if not metadata_path.exists():
            print("⚠️  No metadata.json found, using defaults")
            return {
                "fps": 30,
                "width": 1920,
                "height": 1440,
                "device": "iPhone"
            }

        with open(metadata_path, 'r') as f:
            return json.load(f)

    def load_intrinsics(self) -> Dict[str, float]:
        """Load camera intrinsics."""
        intrinsics_path = self.temp_dir / "intrinsics.json"

        if not intrinsics_path.exists():
            print("⚠️  No intrinsics.json found, using defaults")
            # Default iPhone 15 Pro intrinsics (approximate)
            return {
                "fx": 1425.0,
                "fy": 1425.0,
                "cx": 960.0,
                "cy": 720.0,
                "width": 1920,
                "height": 1440
            }

        with open(intrinsics_path, 'r') as f:
            data = json.load(f)
            return {
                "fx": data.get("fx", 1425.0),
                "fy": data.get("fy", 1425.0),
                "cx": data.get("cx", 960.0),
                "cy": data.get("cy", 720.0),
                "width": data.get("width", 1920),
                "height": data.get("height", 1440)
            }

    def load_arkit_poses(self) -> List[np.ndarray]:
        """
        Load ARKit camera poses.

        Returns:
            List of 4x4 transformation matrices (camera-to-world)
        """
        poses_path = self.temp_dir / "poses" / "arkit_poses.json"

        if not poses_path.exists():
            raise FileNotFoundError(
                "No ARKit poses found. Ensure Record3D settings have "
                "'Export ARKit poses' enabled."
            )

        with open(poses_path, 'r') as f:
            poses_data = json.load(f)

        poses = []
        for pose_dict in poses_data:
            # ARKit poses are typically stored as 4x4 matrices
            if isinstance(pose_dict, list) and len(pose_dict) == 16:
                # Flat list of 16 elements (row-major)
                matrix = np.array(pose_dict).reshape(4, 4)
            elif isinstance(pose_dict, dict) and 'matrix' in pose_dict:
                matrix = np.array(pose_dict['matrix']).reshape(4, 4)
            else:
                print(f"⚠️  Skipping malformed pose: {pose_dict}")
                continue

            poses.append(matrix)

        print(f"✅ Loaded {len(poses)} ARKit poses")
        return poses

    def get_rgb_frames(self) -> List[Path]:
        """Get list of RGB frame paths."""
        rgbd_dir = self.temp_dir / "rgbd"

        if not rgbd_dir.exists():
            raise FileNotFoundError("No rgbd/ directory found in .r3d file")

        frames = sorted(rgbd_dir.glob("*.jpg")) + sorted(rgbd_dir.glob("*.png"))

        if not frames:
            raise FileNotFoundError("No RGB frames found in rgbd/")

        print(f"✅ Found {len(frames)} RGB frames")
        return frames

    def get_depth_maps(self) -> List[Path]:
        """Get list of depth map paths (optional)."""
        rgbd_dir = self.temp_dir / "rgbd"

        if not rgbd_dir.exists():
            return []

        depth_files = sorted(rgbd_dir.glob("*.depth"))

        if depth_files:
            print(f"✅ Found {len(depth_files)} LiDAR depth maps")
        else:
            print("ℹ️  No depth maps found (LiDAR may not be enabled)")

        return depth_files

    def convert_to_nerfstudio(
        self,
        output_dir: Path,
        include_depth: bool = True
    ) -> Dict[str, Any]:
        """
        Convert R3D data to Nerfstudio format.

        Args:
            output_dir: Output directory for processed data
            include_depth: Whether to export depth maps

        Returns:
            Conversion statistics
        """
        print("\n" + "=" * 60)
        print("Converting Record3D → Nerfstudio Format")
        print("=" * 60)

        # Create output structure
        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        # Extract archive
        self.extract_archive()

        # Load data
        metadata = self.load_metadata()
        intrinsics = self.load_intrinsics()
        poses = self.load_arkit_poses()
        rgb_frames = self.get_rgb_frames()
        depth_maps = self.get_depth_maps() if include_depth else []

        # Validate alignment
        if len(poses) != len(rgb_frames):
            print(f"⚠️  Pose count ({len(poses)}) != frame count ({len(rgb_frames)})")
            print(f"   Using minimum: {min(len(poses), len(rgb_frames))}")
            num_frames = min(len(poses), len(rgb_frames))
        else:
            num_frames = len(poses)

        # Copy RGB frames
        print(f"\n📸 Copying {num_frames} RGB frames...")
        frames_data = []

        for i in range(num_frames):
            src = rgb_frames[i]
            dst = images_dir / f"frame_{i:04d}.jpg"
            shutil.copy(src, dst)

            # Convert pose to Nerfstudio format
            # ARKit uses camera-to-world, Nerfstudio expects same
            transform_matrix = poses[i].tolist()

            frames_data.append({
                "file_path": f"images/frame_{i:04d}.jpg",
                "transform_matrix": transform_matrix
            })

        # Export depth maps if available
        if depth_maps and include_depth:
            print(f"\n🌊 Exporting {len(depth_maps)} depth maps...")
            depths_dir = output_dir / "depths"
            depths_dir.mkdir(exist_ok=True)

            for i in range(min(num_frames, len(depth_maps))):
                src = depth_maps[i]
                dst = depths_dir / f"frame_{i:04d}.npy"

                # Record3D depth format is typically binary float32
                try:
                    with open(src, 'rb') as f:
                        depth_data = np.frombuffer(f.read(), dtype=np.float32)
                        # Reshape to image dimensions
                        h, w = intrinsics['height'], intrinsics['width']
                        depth_image = depth_data.reshape((h, w))
                        np.save(dst, depth_image)
                except Exception as e:
                    print(f"⚠️  Failed to export depth {i}: {e}")

        # Build transforms.json
        transforms = {
            "camera_model": "OPENCV",
            "fl_x": intrinsics['fx'],
            "fl_y": intrinsics['fy'],
            "cx": intrinsics['cx'],
            "cy": intrinsics['cy'],
            "w": intrinsics['width'],
            "h": intrinsics['height'],
            "k1": 0.0,  # ARKit typically pre-undistorts
            "k2": 0.0,
            "p1": 0.0,
            "p2": 0.0,
            "frames": frames_data,
            "applied_transform": [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0]
            ],
            "ply_file_path": ""
        }

        # Save transforms.json
        transforms_path = output_dir / "transforms.json"
        with open(transforms_path, 'w') as f:
            json.dump(transforms, f, indent=2)

        print(f"✅ Saved transforms.json ({len(frames_data)} frames)")

        # Save conversion metadata
        conversion_meta = {
            "source_r3d": str(self.r3d_path),
            "converted_at": "2026-09-29",  # Would use datetime in production
            "num_frames": num_frames,
            "has_depth": bool(depth_maps and include_depth),
            "intrinsics": intrinsics,
            "metadata": metadata
        }

        meta_path = output_dir / "conversion_metadata.json"
        with open(meta_path, 'w') as f:
            json.dump(conversion_meta, f, indent=2)

        # Cleanup
        shutil.rmtree(self.temp_dir)

        print("\n" + "=" * 60)
        print("✅ Conversion Complete")
        print("=" * 60)
        print(f"Output: {output_dir}")
        print(f"Frames: {num_frames}")
        print(f"Depth maps: {'Yes' if depth_maps and include_depth else 'No'}")
        print(f"transforms.json: {transforms_path}")
        print("=" * 60)

        return {
            "num_frames": num_frames,
            "has_depth": bool(depth_maps and include_depth),
            "output_dir": str(output_dir)
        }


def main():
    parser = argparse.ArgumentParser(
        description="Convert Record3D .r3d files to Nerfstudio format"
    )
    parser.add_argument(
        "--r3d",
        type=Path,
        required=True,
        help="Input .r3d file from Record3D app"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory for Nerfstudio data"
    )
    parser.add_argument(
        "--no-depth",
        action="store_true",
        help="Skip exporting depth maps (faster)"
    )

    args = parser.parse_args()

    # Parse and convert
    try:
        parser_obj = R3DParser(args.r3d)
        result = parser_obj.convert_to_nerfstudio(
            output_dir=args.output,
            include_depth=not args.no_depth
        )

        print(f"\n✅ Ready for Nerfstudio training:")
        print(f"   ns-train splatfacto --data {args.output}")

        return 0
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
