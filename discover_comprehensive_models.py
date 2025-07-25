#!/usr/bin/env python3
"""
Comprehensive Free Model Discovery & Testing
===========================================

Find more working free models on OpenRouter and test premium backup options.
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openrouter_models():
    """Fetch all available models from OpenRouter API"""
    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        if response.status_code == 200:
            models = response.json()
            return models.get('data', [])
        else:
            print(f"❌ Failed to fetch models: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        return []

def find_free_models():
    """Find all free models available on OpenRouter"""
    print("🔍 DISCOVERING FREE MODELS ON OPENROUTER")
    print("=" * 50)
    
    all_models = get_openrouter_models()
    if not all_models:
        return []
    
    free_models = []
    
    for model in all_models:
        pricing = model.get('pricing', {})
        prompt_price = float(pricing.get('prompt', '999'))
        completion_price = float(pricing.get('completion', '999'))
        
        # Check if it's free (price = 0)
        if prompt_price == 0 and completion_price == 0:
            free_models.append({
                'id': model['id'],
                'name': model.get('name', model['id']),
                'context_length': model.get('context_length', 'Unknown'),
                'architecture': model.get('architecture', {})
            })
    
    print(f"📊 Found {len(free_models)} free models:")
    for model in free_models:
        print(f"   • {model['name']}: {model['id']}")
    
    return free_models

def test_model_api_call(model_id, model_name, api_key):
    """Test a single model with OpenRouter API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_id,  # No openrouter/ prefix for direct API calls
        "messages": [
            {"role": "user", "content": "Say 'OK' if you can respond."}
        ],
        "max_tokens": 10,
        "temperature": 0.1
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
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                return True, f"✅ SUCCESS - Response: {content.strip()}"
        elif response.status_code == 429:
            return False, "⚠️ RATE LIMITED (429)"
        elif response.status_code == 404:
            return False, "❌ NOT FOUND (404)"
        elif response.status_code == 400:
            return False, "❌ BAD REQUEST (400)"
        elif response.status_code == 401:
            return False, "❌ UNAUTHORIZED (401)"
        else:
            return False, f"❌ ERROR ({response.status_code})"
            
    except requests.exceptions.Timeout:
        return False, "❌ TIMEOUT"
    except Exception as e:
        return False, f"❌ EXCEPTION: {str(e)[:50]}"

def test_premium_models(api_key):
    """Test premium backup models"""
    print("\n🎯 TESTING PREMIUM BACKUP MODELS")
    print("=" * 50)
    
    premium_models = [
        ("deepseek/deepseek-v3", "DeepSeek V3"),
        ("openai/gpt-4o-mini", "GPT-4o Mini"),
        ("anthropic/claude-3-haiku", "Claude 3 Haiku"),
        ("google/gemini-flash-1.5", "Gemini Flash 1.5"),
        ("mistralai/mistral-small", "Mistral Small")
    ]
    
    working_premium = []
    
    for model_id, model_name in premium_models:
        print(f"\n🔍 Testing: {model_name}")
        print(f"   ID: {model_id}")
        
        success, message = test_model_api_call(model_id, model_name, api_key)
        print(f"   {message}")
        
        if success:
            working_premium.append((model_id, model_name))
        
        time.sleep(1)  # Rate limiting
    
    return working_premium

def test_discovered_free_models(free_models, api_key):
    """Test all discovered free models"""
    print("\n🧪 TESTING DISCOVERED FREE MODELS")
    print("=" * 50)
    
    working_free = []
    failed_free = []
    
    # Prioritize models that look promising
    priority_keywords = ['instruct', 'chat', 'free', 'coder', 'gemma', 'llama', 'mistral', 'phi', 'qwen']
    
    # Sort models by priority
    def priority_score(model):
        score = 0
        model_lower = model['id'].lower()
        for keyword in priority_keywords:
            if keyword in model_lower:
                score += 1
        return score
    
    free_models.sort(key=priority_score, reverse=True)
    
    print(f"🔄 Testing {len(free_models)} free models...")
    
    for i, model in enumerate(free_models):
        model_id = model['id']
        model_name = model['name']
        
        print(f"\n🔍 [{i+1}/{len(free_models)}] Testing: {model_name}")
        print(f"   ID: {model_id}")
        
        success, message = test_model_api_call(model_id, model_name, api_key)
        print(f"   {message}")
        
        if success:
            working_free.append(model)
        else:
            failed_free.append((model, message))
        
        time.sleep(1)  # Rate limiting between requests
        
        # Stop early if we find enough working models
        if len(working_free) >= 10:
            print(f"\n✅ Found {len(working_free)} working models, stopping early...")
            break
    
    return working_free, failed_free

def main():
    """Main discovery and testing function"""
    print("🚀 COMPREHENSIVE MODEL DISCOVERY & TESTING")
    print("🎯 Finding more free models + premium backups")
    print("=" * 60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return
    
    # Step 1: Discover all free models
    free_models = find_free_models()
    
    if not free_models:
        print("❌ No free models discovered")
        return
    
    # Step 2: Test premium backup models first
    working_premium = test_premium_models(api_key)
    
    # Step 3: Test discovered free models
    working_free, failed_free = test_discovered_free_models(free_models, api_key)
    
    # Step 4: Generate results
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    print(f"\n✅ WORKING FREE MODELS ({len(working_free)}):")
    for model in working_free:
        print(f"   • {model['name']}: {model['id']}")
    
    print(f"\n🎯 WORKING PREMIUM BACKUP MODELS ({len(working_premium)}):")
    for model_id, model_name in working_premium:
        print(f"   • {model_name}: {model_id}")
    
    print(f"\n❌ FAILED FREE MODELS ({len(failed_free)}):")
    for model, reason in failed_free[:10]:  # Show first 10 failures
        print(f"   • {model['name']}: {reason}")
    
    # Step 5: Generate configuration recommendations
    print(f"\n🔧 RECOMMENDED CONFIGURATION:")
    print("=" * 40)
    
    if working_free:
        print("\n# Add to .env for free models:")
        for i, model in enumerate(working_free[:5]):  # Top 5 working free models
            if i == 0:
                print(f"DEFAULT_MODEL={model['id']}")
            else:
                print(f"BACKUP_MODEL_{i}={model['id']}")
    
    if working_premium:
        print(f"\n# Add to .env for premium backup:")
        for i, (model_id, model_name) in enumerate(working_premium[:2]):  # Top 2 premium
            print(f"PREMIUM_BACKUP_{i+1}={model_id}")
    
    # Step 6: Save results to file
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'working_free_models': working_free,
        'working_premium_models': working_premium,
        'failed_models': [(model['id'], reason) for model, reason in failed_free]
    }
    
    with open('model_discovery_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: model_discovery_results.json")
    print(f"🎉 Discovery complete! Found {len(working_free)} free + {len(working_premium)} premium models")

if __name__ == "__main__":
    main()
