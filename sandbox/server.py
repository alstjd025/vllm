#!/usr/bin/env python3
import os
import sys
import subprocess

# ===== Server defaults (override via env if needed) =====
DEFAULT_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = "8000"
DEFAULT_TP = "2"            # 당신 환경: 2×3090
DEFAULT_DTYPE = "float16"
DEFAULT_GPU_MEM_UTIL = "0.90"
DEFAULT_MAX_MODEL_LEN = "4096"
# =======================================================

def main():
    model = os.environ.get("VLLM_MODEL", DEFAULT_MODEL)
    host = os.environ.get("VLLM_HOST", DEFAULT_HOST)
    port = os.environ.get("VLLM_PORT", DEFAULT_PORT)

    tp = os.environ.get("TENSOR_PARALLEL_SIZE", DEFAULT_TP)
    dtype = os.environ.get("DTYPE", DEFAULT_DTYPE)
    gpu_mem_util = os.environ.get("GPU_MEMORY_UTILIZATION", DEFAULT_GPU_MEM_UTIL)
    max_model_len = os.environ.get("MAX_MODEL_LEN", DEFAULT_MAX_MODEL_LEN)

    # Optional API key (enable auth only if set)
    api_key = os.environ.get("VLLM_API_KEY", "")

    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", model,
        "--host", host,
        "--port", port,
        "--dtype", dtype,
        "--tensor-parallel-size", tp,
        "--gpu-memory-utilization", gpu_mem_util,
        "--max-model-len", max_model_len,
    ]

    if api_key:
        cmd += ["--api-key", api_key]

    print("\n=== Launching vLLM OpenAI-compatible server ===")
    print(" ".join(cmd))
    print("\nNotes:")
    print(" - CUDA_VISIBLE_DEVICES controls which GPUs are used")
    print(" - Override defaults via env vars if needed\n")

    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
