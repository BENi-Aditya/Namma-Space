#!/bin/bash
# Fix PyTorch for macOS 27.0 and start training with web viewer

set -e

echo "=================================================="
echo "  M5 Max GPU Training Setup & Start"
echo "  With Real-Time Web Viewer"
echo "=================================================="
echo ""

# Activate conda environment
echo "Activating namma-space environment..."
source ~/miniforge3/bin/activate namma-space

echo ""
echo "Step 1: Downgrading PyTorch to 2.3.1..."
echo "This fixes the macOS 27.0 detection bug and enables your M5 Max GPU"
echo ""

# Downgrade PyTorch
pip install --upgrade --force-reinstall torch==2.3.1 torchvision==0.18.1

echo ""
echo "✅ PyTorch 2.3.1 installed!"
echo ""
echo "Step 2: Starting training with web viewer..."
echo "Open your browser to: http://localhost:7007"
echo ""
echo "🚀 Training will take 30 mins - 2 hours on GPU"
echo "You'll see real-time 3D rendering as it trains!"
echo ""

# Start training with viewer enabled
python3 train_gpu_with_viewer.py
