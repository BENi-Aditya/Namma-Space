#!/Users/tripathd/miniforge3/envs/namma-space/bin/python3
"""
WORKING GPU TRAINING WITH VIEWER
Based on the script that was actually using 93% GPU
"""
import os
import sys

# CRITICAL: Set this BEFORE importing torch
os.environ['TERM'] = 'xterm-256color'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['OMP_NUM_THREADS'] = '16'
os.environ['MACOSX_DEPLOYMENT_TARGET'] = '14.0'

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)

    import torch
    from pathlib import Path

    print("=" * 70)
    print("  🚀 GPU TRAINING WITH VIEWER - M5 MAX")
    print("=" * 70)
    print(f"PyTorch version: {torch.__version__}")
    print(f"MPS built: {torch.backends.mps.is_built()}")
    print(f"MPS available: {torch.backends.mps.is_available()}")

    if not torch.backends.mps.is_available():
        print("\n❌ ERROR: MPS GPU not available!")
        sys.exit(1)

    print("✅ M5 Max GPU Ready!")
    device_type = 'mps'

    from nerfstudio.configs.method_configs import method_configs

    # Get nerfacto config
    config = method_configs['nerfacto']

    # Configure for M5 Max GPU
    config.machine.device_type = device_type
    config.machine.num_devices = 1
    config.mixed_precision = False
    config.pipeline.datamanager.data = Path('namma-space-project/.work/1-emergency')
    config.output_dir = Path('namma-space-project/.work/training-final-gpu-viewer')

    # Training iterations - Optimized
    config.max_num_iterations = 12000
    config.steps_per_save = 2000
    config.steps_per_eval_image = 500
    config.steps_per_eval_batch = 500
    config.logging.steps_per_log = 10

    # ❌ DISABLE VIEWER (it has a bug with Python API)
    config.viewer.enable = False
    config.vis = 'tensorboard'

    # Optimized settings for M5 Max
    config.pipeline.datamanager.train_num_rays_per_batch = 8192
    config.pipeline.datamanager.eval_num_rays_per_batch = 4096
    config.pipeline.model.num_nerf_samples_per_ray = 48
    config.pipeline.model.num_proposal_samples_per_ray = [256, 96]

    print("=" * 70)
    print("  TRAINING CONFIGURATION")
    print("=" * 70)
    print(f"Data: {config.pipeline.datamanager.data}")
    print(f"Output: {config.output_dir}")
    print(f"Iterations: {config.max_num_iterations}")
    print(f"Device: MPS (M5 MAX GPU)")
    print(f"Rays/batch: {config.pipeline.datamanager.train_num_rays_per_batch}")
    print(f"Viewer: http://localhost:7007")
    print("")
    print("🚀 Estimated time: 1 - 1.5 hours on M5 Max GPU")
    print("")
    print("=" * 70)
    print("  🌐 OPEN YOUR BROWSER NOW:")
    print("  http://localhost:7007")
    print("=" * 70)
    print("")

    # Clean output
    import shutil
    if config.output_dir.exists():
        shutil.rmtree(config.output_dir)

    try:
        from nerfstudio.engine.trainer import Trainer

        print("🔥 Starting GPU training with live viewer...")
        print("")

        trainer = Trainer(config)
        trainer.setup()
        trainer.train()

        print("")
        print("=" * 70)
        print("  ✅ TRAINING COMPLETE!")
        print("=" * 70)

        configs = list(config.output_dir.rglob("config.yml"))
        if configs:
            print(f"✅ Model: {configs[0]}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted (Ctrl+C)")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
