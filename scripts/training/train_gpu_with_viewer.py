#!/usr/bin/env python3
"""GPU Training with Real-Time Web Viewer - Watch your 3D scene train live!"""
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

    print("=" * 60)
    print("  GPU TRAINING WITH REAL-TIME WEB VIEWER")
    print("=" * 60)
    print(f"PyTorch version: {torch.__version__}")
    print(f"MPS built: {torch.backends.mps.is_built()}")
    print(f"MPS available: {torch.backends.mps.is_available()}")

    if not torch.backends.mps.is_available():
        print("\n❌ ERROR: MPS GPU not available!")
        print("Did you run the fix script first?")
        print("Run: ./fix-pytorch-and-train-with-viewer.sh")
        sys.exit(1)

    print("✅ MPS GPU detected - M5 Max ready!")
    device_type = 'mps'

    from nerfstudio.configs.method_configs import method_configs

    # Get nerfacto config
    config = method_configs['nerfacto']

    # Configure for GPU with VIEWER ENABLED
    config.machine.device_type = device_type
    config.machine.num_devices = 1
    config.mixed_precision = False
    config.pipeline.datamanager.data = Path('namma-space-project/.work/1-emergency')
    config.output_dir = Path('namma-space-project/.work/training-final')
    config.max_num_iterations = 15000
    config.steps_per_save = 2500
    config.logging.steps_per_log = 10

    # ✨ ENABLE WEB VIEWER - Watch training in real-time! ✨
    config.viewer.enable = True
    config.viewer.websocket_port = 7007
    config.vis = 'viewer'

    # Quality settings optimized for M5 Max
    config.pipeline.datamanager.train_num_rays_per_batch = 4096
    config.pipeline.datamanager.eval_num_rays_per_batch = 2048
    config.pipeline.model.num_nerf_samples_per_ray = 64
    config.pipeline.model.num_proposal_samples_per_ray = [128, 64]

    print("=" * 60)
    print("  TRAINING CONFIGURATION")
    print("=" * 60)
    print(f"Data: {config.pipeline.datamanager.data}")
    print(f"Output: {config.output_dir}")
    print(f"Iterations: {config.max_num_iterations}")
    print(f"Device: MPS (M5 MAX GPU)")
    print(f"Viewer: ENABLED at http://localhost:7007")
    print("")
    print("🚀 Estimated time: 30 mins - 2 hours (GPU mode)")
    print("")
    print("=" * 60)
    print("  🌐 OPEN YOUR BROWSER NOW!")
    print("  http://localhost:7007")
    print("=" * 60)
    print("")
    print("You'll see your 3D scene rendering in real-time as it trains!")
    print("The view will improve every few seconds as the model learns.")
    print("")

    # Clean output
    import shutil
    if config.output_dir.exists():
        print("Cleaning previous training output...")
        shutil.rmtree(config.output_dir)

    try:
        from nerfstudio.engine.trainer import Trainer

        print("🔥 Starting GPU training with live viewer...")
        print("=" * 60)
        print("")

        trainer = Trainer(config)
        trainer.setup()
        trainer.train()

        print("")
        print("=" * 60)
        print("  ✅ TRAINING COMPLETE!")
        print("=" * 60)

        configs = list(config.output_dir.rglob("config.yml"))
        if configs:
            print(f"Model saved: {configs[0]}")
            print("")
            print("To view the final result:")
            print(f"  ns-viewer --load-config {configs[0]}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print("Progress has been saved. You can resume later.")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
