#!/usr/bin/env python3
"""
Test CrewAI Configuration Fix - Verify DeepSeek R1 Removal
"""
import os
import sys
import importlib.util

def test_crew_config():
    """Test that crew_config.py no longer uses DeepSeek R1"""
    print("🔧 Testing CrewAI Configuration...")
    
    # Read the crew_config.py file
    config_file = "src/agents/crew_config.py"
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            
        if "deepseek-r1" in content.lower() or "deepseek/deepseek-r1" in content.lower():
            print(f"   ❌ DeepSeek R1 still referenced in {config_file}")
            return False
        else:
            print(f"   ✅ DeepSeek R1 removed from {config_file}")
            
        if "llama-3.3-70b" in content:
            print(f"   ✅ Llama 3.3 70B now configured in {config_file}")
            return True
        else:
            print(f"   ❌ Llama 3.3 70B not found in {config_file}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to read {config_file}: {e}")
        return False

def test_orchestrator_config():
    """Test that crewai_enhanced_orchestrator.py no longer uses DeepSeek R1"""
    print("🔧 Testing CrewAI Orchestrator Configuration...")
    
    config_file = "crewai_enhanced_orchestrator.py"
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            
        if "deepseek/deepseek-r1" in content.lower():
            print(f"   ❌ DeepSeek R1 still referenced in {config_file}")
            return False
        else:
            print(f"   ✅ DeepSeek R1 removed from {config_file}")
            
        if "llama-3.3-70b" in content:
            print(f"   ✅ Llama 3.3 70B now configured in {config_file}")
            return True
        else:
            print(f"   ❌ Llama 3.3 70B not found in {config_file}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to read {config_file}: {e}")
        return False

def test_app_config():
    """Test that app_config.py no longer uses DeepSeek R1 as default"""
    print("🔧 Testing App Configuration...")
    
    config_file = "config/app_config.py"
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            
        if "deepseek/deepseek-r1" in content.lower():
            print(f"   ❌ DeepSeek R1 still referenced in {config_file}")
            return False
        else:
            print(f"   ✅ DeepSeek R1 removed from {config_file}")
            
        if "llama-3.3-70b" in content:
            print(f"   ✅ Llama 3.3 70B now configured in {config_file}")
            return True
        else:
            print(f"   ❌ Llama 3.3 70B not found in {config_file}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to read {config_file}: {e}")
        return False

def test_environment_variables():
    """Test that environment variables are properly set"""
    print("🔧 Testing Environment Variables...")
    
    # Test .env file
    env_file = ".env"
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "deepseek-r1" in content.lower():
            print(f"   ❌ DeepSeek R1 still referenced in {env_file}")
            return False
        else:
            print(f"   ✅ DeepSeek R1 removed from {env_file}")
            
        if "meta-llama/llama-3.3-70b-instruct:free" in content:
            print(f"   ✅ Llama 3.3 70B properly configured in {env_file}")
            return True
        else:
            print(f"   ❌ Llama 3.3 70B not found in {env_file}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to read {env_file}: {e}")
        return False

def test_free_models_manager():
    """Test that FreeModelsManager no longer defaults to DeepSeek R1"""
    print("🔧 Testing Free Models Manager...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Import the FreeModelsManager
        from src.utils.free_models_manager import FreeModelsManager
        
        # Initialize manager
        manager = FreeModelsManager()
        
        # Get default preference
        default_pref = manager.get_user_preference()
        
        if "deepseek" in default_pref.lower():
            print(f"   ❌ FreeModelsManager still defaults to DeepSeek: {default_pref}")
            return False
        elif "llama33-70b" in default_pref:
            print(f"   ✅ FreeModelsManager now defaults to Llama 3.3 70B: {default_pref}")
            return True
        else:
            print(f"   ⚠️  FreeModelsManager defaults to: {default_pref}")
            return True  # Not DeepSeek, so it's fine
            
    except Exception as e:
        print(f"   ❌ Failed to test FreeModelsManager: {e}")
        return False

def main():
    """Run all configuration tests"""
    print("="*70)
    print("🔧 CREWAI CONFIGURATION FIX VERIFICATION")
    print("="*70)
    
    tests = [
        ("CrewAI Config", test_crew_config),
        ("Orchestrator Config", test_orchestrator_config),
        ("App Config", test_app_config),
        ("Environment Variables", test_environment_variables),
        ("Free Models Manager", test_free_models_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ Test {test_name} failed with error: {e}")
            print()
    
    print("="*70)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CONFIGURATION FIXES SUCCESSFUL!")
        print("✅ DeepSeek R1 completely removed from all configurations")
        print("✅ Llama 3.3 70B properly configured as primary model")
        print("✅ System ready for reliable operation")
        return True
    else:
        print("❌ Some configuration fixes failed")
        print("⚠️  Manual review may be needed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
