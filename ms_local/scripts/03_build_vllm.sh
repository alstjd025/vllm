#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_env.sh"
source "$VENV_DIR/bin/activate"

cd "$VLLM_SRC_DIR"

# vLLM 빌드 의존성 (repo에 존재하면 설치)
if [ -f "requirements/build.txt" ]; then
  pip install -r requirements/build.txt
fi

# editable install (C++/CUDA 변경 시 재실행하면 재빌드 유도)
MAX_JOBS="$MAX_JOBS" \
NVCC_THREADS="$NVCC_THREADS" \
TORCH_EXTENSIONS_DIR="$TORCH_EXTENSIONS_DIR" \
PIP_CACHE_DIR="$PIP_CACHE_DIR" \
pip install -e . -v

# ccache 상태 출력(선택)
ccache -s || true

echo "OK: vLLM built (editable) from $VLLM_SRC_DIR"

