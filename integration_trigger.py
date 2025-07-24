#!/usr/bin/env python3
"""
Integration Trigger for Lead Intelligence Dashboard
=================================================

Simple button/trigger that can be added to the Lead Intelligence Dashboard
to automatically send analysis results to Sales Optimization Agent via
the Agent Integration Service.

Author: Agentic AI Revenue Assistant
Date: 2025-07-23
"""

import streamlit as st
import json
import sys
import os
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.agent_integration_orchestrator import create_integration_service

def add_agent_collaboration_trigger():
    """
    Add this function to the Lead Intelligence Dashboard to enable
    automatic agent collaboration.
    """
    
    st.markdown("---")
    st.subheader("🤖 Automatic Agent Collaboration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Enable Multi-Agent Processing:** 
        Automatically send your analysis results to the Sales Optimization Agent 
        for immediate revenue optimization strategies and personalized offers.
        """)
    
    with col2:
        if st.button("🚀 Trigger Agent Collaboration", key="agent_collaboration"):
            return True
    
    return False

def process_agent_collaboration(lead_analysis_results: Dict[str, Any]):
    """
    Process agent collaboration with given lead analysis results.
    
    Args:
        lead_analysis_results: Results from Lead Intelligence Agent analysis
    """
    
    with st.spinner("🤖 Initiating agent collaboration..."):
        try:
            # Initialize integration service
            integration_service = create_integration_service()
            
            # Process the collaboration
            collaboration_results = integration_service.process_lead_intelligence_completion(
                lead_analysis_results
            )
            
            # Display results
            if collaboration_results.get("error"):
                st.error(f"❌ Agent collaboration failed: {collaboration_results['error']}")
                return
            
            st.success("✅ Agent collaboration completed successfully!")
            
            # Show workflow steps
            with st.expander("🔄 View Collaboration Workflow"):
                steps = collaboration_results.get("workflow_steps", [])
                for step in steps:
                    status_icon = "✅" if step.get("status") == "completed" else "❌"
                    st.write(f"{status_icon} **Step {step.get('step')}:** {step.get('action')}")
            
            # Show business impact
            business_impact = collaboration_results.get("business_impact", {})
            if business_impact:
                st.subheader("📊 Business Impact Analysis")
                
                revenue_analysis = business_impact.get("revenue_analysis", {})
                if revenue_analysis:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        current_revenue = revenue_analysis.get("current_monthly_revenue", 0)
                        st.metric("Current Monthly Revenue", f"HK${current_revenue:,.0f}")
                    
                    with col2:
                        projected_revenue = revenue_analysis.get("projected_monthly_revenue", 0)
                        st.metric("Projected Monthly Revenue", f"HK${projected_revenue:,.0f}")
                    
                    with col3:
                        uplift = revenue_analysis.get("uplift_percentage", 0)
                        st.metric("Revenue Uplift", f"{uplift:.1f}%")
                
                customer_impact = business_impact.get("customer_impact", {})
                if customer_impact:
                    st.write("**Customer Impact:**")
                    st.write(f"- **{customer_impact.get('total_customers_analyzed', 0)}** customers analyzed")
                    st.write(f"- **{customer_impact.get('segments_identified', 0)}** segments identified")
                    st.write(f"- **{customer_impact.get('personalized_offers_created', 0)}** personalized offers created")
            
            # Show sales optimization results
            sales_results = collaboration_results.get("collaboration_results", {}).get("sales_optimization", {})
            if sales_results:
                st.subheader("🎯 Sales Optimization Results")
                
                # Show optimizations
                optimizations = sales_results.get("sales_optimizations", [])
                if optimizations:
                    st.write("**Segment Optimization Strategies:**")
                    for opt in optimizations:
                        st.write(f"- **{opt.get('segment')}**: {opt.get('optimization_strategy')} "
                                f"(Expected uplift: {opt.get('expected_uplift', 0)}%)")
                
                # Show personalized offers
                offers = sales_results.get("personalized_offers", [])
                if offers:
                    with st.expander("💰 View Personalized Offers"):
                        for offer in offers:
                            st.write(f"**{offer.get('plan', 'Unknown Plan')}** - {offer.get('price', 'N/A')}")
                            st.write(f"Target: {offer.get('target_segment', 'N/A')} "
                                    f"({offer.get('customer_count', 0)} customers)")
                            st.write(f"Expected conversion: {offer.get('expected_conversion_rate', 0)}%")
                            st.write("---")
            
            # Show priority actions
            next_actions = collaboration_results.get("next_actions", [])
            if next_actions:
                st.subheader("⚡ Priority Actions")
                
                priority_actions = [a for a in next_actions if a.get("priority", 99) <= 2]
                for action in priority_actions:
                    priority_color = "🔴" if action.get("priority") == 1 else "🟡"
                    st.write(f"{priority_color} **{action.get('action_type', 'Unknown').replace('_', ' ').title()}**")
                    st.write(f"   - {action.get('description', 'No description')}")
                    st.write(f"   - Timeline: {action.get('timeline', 'TBD')}")
                    st.write(f"   - Expected outcome: {action.get('expected_outcome', 'N/A')}")
            
            # Show agent protocol tasks created
            workflow_steps = collaboration_results.get("workflow_steps", [])
            protocol_step = next((s for s in workflow_steps if s.get("action") == "Create Agent Protocol Tasks"), None)
            if protocol_step and protocol_step.get("tasks_created", 0) > 0:
                st.info(f"🔗 Created {protocol_step['tasks_created']} tasks in Agent Protocol for further processing")
            
            return collaboration_results
            
        except Exception as e:
            st.error(f"❌ Error during agent collaboration: {e}")
            return None

def demo_agent_collaboration():
    """
    Standalone demo of agent collaboration functionality.
    """
    st.title("🤖 Agent Collaboration Demo")
    st.markdown("Demonstration of automatic agent handoff from Lead Intelligence to Sales Optimization")
    
    # Sample lead analysis data
    sample_data = {
        "customer_segments": {
            "high_value": {"count": 150, "avg_arpu": 650},
            "business": {"count": 89, "avg_arpu": 890},
            "family": {"count": 234, "avg_arpu": 420},
            "price_sensitive": {"count": 112, "avg_arpu": 280}
        },
        "lead_scores": {
            "customer_001": 85,
            "customer_002": 92,
            "customer_003": 76,
            "customer_004": 88
        },
        "churn_analysis": {
            "high_risk_customers": 45,
            "medium_risk_customers": 78,
            "segments": ["price_sensitive"]
        },
        "revenue_insights": {
            "average_arpu": 485,
            "total_customers": 585,
            "monthly_revenue": 283725
        }
    }
    
    st.subheader("📊 Sample Lead Analysis Results")
    st.json(sample_data)
    
    if st.button("🚀 Execute Agent Collaboration Demo"):
        results = process_agent_collaboration(sample_data)
        
        if results:
            st.balloons()
            st.success("🎉 Agent collaboration demo completed successfully!")

# Instructions for integration
INTEGRATION_INSTRUCTIONS = """
## 🔧 Integration Instructions

To add agent collaboration to your Lead Intelligence Dashboard:

1. **Import the trigger function:**
   ```python
   from integration_trigger import add_agent_collaboration_trigger, process_agent_collaboration
   ```

2. **Add to your dashboard (after analysis results):**
   ```python
   # After displaying analysis results
   if add_agent_collaboration_trigger():
       collaboration_results = process_agent_collaboration(your_analysis_results)
   ```

3. **Required data format for lead_analysis_results:**
   ```python
   {
       "customer_segments": {
           "segment_name": {"count": int, "avg_arpu": float}
       },
       "lead_scores": {
           "customer_id": score_value
       },
       "churn_analysis": {
           "high_risk_customers": int,
           "segments": ["segment_names"]
       },
       "revenue_insights": {
           "average_arpu": float,
           "total_customers": int
       }
   }
   ```
"""

if __name__ == "__main__":
    # Run as standalone demo
    demo_agent_collaboration()
    
    # Show integration instructions
    with st.expander("🔧 Integration Instructions"):
        st.markdown(INTEGRATION_INSTRUCTIONS)
