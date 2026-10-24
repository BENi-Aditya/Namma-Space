#!/usr/bin/env python3
"""Initialize PyTorch before Open3D on macOS to avoid a native import crash.

Keep this in a separate process: training and export have separate resource lifetimes.
The stock ns-export CLI imports Open3D first; this wrapper uses the same entrypoint.
"""
import torch  # noqa: F401 -- import order is intentional
from nerfstudio.scripts.exporter import entrypoint

if __name__ == '__main__':
    entrypoint()
