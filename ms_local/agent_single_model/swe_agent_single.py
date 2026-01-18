import time
import psutil
import GPUtil
from typing import TypedDict, Annotated
import operator

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

class PerformanceTracker:
    def __init__(self):
        self.metrics = {"planning": [], "coding": [], "debugging": []}

    def track(self, node_name, start_time, end_time):
        latency = end_time - start_time

        gpus = GPUtil.getGPUs()
        gpu_memory = gpus[0].memoryUsed if gpus else 0  # MB

        cpu_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        self.metrics[node_name].append({
            "latency": latency,
            "gpu_memory_mb": gpu_memory,
            "cpu_memory_mb": cpu_memory,
            "timestamp": time.time()
        })

    def summary(self):
        import numpy as np
        out = {}
        for node, data in self.metrics.items():
            if not data:
                continue
            latencies = [d["latency"] for d in data]
            out[node] = {
                "count": len(data),
                "avg_latency": float(np.mean(latencies)),
                "p50_latency": float(np.percentile(latencies, 50)),
                "p95_latency": float(np.percentile(latencies, 95)),
                "p99_latency": float(np.percentile(latencies, 99)),
                "total_time": float(sum(latencies)),
            }
        return out

tracker = PerformanceTracker()

class AgentState(TypedDict):
    task_id: str
    problem_statement: str
    repo: str
    plan: str
    code: str
    debug_result: str
    iteration: int
    max_iterations: int
    history: Annotated[list, operator.add]

# === 단일 vLLM 서버/단일 모델 ===
BASE_URL = "http://localhost:8001/v1"
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

shared_llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key="dummy",
    model=MODEL_ID,
    temperature=0.3,
    timeout=120,
)

def planning_node(state: AgentState):
    start_time = time.time()
    print(f"\n[ITERATION {state['iteration']}] Planning...")

    feedback = ""
    if state.get("debug_result") and "FAIL" in state["debug_result"].upper():
        feedback = f"\n\nPrevious attempt failed:\n{state['debug_result']}\n\nPlease revise your plan."

    prompt = f"""You are a senior software engineer analyzing a bug report.

Bug Report:
{state['problem_statement']}

Repository: {state['repo']}
{feedback}

Create a detailed plan to fix this bug:
1. Which files need to be modified?
2. What functions/classes are involved?
3. What is the root cause?
4. How should we fix it?

Plan:"""

    response = shared_llm.invoke([{"role": "user", "content": prompt}])

    end_time = time.time()
    tracker.track("planning", start_time, end_time)
    print(f"Planning took {end_time - start_time:.2f}s")

    return {
        "plan": response.content,
        "history": [{"role": "planner", "iteration": state["iteration"], "content": response.content}],
    }

def coding_node(state: AgentState):
    start_time = time.time()
    print(f"[ITERATION {state['iteration']}] Coding...")

    prompt = f"""You are an expert programmer. Implement the following fix.

Plan:
{state['plan']}

Bug Report:
{state['problem_statement']}

Generate the complete fixed code or a patch in unified diff format.

Code:"""

    response = shared_llm.invoke([{"role": "user", "content": prompt}])

    end_time = time.time()
    tracker.track("coding", start_time, end_time)
    print(f"Coding took {end_time - start_time:.2f}s")

    return {
        "code": response.content,
        "history": [{"role": "coder", "iteration": state["iteration"], "content": response.content}],
    }

def debugging_node(state: AgentState):
    start_time = time.time()
    print(f"[ITERATION {state['iteration']}] Debugging...")

    prompt = f"""You are a senior code reviewer. Verify if this code correctly fixes the bug.

Original Bug:
{state['problem_statement']}

Plan:
{state['plan']}

Generated Code:
{state['code']}

Respond with ONLY:
- "PASS" if the fix is correct
- "FAIL: [detailed reason]" if there are issues

Verdict:"""

    response = shared_llm.invoke([{"role": "user", "content": prompt}])

    end_time = time.time()
    tracker.track("debugging", start_time, end_time)
    print(f"Debugging took {end_time - start_time:.2f}s")

    return {
        "debug_result": response.content,
        "iteration": state["iteration"] + 1,
        "history": [{"role": "debugger", "iteration": state["iteration"], "content": response.content}],
    }

def should_continue(state: AgentState):
    if "PASS" in state["debug_result"].upper():
        print("✓ PASSED!")
        return END
    if state["iteration"] >= state["max_iterations"]:
        print("✗ Max iterations reached")
        return END
    print("→ Retrying with feedback...")
    return "planning"

workflow = StateGraph(AgentState)
workflow.add_node("planning", planning_node)
workflow.add_node("coding", coding_node)
workflow.add_node("debugging", debugging_node)

workflow.set_entry_point("planning")
workflow.add_edge("planning", "coding")
workflow.add_edge("coding", "debugging")
workflow.add_conditional_edges("debugging", should_continue, {"planning": "planning", END: END})

agent = workflow.compile()

if __name__ == "__main__":
    print("Agent (single model) initialized successfully!")

    # 예시 실행(원하면 run_swebench.py에서 이 agent를 import 해서 써도 됨)
    init_state: AgentState = {
        "task_id": "demo",
        "problem_statement": "There is a bug in function foo() that crashes on empty input.",
        "repo": "demo-repo",
        "plan": "",
        "code": "",
        "debug_result": "",
        "iteration": 0,
        "max_iterations": 3,
        "history": [],
    }

    final = agent.invoke(init_state)
    print("\nFinal verdict:", final.get("debug_result"))
    print("Metrics:", tracker.summary())

