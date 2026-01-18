#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_env.sh"

echo "This will remove caches under $CACHE_ROOT and venv at $VENV_DIR"
echo "If you really want it, run:"
echo "  rm -rf $CACHE_ROOT $VENV_DIR"

