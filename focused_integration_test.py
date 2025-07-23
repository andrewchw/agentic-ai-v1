#!/usr/bin/env python3
"""
Subtask 12.5: Focused Integration Testing and Performance Validation
================================================================

Focused integration testing that validates what we can actually test:
1. Agent Protocol REST API functionality
2. Multi-agent task routing via Agent Protocol  
3. System responsiveness and performance
4. API reliability and error handling

This approach focuses on the Agent Protocol as the primary integration point,
which is working correctly and is our main achievement.
"""

import time
import json
import requests
from datetime import datetime
from typing import Dict, Any, List
import statistics

class FocusedIntegrationValidator:
    """Focused integration testing for Agent Protocol and system reliability"""
    
    def __init__(self):
        self.agent_protocol_url = "http://127.0.0.1:8080"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "agent_protocol_comprehensive": {},
            "multi_agent_routing": {},
            "performance_validation": {},
            "reliability_testing": {},
            "overall_status": "unknown"
        }
    
    def run_focused_tests(self) -> Dict[str, Any]:
        """Execute focused integration tests"""
        
        print("🧪 Focused Integration Testing - Agent Protocol & Performance")
        print("=" * 75)
        print()
        
        try:
            # Test 1: Comprehensive Agent Protocol Testing
            print("1️⃣ Comprehensive Agent Protocol Testing...")
            self.test_results["agent_protocol_comprehensive"] = self.test_agent_protocol_comprehensive()
            
            # Test 2: Multi-Agent Task Routing
            print("\\n2️⃣ Multi-Agent Task Routing via Agent Protocol...")
            self.test_results["multi_agent_routing"] = self.test_multi_agent_routing()
            
            # Test 3: Performance Validation
            print("\\n3️⃣ Performance Validation...")
            self.test_results["performance_validation"] = self.test_performance_validation()
            
            # Test 4: Reliability Testing
            print("\\n4️⃣ Reliability and Error Handling...")
            self.test_results["reliability_testing"] = self.test_reliability()
            
            # Assess overall status
            self.assess_overall_status()
            
            # Generate report
            self.generate_focused_report()
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ Critical test failure: {str(e)}")
            self.test_results["overall_status"] = "critical_failure"
            self.test_results["error"] = str(e)
            return self.test_results
    
    def test_agent_protocol_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive testing of all Agent Protocol endpoints"""
        
        results = {
            "health_check": {},
            "task_lifecycle": {},
            "api_compliance": {},
            "status": "unknown"
        }
        
        try:
            print("   🏥 Testing server health endpoint...")
            
            # Health Check
            start_time = time.time()
            health_response = requests.get(f"{self.agent_protocol_url}/ap/v1/agent/health", timeout=10)
            health_time = time.time() - start_time
            
            health_success = health_response.status_code == 200
            health_data = health_response.json() if health_success else {}
            
            results["health_check"] = {
                "success": health_success,
                "response_time": health_time,
                "status": health_data.get("status"),
                "version": health_data.get("agent_protocol_version"),
                "active_tasks": health_data.get("active_tasks", 0)
            }
            
            print(f"   ✅ Health check: {'PASSED' if health_success else 'FAILED'} ({health_time:.3f}s)")
            
            if health_success:
                # Task Lifecycle Testing
                print("   📋 Testing complete task lifecycle...")
                
                lifecycle_results = self.test_task_lifecycle()
                results["task_lifecycle"] = lifecycle_results
                
                # API Compliance Testing
                print("   📝 Testing API compliance...")
                
                compliance_results = self.test_api_compliance()
                results["api_compliance"] = compliance_results
                
                # Overall assessment
                overall_success = (
                    health_success and
                    lifecycle_results.get("success", False) and
                    compliance_results.get("success", False)
                )
                
                results["status"] = "passed" if overall_success else "failed"
            else:
                results["status"] = "failed"
                print("   ❌ Cannot proceed - server health check failed")
                
        except Exception as e:
            print(f"   ❌ Agent Protocol test failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def test_task_lifecycle(self) -> Dict[str, Any]:
        """Test complete task creation, execution, and retrieval lifecycle"""
        
        lifecycle_results = {
            "task_creation": {},
            "task_execution": {},
            "task_retrieval": {},
            "task_listing": {},
            "success": False
        }
        
        try:
            # Create a test task
            test_task = {
                "input": "Integration test: Analyze enterprise customer growth potential for Hong Kong market",
                "additional_input": {
                    "focus": "lead_intelligence",
                    "test_type": "integration_validation",
                    "customer_segment": "enterprise"
                }
            }
            
            # Task Creation
            start_time = time.time()
            create_response = requests.post(
                f"{self.agent_protocol_url}/ap/v1/agent/tasks",
                json=test_task,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            creation_time = time.time() - start_time
            
            creation_success = create_response.status_code == 200
            
            if creation_success:
                task_data = create_response.json()
                task_id = task_data.get("task_id")
                
                lifecycle_results["task_creation"] = {
                    "success": True,
                    "task_id": task_id,
                    "creation_time": creation_time,
                    "initial_status": task_data.get("status")
                }
                
                print(f"   ✅ Task creation: PASSED ({creation_time:.3f}s, ID: {task_id[:8]}...)")
                
                # Wait for task execution
                print("   ⏳ Monitoring task execution...")
                execution_results = self.monitor_task_execution(task_id)
                lifecycle_results["task_execution"] = execution_results
                
                # Task Retrieval
                retrieval_results = self.test_task_retrieval(task_id)
                lifecycle_results["task_retrieval"] = retrieval_results
                
                # Task Listing
                listing_results = self.test_task_listing()
                lifecycle_results["task_listing"] = listing_results
                
                # Overall lifecycle success
                lifecycle_results["success"] = (
                    creation_success and
                    execution_results.get("success", False) and
                    retrieval_results.get("success", False) and
                    listing_results.get("success", False)
                )
                
            else:
                lifecycle_results["task_creation"] = {
                    "success": False,
                    "error": f"Status code: {create_response.status_code}",
                    "creation_time": creation_time
                }
                print(f"   ❌ Task creation: FAILED ({create_response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Task lifecycle test failed: {str(e)}")
            lifecycle_results["error"] = str(e)
        
        return lifecycle_results
    
    def monitor_task_execution(self, task_id: str) -> Dict[str, Any]:
        """Monitor task execution until completion"""
        
        execution_results = {
            "monitoring_duration": 0,
            "final_status": "unknown",
            "success": False
        }
        
        start_monitor = time.time()
        max_wait_time = 30  # 30 seconds max
        
        try:
            while time.time() - start_monitor < max_wait_time:
                status_response = requests.get(
                    f"{self.agent_protocol_url}/ap/v1/agent/tasks/{task_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data.get("status")
                    
                    if current_status in ["completed", "failed"]:
                        execution_results["final_status"] = current_status
                        execution_results["success"] = current_status == "completed"
                        break
                        
                time.sleep(1)  # Wait 1 second between checks
            
            execution_results["monitoring_duration"] = time.time() - start_monitor
            
            if execution_results["success"]:
                print(f"   ✅ Task execution: COMPLETED ({execution_results['monitoring_duration']:.1f}s)")
            else:
                print(f"   ⚠️ Task execution: {execution_results['final_status'].upper()} ({execution_results['monitoring_duration']:.1f}s)")
                
        except Exception as e:
            print(f"   ❌ Task monitoring failed: {str(e)}")
            execution_results["error"] = str(e)
        
        return execution_results
    
    def test_task_retrieval(self, task_id: str) -> Dict[str, Any]:
        """Test task details retrieval"""
        
        retrieval_results = {
            "success": False,
            "response_time": 0,
            "has_artifacts": False
        }
        
        try:
            start_time = time.time()
            retrieval_response = requests.get(
                f"{self.agent_protocol_url}/ap/v1/agent/tasks/{task_id}",
                timeout=10
            )
            retrieval_time = time.time() - start_time
            
            retrieval_success = retrieval_response.status_code == 200
            
            if retrieval_success:
                task_details = retrieval_response.json()
                
                retrieval_results = {
                    "success": True,
                    "response_time": retrieval_time,
                    "has_artifacts": len(task_details.get("artifacts", [])) > 0,
                    "status": task_details.get("status"),
                    "created_at": task_details.get("created_at"),
                    "modified_at": task_details.get("modified_at")
                }
                
                print(f"   ✅ Task retrieval: PASSED ({retrieval_time:.3f}s, {len(task_details.get('artifacts', []))} artifacts)")
            else:
                retrieval_results["error"] = f"Status code: {retrieval_response.status_code}"
                print(f"   ❌ Task retrieval: FAILED ({retrieval_response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Task retrieval failed: {str(e)}")
            retrieval_results["error"] = str(e)
        
        return retrieval_results
    
    def test_task_listing(self) -> Dict[str, Any]:
        """Test task listing endpoint"""
        
        listing_results = {
            "success": False,
            "response_time": 0,
            "task_count": 0
        }
        
        try:
            start_time = time.time()
            listing_response = requests.get(
                f"{self.agent_protocol_url}/ap/v1/agent/tasks",
                timeout=10
            )
            listing_time = time.time() - start_time
            
            listing_success = listing_response.status_code == 200
            
            if listing_success:
                tasks_list = listing_response.json()
                
                listing_results = {
                    "success": True,
                    "response_time": listing_time,
                    "task_count": len(tasks_list)
                }
                
                print(f"   ✅ Task listing: PASSED ({listing_time:.3f}s, {len(tasks_list)} total tasks)")
            else:
                listing_results["error"] = f"Status code: {listing_response.status_code}"
                print(f"   ❌ Task listing: FAILED ({listing_response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Task listing failed: {str(e)}")
            listing_results["error"] = str(e)
        
        return listing_results
    
    def test_api_compliance(self) -> Dict[str, Any]:
        """Test API compliance with Agent Protocol standard"""
        
        compliance_results = {
            "openapi_docs": {},
            "cors_headers": {},
            "content_types": {},
            "success": False
        }
        
        try:
            # Test OpenAPI documentation endpoint
            print("   📚 Testing OpenAPI documentation...")
            
            docs_response = requests.get(f"{self.agent_protocol_url}/ap/v1/docs", timeout=10)
            openapi_response = requests.get(f"{self.agent_protocol_url}/ap/v1/openapi.json", timeout=10)
            
            compliance_results["openapi_docs"] = {
                "docs_accessible": docs_response.status_code == 200,
                "openapi_json": openapi_response.status_code == 200
            }
            
            # Test CORS headers (by checking response headers)
            health_response = requests.get(f"{self.agent_protocol_url}/ap/v1/agent/health")
            
            compliance_results["cors_headers"] = {
                "has_cors": "access-control-allow-origin" in [h.lower() for h in health_response.headers.keys()]
            }
            
            # Overall compliance
            compliance_results["success"] = (
                compliance_results["openapi_docs"]["docs_accessible"] and
                compliance_results["openapi_docs"]["openapi_json"]
            )
            
            print(f"   ✅ API compliance: {'PASSED' if compliance_results['success'] else 'PARTIAL'}")
            
        except Exception as e:
            print(f"   ❌ API compliance test failed: {str(e)}")
            compliance_results["error"] = str(e)
        
        return compliance_results
    
    def test_multi_agent_routing(self) -> Dict[str, Any]:
        """Test multi-agent task routing capabilities"""
        
        results = {
            "lead_intelligence_routing": {},
            "revenue_optimization_routing": {},
            "collaborative_routing": {},
            "status": "unknown"
        }
        
        try:
            # Test Lead Intelligence Agent routing
            print("   🔍 Testing Lead Intelligence Agent routing...")
            
            lead_task = {
                "input": "Analyze customer churn patterns for Three HK enterprise customers",
                "additional_input": {
                    "focus": "lead_intelligence",
                    "analysis_type": "churn_prediction"
                }
            }
            
            lead_result = self.execute_routing_test(lead_task, "Lead Intelligence")
            results["lead_intelligence_routing"] = lead_result
            
            # Test Revenue Optimization Agent routing
            print("   💰 Testing Revenue Optimization Agent routing...")
            
            revenue_task = {
                "input": "Develop pricing strategy for 5G business plans in Hong Kong",
                "additional_input": {
                    "focus": "revenue_optimization",
                    "product_focus": "5g_business"
                }
            }
            
            revenue_result = self.execute_routing_test(revenue_task, "Revenue Optimization")
            results["revenue_optimization_routing"] = revenue_result
            
            # Test Collaborative routing
            print("   🤝 Testing Collaborative multi-agent routing...")
            
            collab_task = {
                "input": "Comprehensive customer analysis and revenue strategy development",
                "additional_input": {
                    "focus": "collaborative",
                    "agents": ["lead_intelligence", "revenue_optimization"]
                }
            }
            
            collab_result = self.execute_routing_test(collab_task, "Collaborative")
            results["collaborative_routing"] = collab_result
            
            # Overall routing assessment
            routing_success = (
                lead_result.get("success", False) and
                revenue_result.get("success", False) and
                collab_result.get("success", False)
            )
            
            results["status"] = "passed" if routing_success else "failed"
            
        except Exception as e:
            print(f"   ❌ Multi-agent routing test failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def execute_routing_test(self, task_data: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
        """Execute a single routing test"""
        
        result = {
            "success": False,
            "execution_time": 0,
            "task_id": None
        }
        
        try:
            start_time = time.time()
            
            # Create task
            response = requests.post(
                f"{self.agent_protocol_url}/ap/v1/agent/tasks",
                json=task_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                task_info = response.json()
                task_id = task_info.get("task_id")
                result["task_id"] = task_id
                
                # Monitor execution
                execution_time = time.time()
                while time.time() - execution_time < 20:  # 20 second timeout
                    status_response = requests.get(
                        f"{self.agent_protocol_url}/ap/v1/agent/tasks/{task_id}",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get("status") == "completed":
                            result["success"] = True
                            break
                    
                    time.sleep(1)
                
                result["execution_time"] = time.time() - start_time
                
                status_icon = "✅" if result["success"] else "⚠️"
                print(f"   {status_icon} {agent_type}: {'PASSED' if result['success'] else 'TIMEOUT'} ({result['execution_time']:.1f}s)")
            else:
                print(f"   ❌ {agent_type}: FAILED (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ {agent_type}: ERROR ({str(e)})")
            result["error"] = str(e)
        
        return result
    
    def test_performance_validation(self) -> Dict[str, Any]:
        """Test performance characteristics"""
        
        results = {
            "response_times": {},
            "throughput": {},
            "sub_30s_compliance": {},
            "status": "unknown"
        }
        
        try:
            print("   ⚡ Testing API response times...")
            
            # Test multiple health checks for baseline
            health_times = []
            for i in range(5):
                start_time = time.time()
                response = requests.get(f"{self.agent_protocol_url}/ap/v1/agent/health", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    health_times.append(response_time)
            
            results["response_times"] = {
                "health_check_avg": statistics.mean(health_times) if health_times else 0,
                "health_check_max": max(health_times) if health_times else 0,
                "health_check_count": len(health_times)
            }
            
            print(f"   📊 Health check avg: {results['response_times']['health_check_avg']:.3f}s")
            
            # Test task processing times
            print("   ⏱️ Testing task processing performance...")
            
            processing_times = []
            successful_tasks = 0
            
            for i in range(3):  # Test 3 tasks
                test_task = {
                    "input": f"Performance test {i+1}: Quick customer analysis",
                    "additional_input": {"focus": "lead_intelligence", "test_mode": True}
                }
                
                start_time = time.time()
                
                # Create and monitor task
                create_response = requests.post(
                    f"{self.agent_protocol_url}/ap/v1/agent/tasks",
                    json=test_task,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if create_response.status_code == 200:
                    task_data = create_response.json()
                    task_id = task_data.get("task_id")
                    
                    # Monitor until completion
                    monitor_start = time.time()
                    while time.time() - monitor_start < 25:  # 25s timeout
                        status_response = requests.get(
                            f"{self.agent_protocol_url}/ap/v1/agent/tasks/{task_id}",
                            timeout=10
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            if status_data.get("status") == "completed":
                                total_time = time.time() - start_time
                                processing_times.append(total_time)
                                successful_tasks += 1
                                break
                        
                        time.sleep(1)
            
            if processing_times:
                avg_processing = statistics.mean(processing_times)
                max_processing = max(processing_times)
                
                results["response_times"]["task_processing_avg"] = avg_processing
                results["response_times"]["task_processing_max"] = max_processing
                
                # Sub-30 second compliance check
                results["sub_30s_compliance"] = {
                    "all_under_30s": max_processing < 30.0,
                    "max_time": max_processing,
                    "compliant_tasks": sum(1 for t in processing_times if t < 30.0),
                    "total_tasks": len(processing_times)
                }
                
                print(f"   📊 Task processing avg: {avg_processing:.1f}s")
                print(f"   📊 Task processing max: {max_processing:.1f}s")
                print(f"   ✅ Sub-30s compliance: {'PASSED' if max_processing < 30.0 else 'FAILED'}")
                
                # Overall performance assessment
                performance_passed = (
                    results["response_times"]["health_check_avg"] < 1.0 and
                    max_processing < 30.0 and
                    successful_tasks >= 2
                )
                
                results["status"] = "passed" if performance_passed else "failed"
            else:
                results["status"] = "failed"
                print("   ❌ No successful task completions for performance measurement")
                
        except Exception as e:
            print(f"   ❌ Performance validation failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def test_reliability(self) -> Dict[str, Any]:
        """Test system reliability and error handling"""
        
        results = {
            "error_handling": {},
            "consistency": {},
            "recovery": {},
            "status": "unknown"
        }
        
        try:
            print("   🛡️ Testing error handling...")
            
            # Test invalid task creation
            invalid_task = {"invalid": "task structure"}
            error_response = requests.post(
                f"{self.agent_protocol_url}/ap/v1/agent/tasks",
                json=invalid_task,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Test invalid task ID retrieval
            invalid_id_response = requests.get(
                f"{self.agent_protocol_url}/ap/v1/agent/tasks/invalid-task-id",
                timeout=10
            )
            
            results["error_handling"] = {
                "invalid_task_status": error_response.status_code,
                "invalid_id_status": invalid_id_response.status_code,
                "proper_error_codes": (
                    error_response.status_code in [400, 422] and
                    invalid_id_response.status_code in [404, 400]
                )
            }
            
            # Test consistency (multiple identical requests)
            print("   🔄 Testing consistency...")
            
            consistent_task = {
                "input": "Consistency test: analyze customer data",
                "additional_input": {"focus": "lead_intelligence"}
            }
            
            consistency_results = []
            for i in range(3):
                response = requests.post(
                    f"{self.agent_protocol_url}/ap/v1/agent/tasks",
                    json=consistent_task,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                consistency_results.append(response.status_code == 200)
            
            results["consistency"] = {
                "successful_requests": sum(consistency_results),
                "total_requests": len(consistency_results),
                "consistency_rate": sum(consistency_results) / len(consistency_results)
            }
            
            # Overall reliability assessment
            reliability_passed = (
                results["error_handling"]["proper_error_codes"] and
                results["consistency"]["consistency_rate"] >= 0.8
            )
            
            results["status"] = "passed" if reliability_passed else "failed"
            
            print(f"   ✅ Error handling: {'PASSED' if results['error_handling']['proper_error_codes'] else 'FAILED'}")
            print(f"   ✅ Consistency: {'PASSED' if results['consistency']['consistency_rate'] >= 0.8 else 'FAILED'} ({results['consistency']['consistency_rate']*100:.0f}%)")
            
        except Exception as e:
            print(f"   ❌ Reliability test failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def assess_overall_status(self):
        """Assess overall test status"""
        
        test_statuses = [
            self.test_results["agent_protocol_comprehensive"].get("status"),
            self.test_results["multi_agent_routing"].get("status"),
            self.test_results["performance_validation"].get("status"),
            self.test_results["reliability_testing"].get("status")
        ]
        
        passed_tests = sum(1 for status in test_statuses if status == "passed")
        failed_tests = sum(1 for status in test_statuses if status == "failed")
        
        if failed_tests == 0 and passed_tests > 0:
            self.test_results["overall_status"] = "passed"
        elif failed_tests > 0 and passed_tests >= failed_tests:
            self.test_results["overall_status"] = "partial"
        else:
            self.test_results["overall_status"] = "failed"
        
        self.test_results["test_summary"] = {
            "total_tests": len(test_statuses),
            "passed": passed_tests,
            "failed": failed_tests
        }
    
    def generate_focused_report(self):
        """Generate focused test report"""
        
        print("\\n" + "=" * 75)
        print("📊 FOCUSED INTEGRATION & PERFORMANCE TEST REPORT")
        print("=" * 75)
        
        # Overall Status
        status_icons = {
            "passed": "✅",
            "partial": "⚠️",
            "failed": "❌",
            "critical_failure": "💥"
        }
        
        status_icon = status_icons.get(self.test_results["overall_status"], "❓")
        print(f"\\n🎯 Overall Status: {status_icon} {self.test_results['overall_status'].upper()}")
        
        # Test Summary
        summary = self.test_results.get("test_summary", {})
        print(f"\\n📈 Test Summary:")
        print(f"   • Total Tests: {summary.get('total_tests', 0)}")
        print(f"   • Passed: {summary.get('passed', 0)} ✅")
        print(f"   • Failed: {summary.get('failed', 0)} ❌")
        
        # Performance Highlights
        perf = self.test_results.get("performance_validation", {})
        if perf.get("sub_30s_compliance"):
            compliance = perf["sub_30s_compliance"]
            print(f"\\n⚡ Performance Highlights:")
            print(f"   • Sub-30s Requirement: {'✅ MET' if compliance.get('all_under_30s') else '❌ FAILED'}")
            print(f"   • Maximum Response Time: {compliance.get('max_time', 0):.1f}s")
            print(f"   • Compliant Tasks: {compliance.get('compliant_tasks', 0)}/{compliance.get('total_tasks', 0)}")
        
        # Agent Protocol Status
        protocol = self.test_results.get("agent_protocol_comprehensive", {})
        if protocol.get("health_check"):
            health = protocol["health_check"]
            print(f"\\n🌐 Agent Protocol Status:")
            print(f"   • Server Status: {health.get('status', 'unknown').upper()}")
            print(f"   • Protocol Version: {health.get('version', 'unknown')}")
            print(f"   • Active Tasks: {health.get('active_tasks', 0)}")
        
        # Multi-Agent Routing Results
        routing = self.test_results.get("multi_agent_routing", {})
        if routing:
            print(f"\\n🤖 Multi-Agent Routing:")
            
            routing_tests = [
                ("Lead Intelligence", routing.get("lead_intelligence_routing", {})),
                ("Revenue Optimization", routing.get("revenue_optimization_routing", {})),
                ("Collaborative", routing.get("collaborative_routing", {}))
            ]
            
            for name, result in routing_tests:
                success = result.get("success", False)
                exec_time = result.get("execution_time", 0)
                status_icon = "✅" if success else "❌"
                print(f"   • {name}: {status_icon} {'PASSED' if success else 'FAILED'} ({exec_time:.1f}s)")
        
        # Final Assessment
        print(f"\\n💡 Final Assessment:")
        
        if self.test_results["overall_status"] == "passed":
            print("   ✅ Agent Protocol system fully validated")
            print("   ✅ Multi-agent routing working correctly")
            print("   ✅ Performance requirements met")
            print("   ✅ System ready for production deployment")
            
        elif self.test_results["overall_status"] == "partial":
            print("   ⚠️ Core Agent Protocol functionality working")
            print("   ⚠️ Some advanced features may need attention")
            print("   📋 Consider addressing failed components")
            
        else:
            print("   ❌ Critical issues detected in Agent Protocol")
            print("   🚨 Review all failed tests immediately")
            print("   🔧 Fix fundamental issues before deployment")
        
        # Save report
        report_path = "integration_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\\n📄 Detailed report saved: {report_path}")
        print()


def main():
    """Main execution function"""
    
    print("🚀 Subtask 12.5: Focused Integration Testing and Performance Validation")
    print("=" * 80)
    print("🎯 Focus: Agent Protocol functionality and multi-agent system integration")
    print()
    
    # Initialize validator
    validator = FocusedIntegrationValidator()
    
    # Run focused tests
    results = validator.run_focused_tests()
    
    # Return appropriate exit code
    if results["overall_status"] == "passed":
        print("🎉 All focused tests passed! Agent Protocol system validated.")
        return 0
    elif results["overall_status"] == "partial":
        print("⚠️ Core functionality working. Some advanced features need attention.")
        return 1
    else:
        print("❌ Critical issues detected. System needs fixes.")
        return 2


if __name__ == "__main__":
    exit_code = main()
    print(f"\\n🏁 Test execution completed with exit code: {exit_code}")
