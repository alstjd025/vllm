#!/usr/bin/env bash
set -euo pipefail

# ✅ vLLM 설치된 venv를 강제로 사용
source /workspace/vllm/ms_local/scripts/00_env.sh
source "$VENV_DIR/bin/activate"

LOG_DIR="/workspace/vllm/ms_local/agent_single_model/logs"
mkdir -p "$LOG_DIR"
PORT="${PORT:-8001}"
MODEL="${MODEL:-meta-llama/Meta-Llama-3-8B-Instruct}"

# 기존 서버 정리
pkill -9 -f "vllm.entrypoints.openai.api_server" || true

echo "[*] Starting vLLM server on :$PORT"
echo "[*] Logs will be saved to $LOG_DIR/server.log"

python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.85 \
  2>&1 | tee "$LOG_DIR/server.log"

