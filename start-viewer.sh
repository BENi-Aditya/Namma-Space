#!/usr/bin/env bash
# Serve only the viewer, never private reconstruction files.
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python3}" "$PROJECT_DIR/scripts/serve_viewer.py" "$@"
