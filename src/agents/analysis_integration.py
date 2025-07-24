"""
Analysis Results Integration
===========================

Integration component to automatically trigger agent collaboration
when Lead Intelligence analysis completes.

This file provides the integration hooks that should be added to the
Lead Intelligence Dashboard to enable automatic multi-agent collaboration.

Usage in Lead Intelligence Dashboard:
    from src.agents.analysis_integration import trigger_collaboration_on_completion
    
    # After analysis completes:
    trigger_collaboration_on_completion(analysis_results)

Author: Agentic AI Revenue Assistant  
Date: 2025-07-23
"""

import streamlit as st
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import the integration service
try:
    from .agent_integration_service import trigger_agent_collaboration, get_collaboration_status
except ImportError:
    # Fallback for when running as standalone
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from agents.agent_integration_service import trigger_agent_collaboration, get_collaboration_status

logger = logging.getLogger(__name__)

def trigger_collaboration_on_completion(analysis_results: Dict[str, Any], 
                                       show_progress: bool = True) -> Optional[Dict[str, Any]]:
    """
    Trigger agent collaboration when Lead Intelligence analysis completes.
    
    Args:
        analysis_results: The complete analysis results from Lead Intelligence Agent
        show_progress: Whether to show progress in Streamlit UI
        
    Returns:
        Collaboration workflow results or None if disabled
    """
    try:
        # Check if collaboration is enabled
        if not is_collaboration_available():
            if show_progress:
                st.info("ℹ️ Agent collaboration is not available - Agent Protocol server may be offline")
            return None
        
        if show_progress:
            with st.spinner("🤝 Triggering multi-agent collaboration..."):
                st.write("📤 Sending analysis results to Revenue Optimization Agent...")
                
                # Trigger the collaboration workflow
                collaboration_result = trigger_agent_collaboration(analysis_results)
                
                if collaboration_result['success']:
                    st.success(f"✅ Agent collaboration completed successfully!")
                    st.write(f"🕐 Workflow duration: {collaboration_result['workflow_duration']:.1f} seconds")
                    
                    # Show collaboration summary
                    with st.expander("📊 Collaboration Summary", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Task ID", collaboration_result['task_id'][:8])
                            st.metric("Customers Analyzed", collaboration_result['analysis_summary']['customer_count'])
                        
                        with col2:
                            st.metric("Patterns Found", collaboration_result['analysis_summary']['patterns_found'])
                            st.metric("Collaboration Requests", collaboration_result['analysis_summary']['collaboration_requests'])
                    
                    return collaboration_result
                else:
                    st.error("❌ Agent collaboration failed")
                    if 'error' in collaboration_result:
                        st.error(f"Error: {collaboration_result['error']}")
                    return None
        else:
            # Silent collaboration (no UI feedback)
            return trigger_agent_collaboration(analysis_results)
            
    except Exception as e:
        logger.error(f"Error in collaboration trigger: {e}")
        if show_progress:
            st.error(f"❌ Collaboration error: {str(e)}")
        return None


def is_collaboration_available() -> bool:
    """Check if agent collaboration is available."""
    try:
        status = get_collaboration_status()
        return status['service_enabled'] and status['agent_protocol_available']
    except Exception:
        return False


def render_collaboration_status_widget():
    """Render a collaboration status widget for the dashboard sidebar."""
    try:
        status = get_collaboration_status()
        
        st.markdown("### 🤝 Agent Collaboration")
        
        # Service status
        if status['service_enabled']:
            st.success("✅ Collaboration Service: Enabled")
        else:
            st.warning("⚠️ Collaboration Service: Disabled")
        
        # Agent Protocol status
        if status['agent_protocol_available']:
            st.success("✅ Agent Protocol: Connected")
        else:
            st.error("🔴 Agent Protocol: Offline")
        
        # Collaboration metrics
        if status['total_collaborations'] > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", status['total_collaborations'])
            with col2:
                st.metric("Success Rate", f"{status['success_rate']:.1f}%")
            
            # Recent collaborations
            if status['recent_collaborations']:
                with st.expander("Recent Collaborations", expanded=False):
                    for collab in status['recent_collaborations']:
                        timestamp = datetime.fromisoformat(collab['timestamp']).strftime('%H:%M:%S')
                        st.write(f"🕐 {timestamp} - {collab['source_agent']} → {collab['target_agent']}")
        
    except Exception as e:
        st.error(f"Error loading collaboration status: {e}")


def render_collaboration_controls():
    """Render collaboration controls for manual testing."""
    st.markdown("### 🧪 Collaboration Testing")
    
    if st.button("🔄 Check Agent Protocol Status"):
        status = get_collaboration_status()
        st.json(status)
    
    if st.button("🚀 Test Collaboration (Demo Data)"):
        demo_results = {
            'customer_count': 100,
            'patterns': {
                'high_value_segments': [
                    {'segment': 'Premium Mobile', 'count': 25, 'avg_arpu': 850},
                    {'segment': 'Business Users', 'count': 15, 'avg_arpu': 1200}
                ],
                'churn_indicators': [
                    {'risk_level': 'high', 'count': 12, 'factors': ['low_usage', 'billing_issues']},
                    {'risk_level': 'medium', 'count': 28, 'factors': ['competitive_offers']}
                ],
                'lead_scores': [
                    {'score_range': '80-100', 'count': 18, 'conversion_probability': 0.85},
                    {'score_range': '60-79', 'count': 35, 'conversion_probability': 0.65}
                ]
            }
        }
        
        result = trigger_collaboration_on_completion(demo_results, show_progress=True)
        if result:
            st.balloons()


# Integration hooks for existing dashboard components
def add_collaboration_to_analysis_complete(analysis_function):
    """
    Decorator to add automatic collaboration to existing analysis functions.
    
    Usage:
        @add_collaboration_to_analysis_complete
        def run_customer_analysis():
            # existing analysis code
            return analysis_results
    """
    def wrapper(*args, **kwargs):
        # Run the original analysis
        result = analysis_function(*args, **kwargs)
        
        # Trigger collaboration if analysis successful
        if result and isinstance(result, dict):
            collaboration_result = trigger_collaboration_on_completion(result, show_progress=False)
            if collaboration_result:
                # Add collaboration info to results
                result['collaboration'] = collaboration_result
        
        return result
    
    return wrapper


# Configuration helper
def configure_collaboration_settings():
    """Configure collaboration settings in the dashboard."""
    st.markdown("### ⚙️ Collaboration Settings")
    
    current_status = get_collaboration_status()
    
    # Enable/disable toggle
    enabled = st.checkbox(
        "Enable automatic agent collaboration",
        value=current_status['service_enabled'],
        help="Automatically send analysis results to Revenue Optimization Agent"
    )
    
    if enabled != current_status['service_enabled']:
        st.info("⚠️ Collaboration setting change requires restart to take effect")
    
    # Agent Protocol URL
    st.text_input(
        "Agent Protocol URL",
        value="http://127.0.0.1:8080",
        disabled=True,
        help="URL of the Agent Protocol server for multi-agent communication"
    )
    
    # Collaboration timeout
    timeout = st.slider(
        "Collaboration timeout (seconds)",
        min_value=15,
        max_value=120,
        value=45,
        help="Maximum time to wait for agent collaboration to complete"
    )
    
    return {
        'enabled': enabled,
        'timeout': timeout
    }
