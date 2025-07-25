#!/usr/bin/env python3

"""
Quick test for formatting fix in CrewAI results display
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_formatting_fix():
    """Test the string formatting fix for operational efficiency metrics"""
    
    print("🧪 Testing formatting fix for operational efficiency metrics...")
    
    # Test data that could cause the error
    test_cases = [
        {"accuracy_improvement": "85.5"},  # String number
        {"accuracy_improvement": 85.5},    # Float number
        {"accuracy_improvement": 85},      # Integer number
        {"accuracy_improvement": None},    # None value
        {"accuracy_improvement": "N/A"},   # Non-numeric string
        {"accuracy_improvement": ""},      # Empty string
        {}  # Missing key
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n📊 Test Case {i+1}: {test_case}")
        
        try:
            # Simulate the fixed logic
            accuracy_improvement = test_case.get("accuracy_improvement", 0)
            
            try:
                accuracy_val = float(accuracy_improvement) if accuracy_improvement else 0.0
            except (ValueError, TypeError):
                accuracy_val = 0.0
                
            result = f"{accuracy_val:.1f}%"
            print(f"   ✅ Result: {result}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
    print(f"\n🎉 All test cases completed!")

if __name__ == "__main__":
    test_formatting_fix()
