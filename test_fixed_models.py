#!/usr/bin/env python3
"""
Quick Test for Fixed Model System
=================================

Test the fixed model system with better error handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.free_models_manager import FreeModelsManager
from src.utils.smart_litellm_client import SmartLiteLLMClient

def test_fixed_system():
    """Test the fixed system"""
    print("🔧 Testing Fixed Model System")
    print("=" * 40)
    
    # Test models manager
    manager = FreeModelsManager()
    
    print(f"📊 Current Default: {manager.current_model_id}")
    current_model = manager.get_current_model()
    print(f"   Name: {current_model.name}")
    print(f"   Available: {current_model.is_available}")
    
    print(f"\n📋 All Models ({len(manager.get_available_models())}):")
    for key, model in manager.get_available_models().items():
        status = "✅" if model.is_available else "❌"
        current = "⭐" if key == manager.current_model_id else " "
        failures = f"({model.failure_count}f)" if model.failure_count > 0 else ""
        print(f"   {current} {status} {model.name} {failures}")
    
    print(f"\n🔧 Working Models ({len(manager.get_working_models())}):")
    for key, model in manager.get_working_models().items():
        current = "⭐" if key == manager.current_model_id else " "
        print(f"   {current} ✅ {model.name}")
    
    # Test smart client
    print(f"\n🤖 Testing Smart Client:")
    try:
        client = SmartLiteLLMClient()
        
        response = client.completion(
            messages=[{"role": "user", "content": "Hello! Please identify yourself briefly."}],
            max_tokens=50,
            temperature=0.7
        )
        
        print(f"✅ Smart client test successful!")
        print(f"   Model used: {response.model}")
        print(f"   Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Smart client test failed: {e}")
    
    return True

if __name__ == "__main__":
    test_fixed_system()
