#!/usr/bin/env python3
"""
Test and Complete Task Script
Runs comprehensive tests before marking a task as complete in Task Master
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.task_completion_tests import TaskCompletionTester

def test_and_complete_task(task_id: str) -> bool:
    """
    Run comprehensive tests for a task and mark as complete if all pass
    
    Args:
        task_id: The Task Master task ID to test and complete
        
    Returns:
        bool: True if tests passed and task was marked complete, False otherwise
    """
    print(f"🎯 Testing Task {task_id} before marking as complete...")
    
    # Run the comprehensive test suite
    tester = TaskCompletionTester(str(project_root))
    results = tester.run_full_test_suite(task_id)
    tester.print_test_summary(results)
    
    if results["overall_success"]:
        print(f"\n✅ All tests passed! Task {task_id} is ready for completion.")
        print("📝 You can now mark this task as 'done' in Task Master.")
        return True
    else:
        print(f"\n❌ Tests failed! Task {task_id} needs fixes before completion.")
        print("🔧 Please address the issues and run tests again.")
        return False

def main():
    """CLI entry point"""
    if len(sys.argv) != 2:
        print("Usage: python test_and_complete_task.py <task_id>")
        print("Example: python test_and_complete_task.py 3")
        sys.exit(1)
    
    task_id = sys.argv[1]
    success = test_and_complete_task(task_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 