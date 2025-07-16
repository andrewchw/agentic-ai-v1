"""
Integration Test Runner - Task 16 
Automated runner for comprehensive integration testing and demo data pipeline validation

This runner orchestrates:
1. Demo data validation and loading
2. End-to-end workflow testing
3. Performance benchmarking
4. Privacy compliance validation  
5. Detailed reporting and metrics

Usage:
    python tests/test_integration_runner.py
    python tests/test_integration_runner.py --performance-only
    python tests/test_integration_runner.py --compliance-only
"""

import argparse
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import test modules
import pytest
from tests.test_comprehensive_integration import (
    TestEndToEndWorkflow, 
    TestPerformanceIntegration, 
    TestComplianceIntegration
)

# Import demo data utilities
import pandas as pd
from src.components.upload import process_data_through_privacy_pipeline
from src.utils.data_merging import DataMerger, MergeStrategy


class IntegrationTestRunner:
    """Comprehensive integration test runner with reporting"""

    def __init__(self, output_dir: str = "tests/integration_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_results = {
            "run_timestamp": datetime.now().isoformat(),
            "environment": self._get_environment_info(),
            "demo_data_validation": {},
            "end_to_end_tests": {},
            "performance_tests": {},
            "compliance_tests": {},
            "summary": {}
        }
        
        # Demo data paths
        self.demo_customer_path = "data/demo/demo_customer_data_comprehensive.csv"
        self.demo_purchase_path = "data/demo/demo_purchase_data_comprehensive.csv"

    def _get_environment_info(self) -> Dict[str, Any]:
        """Collect environment information for testing context"""
        import platform
        import subprocess
        
        try:
            git_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            git_hash = "unknown"
        
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "git_commit": git_hash,
            "working_directory": str(Path.cwd()),
            "test_runner_version": "1.0.0"
        }

    def validate_demo_data(self) -> bool:
        """Validate demo data files and report on their characteristics"""
        print("📊 Validating demo data files...")
        
        validation_results = {
            "customer_data": {},
            "purchase_data": {},
            "validation_passed": True
        }
        
        try:
            # Load and validate customer data
            if Path(self.demo_customer_path).exists():
                customer_df = pd.read_csv(self.demo_customer_path)
                validation_results["customer_data"] = {
                    "file_exists": True,
                    "record_count": len(customer_df),
                    "column_count": len(customer_df.columns),
                    "columns": customer_df.columns.tolist(),
                    "pii_fields_present": self._identify_pii_fields(customer_df),
                    "data_quality": self._assess_data_quality(customer_df, "customer")
                }
                print(f"  ✅ Customer data: {len(customer_df)} records, {len(customer_df.columns)} columns")
            else:
                validation_results["customer_data"]["file_exists"] = False
                validation_results["validation_passed"] = False
                print(f"  ❌ Customer data file not found: {self.demo_customer_path}")
            
            # Load and validate purchase data
            if Path(self.demo_purchase_path).exists():
                purchase_df = pd.read_csv(self.demo_purchase_path)
                validation_results["purchase_data"] = {
                    "file_exists": True,
                    "record_count": len(purchase_df),
                    "column_count": len(purchase_df.columns),
                    "columns": purchase_df.columns.tolist(),
                    "pii_fields_present": self._identify_pii_fields(purchase_df),
                    "data_quality": self._assess_data_quality(purchase_df, "purchase"),
                    "account_overlap": self._calculate_account_overlap(customer_df, purchase_df)
                }
                print(f"  ✅ Purchase data: {len(purchase_df)} records, {len(purchase_df.columns)} columns")
            else:
                validation_results["purchase_data"]["file_exists"] = False
                validation_results["validation_passed"] = False
                print(f"  ❌ Purchase data file not found: {self.demo_purchase_path}")
                
        except Exception as e:
            validation_results["validation_passed"] = False
            validation_results["error"] = str(e)
            print(f"  ❌ Demo data validation error: {e}")
        
        self.test_results["demo_data_validation"] = validation_results
        return validation_results["validation_passed"]

    def _identify_pii_fields(self, df: pd.DataFrame) -> List[str]:
        """Identify potential PII fields in the dataframe"""
        pii_indicators = [
            "name", "email", "phone", "id", "account", "address", 
            "birth", "hkid", "chinese", "given", "family"
        ]
        
        pii_fields = []
        for column in df.columns:
            column_lower = column.lower()
            if any(indicator in column_lower for indicator in pii_indicators):
                pii_fields.append(column)
        
        return pii_fields

    def _assess_data_quality(self, df: pd.DataFrame, data_type: str) -> Dict[str, Any]:
        """Assess data quality metrics"""
        return {
            "null_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            "duplicate_rows": df.duplicated().sum(),
            "empty_strings": (df == "").sum().sum(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
        }

    def _calculate_account_overlap(self, customer_df: pd.DataFrame, purchase_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Account ID overlap between datasets"""
        if "Account ID" not in customer_df.columns or "Account ID" not in purchase_df.columns:
            return {"error": "Account ID column not found"}
        
        customer_accounts = set(customer_df["Account ID"].unique())
        purchase_accounts = set(purchase_df["Account ID"].unique())
        
        overlap = customer_accounts.intersection(purchase_accounts)
        
        return {
            "customer_unique_accounts": len(customer_accounts),
            "purchase_unique_accounts": len(purchase_accounts),
            "overlapping_accounts": len(overlap),
            "customer_match_rate": len(overlap) / len(customer_accounts) * 100 if customer_accounts else 0,
            "purchase_match_rate": len(overlap) / len(purchase_accounts) * 100 if purchase_accounts else 0
        }

    def run_end_to_end_tests(self) -> bool:
        """Run comprehensive end-to-end workflow tests"""
        print("🔄 Running end-to-end workflow tests...")
        
        test_results = {
            "tests_run": [],
            "tests_passed": 0,
            "tests_failed": 0,
            "execution_time": 0,
            "detailed_results": []
        }
        
        start_time = time.time()
        
        try:
            # Run end-to-end tests using pytest
            test_instance = TestEndToEndWorkflow()
            test_instance.setup_method()
            
            # Test complete workflow
            try:
                test_instance.test_complete_upload_to_merge_workflow()
                test_results["tests_passed"] += 1
                test_results["detailed_results"].append({
                    "test": "complete_upload_to_merge_workflow",
                    "status": "PASSED",
                    "processing_times": getattr(test_instance, 'processing_times', {})
                })
                print("  ✅ Complete upload-to-merge workflow")
            except Exception as e:
                test_results["tests_failed"] += 1
                test_results["detailed_results"].append({
                    "test": "complete_upload_to_merge_workflow",
                    "status": "FAILED",
                    "error": str(e)
                })
                print(f"  ❌ Complete upload-to-merge workflow: {e}")
            
            # Test error handling
            try:
                test_instance.test_error_handling_and_edge_cases()
                test_results["tests_passed"] += 1
                test_results["detailed_results"].append({
                    "test": "error_handling_and_edge_cases",
                    "status": "PASSED"
                })
                print("  ✅ Error handling and edge cases")
            except Exception as e:
                test_results["tests_failed"] += 1
                test_results["detailed_results"].append({
                    "test": "error_handling_and_edge_cases", 
                    "status": "FAILED",
                    "error": str(e)
                })
                print(f"  ❌ Error handling and edge cases: {e}")
            
            # Test cross-merge strategy consistency
            try:
                test_instance.test_cross_merge_strategy_consistency()
                test_results["tests_passed"] += 1
                test_results["detailed_results"].append({
                    "test": "cross_merge_strategy_consistency",
                    "status": "PASSED"
                })
                print("  ✅ Cross-merge strategy consistency")
            except Exception as e:
                test_results["tests_failed"] += 1
                test_results["detailed_results"].append({
                    "test": "cross_merge_strategy_consistency",
                    "status": "FAILED", 
                    "error": str(e)
                })
                print(f"  ❌ Cross-merge strategy consistency: {e}")
            
            test_instance.teardown_method()
            
        except Exception as e:
            test_results["tests_failed"] += 1
            test_results["detailed_results"].append({
                "test": "test_setup",
                "status": "FAILED",
                "error": str(e)
            })
            print(f"  ❌ Test setup error: {e}")
        
        test_results["execution_time"] = time.time() - start_time
        test_results["success_rate"] = (
            test_results["tests_passed"] / 
            (test_results["tests_passed"] + test_results["tests_failed"]) * 100
            if (test_results["tests_passed"] + test_results["tests_failed"]) > 0 else 0
        )
        
        self.test_results["end_to_end_tests"] = test_results
        return test_results["tests_failed"] == 0

    def run_performance_tests(self) -> bool:
        """Run performance benchmarking tests"""
        print("🚀 Running performance tests...")
        
        test_results = {
            "tests_run": [],
            "tests_passed": 0,
            "tests_failed": 0,
            "execution_time": 0,
            "performance_metrics": {},
            "detailed_results": []
        }
        
        start_time = time.time()
        
        try:
            test_instance = TestPerformanceIntegration()
            test_instance.setup_method()
            
            # Test large dataset performance
            try:
                test_instance.test_large_dataset_performance()
                test_results["tests_passed"] += 1
                test_results["performance_metrics"].update(
                    getattr(test_instance, 'performance_metrics', {})
                )
                test_results["detailed_results"].append({
                    "test": "large_dataset_performance",
                    "status": "PASSED",
                    "metrics": getattr(test_instance, 'performance_metrics', {})
                })
                print("  ✅ Large dataset performance")
            except Exception as e:
                test_results["tests_failed"] += 1
                test_results["detailed_results"].append({
                    "test": "large_dataset_performance",
                    "status": "FAILED",
                    "error": str(e)
                })
                print(f"  ❌ Large dataset performance: {e}")
            
            # Test memory usage monitoring
            try:
                test_instance.test_memory_usage_monitoring()
                test_results["tests_passed"] += 1
                test_results["detailed_results"].append({
                    "test": "memory_usage_monitoring",
                    "status": "PASSED"
                })
                print("  ✅ Memory usage monitoring")
            except Exception as e:
                test_results["tests_failed"] += 1
                test_results["detailed_results"].append({
                    "test": "memory_usage_monitoring",
                    "status": "FAILED",
                    "error": str(e)
                })
                print(f"  ❌ Memory usage monitoring: {e}")
            
            test_instance.teardown_method()
            
        except Exception as e:
            test_results["tests_failed"] += 1
            test_results["detailed_results"].append({
                "test": "performance_setup",
                "status": "FAILED",
                "error": str(e)
            })
            print(f"  ❌ Performance test setup error: {e}")
        
        test_results["execution_time"] = time.time() - start_time
        test_results["success_rate"] = (
            test_results["tests_passed"] / 
            (test_results["tests_passed"] + test_results["tests_failed"]) * 100
            if (test_results["tests_passed"] + test_results["tests_failed"]) > 0 else 0
        )
        
        self.test_results["performance_tests"] = test_results
        return test_results["tests_failed"] == 0

    def run_compliance_tests(self) -> bool:
        """Run privacy and compliance validation tests"""
        print("🔒 Running compliance tests...")
        
        test_results = {
            "tests_run": [],
            "tests_passed": 0,
            "tests_failed": 0,
            "execution_time": 0,
            "detailed_results": []
        }
        
        start_time = time.time()
        
        try:
            test_instance = TestComplianceIntegration()
            
            # Test GDPR compliance
            try:
                test_instance.test_gdpr_compliance_workflow()
                test_results["tests_passed"] += 1
                test_results["detailed_results"].append({
                    "test": "gdpr_compliance_workflow",
                    "status": "PASSED"
                })
                print("  ✅ GDPR compliance workflow")
            except Exception as e:
                test_results["tests_failed"] += 1
                test_results["detailed_results"].append({
                    "test": "gdpr_compliance_workflow",
                    "status": "FAILED",
                    "error": str(e)
                })
                print(f"  ❌ GDPR compliance workflow: {e}")
            
            # Test Hong Kong PDPO compliance
            try:
                test_instance.test_hong_kong_pdpo_compliance()
                test_results["tests_passed"] += 1
                test_results["detailed_results"].append({
                    "test": "hong_kong_pdpo_compliance",
                    "status": "PASSED"
                })
                print("  ✅ Hong Kong PDPO compliance")
            except Exception as e:
                test_results["tests_failed"] += 1
                test_results["detailed_results"].append({
                    "test": "hong_kong_pdpo_compliance",
                    "status": "FAILED",
                    "error": str(e)
                })
                print(f"  ❌ Hong Kong PDPO compliance: {e}")
                
        except Exception as e:
            test_results["tests_failed"] += 1
            test_results["detailed_results"].append({
                "test": "compliance_setup",
                "status": "FAILED",
                "error": str(e)
            })
            print(f"  ❌ Compliance test setup error: {e}")
        
        test_results["execution_time"] = time.time() - start_time
        test_results["success_rate"] = (
            test_results["tests_passed"] / 
            (test_results["tests_passed"] + test_results["tests_failed"]) * 100
            if (test_results["tests_passed"] + test_results["tests_failed"]) > 0 else 0
        )
        
        self.test_results["compliance_tests"] = test_results
        return test_results["tests_failed"] == 0

    def test_demo_data_integration(self) -> bool:
        """Test integration with actual demo data files"""
        print("📋 Testing demo data integration...")
        
        if not Path(self.demo_customer_path).exists() or not Path(self.demo_purchase_path).exists():
            print("  ❌ Demo data files not found, skipping integration test")
            return False
        
        try:
            # Load demo data
            customer_df = pd.read_csv(self.demo_customer_path)
            purchase_df = pd.read_csv(self.demo_purchase_path)
            
            print(f"  📊 Testing with {len(customer_df)} customers, {len(purchase_df)} purchases")
            
            # Process through privacy pipeline
            customer_start = time.time()
            customer_success, customer_message, customer_processed = process_data_through_privacy_pipeline(
                customer_df, "demo_customer", "demo_customer.csv"
            )
            customer_time = time.time() - customer_start
            
            purchase_start = time.time()
            purchase_success, purchase_message, purchase_processed = process_data_through_privacy_pipeline(
                purchase_df, "demo_purchase", "demo_purchase.csv"
            )
            purchase_time = time.time() - purchase_start
            
            if not (customer_success and purchase_success):
                print(f"  ❌ Privacy processing failed: {customer_message}, {purchase_message}")
                return False
            
            # Test data merging
            merger = DataMerger()
            merge_start = time.time()
            merge_result = merger.merge_datasets(
                customer_processed, purchase_processed,
                strategy=MergeStrategy.LEFT, show_sensitive=False
            )
            merge_time = time.time() - merge_start
            
            if not merge_result.success:
                print(f"  ❌ Data merging failed: {merge_result.message}")
                return False
            
            # Report results
            merged_count = len(merge_result.merged_data) if merge_result.merged_data is not None else 0
            
            demo_results = {
                "customer_processing_time": customer_time,
                "purchase_processing_time": purchase_time,
                "merge_time": merge_time,
                "total_time": customer_time + purchase_time + merge_time,
                "merged_record_count": merged_count,
                "input_customer_count": len(customer_df),
                "input_purchase_count": len(purchase_df)
            }
            
            self.test_results["demo_data_integration"] = demo_results
            
            print(f"  ✅ Demo data integration successful:")
            print(f"    - Customer processing: {customer_time:.3f}s")
            print(f"    - Purchase processing: {purchase_time:.3f}s") 
            print(f"    - Data merging: {merge_time:.3f}s")
            print(f"    - Total time: {demo_results['total_time']:.3f}s")
            print(f"    - Records merged: {merged_count}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Demo data integration error: {e}")
            return False

    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        print("📊 Generating comprehensive test report...")
        
        # Calculate overall summary
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for test_category in ["end_to_end_tests", "performance_tests", "compliance_tests"]:
            if test_category in self.test_results:
                results = self.test_results[test_category]
                total_tests += results.get("tests_passed", 0) + results.get("tests_failed", 0)
                total_passed += results.get("tests_passed", 0)
                total_failed += results.get("tests_failed", 0)
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        self.test_results["summary"] = {
            "overall_success_rate": overall_success_rate,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "demo_data_valid": self.test_results.get("demo_data_validation", {}).get("validation_passed", False),
            "integration_successful": total_failed == 0
        }
        
        # Save detailed report
        report_path = self.output_dir / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        # Generate summary report
        summary_path = self.output_dir / "latest_integration_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("INTEGRATION TEST SUMMARY REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Run Timestamp: {self.test_results['run_timestamp']}\n")
            f.write(f"Environment: {self.test_results['environment']['platform']}\n")
            f.write(f"Python Version: {self.test_results['environment']['python_version']}\n")
            f.write(f"Git Commit: {self.test_results['environment']['git_commit']}\n\n")
            
            f.write("OVERALL RESULTS:\n")
            f.write(f"  Success Rate: {overall_success_rate:.1f}%\n")
            f.write(f"  Total Tests: {total_tests}\n")
            f.write(f"  Passed: {total_passed}\n")
            f.write(f"  Failed: {total_failed}\n\n")
            
            # Demo data validation
            demo_validation = self.test_results.get("demo_data_validation", {})
            f.write("DEMO DATA VALIDATION:\n")
            f.write(f"  Status: {'✅ PASSED' if demo_validation.get('validation_passed', False) else '❌ FAILED'}\n")
            if "customer_data" in demo_validation:
                customer = demo_validation["customer_data"]
                f.write(f"  Customer Records: {customer.get('record_count', 'N/A')}\n")
            if "purchase_data" in demo_validation:
                purchase = demo_validation["purchase_data"]
                f.write(f"  Purchase Records: {purchase.get('record_count', 'N/A')}\n")
            f.write("\n")
            
            # Test category results
            for category, title in [
                ("end_to_end_tests", "END-TO-END TESTS"),
                ("performance_tests", "PERFORMANCE TESTS"),
                ("compliance_tests", "COMPLIANCE TESTS")
            ]:
                if category in self.test_results:
                    results = self.test_results[category]
                    f.write(f"{title}:\n")
                    f.write(f"  Success Rate: {results.get('success_rate', 0):.1f}%\n")
                    f.write(f"  Execution Time: {results.get('execution_time', 0):.3f}s\n")
                    f.write(f"  Tests Passed: {results.get('tests_passed', 0)}\n")
                    f.write(f"  Tests Failed: {results.get('tests_failed', 0)}\n\n")
        
        print(f"  📄 Detailed report: {report_path}")
        print(f"  📋 Summary report: {summary_path}")
        
        return str(report_path)

    def run_all_tests(self, skip_performance: bool = False, skip_compliance: bool = False) -> bool:
        """Run all integration tests and generate report"""
        print("🚀 Starting comprehensive integration testing...")
        print("=" * 60)
        
        overall_success = True
        
        # Validate demo data
        if not self.validate_demo_data():
            print("⚠️  Demo data validation failed, but continuing with tests...")
        
        # Test demo data integration
        if not self.test_demo_data_integration():
            print("⚠️  Demo data integration failed, but continuing with tests...")
            overall_success = False
        
        # Run end-to-end tests
        if not self.run_end_to_end_tests():
            print("❌ End-to-end tests failed")
            overall_success = False
        
        # Run performance tests (optional)
        if not skip_performance:
            if not self.run_performance_tests():
                print("❌ Performance tests failed")
                overall_success = False
        else:
            print("⏭️  Skipping performance tests")
        
        # Run compliance tests (optional)
        if not skip_compliance:
            if not self.run_compliance_tests():
                print("❌ Compliance tests failed")
                overall_success = False
        else:
            print("⏭️  Skipping compliance tests")
        
        # Generate report
        report_path = self.generate_report()
        
        print("=" * 60)
        if overall_success:
            print("🎉 All integration tests PASSED!")
        else:
            print("❌ Some integration tests FAILED!")
        
        print(f"📊 Full report available: {report_path}")
        
        return overall_success


def main():
    """Main entry point for integration test runner"""
    parser = argparse.ArgumentParser(description="Run comprehensive integration tests")
    parser.add_argument("--performance-only", action="store_true", 
                       help="Run only performance tests")
    parser.add_argument("--compliance-only", action="store_true",
                       help="Run only compliance tests")
    parser.add_argument("--skip-performance", action="store_true",
                       help="Skip performance tests")
    parser.add_argument("--skip-compliance", action="store_true", 
                       help="Skip compliance tests")
    parser.add_argument("--output-dir", default="tests/integration_reports",
                       help="Output directory for reports")
    
    args = parser.parse_args()
    
    runner = IntegrationTestRunner(output_dir=args.output_dir)
    
    if args.performance_only:
        success = runner.run_performance_tests()
        runner.generate_report()
    elif args.compliance_only:
        success = runner.run_compliance_tests()
        runner.generate_report()
    else:
        success = runner.run_all_tests(
            skip_performance=args.skip_performance,
            skip_compliance=args.skip_compliance
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 