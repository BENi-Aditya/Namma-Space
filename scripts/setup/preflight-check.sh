#!/bin/bash

# ==============================================================================
# NAMMA SPACE - Preflight Check
# Verifies all prerequisites before running main script
# ==============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════╗"
echo "║            NAMMA SPACE - Preflight Check                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0

# Check conda
echo -n "Checking conda... "
if command -v conda &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check conda environment
echo -n "Checking namma-space environment... "
if conda env list 2>/dev/null | grep -q "namma-space"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    echo "  Run: ./clean-install.sh"
    ERRORS=$((ERRORS + 1))
fi

# Check nerfstudio (if environment exists)
if conda env list 2>/dev/null | grep -q "namma-space"; then
    echo -n "Checking nerfstudio... "
    CONDA_BASE=$(conda info --base 2>/dev/null)
    source "$CONDA_BASE/etc/profile.d/conda.sh" 2>/dev/null
    conda activate namma-space 2>/dev/null
    if python -c "import nerfstudio" 2>/dev/null; then
        VERSION=$(python -c "import nerfstudio; print(nerfstudio.__version__)" 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✓ ($VERSION)${NC}"
    else
        echo -e "${RED}✗ NOT INSTALLED${NC}"
        echo "  Run: conda activate namma-space && pip install nerfstudio"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check COLMAP
echo -n "Checking COLMAP... "
if command -v colmap &> /dev/null; then
    VERSION=$(colmap -h 2>&1 | grep "COLMAP" | head -1 | awk '{print $2}')
    echo -e "${GREEN}✓ ($VERSION)${NC}"
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    echo "  Run: brew install colmap"
    ERRORS=$((ERRORS + 1))
fi

# Check ffmpeg
echo -n "Checking ffmpeg... "
if command -v ffmpeg &> /dev/null; then
    VERSION=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
    echo -e "${GREEN}✓ ($VERSION)${NC}"
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check Node.js
echo -n "Checking Node.js... "
if command -v node &> /dev/null; then
    VERSION=$(node -v 2>&1)
    echo -e "${GREEN}✓ ($VERSION)${NC}"
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    echo "  Run: brew install node"
    ERRORS=$((ERRORS + 1))
fi

# Check video file
echo -n "Checking video file... "
if [ -f "namma-space-project/input-videos/your-video.mov" ]; then
    SIZE=$(du -h "namma-space-project/input-videos/your-video.mov" | cut -f1)
    echo -e "${GREEN}✓ ($SIZE)${NC}"
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    echo "  Copy your iPhone video to: namma-space-project/input-videos/"
    ERRORS=$((ERRORS + 1))
fi

# Check disk space
echo -n "Checking disk space... "
FREE=$(df -h . | awk 'NR==2 {print $4}')
echo -e "${GREEN}$FREE available${NC}"

# Summary
echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              All Checks Passed! ✓                          ║${NC}"
    echo -e "${GREEN}║          Ready to run: ./run-simple.sh                     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║            $ERRORS Error(s) Found                               ║${NC}"
    echo -e "${RED}║          Fix issues above before running                   ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
