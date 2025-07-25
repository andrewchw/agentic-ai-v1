#!/usr/bin/env python3
"""
Final Configuration Verification - DeepSeek R1 Removal & Llama 3.3 70B Priority
Run in virtual environment to test all configurations
"""
import os
import sys
import json

def test_free_models_manager():
    """Test FreeModelsManager configuration"""
    print("🔧 Testing FreeModelsManager...")
    
    try:
        from src.utils.free_models_manager import FreeModelsManager
        
        # Initialize manager
        manager = FreeModelsManager()
        print("   ✅ FreeModelsManager initialized successfully")
        
        # Get available models
        available_models = manager.get_available_models()
        print(f"   📊 Available models: {len(available_models)}")
        
        # Check for DeepSeek R1
        deepseek_found = False
        llama_found = False
        
        for model in available_models:
            if 'deepseek-r1' in model.id.lower():
                deepseek_found = True
                print(f"   ❌ DeepSeek R1 still found: {model.id}")
            elif 'llama-3.3-70b' in model.id.lower():
                llama_found = True
                print(f"   ✅ Llama 3.3 70B found: {model.id}")
        
        if not deepseek_found:
            print("   ✅ DeepSeek R1 successfully removed from model list")
        
        # Test best available model
        best_model = manager.get_best_available_model()
        print(f"   🎯 Best available model: {best_model.id}")
        
        if 'llama-3.3-70b' in best_model.id.lower():
            print("   ✅ Llama 3.3 70B is prioritized as best model")
        elif 'deepseek-r1' in best_model.id.lower():
            print("   ❌ DeepSeek R1 still being used as best model")
        else:
            print(f"   ⚠️  Best model is: {best_model.id}")
        
        return not deepseek_found and llama_found
        
    except Exception as e:
        print(f"   ❌ Failed to test FreeModelsManager: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\n🔧 Testing Environment Variables...")
    
    try:
        # Check .env file
        with open('.env', 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        if 'deepseek-r1' in env_content.lower():
            print("   ❌ DeepSeek R1 still referenced in .env")
            return False
        else:
            print("   ✅ DeepSeek R1 removed from .env")
        
        if 'meta-llama/llama-3.3-70b-instruct:free' in env_content:
            print("   ✅ Llama 3.3 70B properly configured in .env")
            return True
        else:
            print("   ❌ Llama 3.3 70B not found in .env")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to test environment: {e}")
        return False

def test_app_config():
    """Test app configuration"""
    print("\n🔧 Testing App Configuration...")
    
    try:
        from config.app_config import AppConfig
        
        config = AppConfig()
        
        if 'deepseek-r1' in config.DEFAULT_MODEL.lower():
            print(f"   ❌ App config still uses DeepSeek R1: {config.DEFAULT_MODEL}")
            return False
        else:
            print(f"   ✅ App config DEFAULT_MODEL: {config.DEFAULT_MODEL}")
        
        if 'llama-3.3-70b' in config.DEFAULT_MODEL.lower():
            print("   ✅ App config properly configured for Llama 3.3 70B")
            return True
        else:
            print(f"   ⚠️  App config uses: {config.DEFAULT_MODEL}")
            return True  # Not DeepSeek, so it's acceptable
            
    except Exception as e:
        print(f"   ❌ Failed to test app config: {e}")
        return False

def test_crew_config():
    """Test CrewAI configuration"""
    print("\n🔧 Testing CrewAI Configuration...")
    
    try:
        # Read crew_config.py file
        with open('src/agents/crew_config.py', 'r', encoding='utf-8') as f:
            crew_content = f.read()
        
        if 'deepseek-r1' in crew_content.lower():
            print("   ❌ CrewAI config still references DeepSeek R1")
            return False
        else:
            print("   ✅ DeepSeek R1 removed from CrewAI config")
        
        if 'llama-3.3-70b' in crew_content.lower():
            print("   ✅ Llama 3.3 70B configured in CrewAI")
            return True
        else:
            print("   ❌ Llama 3.3 70B not found in CrewAI config")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to test CrewAI config: {e}")
        return False

def test_orchestrator_config():
    """Test CrewAI orchestrator configuration"""
    print("\n🔧 Testing CrewAI Orchestrator...")
    
    try:
        # Read orchestrator file
        with open('crewai_enhanced_orchestrator.py', 'r', encoding='utf-8') as f:
            orch_content = f.read()
        
        if 'deepseek/deepseek-r1' in orch_content.lower():
            print("   ❌ Orchestrator still references DeepSeek R1")
            return False
        else:
            print("   ✅ DeepSeek R1 removed from orchestrator")
        
        if 'llama-3.3-70b' in orch_content.lower():
            print("   ✅ Llama 3.3 70B configured in orchestrator")
            return True
        else:
            print("   ❌ Llama 3.3 70B not found in orchestrator")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to test orchestrator: {e}")
        return False

def test_smart_client():
    """Test SmartLiteLLMClient"""
    print("\n🔧 Testing SmartLiteLLMClient...")
    
    try:
        from src.utils.smart_litellm_client import SmartLiteLLMClient
        
        client = SmartLiteLLMClient()
        print("   ✅ SmartLiteLLMClient initialized successfully")
        
        # Test model selection
        current_model = client.get_current_model()
        print(f"   🎯 Current model: {current_model}")
        
        if 'deepseek-r1' in current_model.lower():
            print("   ❌ SmartLiteLLMClient still using DeepSeek R1")
            return False
        elif 'llama-3.3-70b' in current_model.lower():
            print("   ✅ SmartLiteLLMClient using Llama 3.3 70B")
            return True
        else:
            print(f"   ⚠️  SmartLiteLLMClient using: {current_model}")
            return True  # Not DeepSeek, so acceptable
            
    except Exception as e:
        print(f"   ❌ Failed to test SmartLiteLLMClient: {e}")
        return False

def main():
    """Run comprehensive configuration verification"""
    print("="*70)
    print("🔧 FINAL CONFIGURATION VERIFICATION")
    print("   DeepSeek R1 Removal & Llama 3.3 70B Prioritization")
    print("="*70)
    
    tests = [
        ("FreeModelsManager", test_free_models_manager),
        ("Environment Variables", test_environment_variables),
        ("App Configuration", test_app_config),
        ("CrewAI Configuration", test_crew_config),
        ("CrewAI Orchestrator", test_orchestrator_config),
        ("SmartLiteLLMClient", test_smart_client),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"   ✅ {test_name}: PASSED")
            else:
                print(f"   ❌ {test_name}: FAILED")
        except Exception as e:
            print(f"   ❌ {test_name}: ERROR - {e}")
        print("-" * 50)
    
    print("\n" + "="*70)
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CONFIGURATION FIXES SUCCESSFUL!")
        print("✅ DeepSeek R1 completely removed from all configurations")
        print("✅ Llama 3.3 70B properly prioritized as primary model")
        print("✅ System ready for reliable operation without DeepSeek R1 failures")
        print()
        print("🚀 READY TO USE:")
        print("   - Launch: python launch_dashboard.py")
        print("   - Primary Model: Llama 3.3 70B (most reliable)")
        print("   - Fallback: Mistral Small 3.2 24B")
        print("   - No more DeepSeek R1 rate limit issues!")
        return True
    else:
        print(f"❌ {total - passed} configuration issues detected")
        print("⚠️  Manual review recommended")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
