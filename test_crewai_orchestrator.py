#!/usr/bin/env python3
"""
CrewAI Enhanced Orchestrator Test
================================

Direct test of the CrewAI enhanced orchestrator to verify it works with OpenRouter API.
"""

import os
import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_crewai_orchestrator():
    """Test the CrewAI orchestrator directly"""
    
    print("🧪 Testing CrewAI Enhanced Orchestrator")
    print("=" * 50)
    
    # Check OpenRouter API key
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        print(f"✅ OPENROUTER_API_KEY: Available (length: {len(openrouter_key)})")
    else:
        print("❌ OPENROUTER_API_KEY: Not found")
        return False
    
    # Test CrewAI orchestrator initialization
    try:
        print("\n🔄 Initializing CrewAI Enhanced Orchestrator...")
        
        from crewai_enhanced_orchestrator import create_crewai_enhanced_orchestrator
        
        orchestrator = create_crewai_enhanced_orchestrator()
        print("✅ CrewAI Enhanced Orchestrator initialized successfully!")
        
        # Test sample data processing
        print("\n📊 Testing with sample customer data...")
        
        sample_customer_data = {
            "total_customers": 190,
            "fields": ["customer_id", "segment", "arpu", "churn_risk", "behavior_pattern"],
            "timestamp": datetime.now().isoformat(),
            "market_context": "Hong Kong telecom competitive environment",
            "segment_analysis": {
                "high_value_business": {"count": 45, "avg_arpu": 1250},
                "family_premium": {"count": 78, "avg_arpu": 680},
                "price_sensitive": {"count": 67, "avg_arpu": 320}
            },
            "revenue_baseline": 130000,
            "churn_indicators": {
                "high_risk_customers": 67,
                "medium_risk_customers": 45
            }
        }
        
        print("🚀 Processing enhanced customer analysis...")
        results = await orchestrator.process_enhanced_customer_analysis(sample_customer_data)
        
        if results.get("success"):
            print("✅ Enhanced customer analysis completed successfully!")
            
            # Display key results
            business_impact = results.get("enhanced_business_impact", {})
            revenue_analysis = business_impact.get("revenue_analysis", {})
            
            if revenue_analysis:
                current_revenue = revenue_analysis.get("current_monthly_revenue", 0)
                projected_revenue = revenue_analysis.get("projected_monthly_revenue", 0)
                uplift_percentage = revenue_analysis.get("uplift_percentage", 0)
                
                print(f"   💰 Current Revenue: HK${current_revenue:,}")
                print(f"   📈 Projected Revenue: HK${projected_revenue:,}")
                print(f"   🚀 Revenue Uplift: {uplift_percentage:.1f}%")
            
            # Show collaboration metrics
            collaboration_metrics = results.get("collaboration_metrics", {})
            if collaboration_metrics:
                consensus_score = collaboration_metrics.get("consensus_score", 0)
                avg_confidence = collaboration_metrics.get("average_confidence", 0)
                print(f"   🤝 Consensus Score: {consensus_score:.1%}")
                print(f"   🎯 Average Confidence: {avg_confidence:.1%}")
            
            # Show strategic recommendations
            strategic_recommendations = results.get("strategic_recommendations", [])
            print(f"   📋 Strategic Recommendations: {len(strategic_recommendations)}")
            
            return True
        else:
            print(f"❌ Enhanced customer analysis failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ CrewAI orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Set the OpenRouter API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Setting OpenRouter API key from .env...")
        try:
            import dotenv
            dotenv.load_dotenv()
        except ImportError:
            print("⚠️ python-dotenv not available")
    
    # Run the async test
    success = asyncio.run(test_crewai_orchestrator())
    
    if success:
        print(f"\n🎉 CrewAI Enhanced Orchestrator Test: SUCCESS")
        print(f"✅ Ready for dashboard integration")
    else:
        print(f"\n❌ CrewAI Enhanced Orchestrator Test: FAILED")
        print(f"⚠️ Will fallback to standard mode in dashboard")
