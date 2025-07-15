"""
Playwright end-to-end tests for Agentic AI Revenue Assistant
Tests the full user experience in a real browser
"""

import pytest
import subprocess
import time
import re
from playwright.sync_api import Page, expect

# Test configuration
TEST_PORT = 8502  # Use same port as test completion script
BASE_URL = f"http://localhost:{TEST_PORT}"

# Global variable to store the Streamlit process
streamlit_process = None


@pytest.fixture(scope="session")
def streamlit_server():
    """Start Streamlit server for testing"""

    # Start the Streamlit server
    process = subprocess.Popen(
        ["streamlit", "run", "src/main.py", f"--server.port={TEST_PORT}", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(8)

    yield process

    # Clean up
    process.terminate()
    process.wait()


@pytest.fixture
def page_with_server(page: Page, streamlit_server):
    """Page fixture with server running"""
    # Navigate to the Streamlit app
    page.goto(BASE_URL)
    return page


class TestUserInterface:
    """Test the user interface and user experience"""

    def test_app_loads_and_displays_title(self, page_with_server: Page):
        """Test that the app loads and shows the correct title"""
        page = page_with_server

        # Wait for app to load
        page.wait_for_load_state("networkidle")

        # Check that the page title contains our app name
        expect(page).to_have_title(re.compile(r"Agentic AI Revenue Assistant"))

        # Check for main heading in sidebar (where app name is displayed)
        expect(page.locator("h3")).to_contain_text("Agentic AI Revenue Assistant")

    def test_navigation_between_pages(self, page_with_server: Page):
        """Test navigation between different pages"""
        page = page_with_server

        # Wait for app to load
        page.wait_for_load_state("networkidle")

        # Find the navigation selectbox in sidebar
        nav_selectbox = page.locator('div[data-testid="stSelectbox"]').first

        # Test navigation to Upload Data page
        nav_selectbox.click()
        page.locator('div[data-testid="stSelectboxVirtualDropdown"]').locator(
            'text="Upload Data"'
        ).click()

        # Wait for page to update and check content
        page.wait_for_timeout(1000)
        expect(page.get_by_text("📂 Upload Customer Data")).to_be_visible()

        # Navigate back to Home
        nav_selectbox.click()
        page.locator('div[data-testid="stSelectboxVirtualDropdown"]').locator('text="Home"').click()
        page.wait_for_timeout(1000)
        expect(page.get_by_text("Welcome to the Agentic AI Revenue Assistant")).to_be_visible()

    def test_sidebar_system_status(self, page_with_server: Page):
        """Test sidebar system status indicators"""
        page = page_with_server

        # Check sidebar contains system status
        sidebar = page.locator('section[data-testid="stSidebar"]')
        expect(sidebar).to_contain_text("System Status")

        # Should show API connection status
        expect(sidebar).to_contain_text("OpenRouter API")
        expect(sidebar).to_contain_text("Encryption")

    def test_three_hk_branding_colors(self, page_with_server: Page):
        """Test that Three HK branding colors are applied"""
        page = page_with_server

        # Check for green color in styling (Three HK primary color)
        # This is a basic test - more sophisticated color testing could be added
        page_content = page.content()

        # Should contain Three HK color references
        assert "#00FF00" in page_content or "rgb(0, 255, 0)" in page_content

    def test_home_page_content_and_metrics(self, page_with_server: Page):
        """Test home page displays correct content and metrics"""
        page = page_with_server

        # Ensure we're on home page
        nav_selectbox = page.locator('div[data-testid="stSelectbox"]').first
        nav_selectbox.click()
        page.locator('text="Home"').click()
        page.wait_for_load_state("networkidle")

        # Check for key features section
        expect(page.locator("main")).to_contain_text("What This Tool Does")
        expect(page.locator("main")).to_contain_text("Privacy & Security")
        expect(page.locator("main")).to_contain_text("Getting Started")

        # Check for metrics display
        expect(page.locator("main")).to_contain_text("Max Records Supported")
        expect(page.locator("main")).to_contain_text("Privacy Status")
        expect(page.locator("main")).to_contain_text("AI Model")

    def test_upload_page_placeholder_functionality(self, page_with_server: Page):
        """Test upload page shows appropriate placeholders"""
        page = page_with_server

        # Navigate to upload page
        nav_selectbox = page.locator('div[data-testid="stSelectbox"]').first
        nav_selectbox.click()
        page.locator('text="Upload Data"').click()
        page.wait_for_load_state("networkidle")

        # Check for upload components (disabled)
        expect(page.locator("main")).to_contain_text("Customer Profile Data")
        expect(page.locator("main")).to_contain_text("Purchase History Data")

        # Should show Task 3 implementation notice
        expect(page.locator("main")).to_contain_text("Task 3")

        # Check for privacy notice
        expect(page.locator("main")).to_contain_text("Privacy Notice")

    def test_results_page_placeholder_content(self, page_with_server: Page):
        """Test results page shows mock data and future features"""
        page = page_with_server

        # Navigate to results page
        nav_selectbox = page.locator('div[data-testid="stSelectbox"]').first
        nav_selectbox.click()
        page.locator('text="Analysis Results"').click()
        page.wait_for_load_state("networkidle")

        # Check for results structure
        expect(page.locator("main")).to_contain_text("Lead Analysis Summary")
        expect(page.locator("main")).to_contain_text("Prioritized Lead Recommendations")

        # Check for Three HK offers section
        expect(page.locator("main")).to_contain_text("Three HK Offer Categories")
        expect(page.locator("main")).to_contain_text("Device Upgrade Offers")
        expect(page.locator("main")).to_contain_text("5G Plan Upsells")

    def test_privacy_page_compliance_content(self, page_with_server: Page):
        """Test privacy page shows comprehensive compliance information"""
        page = page_with_server

        # Navigate to privacy page
        nav_selectbox = page.locator('div[data-testid="stSelectbox"]').first
        nav_selectbox.click()
        page.locator('text="Privacy & Security"').click()
        page.wait_for_load_state("networkidle")

        # Check for privacy principles
        expect(page.locator("main")).to_contain_text("Privacy-First Commitment")
        expect(page.locator("main")).to_contain_text("Immediate Pseudonymization")
        expect(page.locator("main")).to_contain_text("No Raw PII to AI Services")

        # Check for compliance sections
        expect(page.locator("main")).to_contain_text("GDPR")
        expect(page.locator("main")).to_contain_text("Hong Kong PDPO")

        # Check for technical implementation details
        expect(page.locator("main")).to_contain_text("Technical Implementation")
        expect(page.locator("main")).to_contain_text("Pseudonymization Process")

    def test_responsive_design_basics(self, page_with_server: Page):
        """Test basic responsive design functionality"""
        page = page_with_server

        # Test different viewport sizes
        viewport_sizes = [(1920, 1080), (768, 1024), (375, 667)]  # Desktop  # Tablet  # Mobile

        for width, height in viewport_sizes:
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_load_state("networkidle")

            # Basic check that content is still visible
            expect(page.locator("h1")).to_be_visible()
            expect(page.locator('section[data-testid="stSidebar"]')).to_be_visible()

    def test_error_handling_graceful(self, page_with_server: Page):
        """Test that the app handles errors gracefully"""
        page = page_with_server

        # Check that no visible errors are displayed on any page
        pages_to_check = ["Home", "Upload Data", "Analysis Results", "Privacy & Security"]

        nav_selectbox = page.locator('div[data-testid="stSelectbox"]').first

        for page_name in pages_to_check:
            nav_selectbox.click()
            page.locator(f'text="{page_name}"').click()
            page.wait_for_load_state("networkidle")

            # Should not show Streamlit error messages
            error_indicators = ["Traceback", "Error", "Exception", "KeyError", "AttributeError"]

            page_content = page.content()
            for error_indicator in error_indicators:
                assert (
                    error_indicator not in page_content
                ), f"Found error indicator '{error_indicator}' on {page_name} page"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
