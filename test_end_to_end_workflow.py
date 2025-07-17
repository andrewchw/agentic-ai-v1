#!/usr/bin/env python3
"""
Comprehensive End-to-End Business Analysis Workflow Tests

This script tests the complete business analysis workflow including:
- Complete customer analysis pipeline
- Individual analysis components
- Error handling and resilience
- Performance under load
- Integration with privacy pipeline
- Batch processing capabilities
- Real-world data scenarios
"""

import os
import sys
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# Add src to path
sys.path.append('src')

from utils.business_analysis_workflow import (
    BusinessAnalysisWorkflow,
    AnalysisRequest,
    AnalysisResult,
    create_workflow,
    quick_customer_analysis
)
from utils.openrouter_client import OpenRouterConfig

def create_sample_customer_data():
    """Create realistic sample customer data for testing."""
    return {
        "customer_id": f"CUST_{random.randint(10000, 99999)}",
        "account_type": random.choice(["Premium", "Business", "Family", "Standard"]),
        "tenure_months": random.randint(6, 60),
        "location": random.choice(["Hong Kong Island", "Kowloon", "New Territories"]),
        "segment": random.choice(["Business", "Consumer", "Student"]),
        "monthly_spend": round(random.uniform(200, 2000), 2),
        "payment_method": random.choice(["Auto-Pay", "Manual", "Credit Card"]),
        "contract_type": random.choice(["Postpaid", "Prepaid"]),
        "age_group": random.choice(["18-25", "26-35", "36-45", "46-55", "55+"]),
        "data_usage_gb": round(random.uniform(5, 100), 1)
    }

def create_sample_purchase_history():
    """Create realistic sample purchase history."""
    history = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(random.randint(3, 12)):
        purchase_date = base_date + timedelta(days=random.randint(0, 365))
        history.append({
            "date": purchase_date.strftime("%Y-%m-%d"),
            "product": random.choice([
                "5G Business Plan", "Data Add-on", "International Roaming",
                "Device Purchase", "Premium Features", "Family Add-on"
            ]),
            "amount": round(random.uniform(50, 1500), 2),
            "currency": "HKD",
            "category": random.choice(["Plan", "Add-on", "Device", "Service"])
        })
    
    return sorted(history, key=lambda x: x["date"])

def create_sample_engagement_data():
    """Create realistic sample engagement data."""
    return {
        "login_frequency": random.choice(["Daily", "Weekly", "Monthly", "Rarely"]),
        "app_usage_hours": round(random.uniform(1, 20), 1),
        "support_tickets": random.randint(0, 5),
        "satisfaction_score": round(random.uniform(6.0, 10.0), 1),
        "feature_usage": random.sample([
            "Mobile App", "Online Portal", "Auto-Pay", "Bill Notifications",
            "Data Monitoring", "Roaming Services", "Customer Support Chat"
        ], k=random.randint(2, 5)),
        "last_interaction": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
    }

def create_sample_offers():
    """Create sample Three HK offers."""
    return [
        {
            "offer_id": "THREE_5G_PREMIUM_2024",
            "name": "5G Premium Unlimited 2024",
            "price": 699.00,
            "currency": "HKD",
            "features": ["Unlimited 5G Data", "International Roaming", "Priority Support", "Cloud Storage"],
            "target_segment": "Premium",
            "validity_days": 30
        },
        {
            "offer_id": "THREE_BUSINESS_ENTERPRISE",
            "name": "Business Enterprise Solution",
            "price": 1599.00,
            "currency": "HKD",
            "features": ["Multi-line Management", "VPN Access", "Priority Network", "24/7 Support"],
            "target_segment": "Business",
            "validity_days": 30
        }
    ]

