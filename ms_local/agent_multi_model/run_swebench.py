from datasets import load_dataset
from swe_agent import agent, tracker
import time
import json

print("Loading SWE-bench Lite...")
dataset = load_dataset("princeton-nlp/SWE-bench_Lite")

# 첫 번째 태스크
task = dataset['test'][0]

print(f"\n{'='*60}")
print(f"Task ID: {task['instance_id']}")
print(f"Repository: {task['repo']}")
print(f"{'='*60}\n")
print("Problem Statement:")
print(task['problem_statement'][:500])
print("...\n")

# Agent 실행
initial_state = {
    "task_id": task["instance_id"],
    "problem_statement": task["problem_statement"],
    "repo": task["repo"],
    "plan": "",
    "code": "",
    "debug_result": "",
    "iteration": 0,
    "max_iterations": 3,
    "history": []
}

print("Starting agent...")

overall_start = time.time()
result = agent.invoke(initial_state)
overall_end = time.time()
perf_summary = tracker.summary()

print(f"\n{'='*60}")
print("PERFORMANCE METRICS")
print(f"{'='*60}")
print(f"Total Task Time: {overall_end - overall_start:.2f}s")
print(f"\nPer-Agent Breakdown:")
for agent_name, metrics in perf_summary.items():
    print(f"\n{agent_name.upper()}:")
    print(f"  Calls: {metrics['count']}")
    print(f"  Avg Latency: {metrics['avg_latency']:.2f}s")
    print(f"  P50: {metrics['p50_latency']:.2f}s")
    print(f"  P95: {metrics['p95_latency']:.2f}s")
    print(f"  P99: {metrics['p99_latency']:.2f}s")
    print(f"  Total: {metrics['total_time']:.2f}s")

# 결과 저장
output = {
    "task_id": result['task_id'],
    "total_time": overall_end - overall_start,
    "iterations": result['iteration'],
    "verdict": result['debug_result'],
    "performance": perf_summary,
    "code": result['code'],
    "history": result['history']
}

with open('/workspace/ms_docker/results/first_run.json', 'w') as f:
    json.dump(output, f, indent=2)
