#!/bin/bash
# Start TensorBoard to monitor training progress

source ~/miniforge3/bin/activate namma-space
cd ~/Downloads/Manual\ Library/Projects/3D

echo "=================================================="
echo "  Starting TensorBoard"
echo "=================================================="
echo ""
echo "Open your browser to: http://localhost:6006"
echo ""

tensorboard --logdir namma-space-project/.work/training-final --port 6006
