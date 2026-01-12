#!/bin/bash
set -e

WORKSPACE_DIR="/workspace"
VENV_DIR="${WORKSPACE_DIR}/.venv"

cd "$WORKSPACE_DIR"
source "${VENV_DIR}/bin/activate"

echo "Cleaning previous build artifacts..."
rm -rf .deps/ vllm/_version.py build/ *.egg-info

echo "Building vLLM (this may take 10-30 minutes)..."
export MAX_JOBS=16  # Limit parallel jobs

pip install -e . --no-build-isolation -v

# Verify installation
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')" || exit 1

echo "✓ vLLM built successfully"
