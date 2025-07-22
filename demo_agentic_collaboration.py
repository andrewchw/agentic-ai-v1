"""
Streamlit Demo: Multi-Agent Revenue Optimization
Showcases true agentic AI collaboration using CrewAI framework
"""

import streamlit as st
import pandas as pd
import json
import time
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go

# Import our multi-agent system
try:
    from src.agents.agentic_revenue_accelerator import (
        AgenticRevenueAccelerator,
        MarketContext,
        demonstrate_collaboration
    )
    AGENTS_AVAILABLE = True
except ImportError as e:
    st.error(f"Multi-agent system not available: {e}")
    AGENTS_AVAILABLE = False


def main():
    st.set_page_config(
        page_title="Agentic AI Revenue Accelerator",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for Three HK styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #00FF00, #007700);
        padding: 1rem;
        border-radius: 10px;
        color: black;
        margin-bottom: 2rem;
    }
    .agent-card {
        border: 2px solid #00FF00;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .collaboration-highlight {
        background-color: #e6ffe6;
        border-left: 4px solid #00FF00;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #00FF00;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Agentic AI Revenue Accelerator</h1>
        <p><strong>Multi-Agent Collaboration Demo</strong> | Powered by CrewAI Framework</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar - Agent Status and Configuration
    with st.sidebar:
        st.markdown("## 🔧 System Configuration")
        
        # Agent Status
        st.markdown("### Agent Status")
        if AGENTS_AVAILABLE:
            st.success("✅ Multi-Agent System Online")
            st.info("🤝 Collaboration Enabled")
        else:
            st.error("❌ Multi-Agent System Offline")
            st.warning("Fallback to single-agent mode")
        
        # Configuration
        st.markdown("### Market Configuration")
        economic_scenario = st.selectbox(
            "Economic Scenario",
            ["Recession (-1.2% GDP)", "Slow Growth (0.5% GDP)", "Strong Growth (2.8% GDP)"],
            index=0
        )
        
        collaboration_mode = st.selectbox(
            "Collaboration Mode",
            ["Full Multi-Agent", "Sequential Only", "Single Agent Fallback"],
            index=0
        )
        
        st.markdown("### Demo Controls")
        show_agent_thinking = st.checkbox("Show Agent Reasoning", value=True)
        show_collaboration_details = st.checkbox("Show Collaboration Metrics", value=True)

    # Main Demo Area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("## 👥 Meet Your AI Agent Team")
        
        # Lead Intelligence Agent Card
        st.markdown("""
        <div class="agent-card">
            <h3>🔍 Lead Intelligence Agent</h3>
            <p><strong>Role:</strong> Customer Data Analysis & Pattern Recognition</p>
            <p><strong>Specialization:</strong> Hong Kong telecom market behaviors</p>
            <p><strong>Collaboration Style:</strong> Delegates pricing questions, asks for strategic validation</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Revenue Optimization Agent Card  
        st.markdown("""
        <div class="agent-card">
            <h3>💰 Revenue Optimization Agent</h3>
            <p><strong>Role:</strong> Business Strategy & Revenue Growth</p>
            <p><strong>Specialization:</strong> Three HK product portfolio & competitive positioning</p>
            <p><strong>Collaboration Style:</strong> Responds to lead insights, provides strategic guidance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("## 📊 Collaboration Workflow")
        
        # Workflow Diagram
        workflow_data = {
            'Step': ['1. Data Analysis', '2. Pattern Recognition', '3. Strategic Questioning', 
                    '4. Revenue Optimization', '5. Collaborative Integration'],
            'Agent': ['Lead Intelligence', 'Lead Intelligence', 'Both Agents', 
                     'Revenue Optimization', 'Both Agents'],
            'Collaboration': ['Individual', 'Individual', 'Active Delegation', 
                            'Responds to Questions', 'Joint Decision Making']
        }
        
        workflow_df = pd.DataFrame(workflow_data)
        st.dataframe(workflow_df, use_container_width=True)
        
        # Collaboration Benefits
        st.markdown("""
        <div class="collaboration-highlight">
            <h4>🤝 Why Multi-Agent Collaboration?</h4>
            <ul>
                <li><strong>Specialized Expertise:</strong> Each agent focuses on their domain</li>
                <li><strong>Cross-Validation:</strong> Strategies grounded in data insights</li>
                <li><strong>Dynamic Adaptation:</strong> Agents adapt based on peer feedback</li>
                <li><strong>Explainable AI:</strong> Clear reasoning chains from collaboration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Demo Execution Section
    st.markdown("## 🚀 Live Multi-Agent Demo")
    
    # Sample Data Selection
    st.markdown("### Select Demo Scenario")
    scenario = st.selectbox(
        "Choose Customer Scenario",
        [
            "Enterprise Growth Opportunity",
            "SME Retention Challenge", 
            "Mixed Portfolio Analysis",
            "Custom Data Upload"
        ]
    )
    
    # Prepare demo data based on scenario
    demo_data = get_demo_data(scenario)
    
    # Show sample data
    with st.expander("📋 View Customer Data", expanded=False):
        st.json(demo_data['customers'])
    
    # Execute Demo Button
    if st.button("🎯 Execute Multi-Agent Analysis", type="primary", use_container_width=True):
        if not AGENTS_AVAILABLE:
            st.error("Multi-agent system not available. Please check installation.")
            return
            
        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Execute the analysis with real-time updates
        with st.spinner("Agents are collaborating..."):
            try:
                # Update progress
                status_text.text("🔍 Lead Intelligence Agent analyzing customer patterns...")
                progress_bar.progress(20)
                time.sleep(1)
                
                status_text.text("💰 Revenue Optimization Agent developing strategies...")
                progress_bar.progress(50)
                time.sleep(1)
                
                status_text.text("🤝 Agents collaborating on final recommendations...")
                progress_bar.progress(80)
                time.sleep(1)
                
                # Execute actual analysis
                result = demonstrate_collaboration(demo_data['customers'])
                
                progress_bar.progress(100)
                status_text.text("✅ Multi-agent analysis complete!")
                
                # Display Results
                display_collaboration_results(result, show_agent_thinking, show_collaboration_details)
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.info("This is normal in development - agents are still learning to collaborate!")

    # Educational Section
    st.markdown("---")
    st.markdown("## 📚 Understanding Agentic AI")
    
    edu_col1, edu_col2, edu_col3 = st.columns(3)
    
    with edu_col1:
        st.markdown("""
        ### 🧠 What Makes It "Agentic"?
        - **Autonomous Decision Making**
        - **Goal-Driven Behavior** 
        - **Dynamic Collaboration**
        - **Context Awareness**
        - **Self-Monitoring & Adaptation**
        """)
    
    with edu_col2:
        st.markdown("""
        ### 🔄 Collaboration Patterns
        - **Delegation:** "Ask the strategy expert"
        - **Consultation:** "Validate this analysis"
        - **Context Sharing:** Pass insights between agents
        - **Conflict Resolution:** Negotiate different approaches
        """)
    
    with edu_col3:
        st.markdown("""
        ### 🎯 Business Value
        - **Higher Quality Decisions**
        - **Reduced Blind Spots**
        - **Faster Problem Solving**
        - **Explainable Reasoning**
        - **Scalable Expertise**
        """)


def get_demo_data(scenario: str) -> Dict[str, Any]:
    """Generate demo data based on selected scenario"""
    
    base_customers = {
        "Enterprise Growth Opportunity": [
            {
                'customer_id': 'ENT_001',
                'customer_name': 'TechCorp Asia',
                'customer_type': 'enterprise',
                'current_monthly_spend': 45000,
                'contract_length': 24,
                'engagement_score': 0.85,
                'growth_indicators': ['expanding_workforce', 'new_locations', '5g_infrastructure_needs']
            }
        ],
        "SME Retention Challenge": [
            {
                'customer_id': 'SME_002',
                'customer_name': 'Local Business Ltd',
                'customer_type': 'sme', 
                'current_monthly_spend': 8500,
                'contract_length': 12,
                'engagement_score': 0.45,  # Low engagement
                'churn_risk_factors': ['price_sensitivity', 'economic_pressure', 'competitor_offers']
            }
        ],
        "Mixed Portfolio Analysis": [
            {
                'customer_id': 'ENT_003',
                'customer_name': 'Finance Corp',
                'customer_type': 'enterprise',
                'current_monthly_spend': 32000,
                'engagement_score': 0.92,
                'growth_indicators': ['digital_transformation']
            },
            {
                'customer_id': 'SME_004', 
                'customer_name': 'Creative Agency',
                'customer_type': 'sme',
                'current_monthly_spend': 12000,
                'engagement_score': 0.78,
                'growth_indicators': ['remote_work_setup']
            }
        ]
    }
    
    return {
        'customers': base_customers.get(scenario, base_customers["Enterprise Growth Opportunity"]),
        'scenario_context': f"Demonstration scenario: {scenario}"
    }


def display_collaboration_results(result: Dict[str, Any], show_thinking: bool, show_metrics: bool):
    """Display the multi-agent collaboration results"""
    
    st.markdown("## 🎯 Multi-Agent Analysis Results")
    
    if not result.get('success', False):
        st.error(f"Analysis encountered issues: {result.get('error', 'Unknown error')}")
        if 'fallback_analysis' in result:
            st.info("Showing fallback single-agent analysis:")
            st.json(result['fallback_analysis'])
        return
    
    # Success Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>✅</h3>
            <p><strong>Collaboration Status</strong><br>Successful</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖</h3>
            <p><strong>Agents Involved</strong><br>2 Specialized</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🔄</h3>
            <p><strong>Collaboration Type</strong><br>Sequential + Cross-Delegation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>📊</h3>
            <p><strong>Decision Quality</strong><br>Multi-Perspective</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Collaboration Details
    if show_metrics and 'agent_interactions' in result:
        st.markdown("### 🤝 Agent Collaboration Metrics")
        
        interactions = result['agent_interactions']
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Delegations Made:** {interactions.get('delegations_made', 'Available in logs')}")
            st.info(f"**Context Sharing:** {interactions.get('context_sharing', 'Enabled')}")
        
        with col2:
            st.info(f"**Questions Asked:** {interactions.get('questions_asked', 'Available in logs')}")
            st.info(f"**Memory Usage:** {interactions.get('memory_usage', 'Enabled')}")
    
    # Main Results
    st.markdown("### 📋 Collaborative Recommendations")
    
    if 'recommendations' in result:
        recommendations = result['recommendations']
        
        for i, rec in enumerate(recommendations, 1):
            priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            priority_icon = priority_color.get(rec.get('priority', 'Medium'), "🔵")
            
            st.markdown(f"""
            <div class="collaboration-highlight">
                <h4>{priority_icon} Recommendation {i}: {rec.get('type', 'General')}</h4>
                <p><strong>Description:</strong> {rec.get('description', 'N/A')}</p>
                <p><strong>Priority:</strong> {rec.get('priority', 'Medium')} | 
                   <strong>Complexity:</strong> {rec.get('implementation_complexity', 'Unknown')}</p>
                <p><strong>Expected Impact:</strong> {rec.get('expected_impact', 'To be calculated')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Agent Reasoning (if enabled)
    if show_thinking:
        st.markdown("### 🧠 Agent Reasoning Process")
        
        with st.expander("🔍 Lead Intelligence Agent Thinking", expanded=False):
            st.markdown("""
            **Analysis Process:**
            1. Processed customer data patterns
            2. Identified high-value opportunities  
            3. Calculated risk factors
            4. **Delegated pricing questions** to Revenue Agent
            5. Integrated strategic feedback
            """)
        
        with st.expander("💰 Revenue Optimization Agent Thinking", expanded=False):
            st.markdown("""
            **Strategy Development:**
            1. Received lead intelligence insights
            2. **Responded to pricing questions** from Lead Agent
            3. Applied Three HK business rules
            4. Assessed market positioning
            5. **Collaborated on final recommendations**
            """)
    
    # Technical Details
    with st.expander("🔧 Technical Implementation Details", expanded=False):
        st.markdown("**Multi-Agent Architecture:**")
        st.code("""
        CrewAI Framework Configuration:
        - Process: Sequential with Cross-Delegation
        - Memory: Enabled (agents remember interactions)  
        - Planning: Automatic task planning enabled
        - Collaboration: allow_delegation=True for both agents
        - Context Sharing: Task outputs passed between agents
        """)
        
        st.json(result.get('metadata', {}))


if __name__ == "__main__":
    main()
