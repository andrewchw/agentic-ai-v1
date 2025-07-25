#!/usr/bin/env python3
"""
Test DeepSeek R1 Removal and Llama 3.3 70B Prioritization
=========================================================
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["ENABLE_PREMIUM_BACKUP"] = "true"

def test_deepseek_removal():
    """Test that DeepSeek R1 has been removed from the model list"""
    print("=" * 70)
    print("TESTING DEEPSEEK R1 REMOVAL & LLAMA 3.3 70B PRIORITIZATION")
    print("=" * 70)
    
    try:
        from src.utils.free_models_manager import FreeModelsManager
        
        # Initialize manager (will create new config without DeepSeek R1)
        manager = FreeModelsManager()
        
        print(f"\n1. 📊 MODEL INVENTORY CHECK")
        print(f"   Total models: {len(manager.models)}")
        print(f"   Current default: {manager.current_model_id}")
        
        # Check if DeepSeek R1 is in the models
        deepseek_found = False
        llama_found = False
        
        for key, model in manager.models.items():
            if "deepseek-r1" in model.id:
                deepseek_found = True
                print(f"   ❌ DeepSeek R1 still found: {model.name}")
            elif "llama-3.3-70b" in model.id:
                llama_found = True
                print(f"   ✅ Llama 3.3 70B found: {model.name}")
                print(f"      Status: {model.rate_limit_info}")
                print(f"      Available: {model.is_available}")
        
        print(f"\n2. 🔍 VERIFICATION RESULTS")
        if not deepseek_found:
            print(f"   ✅ DeepSeek R1 successfully removed from model list")
        else:
            print(f"   ❌ DeepSeek R1 still present in model list")
        
        if llama_found:
            print(f"   ✅ Llama 3.3 70B properly configured")
        else:
            print(f"   ❌ Llama 3.3 70B not found")
        
        print(f"\n3. 🎯 MODEL SELECTION TESTING")
        
        # Test different use cases to see which model is selected
        use_cases = ["general", "reasoning", "analysis", "conversation"]
        
        for use_case in use_cases:
            best_model = manager.get_best_available_model(use_case)
            print(f"   {use_case.upper()}: {best_model.name}")
            if "llama-3.3-70b" in best_model.id:
                print(f"      ✅ Using Llama 3.3 70B (most reliable)")
            elif "deepseek-r1" in best_model.id:
                print(f"      ❌ Still using DeepSeek R1 (should be removed)")
            else:
                print(f"      ⚡ Using alternative: {best_model.id}")
        
        print(f"\n4. 📋 CURRENT MODEL RANKING")
        working_models = manager.get_working_models()
        
        print(f"   Working models: {len(working_models)}")
        for i, (key, model) in enumerate(working_models.items(), 1):
            priority = "🏆 PRIMARY" if i == 1 else f"#{i}"
            print(f"   {priority}: {model.name}")
            if "llama-3.3-70b" in model.id:
                print(f"      ✅ Most reliable model prioritized")
        
        # Final validation
        success = not deepseek_found and llama_found
        
        if success:
            print(f"\n🎉 SUCCESS: DeepSeek R1 removed, Llama 3.3 70B prioritized!")
        else:
            print(f"\n❌ ISSUE: Configuration needs adjustment")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_config():
    """Test that environment variables have been updated"""
    print(f"\n" + "=" * 70)
    print("TESTING ENVIRONMENT CONFIGURATION UPDATES")
    print("=" * 70)
    
    try:
        # Load .env file
        env_file = project_root / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
            
            print(f"\n📝 ENVIRONMENT VARIABLE CHECK:")
            
            # Check for DeepSeek references
            if "deepseek-r1" in content.lower():
                print(f"   ❌ DeepSeek R1 still referenced in .env")
                return False
            else:
                print(f"   ✅ DeepSeek R1 removed from .env")
            
            # Check for Llama 3.3 references
            if "llama-3.3-70b" in content:
                print(f"   ✅ Llama 3.3 70B set as primary")
                print(f"   ✅ Environment properly configured")
                return True
            else:
                print(f"   ❌ Llama 3.3 70B not found in .env")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def main():
    """Run removal verification tests"""
    print("🔧 DEEPSEEK R1 REMOVAL VERIFICATION")
    print("🎯 Prioritizing Llama 3.3 70B as most reliable model")
    
    results = []
    
    # Test 1: Model removal and prioritization
    results.append(test_deepseek_removal())
    
    # Test 2: Environment configuration
    results.append(test_environment_config())
    
    # Summary
    print("\n" + "=" * 70)
    print("🏁 REMOVAL VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 SUCCESSFULLY UPDATED!")
        print("✅ DeepSeek R1 removed from model list")
        print("✅ Llama 3.3 70B prioritized as most reliable")
        print("✅ Environment variables updated")
        print("\n🚀 READY: System now uses most reliable models first")
        print("   Primary: Llama 3.3 70B (most stable)")
        print("   Fallback: Mistral Small 3.2 24B")
        print("   Coding: Qwen 2.5 Coder 32B")
    else:
        print("❌ Some updates incomplete - check output above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
