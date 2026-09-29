#!/usr/bin/env python3
"""Direct training script - bypasses ns-train to avoid viewer issues"""
import os
import sys

# Set environment FIRST
os.environ['TERM'] = 'xterm-256color'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
# REMOVED: Don't block CUDA devices for MPS
# os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OMP_NUM_THREADS'] = '8'

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)

    import torch
    from pathlib import Path
    from nerfstudio.configs.method_configs import method_configs

    # Get nerfacto config
    config = method_configs['nerfacto']

    # Override settings - ENABLE MPS GPU!
    config.machine.device_type = 'mps'  # CHANGED FROM CPU TO MPS
    config.machine.num_devices = 1
    config.mixed_precision = False  # Disable mixed precision (not supported on MPS)
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
    print("  TRAINING STARTED")
    print("=" * 50)
    print(f"Data: {config.pipeline.datamanager.data}")
    print(f"Output: {config.output_dir}")
    print(f"Iterations: {config.max_num_iterations}")
    print(f"Device: MPS (M5 Max GPU)")
    print(f"Mixed Precision: {config.mixed_precision}")
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
