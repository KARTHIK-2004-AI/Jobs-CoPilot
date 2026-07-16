import os
import unittest
from unittest.mock import patch
from applypilot.llm import LLMClient, _detect_provider

def test_llm_client_key_parsing():
    # Test single key
    client = LLMClient(base_url="http://test", model="test-model", api_key="key1")
    assert client.api_keys == ["key1"]
    assert client.api_key == "key1"
    
    # Test multiple keys
    client2 = LLMClient(base_url="http://test", model="test-model", api_key="key1, key2 ,key3")
    assert client2.api_keys == ["key1", "key2", "key3"]
    assert client2.api_key == "key1"
    
    # Test empty key
    client3 = LLMClient(base_url="http://test", model="test-model", api_key="")
    assert client3.api_keys == [""]
    assert client3.api_key == ""

def test_llm_client_rotation():
    client = LLMClient(base_url="http://test", model="test-model", api_key="key1,key2,key3")
    assert client.api_key == "key1"
    
    client.rotate_key()
    assert client.api_key == "key2"
    
    client.rotate_key()
    assert client.api_key == "key3"
    
    client.rotate_key()
    assert client.api_key == "key1"  # Wrap around

@patch.dict(os.environ, {"GEMINI_API_KEY": "some-key", "LLM_MODEL": "qwen2.5-coder:3b"})
def test_detect_provider_gemini_leakage_prevention():
    # Clear LLM_URL to trigger Gemini detection
    if "LLM_URL" in os.environ:
        del os.environ["LLM_URL"]
        
    base_url, model, key = _detect_provider()
    # It should discard 'qwen' and fallback to default gemini-2.0-flash
    assert model == "gemini-2.0-flash"
    assert key == "some-key"

@patch.dict(os.environ, {"GEMINI_API_KEY": "some-key", "LLM_MODEL": "gemini-3.5-flash"})
def test_detect_provider_gemini_valid_override():
    # Clear LLM_URL to trigger Gemini detection
    if "LLM_URL" in os.environ:
        del os.environ["LLM_URL"]
        
    base_url, model, key = _detect_provider()
    # It should allow gemini-3.5-flash as a valid Gemini model override
    assert model == "gemini-3.5-flash"