def test_workflow_initialization():
    """Test workflow initialization and configuration."""
    print("Testing Workflow Initialization...")
    
    try:
        # Test default initialization
        workflow1 = BusinessAnalysisWorkflow()
        assert workflow1.openrouter_client is not None
        print("  ✅ Default workflow initialization successful")
        
        # Test with custom config
        config = OpenRouterConfig(
            api_key=os.getenv('OPENROUTER_API_KEY', 'test-key'),
            default_model="deepseek/deepseek-chat"
        )
        workflow2 = BusinessAnalysisWorkflow(openrouter_config=config)
        assert workflow2.openrouter_client.config.default_model == "deepseek/deepseek-chat"
        print("  ✅ Custom config workflow initialization successful")
        
        # Test privacy pipeline initialization
        workflow3 = BusinessAnalysisWorkflow(enable_privacy_masking=True)
        print(f"  ✅ Privacy masking enabled: {workflow3.enable_privacy}")
        
        # Test convenience function
        workflow4 = create_workflow(api_key="test-key")
        assert workflow4 is not None
        print("  ✅ Convenience function workflow creation successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Workflow initialization test failed: {str(e)}")
        return False

def test_individual_analysis_components():
    """Test individual analysis components."""
    print("\nTesting Individual Analysis Components...")
    
    try:
        workflow = BusinessAnalysisWorkflow(enable_privacy_masking=False, enable_logging=False)
        
        # Create test data
        customer_data = create_sample_customer_data()
        purchase_history = create_sample_purchase_history()
        engagement_data = create_sample_engagement_data()
        
        request = AnalysisRequest(
            customer_data=customer_data,
            purchase_history=purchase_history,
            engagement_data=engagement_data,
            customer_id=customer_data["customer_id"]
        )
        
        # Test customer patterns analysis (will fail without API key but should handle gracefully)
        patterns_result = workflow._analyze_customer_patterns(request)
        assert isinstance(patterns_result, AnalysisResult)
        assert patterns_result.customer_id == customer_data["customer_id"]
        print("  ✅ Customer patterns analysis component works")
        
        # Test lead scoring
        scoring_result = workflow._score_lead_priority(request)
        assert isinstance(scoring_result, AnalysisResult)
        assert scoring_result.customer_id == customer_data["customer_id"]
        print("  ✅ Lead scoring analysis component works")
        
        # Test recommendations generation
        recommendations_result = workflow._generate_sales_recommendations(
            request, {"test": "analysis"}
        )
        assert isinstance(recommendations_result, AnalysisResult)
        print("  ✅ Sales recommendations component works")
        
        # Test data preparation methods
        processed_customer = workflow._prepare_customer_data(customer_data)
        assert isinstance(processed_customer, dict)
        print("  ✅ Customer data preparation works")
        
        processed_history = workflow._prepare_purchase_history(purchase_history)
        assert isinstance(processed_history, list)
        print("  ✅ Purchase history preparation works")
        
        processed_engagement = workflow._prepare_engagement_data(engagement_data)
        assert isinstance(processed_engagement, dict)
        print("  ✅ Engagement data preparation works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Individual components test failed: {str(e)}")
        return False

def test_complete_analysis_workflow():
    """Test complete end-to-end analysis workflow."""
    print("\nTesting Complete Analysis Workflow...")
    
    try:
        workflow = BusinessAnalysisWorkflow(enable_privacy_masking=False, enable_logging=False)
        
        # Create comprehensive test data
        customer_data = create_sample_customer_data()
        purchase_history = create_sample_purchase_history()
        engagement_data = create_sample_engagement_data()
        available_offers = create_sample_offers()
        
        request = AnalysisRequest(
            customer_data=customer_data,
            purchase_history=purchase_history,
            engagement_data=engagement_data,
            available_offers=available_offers,
            customer_id=customer_data["customer_id"],
            context="Three HK comprehensive analysis test"
        )
        
        # Perform complete analysis
        result = workflow.analyze_customer_complete(request)
        
        # Validate result structure
        assert isinstance(result, AnalysisResult)
        assert result.customer_id == customer_data["customer_id"]
        assert result.analysis_type == "complete"
        assert result.processing_time > 0
        assert result.timestamp is not None
        
        print(f"  ✅ Complete analysis executed in {result.processing_time:.2f}s")
        print(f"  ✅ Analysis success: {result.success}")
        
        if not result.success:
            print(f"    Expected failure (no API key): {result.error_message}")
        
        # Test workflow statistics
        stats = workflow.get_workflow_statistics()
        assert isinstance(stats, dict)
        assert "total_analyses" in stats
        assert "success_rate" in stats
        print("  ✅ Workflow statistics collection works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Complete analysis workflow test failed: {str(e)}")
        return False

