#!/usr/bin/env python3
"""
Enhanced COLMAP Pipeline for Namma Space
==========================================

Improvements over baseline:
1. Sequential matching (not exhaustive) - better for video sequences
2. Higher feature density (8192 features/image vs default 4096)
3. GPU acceleration where available
4. Better matching thresholds
5. Vocabulary tree for loop closure
6. Diagnostic output for troubleshooting

Target: ≥80% frame registration (vs baseline 0.25%)
"""

import subprocess
import argparse
import json
from pathlib import Path
from typing import Dict, Any
import shutil


class EnhancedCOLMAP:
    """Enhanced COLMAP pipeline with better defaults for iPhone video."""

    def __init__(self, workspace: Path, images_dir: Path):
        self.workspace = workspace
        self.images_dir = images_dir
        self.database_path = workspace / "database.db"
        self.sparse_dir = workspace / "sparse"
        self.sparse_dir.mkdir(parents=True, exist_ok=True)

        # Enhanced feature extraction settings
        self.feature_settings = {
            "ImageReader.camera_model": "OPENCV",
            "ImageReader.single_camera": "1",
            "SiftExtraction.max_num_features": "8192",  # 2x default
            "SiftExtraction.use_gpu": "1",
            "SiftExtraction.gpu_index": "0",
            "SiftExtraction.max_image_size": "3200",
            "SiftExtraction.estimate_affine_shape": "1",
            "SiftExtraction.domain_size_pooling": "1",
        }

        # Sequential matching for video (much faster than exhaustive)
        self.matching_settings = {
            "SiftMatching.use_gpu": "1",
            "SiftMatching.gpu_index": "0",
            "SiftMatching.guided_matching": "1",
            "SiftMatching.max_ratio": "0.8",
            "SiftMatching.max_distance": "0.7",
            "SiftMatching.cross_check": "1",
            "SiftMatching.max_error": "4.0",
        }

        # Mapper settings for robust reconstruction
        self.mapper_settings = {
            "Mapper.ba_refine_focal_length": "1",
            "Mapper.ba_refine_principal_point": "0",
            "Mapper.ba_refine_extra_params": "1",
            "Mapper.ba_local_max_num_iterations": "50",
            "Mapper.ba_global_max_num_iterations": "100",
            "Mapper.min_num_matches": "15",
            "Mapper.init_min_num_inliers": "100",
            "Mapper.abs_pose_min_num_inliers": "30",
            "Mapper.abs_pose_min_inlier_ratio": "0.25",
            "Mapper.filter_max_reproj_error": "4.0",
            "Mapper.filter_min_tri_angle": "1.5",
        }

    def run_feature_extraction(self) -> bool:
        """Extract SIFT features with enhanced settings."""
        print("🔍 Extracting features (enhanced settings)...")

        cmd = ["colmap", "feature_extractor"]
        cmd.extend(["--database_path", str(self.database_path)])
        cmd.extend(["--image_path", str(self.images_dir)])

        for key, value in self.feature_settings.items():
            cmd.extend([f"--{key}", value])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Feature extraction failed: {result.stderr}")
            return False

        print("✅ Feature extraction complete")
        return True

    def run_sequential_matching(self, overlap: int = 10) -> bool:
        """
        Sequential matching for video sequences.

        Args:
            overlap: Number of consecutive frames to match (default 10)
        """
        print(f"🔗 Sequential matching (overlap={overlap})...")

        cmd = [
            "colmap", "sequential_matcher",
            "--database_path", str(self.database_path),
            "--SequentialMatching.overlap", str(overlap),
            "--SequentialMatching.loop_detection", "1",
            "--SequentialMatching.vocab_tree_path", "",  # Optional: add vocab tree path
        ]

        for key, value in self.matching_settings.items():
            cmd.extend([f"--{key}", value])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Sequential matching failed: {result.stderr}")
            return False

        print("✅ Sequential matching complete")
        return True

    def run_mapper(self) -> bool:
        """Run mapper with enhanced settings."""
        print("🗺️  Running mapper...")

        cmd = [
            "colmap", "mapper",
            "--database_path", str(self.database_path),
            "--image_path", str(self.images_dir),
            "--output_path", str(self.sparse_dir),
        ]

        for key, value in self.mapper_settings.items():
            cmd.extend([f"--{key}", value])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Mapper failed: {result.stderr}")
            return False

        print("✅ Mapper complete")
        return True

    def get_registration_stats(self) -> Dict[str, Any]:
        """Get statistics about registered images."""
        model_dir = self.sparse_dir / "0"
        images_file = model_dir / "images.txt"

        if not images_file.exists():
            return {"registered": 0, "total": 0, "rate": 0.0}

        # Count registered images (skip comments and empty lines)
        registered = 0
        with open(images_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Every image has 2 lines (metadata + points)
                    registered += 1

        # Registered images are on every other line after header
        registered = registered // 2

        # Count total images
        total = len(list(self.images_dir.glob("*.jpg"))) + \
                len(list(self.images_dir.glob("*.png")))

        rate = (registered / total * 100) if total > 0 else 0.0

        return {
            "registered": registered,
            "total": total,
            "rate": rate,
            "model_dir": str(model_dir)
        }

    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run complete enhanced COLMAP pipeline."""
        print("=" * 60)
        print("Enhanced COLMAP Pipeline for Namma Space")
        print("=" * 60)

        # Step 1: Feature extraction
        if not self.run_feature_extraction():
            return {"success": False, "error": "Feature extraction failed"}

        # Step 2: Sequential matching
        if not self.run_sequential_matching(overlap=10):
            return {"success": False, "error": "Sequential matching failed"}

        # Step 3: Mapper
        if not self.run_mapper():
            return {"success": False, "error": "Mapper failed"}

        # Step 4: Get stats
        stats = self.get_registration_stats()

        print("\n" + "=" * 60)
        print("📊 Registration Statistics")
        print("=" * 60)
        print(f"Registered: {stats['registered']} / {stats['total']} frames")
        print(f"Success Rate: {stats['rate']:.2f}%")
        print(f"Target: ≥80%")

        if stats['rate'] >= 80:
            print("✅ SUCCESS: Target achieved!")
        else:
            print(f"⚠️  Below target (need {80 - stats['rate']:.2f}% more)")

        print("=" * 60)

        return {
            "success": True,
            "stats": stats
        }


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced COLMAP pipeline for iPhone video"
    )
    parser.add_argument(
        "--images",
        type=Path,
        required=True,
        help="Directory containing extracted frames"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="COLMAP workspace directory (will contain database.db and sparse/)"
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=10,
        help="Sequential matching overlap (default: 10)"
    )

    args = parser.parse_args()

    # Validate paths
    if not args.images.exists():
        print(f"❌ Images directory not found: {args.images}")
        return 1

    args.workspace.mkdir(parents=True, exist_ok=True)

    # Run pipeline
    colmap = EnhancedCOLMAP(args.workspace, args.images)
    result = colmap.run_full_pipeline()

    # Save results
    results_file = args.workspace / "enhanced_colmap_results.json"
    with open(results_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n📄 Results saved to: {results_file}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
