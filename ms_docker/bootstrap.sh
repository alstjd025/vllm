#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# 자동 생성되는 버전 파일(권한 꼬임 방지)
rm -f vllm/_version.py || true

# venv 생성/활성화
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

python --version

# 기본 툴링
pip install -U pip setuptools wheel setuptools_scm

# ---- Torch 버전/인덱스(필요 시 외부에서 override 가능) ----
: "${TORCH_VERSION:=2.9.0}"
: "${TORCHVISION_VERSION:=0.24.0}"
: "${TORCHAUDIO_VERSION:=2.9.0}"
: "${TORCH_INDEX_URL:=https://download.pytorch.org/whl/cu128}"

# venv 안의 torch 계열을 확실히 최신으로 맞추기
pip uninstall -y torch torchvision torchaudio || true

pip install --index-url "${TORCH_INDEX_URL}" \
  "torch==${TORCH_VERSION}" \
  "torchvision==${TORCHVISION_VERSION}" \
  "torchaudio==${TORCHAUDIO_VERSION}"

python -c "import torch; print('torch:', torch.__version__, 'cuda:', torch.version.cuda, 'gpu:', torch.cuda.is_available())"

# vLLM editable build (현재 venv의 torch/툴체인 그대로 사용)
pip install -e . --no-build-isolation -v

