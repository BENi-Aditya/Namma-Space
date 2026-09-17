#!/bin/bash

# ==============================================================================
# NAMMA SPACE - CLEAN INSTALL (Apple Silicon Native)
# IIT Bombay Techfest 2026-27
# ==============================================================================
# This removes old environments and does a fresh Apple Silicon native install
# ==============================================================================

set -e

echo "=================================================="
echo "Namma Space - Clean Install for Apple Silicon"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# ==============================================================================
# STEP 1: Remove old environment
# ==============================================================================

echo -e "${YELLOW}[1/6] Cleaning up old environment...${NC}"

# Check if conda exists
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"

    # Remove old namma-space environment if it exists
    if conda env list | grep -q "namma-space"; then
        echo "Removing old namma-space environment..."
        conda env remove -n namma-space -y
        echo -e "${GREEN}✓ Old environment removed${NC}"
    else
        echo "No old environment found."
    fi
fi

# ==============================================================================
# STEP 2: Install/Check Miniforge (ARM64 native)
# ==============================================================================

echo ""
echo -e "${YELLOW}[2/6] Setting up Miniforge (Apple Silicon native)...${NC}"

MINIFORGE_PATH="$HOME/miniforge3"

if [ ! -d "$MINIFORGE_PATH" ]; then
    echo "Installing Miniforge (Apple Silicon optimized)..."
    curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
    bash Miniforge3-MacOSX-arm64.sh -b -p "$MINIFORGE_PATH"
    rm Miniforge3-MacOSX-arm64.sh

    # Initialize
    "$MINIFORGE_PATH/bin/conda" init bash

    echo -e "${GREEN}✓ Miniforge installed${NC}"
    echo -e "${YELLOW}Please run: source ~/.bash_profile (or restart terminal)${NC}"
    echo -e "${YELLOW}Then run this script again.${NC}"
    exit 0
else
    echo -e "${GREEN}✓ Miniforge already installed${NC}"
fi

# Use miniforge's conda
export PATH="$MINIFORGE_PATH/bin:$PATH"
eval "$(conda shell.bash hook)"

# ==============================================================================
# STEP 3: Install Homebrew dependencies
# ==============================================================================

echo ""
echo -e "${YELLOW}[3/6] Installing Homebrew dependencies...${NC}"

# Install COLMAP (force overwrite to fix conflicts)
brew install colmap || brew link --overwrite colmap
echo -e "${GREEN}✓ COLMAP ready${NC}"

# Install ffmpeg
brew install ffmpeg
echo -e "${GREEN}✓ ffmpeg ready${NC}"

# Install Node.js
if ! command -v node &> /dev/null; then
    brew install node
fi
echo -e "${GREEN}✓ Node.js ready${NC}"

# ==============================================================================
# STEP 4: Create fresh environment
# ==============================================================================

echo ""
echo -e "${YELLOW}[4/6] Creating fresh namma-space environment...${NC}"

conda create -n namma-space python=3.10 -y
conda activate namma-space

echo -e "${GREEN}✓ Environment created${NC}"

# ==============================================================================
# STEP 5: Install Python packages (ARM64 native)
# ==============================================================================

echo ""
echo -e "${YELLOW}[5/6] Installing Python packages (this takes 5-10 minutes)...${NC}"

# Upgrade pip
pip install --upgrade pip

# Install PyTorch (Apple Silicon optimized)
echo "Installing PyTorch..."
pip install torch torchvision torchaudio

# Install scipy/numpy (ARM64 builds from conda-forge)
echo "Installing scientific Python packages..."
conda install -c conda-forge numpy scipy scikit-learn -y

# Install nerfstudio core dependencies
echo "Installing nerfstudio dependencies..."
pip install tyro omegaconf tensorboard
pip install rich opencv-python Pillow
pip install mediapy imageio imageio-ffmpeg
pip install plotly

# Install open3d (skip if it causes issues - not critical)
pip install open3d || echo -e "${YELLOW}⚠ open3d skipped (optional)${NC}"

# Install 3D libraries
pip install lpips trimesh
pip install gsplat jaxtyping
pip install nerfacc

# Install nerfstudio
echo "Installing nerfstudio..."
pip install nerfstudio

echo -e "${GREEN}✓ All packages installed${NC}"

# ==============================================================================
# STEP 6: Test installation
# ==============================================================================

echo ""
echo -e "${YELLOW}[6/6] Testing installation...${NC}"

# Test nerfstudio import
if python -c "import nerfstudio; import torch; print(f'PyTorch: {torch.__version__}'); print(f'MPS available: {torch.backends.mps.is_available()}')" 2>/dev/null; then
    echo -e "${GREEN}✓ Nerfstudio working!${NC}"
    echo -e "${GREEN}✓ Apple Silicon GPU (MPS) detected!${NC}"
else
    echo -e "${RED}✗ Import test failed${NC}"
    exit 1
fi

# Create project structure
echo ""
echo -e "${YELLOW}Creating project structure...${NC}"
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
mkdir -p namma-space-project/{input-videos,output-models,.temp-processing,.temp-training}

# ==============================================================================
# SUMMARY
# ==============================================================================

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Clean Installation Complete!${NC}"
echo "=================================================="
echo ""
echo "Your setup:"
echo "  - Miniforge (Apple Silicon native conda)"
echo "  - Python 3.10 with ARM64 packages"
echo "  - PyTorch with MPS (Metal Performance Shaders)"
echo "  - Nerfstudio + all dependencies"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo ""
echo "1. Record video on iPhone (2-3 min, 4K 30fps)"
echo "2. Copy to: namma-space-project/input-videos/"
echo "3. Run: ./run.sh"
echo ""
echo -e "${YELLOW}In new terminals, activate with:${NC}"
echo "   conda activate namma-space"
echo ""
echo -e "${GREEN}Ready to create your first 3D model! 🚀${NC}"
echo ""
