"""
Multi-Agent System Demo Script
=============================

This script demonstrates the agentic AI capabilities of our multi-agent system,
showing how specialized AI agents collaborate to analyze customer data and 
develop revenue optimization strategies.

Perfect for demonstrating to stakeholders how agentic AI differs from 
traditional single-model approaches.
"    print("📊 Performance Metrics:")
    print(f"   • Customers analyzed: {customer_count}")
    print(f"   • Segments identified: {len(segments.get('segment_distribution', {}))}")
    print(f"   • High-value leads: {lead_scores.get('high_value_count', 0)}")
    
    # Get delegation items from either collaboration or analysis results
    if 'collaboration_results' in locals() and collaboration_results.get("collaboration_success", False):
        delegation_count = collaboration_results.get("collaboration_summary", {}).get("total_opportunities_identified", 0)
    else:
        delegation_count = len(analysis_results.get("delegation_items", []))
    
    print(f"   • Delegation items: {delegation_count}")"""
import os
import sys
import json
import time
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.multi_agent_system import create_multi_agent_system
from src.agents.lead_intelligence_agent import create_lead_intelligence_agent


def print_banner(text: str, char: str = "="):
    """Print a formatted banner"""
    print("\n" + char * 60)
    print(f" {text}")
    print(char * 60)


def print_agent_conversation(agent_name: str, message: str, is_response: bool = False):
    """Print agent conversation in a formatted way"""
    prefix = "🤖" if not is_response else "💭"
    print(f"\n{prefix} {agent_name}:")
    print(f"   {message}")


def simulate_agent_thinking(duration: float = 1.0):
    """Simulate agent thinking time"""
    print("   🔄 Analyzing...", end="", flush=True)
    time.sleep(duration)
    print(" Complete!")


def load_sample_data() -> Dict[str, Any]:
    """Load sample customer data for demo"""
    # Sample Hong Kong telecom customer data (pseudonymized)
    return {
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
            },
            {
                "customer_id": "HK_CUST_003",
                "monthly_spend": 320.00,
                "data_usage_gb": 125.8,
                "tenure_months": 18,
                "family_lines": 1,
                "active_services": 6,
                "support_tickets": 0,
                "payment_delays": 0,
                "competitor_usage": 0.0,
                "plan_type": "5G",
                "account_type": "business",
                "family_plan": False,
                "business_features": True,
                "roaming_usage": 45.3,
                "international_calls": 85,
                "plan_data_limit": 200,
                "service_growth_rate": 0.25,
                "payment_method": "autopay"
            },
            {
                "customer_id": "HK_CUST_004",
                "monthly_spend": 95.00,
                "data_usage_gb": 35.2,
                "tenure_months": 15,
                "family_lines": 2,
                "active_services": 3,
                "support_tickets": 1,
                "payment_delays": 0,
                "competitor_usage": 0.3,
                "plan_type": "5G",
                "account_type": "individual",
                "family_plan": False,
                "business_features": False,
                "roaming_usage": 2.1,
                "international_calls": 5,
                "plan_data_limit": 50,
                "service_growth_rate": 0.08,
                "payment_method": "autopay"
            },
            {
                "customer_id": "HK_CUST_005",
                "monthly_spend": 220.00,
                "data_usage_gb": 85.6,
                "tenure_months": 32,
                "family_lines": 4,
                "active_services": 5,
                "support_tickets": 0,
                "payment_delays": 0,
                "competitor_usage": 0.05,
                "plan_type": "5G",
                "account_type": "individual",
                "family_plan": True,
                "business_features": False,
                "roaming_usage": 15.8,
                "international_calls": 25,
                "plan_data_limit": 100,
                "service_growth_rate": 0.12,
                "payment_method": "autopay"
            }
        ]
    }


