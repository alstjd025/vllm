import time
import psutil
import GPUtil
from typing import TypedDict, Annotated
import operator
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

class PerformanceTracker:
    def __init__(self):
        self.metrics = {
            'planning': [],
            'coding': [],
            'debugging': []
        }
    
    def track(self, node_name, start_time, end_time):
        latency = end_time - start_time
        
        # GPU 메모리
        gpus = GPUtil.getGPUs()
        gpu_memory = gpus[0].memoryUsed if gpus else 0
        
        # CPU 메모리
        cpu_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        self.metrics[node_name].append({
            'latency': latency,
            'gpu_memory_mb': gpu_memory,
            'cpu_memory_mb': cpu_memory,
            'timestamp': time.time()
        })
    
    def summary(self):
        import numpy as np
        result = {}
        for node, data in self.metrics.items():
            if data:
                latencies = [d['latency'] for d in data]
                result[node] = {
                    'count': len(data),
                    'avg_latency': np.mean(latencies),
                    'p50_latency': np.percentile(latencies, 50),
                    'p95_latency': np.percentile(latencies, 95),
                    'p99_latency': np.percentile(latencies, 99),
                    'total_time': sum(latencies)
                }
        return result

# 글로벌 tracker
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

# LLM 초기화
planner_llm = ChatOpenAI(
    base_url="http://localhost:8001/v1",
    api_key="dummy",
    model="/workspace/ms_docker/models/Llama-3.2-3B-Instruct",
    temperature=0.7,
    timeout=120
)

coder_llm = ChatOpenAI(
    base_url="http://localhost:8002/v1",
    api_key="dummy",
    model="/workspace/ms_docker/models/Qwen2.5-Coder-3B-Instruct",
    temperature=0.2,
    timeout=120
)

debugger_llm = ChatOpenAI(
    base_url="http://localhost:8003/v1",
    api_key="dummy",
    model="/workspace/ms_docker/models/deepseek-coder-6.7b-instruct",
    temperature=0.1,
    timeout=120
)

def planning_node(state: AgentState):
    start_time = time.time()
    print(f"\n[ITERATION {state['iteration']}] Planning...")
    
    feedback = ""
    if state.get("debug_result") and "FAIL" in state["debug_result"]:
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
    
    response = planner_llm.invoke([{"role": "user", "content": prompt}])
    
    end_time = time.time()
    tracker.track('planning', start_time, end_time)
    print(f"Planning took {end_time - start_time:.2f}s")
    
    return {
        "plan": response.content,
        "history": [{"role": "planner", "iteration": state['iteration'], "content": response.content}]
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
    
    response = coder_llm.invoke([{"role": "user", "content": prompt}])
    
    end_time = time.time()
    tracker.track('coding', start_time, end_time)
    print(f"Coding took {end_time - start_time:.2f}s")
    
    return {
        "code": response.content,
        "history": [{"role": "coder", "iteration": state['iteration'], "content": response.content}]
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

Carefully check for:
1. Does it address the root cause?
2. Are there any logic errors?
3. Edge cases handled?
4. Code quality

Respond with ONLY:
- "PASS" if the fix is correct
- "FAIL: [detailed reason]" if there are issues

Verdict:"""
    
    response = debugger_llm.invoke([{"role": "user", "content": prompt}])
    
    end_time = time.time()
    tracker.track('debugging', start_time, end_time)
    print(f"Debugging took {end_time - start_time:.2f}s")
    
    return {
        "debug_result": response.content,
        "iteration": state["iteration"] + 1,
        "history": [{"role": "debugger", "iteration": state['iteration'], "content": response.content}]
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

# 그래프 구성
workflow = StateGraph(AgentState)

workflow.add_node("planning", planning_node)
workflow.add_node("coding", coding_node)
workflow.add_node("debugging", debugging_node)

workflow.set_entry_point("planning")
workflow.add_edge("planning", "coding")
workflow.add_edge("coding", "debugging")
workflow.add_conditional_edges(
    "debugging",
    should_continue,
    {
        "planning": "planning",
        END: END
    }
)

agent = workflow.compile()

if __name__ == "__main__":
    print("Agent initialized successfully!")
