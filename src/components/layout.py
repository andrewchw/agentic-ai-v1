"""
Layout components for the Streamlit application
Handles page configuration, header, sidebar, and Three HK branding
"""

import streamlit as st
from config.app_config import config


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
            "About": f"{config.APP_NAME} v{config.APP_VERSION} - Privacy-first AI lead generation tool",
        },
    )

    # Apply Three HK color scheme
    st.markdown(
        """
    <style>
        .stApp {{
            background-color: {config.ACCENT_COLOR};
        }}
        .main-header {{
            color: {config.SECONDARY_COLOR};
            background-color: {config.ACCENT_COLOR};
            padding: 20px;
            border-bottom: 3px solid {config.PRIMARY_COLOR};
        }}
        .sidebar .sidebar-content {{
            background-color: #f8f9fa;
        }}
        .stButton > button {{
            background-color: {config.PRIMARY_COLOR};
            color: {config.SECONDARY_COLOR};
            border: none;
            border-radius: 5px;
        }}
        .stSelectbox > div > div {{
            background-color: {config.ACCENT_COLOR};
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_header():
    """Render the main application header"""
    st.markdown(
        """
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
