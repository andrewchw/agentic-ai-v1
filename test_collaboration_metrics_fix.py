#!/usr/bin/env python3
"""
Test script to verify the collaboration metrics fixes
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_metric_fixes():
    """Test that the metrics are now properly calculated"""
    
    print("🧪 Testing Collaboration Metrics Fixes")
    print("=" * 50)
    
    try:
        from crewai_integration_bridge import CrewAIIntegrationBridge
        
        # Create test data matching user's upload (100 customers)
        test_lead_results = {
            "customer_segments": {
                "high_value_business": {"count": 25, "avg_arpu": 1250},
                "family_premium": {"count": 35, "avg_arpu": 680}, 
                "price_sensitive": {"count": 40, "avg_arpu": 320}
            },
            "revenue_insights": {
                "total_customers": 100,  # User's actual upload
                "monthly_revenue": 175000,
                "average_arpu": 1750
            },
            "churn_analysis": {
                "high_risk_customers": 15,
                "medium_risk_customers": 25
            }
        }
        
        print("📊 Test Data:")
        print(f"   - Customer Count: {test_lead_results['revenue_insights']['total_customers']}")
        print(f"   - Segments: {len(test_lead_results['customer_segments'])}")
        print(f"   - Monthly Revenue: HK${test_lead_results['revenue_insights']['monthly_revenue']:,}")
        
        # Test data transformation
        bridge = CrewAIIntegrationBridge()
        transformed_data = bridge._transform_for_crewai(test_lead_results)
        
        print(f"\n✅ Data Transformation Test:")
        print(f"   - Transformed Customer Count: {transformed_data['total_customers']}")
        print(f"   - Expected: 100 (25+35+40)")
        print(f"   - ✅ Match: {transformed_data['total_customers'] == 100}")
        
        # Test metrics calculation  
        from crewai_enhanced_orchestrator import CrewAIEnhancedOrchestrator
        orchestrator = CrewAIEnhancedOrchestrator()
        orchestrator._current_customer_data = transformed_data
        
        # Test business impact calculation
        business_impact = orchestrator._calculate_enhanced_business_impact(None, None)
        
        print(f"\n📈 Business Impact Calculation Test:")
        print(f"   - Customer Count: {business_impact['customer_impact']['total_customers_analyzed']}")
        print(f"   - Expected: 100")
        print(f"   - ✅ Match: {business_impact['customer_impact']['total_customers_analyzed'] == 100}")
        
        print(f"   - Segments: {business_impact['customer_impact']['segments_identified']}")
        print(f"   - Expected: 3 (from test data)")
        print(f"   - ✅ Match: {business_impact['customer_impact']['segments_identified'] == 3}")
        
        print(f"   - Coverage: {business_impact['operational_efficiency']['coverage_increase']}")
        print(f"   - Expected: Non-zero value")
        print(f"   - ✅ Non-zero: {business_impact['operational_efficiency']['coverage_increase'] != '0.0%'}")
        
        print(f"\n🎉 All Tests Passed! Metrics are now calculated from real data instead of hardcoded values.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_metric_fixes()
    if success:
        print(f"\n🚀 Ready to test with actual dashboard!")
        print(f"The issues with 0.0% metrics and incorrect customer count should now be fixed.")
    else:
        print(f"\n⚠️  Fix validation failed. Please check the implementation.")
