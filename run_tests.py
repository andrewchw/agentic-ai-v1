#!/usr/bin/env python3
"""
Test runner for Agentic AI Revenue Assistant
Runs different types of tests based on command line arguments
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_unit_tests():
    """Run unit tests using pytest"""
    print("🧪 Running unit tests...")
    cmd = ["python", "-m", "pytest", "tests/test_app.py", "-v", "-m", "not e2e"]
    return subprocess.run(cmd).returncode

def run_e2e_tests():
    """Run end-to-end tests with Playwright"""
    print("🌐 Running end-to-end tests...")
    
    # Install Playwright browsers if needed
    print("📦 Installing Playwright browsers...")
    subprocess.run(["python", "-m", "playwright", "install"])
    
    # Run E2E tests
    cmd = ["python", "-m", "pytest", "tests/test_playwright.py", "-v", "-m", "e2e"]
    return subprocess.run(cmd).returncode

def run_all_tests():
    """Run all tests"""
    print("🔄 Running complete test suite...")
    
    # Run unit tests first
    unit_result = run_unit_tests()
    if unit_result != 0:
        print("❌ Unit tests failed!")
        return unit_result
    
    print("✅ Unit tests passed!")
    
    # Run E2E tests
    e2e_result = run_e2e_tests()
    if e2e_result != 0:
        print("❌ E2E tests failed!")
        return e2e_result
    
    print("✅ All tests passed!")
    return 0

def check_app_runs():
    """Quick check that the app can start without errors"""
    print("🚀 Testing app startup...")
    
    # Try to import and run basic checks
    try:
        import sys
        from pathlib import Path
        
        # Add project root to path
        PROJECT_ROOT = Path(__file__).parent
        sys.path.append(str(PROJECT_ROOT))
        
        # Test imports
        from config.app_config import config
        from src.components.layout import setup_page_config
        from src.components.home import render_home_page
        from src.utils.logger import setup_logging
        
        print("✅ All imports successful")
        
        # Test configuration
        config.setup_directories()
        print("✅ Configuration and directories setup successful")
        
        return 0
        
    except Exception as e:
        print(f"❌ App startup test failed: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Test runner for Agentic AI Revenue Assistant")
    parser.add_argument(
        "test_type", 
        choices=["unit", "e2e", "all", "check"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage reporting"
    )
    
    args = parser.parse_args()
    
    if args.test_type == "check":
        return check_app_runs()
    elif args.test_type == "unit":
        return run_unit_tests()
    elif args.test_type == "e2e":
        return run_e2e_tests()
    elif args.test_type == "all":
        return run_all_tests()

if __name__ == "__main__":
    sys.exit(main()) 