#!/usr/bin/env python3
"""
Quick Model Verification
=======================

Test specific models to see which ones work
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_specific_models():
    """Test specific models we want to use"""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        return
    
    # Test only the models we're actually trying to use
    models_to_test = [
        ("deepseek/deepseek-r1:free", "DeepSeek R1 Free"),
        ("qwen/qwen3-coder:free", "Qwen3 Coder Free"),
        ("meta-llama/llama-3.1-8b-instruct:free", "Llama 3.1 8B (should fail)"),
        ("google/gemma-2-7b-it:free", "Gemma 2 7B Free"),
        ("mistralai/mistral-7b-instruct:free", "Mistral 7B Free")
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    working = []
    failed = []
    
    print("🧪 Testing Key Models for Configuration")
    print("=" * 50)
    
    for model_id, model_name in models_to_test:
        print(f"\n🔍 Testing: {model_name}")
        print(f"   ID: {model_id}")
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS")
                working.append((model_id, model_name))
            else:
                error_info = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"   ❌ FAILED ({response.status_code})")
                failed.append((model_id, model_name, response.status_code))
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed.append((model_id, model_name, "exception"))
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Working models ({len(working)}):")
    for model_id, name in working:
        print(f"   • {name}: {model_id}")
    
    print(f"\n❌ Failed models ({len(failed)}):")
    for model_id, name, error in failed:
        print(f"   • {name}: {error}")
    
    if working:
        print(f"\n🔧 RECOMMENDED CONFIGURATION:")
        print(f"DEFAULT_MODEL={working[0][0]}")
        if len(working) > 1:
            print(f"FALLBACK_LLM_MODEL=openrouter/{working[1][0]}")

if __name__ == "__main__":
    test_specific_models()
