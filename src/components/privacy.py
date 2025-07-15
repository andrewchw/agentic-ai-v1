"""
Privacy and Security page component
Shows data protection measures and compliance information
"""

import streamlit as st
from config.app_config import config

def render_privacy_page():
    """Render the privacy and security information page"""
    
    st.markdown("## 🔒 Privacy & Security")
    
    st.markdown("""
    ### Our Privacy-First Commitment
    
    The Agentic AI Revenue Assistant is designed with **privacy as the foundation**, not an afterthought.
    Every aspect of data handling prioritizes your customers' privacy and regulatory compliance.
    """)
    
    # Privacy principles
    st.markdown("### 🛡️ Core Privacy Principles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🔐 Immediate Pseudonymization**
        - All sensitive data is masked within seconds of upload
        - Original personal information never stored
        - Reversible only with proper authorization
        """)
        
        st.info("""
        **🚫 No Raw PII to AI Services**
        - Only anonymized data sent to external LLMs
        - Personal identifiers completely removed
        - Zero risk of data leakage to AI providers
        """)
    
    with col2:
        st.info("""
        **🔒 Encryption Everywhere**
        - Data encrypted in transit (TLS 1.3)
        - Storage encryption at rest (AES-256)
        - Secure key management
        """)
        
        st.info("""
        **📋 Complete Audit Trail**
        - All data operations logged
        - Privacy-aware logging (no PII in logs)
        - 90-day audit retention
        """)
    
    # Compliance section
    st.markdown("---")
    st.markdown("### ⚖️ Regulatory Compliance")
    
    tab1, tab2 = st.tabs(["🇪🇺 GDPR", "🇭🇰 Hong Kong PDPO"])
    
    with tab1:
        st.markdown("""
        **General Data Protection Regulation (GDPR)**
        
        ✅ **Right to be Forgotten**: Data can be completely removed upon request  
        ✅ **Data Minimization**: Only necessary data is processed  
        ✅ **Purpose Limitation**: Data used only for stated business purposes  
        ✅ **Storage Limitation**: Automatic data cleanup after sessions  
        ✅ **Security by Design**: Privacy built into system architecture  
        ✅ **Transparency**: Clear consent and processing notices  
        """)
    
    with tab2:
        st.markdown("""
        **Hong Kong Personal Data (Privacy) Ordinance**
        
        ✅ **Data Protection Principle 1**: Fair and lawful collection  
        ✅ **Data Protection Principle 2**: Accurate and up-to-date data  
        ✅ **Data Protection Principle 3**: Data used only for stated purposes  
        ✅ **Data Protection Principle 4**: Adequate security measures  
        ✅ **Data Protection Principle 5**: Information provided on request  
        ✅ **Data Protection Principle 6**: Access and correction rights  
        """)
    
    # Technical implementation
    st.markdown("---")
    st.markdown("### 🔧 Technical Implementation")
    
    st.markdown("""
    **Data Pseudonymization Process:**
    1. 📁 **Upload**: CSV files received via secure Streamlit upload
    2. ⚡ **Immediate Processing**: Sensitive fields identified and masked
    3. 🏷️ **Pseudonymization**: SHA-256 hashing with salt for reversibility
    4. 🗃️ **Storage**: Only pseudonymized data stored locally
    5. 🤖 **AI Processing**: Anonymous data sent to DeepSeek LLM
    6. 📊 **Results**: Lead recommendations with masked identifiers
    7. 🧹 **Cleanup**: All data purged at session end
    """)
    
    # Security measures
    st.markdown("### 🛡️ Security Measures")
    
    security_features = [
        "🔐 **Session Management**: Automatic timeout and data cleanup",
        "🔒 **API Security**: Secure OpenRouter integration with rate limiting", 
        "📝 **Input Validation**: Comprehensive CSV validation and sanitization",
        "🚫 **Access Control**: No persistent data storage",
        "⚠️ **Error Handling**: Privacy-aware error messages",
        "📊 **Monitoring**: Real-time security monitoring and alerts"
    ]
    
    for feature in security_features:
        st.markdown(f"- {feature}")
    
    # Contact and support
    st.markdown("---")
    st.markdown("### 📞 Privacy Support")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Data Subject Rights:**
        - Request data deletion
        - Access processing information  
        - Correct inaccurate data
        - Object to processing
        """)
    
    with col2:
        st.markdown("""
        **Security Concerns:**
        - Report potential data breaches
        - Request security information
        - Compliance documentation
        - Technical specifications
        """)
    
    # Configuration status
    st.markdown("---")
    st.markdown("### ⚙️ Current Configuration Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if config.ENCRYPTION_KEY and config.ENCRYPTION_KEY != "your_encryption_key_here_please_change_this":
            st.success("✅ Encryption Configured")
        else:
            st.warning("⚠️ Default Encryption Key")
    
    with col2:
        if config.ENABLE_AUDIT_LOGGING:
            st.success("✅ Audit Logging Enabled")
        else:
            st.error("❌ Audit Logging Disabled")
    
    with col3:
        if config.SESSION_TIMEOUT_MINUTES > 0:
            st.success(f"✅ Session Timeout: {config.SESSION_TIMEOUT_MINUTES}min")
        else:
            st.warning("⚠️ No Session Timeout") 