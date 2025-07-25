"""
Main Streamlit Application for Agentic AI Revenue Assistant
Entry point for the lead generation and analysis tool
"""

import streamlit as st
import sys
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from config.app_config import config
from src.components.layout import setup_page_config, render_header, render_sidebar
from src.utils.logger import setup_logging

# Import model selection components
try:
    from src.components.model_selection import render_model_status_page, should_show_model_status, hide_model_status
    MODEL_SELECTION_AVAILABLE = True
except ImportError:
    MODEL_SELECTION_AVAILABLE = False


def main():
    """Main application function"""

    # Setup logging
    setup_logging()

    # Setup page configuration
    setup_page_config()

    # Create necessary directories
    config.setup_directories()

    # Validate configuration
    missing_config = config.validate_config()
    if missing_config:
        st.error(f"Missing required configuration: {', '.join(missing_config)}")
        st.info("Please check your .env file and ensure all required variables are set.")
        st.stop()

    # Check if we should show model status page
    if MODEL_SELECTION_AVAILABLE and should_show_model_status():
        render_model_status_page()
        
        # Back button
        if st.button("← Back to Main App"):
            hide_model_status()
            st.rerun()
        return

    # Render main layout
    render_header()

    # Sidebar navigation
    render_sidebar()

    # Get current page from session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    page = st.session_state.current_page

    # Main content area
    if page == "Home":
        from src.components.home import render_home_page

        render_home_page()
    elif page == "Upload Data":
        from src.components.upload import render_upload_page

        render_upload_page()
    elif page == "Analysis Results":
        from src.components.results import render_results_page

        render_results_page()
    elif page == "Privacy & Security":
        from src.components.privacy import render_privacy_page

        render_privacy_page()


if __name__ == "__main__":
    main()
