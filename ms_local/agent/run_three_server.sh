#!/usr/bin/env bash

# 1. 기존 프로세스 종료
pkill -9 -f vllm

# 2. 확인
ps aux | grep vllm

# 3. 로그 정리
rm -f /workspace/logs/*.log

# 4. 다시 시작 (3개 동시)
python -m vllm.entrypoints.openai.api_server \
  --model /workspace/ms_docker/models/Llama-3.2-3B-Instruct \
  --host 0.0.0.0 \
  --port 8001 \
  --gpu-memory-utilization 0.25 \
  --max-model-len 4096 \
  > /workspace/logs/planner.log 2>&1 &

sleep 30

python -m vllm.entrypoints.openai.api_server \
  --model /workspace/ms_docker/models/Qwen2.5-Coder-3B-Instruct \
  --host 0.0.0.0 \
  --port 8002 \
  --gpu-memory-utilization 0.25 \
  --max-model-len 4096 \
  > /workspace/logs/coder.log 2>&1 &

sleep 30

python -m vllm.entrypoints.openai.api_server \
  --model /workspace/ms_docker/models/deepseek-coder-6.7b-instruct \
  --host 0.0.0.0 \
  --port 8003 \
  --gpu-memory-utilization 0.3 \
  --max-model-len 4096 \
  > /workspace/logs/debugger.log 2>&1 &


