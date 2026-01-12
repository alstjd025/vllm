#!/bin/bash
set -e

WORKSPACE_DIR="/workspace"
VENV_DIR="${WORKSPACE_DIR}/.venv"
MODELS_DIR="${WORKSPACE_DIR}/ms_docker/models"
LOGS_DIR="${WORKSPACE_DIR}/logs"

source "${VENV_DIR}/bin/activate"

mkdir -p "$LOGS_DIR"

# Kill existing servers
echo "Stopping existing vLLM servers..."
pkill -9 -f "vllm.entrypoints.openai.api_server" 2>/dev/null || true
sleep 2

# Start Planner
echo "Starting Planner server (port 8001)..."
python -m vllm.entrypoints.openai.api_server \
  --model "${MODELS_DIR}/Llama-3.2-3B-Instruct" \
  --host 0.0.0.0 \
  --port 8001 \
  --gpu-memory-utilization 0.25 \
  --max-model-len 4096 \
  > "${LOGS_DIR}/planner.log" 2>&1 &
PLANNER_PID=$!
echo "Planner PID: $PLANNER_PID"

sleep 30

# Start Coder
echo "Starting Coder server (port 8002)..."
python -m vllm.entrypoints.openai.api_server \
  --model "${MODELS_DIR}/Qwen2.5-Coder-3B-Instruct" \
  --host 0.0.0.0 \
  --port 8002 \
  --gpu-memory-utilization 0.25 \
  --max-model-len 4096 \
  > "${LOGS_DIR}/coder.log" 2>&1 &
CODER_PID=$!
echo "Coder PID: $CODER_PID"

sleep 30

# Start Debugger
echo "Starting Debugger server (port 8003)..."
python -m vllm.entrypoints.openai.api_server \
  --model "${MODELS_DIR}/deepseek-coder-6.7b-instruct" \
  --host 0.0.0.0 \
  --port 8003 \
  --gpu-memory-utilization 0.3 \
  --max-model-len 4096 \
  > "${LOGS_DIR}/debugger.log" 2>&1 &
DEBUGGER_PID=$!
echo "Debugger PID: $DEBUGGER_PID"

echo ""
echo "Waiting for servers to start (60s)..."
sleep 60

# Health checks
echo ""
echo "Checking server health..."
for PORT in 8001 8002 8003; do
    if curl -s http://localhost:${PORT}/health > /dev/null 2>&1; then
        echo "✓ Port ${PORT}: OK"
    else
        echo "✗ Port ${PORT}: FAILED"
        echo "Check logs: ${LOGS_DIR}/"
    fi
done

echo ""
echo "Server PIDs:"
echo "  Planner:  $PLANNER_PID"
echo "  Coder:    $CODER_PID"
echo "  Debugger: $DEBUGGER_PID"
echo ""
echo "Stop servers with: pkill -9 -f vllm.entrypoints.openai.api_server"
