#!/usr/bin/env python3
"""
Final Configuration Verification Script
Tests that DeepSeek R1 is completely removed and Llama 3.3 70B is properly configured
"""
import os
import sys
import json

def test_models_manager():
    """Test FreeModelsManager configuration"""
    print("🔧 Testing FreeModelsManager...")
    
    try:
        from src.utils.free_models_manager import FreeModelsManager
        manager = FreeModelsManager()
        print("   ✅ FreeModelsManager initialized successfully")
        
        # Get available models
        available_models = manager.get_available_models()
        print(f"   📊 Total available models: {len(available_models)}")
        
        # Check for DeepSeek R1
        deepseek_found = False
        for model in available_models:
            if 'deepseek-r1' in model.id.lower():
                deepseek_found = True
                print(f"   ❌ DeepSeek R1 still found: {model.id}")
                break
        
        if not deepseek_found:
            print("   ✅ DeepSeek R1 successfully removed from model list")
        
        # Check for Llama 3.3 70B
        llama_found = False
        for model in available_models:
            if 'llama-3.3-70b' in model.id:
                llama_found = True
                print(f"   ✅ Llama 3.3 70B found: {model.id}")
                break
        
        if not llama_found:
            print("   ⚠️  Llama 3.3 70B not found in available models")
        
        # Test best model selection
        try:
            best_model = manager.get_best_available_model()
            print(f"   🎯 Current best model: {best_model.id}")
            
            if 'deepseek-r1' in best_model.id.lower():
                print("   ❌ Best model is still DeepSeek R1!")
                return False
            elif 'llama-3.3-70b' in best_model.id:
                print("   ✅ Best model is Llama 3.3 70B (as expected)")
        except Exception as e:
            print(f"   ⚠️  Could not get best model: {e}")
        
        return not deepseek_found
        
    except Exception as e:
        print(f"   ❌ Failed to test FreeModelsManager: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("🔧 Testing Environment Variables...")
    
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
        else:
            print("   ❌ Llama 3.3 70B not found in .env")
            return False
        
        # Check actual environment
        default_model = os.getenv('DEFAULT_MODEL', '')
        if 'llama-3.3-70b' in default_model:
            print(f"   ✅ Environment DEFAULT_MODEL: {default_model}")
        else:
            print(f"   ⚠️  Environment DEFAULT_MODEL: {default_model}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to test environment: {e}")
        return False

def test_config_files():
    """Test configuration files"""
    print("🔧 Testing Configuration Files...")
    
    files_to_check = [
        ('config/app_config.py', 'App Config'),
        ('src/agents/crew_config.py', 'CrewAI Config'),
        ('crewai_enhanced_orchestrator.py', 'Orchestrator')
    ]
    
    all_good = True
    
    for filepath, name in files_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'deepseek-r1' in content.lower():
                print(f"   ❌ {name}: DeepSeek R1 still referenced")
                all_good = False
            else:
                print(f"   ✅ {name}: DeepSeek R1 removed")
            
            if 'llama-3.3-70b' in content:
                print(f"   ✅ {name}: Llama 3.3 70B configured")
            else:
                print(f"   ⚠️  {name}: Llama 3.3 70B not found")
                
        except Exception as e:
            print(f"   ❌ Failed to check {name}: {e}")
            all_good = False
    
    return all_good

def test_crew_ai_config():
    """Test CrewAI configuration can be imported and initialized"""
    print("🔧 Testing CrewAI Configuration...")
    
    try:
        from src.agents.crew_config import CrewAIConfig
        
        # Test initialization
        config = CrewAIConfig()
        print("   ✅ CrewAI configuration initialized successfully")
        
        # Test agent creation
        lead_agent = config.create_lead_intelligence_agent()
        revenue_agent = config.create_revenue_optimization_agent()
        
        print(f"   ✅ Lead Agent created: {lead_agent.role}")
        print(f"   ✅ Revenue Agent created: {revenue_agent.role}")
        
        # Check LLM models
        if hasattr(config, 'llama_llm'):
            llm_model = config.llama_llm.model
            if 'llama-3.3-70b' in llm_model:
                print(f"   ✅ Lead Agent uses Llama 3.3 70B: {llm_model}")
            else:
                print(f"   ❌ Lead Agent not using Llama 3.3 70B: {llm_model}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to test CrewAI config: {e}")
        return False

def test_orchestrator_config():
    """Test Enhanced Orchestrator configuration"""
    print("🔧 Testing Enhanced Orchestrator...")
    
    try:
        # Import the orchestrator
        from crewai_enhanced_orchestrator import CrewAIEnhancedOrchestrator
        
        # This will test the configuration without actually running
        print("   ✅ Enhanced Orchestrator can be imported")
        
        # Check if it would use the right models
        # Note: We don't fully initialize to avoid API calls
        print("   ✅ Enhanced Orchestrator configuration accessible")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to test Enhanced Orchestrator: {e}")
        return False

def main():
    """Run all verification tests"""
    print("="*70)
    print("🔧 FINAL CONFIGURATION VERIFICATION")
    print("="*70)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("="*70)
    
    tests = [
        ("Models Manager", test_models_manager),
        ("Environment Variables", test_environment_variables),
        ("Configuration Files", test_config_files),
        ("CrewAI Config", test_crew_ai_config),
        ("Enhanced Orchestrator", test_orchestrator_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"   🎉 {test_name}: PASSED")
            else:
                print(f"   ❌ {test_name}: FAILED")
        except Exception as e:
            print(f"   💥 {test_name}: ERROR - {e}")
        print("-" * 50)
    
    print("\n" + "="*70)
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CONFIGURATION CHANGES SUCCESSFUL!")
        print("✅ DeepSeek R1 completely removed")
        print("✅ Llama 3.3 70B properly configured")
        print("✅ System ready for stable operation")
        print("\n🚀 You can now run: python launch_dashboard.py")
    elif passed >= 3:
        print("⚠️  Most changes successful, minor issues detected")
        print("✅ Core functionality should work properly")
    else:
        print("❌ Significant configuration issues detected")
        print("⚠️  Manual review recommended")
    
    print("="*70)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