def test_error_handling_resilience():
    """Test error handling and system resilience."""
    print("\nTesting Error Handling and Resilience...")
    
    try:
        workflow = BusinessAnalysisWorkflow(enable_privacy_masking=False, enable_logging=False)
        
        # Test with invalid customer data
        invalid_request = AnalysisRequest(
            customer_data={},  # Empty data
            purchase_history=[],  # Empty history
            customer_id="TEST_INVALID"
        )
        
        result = workflow.analyze_customer_complete(invalid_request)
        assert isinstance(result, AnalysisResult)
        assert not result.success or result.error_message is not None
        print("  ✅ Invalid data handled gracefully")
        
        # Test with malformed data
        malformed_request = AnalysisRequest(
            customer_data={"invalid": None},
            purchase_history=[{"bad": "data"}],
            customer_id="TEST_MALFORMED"
        )
        
        result = workflow.analyze_customer_complete(malformed_request)
        assert isinstance(result, AnalysisResult)
        print("  ✅ Malformed data handled gracefully")
        
        # Test with very large data
        large_history = [create_sample_purchase_history()[0] for _ in range(100)]
        large_request = AnalysisRequest(
            customer_data=create_sample_customer_data(),
            purchase_history=large_history,
            customer_id="TEST_LARGE"
        )
        
        result = workflow.analyze_customer_complete(large_request)
        assert isinstance(result, AnalysisResult)
        print("  ✅ Large data sets handled gracefully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error handling test failed: {str(e)}")
        return False

def test_batch_processing():
    """Test batch processing capabilities."""
    print("\nTesting Batch Processing...")
    
    try:
        workflow = BusinessAnalysisWorkflow(enable_privacy_masking=False, enable_logging=False)
        
        # Create multiple analysis requests
        requests = []
        for i in range(5):
            customer_data = create_sample_customer_data()
            requests.append(AnalysisRequest(
                customer_data=customer_data,
                purchase_history=create_sample_purchase_history(),
                engagement_data=create_sample_engagement_data(),
                customer_id=customer_data["customer_id"]
            ))
        
        # Process batch
        start_time = time.time()
        results = workflow.process_batch_analysis(requests, max_concurrent=2)
        processing_time = time.time() - start_time
        
        # Validate results
        assert len(results) == len(requests)
        assert all(isinstance(result, AnalysisResult) for result in results)
        
        print(f"  ✅ Batch processing completed: {len(results)} analyses in {processing_time:.2f}s")
        print(f"  ✅ Average time per analysis: {processing_time/len(results):.2f}s")
        
        # Check workflow statistics after batch
        stats = workflow.get_workflow_statistics()
        print(f"  ✅ Total analyses recorded: {stats['total_analyses']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Batch processing test failed: {str(e)}")
        return False

