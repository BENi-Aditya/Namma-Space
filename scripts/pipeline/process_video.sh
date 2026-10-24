#!/usr/bin/env bash
# Supported pipeline wrapper; dry run unless --execute is supplied.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python3}" "$SCRIPT_DIR/reconstruct.py" "$@"
