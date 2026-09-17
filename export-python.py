#!/usr/bin/env python3
"""Export trained NeRF model as point cloud using Python API."""
import sys
import os
import warnings
warnings.filterwarnings("ignore")

os.chdir("/Users/tripathd/Downloads/Manual Library/Projects/3D")
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import torch

print("Loading checkpoint...")
ckpt_path = "namma-space-project/.work/training-fast/your-video/nerfacto/2026-09-13_154156/nerfstudio_models/step-000002999.ckpt"
ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
print(f"Checkpoint keys: {list(ckpt.keys()) if isinstance(ckpt, dict) else type(ckpt)}")

if isinstance(ckpt, dict):
    print(f"Top-level sub-keys: {list(ckpt.keys())}")
    if "model_state_dict" in ckpt:
        print(f"Model state dict keys (first 10): {list(ckpt['model_state_dict'].keys())[:10]}")
    if "pipeline" in ckpt:
        print(f"Pipeline type: {type(ckpt['pipeline'])}")
