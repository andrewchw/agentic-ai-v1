#!/usr/bin/env python3
"""
Discover and test all available free models on OpenRouter
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ["OPENROUTER_API_KEY"] = "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"

def get_openrouter_models():
    """Get all available models from OpenRouter API"""
    print("🔍 Fetching all models from OpenRouter...")
    
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])
            print(f"✅ Found {len(models)} total models")
            return models
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        return []

def find_free_models(models):
    """Filter for free models"""
    print("\n🆓 Filtering for free models...")
    
    free_models = []
    
    for model in models:
        model_id = model.get('id', '')
        pricing = model.get('pricing', {})
        
        # Check if model has free pricing
        prompt_cost = pricing.get('prompt', '0')
        completion_cost = pricing.get('completion', '0')
        
        # Convert to float and check if free
        try:
            prompt_price = float(prompt_cost)
            completion_price = float(completion_cost)
            
            if prompt_price == 0 and completion_price == 0:
                free_models.append({
                    'id': model_id,
                    'name': model.get('name', ''),
                    'context_length': model.get('context_length', 0),
                    'description': model.get('description', ''),
                    'architecture': model.get('architecture', {}),
                    'top_provider': model.get('top_provider', {})
                })
        except:
            continue
    
    print(f"✅ Found {len(free_models)} free models")
    return free_models

def test_model_api(model_id):
    """Test if a model actually works via API call"""
    try:
        test_messages = [{"role": "user", "content": "Hi! Say 'OK' if you can respond."}]
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_id,
                "messages": test_messages,
                "max_tokens": 10,
                "temperature": 0.1
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return True, "✅ SUCCESS"
        elif response.status_code == 429:
            return False, "⚠️ RATE LIMITED"
        elif response.status_code == 404:
            return False, "❌ NOT FOUND"
        elif response.status_code == 400:
            return False, "❌ BAD REQUEST"
        else:
            return False, f"❌ ERROR {response.status_code}"
            
    except Exception as e:
        return False, f"❌ EXCEPTION: {str(e)[:50]}"
    
    return False, "❌ UNKNOWN"

def test_premium_models():
    """Test premium backup models"""
    print("\n" + "=" * 60)
    print("🔥 TESTING PREMIUM BACKUP MODELS")
    print("=" * 60)
    
    premium_models = [
        "deepseek/deepseek-v3",
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "anthropic/claude-3-haiku",
        "anthropic/claude-3-sonnet",
        "google/gemini-pro",
        "meta-llama/llama-3.3-70b-instruct"
    ]
    
    working_premium = []
    
    for model_id in premium_models:
        print(f"\n🔍 Testing: {model_id}")
        
        # Test with very short message to minimize costs
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5,
                    "temperature": 0.1
                },
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"   ✅ {model_id} - WORKS")
                working_premium.append(model_id)
            else:
                print(f"   ❌ {model_id} - ERROR {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {model_id} - EXCEPTION: {str(e)[:30]}")
    
    return working_premium

def main():
    """Main discovery function"""
    print("🚀 OPENROUTER FREE MODELS DISCOVERY")
    print("=" * 60)
    
    # Get all models
    all_models = get_openrouter_models()
    if not all_models:
        return
    
    # Filter for free models
    free_models = find_free_models(all_models)
    
    # Test each free model
    print(f"\n🧪 Testing {len(free_models)} free models...")
    print("=" * 60)
    
    working_models = []
    failed_models = []
    
    for i, model in enumerate(free_models, 1):
        model_id = model['id']
        print(f"\n{i:2d}/{len(free_models)} Testing: {model_id}")
        print(f"     Name: {model['name']}")
        
        works, status = test_model_api(model_id)
        print(f"     Status: {status}")
        
        if works:
            working_models.append(model)
        else:
            failed_models.append({**model, 'error': status})
        
        # Small delay to be respectful
        time.sleep(1)
    
    # Test premium models
    working_premium = test_premium_models()
    
    # Results
    print("\n" + "=" * 60)
    print("📊 DISCOVERY RESULTS")
    print("=" * 60)
    
    print(f"\n✅ WORKING FREE MODELS ({len(working_models)}):")
    for model in working_models:
        print(f"   • {model['name']}: {model['id']}")
        print(f"     Context: {model['context_length']:,} tokens")
    
    print(f"\n✅ WORKING PREMIUM MODELS ({len(working_premium)}):")
    for model_id in working_premium:
        print(f"   • {model_id}")
    
    print(f"\n❌ FAILED FREE MODELS ({len(failed_models)}):")
    for model in failed_models[:10]:  # Show first 10
        print(f"   • {model['name']}: {model['error']}")
    
    # Save results
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'working_free_models': working_models,
        'working_premium_models': working_premium,
        'failed_models': failed_models
    }
    
    with open('model_discovery_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to model_discovery_results.json")
    
    return working_models, working_premium

if __name__ == "__main__":
    working_free, working_premium = main()
