#!/bin/bash

# ==============================================================================
# NAMMA SPACE - FIXED SETUP SCRIPT FOR M5 MAX
# IIT Bombay Techfest 2026-27
# ==============================================================================
# This version fixes the rawpy compilation issue on Apple Silicon
# ==============================================================================

set -e

echo "=================================================="
echo "Namma Space - Development Environment Setup"
echo "M5 Max Compatible Version"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This script is designed for macOS${NC}"
    exit 1
fi

# Check for Homebrew
echo -e "${YELLOW}[1/8] Checking Homebrew...${NC}"
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo -e "${GREEN}✓ Homebrew already installed${NC}"
fi

# Install system dependencies
echo -e "${YELLOW}[2/8] Installing system dependencies...${NC}"

# Install COLMAP
if ! command -v colmap &> /dev/null; then
    brew install colmap
    echo -e "${GREEN}✓ COLMAP installed${NC}"
else
    echo -e "${GREEN}✓ COLMAP already installed${NC}"
fi

# Install ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    brew install ffmpeg
    echo -e "${GREEN}✓ ffmpeg installed${NC}"
else
    echo -e "${GREEN}✓ ffmpeg already installed${NC}"
fi

# Install jpeg library (fixes rawpy issue)
echo -e "${YELLOW}[3/8] Installing JPEG library for rawpy fix...${NC}"
brew install jpeg-turbo
export LDFLAGS="-L/opt/homebrew/opt/jpeg-turbo/lib"
export CPPFLAGS="-I/opt/homebrew/opt/jpeg-turbo/include"
echo -e "${GREEN}✓ JPEG library installed${NC}"

# Check for conda
echo -e "${YELLOW}[4/8] Checking Conda/Miniconda...${NC}"
if ! command -v conda &> /dev/null; then
    echo -e "${RED}Conda not found. Installing Miniforge (Apple Silicon optimized)...${NC}"

    # Download Miniforge (conda optimized for Apple Silicon)
    curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
    bash Miniforge3-MacOSX-arm64.sh -b -p $HOME/miniforge3
    rm Miniforge3-MacOSX-arm64.sh

    # Initialize conda
    $HOME/miniforge3/bin/conda init bash

    echo -e "${YELLOW}Please close and reopen your terminal, then run this script again.${NC}"
    exit 0
else
    echo -e "${GREEN}✓ Conda found${NC}"
fi

# Create conda environment
echo -e "${YELLOW}[5/8] Creating conda environment 'namma-space'...${NC}"
eval "$(conda shell.bash hook)"

if conda env list | grep -q "namma-space"; then
    echo "Environment 'namma-space' already exists."
    read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        conda env remove -n namma-space -y
        conda create -n namma-space python=3.10 -y
    fi
else
    conda create -n namma-space python=3.10 -y
fi

echo -e "${GREEN}✓ Environment ready${NC}"

# Activate environment
echo -e "${YELLOW}[6/8] Activating environment and installing packages...${NC}"
conda activate namma-space

# Install PyTorch (Apple Silicon optimized)
echo "Installing PyTorch for Apple Silicon..."
pip install --upgrade pip
pip install torch torchvision torchaudio

# Install nerfstudio WITHOUT rawpy first
echo -e "${YELLOW}[7/8] Installing nerfstudio (this may take 5-10 minutes)...${NC}"

# Install nerfstudio dependencies manually to avoid rawpy
pip install tyro omegaconf tensorboard
pip install rich opencv-python Pillow
pip install mediapy imageio imageio-ffmpeg
pip install plotly scipy scikit-image
pip install open3d lpips

# Install nerfstudio without optional dependencies
pip install nerfstudio --no-deps

# Install remaining required dependencies
pip install gsplat jaxtyping trimesh
pip install nerfacc

# Try installing rawpy with explicit flags (may still fail, but nerfstudio works without it)
echo -e "${YELLOW}[8/8] Attempting to install rawpy (optional - failure is OK)...${NC}"
LDFLAGS="-L/opt/homebrew/opt/jpeg-turbo/lib" \
CPPFLAGS="-I/opt/homebrew/opt/jpeg-turbo/include" \
pip install rawpy || echo -e "${YELLOW}⚠ rawpy failed (this is OK - nerfstudio will work without it)${NC}"

echo -e "${GREEN}✓ Nerfstudio installed${NC}"

# Check for Node.js
echo -e "${YELLOW}[Node.js] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Installing via Homebrew..."
    brew install node
    echo -e "${GREEN}✓ Node.js installed${NC}"
else
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✓ Node.js already installed (${NODE_VERSION})${NC}"
fi

# Create project structure
echo -e "${YELLOW}Creating project structure...${NC}"
cd "/Users/tripathd/Downloads/Manual Library/Projects/3D"
mkdir -p namma-space-project/{input-videos,output-models,.temp-processing,.temp-training}

echo -e "${GREEN}✓ Project structure created${NC}"

# Test nerfstudio installation
echo ""
echo -e "${YELLOW}Testing nerfstudio installation...${NC}"
if python -c "import nerfstudio" 2>/dev/null; then
    echo -e "${GREEN}✓ Nerfstudio imports successfully${NC}"
else
    echo -e "${RED}✗ Nerfstudio import failed${NC}"
    exit 1
fi

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Installed components:"
echo "  ✓ COLMAP - Camera pose estimation"
echo "  ✓ ffmpeg - Video processing"
echo "  ✓ PyTorch - Machine learning framework"
echo "  ✓ Nerfstudio - 3D reconstruction"
echo "  ✓ Node.js - Web development"
echo ""
echo "Next steps:"
echo ""
echo "1. Record video on iPhone 15 Pro (2-3 minutes)"
echo "2. Transfer to: namma-space-project/input-videos/"
echo "3. Run: ./run.sh"
echo ""
echo -e "${YELLOW}Note: In each new terminal, activate environment with:${NC}"
echo "      conda activate namma-space"
echo ""
echo -e "${GREEN}Ready to capture your first 3D space! 🚀${NC}"
echo ""
