#!/usr/bin/env python3
"""
Check available FREE models on OpenRouter
=========================================

This script checks what free models are actually available on OpenRouter
to avoid using paid models.
"""

import os
import requests

def check_free_openrouter_models():
    """Check what free models are available on OpenRouter"""
    
    print("🔍 Checking Available FREE Models on OpenRouter")
    print("=" * 50)
    
    try:
        # Get models from OpenRouter API
        response = requests.get("https://openrouter.ai/api/v1/models")
        
        if response.status_code == 200:
            models = response.json()
            
            # Filter for free models
            free_models = []
            for model in models.get("data", []):
                pricing = model.get("pricing", {})
                prompt_price = float(pricing.get("prompt", "1"))
                completion_price = float(pricing.get("completion", "1"))
                
                if prompt_price == 0 and completion_price == 0:
                    free_models.append({
                        "id": model.get("id"),
                        "name": model.get("name", "Unknown"),
                        "context_length": model.get("context_length", "Unknown")
                    })
            
            print(f"✅ Found {len(free_models)} FREE models:")
            print()
            
            for i, model in enumerate(free_models[:10], 1):  # Show top 10
                print(f"{i:2}. {model['id']}")
                print(f"    Name: {model['name']}")
                print(f"    Context: {model['context_length']}")
                print()
            
            if free_models:
                print(f"🎯 Recommended free model for CrewAI: {free_models[0]['id']}")
                return free_models[0]['id']
            else:
                print("❌ No completely free models found")
                return None
                
        else:
            print(f"❌ Failed to fetch models: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return None

def test_free_model(model_id):
    """Test a specific free model"""
    
    print(f"\n🧪 Testing Free Model: {model_id}")
    print("-" * 40)
    
    try:
        from crewai import LLM
        
        # Set environment variables
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        os.environ["OPENAI_API_KEY"] = openrouter_key
        os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
        
        # Create LLM with the free model
        llm = LLM(
            model=f"openrouter/{model_id}",
            temperature=0.3,
            max_tokens=100
        )
        
        # Simple test call
        test_prompt = "What is 2+2? Respond with just the number."
        response = llm.call(test_prompt)
        
        print(f"✅ Free model test successful!")
        print(f"   Model: {model_id}")
        print(f"   Prompt: {test_prompt}")
        print(f"   Response: {str(response)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Free model test failed: {e}")
        return False

if __name__ == "__main__":
    # Check available free models
    recommended_model = check_free_openrouter_models()
    
    # Test the recommended model if found
    if recommended_model:
        success = test_free_model(recommended_model)
        
        if success:
            print(f"\n✅ SUCCESS: Use '{recommended_model}' as your free model")
        else:
            print(f"\n❌ FAILED: '{recommended_model}' didn't work, try another from the list above")
    else:
        print("\n⚠️  No free models found - you may need to use low-cost models instead")
