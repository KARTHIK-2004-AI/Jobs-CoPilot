import sys
from pathlib import Path

# Add src folder to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from applypilot.config import load_env
from applypilot.llm import get_client

load_env()

print("Initializing LLM client using configured settings from env...")
try:
    client = get_client()
    print(f"Provider URL: {client.base_url}")
    print(f"Model: {client.model}")
    print(f"Is Gemini: {client._is_gemini}")
    print(f"Number of API keys loaded: {len(client.api_keys)}")
    
    print("\n--- Sending request... ---")
    response = client.ask("Say 'The configured LLM is working properly!' in one sentence.")
    print(f"Success! Response: {response}")
except Exception as e:
    print(f"\nFailed with error: {e}")
