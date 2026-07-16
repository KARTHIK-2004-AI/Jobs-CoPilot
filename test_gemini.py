import httpx
import os
from applypilot.config import load_env

load_env()
key = os.environ.get("GEMINI_API_KEY", "")
model = "gemini-3.5-flash"

print(f"Testing API key starting with: {key[:10]}...")

# 1. Test OpenAI-compat
print(f"\n--- Testing OpenAI-compatible endpoint for {model} ---")
try:
    url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say hello"}],
        "temperature": 0.2
    }
    resp = httpx.post(url, json=payload, headers=headers)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

# 2. Test Native
print(f"\n--- Testing Native Gemini endpoint for {model} ---")
try:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": "Say hello"}]}]
    }
    resp = httpx.post(url, json=payload, params={"key": key})
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text[:300]}")
except Exception as e:
    print(f"Error: {e}")
