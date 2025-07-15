"""
Home page component for the Agentic AI Revenue Assistant
"""

import streamlit as st
from config.app_config import config

def render_home_page():
    """Render the home page content"""
    
    st.markdown("## Welcome to the Agentic AI Revenue Assistant")
    
    st.markdown("""
    ### 🎯 What This Tool Does
    
    This privacy-first AI assistant helps Hong Kong telecom companies:
    - **Analyze customer data** while protecting privacy
    - **Prioritize leads** based on purchase patterns and engagement
    - **Generate actionable recommendations** for sales teams
    - **Maintain compliance** with GDPR and Hong Kong PDPO
    
    ### 🔒 Privacy & Security
    
    - All sensitive data is **pseudonymized immediately** upon upload
    - No raw personal information is ever sent to external AI services
    - Data encryption in transit and at rest
    - Audit logging for compliance
    
    ### 🚀 Getting Started
    
    1. **Upload Data**: Go to "Upload Data" to upload customer and purchase CSV files
    2. **Review Privacy**: Check "Privacy & Security" for data protection details
    3. **View Results**: See analysis and recommendations in "Analysis Results"
    
    ### 📊 Demo Features
    
    - Support for up to 10,000 customer records
    - Three HK branded interface
    - Telecom-specific offer recommendations
    - Export functionality for sales teams
    """)
    
    # Status cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Max Records Supported",
            value=f"{config.MAX_RECORDS:,}",
            help="Maximum number of customer records supported in this demo"
        )
    
    with col2:
        st.metric(
            label="Privacy Status",
            value="✅ Protected",
            help="All data is pseudonymized and encrypted"
        )
    
    with col3:
        st.metric(
            label="AI Model",
            value="DeepSeek",
            help="Using DeepSeek LLM via OpenRouter for analysis"
        )
    
    st.markdown("---")
    
    # Sample data information
    st.markdown("### 📂 Sample Data Available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Customer Data Sample**
        - Customer profiles and demographics
        - Account information and status
        - Contact preferences
        
        File: `sample-customer-data-20250714.csv`
        """)
    
    with col2:
        st.info("""
        **Purchase History Sample**
        - Transaction records
        - Service usage patterns
        - Engagement metrics
        
        File: `sample_purchase_history.csv`
        """)
    
    # Call to action
    st.markdown("### 👉 Ready to Start?")
    if st.button("🚀 Go to Upload Data", type="primary"):
        st.session_state.current_page = "Upload Data"
        st.rerun() 