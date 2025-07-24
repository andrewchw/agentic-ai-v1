#!/usr/bin/env python3
"""
Quick test to diagnose CrewAI integration issues
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Environment Variable Diagnosis:")
print(f"OPENROUTER_API_KEY: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}")
print(f"OPENROUTER_API_KEY length: {len(os.getenv('OPENROUTER_API_KEY', ''))}")

print("\n🧪 Testing CrewAI Import Chain:")

try:
    print("Step 1: Testing basic import...")
    import sys
    sys.path.append('.')
    print("✅ Path setup OK")
    
    print("Step 2: Testing CrewAI orchestrator import...")
    from crewai_enhanced_orchestrator import create_crewai_enhanced_orchestrator
    print("✅ CrewAI orchestrator import OK")
    
    print("Step 3: Testing bridge import...")
    from crewai_integration_bridge import process_agent_collaboration_with_crewai
    print("✅ Bridge import OK")
    
    print("Step 4: Testing orchestrator creation...")
    orchestrator = create_crewai_enhanced_orchestrator()
    print("✅ Orchestrator creation OK")
    
    print("\n🎉 All tests passed! CrewAI integration should work.")
    
except Exception as e:
    print(f"\n❌ Error at step: {e}")
    import traceback
    traceback.print_exc()
