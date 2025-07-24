#!/usr/bin/env python3
"""
Agent Integration Test
=====================

Test script to demonstrate the automatic integration between
Lead Intelligence Agent results and Agent Protocol for 
multi-agent collaboration.

This script simulates the missing integration that should happen
automatically when analysis completes in the Lead Intelligence Dashboard.

Usage:
    python test_agent_integration.py

Author: Agentic AI Revenue Assistant
Date: 2025-07-23
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.agents.agent_integration_service import get_integration_service, trigger_agent_collaboration

def create_sample_analysis_results():
    """Create sample analysis results like those from Lead Intelligence Agent."""
    return {
        'analysis_timestamp': datetime.now().isoformat(),
        'customer_count': 150,
        'analysis_type': 'lead_intelligence_analysis',
        'market_focus': 'hong_kong_telecom',
        'patterns': {
            'high_value_segments': [
                {
                    'segment_name': 'Premium Mobile Users',
                    'customer_count': 35,
                    'avg_arpu': 850,
                    'characteristics': ['high_data_usage', '5g_enabled', 'business_user'],
                    'opportunity_score': 92
                },
                {
                    'segment_name': 'Family Plan Subscribers', 
                    'customer_count': 28,
                    'avg_arpu': 620,
                    'characteristics': ['multi_line', 'stable_payment', 'long_tenure'],
                    'opportunity_score': 78
                }
            ],
            'churn_indicators': [
                {
                    'risk_level': 'high',
                    'customer_count': 18,
                    'key_factors': ['billing_complaints', 'competitor_contact', 'usage_decline'],
                    'urgency_score': 95
                },
                {
                    'risk_level': 'medium',
                    'customer_count': 31,
                    'key_factors': ['contract_expiry_soon', 'price_sensitivity'],
                    'urgency_score': 68
                }
            ],
            'lead_scores': [
                {
                    'score_range': '90-100',
                    'customer_count': 22,
                    'conversion_probability': 0.89,
                    'recommended_offers': ['5g_premium_upgrade', 'business_package']
                },
                {
                    'score_range': '75-89', 
                    'customer_count': 41,
                    'conversion_probability': 0.72,
                    'recommended_offers': ['family_plan_upgrade', 'data_boost']
                }
            ],
            'collaboration_requests': [
                {
                    'request_type': 'optimization_strategy',
                    'focus': 'premium_segment_expansion',
                    'priority': 'high',
                    'data_context': 'Premium Mobile Users showing 92% opportunity score'
                },
                {
                    'request_type': 'retention_strategy',
                    'focus': 'churn_prevention', 
                    'priority': 'urgent',
                    'data_context': '18 high-risk customers requiring immediate intervention'
                },
                {
                    'request_type': 'upsell_campaign',
                    'focus': 'lead_conversion',
                    'priority': 'medium',
                    'data_context': '63 qualified leads with 75%+ conversion probability'
                }
            ]
        },
        'recommendations': [
            'Focus retention efforts on 18 high-risk customers immediately',
            'Design premium upsell campaign for 35 high-value mobile users',
            'Create family plan expansion strategy for stable subscribers',
            'Implement competitive response for price-sensitive segments'
        ],
        'confidence_score': 0.87,
        'data_quality_score': 0.94
    }

def test_agent_integration():
    """Test the agent integration functionality."""
    print("🚀 Testing Agent Integration Service")
    print("=" * 50)
    
    # Get integration service
    integration_service = get_integration_service()
    
    # Check Agent Protocol availability
    print("1. Checking Agent Protocol availability...")
    protocol_available = integration_service.check_agent_protocol_availability()
    
    if protocol_available:
        print("   ✅ Agent Protocol server is available")
    else:
        print("   ❌ Agent Protocol server is not available")
        print("   💡 Make sure to start the server: python start_agent_protocol.py")
        return
    
    # Get collaboration status
    print("\n2. Getting collaboration status...")
    status = integration_service.get_collaboration_status()
    print(f"   📊 Service enabled: {status['service_enabled']}")
    print(f"   📊 Total collaborations: {status['total_collaborations']}")
    print(f"   📊 Success rate: {status['success_rate']:.1f}%")
    
    # Create sample analysis results
    print("\n3. Creating sample Lead Intelligence analysis results...")
    analysis_results = create_sample_analysis_results()
    print(f"   📈 Simulated analysis for {analysis_results['customer_count']} customers")
    print(f"   📈 Found {len(analysis_results['patterns']['high_value_segments'])} high-value segments")
    print(f"   📈 Identified {len(analysis_results['patterns']['churn_indicators'])} churn risk groups")
    print(f"   📈 Generated {len(analysis_results['patterns']['collaboration_requests'])} collaboration requests")
    
    # Trigger collaboration workflow
    print("\n4. Triggering multi-agent collaboration workflow...")
    print("   🤝 Sending analysis results to Revenue Optimization Agent...")
    
    collaboration_result = trigger_agent_collaboration(analysis_results)
    
    if collaboration_result['success']:
        print(f"   ✅ Collaboration completed successfully!")
        print(f"   🕐 Workflow duration: {collaboration_result['workflow_duration']:.1f} seconds")
        print(f"   🆔 Task ID: {collaboration_result['task_id']}")
        
        # Show collaboration summary
        summary = collaboration_result['analysis_summary']
        print(f"   📊 Collaboration Summary:")
        print(f"      - Customers analyzed: {summary['customer_count']}")
        print(f"      - Patterns found: {summary['patterns_found']}")
        print(f"      - Collaboration requests: {summary['collaboration_requests']}")
        
    else:
        print(f"   ❌ Collaboration failed")
        if 'error' in collaboration_result:
            print(f"   Error: {collaboration_result['error']}")
    
    # Show updated collaboration history
    print("\n5. Collaboration history:")
    history = integration_service.get_collaboration_history()
    
    if history:
        for i, collab in enumerate(history[-3:], 1):  # Show last 3
            timestamp = collab['timestamp'][:19]  # Remove microseconds
            print(f"   {i}. {timestamp} - {collab['source_agent']} → {collab['target_agent']} ({collab['status']})")
    else:
        print("   📭 No collaboration history yet")
    
    print("\n" + "=" * 50)
    print("🎯 Integration Test Complete!")
    
    if collaboration_result.get('success'):
        print("✅ SUCCESS: Lead Intelligence → Revenue Agent collaboration working!")
        print("💡 This demonstrates automatic multi-agent workflow integration")
        print("🔗 Check the Agent Collaboration Dashboard at http://localhost:8501")
    else:
        print("⚠️  Integration test completed but collaboration failed")
        print("💡 Check Agent Protocol server logs for details")

def main():
    """Main test execution."""
    try:
        test_agent_integration()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
