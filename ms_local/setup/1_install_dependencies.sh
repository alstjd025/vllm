#!/bin/bash
set -e

WORKSPACE_DIR="/workspace"
VENV_DIR="${WORKSPACE_DIR}/.venv"

echo "Installing system dependencies..."

# Check if running in conda base
if [[ -n "$CONDA_DEFAULT_ENV" ]]; then
    echo "Detected conda environment: $CONDA_DEFAULT_ENV"
fi

# Create venv if not exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "${VENV_DIR}/bin/activate"

# Upgrade pip
pip install -U pip setuptools wheel setuptools_scm

# Install Torch
echo "Installing PyTorch..."
pip install --index-url https://download.pytorch.org/whl/cu128 \
    torch==2.9.0 \
    torchvision==0.24.0 \
    torchaudio==2.9.0

# Verify Torch
python -c "import torch; print(f'Torch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')" || exit 1

# Install Agent dependencies
echo "Installing Agent dependencies..."
pip install langchain==0.3.14
pip install langchain-openai==0.2.14
pip install langgraph==0.2.60
pip install langfuse==2.63.3
pip install datasets==3.2.0
pip install huggingface_hub==0.26.5
pip install numpy==2.2.1
pip install pandas==2.2.3

# Performance monitoring
pip install psutil gputil

echo "✓ All dependencies installed"
