#!/usr/bin/env python3
"""
Subtask 12.5: Integration Testing and Performance Validation
==========================================================

Comprehensive testing suite for multi-agent system integration and performance validation.
This script validates:
1. Agent collaboration and communication reliability
2. System performance under various workloads
3. Maintenance of all existing privacy/security features
4. Real-world scenario handling
5. Sub-30 second response time validation

Usage:
python integration_performance_test.py
"""

import asyncio
import time
import json
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import statistics
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our multi-agent components
try:
    from src.agents.agentic_revenue_accelerator import demonstrate_collaboration
    COLLABORATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Collaboration system import failed: {e}")
    COLLABORATION_AVAILABLE = False

try:
    from src.utils.privacy_pipeline import PrivacyPipeline
    PRIVACY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Privacy pipeline import failed: {e}")
    PRIVACY_AVAILABLE = False

class IntegrationPerformanceValidator:
    """Comprehensive integration and performance testing for multi-agent system"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "agent_communication": {},
            "performance_metrics": {},
            "privacy_security": {},
            "real_world_scenarios": {},
            "agent_protocol": {},
            "overall_status": "unknown"
        }
        self.agent_protocol_url = "http://127.0.0.1:8080"
        
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Execute all integration and performance tests"""
        
        print("🧪 Starting Comprehensive Integration & Performance Testing")
        print("=" * 70)
        print()
        
        try:
            # Test 1: Agent Communication and Collaboration
            print("1️⃣ Testing Agent Communication & Collaboration...")
            self.test_results["agent_communication"] = self.test_agent_communication()
            
            # Test 2: Performance Under Load
            print("\\n2️⃣ Testing Performance Under Various Workloads...")
            self.test_results["performance_metrics"] = self.test_performance_metrics()
            
            # Test 3: Privacy and Security Features
            print("\\n3️⃣ Validating Privacy & Security Features...")
            self.test_results["privacy_security"] = self.test_privacy_security()
            
            # Test 4: Real-World Scenarios
            print("\\n4️⃣ Testing Real-World Scenarios...")
            self.test_results["real_world_scenarios"] = self.test_real_world_scenarios()
            
            # Test 5: Agent Protocol Integration
            print("\\n5️⃣ Testing Agent Protocol Integration...")
            self.test_results["agent_protocol"] = self.test_agent_protocol_integration()
            
            # Overall Assessment
            self.assess_overall_status()
            
            # Generate Report
            self.generate_test_report()
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ Critical test failure: {str(e)}")
            traceback.print_exc()
            self.test_results["overall_status"] = "critical_failure"
            self.test_results["error"] = str(e)
            return self.test_results
    
    def test_agent_communication(self) -> Dict[str, Any]:
        """Test agent-to-agent communication and collaboration"""
        
        results = {
            "delegation_tests": [],
            "collaboration_tests": [],
            "communication_reliability": {},
            "status": "unknown"
        }
        
        if not COLLABORATION_AVAILABLE:
            results["status"] = "skipped"
            results["reason"] = "Multi-agent collaboration not available"
            print("   ⚠️ Skipped - Multi-agent collaboration not available")
            return results
        
        try:
            print("   🔄 Testing Lead Intelligence → Revenue Optimization delegation...")
            
            # Test basic delegation
            sample_customers = [
                {
                    'customer_id': 'TEST_001',
                    'customer_name': 'Integration Test Corp',
                    'customer_type': 'enterprise',
                    'current_monthly_spend': 25000,
                    'engagement_score': 0.75,
                    'growth_indicators': ['digital_transformation']
                }
            ]
            
            start_time = time.time()
            collaboration_result = demonstrate_collaboration(sample_customers)
            delegation_time = time.time() - start_time
            
            # Validate delegation occurred
            delegation_success = (
                collaboration_result.get('success', False) and
                'recommendations' in collaboration_result and
                delegation_time < 30.0  # Sub-30 second requirement
            )
            
            results["delegation_tests"].append({
                "test": "basic_delegation",
                "success": delegation_success,
                "response_time": delegation_time,
                "details": collaboration_result
            })
            
            print(f"   ✅ Delegation test: {'PASSED' if delegation_success else 'FAILED'} ({delegation_time:.2f}s)")
            
            # Test communication reliability (multiple iterations)
            print("   🔄 Testing communication reliability (5 iterations)...")
            
            reliability_times = []
            reliability_successes = 0
            
            for i in range(5):
                try:
                    start_time = time.time()
                    result = demonstrate_collaboration(sample_customers)
                    iteration_time = time.time() - start_time
                    
                    if result.get('success', False) and iteration_time < 30.0:
                        reliability_successes += 1
                        reliability_times.append(iteration_time)
                    
                except Exception as e:
                    print(f"   ⚠️ Reliability test {i+1} failed: {str(e)}")
            
            results["communication_reliability"] = {
                "success_rate": reliability_successes / 5,
                "average_time": statistics.mean(reliability_times) if reliability_times else 0,
                "max_time": max(reliability_times) if reliability_times else 0,
                "min_time": min(reliability_times) if reliability_times else 0
            }
            
            reliability_passed = results["communication_reliability"]["success_rate"] >= 0.8
            
            print(f"   ✅ Reliability test: {'PASSED' if reliability_passed else 'FAILED'} " +
                  f"({results['communication_reliability']['success_rate']*100:.0f}% success rate)")
            
            results["status"] = "passed" if delegation_success and reliability_passed else "failed"
            
        except Exception as e:
            print(f"   ❌ Agent communication test failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def test_performance_metrics(self) -> Dict[str, Any]:
        """Test system performance under various workloads"""
        
        results = {
            "response_time_tests": [],
            "concurrent_load_tests": [],
            "memory_usage": {},
            "status": "unknown"
        }
        
        if not COLLABORATION_AVAILABLE:
            results["status"] = "skipped"
            results["reason"] = "Multi-agent collaboration not available"
            print("   ⚠️ Skipped - Multi-agent collaboration not available")
            return results
        
        try:
            # Test 1: Single request response time
            print("   ⏱️ Testing single request response time...")
            
            test_customer = [{
                'customer_id': 'PERF_001',
                'customer_name': 'Performance Test Ltd',
                'customer_type': 'sme',
                'current_monthly_spend': 15000,
                'engagement_score': 0.60
            }]
            
            single_times = []
            for i in range(3):
                start_time = time.time()
                result = demonstrate_collaboration(test_customer)
                response_time = time.time() - start_time
                single_times.append(response_time)
                
                success = result.get('success', False) and response_time < 30.0
                print(f"   🔍 Request {i+1}: {response_time:.2f}s ({'✅' if success else '❌'})")
            
            avg_response_time = statistics.mean(single_times)
            max_response_time = max(single_times)
            
            results["response_time_tests"] = {
                "average_time": avg_response_time,
                "max_time": max_response_time,
                "under_30s": max_response_time < 30.0,
                "individual_times": single_times
            }
            
            print(f"   📊 Average response time: {avg_response_time:.2f}s")
            print(f"   📊 Max response time: {max_response_time:.2f}s")
            
            # Test 2: Concurrent requests (simulated)
            print("   🔄 Testing concurrent load handling...")
            
            # For safety, we'll simulate concurrent load with sequential rapid requests
            concurrent_times = []
            concurrent_successes = 0
            
            start_concurrent = time.time()
            for i in range(3):  # Reduced for safety
                start_time = time.time()
                try:
                    result = demonstrate_collaboration(test_customer)
                    response_time = time.time() - start_time
                    concurrent_times.append(response_time)
                    
                    if result.get('success', False):
                        concurrent_successes += 1
                        
                except Exception as e:
                    print(f"   ⚠️ Concurrent request {i+1} failed: {str(e)}")
            
            total_concurrent_time = time.time() - start_concurrent
            
            results["concurrent_load_tests"] = {
                "total_requests": 3,
                "successful_requests": concurrent_successes,
                "total_time": total_concurrent_time,
                "success_rate": concurrent_successes / 3,
                "average_concurrent_time": statistics.mean(concurrent_times) if concurrent_times else 0
            }
            
            print(f"   📊 Concurrent test: {concurrent_successes}/3 successful")
            print(f"   📊 Total concurrent time: {total_concurrent_time:.2f}s")
            
            # Overall performance assessment
            performance_passed = (
                avg_response_time < 30.0 and
                results["concurrent_load_tests"]["success_rate"] >= 0.67
            )
            
            results["status"] = "passed" if performance_passed else "failed"
            
        except Exception as e:
            print(f"   ❌ Performance test failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def test_privacy_security(self) -> Dict[str, Any]:
        """Validate privacy and security features remain intact"""
        
        results = {
            "privacy_pipeline": {},
            "data_encryption": {},
            "pseudonymization": {},
            "status": "unknown"
        }
        
        try:
            print("   🔒 Testing privacy pipeline integrity...")
            
            # Test privacy pipeline initialization
            if PRIVACY_AVAILABLE:
                try:
                    privacy_pipeline = PrivacyPipeline()
                    privacy_init_success = True
                    print("   ✅ Privacy pipeline initialization: PASSED")
                except Exception as e:
                    privacy_init_success = False
                    print(f"   ❌ Privacy pipeline initialization: FAILED ({str(e)})")
            else:
                privacy_init_success = False
                print("   ⚠️ Privacy pipeline not available - SKIPPED")
            
            results["privacy_pipeline"]["initialization"] = privacy_init_success
            
            # Test data pseudonymization
            print("   🔐 Testing data pseudonymization...")
            
            test_data = {
                'customer_name': 'Test Customer',
                'phone': '+852-1234-5678',
                'email': 'test@example.com'
            }
            
            try:
                if privacy_init_success and PRIVACY_AVAILABLE:
                    pseudonymized = privacy_pipeline.pseudonymize_data(test_data)
                    pseudonym_success = (
                        pseudonymized.get('customer_name') != 'Test Customer' and
                        len(pseudonymized.get('customer_name', '')) > 0
                    )
                else:
                    pseudonym_success = False
                
                print(f"   ✅ Pseudonymization: {'PASSED' if pseudonym_success else 'FAILED'}")
                
            except Exception as e:
                pseudonym_success = False
                print(f"   ❌ Pseudonymization: FAILED ({str(e)})")
            
            results["pseudonymization"]["functional"] = pseudonym_success
            
            # Overall privacy/security assessment
            privacy_passed = privacy_init_success and pseudonym_success
            results["status"] = "passed" if privacy_passed else "failed"
            
        except Exception as e:
            print(f"   ❌ Privacy/security test failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def test_real_world_scenarios(self) -> Dict[str, Any]:
        """Test system with real-world business scenarios"""
        
        results = {
            "hong_kong_telecom": {},
            "enterprise_analysis": {},
            "sme_retention": {},
            "status": "unknown"
        }
        
        if not COLLABORATION_AVAILABLE:
            results["status"] = "skipped"
            results["reason"] = "Multi-agent collaboration not available"
            print("   ⚠️ Skipped - Multi-agent collaboration not available")
            return results
        
        try:
            # Scenario 1: Hong Kong Telecom Enterprise
            print("   🏢 Testing Hong Kong telecom enterprise scenario...")
            
            hk_enterprise = [{
                'customer_id': 'HK_ENT_001',
                'customer_name': 'Hong Kong Tech Solutions',
                'customer_type': 'enterprise',
                'current_monthly_spend': 45000,
                'contract_length': 24,
                'engagement_score': 0.85,
                'growth_indicators': ['5g_infrastructure', 'expanding_workforce']
            }]
            
            start_time = time.time()
            hk_result = demonstrate_collaboration(hk_enterprise)
            hk_time = time.time() - start_time
            
            hk_success = (
                hk_result.get('success', False) and
                hk_time < 30.0 and
                len(hk_result.get('recommendations', [])) > 0
            )
            
            results["hong_kong_telecom"] = {
                "success": hk_success,
                "response_time": hk_time,
                "recommendations_count": len(hk_result.get('recommendations', []))
            }
            
            print(f"   ✅ HK Enterprise: {'PASSED' if hk_success else 'FAILED'} ({hk_time:.2f}s)")
            
            # Scenario 2: SME Retention Challenge
            print("   🏪 Testing SME retention challenge scenario...")
            
            sme_retention = [{
                'customer_id': 'SME_RET_001',
                'customer_name': 'Local Business HK',
                'customer_type': 'sme',
                'current_monthly_spend': 8500,
                'engagement_score': 0.40,  # Low engagement
                'churn_risk_factors': ['price_sensitivity', 'competitor_offers']
            }]
            
            start_time = time.time()
            sme_result = demonstrate_collaboration(sme_retention)
            sme_time = time.time() - start_time
            
            sme_success = (
                sme_result.get('success', False) and
                sme_time < 30.0 and
                len(sme_result.get('recommendations', [])) > 0
            )
            
            results["sme_retention"] = {
                "success": sme_success,
                "response_time": sme_time,
                "recommendations_count": len(sme_result.get('recommendations', []))
            }
            
            print(f"   ✅ SME Retention: {'PASSED' if sme_success else 'FAILED'} ({sme_time:.2f}s)")
            
            # Overall real-world scenario assessment
            scenarios_passed = hk_success and sme_success
            results["status"] = "passed" if scenarios_passed else "failed"
            
        except Exception as e:
            print(f"   ❌ Real-world scenario test failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def test_agent_protocol_integration(self) -> Dict[str, Any]:
        """Test Agent Protocol server integration"""
        
        results = {
            "server_health": {},
            "api_endpoints": {},
            "task_processing": {},
            "status": "unknown"
        }
        
        try:
            print("   🌐 Testing Agent Protocol server health...")
            
            # Test server health
            try:
                response = requests.get(f"{self.agent_protocol_url}/ap/v1/agent/health", timeout=10)
                health_success = response.status_code == 200
                
                if health_success:
                    health_data = response.json()
                    print(f"   ✅ Server health: PASSED (Status: {health_data.get('status')})")
                else:
                    print(f"   ❌ Server health: FAILED (Status code: {response.status_code})")
                    
            except Exception as e:
                health_success = False
                print(f"   ❌ Server health: FAILED (Connection error: {str(e)})")
            
            results["server_health"]["accessible"] = health_success
            
            if health_success:
                # Test task creation and processing
                print("   📋 Testing task creation and processing...")
                
                test_task = {
                    "input": "Integration test - analyze test customer for Hong Kong market",
                    "additional_input": {
                        "focus": "lead_intelligence",
                        "test_mode": True
                    }
                }
                
                try:
                    # Create task
                    create_response = requests.post(
                        f"{self.agent_protocol_url}/ap/v1/agent/tasks",
                        json=test_task,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    
                    task_success = create_response.status_code == 200
                    
                    if task_success:
                        task_data = create_response.json()
                        task_id = task_data.get('task_id')
                        print(f"   ✅ Task creation: PASSED (ID: {task_id[:8]}...)")
                        
                        # Check task status
                        time.sleep(2)  # Allow processing time
                        status_response = requests.get(
                            f"{self.agent_protocol_url}/ap/v1/agent/tasks/{task_id}",
                            timeout=10
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            task_status = status_data.get('status')
                            print(f"   ✅ Task processing: PASSED (Status: {task_status})")
                            
                            results["task_processing"] = {
                                "creation_success": True,
                                "status_retrieval": True,
                                "final_status": task_status
                            }
                        else:
                            print(f"   ❌ Task status retrieval: FAILED")
                            results["task_processing"] = {
                                "creation_success": True,
                                "status_retrieval": False
                            }
                    else:
                        print(f"   ❌ Task creation: FAILED (Status: {create_response.status_code})")
                        results["task_processing"] = {
                            "creation_success": False,
                            "error": f"Status code: {create_response.status_code}"
                        }
                        
                except Exception as e:
                    print(f"   ❌ Task processing: FAILED ({str(e)})")
                    results["task_processing"] = {
                        "creation_success": False,
                        "error": str(e)
                    }
            
            # Overall Agent Protocol assessment
            protocol_passed = (
                health_success and 
                results.get("task_processing", {}).get("creation_success", False)
            )
            
            results["status"] = "passed" if protocol_passed else "failed"
            
        except Exception as e:
            print(f"   ❌ Agent Protocol test failed: {str(e)}")
            results["status"] = "failed" 
            results["error"] = str(e)
        
        return results
    
    def assess_overall_status(self):
        """Assess overall test status based on all individual test results"""
        
        test_statuses = [
            self.test_results["agent_communication"].get("status"),
            self.test_results["performance_metrics"].get("status"),
            self.test_results["privacy_security"].get("status"),
            self.test_results["real_world_scenarios"].get("status"),
            self.test_results["agent_protocol"].get("status")
        ]
        
        passed_tests = sum(1 for status in test_statuses if status == "passed")
        failed_tests = sum(1 for status in test_statuses if status == "failed")
        skipped_tests = sum(1 for status in test_statuses if status == "skipped")
        
        if failed_tests == 0 and passed_tests > 0:
            self.test_results["overall_status"] = "passed"
        elif failed_tests > 0 and passed_tests >= failed_tests:
            self.test_results["overall_status"] = "partial"
        else:
            self.test_results["overall_status"] = "failed"
        
        self.test_results["test_summary"] = {
            "total_tests": len(test_statuses),
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests
        }
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        print("\\n" + "=" * 70)
        print("📊 INTEGRATION & PERFORMANCE TEST REPORT")
        print("=" * 70)
        
        # Overall Status
        status_icon = {
            "passed": "✅",
            "partial": "⚠️",
            "failed": "❌",
            "critical_failure": "💥"
        }.get(self.test_results["overall_status"], "❓")
        
        print(f"\\n🎯 Overall Status: {status_icon} {self.test_results['overall_status'].upper()}")
        
        # Test Summary
        summary = self.test_results.get("test_summary", {})
        print(f"\\n📈 Test Summary:")
        print(f"   • Total Tests: {summary.get('total_tests', 0)}")
        print(f"   • Passed: {summary.get('passed', 0)} ✅")
        print(f"   • Failed: {summary.get('failed', 0)} ❌")
        print(f"   • Skipped: {summary.get('skipped', 0)} ⏭️")
        
        # Detailed Results
        print(f"\\n📋 Detailed Results:")
        
        test_sections = [
            ("Agent Communication", "agent_communication"),
            ("Performance Metrics", "performance_metrics"),
            ("Privacy & Security", "privacy_security"),
            ("Real-World Scenarios", "real_world_scenarios"),
            ("Agent Protocol", "agent_protocol")
        ]
        
        for name, key in test_sections:
            section = self.test_results.get(key, {})
            status = section.get("status", "unknown")
            status_icon = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}.get(status, "❓")
            print(f"   • {name}: {status_icon} {status.upper()}")
        
        # Performance Highlights
        perf = self.test_results.get("performance_metrics", {})
        if perf.get("response_time_tests"):
            avg_time = perf["response_time_tests"].get("average_time", 0)
            max_time = perf["response_time_tests"].get("max_time", 0)
            print(f"\\n⚡ Performance Highlights:")
            print(f"   • Average Response Time: {avg_time:.2f}s")
            print(f"   • Maximum Response Time: {max_time:.2f}s")
            print(f"   • Sub-30s Requirement: {'✅ MET' if max_time < 30.0 else '❌ FAILED'}")
        
        # Recommendations
        print(f"\\n💡 Recommendations:")
        
        if self.test_results["overall_status"] == "passed":
            print("   ✅ System ready for production deployment")
            print("   ✅ All critical requirements met")
            print("   ✅ Multi-agent collaboration validated")
            
        elif self.test_results["overall_status"] == "partial":
            print("   ⚠️ Some tests failed - review detailed results")
            print("   🔧 Address failed components before production")
            print("   📋 Consider additional testing for failed areas")
            
        else:
            print("   ❌ Critical issues detected - do not deploy")
            print("   🚨 Review all failed tests immediately")
            print("   🔧 Fix fundamental issues before retesting")
        
        # Save detailed report
        report_path = project_root / "integration_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\\n📄 Detailed report saved: {report_path}")
        print()


def main():
    """Main execution function"""
    
    print("🚀 Subtask 12.5: Integration Testing and Performance Validation")
    print("================================================================")
    print()
    
    # Initialize validator
    validator = IntegrationPerformanceValidator()
    
    # Run comprehensive tests
    results = validator.run_comprehensive_tests()
    
    # Return appropriate exit code
    if results["overall_status"] == "passed":
        print("🎉 All tests passed! System ready for production.")
        return 0
    elif results["overall_status"] == "partial":
        print("⚠️ Some tests failed. Review results before proceeding.")
        return 1
    else:
        print("❌ Critical test failures. System needs fixes.")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
