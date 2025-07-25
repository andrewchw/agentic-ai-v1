#!/usr/bin/env python3
"""
Debug Model Switching Issues
============================

This script will help debug why model switching isn't working
and why auto-fallback is failing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.free_models_manager import FreeModelsManager
from src.utils.smart_litellm_client import SmartLiteLLMClient
import litellm
import json

def test_environment_setup():
    """Test the current environment setup"""
    print("🔧 Environment Configuration:")
    print("-" * 40)
    
    env_vars = [
        "OPENROUTER_API_KEY", "DEFAULT_MODEL", "FALLBACK_LLM_MODEL",
        "OPENAI_API_BASE", "OPENAI_MODEL_NAME", "LITELLM_DEFAULT_MODEL"
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "Not set")
        print(f"   {var}: {value}")
    
    print()

def test_models_manager():
    """Test the models manager directly"""
    print("🎯 Models Manager Test:")
    print("-" * 40)
    
    manager = FreeModelsManager()
    
    print(f"Current model ID: {manager.current_model_id}")
    current_model = manager.get_current_model()
    print(f"Current model name: {current_model.name}")
    print(f"Current model for LiteLLM: {manager.get_model_for_litellm()}")
    
    print(f"\nAvailable models: {len(manager.get_available_models())}")
    for key, model in manager.get_available_models().items():
        status = "✅" if model.is_available else "❌"
        failures = f"({model.failure_count} failures)" if model.failure_count > 0 else ""
        current = "⭐ CURRENT" if key == manager.current_model_id else ""
        print(f"   {status} {model.name} {failures} {current}")
    
    return manager

def test_litellm_direct():
    """Test LiteLLM directly without smart client"""
    print("\n🤖 Direct LiteLLM Test:")
    print("-" * 40)
    
    try:
        # Test with environment default
        default_model = os.environ.get("LITELLM_DEFAULT_MODEL", "openrouter/meta-llama/llama-3.1-8b-instruct:free")
        
        print(f"Testing model: {default_model}")
        
        response = litellm.completion(
            model=default_model,
            messages=[{"role": "user", "content": "Say 'Hello from direct LiteLLM test' and identify yourself"}],
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"✅ Direct LiteLLM success!")
        print(f"   Model used: {response.model}")
        print(f"   Response: {response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct LiteLLM failed: {e}")
        return False

def test_smart_client():
    """Test the smart client"""
    print("\n🧠 Smart Client Test:")
    print("-" * 40)
    
    try:
        client = SmartLiteLLMClient()
        
        response = client.completion(
            messages=[{"role": "user", "content": "Say 'Hello from smart client test' and identify yourself"}],
            use_case="general",
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"✅ Smart client success!")
        print(f"   Model used: {response.model}")
        print(f"   Response: {response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Smart client failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_switching():
    """Test manual model switching"""
    print("\n🔄 Model Switching Test:")
    print("-" * 40)
    
    manager = FreeModelsManager()
    
    # Get current model
    original_model = manager.current_model_id
    print(f"Original model: {original_model}")
    
    # Get available models
    available = list(manager.get_available_models().keys())
    print(f"Available models: {available}")
    
    # Try switching to a different model
    for model_key in available:
        if model_key != original_model:
            print(f"\nSwitching to: {model_key}")
            manager.save_user_preference(model_key)
            
            new_current = manager.current_model_id
            print(f"New current: {new_current}")
            print(f"LiteLLM format: {manager.get_model_for_litellm()}")
            
            # Test with the new model
            try:
                client = SmartLiteLLMClient()
                response = client.completion(
                    messages=[{"role": "user", "content": f"Hello from {model_key}"}],
                    max_tokens=50
                )
                print(f"✅ Test successful with {model_key}")
                print(f"   Response: {response.choices[0].message.content}")
            except Exception as e:
                print(f"❌ Test failed with {model_key}: {e}")
            
            break
    
    # Switch back
    print(f"\nSwitching back to: {original_model}")
    manager.save_user_preference(original_model)

def simulate_failure():
    """Simulate a model failure to test auto-switching"""
    print("\n⚠️  Failure Simulation Test:")
    print("-" * 40)
    
    manager = FreeModelsManager()
    original_model = manager.current_model_id
    
    # Simulate failure
    current_model_obj = manager.get_current_model()
    print(f"Simulating failure for: {current_model_obj.name}")
    
    # Handle the failure
    manager.handle_model_failure(
        f"openrouter/{current_model_obj.id}", 
        "rate_limit"
    )
    
    # Check if it switched
    new_model = manager.current_model_id
    if new_model != original_model:
        print(f"✅ Auto-switched from {original_model} to {new_model}")
    else:
        print(f"❌ No auto-switch occurred (still using {new_model})")
    
    # Reset the failure count
    manager.reset_model_failures(original_model)

def main():
    """Main debug function"""
    print("🔍 Debugging Model Switching Issues")
    print("=" * 50)
    
    # Test environment
    test_environment_setup()
    
    # Test models manager
    manager = test_models_manager()
    
    # Test direct LiteLLM
    direct_works = test_litellm_direct()
    
    # Test smart client
    smart_works = test_smart_client()
    
    # Test model switching
    test_model_switching()
    
    # Test failure simulation
    simulate_failure()
    
    print("\n📋 Summary:")
    print("-" * 40)
    print(f"   Direct LiteLLM: {'✅ Working' if direct_works else '❌ Failed'}")
    print(f"   Smart Client: {'✅ Working' if smart_works else '❌ Failed'}")
    print(f"   Current Default: {manager.current_model_id}")
    print(f"   Models Available: {len(manager.get_available_models())}")

if __name__ == "__main__":
    main()
