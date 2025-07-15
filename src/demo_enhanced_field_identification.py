"""
Demonstration Script for Enhanced Field Identification Module

This script demonstrates the enhanced field identification capabilities including:
- Comprehensive PII coverage (passport, credit card, etc.)
- Hong Kong-specific pattern matching
- Confidence scoring and accuracy improvements
- Configurable sensitivity rules
"""

import pandas as pd
import sys
import os
import json
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.enhanced_field_identification import (
    EnhancedFieldIdentifier,
    FieldType,
    create_field_identifier,
    analyze_dataframe_fields,
    get_sensitive_columns_enhanced
)

def create_comprehensive_sample_data():
    """Create comprehensive sample data with various PII types"""
    return pd.DataFrame({
        # Basic customer information
        'Account_ID': ['ACCT001', 'ACCT002', 'ACCT003', 'ACCT004', 'ACCT005'],
        'Customer_Name': ['John Doe', 'Jane Smith', 'Wong Tai Sin', 'Alice Chen', 'Bob Johnson'],
        'Email': ['john.doe@example.com', 'jane.smith@company.hk', 'wong.taixin@gmail.com', 
                 'alice.chen@outlook.com', 'bob.johnson@yahoo.com'],
        
        # Hong Kong-specific identifiers
        'HKID': ['A123456(7)', 'B234567(8)', 'C345678(9)', 'D456789(0)', 'E567890(1)'],
        'Phone': ['+852 1234 5678', '23456789', '+852 3456 7890', '45678901', '+852 5678 9012'],
        'Address': ['Flat 5A, 123 Nathan Road, Kowloon', 'Suite 1001, Tower 2, Hong Kong',
                   '789 Pine Road, New Territories', 'Room 15B, 321 Queen\'s Road, Central',
                   'Apartment 8C, 654 Maple Street, Tsim Sha Tsui'],
        
        # Extended PII types
        'Passport': ['A12345678', 'B87654321', 'C11223344', 'D99887766', 'E55443322'],
        'Credit_Card': ['4111111111111111', '5555555555554444', '378282246310005', 
                       '6011111111111117', '30569309025904'],
        'Bank_Account': ['123-456789-001', '987-654321-002', '456-789123-003', 
                        '789-123456-004', '321-987654-005'],
        'Date_of_Birth': ['1990-01-15', '1985-05-22', '1992-09-08', '1988-12-03', '1995-07-18'],
        'IP_Address': ['192.168.1.1', '10.0.0.1', '172.16.0.1', '203.198.23.45', '127.0.0.1'],
        
        # Non-sensitive data
        'Plan_Type': ['Premium', 'Basic', 'Standard', 'Premium', 'Basic'],
        'Monthly_Fee': [500, 200, 300, 500, 200],
        'Data_Usage_GB': [50, 20, 30, 60, 15],
        'Contract_Status': ['Active', 'Active', 'Pending', 'Active', 'Expired'],
        'Region': ['Hong Kong Island', 'Kowloon', 'New Territories', 'Hong Kong Island', 'Kowloon']
    })

