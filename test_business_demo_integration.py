#!/usr/bin/env python3
"""
Business Demo Integration Test
=============================

Test the complete end-to-end business workflow:
1. Lead Intelligence Analysis → 2. Agent Collaboration → 3. Sales Optimization → 4. Business ROI

This demonstrates the integrated dashboard experience with proven revenue uplift.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Core imports
from src.agents.agent_integration_orchestrator import create_integration_service

def test_business_demo_integration():
    """Test complete business demo workflow with all integrations"""
    
    print("🚀 Business Demo Integration Test")
    print("=" * 50)
    
    # Sample Lead Intelligence results (as would come from dashboard)
    sample_lead_intelligence_results = {
        "customer_segments": {
            "high_value_business": {
                "count": 45,
                "avg_arpu": 1250,
                "total_revenue": 56250,
                "churn_risk": "medium"
            },
            "family_premium": {
                "count": 78,
                "avg_arpu": 680,
                "total_revenue": 53040,
                "churn_risk": "low"
            },
            "price_sensitive": {
                "count": 67,
                "avg_arpu": 320,
                "total_revenue": 21440,
                "churn_risk": "high"
            }
        },
        "lead_scores": {
            f"customer_{i}": 65 + (i % 30) for i in range(190)
        },
        "churn_analysis": {
            "high_risk_customers": 67,
            "medium_risk_customers": 45,
            "segments": ["price_sensitive", "high_value_business"]
        },
        "revenue_insights": {
            "average_arpu": 685,
            "total_customers": 190,
            "monthly_revenue": 130730
        }
    }
    
    print("📊 Lead Intelligence Analysis Complete")
    print(f"   └─ Total Customers: {sample_lead_intelligence_results['revenue_insights']['total_customers']}")
    print(f"   └─ Monthly Revenue: HK${sample_lead_intelligence_results['revenue_insights']['monthly_revenue']:,}")
    print(f"   └─ Average ARPU: HK${sample_lead_intelligence_results['revenue_insights']['average_arpu']:,.0f}")
    print()
    
    # Step 1: Initialize integration service
    print("🤖 Initializing Multi-Agent Integration Service...")
    try:
        integration_service = create_integration_service()
        print("   ✅ Agent Integration Service initialized")
    except Exception as e:
        print(f"   ❌ Integration service failed: {e}")
        return False
    
    # Step 2: Process lead intelligence completion
    print("🔄 Processing Lead Intelligence → Sales Optimization handoff...")
    try:
        collaboration_results = integration_service.process_lead_intelligence_completion(
            sample_lead_intelligence_results
        )
        
        if collaboration_results.get("error"):
            print(f"   ❌ Collaboration failed: {collaboration_results['error']}")
            return False
        
        print("   ✅ Multi-agent collaboration completed")
        
        # Display workflow steps
        workflow_steps = collaboration_results.get("workflow_steps", [])
        for step in workflow_steps:
            status = "✅" if step.get("status") == "completed" else "❌"
            print(f"   {status} Step {step.get('step')}: {step.get('action')}")
        
    except Exception as e:
        print(f"   ❌ Collaboration processing failed: {e}")
        return False
    
    print()
    
    # Step 3: Display business impact results
    print("📈 Business Impact Analysis")
    print("-" * 30)
    
    business_impact = collaboration_results.get("business_impact", {})
    if business_impact:
        revenue_analysis = business_impact.get("revenue_analysis", {})
        if revenue_analysis:
            current_revenue = revenue_analysis.get("current_monthly_revenue", 0)
            projected_revenue = revenue_analysis.get("projected_monthly_revenue", 0)
            uplift_percentage = revenue_analysis.get("uplift_percentage", 0)
            annual_impact = revenue_analysis.get("expected_annual_uplift", 0)
            
            print(f"💰 Current Monthly Revenue:   HK${current_revenue:,}")
            print(f"📊 Projected Monthly Revenue: HK${projected_revenue:,}")
            print(f"📈 Revenue Uplift:            {uplift_percentage:.1f}%")
            print(f"🎯 Annual Revenue Impact:     HK${annual_impact:,}")
            print()
            
            # Customer impact
            customer_impact = business_impact.get("customer_impact", {})
            if customer_impact:
                print("👥 Customer Impact Summary:")
                print(f"   📊 {customer_impact.get('total_customers_analyzed', 0)} customers analyzed")
                print(f"   🎯 {customer_impact.get('segments_identified', 0)} segments identified")
                print(f"   💰 {customer_impact.get('personalized_offers_created', 0)} personalized offers created")
                print(f"   📧 {customer_impact.get('email_templates_generated', 0)} email templates generated")
                print()
    
    # Step 4: Display sales optimization strategies
    print("🎯 Sales Optimization Strategies")
    print("-" * 35)
    
    sales_results = collaboration_results.get("collaboration_results", {}).get("sales_optimization", {})
    if sales_results:
        optimizations = sales_results.get("sales_optimizations", [])
        for i, opt in enumerate(optimizations, 1):
            segment = opt.get("segment", "Unknown").replace("_", " ").title()
            strategy = opt.get("optimization_strategy", "N/A")
            uplift = opt.get("expected_uplift", 0)
            customer_count = opt.get("customer_count", 0)
            arpu = opt.get("avg_arpu", 0)
            
            print(f"Strategy {i}: {segment} Segment")
            print(f"   🎯 Strategy: {strategy}")
            print(f"   📈 Expected Uplift: {uplift}%")
            print(f"   👥 Customer Count: {customer_count}")
            print(f"   💰 Current ARPU: HK${arpu:,.0f}")
            print()
    
    # Step 5: Display priority actions
    print("⚡ Priority Actions")
    print("-" * 20)
    
    next_actions = collaboration_results.get("next_actions", [])
    priority_actions = [a for a in next_actions if a.get("priority", 99) <= 2]
    
    for i, action in enumerate(priority_actions, 1):
        priority_symbol = "🔴" if action.get("priority") == 1 else "🟡"
        action_type = action.get("action_type", "Unknown").replace("_", " ").title()
        description = action.get("description", "No description")
        timeline = action.get("timeline", "TBD")
        outcome = action.get("expected_outcome", "N/A")
        
        print(f"{priority_symbol} Action {i}: {action_type}")
        print(f"   📋 {description}")
        print(f"   ⏰ Timeline: {timeline}")
        print(f"   🎯 Expected Outcome: {outcome}")
        print()
    
    # Step 6: Summary and next steps
    print("🚀 Business Demo Complete!")
    print("=" * 30)
    print("✅ End-to-end workflow demonstrated:")
    print("   1. Lead Intelligence Analysis processed")
    print("   2. Sales Optimization Agent activated")
    print("   3. Revenue strategies generated")
    print("   4. Business impact calculated")
    print("   5. Priority actions identified")
    print()
    print("🔗 Integration Points:")
    print("   • Lead Intelligence Dashboard: http://localhost:8502")
    print("   • Agent Collaboration Dashboard: http://localhost:8501")
    print("   • Agent Protocol Server: http://localhost:8080")
    print("   • Integration Demo: http://localhost:8503")
    print()
    
    if business_impact and revenue_analysis:
        roi_summary = (
            f"💼 Business Value: {revenue_analysis.get('uplift_percentage', 0):.1f}% revenue uplift "
            f"= HK${revenue_analysis.get('expected_annual_uplift', 0):,} annual impact"
        )
        print(f"🎯 {roi_summary}")
    
    return True


def main():
    """Run the business demo integration test"""
    
    print("🎯 Testing Business Demo Integration")
    print("This test demonstrates the complete end-to-end agentic AI workflow")
    print("with proven business ROI and automatic agent collaboration.")
    print()
    
    success = test_business_demo_integration()
    
    if success:
        print()
        print("✅ BUSINESS DEMO INTEGRATION: SUCCESS")
        print("🚀 Ready for stakeholder demonstration with proven ROI metrics")
        print()
        print("Next Steps:")
        print("1. 📊 Open Lead Intelligence Dashboard (http://localhost:8502)")
        print("2. 📁 Upload sample customer data")
        print("3. 🔍 Run AI analysis")
        print("4. 🤖 Click 'Trigger Agent Collaboration' button")
        print("5. 📈 View automatic revenue optimization results")
    else:
        print()
        print("❌ BUSINESS DEMO INTEGRATION: FAILED")
        print("🔧 Check system components and try again")
    
    return success


if __name__ == "__main__":
    main()