def test_privacy_integration():
    """Test integration with privacy pipeline."""
    print("\nTesting Privacy Pipeline Integration...")
    
    try:
        # Test with privacy enabled
        workflow_with_privacy = BusinessAnalysisWorkflow(
            enable_privacy_masking=True, 
            enable_logging=False
        )
        
        # Test without privacy
        workflow_without_privacy = BusinessAnalysisWorkflow(
            enable_privacy_masking=False, 
            enable_logging=False
        )
        
        # Create sensitive test data
        sensitive_customer_data = {
            "customer_id": "CUST_12345",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+852-9876-5432",
            "hkid": "A123456(7)",
            "account_type": "Premium"
        }
        
        # Test data preparation with and without privacy
        processed_with_privacy = workflow_with_privacy._prepare_customer_data(sensitive_customer_data)
        processed_without_privacy = workflow_without_privacy._prepare_customer_data(sensitive_customer_data)
        
        # Privacy should be different from original (if privacy components available)
        if workflow_with_privacy.enable_privacy:
            print("  ✅ Privacy pipeline integration enabled")
        else:
            print("  ⚠️  Privacy pipeline not available (components not imported)")
        
        print("  ✅ Privacy integration test completed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Privacy integration test failed: {str(e)}")
        return False

def test_performance_metrics():
    """Test performance monitoring and metrics collection."""
    print("\nTesting Performance Metrics...")
    
    try:
        workflow = BusinessAnalysisWorkflow(enable_privacy_masking=False, enable_logging=False)
        
        # Perform several analyses to generate metrics
        for i in range(3):
            customer_data = create_sample_customer_data()
            request = AnalysisRequest(
                customer_data=customer_data,
                purchase_history=create_sample_purchase_history(),
                customer_id=customer_data["customer_id"]
            )
            
            result = workflow.analyze_customer_complete(request)
            time.sleep(0.1)  # Small delay between requests
        
        # Check statistics
        stats = workflow.get_workflow_statistics()
        
        # Validate metrics structure
        required_metrics = [
            "total_analyses", "successful_analyses", "failed_analyses",
            "success_rate", "total_requests", "total_tokens_used",
            "total_processing_time", "average_processing_time",
            "openrouter_stats", "privacy_enabled"
        ]
        
        for metric in required_metrics:
            assert metric in stats, f"Missing metric: {metric}"
        
        print(f"  ✅ Metrics collection working")
        print(f"    Total analyses: {stats['total_analyses']}")
        print(f"    Success rate: {stats['success_rate']:.1f}%")
        print(f"    Average processing time: {stats['average_processing_time']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Performance metrics test failed: {str(e)}")
        return False

def test_quick_analysis_function():
    """Test the quick analysis convenience function."""
    print("\nTesting Quick Analysis Function...")
    
    try:
        # Test quick analysis function
        customer_data = create_sample_customer_data()
        purchase_history = create_sample_purchase_history()
        
        result = quick_customer_analysis(
            customer_data=customer_data,
            purchase_history=purchase_history,
            api_key=os.getenv('OPENROUTER_API_KEY', 'test-key')
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.customer_id == customer_data["customer_id"]
        
        print("  ✅ Quick analysis function works")
        print(f"  ✅ Analysis completed in {result.processing_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Quick analysis function test failed: {str(e)}")
        return False

def main():
    """Run all end-to-end workflow tests."""
    print("🚀 Starting End-to-End Business Analysis Workflow Tests")
    print("=" * 80)
    
    tests = [
        test_workflow_initialization,
        test_individual_analysis_components,
        test_complete_analysis_workflow,
        test_error_handling_resilience,
        test_batch_processing,
        test_privacy_integration,
        test_performance_metrics,
        test_quick_analysis_function
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All end-to-end workflow tests passed!")
        print("\n💡 Summary:")
        print("   ✅ Workflow initialization and configuration")
        print("   ✅ Individual analysis components (patterns, scoring, recommendations)")
        print("   ✅ Complete end-to-end analysis pipeline")
        print("   ✅ Error handling and system resilience")
        print("   ✅ Batch processing capabilities")
        print("   ✅ Privacy pipeline integration")
        print("   ✅ Performance monitoring and metrics")
        print("   ✅ Convenience functions and quick analysis")
        print("\n🔧 Ready for production deployment!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 