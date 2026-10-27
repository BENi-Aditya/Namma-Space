#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
CURRENT="$(git config --get core.hooksPath || true)"
if [[ -n "$CURRENT" && "$CURRENT" != '.githooks' ]]; then
  echo "Existing hooks at $CURRENT; integrate .githooks/pre-commit manually to preserve them."
  exit 1
fi
if [[ -z "$CURRENT" && -f .git/hooks/pre-commit ]]; then
  echo 'Existing pre-commit hook found; integrate .githooks/pre-commit manually.'
  exit 1
fi
git config core.hooksPath .githooks
echo 'Publishing sync enabled: commits snapshot model exports and saved scene settings.'
