#!/usr/bin/env python3
"""
Test Smart Model Management System
=================================

Quick test to validate the new multi-model system with automatic failover.
"""

import os
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.free_models_manager import get_free_models_manager
from src.utils.smart_litellm_client import get_smart_litellm_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_free_models_manager():
    """Test the free models manager"""
    print("🧪 Testing Free Models Manager...")
    
    manager = get_free_models_manager()
    
    # Show available models
    models = manager.get_available_models()
    print(f"📋 Found {len(models)} free models:")
    for key, model in models.items():
        status = "🟢" if manager._is_model_available(model) else "🔴"
        print(f"  {status} {model.name} ({model.provider})")
    
    # Test model selection
    current_model = manager.get_current_model()
    print(f"\n⭐ Current model: {current_model.name}")
    
    # Test different use cases
    use_cases = ["code", "analysis", "creative", "general"]
    for use_case in use_cases:
        model_for_litellm = manager.get_model_for_litellm(use_case)
        model_for_openrouter = manager.get_model_for_openrouter_client(use_case)
        print(f"  📝 {use_case}: LiteLLM='{model_for_litellm}', OpenRouter='{model_for_openrouter}'")
    
    print("✅ Free Models Manager test completed\n")

def test_smart_client():
    """Test the smart LiteLLM client"""
    print("🧪 Testing Smart LiteLLM Client...")
    
    client = get_smart_litellm_client()
    
    # Show model info
    model_info = client.get_model_info()
    print(f"📊 Current model info:")
    for key, value in model_info.items():
        print(f"  {key}: {value}")
    
    # Test a simple completion
    print("\n🔄 Testing completion...")
    try:
        test_messages = [
            {"role": "user", "content": "Say 'Hello from the free model system!' in exactly those words."}
        ]
        
        response = client.completion(
            messages=test_messages,
            use_case="general",
            max_tokens=50
        )
        
        content = response.choices[0].message.content
        print(f"✅ Completion successful!")
        print(f"📝 Response: {content}")
        
    except Exception as e:
        print(f"❌ Completion failed: {e}")
    
    print("✅ Smart Client test completed\n")

def test_model_status():
    """Test model status reporting"""
    print("🧪 Testing Model Status...")
    
    manager = get_free_models_manager()
    client = get_smart_litellm_client()
    
    # Get comprehensive status
    status = client.get_all_models_status()
    print(f"📊 System Status:")
    print(f"  Total Models: {status['total_models']}")
    print(f"  Available Models: {status['available_models']}")
    print(f"  Current Model: {status['current_model']}")
    
    print(f"\n📋 Individual Model Status:")
    for key, model_status in status['models'].items():
        available_icon = "🟢" if model_status['available'] else "🔴"
        print(f"  {available_icon} {model_status['name']}")
        print(f"    Failures: {model_status['failure_count']}")
        print(f"    Last Used: {model_status['last_used'] or 'Never'}")
    
    print("✅ Model Status test completed\n")

def main():
    """Run all tests"""
    print("🚀 Starting Smart Model Management Tests\n")
    
    try:
        test_free_models_manager()
        test_smart_client()
        test_model_status()
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