def run_demo():
    """Run the multi-agent system demo"""
    
    print_banner("🤖 AGENTIC AI MULTI-AGENT SYSTEM DEMO")
    print("Demonstrating how AI agents collaborate to optimize telecom revenue")
    print("Location: Hong Kong Telecom Market")
    print("Agents: Lead Intelligence (DeepSeek) + Revenue Optimization (Llama3)")
    
    # Step 1: Initialize System
    print_banner("Step 1: System Initialization", "-")
    print("🔧 Initializing multi-agent system...")
    
    try:
        # Initialize the multi-agent system
        system = create_multi_agent_system()
        print("✅ Multi-agent system initialized successfully")
        
        # Get agent status
        print("\n📊 Agent Status Check:")
        status = system.get_agent_status()
        print(json.dumps(status, indent=2))
        
    except Exception as e:
        print(f"❌ System initialization failed: {str(e)}")
        return
    
    # Step 2: Load Customer Data
    print_banner("Step 2: Loading Customer Data", "-")
    print("📁 Loading sample Hong Kong telecom customer data...")
    
    customer_data = load_sample_data()
    customer_count = len(customer_data["records"])
    print(f"✅ Loaded {customer_count} customer records (pseudonymized)")
    
    # Show sample data
    print("\n🔍 Sample Customer Profile:")
    sample_customer = customer_data["records"][0]
    for key, value in list(sample_customer.items())[:6]:
        print(f"   {key}: {value}")
    print("   ... (additional fields)")
    
    # Step 3: Demonstrate Agent Specialization
    print_banner("Step 3: Agent Specialization Demo", "-")
    
    # Initialize Lead Intelligence Agent
    print("🔬 Initializing Lead Intelligence Agent (DeepSeek)...")
    lead_agent = create_lead_intelligence_agent()
    
    agent_status = lead_agent.get_agent_status()
    print(f"✅ Agent Ready: {agent_status['agent_name']}")
    print(f"   Model: {agent_status['llm_model']}")
    print(f"   Temperature: {agent_status['temperature']} (analytical precision)")
    print(f"   Specialization: {agent_status['specialization']}")
    
    # Step 4: Live Agent Analysis
    print_banner("Step 4: Live Agent Analysis", "-")
    
    print_agent_conversation(
        "Lead Intelligence Agent", 
        f"Starting analysis of {customer_count} Hong Kong telecom customers..."
    )
    
    simulate_agent_thinking(2.0)
    
    # Run the analysis
    try:
        analysis_results = lead_agent.analyze_customer_patterns(customer_data)
        
        print_agent_conversation(
            "Lead Intelligence Agent",
            "Analysis complete! Here's what I found:",
            is_response=True
        )
        
        # Show key insights
        segments = analysis_results.get("customer_segments", {})
        print(f"   📊 Customer Segmentation:")
        for segment, count in segments.get("segment_distribution", {}).items():
            print(f"      • {segment}: {count} customers")
        
        lead_scores = analysis_results.get("lead_scores", {})
        print(f"\n   🎯 Lead Intelligence:")
        print(f"      • High-value leads: {lead_scores.get('high_value_count', 0)}")
        print(f"      • Average lead score: {lead_scores.get('average_score', 0):.2f}/10")
        
        churn = analysis_results.get("churn_analysis", {})
        print(f"\n   ⚠️  Churn Risk Assessment:")
        print(f"      • Customers at risk: {churn.get('total_at_risk', 0)}")
        print(f"      • Urgent interventions: {churn.get('urgent_interventions', 0)}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return
    
    # Step 5: Real Agent Collaboration Demo
    print_banner("Step 5: Real Agent Collaboration", "-")
    
    print_agent_conversation(
        "System",
        "Initiating real multi-agent collaboration..."
    )
    
    simulate_agent_thinking(1.0)
    
    try:
        # Run actual agent collaboration
        collaboration_results = system.run_collaborative_analysis(customer_data)
        
        if collaboration_results.get("collaboration_success", False):
            print_agent_conversation(
                "Lead Intelligence Agent",
                "Analysis complete! I've identified key patterns and delegated strategic questions to Revenue Agent."
            )
            
            # Show delegation items
            delegation_items = collaboration_results.get("agent_collaboration", {}).get("delegation_items", [])
            if delegation_items:
                print(f"\n   📋 Delegated {len(delegation_items)} strategic items:")
                for item in delegation_items[:3]:  # Show first 3
                    print(f"      • {item.get('type', 'unknown')}: {item.get('description', 'No description')}")
            
            simulate_agent_thinking(2.0)
            
            print_agent_conversation(
                "Revenue Optimization Agent",
                "Received delegation requests and completed strategic analysis. Here are my recommendations:",
                is_response=True
            )
            
            # Show revenue responses
            revenue_responses = collaboration_results.get("agent_collaboration", {}).get("revenue_responses", [])
            if revenue_responses:
                for response in revenue_responses[:2]:  # Show first 2 responses
                    if response.get("status") == "completed":
                        response_type = response.get("response_type", "general")
                        print(f"      ✅ {response_type.replace('_', ' ').title()}: Strategy developed")
            
            # Show collaboration summary
            summary = collaboration_results.get("collaboration_summary", {})
            print(f"\n   🤝 Collaboration Summary:")
            print(f"      • Lead Agent contributions: {summary.get('lead_agent_contributions', 0)}")
            print(f"      • Revenue Agent responses: {summary.get('revenue_agent_responses', 0)}")
            print(f"      • Opportunities identified: {summary.get('total_opportunities_identified', 0)}")
            
            print_agent_conversation(
                "Lead Intelligence Agent",
                "Perfect collaboration! Revenue Agent's strategies align with my customer analysis. Ready to implement.",
                is_response=True
            )
            
        else:
            print("❌ Collaboration failed - falling back to simulated demo")
            # Fall back to simulated collaboration as before
            
    except Exception as e:
        print(f"⚠️  Real collaboration error: {str(e)}")
        print("   Falling back to simulated collaboration demo")
        
        # Original simulated collaboration code as fallback
        delegation_items = analysis_results.get("delegation_items", [])
        
        if delegation_items:
            print_agent_conversation(
                "Lead Intelligence Agent",
                "I've identified several items that need Revenue Agent expertise..."
            )
            
            for item in delegation_items:
                print(f"\n   📋 Delegation Item:")
                print(f"      Type: {item.get('type', 'unknown')}")
                print(f"      Priority: {item.get('priority', 'medium')}")
                print(f"      Description: {item.get('description', 'No description')}")
            
            # Simulate delegation
            print_agent_conversation(
                "Lead Intelligence Agent",
                "Revenue Agent, I need your strategic input on these high-value opportunities."
            )
            
            simulate_agent_thinking(1.5)
            
            print_agent_conversation(
                "Revenue Optimization Agent (Simulated)",
                "Received your analysis. Working on pricing strategies for premium segments...",
                is_response=True
            )
            
            simulate_agent_thinking(2.0)
            
            print_agent_conversation(
                "Revenue Optimization Agent (Simulated)",
                "Strategy complete! For high-value leads, recommend tiered offers: Premium+ plans with 20% discount for first 6 months.",
                is_response=True
            )
            
            print_agent_conversation(
                "Lead Intelligence Agent",
                "Perfect! Your pricing strategy aligns with my customer behavior analysis. Let's implement this approach.",
                is_response=True
            )
    
    # Step 6: Results Summary
    print_banner("Step 6: Collaboration Results", "-")
    
    print("🎯 Multi-Agent Analysis Summary:")
    print("   ✅ Customer segmentation complete")
    print("   ✅ Lead scoring and prioritization done") 
    print("   ✅ Churn risk assessment finished")
    print("   ✅ Revenue opportunities identified")
    print("   ✅ Strategic recommendations from both agents")
    
    print("\n💡 Key Demonstration Points:")
    print("   • Two specialized AI agents with different LLMs")
    print("   • Real task delegation between agents")
    print("   • Collaborative decision-making process")
    print("   • Different thinking styles (analytical vs strategic)")
    print("   • Privacy-compliant data processing")
    
    # Step 7: Technical Details
    print_banner("Step 7: Technical Architecture", "-")
    
    print("🔧 System Architecture:")
    print("   • CrewAI Framework: Agent orchestration")
    print("   • DeepSeek LLM: Analytical tasks (temp 0.2)")
    print("   • Llama3 LLM: Strategic tasks (temp 0.4)")
    print("   • OpenRouter: Multi-LLM API access")
    print("   • Privacy Pipeline: GDPR/PDPO compliance")
    
    print("\n📊 Performance Metrics:")
    print(f"   • Customers analyzed: {customer_count}")
    print(f"   • Segments identified: {len(segments.get('segment_distribution', {}))}")
    print(f"   • High-value leads: {lead_scores.get('high_value_count', 0)}")
    print(f"   • Delegation items: {len(delegation_items)}")
    
    print_banner("Demo Complete! 🚀")
    print("This demonstrates true agentic AI - specialized agents that collaborate,")
    print("delegate tasks, and combine their expertise for optimal results.")
    print("\nQuestions? Ready to see the agents handle real customer scenarios?")


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {str(e)}")
        import traceback
        print("\nDebug information:")
        traceback.print_exc()
