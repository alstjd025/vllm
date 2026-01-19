# test_langchain_seed.py
from langchain_openai import ChatOpenAI
import logging

# HTTP 요청 로깅 활성화
logging.basicConfig(level=logging.DEBUG)

llm = ChatOpenAI(
    base_url="http://localhost:8001/v1",
    api_key="dummy",
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    temperature=0.7,
    seed=42,  # ← 명시적 seed
    verbose=True
)

# 3번 호출
responses = []
for i in range(3):
    response = llm.invoke([{"role": "user", "content": "Write a short sentence about AI."}])
    responses.append(response.content)
    print(f"Response {i+1}: {response.content[:80]}")

# 비교
if responses[0] == responses[1] == responses[2]:
    print("\n✅ SAME - Seed working in LangChain")
else:
    print("\n❌ DIFFERENT - Seed NOT working in LangChain")
