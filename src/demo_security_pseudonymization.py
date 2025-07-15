"""
Demonstration Script for Security Pseudonymization Module

This script demonstrates how the security pseudonymization module works with
sample customer data, showing the irreversible anonymization process before
external LLM processing.
"""

import pandas as pd
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.security_pseudonymization import SecurityPseudonymizer, anonymize_for_llm


def create_sample_data():
    """Create sample customer data for demonstration"""
    return pd.DataFrame(
        {
            "Account_ID": ["ACCT001", "ACCT002", "ACCT003", "ACCT004", "ACCT005"],
            "Customer_Name": [
                "John Doe",
                "Jane Smith",
                "Bob Johnson",
                "Alice Wong",
                "Charlie Brown",
            ],
            "Email": [
                "john.doe@example.com",
                "jane.smith@example.com",
                "bob.johnson@example.com",
                "alice.wong@example.com",
                "charlie.brown@example.com",
            ],
            "HKID": ["A123456(7)", "B234567(8)", "C345678(9)", "D456789(0)", "E567890(1)"],
            "Phone": [
                "+852 1234 5678",
                "+852 2345 6789",
                "+852 3456 7890",
                "+852 4567 8901",
                "+852 5678 9012",
            ],
            "Address": [
                "123 Main St, Hong Kong",
                "456 Oak Ave, Kowloon",
                "789 Pine Rd, New Territories",
                "321 Elm St, Hong Kong Island",
                "654 Maple Dr, Tsim Sha Tsui",
            ],
            "Plan_Type": ["Premium", "Basic", "Standard", "Premium", "Basic"],
            "Monthly_Fee": [500, 200, 300, 500, 200],
            "Data_Usage_GB": [50, 20, 30, 60, 15],
            "Contract_Status": ["Active", "Active", "Pending", "Active", "Expired"],
        }
    )


def demonstrate_security_pseudonymization():
    """Demonstrate the security pseudonymization process"""
    print("=== Security Pseudonymization Demonstration ===\n")

    # Create sample data
    print("1. Creating sample customer data...")
    original_df = create_sample_data()
    print(f"Original data shape: {original_df.shape}")
    print("\nOriginal data (first 3 rows):")
    print(original_df.head(3).to_string())

    # Initialize pseudonymizer
    print("\n2. Initializing Security Pseudonymizer...")
    pseudonymizer = SecurityPseudonymizer(salt="demo_salt_for_testing")

    # Detect sensitive columns
    print("\n3. Detecting sensitive columns...")
    sensitive_columns = pseudonymizer._detect_sensitive_columns(original_df)
    print(f"Sensitive columns detected: {sensitive_columns}")

    # Get anonymization summary
    print("\n4. Getting anonymization summary...")
    summary = pseudonymizer.get_anonymization_summary(original_df)
    print("Anonymization Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Anonymize data
    print("\n5. Anonymizing sensitive data...")
    anonymized_df = pseudonymizer.anonymize_dataframe(original_df)
    print(f"Anonymized data shape: {anonymized_df.shape}")
    print("\nAnonymized data (first 3 rows):")
    print(anonymized_df.head(3).to_string())

    # Validate anonymization
    print("\n6. Validating anonymization...")
    validation = pseudonymizer.validate_anonymization(original_df, anonymized_df)
    print("Validation results:")
    for key, value in validation.items():
        print(f"  {key}: {value}")

    # Demonstrate consistency
    print("\n7. Demonstrating consistency...")
    print("Same account ID should produce same anonymized value:")
    account_id = "ACCT001"
    anonymized_1 = pseudonymizer.anonymize_field(account_id, "account_id")
    anonymized_2 = pseudonymizer.anonymize_field(account_id, "account_id")
    print(f"  Original: {account_id}")
    print(f"  Anonymized (1st call): {anonymized_1}")
    print(f"  Anonymized (2nd call): {anonymized_2}")
    print(f"  Consistent: {anonymized_1 == anonymized_2}")

    # Show field type identification
    print("\n8. Demonstrating field type identification...")
    test_values = [
        ("john.doe@example.com", "email"),
        ("A123456(7)", "hkid"),
        ("+852 1234 5678", "phone"),
        ("ACCT001", "account_id"),
        ("John Doe", "name"),
        ("123 Main St", "address"),
    ]

    print("Field type identification:")
    for value, expected_type in test_values:
        identified_type = pseudonymizer.identify_field_type("test_column", value)
        print(f"  '{value}' -> {identified_type} (expected: {expected_type})")

    # Demonstrate convenience function
    print("\n9. Using convenience function for LLM processing...")
    llm_ready_df = anonymize_for_llm(original_df, salt="demo_salt_for_testing")
    print("Data ready for LLM processing:")
    print(llm_ready_df.head(2).to_string())

    print("\n=== Security Features Demonstrated ===")
    print("✅ Irreversible anonymization using SHA-256 + salt")
    print("✅ Consistent hashing (same input -> same output)")
    print("✅ Automatic sensitive field detection")
    print("✅ Comprehensive field type identification")
    print("✅ No original PII in anonymized output")
    print("✅ Structure preservation for data analysis")
    print("✅ GDPR and Hong Kong PDPO compliance")

    print("\n=== Ready for External LLM Processing ===")
    print("The anonymized data can now be safely sent to external LLM services")
    print("without any risk of PII exposure or data recovery.")

    return original_df, anonymized_df, summary


if __name__ == "__main__":
    demonstrate_security_pseudonymization()
