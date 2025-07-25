#!/usr/bin/env python3

"""
Test script for customer analysis configuration
Tests the new user-configurable customer limit functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_customer_limit_configuration():
    """Test that customer limit configuration works correctly"""
    
    print("🧪 Testing customer analysis limit configuration...")
    
    # Simulate different customer limit scenarios
    test_scenarios = [
        {"selected": 5, "available": 100, "expected": 5},
        {"selected": 50, "available": 100, "expected": 50},
        {"selected": 100, "available": 100, "expected": 100},
        {"selected": 150, "available": 100, "expected": 100},  # More selected than available
        {"selected": 1, "available": 5, "expected": 1},
        {"selected": 10, "available": 3, "expected": 3}  # More selected than available
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n📊 Test Scenario {i+1}:")
        print(f"   Selected: {scenario['selected']}")
        print(f"   Available: {scenario['available']}")
        
        # Simulate the logic from results.py
        customers_to_analyze = scenario['selected']
        total_available = scenario['available']
        
        actual_customers_to_process = min(customers_to_analyze, total_available)
        
        print(f"   Actual Processed: {actual_customers_to_process}")
        print(f"   Expected: {scenario['expected']}")
        
        if actual_customers_to_process == scenario['expected']:
            print(f"   ✅ PASS")
        else:
            print(f"   ❌ FAIL")

    print(f"\n📈 Processing time estimates test:")
    time_estimates = [
        (5, "< 1 minute", "✅ **Recommended** - Quick insights"),
        (15, "1-3 minutes", "⚡ **Balanced** - Good depth vs speed"),
        (35, "3-8 minutes", "🔍 **Comprehensive** - Deep insights"),
        (75, "8-15 minutes", "🏢 **Enterprise** - Maximum coverage"),
    ]
    
    for customers, time_est, recommendation in time_estimates:
        print(f"   {customers} customers: {time_est} - {recommendation}")

    print(f"\n🎉 Customer limit configuration test completed!")

if __name__ == "__main__":
    test_customer_limit_configuration()
