# test_seed_direct.py
import requests
import json

def test_seed_reproducibility():
    """vLLM API에 직접 seed를 전달하여 테스트"""
    
    url = "http://localhost:8001/v1/chat/completions"
    
    prompt = "Write a short sentence about AI."
    
    # 같은 seed로 3번 호출
    responses = []
    
    for i in range(3):
        payload = {
            "model": "meta-llama/Meta-Llama-3-8B-Instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "seed": 42,  # ← 명시적 seed
            "max_tokens": 100
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        text = result['choices'][0]['message']['content']
        responses.append(text)
        
        print(f"Response {i+1}:")
        print(text)
        print("-" * 80)
    
    # 비교
    print("\n=== Comparison ===")
    if responses[0] == responses[1] == responses[2]:
        print("✅ ALL SAME - Seed is working!")
        return True
    else:
        print("❌ DIFFERENT - Seed is NOT working!")
        print(f"\nResponse 1: {responses[0][:100]}")
        print(f"Response 2: {responses[1][:100]}")
        print(f"Response 3: {responses[2][:100]}")
        return False

if __name__ == "__main__":
    test_seed_reproducibility()
