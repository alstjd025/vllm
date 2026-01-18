#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_env.sh"

# venv 활성화
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "Venv not found at $VENV_DIR"
  echo "Run 02_venv.sh first."
  exit 1
fi
source "$VENV_DIR/bin/activate"

echo "[1/3] Installing agent Python deps into venv: $VENV_DIR"

python -m pip install -U pip wheel setuptools

# ✅ IMPORTANT: quote version constraints (<=) so bash doesn't treat it as redirection
# ✅ IMPORTANT: gputil (pip) provides GPUtil (import)
pip install \
  langchain-openai \
  langgraph \
  psutil \
  gputil \
  "numpy<=2.2.0" \
  requests \
  python-dotenv \
  tqdm

echo "[2/3] Quick import sanity check..."
python - <<'PY'
import psutil
import GPUtil
import numpy as np
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
print("OK: imports succeeded")
print("psutil:", psutil.__version__)
print("numpy:", np.__version__)
print("GPUtil:", GPUtil.__version__ if hasattr(GPUtil, "__version__") else "unknown")
print("GPUs visible:", len(GPUtil.getGPUs()))
PY

echo "[3/3] Optional: check server health endpoints (if running)..."
if command -v curl >/dev/null 2>&1; then
  for p in 8001 8002 8003; do
    echo "- http://127.0.0.1:${p}/v1/models"
    curl -s "http://127.0.0.1:${p}/v1/models" | head -c 200 || true
    echo
  done
else
  echo "curl not found; skipping server health checks."
fi

echo "OK: agent deps installed."