def demonstrate_enhanced_field_identification():
    """Demonstrate the enhanced field identification capabilities"""
    print("=== Enhanced Field Identification Demonstration ===\n")
    
    # Create comprehensive sample data
    print("1. Creating comprehensive sample data with various PII types...")
    df = create_comprehensive_sample_data()
    print(f"Sample data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Initialize enhanced field identifier
    print("\n2. Initializing Enhanced Field Identifier...")
    identifier = EnhancedFieldIdentifier()
    print(f"Sensitivity threshold: {identifier.sensitivity_threshold}")
    print(f"Number of field patterns loaded: {len(identifier.patterns)}")
    
    # Analyze the entire DataFrame
    print("\n3. Analyzing all fields in the DataFrame...")
    analysis_results = identifier.analyze_dataframe(df)
    
    print("\nField Analysis Results:")
    print("-" * 80)
    print(f"{'Column Name':<20} {'Field Type':<15} {'Confidence':<12} {'Sensitive':<10} {'Method':<15}")
    print("-" * 80)
    
    for column, result in analysis_results.items():
        print(f"{column:<20} {result.field_type.value:<15} {result.confidence:<12.2f} "
              f"{result.is_sensitive:<10} {result.method:<15}")
    
    # Get sensitive columns
    print("\n4. Identifying sensitive columns...")
    sensitive_columns = identifier.get_sensitive_columns(df)
    print(f"Sensitive columns ({len(sensitive_columns)}): {sensitive_columns}")
    
    # Get field summary
    print("\n5. Getting comprehensive field summary...")
    summary = identifier.get_field_summary(df)
    print("Field Summary:")
    print(f"  Total columns: {summary['total_columns']}")
    print(f"  Sensitive columns: {summary['sensitive_columns']}")
    print(f"  High confidence columns: {summary['high_confidence_columns']}")
    print(f"  Hong Kong specific fields: {summary['hong_kong_specific_fields']}")
    
    print("\n  Field type breakdown:")
    for field_type, count in summary['field_type_breakdown'].items():
        print(f"    {field_type}: {count}")
    
    # Demonstrate Hong Kong-specific patterns
    print("\n6. Demonstrating Hong Kong-specific pattern recognition...")
    hk_test_data = {
        'HKID': ['A123456(7)', 'AB123456(8)', 'C999999(0)'],
        'HK_Phone': ['+852 1234 5678', '12345678', '+852-9876-5432'],
        'HK_Address': ['Flat 10A, 123 Nathan Road, Kowloon', 
                      'Suite 2001, IFC Tower, Central, Hong Kong',
                      'Room 5B, 456 Queen\'s Road, Wan Chai']
    }
    
    for field_name, values in hk_test_data.items():
        result = identifier.identify_field(field_name, values)
        print(f"  {field_name}: {result.field_type.value} (confidence: {result.confidence:.2f})")
    
    # Demonstrate confidence scoring
    print("\n7. Demonstrating confidence scoring...")
    confidence_test_cases = [
        ('email', ['john@example.com', 'jane@test.org', 'valid@email.com']),
        ('maybe_phone', ['123456789', '987654321', '555123456']),
        ('random_data', ['abc', 'def', 'ghi']),
        ('credit_card', ['4111111111111111', '5555555555554444', '378282246310005'])
    ]
    
    print("Confidence scoring examples:")
    for field_name, values in confidence_test_cases:
        result = identifier.identify_field(field_name, values)
        print(f"  {field_name}: {result.field_type.value} (confidence: {result.confidence:.2f}, "
              f"sensitive: {result.is_sensitive})")
    
    # Test sensitivity threshold adjustment
    print("\n8. Testing sensitivity threshold adjustment...")
    print(f"Current threshold: {identifier.sensitivity_threshold}")
    
    # Count sensitive fields at current threshold
    current_sensitive = len(identifier.get_sensitive_columns(df))
    print(f"Sensitive fields at current threshold: {current_sensitive}")
    
    # Adjust threshold and recount
    identifier.set_sensitivity_threshold(0.8)
    high_threshold_sensitive = len(identifier.get_sensitive_columns(df))
    print(f"Sensitive fields at threshold 0.8: {high_threshold_sensitive}")
    
    identifier.set_sensitivity_threshold(0.4)
    low_threshold_sensitive = len(identifier.get_sensitive_columns(df))
    print(f"Sensitive fields at threshold 0.4: {low_threshold_sensitive}")
    
    # Reset to original threshold
    identifier.set_sensitivity_threshold(0.6)
    
    # Demonstrate extended PII types
    print("\n9. Demonstrating extended PII type detection...")
    extended_pii_examples = {
        'Passport Numbers': ['A12345678', 'B87654321', 'UK123456789'],
        'Credit Cards': ['4111111111111111', '5555555555554444', '378282246310005'],
        'Bank Accounts': ['123-456789-001', '987654321', 'GB82WEST12345698765432'],
        'IP Addresses': ['192.168.1.1', '2001:0db8:85a3:0000:0000:8a2e:0370:7334'],
        'Dates of Birth': ['1990-01-15', '01/15/1990', '15-01-1990']
    }
    
    for pii_type, examples in extended_pii_examples.items():
        result = identifier.identify_field(pii_type.lower().replace(' ', '_'), examples)
        print(f"  {pii_type}: {result.field_type.value} (confidence: {result.confidence:.2f})")
    
    # Performance demonstration
    print("\n10. Performance demonstration with large dataset...")
    import time
    
    # Create larger dataset
    large_df = pd.DataFrame({
        'Account_ID': [f'ACCT{i:06d}' for i in range(1000)],
        'Email': [f'user{i}@example.com' for i in range(1000)],
        'HKID': [f'A{i:06d}(7)' for i in range(1000)],
        'Plan_Type': (['Premium', 'Basic', 'Standard'] * 334)[:1000]
    })
    
    start_time = time.time()
    large_analysis = identifier.analyze_dataframe(large_df)
    end_time = time.time()
    
    print(f"  Analyzed {large_df.shape[0]} rows x {large_df.shape[1]} columns")
    print(f"  Processing time: {end_time - start_time:.2f} seconds")
    print(f"  Sensitive columns identified: {len([r for r in large_analysis.values() if r.is_sensitive])}")
    
    # Export configuration demonstration
    print("\n11. Configuration export/import demonstration...")
    config_path = "demo_field_config.json"
    identifier.export_configuration(config_path)
    print(f"Configuration exported to {config_path}")
    
    # Show what's in the config file
    with open(config_path, 'r') as f:
        config = json.load(f)
    print(f"Configuration contains {len(config['patterns'])} patterns")
    
    # Clean up
    os.remove(config_path)
    
    print("\n=== Enhanced Features Summary ===")
    print("✅ Comprehensive PII Coverage:")
    print("   - Account IDs, HKID, Email, Phone, Names, Addresses")
    print("   - Passport, Driver's License, Credit Cards, Bank Accounts")
    print("   - IP Addresses, Dates of Birth, and more")
    print("✅ Hong Kong-specific Pattern Matching:")
    print("   - HKID formats (A123456(7), AB123456(8))")
    print("   - Hong Kong phone formats (+852 1234 5678, 12345678)")
    print("   - Hong Kong address patterns (Flat 5A, Suite 1001)")
    print("✅ Improved Accuracy:")
    print("   - Context-aware identification (column names + values)")
    print("   - Confidence scoring for detection quality")
    print("   - False positive reduction")
    print("✅ Configuration and Extensibility:")
    print("   - Adjustable sensitivity thresholds")
    print("   - Custom pattern support")
    print("   - Export/import configuration")
    print("✅ Performance Optimized:")
    print("   - Efficient processing for large datasets")
    print("   - Quick analysis of 1000+ rows")
    
    return df, analysis_results, summary

def demonstrate_utility_functions():
    """Demonstrate utility functions for easy integration"""
    print("\n=== Utility Functions Demonstration ===\n")
    
    # Create sample data
    df = pd.DataFrame({
        'Account_ID': ['ACCT001', 'ACCT002'],
        'Email': ['john@example.com', 'jane@example.com'],
        'HKID': ['A123456(7)', 'B234567(8)'],
        'Plan_Type': ['Premium', 'Basic']
    })
    
    # Test utility functions
    print("1. Using create_field_identifier()...")
    identifier = create_field_identifier()
    print(f"   Created identifier with {len(identifier.patterns)} patterns")
    
    print("\n2. Using analyze_dataframe_fields()...")
    results = analyze_dataframe_fields(df)
    print(f"   Analyzed {len(results)} fields")
    
    print("\n3. Using get_sensitive_columns_enhanced()...")
    sensitive_cols = get_sensitive_columns_enhanced(df)
    print(f"   Found {len(sensitive_cols)} sensitive columns: {sensitive_cols}")
    
    print("\n✅ Utility functions provide easy integration with existing code")

if __name__ == "__main__":
    df, analysis, summary = demonstrate_enhanced_field_identification()
    demonstrate_utility_functions() 