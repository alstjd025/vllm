#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_env.sh"
source "$VENV_DIR/bin/activate"

MODEL="${1:-meta-llama/Meta-Llama-3-8B-Instruct}"

python - <<PY
from huggingface_hub import snapshot_download
model_id = "${MODEL}"
path = snapshot_download(repo_id=model_id)
print("Downloaded to:", path)
PY

