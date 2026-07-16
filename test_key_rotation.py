import sys
import os
from pathlib import Path

# Add src folder to path (needed if not installed in editable mode)
sys.path.insert(0, str(Path(__file__).parent / "src"))

from applypilot.config import load_env
from applypilot.llm import LLMClient

load_env()
valid_key = os.environ.get("GEMINI_API_KEY", "")
if not valid_key:
    print("Error: GEMINI_API_KEY not found in environment.")
    sys.exit(1)

# Construct a comma-separated key string: two bad keys, then the good key
comma_separated_keys = f"badkey1, badkey2, {valid_key}"

print(f"Initializing LLMClient with keys: {comma_separated_keys[:40]}...")

# We will use the Gemini endpoint & model override or default gemini-2.0-flash/gemini-3.5-flash
base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
model = "gemini-2.0-flash"

client = LLMClient(base_url=base_url, model=model, api_key=comma_separated_keys)

print(f"Total keys loaded: {len(client.api_keys)}")
print(f"Keys: {client.api_keys}")

print("\n--- Sending request... ---")
try:
    response = client.ask("Say 'Hello, the key rotation is working!' in one sentence.")
    print(f"Success! Response: {response}")
except Exception as e:
    print(f"Failed with error: {e}")
