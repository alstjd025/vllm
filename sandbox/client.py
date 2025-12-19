#!/usr/bin/env python3
import os
import time
import statistics
import requests
from typing import List, Dict, Tuple

from openai import OpenAI
from transformers import AutoTokenizer

# ===== Client defaults =====
DEFAULT_BASE_URL = "http://127.0.0.1:8000/v1"
DEFAULT_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
DEFAULT_SYSTEM = "당신은 유능한 비서입니다. 한국어로 자연스럽고 간결하게 답하세요."
DEFAULT_PROMPT = "vLLM 서버/클라이언트가 정상 동작하는지 한 문단으로 알려줘."
DEFAULT_TEMP = 0.2
DEFAULT_MAX_TOKENS = 200
DEFAULT_WARMUP = 1
DEFAULT_RUNS = 5
# ===========================


def wait_for_server(base_root: str, api_key: str, timeout_s: int = 300) -> None:
    """Wait until /health is OK and /v1/models is accessible (with auth if enabled)."""
    health_url = f"{base_root}/health"
    models_url = f"{base_root}/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    deadline = time.time() + timeout_s
    last_err = None

    while time.time() < deadline:
        try:
            if requests.get(health_url, timeout=2).status_code != 200:
                last_err = "health check failed"
                time.sleep(1)
                continue

            r = requests.get(models_url, headers=headers, timeout=5)
            if r.status_code == 200 and r.json().get("data"):
                print("[ready] vLLM server is ready")
                return
            last_err = f"/v1/models status={r.status_code}"

        except Exception as e:
            last_err = repr(e)

        time.sleep(1)

    raise RuntimeError(f"Server not ready after {timeout_s}s: {last_err}")


def count_tokens(tokenizer: AutoTokenizer, text: str) -> int:
    return len(tokenizer.encode(text))


def run_once_stream(
    client: OpenAI,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> Tuple[float, float, str]:
    """Run one streaming chat completion and return (TTFT, total_time, text)."""
    t0 = time.perf_counter()
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    ttft = None
    chunks = []

    for event in stream:
        delta = event.choices[0].delta
        if delta and getattr(delta, "content", None):
            if ttft is None:
                ttft = time.perf_counter() - t0
            chunks.append(delta.content)

    total = time.perf_counter() - t0
    return ttft or total, total, "".join(chunks)


def main():
    # ---- Config (override via env if needed) ----
    base_url = os.environ.get("VLLM_BASE_URL", DEFAULT_BASE_URL)
    base_root = base_url.rsplit("/v1", 1)[0]
    api_key = os.environ.get("VLLM_API_KEY", "")
    model = os.environ.get("VLLM_MODEL", DEFAULT_MODEL)

    system_msg = os.environ.get("SYSTEM", DEFAULT_SYSTEM)
    prompt = os.environ.get("PROMPT", DEFAULT_PROMPT)

    temperature = float(os.environ.get("TEMP", DEFAULT_TEMP))
    max_tokens = int(os.environ.get("MAX_TOKENS", DEFAULT_MAX_TOKENS))
    warmup = int(os.environ.get("WARMUP", DEFAULT_WARMUP))
    runs = int(os.environ.get("RUNS", DEFAULT_RUNS))

    # ---- Readiness ----
    print(f"[info] waiting for server at {base_root}")
    wait_for_server(base_root, api_key)

    # ---- Client & tokenizer ----
    client = OpenAI(base_url=base_url, api_key=api_key)
    tokenizer = AutoTokenizer.from_pretrained(model)

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt},
    ]

    approx_in_tok = count_tokens(tokenizer, system_msg + "\n" + prompt)
    print(f"[info] approx input tokens: {approx_in_tok}")

    # ---- Warmup ----
    for i in range(warmup):
        ttft, total, text = run_once_stream(
            client, model, messages, temperature, max_tokens
        )
        print(f"[warmup#{i+1}] ttft={ttft:.3f}s total={total:.3f}s")

    # ---- Benchmark ----
    ttfts, totals, tps = [], [], []
    last_text = ""

    for i in range(runs):
        ttft, total, text = run_once_stream(
            client, model, messages, temperature, max_tokens
        )
        out_tok = count_tokens(tokenizer, text)
        tok_per_s = out_tok / total if total > 0 else 0.0

        ttfts.append(ttft)
        totals.append(total)
        tps.append(tok_per_s)
        last_text = text

        print(
            f"[run#{i+1}] ttft={ttft:.3f}s total={total:.3f}s "
            f"out_tok={out_tok} tok/s={tok_per_s:.2f}"
        )

    # ---- Summary ----
    print("\n=== Summary ===")
    print(f"TTFT  : mean={statistics.mean(ttfts):.3f}s p50={statistics.median(ttfts):.3f}s")
    print(f"Total : mean={statistics.mean(totals):.3f}s p50={statistics.median(totals):.3f}s")
    print(f"Tok/s : mean={statistics.mean(tps):.2f}")

    print("\n=== Last output ===")
    print(last_text.strip())


if __name__ == "__main__":
    main()
