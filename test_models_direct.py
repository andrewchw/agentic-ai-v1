#!/usr/bin/env python3
"""
Test Working Free Models
========================

Simple test to validate which models actually work on OpenRouter
"""

import os
import requests
import json

def test_models_directly():
    """Test models directly via OpenRouter API"""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        return
    
    # Models to test based on our configuration
    test_models = [
        "deepseek/deepseek-r1:free",
        "qwen/qwen3-coder:free", 
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemma-2-7b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    working_models = []
    failed_models = []
    
    print("🧪 Testing Models Directly via OpenRouter API")
    print("=" * 50)
    
    for model in test_models:
        print(f"\n🔍 Testing: {model}")
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 20
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"   ✅ SUCCESS: {content}")
                working_models.append(model)
            else:
                error_info = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"   ❌ FAILED ({response.status_code}): {error_info}")
                failed_models.append((model, response.status_code, error_info))
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed_models.append((model, "exception", str(e)))
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Working models ({len(working_models)}):")
    for model in working_models:
        print(f"   • {model}")
    
    print(f"\n❌ Failed models ({len(failed_models)}):")
    for model, status, error in failed_models:
        print(f"   • {model} ({status})")
    
    # Generate updated configuration
    if working_models:
        print(f"\n🔧 Suggested configuration update:")
        print(f"DEFAULT_MODEL={working_models[0]}")
        print(f"FALLBACK_LLM_MODEL=openrouter/{working_models[1] if len(working_models) > 1 else working_models[0]}")

if __name__ == "__main__":
    test_models_directly()
