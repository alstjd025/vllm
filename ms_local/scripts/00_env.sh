#!/usr/bin/env bash
set -euo pipefail

# === Project root (고정) ===
export VLLM_DEV_ROOT="/workspace/vllm/ms_local"

# === vLLM source repo root (이미 존재) ===
export VLLM_SRC_DIR="/workspace/vllm"

# Persistent caches (ms_local 아래에 고정)
export CACHE_ROOT="$VLLM_DEV_ROOT/.cache"
export HF_HOME="$CACHE_ROOT/hf"
export TORCH_EXTENSIONS_DIR="$CACHE_ROOT/torch_extensions"
export CCACHE_DIR="$CACHE_ROOT/ccache"
export PIP_CACHE_DIR="$CACHE_ROOT/pip"

# Python venv (ms_local 아래에 고정)
export VENV_DIR="$VLLM_DEV_ROOT/venvs/vllm-cu128"

# Build parallelism
NPROC="$(nproc 2>/dev/null || echo 16)"
export MAX_JOBS="${MAX_JOBS:-$(( (NPROC + 1) / 2 ))}"
export NVCC_THREADS="${NVCC_THREADS:-2}"

# ccache config
export CCACHE_MAXSIZE="${CCACHE_MAXSIZE:-20G}"
export CCACHE_COMPRESS="${CCACHE_COMPRESS:-1}"
export CCACHE_COMPRESSLEVEL="${CCACHE_COMPRESSLEVEL:-6}"
export CMAKE_CUDA_COMPILER_LAUNCHER="${CMAKE_CUDA_COMPILER_LAUNCHER:-ccache}"
export CMAKE_CXX_COMPILER_LAUNCHER="${CMAKE_CXX_COMPILER_LAUNCHER:-ccache}"

# Create dirs
mkdir -p \
  "$VLLM_DEV_ROOT" \
  "$CACHE_ROOT" \
  "$HF_HOME" \
  "$TORCH_EXTENSIONS_DIR" \
  "$CCACHE_DIR" \
  "$PIP_CACHE_DIR" \
  "$(dirname "$VENV_DIR")"

