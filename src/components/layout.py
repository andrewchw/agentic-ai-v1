"""
Layout components for the Streamlit application
Handles page configuration, header, sidebar, and Three HK branding
"""

import streamlit as st
from config.app_config import config

# Import model selection component
try:
    from src.components.model_selection import render_model_selection_sidebar, init_model_selection_state
    MODEL_SELECTION_AVAILABLE = True
except ImportError:
    MODEL_SELECTION_AVAILABLE = False


def setup_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title=config.APP_NAME,
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": f"{config.APP_NAME} v{config.APP_VERSION} - " f"Privacy-first AI lead generation tool",
        },
    )

    # Apply Three HK color scheme with explicit text colors
    st.markdown(
        f"""
    <style>
        /* Global app styling */
        .stApp {{
            background-color: {config.ACCENT_COLOR} !important;
            color: {config.SECONDARY_COLOR} !important;
        }}
        
        /* Main content area */
        .main .block-container {{
            background-color: {config.ACCENT_COLOR} !important;
            color: {config.SECONDARY_COLOR} !important;
        }}
        
        /* Force text color for ALL text elements */
        .stApp *, .main *, .block-container *, 
        .stMarkdown, .stMarkdown *, .stText, .stCaption, .stWrite, 
        p, div, span, h1, h2, h3, h4, h5, h6, 
        .stSelectbox label, .stTextInput label,
        .element-container *, .stDataFrame *, .stTable *,
        .stMetric *, .stInfo *, .stSuccess *, .stWarning *, .stError * {{
            color: {config.SECONDARY_COLOR} !important;
        }}
        
        /* Header styling */
        .main-header {{
            color: {config.SECONDARY_COLOR} !important;
            background-color: {config.ACCENT_COLOR} !important;
            padding: 20px;
            border-bottom: 3px solid {config.PRIMARY_COLOR};
        }}
        
        /* Sidebar styling */
        .sidebar .sidebar-content {{
            background-color: #f8f9fa !important;
            color: {config.SECONDARY_COLOR} !important;
        }}
        
        /* Button styling */
        .stButton > button {{
            background-color: {config.PRIMARY_COLOR} !important;
            color: {config.SECONDARY_COLOR} !important;
            border: none !important;
            border-radius: 5px !important;
        }}
        
        /* Input field styling */
        .stSelectbox > div > div {{
            background-color: {config.ACCENT_COLOR} !important;
            color: {config.SECONDARY_COLOR} !important;
        }}
        
        .stTextInput > div > div > input, .stSelectbox > div > div > select {{
            color: {config.SECONDARY_COLOR} !important;
            background-color: {config.ACCENT_COLOR} !important;
        }}
        
        /* Streamlit specific element overrides */
        .stMarkdown p, .stMarkdown div, .stMarkdown span {{
            color: {config.SECONDARY_COLOR} !important;
        }}
        
        /* Data display elements */
        .stDataFrame, .stTable, .dataframe {{
            color: {config.SECONDARY_COLOR} !important;
        }}
        
        /* Metrics and status boxes */
        .stMetric > div, .stInfo > div, .stSuccess > div, .stWarning > div, .stError > div {{
            color: {config.SECONDARY_COLOR} !important;
        }}
        
        /* Ensure high contrast for readability */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            color: {config.SECONDARY_COLOR} !important;
            font-weight: bold !important;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_header():
    """Render the main application header"""
    st.markdown(
        f"""
    <div class="main-header">
        <h1>🤖 {config.APP_NAME}</h1>
        <p style="font-size: 18px; margin-bottom: 0;">
            Privacy-first AI lead generation for Hong Kong telecom companies
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")


def render_sidebar():
    """Render the sidebar navigation and return selected page"""
    
    # Initialize model selection state
    if MODEL_SELECTION_AVAILABLE:
        init_model_selection_state()
    
    with st.sidebar:
        st.markdown(f"### {config.APP_NAME}")
        st.markdown(f"**Version:** {config.APP_VERSION}")

        st.markdown("---")

        # Navigation menu with session state support
        # Initialize session state for navigation if not set
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Home"

        # Get the current page index for the selectbox
        pages = ["Home", "Upload Data", "Analysis Results", "Privacy & Security"]
        try:
            current_index = pages.index(st.session_state.current_page)
        except ValueError:
            current_index = 0
            st.session_state.current_page = "Home"

        page = st.selectbox("Navigate to:", pages, index=current_index, key="page_selector")

        # Update session state when selectbox changes
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()

        # Add model selection component
        if MODEL_SELECTION_AVAILABLE:
            render_model_selection_sidebar()

        st.markdown("---")

        # System status
        st.markdown("### System Status")

        # Check API connectivity
        if config.OPENROUTER_API_KEY:
            st.success("✅ OpenRouter API Connected")
        else:
            st.error("❌ OpenRouter API Key Missing")

        if config.ENCRYPTION_KEY:
            st.success("✅ Encryption Configured")
        else:
            st.warning("⚠️ Encryption Key Missing")

        st.markdown("---")

        # Privacy notice
        st.markdown("### 🔒 Privacy Notice")
        st.info(
            "All sensitive data is pseudonymized immediately upon upload. "
            "No personal information is sent to external AI services."
        )

        return st.session_state.current_page


def render_footer():
    """Render the application footer"""
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Three HK Compatible**")
        st.markdown("Designed for telecom industry standards")

    with col2:
        st.markdown("**Privacy First**")
        st.markdown("GDPR & Hong Kong PDPO compliant")

    with col3:
        st.markdown("**AI Powered**")
        st.markdown("Advanced lead analysis and recommendations")
