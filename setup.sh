#!/bin/bash

# Namma Space - Automated Setup Script
# IIT Bombay Techfest 2026-27
# This script sets up the complete development environment for 3D reconstruction and web viewer

set -e  # Exit on any error

echo "=================================================="
echo "Namma Space - Development Environment Setup"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This script is designed for macOS${NC}"
    exit 1
fi

# Check for Homebrew
echo -e "${YELLOW}[1/7] Checking Homebrew...${NC}"
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo -e "${GREEN}✓ Homebrew already installed${NC}"
fi

# Install system dependencies
echo -e "${YELLOW}[2/7] Installing system dependencies (COLMAP, ffmpeg)...${NC}"
if ! command -v colmap &> /dev/null; then
    brew install colmap
    echo -e "${GREEN}✓ COLMAP installed${NC}"
else
    echo -e "${GREEN}✓ COLMAP already installed${NC}"
fi

if ! command -v ffmpeg &> /dev/null; then
    brew install ffmpeg
    echo -e "${GREEN}✓ ffmpeg installed${NC}"
else
    echo -e "${GREEN}✓ ffmpeg already installed${NC}"
fi

# Check for conda
echo -e "${YELLOW}[3/7] Checking Conda/Miniconda...${NC}"
if ! command -v conda &> /dev/null; then
    echo "Conda not found. Please install Miniconda from:"
    echo "https://docs.conda.io/en/latest/miniconda.html"
    echo ""
    echo "After installation, run this script again."
    exit 1
else
    echo -e "${GREEN}✓ Conda found${NC}"
fi

# Create conda environment
echo -e "${YELLOW}[4/7] Creating conda environment 'namma-space'...${NC}"
if conda env list | grep -q "namma-space"; then
    echo "Environment 'namma-space' already exists. Skipping creation."
else
    conda create -n namma-space python=3.10 -y
    echo -e "${GREEN}✓ Environment created${NC}"
fi

# Activate environment and install nerfstudio
echo -e "${YELLOW}[5/7] Installing nerfstudio...${NC}"
eval "$(conda shell.bash hook)"
conda activate namma-space

# Install PyTorch first (for Apple Silicon)
pip install --upgrade pip
pip install torch torchvision

# Install nerfstudio
pip install nerfstudio

echo -e "${GREEN}✓ Nerfstudio installed${NC}"

# Create project structure
echo -e "${YELLOW}[6/7] Creating project structure...${NC}"
mkdir -p namma-space/{data,exports,web-viewer,docs}
mkdir -p namma-space/data/{raw-videos,processed}
mkdir -p namma-space/exports/{models,navmeshes}

echo -e "${GREEN}✓ Project structure created${NC}"

# Check for Node.js
echo -e "${YELLOW}[7/7] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Installing via Homebrew..."
    brew install node
    echo -e "${GREEN}✓ Node.js installed${NC}"
else
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✓ Node.js already installed (${NODE_VERSION})${NC}"
fi

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Activate the environment: conda activate namma-space"
echo "2. Navigate to project: cd namma-space"
echo "3. Follow capture_sop.md to record your first space"
echo "4. Process video with: ns-process-data video --data data/raw-videos/video.mp4 --output-dir data/processed/room1"
echo "5. Train model with: ns-train splatfacto --data data/processed/room1"
echo ""
echo "Web viewer setup:"
echo "1. cd web-viewer"
echo "2. npm install"
echo "3. npm run dev"
echo ""
echo -e "${YELLOW}Note: Conda environment needs to be activated in each new terminal:${NC}"
echo "      conda activate namma-space"
echo ""
