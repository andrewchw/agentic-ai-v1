#!/usr/bin/env python3
"""
Enhanced CrewAI + OpenRouter Test
=================================

Test the improved CrewAI setup with OpenRouter using best practices from the setup guide:
- Environment variable configuration
- Memory disabled for embeddings compatibility
- Proper model naming
- Enhanced error handling

Author: Agentic AI Revenue Assistant
Date: 2025-07-24
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_crewai_openrouter_fixed():
    """Test CrewAI with OpenRouter using improved configuration"""
    
    print("🔧 Testing Improved CrewAI + OpenRouter Configuration")
    print("=" * 60)
    
    # Verify environment setup
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return False
    
    print(f"✅ OpenRouter API Key: {openrouter_key[:15]}...{openrouter_key[-4:]}")
    
    try:
        # Import after environment check
        from crewai_enhanced_orchestrator import CrewAIEnhancedOrchestrator
        
        print("📦 CrewAI Enhanced Orchestrator imported successfully")
        
        # Initialize orchestrator with improved configuration
        print("🚀 Initializing CrewAI Enhanced Orchestrator with OpenRouter...")
        orchestrator = CrewAIEnhancedOrchestrator()
        print("✅ CrewAI Enhanced Orchestrator initialized successfully!")
        
        # Check environment variables are set correctly
        print("\n🔍 Environment Variable Check:")
        print(f"   OPENAI_API_KEY (should be OpenRouter key): {os.getenv('OPENAI_API_KEY', 'NOT SET')[:15]}...")
        print(f"   OPENAI_API_BASE (should be OpenRouter URL): {os.getenv('OPENAI_API_BASE', 'NOT SET')}")
        print(f"   OPENROUTER_API_KEY: {os.getenv('OPENROUTER_API_KEY', 'NOT SET')[:15]}...")
        
        # Test LLM configuration
        print("\n🧠 Testing LLM Configuration:")
        print(f"   DeepSeek LLM Model: {orchestrator.deepseek_llm.model}")
        print(f"   Llama3 LLM Model: {orchestrator.llama3_llm.model}")
        print(f"   Claude LLM Model: {orchestrator.claude_llm.model}")
        print(f"   GPT LLM Model: {orchestrator.gpt_llm.model}")
        
        # Test agent creation
        print("\n🤖 Testing Agent Configuration:")
        print(f"   Lead Intelligence Agent: {orchestrator.lead_intelligence_agent.role}")
        print(f"   Market Intelligence Agent: {orchestrator.market_intelligence_agent.role}")
        print(f"   Sales Optimization Agent: {orchestrator.sales_optimization_agent.role}")
        print(f"   Retention Specialist Agent: {orchestrator.retention_specialist_agent.role}")
        print(f"   Campaign Manager Agent: {orchestrator.campaign_manager_agent.role}")
        
        # Create sample data for processing test
        sample_data = {
            "total_customers": 50,  # Smaller sample for testing
            "fields": ["customer_id", "segment", "arpu", "tenure", "usage_pattern", "churn_risk"],
            "timestamp": datetime.now().isoformat(),
            "market_context": "Hong Kong telecom competitive environment - TEST"
        }
        
        print(f"\n📊 Testing Enhanced Multi-Agent Processing...")
        print(f"   Sample Data: {sample_data['total_customers']} customers")
        
        # Process through enhanced system with timeout
        try:
            import asyncio
            
            # Create a timeout wrapper
            async def run_with_timeout():
                return await orchestrator.process_enhanced_customer_analysis(sample_data)
            
            # Run with 60 second timeout
            results = await asyncio.wait_for(run_with_timeout(), timeout=60.0)
            
            if results.get("success"):
                print("✅ Enhanced multi-agent analysis completed successfully!")
                
                # Display key results
                business_impact = results.get("enhanced_business_impact", {})
                revenue_analysis = business_impact.get("revenue_analysis", {})
                
                print(f"\n📈 Results Summary:")
                print(f"   ✅ Success: {results.get('success')}")
                print(f"   ⏱️  Processing Time: {results.get('processing_time', 0):.2f}s")
                print(f"   💰 Revenue Uplift: {revenue_analysis.get('uplift_percentage', 0)}%")
                print(f"   🎯 Annual Impact: HK${revenue_analysis.get('expected_annual_uplift', 0):,}")
                
                # Display collaboration metrics
                collab_metrics = results.get("collaboration_metrics", {})
                print(f"\n🤝 Collaboration Metrics:")
                print(f"   🤖 Agents: {collab_metrics.get('agents_participated', 0)}")
                print(f"   ✅ Tasks: {collab_metrics.get('tasks_completed', 0)}")
                print(f"   🎯 Consensus: {collab_metrics.get('consensus_achieved', False)}")
                print(f"   📊 Confidence: {collab_metrics.get('confidence_level', 0):.1%}")
                
                return True
            else:
                print(f"❌ Enhanced analysis failed: {results.get('error', 'Unknown error')}")
                print(f"   Fallback used: {results.get('fallback_used', False)}")
                return False
                
        except asyncio.TimeoutError:
            print("⏰ Analysis timed out after 60 seconds - this may indicate LLM connectivity issues")
            return False
        except Exception as e:
            print(f"❌ Analysis execution failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        logger.exception("Full error details:")
        return False


def test_simple_llm_call():
    """Test a simple LLM call to verify OpenRouter connectivity"""
    
    print("\n🔬 Testing Simple LLM Call to OpenRouter...")
    
    try:
        from crewai import LLM
        
        # Set environment variables
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        os.environ["OPENAI_API_KEY"] = openrouter_key
        os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
        
        # Create simple LLM using FREE Qwen3 Coder model
        llm = LLM(
            model="openrouter/qwen/qwen3-coder:free",
            temperature=0.3,
            max_tokens=100
        )
        
        # Simple test call
        test_prompt = "What is 2+2? Respond with just the number."
        response = llm.call(test_prompt)
        
        print(f"✅ Simple LLM call successful!")
        print(f"   Prompt: {test_prompt}")
        print(f"   Response: {str(response)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple LLM call failed: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🧪 CrewAI + OpenRouter Enhanced Test Suite")
        print("=" * 50)
        
        # Test 1: Simple LLM connectivity
        simple_test_passed = test_simple_llm_call()
        
        # Test 2: Full orchestrator test
        if simple_test_passed:
            full_test_passed = await test_crewai_openrouter_fixed()
            
            print(f"\n📋 Test Results Summary:")
            print(f"   Simple LLM Test: {'✅ PASSED' if simple_test_passed else '❌ FAILED'}")
            print(f"   Full Orchestrator Test: {'✅ PASSED' if full_test_passed else '❌ FAILED'}")
            
            if simple_test_passed and full_test_passed:
                print("\n🎉 All tests passed! CrewAI + OpenRouter is working correctly.")
            elif simple_test_passed:
                print("\n⚠️  Basic connectivity works, but orchestrator has issues.")
            else:
                print("\n❌ Basic connectivity failed - check OpenRouter API key and configuration.")
        else:
            print("\n❌ Skipping full test due to simple LLM test failure.")
    
    asyncio.run(main())
