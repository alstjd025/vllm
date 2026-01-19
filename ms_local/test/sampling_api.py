# test_seed_via_api.py
from langchain_openai import ChatOpenAI

# vLLM 서버가 실행 중이어야 함
llm = ChatOpenAI(
    base_url="http://localhost:8001/v1",
    api_key="dummy",
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    temperature=0.7,
    model_kwargs={"seed": 42}
)

prompt = [{"role": "user", "content": "Write a short sentence about AI."}]

# 3번 실행
print("=== Testing seed via LangChain → vLLM API ===")
responses = []
for i in range(3):
    response = llm.invoke(prompt)
    responses.append(response.content)
    print(f"Run {i+1}: {response.content[:80]}...")

# 결과 비교
print("\n=== Result ===")
if responses[0] == responses[1] == responses[2]:
    print("✅ SAME - Seed is working!")
else:
    print("❌ DIFFERENT - Seed is NOT working via API")
    print(f"Response 1: {responses[0][:100]}")
    print(f"Response 2: {responses[1][:100]}")
    print(f"Response 3: {responses[2][:100]}")
