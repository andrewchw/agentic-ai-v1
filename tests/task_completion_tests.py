"""
Task Completion Test Runner
Validates that each completed task works properly before marking as done
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional


class TaskCompletionTester:
    """Test runner for validating task completion"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.streamlit_process = None
        self.test_results = {}

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests using pytest"""
        print("🧪 Running unit tests...")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/test_app.py", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),  # Convert Path to string
            )

            success = result.returncode == 0
            return {
                "success": success,
                "output": result.stdout,
                "errors": result.stderr,
                "test_type": "unit_tests",
            }
        except Exception as e:
            return {"success": False, "output": "", "errors": str(e), "test_type": "unit_tests"}

    def start_streamlit_for_testing(self) -> bool:
        """Start Streamlit server for e2e testing"""
        print("🚀 Starting Streamlit server...")

        try:
            # Use a different port for testing to avoid conflicts
            test_port = 8502
            self.streamlit_process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    "src/main.py",
                    f"--server.port={test_port}",
                    "--server.headless=true",
                    "--server.runOnSave=false",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.project_root),  # Convert Path to string
            )

            # Wait for server to start
            time.sleep(8)

            # Check if process is still running
            if self.streamlit_process.poll() is not None:
                # Get error output if available
                stdout, stderr = self.streamlit_process.communicate()
                print("❌ Streamlit failed to start")
                if stderr:
                    print(f"Error: {stderr.decode()}")
                return False

            print(f"✅ Streamlit server started successfully on port {test_port}")
            return True

        except Exception as e:
            print(f"❌ Error starting Streamlit: {e}")
            return False

    def run_playwright_tests(self) -> Dict[str, Any]:
        """Run Playwright e2e tests"""
        print("🎭 Running Playwright e2e tests...")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/test_playwright.py", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
            )

            success = result.returncode == 0
            return {
                "success": success,
                "output": result.stdout,
                "errors": result.stderr,
                "test_type": "playwright_e2e",
            }
        except Exception as e:
            return {"success": False, "output": "", "errors": str(e), "test_type": "playwright_e2e"}

    def stop_streamlit(self):
        """Stop the Streamlit server"""
        if self.streamlit_process:
            print("🛑 Stopping Streamlit server...")
            self.streamlit_process.terminate()
            self.streamlit_process.wait()
            self.streamlit_process = None

    def validate_task_specific_functionality(self, task_id: str) -> Dict[str, Any]:
        """Run task-specific validation tests"""
        print(f"🎯 Running task-specific tests for Task {task_id}...")

        # Task-specific test mappings
        task_tests = {
            "1": self._test_task_1_project_setup,
            "2": self._test_task_2_basic_ui,
            "3": self._test_task_3_csv_upload,
            "4": self._test_task_4_data_processing,
            "5": self._test_task_5_privacy_engine,
            # Add more as tasks are completed
        }

        test_function = task_tests.get(task_id)
        if not test_function:
            return {
                "success": True,
                "message": f"No specific tests defined for Task {task_id}",
                "test_type": "task_specific",
            }

        try:
            return test_function()
        except Exception as e:
            return {
                "success": False,
                "message": f"Task {task_id} validation failed: {str(e)}",
                "test_type": "task_specific",
            }

    def _test_task_1_project_setup(self) -> Dict[str, Any]:
        """Validate Task 1: Project Setup and Environment Configuration"""
        checks = []

        # Check essential files exist
        required_files = [
            "src/main.py",
            "src/config/app_config.py",
            "src/utils/logging_util.py",
            "src/components/layout.py",
            "src/pages/home.py",
            "requirements.txt",
            ".env.example",
            "README.md",
        ]

        for file_path in required_files:
            exists = (self.project_root / file_path).exists()
            checks.append(f"✅ {file_path}" if exists else f"❌ {file_path}")

        # Check if virtual environment was created
        venv_exists = (self.project_root / "venv").exists()
        checks.append("✅ Virtual environment" if venv_exists else "❌ Virtual environment")

        all_passed = all("✅" in check for check in checks)

        return {
            "success": all_passed,
            "message": f"Task 1 validation: {', '.join(checks)}",
            "test_type": "task_specific",
        }

    def _test_task_2_basic_ui(self) -> Dict[str, Any]:
        """Validate Task 2: Basic Streamlit UI Setup"""
        checks = []

        # Check component files exist (we use component-based architecture)
        component_files = [
            "src/components/upload.py",
            "src/components/results.py",
            "src/components/privacy.py",
            "src/components/home.py",
            "src/components/layout.py",
        ]

        for file_path in component_files:
            exists = (self.project_root / file_path).exists()
            checks.append(f"✅ {file_path}" if exists else f"❌ {file_path}")

        # Check main application file
        main_file = "src/main.py"
        main_exists = (self.project_root / main_file).exists()
        checks.append(f"✅ {main_file}" if main_exists else f"❌ {main_file}")

        # Check configuration files
        config_file = "config/app_config.py"
        config_exists = (self.project_root / config_file).exists()
        checks.append(f"✅ {config_file}" if config_exists else f"❌ {config_file}")

        # Check if Streamlit can start (basic smoke test)
        streamlit_starts = (
            self.streamlit_process is not None and self.streamlit_process.poll() is None
        )
        checks.append(
            "✅ Streamlit starts successfully"
            if streamlit_starts
            else "❌ Streamlit failed to start"
        )

        all_passed = all("✅" in check for check in checks)

        return {
            "success": all_passed,
            "message": f"Task 2 validation: {', '.join(checks)}",
            "test_type": "task_specific",
        }

    def _test_task_3_csv_upload(self) -> Dict[str, Any]:
        """Validate Task 3: CSV File Upload Component"""
        # This will be implemented when Task 3 is complete
        return {
            "success": True,
            "message": "Task 3 validation pending implementation",
            "test_type": "task_specific",
        }

    def _test_task_4_data_processing(self) -> Dict[str, Any]:
        """Validate Task 4: Data Processing and Validation"""
        # This will be implemented when Task 4 is complete
        return {
            "success": True,
            "message": "Task 4 validation pending implementation",
            "test_type": "task_specific",
        }

    def _test_task_5_privacy_engine(self) -> Dict[str, Any]:
        """Validate Task 5: Privacy Engine Implementation"""
        # This will be implemented when Task 5 is complete
        return {
            "success": True,
            "message": "Task 5 validation pending implementation",
            "test_type": "task_specific",
        }

    def run_full_test_suite(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Run complete test suite for task completion validation"""
        print(f"🚀 Starting task completion validation for Task {task_id or 'Unknown'}...")
        print("=" * 60)

        results = {"task_id": task_id, "overall_success": False, "tests_run": [], "summary": {}}

        try:
            # 1. Run unit tests
            unit_results = self.run_unit_tests()
            results["tests_run"].append(unit_results)
            results["summary"]["unit_tests"] = (
                "✅ PASSED" if unit_results["success"] else "❌ FAILED"
            )

            # 2. Start Streamlit for e2e tests
            streamlit_started = self.start_streamlit_for_testing()
            if not streamlit_started:
                results["summary"]["streamlit_startup"] = "❌ FAILED"
                return results

            results["summary"]["streamlit_startup"] = "✅ PASSED"

            # 3. Run Playwright tests
            playwright_results = self.run_playwright_tests()
            results["tests_run"].append(playwright_results)
            results["summary"]["playwright_e2e"] = (
                "✅ PASSED" if playwright_results["success"] else "❌ FAILED"
            )

            # 4. Run task-specific tests
            if task_id:
                task_results = self.validate_task_specific_functionality(task_id)
                results["tests_run"].append(task_results)
                results["summary"]["task_specific"] = (
                    "✅ PASSED" if task_results["success"] else "❌ FAILED"
                )

            # Overall success if all tests pass
            all_tests_passed = all(test["success"] for test in results["tests_run"])
            results["overall_success"] = all_tests_passed and streamlit_started

        finally:
            # Always clean up
            self.stop_streamlit()

        return results

    def print_test_summary(self, results: Dict[str, Any]):
        """Print a formatted test summary"""
        print("\n" + "=" * 60)
        print(f"📊 TASK COMPLETION TEST SUMMARY - Task {results.get('task_id', 'Unknown')}")
        print("=" * 60)

        for test_name, status in results["summary"].items():
            print(f"{test_name.replace('_', ' ').title()}: {status}")

        overall_status = (
            "✅ TASK READY FOR COMPLETION" if results["overall_success"] else "❌ TASK NEEDS FIXES"
        )
        print(f"\n🎯 Overall Result: {overall_status}")

        if not results["overall_success"]:
            print("\n🔍 Issues found:")
            for test in results["tests_run"]:
                if not test["success"] and test.get("errors"):
                    print(f"   - {test['test_type']}: {test['errors'][:200]}...")

        print("=" * 60)


def main():
    """CLI entry point for task completion testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Test task completion before marking as done")
    parser.add_argument("--task-id", required=True, help="Task ID to validate")
    parser.add_argument("--project-root", help="Project root directory")

    args = parser.parse_args()

    tester = TaskCompletionTester(args.project_root)
    results = tester.run_full_test_suite(args.task_id)
    tester.print_test_summary(results)

    # Exit with error code if tests failed
    sys.exit(0 if results["overall_success"] else 1)


if __name__ == "__main__":
    main()
