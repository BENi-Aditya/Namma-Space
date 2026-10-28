#!/usr/bin/env python3
"""Reproducible Vercel/static production build, from committed exports only."""
from pathlib import Path
import subprocess
import sys
from release_assets import restore
from package_viewer import package
ROOT=Path(__file__).resolve().parents[1]
restore()
subprocess.run([sys.executable,str(ROOT/'scripts/check_project.py')],cwd=ROOT,check=True)
subprocess.run(['node',str(ROOT/'test/test_view_state.cjs')],cwd=ROOT,check=True)
package(ROOT/'output/public')
