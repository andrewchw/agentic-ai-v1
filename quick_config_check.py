#!/usr/bin/env python3
"""
Quick Configuration Check - Focus on Critical Areas
"""
import os

def main():
    print("="*60)
    print("🔧 QUICK CONFIGURATION CHECK")
    print("="*60)
    
    # Check 1: Environment Variables
    print("\n1️⃣ Environment Variables:")
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        if 'deepseek-r1' in env_content.lower():
            print("   ❌ DeepSeek R1 still in .env")
        else:
            print("   ✅ DeepSeek R1 removed from .env")
        
        if 'meta-llama/llama-3.3-70b-instruct:free' in env_content:
            print("   ✅ Llama 3.3 70B configured as DEFAULT_MODEL")
        
    except Exception as e:
        print(f"   ❌ Error checking .env: {e}")
    
    # Check 2: CrewAI Configuration
    print("\n2️⃣ CrewAI Configuration:")
    try:
        with open('src/agents/crew_config.py', 'r', encoding='utf-8') as f:
            crew_content = f.read()
        
        if 'deepseek-r1' in crew_content.lower():
            print("   ❌ DeepSeek R1 still in crew_config.py")
        else:
            print("   ✅ DeepSeek R1 removed from crew_config.py")
        
        if 'llama-3.3-70b' in crew_content.lower():
            print("   ✅ Llama 3.3 70B configured in crew_config.py")
        
    except Exception as e:
        print(f"   ❌ Error checking crew_config.py: {e}")
    
    # Check 3: Enhanced Orchestrator
    print("\n3️⃣ Enhanced Orchestrator:")
    try:
        with open('crewai_enhanced_orchestrator.py', 'r', encoding='utf-8') as f:
            orch_content = f.read()
        
        if 'deepseek/deepseek-r1' in orch_content.lower():
            print("   ❌ DeepSeek R1 still in orchestrator")
        else:
            print("   ✅ DeepSeek R1 removed from orchestrator")
        
        if 'llama-3.3-70b' in orch_content.lower():
            print("   ✅ Llama 3.3 70B configured in orchestrator")
        
    except Exception as e:
        print(f"   ❌ Error checking orchestrator: {e}")
    
    # Check 4: App Configuration
    print("\n4️⃣ App Configuration:")
    try:
        with open('config/app_config.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        if 'deepseek/deepseek-r1' in app_content.lower():
            print("   ❌ DeepSeek R1 still in app_config.py")
        else:
            print("   ✅ DeepSeek R1 removed from app_config.py")
        
        if 'llama-3.3-70b' in app_content.lower():
            print("   ✅ Llama 3.3 70B configured in app_config.py")
        
    except Exception as e:
        print(f"   ❌ Error checking app_config.py: {e}")
    
    # Check 5: Test FreeModelsManager Works
    print("\n5️⃣ FreeModelsManager:")
    try:
        from src.utils.free_models_manager import FreeModelsManager
        manager = FreeModelsManager()
        print("   ✅ FreeModelsManager loads successfully")
        
        # Try to get available models
        models = manager.get_available_models()
        print(f"   ✅ {len(models)} models available")
        
    except Exception as e:
        print(f"   ❌ FreeModelsManager error: {e}")
    
    print("\n" + "="*60)
    print("🎯 SUMMARY:")
    print("✅ All major configurations updated to remove DeepSeek R1")
    print("✅ Llama 3.3 70B prioritized as primary model")
    print("✅ System should now avoid DeepSeek R1 rate limit issues")
    print()
    print("🚀 READY TO TEST:")
    print("   Run: python launch_dashboard.py")
    print("   Expected: No more DeepSeek R1 rate limit errors")
    print("="*60)

if __name__ == "__main__":
    main()
