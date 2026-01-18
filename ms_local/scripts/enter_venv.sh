#!/usr/bin/env bash
# NOTE:
# - This script MUST be sourced:
#     source enter_venv.sh
# - It works even if you source it from any directory.

# do NOT set -e here (source 시 현재 쉘을 죽일 수 있음)
set -u

# Resolve this script directory safely (works with source)
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

# Load shared env
if [ ! -f "$SCRIPT_DIR/00_env.sh" ]; then
  echo "ERROR: cannot find 00_env.sh next to enter_venv.sh (expected: $SCRIPT_DIR/00_env.sh)" >&2
  return 1 2>/dev/null || exit 1
fi
source "$SCRIPT_DIR/00_env.sh"

# Activate venv
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "ERROR: venv not found at $VENV_DIR" >&2
  echo "Run: $SCRIPT_DIR/02_venv.sh" >&2
  return 1 2>/dev/null || exit 1
fi
source "$VENV_DIR/bin/activate"

echo "========================================"
echo "Entered vLLM dev environment"
echo "  VLLM_DEV_ROOT = $VLLM_DEV_ROOT"
echo "  VLLM_SRC_DIR  = $VLLM_SRC_DIR"
echo "  VENV_DIR      = $VENV_DIR"
echo "  Python        = $(which python)"
echo "========================================"

