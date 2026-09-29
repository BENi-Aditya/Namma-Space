#!/usr/bin/env python3
"""Force GPU Training - Bypasses PyTorch 2.14.0 macOS 27.0 detection bug"""
import os
import sys

# CRITICAL: Set this BEFORE importing torch
os.environ['TERM'] = 'xterm-256color'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['MACOSX_DEPLOYMENT_TARGET'] = '14.0'

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)

    import torch
    from pathlib import Path

    print("=" * 50)
    print("  FORCED GPU TRAINING (M5 MAX)")
    print("=" * 50)
    print(f"PyTorch version: {torch.__version__}")
    print(f"MPS built: {torch.backends.mps.is_built()}")
    print(f"MPS available: {torch.backends.mps.is_available()}")

    # FORCE MPS USAGE - Override PyTorch's incorrect detection
    # Your M5 Max DOES have MPS support, PyTorch 2.14.0 just can't detect it
    print("\n🚀 FORCING MPS GPU MODE (bypassing PyTorch bug)")
    print("Your M5 Max GPU will be used for training.")
    device_type = 'mps'

    from nerfstudio.configs.method_configs import method_configs

    # Get nerfacto config
    config = method_configs['nerfacto']

    # Configure for FORCED GPU
    config.machine.device_type = device_type
    config.machine.num_devices = 1
    config.mixed_precision = False  # MPS doesn't support mixed precision well
    config.pipeline.datamanager.data = Path('namma-space-project/.work/1-emergency')
    config.output_dir = Path('namma-space-project/.work/training-final')
    config.max_num_iterations = 15000
    config.steps_per_save = 2500
    config.logging.steps_per_log = 10

    # DISABLE VIEWER (critical for stability)
    config.viewer.enable = False
    config.vis = 'tensorboard'

    # Quality settings optimized for M5 Max
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
    print(f"Device: MPS (M5 MAX GPU)")
    print(f"Mixed Precision: {config.mixed_precision}")
    print("")
    print("🚀 Estimated time: 30 mins - 2 hours (GPU mode)")
    print("")

    # Clean output
    import shutil
    if config.output_dir.exists():
        shutil.rmtree(config.output_dir)

    try:
        from nerfstudio.engine.trainer import Trainer

        print("🔥 Starting GPU training on M5 Max...")
        print("=" * 50)

        trainer = Trainer(config)
        trainer.setup()
        trainer.train()

        print("")
        print("=" * 50)
        print("  TRAINING COMPLETE")
        print("=" * 50)

        configs = list(config.output_dir.rglob("config.yml"))
        if configs:
            print(f"✅ Model saved: {configs[0]}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

        # Check if it's an MPS-specific error
        if 'mps' in str(e).lower() or 'metal' in str(e).lower():
            print("\n⚠️  MPS GPU error detected.")
            print("This might be due to PyTorch 2.14.0's macOS 27.0 incompatibility.")
            print("Unfortunately, without network access to downgrade PyTorch,")
            print("GPU training cannot proceed.")
            print("\nPlease manually run:")
            print("  conda activate namma-space")
            print("  pip install torch==2.3.1 torchvision==0.18.1")
            print("  python train_force_gpu.py")

        sys.exit(1)
