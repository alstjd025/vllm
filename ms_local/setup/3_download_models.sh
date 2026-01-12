#!/bin/bash
set -e

WORKSPACE_DIR="/workspace"
VENV_DIR="${WORKSPACE_DIR}/.venv"
MODELS_DIR="${WORKSPACE_DIR}/ms_docker/models"

source "${VENV_DIR}/bin/activate"

mkdir -p "$MODELS_DIR"

# Check for HF token
if [ -z "$HF_TOKEN" ]; then
    echo "WARNING: HF_TOKEN not set. Llama model download may fail."
    echo "Set it with: export HF_TOKEN='your_token_here'"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Model list
MODELS=(
    "meta-llama/Llama-3.2-3B-Instruct"
    "Qwen/Qwen2.5-Coder-3B-Instruct"
    "deepseek-ai/deepseek-coder-6.7b-instruct"
)

# Download models
for MODEL in "${MODELS[@]}"; do
    MODEL_NAME=$(basename "$MODEL")
    MODEL_PATH="${MODELS_DIR}/${MODEL_NAME}"
    
    if [ -d "$MODEL_PATH" ]; then
        echo "✓ $MODEL_NAME already exists, skipping..."
        continue
    fi
    
    echo "Downloading $MODEL..."
    python3 << PYTHON_EOF
from huggingface_hub import snapshot_download
import os

snapshot_download(
    repo_id="${MODEL}",
    token=os.getenv("HF_TOKEN"),
    local_dir="${MODEL_PATH}",
    local_dir_use_symlinks=False
)
print("✓ Downloaded ${MODEL_NAME}")
PYTHON_EOF
done

echo "✓ All models downloaded"
