#!/usr/bin/env python3
"""
Quick Test Validation Script
Validates that our testing infrastructure is properly set up
"""

import os
import sys
from pathlib import Path

def check_testing_infrastructure():
    """Check if our testing infrastructure is properly set up"""
    print("🔍 Checking testing infrastructure...")
    print("=" * 50)
    
    project_root = Path.cwd()
    checks = []
    
    # Check essential test files
    test_files = [
        "tests/test_app.py",
        "tests/test_playwright.py", 
        "tests/task_completion_tests.py",
        "test_and_complete_task.py"
    ]
    
    for file_path in test_files:
        exists = (project_root / file_path).exists()
        status = "✅" if exists else "❌"
        checks.append((file_path, exists))
        print(f"{status} {file_path}")
    
    # Check if main app files exist
    app_files = [
        "src/main.py",
        "src/config/app_config.py",
        "src/components/layout.py",
        "src/pages/home.py"
    ]
    
    print(f"\n📱 Checking main app files...")
    for file_path in app_files:
        exists = (project_root / file_path).exists()
        status = "✅" if exists else "❌"
        checks.append((file_path, exists))
        print(f"{status} {file_path}")
    
    # Check requirements.txt
    requirements_exists = (project_root / "requirements.txt").exists()
    status = "✅" if requirements_exists else "❌"
    checks.append(("requirements.txt", requirements_exists))
    print(f"\n📦 {status} requirements.txt")
    
    # Summary
    all_files_exist = all(exists for _, exists in checks)
    
    print(f"\n" + "=" * 50)
    if all_files_exist:
        print("✅ Testing infrastructure is properly set up!")
        print("🎯 Ready to run task completion tests")
    else:
        print("❌ Some files are missing")
        missing = [path for path, exists in checks if not exists]
        print(f"Missing files: {', '.join(missing)}")
    
    print("=" * 50)
    return all_files_exist

def main():
    """Run the infrastructure check"""
    print("🚀 Agentic AI Revenue Assistant - Test Infrastructure Check")
    print()
    
    success = check_testing_infrastructure()
    
    if success:
        print("\n📋 NEXT STEPS:")
        print("1. Switch to Windows PowerShell")
        print("2. Navigate to project directory")
        print("3. Activate virtual environment: .\\venv\\Scripts\\Activate.ps1")
        print("4. Install Playwright browsers: python -m playwright install")
        print("5. Run task completion tests: python test_and_complete_task.py <task_id>")
        print("\n💡 Example usage:")
        print("   python test_and_complete_task.py 1")
        print("   python test_and_complete_task.py 2")
    else:
        print("\n🔧 Please ensure all required files are present before testing")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 