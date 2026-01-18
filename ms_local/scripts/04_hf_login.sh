#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_env.sh"
source "$VENV_DIR/bin/activate"

if [ -z "${HF_TOKEN:-}" ]; then
  echo "Set HF_TOKEN env var first."
  echo "Example: export HF_TOKEN=hf_xxx"
  exit 1
fi

# HF_HOME이 /workspace/.cache/hf로 고정됨
huggingface-cli login --token "HF_TOKEN"

echo "OK: huggingface login done."

