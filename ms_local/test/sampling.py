from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct")
prompt = "Write a function to calculate fibonacci:"

# 실험 1: Temperature=0, seed 없음
print("=== Temperature=0, No Seed ===")
for i in range(3):
    params = SamplingParams(temperature=0)
    output = llm.generate([prompt], params)[0].outputs[0].text
    print(f"Run {i+1}: {output[:50]}...")

# 결과: 대부분 같지만 가끔 다를 수 있음

# 실험 2: Temperature=0.7, seed 없음
print("\n=== Temperature=0.7, No Seed ===")
for i in range(3):
    params = SamplingParams(temperature=0.7, seed=None)
    output = llm.generate([prompt], params)[0].outputs[0].text
    print(f"Run {i+1}: {output[:50]}...")

# 결과: 매번 다름! ⚠️

# 실험 3: Temperature=0.7, seed=42 (고정)
print("\n=== Temperature=0.7, Seed=42 ===")
for i in range(3):
    params = SamplingParams(temperature=0.7, seed=42)
    output = llm.generate([prompt], params)[0].outputs[0].text
    print(f"Run {i+1}: {output[:50]}...")

# 결과: 완전히 같음! ✅
