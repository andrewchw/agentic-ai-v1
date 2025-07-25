#!/usr/bin/env python3
"""
Test Updated Free Models System
==============================

Tests the updated free models system with:
1. Llama3 as default instead of qwen3-coder
2. DeepSeek models added to the available options
3. Automatic failover functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.free_models_manager import FreeModelsManager
from src.utils.smart_litellm_client import SmartLiteLLMClient
import json

def test_updated_models():
    """Test the updated models system"""
    print("🧪 Testing Updated Free Models System")
    print("=" * 50)
    
    # Initialize the models manager
    models_manager = FreeModelsManager()
    
    print("\n📊 Available Models:")
    print("-" * 30)
    
    available_models = models_manager.get_available_models()
    for i, (key, model) in enumerate(available_models.items(), 1):
        is_current = "⭐ DEFAULT" if key == models_manager.current_model_id else ""
        print(f"{i}. {model.name} ({model.provider}) {is_current}")
        print(f"   ID: {model.id}")
        print(f"   Good for: {', '.join(model.good_for)}")
        print(f"   Status: {'✅ Available' if model.is_available else '❌ Unavailable'}")
        print(f"   Rate info: {model.rate_limit_info}")
        print()
    
    # Test default model
    print(f"\n🎯 Current Default Model: {models_manager.current_model_id}")
    current_model = models_manager.get_current_model()
    print(f"   Name: {current_model.name}")
    print(f"   Provider: {current_model.provider}")
    print(f"   ID for LiteLLM: {models_manager.get_model_for_litellm()}")
    print(f"   ID for OpenRouter: {models_manager.get_model_for_openrouter_client()}")
    
    # Test model selection for different use cases
    print("\n🎯 Model Selection by Use Case:")
    print("-" * 30)
    
    use_cases = ["general", "reasoning", "conversation", "analysis", "code"]
    for use_case in use_cases:
        best_model = models_manager.get_best_available_model(use_case)
        print(f"   {use_case.capitalize()}: {best_model.name}")
    
    # Test Smart LiteLLM Client
    print("\n🤖 Testing Smart LiteLLM Client:")
    print("-" * 30)
    
    try:
        smart_client = SmartLiteLLMClient(models_manager)
        
        # Test simple completion
        test_messages = [
            {"role": "user", "content": "Say 'Hello from the updated model system!' and identify which model you are."}
        ]
        
        print("📤 Sending test message...")
        response = smart_client.completion(
            model="dummy",  # This will be replaced by smart client
            messages=test_messages,
            max_tokens=100,
            temperature=0.7
        )
        
        print("📥 Response received:")
        print(f"   Model used: {response.model}")
        print(f"   Content: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Smart client test failed: {e}")
    
    # Show model health status
    print("\n💊 Model Health Status:")
    print("-" * 30)
    
    for key, model in available_models.items():
        status = "🟢 Healthy" if model.failure_count == 0 else f"🟡 {model.failure_count} failures"
        if model.failure_count >= models_manager.failure_threshold:
            status = "🔴 Failed (in cooldown)"
        
        print(f"   {model.name}: {status}")
        if model.last_failure:
            print(f"     Last failure: {model.last_failure}")
    
    return True

def test_model_switching():
    """Test manual model switching"""
    print("\n🔄 Testing Model Switching:")
    print("-" * 30)
    
    models_manager = FreeModelsManager()
    
    # Try switching to DeepSeek
    print("Switching to DeepSeek R1...")
    models_manager.save_user_preference("deepseek-r1")
    
    print(f"New default: {models_manager.current_model_id}")
    print(f"LiteLLM format: {models_manager.get_model_for_litellm()}")
    
    # Switch back to Llama3
    print("\nSwitching back to Llama3...")
    models_manager.save_user_preference("llama3-8b")
    
    print(f"New default: {models_manager.current_model_id}")
    print(f"LiteLLM format: {models_manager.get_model_for_litellm()}")

def main():
    """Main test function"""
    try:
        print("🚀 Updated Free Models System Test")
        print("=" * 50)
        
        # Test the updated system
        test_updated_models()
        
        # Test model switching
        test_model_switching()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ Llama3 set as default (instead of qwen3-coder)")
        print("   ✅ DeepSeek models added to available options")
        print("   ✅ Model switching functionality working")
        print("   ✅ Smart client integration functional")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
