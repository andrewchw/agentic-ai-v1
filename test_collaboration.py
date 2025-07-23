"""
Simple Multi-Agent Collaboration Test
=====================================

Test script to demonstrate real agent collaboration between Lead Intelligence
and Revenue Optimization agents.
"""

import json
from src.agents.lead_intelligence_agent import create_lead_intelligence_agent
from src.agents.revenue_optimization_agent import create_revenue_optimization_agent

def test_agent_collaboration():
    """Test real agent collaboration"""
    
    print("🤖 Testing Multi-Agent Collaboration")
    print("=" * 50)
    
    # Sample customer data
    customer_data = {
        "records": [
            {
                "customer_id": "HK_CUST_001",
                "monthly_spend": 185.50,
                "data_usage_gb": 65.2,
                "tenure_months": 28,
                "family_lines": 3,
                "active_services": 4,
                "support_tickets": 1,
                "payment_delays": 0,
                "competitor_usage": 0.1,
                "plan_type": "5G",
                "account_type": "individual",
                "family_plan": True,
                "business_features": False,
                "roaming_usage": 5.2,
                "international_calls": 12,
                "plan_data_limit": 80,
                "service_growth_rate": 0.15,
                "payment_method": "autopay"
            },
            {
                "customer_id": "HK_CUST_002", 
                "monthly_spend": 45.00,
                "data_usage_gb": 8.5,
                "tenure_months": 6,
                "family_lines": 1,
                "active_services": 1,
                "support_tickets": 4,
                "payment_delays": 2,
                "competitor_usage": 0.7,
                "plan_type": "4G",
                "account_type": "individual",
                "family_plan": False,
                "business_features": False,
                "roaming_usage": 0,
                "international_calls": 0,
                "plan_data_limit": 20,
                "service_growth_rate": -0.05,
                "payment_method": "manual"
            }
        ]
    }
    
    # Step 1: Lead Intelligence Agent Analysis
    print("\n🧠 Step 1: Lead Intelligence Agent Analysis")
    lead_agent = create_lead_intelligence_agent()
    print(f"✅ Agent Status: {lead_agent.get_agent_status()['status']}")
    
    analysis = lead_agent.analyze_customer_patterns(customer_data)
    print(f"📊 Analyzed {len(customer_data['records'])} customers")
    print(f"🎯 Found {analysis['lead_scores']['high_value_count']} high-value leads")
    print(f"⚠️  {analysis['churn_analysis']['urgent_interventions']} urgent interventions needed")
    
    # Step 2: Delegation to Revenue Agent
    print("\n🤝 Step 2: Agent Delegation")
    delegation_items = analysis.get("delegation_items", [])
    print(f"📋 Lead Agent identified {len(delegation_items)} delegation items:")
    
    for i, item in enumerate(delegation_items, 1):
        print(f"   {i}. {item['type']}: {item['description']}")
    
    # Step 3: Revenue Agent Response
    print("\n💰 Step 3: Revenue Optimization Agent Response")
    revenue_agent = create_revenue_optimization_agent()
    print(f"✅ Agent Status: {revenue_agent.get_agent_status()['status']}")
    
    # Process each delegation
    responses = []
    for item in delegation_items:
        response = revenue_agent.respond_to_delegation(item)
        responses.append(response)
        print(f"   ✅ {item['type']}: {response.get('status', 'unknown')}")
    
    # Step 4: Revenue Analysis
    print("\n📈 Step 4: Revenue Optimization Analysis")
    revenue_analysis = revenue_agent.optimize_revenue_opportunities(analysis)
    
    print(f"💰 Total Revenue Potential: ${revenue_analysis.total_revenue_potential:,.0f}")
    print(f"🔒 Retention Savings: ${revenue_analysis.retention_savings:,.0f}")
    print(f"📈 Upsell Revenue: ${revenue_analysis.upsell_revenue:,.0f}")
    print(f"🎯 Priority Actions: {len(revenue_analysis.recommended_actions)}")
    
    # Step 5: Collaboration Summary
    print("\n🎯 Step 5: Collaboration Summary")
    print("✅ Lead Intelligence Agent completed customer analysis")
    print("✅ Revenue Optimization Agent provided strategic responses")
    print("✅ Both agents collaborated successfully")
    
    # Show sample recommendations
    print(f"\n📋 Sample Recommendations:")
    for i, action in enumerate(revenue_analysis.recommended_actions[:3], 1):
        print(f"   {i}. {action}")
    
    print("\n🚀 Multi-Agent Collaboration Test Complete!")
    print("This demonstrates true agentic AI - specialized agents working together!")

if __name__ == "__main__":
    test_agent_collaboration()
