#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_env.sh"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

python -m pip install -U pip wheel setuptools

# 빌드/테스트 도구
pip install -U ninja cmake pytest requests huggingface_hub

echo "OK: venv ready at $VENV_DIR"

