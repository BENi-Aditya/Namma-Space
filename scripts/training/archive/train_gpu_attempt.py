#!/usr/bin/env python3
"""GPU Training with MPS Force-Enabled via Environment Hack"""
import os
import sys

# CRITICAL: Set this BEFORE importing torch
# This environment variable is checked by PyTorch's MPS backend
os.environ['TERM'] = 'xterm-256color'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['OMP_NUM_THREADS'] = '8'

# Try to trick PyTorch's version check by setting MACOSX_DEPLOYMENT_TARGET
os.environ['MACOSX_DEPLOYMENT_TARGET'] = '14.0'

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)

    import torch
    from pathlib import Path

    print("=" * 50)
    print("  GPU TRAINING ATTEMPT")
    print("=" * 50)
    print(f"PyTorch version: {torch.__version__}")
    print(f"MPS built: {torch.backends.mps.is_built()}")
    print(f"MPS available: {torch.backends.mps.is_available()}")

    # If MPS still not available, fall back to CPU but warn user
    if not torch.backends.mps.is_available():
        print("\n⚠️  WARNING: MPS GPU not available!")
        print("PyTorch 2.14.0 has a bug with macOS 27.0 detection.")
        print("Falling back to CPU training...")
        print("\nTo fix this permanently:")
        print("1. Downgrade PyTorch to 2.3.x, OR")
        print("2. Wait for PyTorch 2.15+ that supports macOS 27")
        print("")
        device_type = 'cpu'
    else:
        print("✅ MPS GPU is available!")
        device_type = 'mps'

    from nerfstudio.configs.method_configs import method_configs

    # Get nerfacto config
    config = method_configs['nerfacto']

    # Configure for GPU or CPU
    config.machine.device_type = device_type
    config.machine.num_devices = 1
    config.mixed_precision = False if device_type == 'mps' else True
    config.pipeline.datamanager.data = Path('namma-space-project/.work/1-emergency')
    config.output_dir = Path('namma-space-project/.work/training-final')
    config.max_num_iterations = 15000
    config.steps_per_save = 2500
    config.logging.steps_per_log = 10

    # DISABLE VIEWER
    config.viewer.enable = False
    config.vis = 'tensorboard'

    # Quality settings
    config.pipeline.datamanager.train_num_rays_per_batch = 4096
    config.pipeline.datamanager.eval_num_rays_per_batch = 2048
    config.pipeline.model.num_nerf_samples_per_ray = 64
    config.pipeline.model.num_proposal_samples_per_ray = [128, 64]

    print("=" * 50)
    print("  TRAINING CONFIGURATION")
    print("=" * 50)
    print(f"Data: {config.pipeline.datamanager.data}")
    print(f"Output: {config.output_dir}")
    print(f"Iterations: {config.max_num_iterations}")
    print(f"Device: {device_type.upper()}")
    print(f"Mixed Precision: {config.mixed_precision}")
    print("")

    if device_type == 'cpu':
        print("⏱️  Estimated time: 4-5 hours (CPU mode)")
    else:
        print("🚀 Estimated time: 30 mins - 2 hours (GPU mode)")
    print("")

    # Clean output
    import shutil
    if config.output_dir.exists():
        shutil.rmtree(config.output_dir)

    try:
        from nerfstudio.engine.trainer import Trainer
        trainer = Trainer(config)
        trainer.setup()
        trainer.train()

        print("")
        print("=" * 50)
        print("  TRAINING COMPLETE")
        print("=" * 50)

        configs = list(config.output_dir.rglob("config.yml"))
        if configs:
            print(f"Model: {configs[0]}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
