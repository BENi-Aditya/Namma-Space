#!/bin/bash
# Ultimate Fast GPU Training Startup Script

echo "=================================================="
echo "  🚀 Starting Ultimate GPU Training"
echo "=================================================="
echo ""

# Make sure we're in the right directory
cd ~/Downloads/Manual\ Library/Projects/3D

echo "✅ Starting training with namma-space environment"
echo ""
echo "⚠️  IMPORTANT: Open your browser to http://localhost:7007"
echo "    to watch the real-time 3D reconstruction!"
echo ""

# Use the conda environment's Python directly
~/miniforge3/envs/namma-space/bin/python3 train_ultimate_gpu_fast.py
