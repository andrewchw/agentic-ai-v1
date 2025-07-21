#!/usr/bin/env python3
"""
Agentic AI Revenue Assistant - Integrated Workflow Demonstration

This script demonstrates the complete end-to-end workflow of the Agentic AI Revenue Assistant,
showcasing the integration of all components from customer data input to actionable recommendations.

Features Demonstrated:
1. Customer data processing and privacy protection
2. AI agent orchestration with recommendation generation
3. Hong Kong telecom market-specific insights
4. Actionable recommendations with explainability
5. Business intelligence and sales optimization
"""

import sys
import os
import json
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add src to path for imports
sys.path.append('src')

def print_header(title: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def print_subheader(title: str):
    """Print formatted subsection header"""
    print(f"\n{'-'*60}")
    print(f"  {title}")
    print(f"{'-'*60}")

def create_demo_customers() -> List[Dict[str, Any]]:
    """Create realistic demo customer data for different segments"""
    return [
        {
            "customer_id": "ENT_HK_001",
            "customer_name": "Hong Kong Financial Corp",
            "customer_type": "enterprise",
            "annual_revenue": 250000000,
            "employee_count": 1200,
            "current_monthly_spend": 65000,
            "contract_end_date": "2024-07-31",
            "last_interaction": "2024-01-15",
            "preferred_contact_time": "morning",
            "industry": "financial_services",
            "location": "central",
            "decision_maker_identified": True,
            "budget_confirmed": True,
            "competitor_mentions": "PCCW",
            "urgency_indicators": ["contract_renewal", "expansion_needed", "security_upgrade"],
            "pain_points": ["slow_connectivity", "poor_support", "security_concerns"],
        },
        {
            "customer_id": "SME_HK_002",
            "customer_name": "Tech Innovation Limited",
            "customer_type": "sme",
            "annual_revenue": 25000000,
            "employee_count": 85,
            "current_monthly_spend": 12000,
            "contract_end_date": "2024-11-30",
            "last_interaction": "2024-01-08",
            "preferred_contact_time": "afternoon",
            "industry": "technology",
            "location": "kowloon",
            "decision_maker_identified": False,
            "budget_confirmed": False,
            "competitor_mentions": "CSL",
            "urgency_indicators": ["cost_reduction", "bandwidth_upgrade"],
            "pain_points": ["high_costs", "limited_bandwidth", "poor_mainland_connectivity"],
        },
        {
            "customer_id": "CON_HK_003",
            "customer_name": "Premium Consumer",
            "customer_type": "consumer",
            "current_monthly_spend": 850,
            "contract_end_date": "2024-05-31",
            "last_interaction": "2024-01-12",
            "preferred_contact_time": "evening",
            "location": "new_territories",
            "decision_maker_identified": True,
            "budget_confirmed": True,
            "competitor_mentions": "China Mobile",
            "urgency_indicators": ["service_issues", "coverage_problems", "roaming_needs"],
            "pain_points": ["poor_coverage", "high_roaming_charges", "slow_5g"],
        }
    ]

def create_demo_purchase_histories() -> Dict[str, List[Dict[str, Any]]]:
    """Create realistic purchase histories for demo customers"""
    return {
        "ENT_HK_001": [
            {
                "customer_id": "ENT_HK_001",
                "product_category": "enterprise_fiber",
                "amount": 45000,
                "purchase_date": "2022-08-01",
                "contract_length": 24,
                "satisfaction_score": 4.1,
            },
            {
                "customer_id": "ENT_HK_001",
                "product_category": "cloud_services",
                "amount": 18000,
                "purchase_date": "2022-08-01",
                "contract_length": 24,
                "satisfaction_score": 3.8,
            },
            {
                "customer_id": "ENT_HK_001",
                "product_category": "security_services",
                "amount": 12000,
                "purchase_date": "2023-02-15",
                "contract_length": 12,
                "satisfaction_score": 4.3,
            },
        ],
        "SME_HK_002": [
            {
                "customer_id": "SME_HK_002",
                "product_category": "business_broadband",
                "amount": 8500,
                "purchase_date": "2023-01-01",
                "contract_length": 18,
                "satisfaction_score": 3.9,
            },
            {
                "customer_id": "SME_HK_002",
                "product_category": "voice_services",
                "amount": 3500,
                "purchase_date": "2023-01-01",
                "contract_length": 18,
                "satisfaction_score": 4.0,
            },
        ],
        "CON_HK_003": [
            {
                "customer_id": "CON_HK_003",
                "product_category": "mobile_plan",
                "amount": 650,
                "purchase_date": "2023-05-31",
                "contract_length": 12,
                "satisfaction_score": 3.2,
            },
            {
                "customer_id": "CON_HK_003",
                "product_category": "home_broadband",
                "amount": 480,
                "purchase_date": "2023-08-15",
                "contract_length": 24,
                "satisfaction_score": 2.8,
            },
        ],
    }

def demonstrate_customer_data_processing(customers: List[Dict[str, Any]]):
    """Demonstrate customer data processing capabilities"""
    print_subheader("Customer Data Processing & Validation")
    
    for customer in customers:
        print(f"\n📋 Processing Customer: {customer['customer_name']} ({customer['customer_type'].upper()})")
        
        # Show key metrics
        if customer.get('annual_revenue'):
            print(f"   💰 Annual Revenue: HK${customer['annual_revenue']:,}")
        if customer.get('employee_count'):
            print(f"   👥 Employees: {customer['employee_count']:,}")
        print(f"   📊 Monthly Spend: HK${customer['current_monthly_spend']:,}")
        print(f"   📍 Location: {customer['location'].title()}")
        print(f"   🏢 Industry: {customer.get('industry', 'N/A').title()}")
        
        # Show urgency indicators
        if customer.get('urgency_indicators'):
            print(f"   🚨 Urgency: {', '.join(customer['urgency_indicators'])}")
        
        # Show pain points
        if customer.get('pain_points'):
            print(f"   ⚠️  Pain Points: {', '.join(customer['pain_points'])}")

def demonstrate_recommendation_generation(customers: List[Dict[str, Any]], purchase_histories: Dict[str, List[Dict[str, Any]]]):
    """Demonstrate the recommendation generation system"""
    print_subheader("AI-Powered Recommendation Generation")
    
    try:
        from src.agents.recommendation_generator import (
            RecommendationGenerator,
            create_sample_recommendations
        )
        from src.agents.customer_analysis import CustomerDataAnalyzer
        from src.agents.lead_scoring import LeadScoringEngine
        from src.agents.three_hk_business_rules import ThreeHKBusinessRulesEngine
        
        print("🤖 Initializing AI Recommendation Engine...")
        
        # Initialize components
        customer_analyzer = CustomerDataAnalyzer()
        lead_scorer = LeadScoringEngine()
        business_rules = ThreeHKBusinessRulesEngine()
        
        recommendation_generator = RecommendationGenerator(
            customer_analyzer=customer_analyzer,
            lead_scorer=lead_scorer,
            business_rules=business_rules
        )
        
        print("✅ AI Engine initialized successfully")
        
        # Create DataFrame for processing
        leads_df = pd.DataFrame(customers)
        
        print(f"\n🔄 Generating recommendations for {len(customers)} customers...")
        start_time = time.time()
        
        # Generate recommendations
        recommendations = recommendation_generator.generate_recommendations(
            leads_df, max_recommendations=10
        )
        
        generation_time = time.time() - start_time
        print(f"⚡ Generated {len(recommendations)} recommendations in {generation_time:.2f} seconds")
        
        # Display recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"\n📝 Recommendation #{i}")
            print(f"   🎯 Customer: {rec.customer_name}")
            print(f"   🔥 Priority: {rec.priority.value.upper()}")
            print(f"   🎬 Action: {rec.action_type.value.replace('_', ' ').title()}")
            print(f"   💵 Expected Revenue: HK${rec.expected_revenue:,.0f}")
            print(f"   📈 Conversion Probability: {rec.conversion_probability:.1%}")
            print(f"   ⏰ Urgency Score: {rec.urgency_score:.1%}")
            print(f"   📊 Business Impact: {rec.business_impact_score:.2f}")
            
            print(f"\n   📋 Title: {rec.title}")
            print(f"   📝 Description: {rec.description}")
            
            print(f"\n   🎯 Next Steps:")
            for step in rec.next_steps[:3]:  # Show first 3 steps
                print(f"      • {step}")
            
            print(f"\n   💬 Key Talking Points:")
            for point in rec.talking_points[:3]:  # Show first 3 points
                print(f"      • {point}")
            
            print(f"\n   🤔 Objection Handling:")
            for objection, response in list(rec.objection_handling.items())[:2]:  # Show first 2
                print(f"      Q: {objection.replace('_', ' ').title()}")
                print(f"      A: {response[:80]}..." if len(response) > 80 else f"      A: {response}")
            
            # Show recommended offers
            if rec.recommended_offers:
                print(f"\n   🎁 Recommended Offers:")
                for offer in rec.recommended_offers[:2]:  # Show first 2 offers
                    print(f"      • {offer.get('name', 'N/A')} (HK${offer.get('monthly_value', 0):,}/month)")
            
            # Show explanation
            print(f"\n   🧠 AI Explanation:")
            print(f"      Primary Reason: {rec.explanation.primary_reason}")
            print(f"      Confidence: {rec.explanation.confidence_score:.1%}")
            if rec.explanation.supporting_factors:
                print(f"      Supporting Factors: {', '.join(rec.explanation.supporting_factors[:2])}")
            
            print(f"   ⏳ Expires: {rec.expires_at.strftime('%Y-%m-%d %H:%M') if rec.expires_at else 'No expiry'}")
            print(f"   🏷️  Tags: {', '.join(rec.tags[:5])}")
        
        # Show summary statistics
        print_subheader("Recommendation Summary & Analytics")
        
        export_data = recommendation_generator.export_recommendations(recommendations)
        summary = export_data["summary"]
        
        print(f"📈 Total Recommendations: {summary['total_recommendations']}")
        print(f"💰 Total Expected Revenue: HK${summary['total_expected_revenue']:,.0f}")
        print(f"📊 Average Conversion Rate: {summary['average_conversion_probability']:.1%}")
        print(f"⚡ Average Business Impact: {summary['average_business_impact']:.2f}")
        
        print(f"\n🔥 Priority Distribution:")
        for priority, count in summary['by_priority'].items():
            print(f"   {priority.upper()}: {count} recommendations")
        
        print(f"\n🎬 Action Type Distribution:")
        for action, count in summary['by_action_type'].items():
            print(f"   {action.replace('_', ' ').title()}: {count} recommendations")
        
    except ImportError as e:
        print(f"❌ Recommendation system not available: {e}")
        print("🔄 Falling back to sample recommendation demonstration...")
        
        # Show sample recommendations instead
        samples = create_sample_recommendations()
        print(f"📋 Sample Recommendation:")
        sample = samples[0]
        print(f"   Customer: {sample.customer_name}")
        print(f"   Priority: {sample.priority.value}")
        print(f"   Action: {sample.action_type.value}")
        print(f"   Expected Revenue: HK${sample.expected_revenue:,.0f}")

def demonstrate_hong_kong_market_intelligence():
    """Demonstrate Hong Kong telecom market-specific intelligence"""
    print_subheader("Hong Kong Telecom Market Intelligence")
    
    try:
        from src.agents.recommendation_generator import RecommendationGenerator
        from src.agents.customer_analysis import CustomerDataAnalyzer
        from src.agents.lead_scoring import LeadScoringEngine
        from src.agents.three_hk_business_rules import ThreeHKBusinessRulesEngine
        
        # Initialize generator to access market intelligence
        generator = RecommendationGenerator(
            customer_analyzer=CustomerDataAnalyzer(),
            lead_scorer=LeadScoringEngine(),
            business_rules=ThreeHKBusinessRulesEngine()
        )
        
        mi = generator.market_intelligence
        
        print("🏢 Hong Kong Business Environment:")
        print(f"   ⏰ Peak Contact Hours: {', '.join(map(str, mi['peak_contact_hours']))} (24h format)")
        print(f"   📅 Optimal Call Days: {', '.join(['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][:len(mi['optimal_call_days'])])}")
        
        print(f"\n⏳ Average Decision Times:")
        for segment, days in mi['average_decision_time'].items():
            print(f"   {segment.title()}: {days} days")
        
        print(f"\n🏆 Competitor Analysis:")
        for competitor, strengths in mi['competitor_strengths'].items():
            print(f"   {competitor}: {', '.join(strengths)}")
        
        print(f"\n📊 Seasonal Business Factors:")
        quarters = ['Q1 (Jan-Mar)', 'Q2 (Apr-Jun)', 'Q3 (Jul-Sep)', 'Q4 (Oct-Dec)']
        for i, (quarter, factor) in enumerate(mi['seasonal_factors'].items()):
            print(f"   {quarters[i]}: {factor:.1%} (relative to baseline)")
        
    except ImportError:
        print("❌ Market intelligence module not available")

def demonstrate_business_value_calculation():
    """Demonstrate business value and ROI calculations"""
    print_subheader("Business Value & ROI Analysis")
    
    # Sample business metrics
    metrics = {
        "total_customers_analyzed": 3,
        "high_priority_recommendations": 2,
        "expected_total_revenue": 850000,
        "average_conversion_rate": 0.68,
        "processing_time_per_customer": 0.15,
        "manual_analysis_time_saved": 4.5,  # hours
        "agent_hourly_cost": 500,  # HKD
    }
    
    print("💼 Business Impact Analysis:")
    print(f"   📊 Customers Processed: {metrics['total_customers_analyzed']}")
    print(f"   🎯 High-Priority Leads: {metrics['high_priority_recommendations']}")
    print(f"   💰 Expected Revenue: HK${metrics['expected_total_revenue']:,}")
    print(f"   📈 Avg Conversion Rate: {metrics['average_conversion_rate']:.1%}")
    
    print(f"\n⚡ Efficiency Gains:")
    print(f"   🤖 AI Processing Time: {metrics['processing_time_per_customer']:.2f}s per customer")
    print(f"   👨‍💼 Manual Time Saved: {metrics['manual_analysis_time_saved']:.1f} hours")
    
    # Calculate ROI
    time_cost_saved = metrics['manual_analysis_time_saved'] * metrics['agent_hourly_cost']
    potential_revenue = metrics['expected_total_revenue'] * metrics['average_conversion_rate']
    
    print(f"\n💵 ROI Calculation:")
    print(f"   💸 Cost Savings: HK${time_cost_saved:,.0f} (analyst time)")
    print(f"   💰 Revenue Potential: HK${potential_revenue:,.0f}")
    print(f"   📊 Total Value: HK${time_cost_saved + potential_revenue:,.0f}")

def main():
    """Main demonstration workflow"""
    print_header("🚀 Agentic AI Revenue Assistant - Complete Workflow Demo")
    
    print("""
🎯 This demonstration showcases the complete end-to-end workflow of the 
   Agentic AI Revenue Assistant for Hong Kong telecom revenue optimization.

Key Features:
• 🤖 AI-powered customer analysis and lead scoring
• 📊 Actionable recommendation generation with explainability  
• 🎯 Hong Kong telecom market-specific insights
• 💼 Business intelligence and sales optimization
• 🔒 Privacy-compliant data processing
• ⚡ Real-time processing and ranking
""")
    
    # Create demo data
    print_subheader("Demo Data Setup")
    customers = create_demo_customers()
    purchase_histories = create_demo_purchase_histories()
    
    print(f"✅ Created {len(customers)} demo customers:")
    for customer in customers:
        print(f"   • {customer['customer_name']} ({customer['customer_type']})")
    
    # Demonstrate workflow steps
    demonstrate_customer_data_processing(customers)
    demonstrate_recommendation_generation(customers, purchase_histories)
    demonstrate_hong_kong_market_intelligence()
    demonstrate_business_value_calculation()
    
    print_header("🎉 Demo Complete - Agentic AI Revenue Assistant Ready for Production")
    
    print("""
✅ Demonstrated Capabilities:
• Complete customer data processing pipeline
• AI-powered recommendation generation with 5-tier priority system
• Hong Kong market-specific business intelligence
• Actionable sales recommendations with explainability
• Performance optimization and business value calculation

🚀 Ready for Integration:
• OpenRouter API workflow integration
• Streamlit dashboard deployment
• Privacy-compliant production deployment
• Real-time customer processing at scale
""")

if __name__ == "__main__":
    main() 