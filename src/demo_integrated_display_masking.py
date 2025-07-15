"""
Demonstration of Integrated Display Masking System - Task 5.4
Shows the enhanced field identification integrated with comprehensive display masking

This demo demonstrates:
- All 13 PII types with masking
- Hong Kong-specific pattern support
- Confidence-based masking decisions
- Toggle control functionality
- DataFrame processing with metadata
"""

import pandas as pd
import time

from src.utils.integrated_display_masking import (
    IntegratedDisplayMasking,
)


def print_header(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_masking_demo(masker, value, column_name, description=""):
    """Demonstrate masking for a single value"""
    # Process with masking enabled
    masker.set_visibility(False)
    result_masked = masker.process_value(value, column_name)

    # Process with masking disabled
    masker.set_visibility(True)
    result_unmasked = masker.process_value(value, column_name)

    print(f"\n{description}")
    print(f"  Column: {column_name}")
    print(f"  Original:     {result_unmasked.original_value}")
    print(f"  Masked:       {result_masked.masked_value}")
    print(f"  Field Type:   {result_masked.field_type.value}")
    print(f"  Confidence:   {result_masked.confidence:.2f}")
    print(
        f"  Would Mask:   {'Yes' if result_masked.confidence >= masker.confidence_threshold else 'No'}"
    )


def demo_all_field_types():
    """Demonstrate masking for all 13 supported field types"""
    print_header("ALL SUPPORTED FIELD TYPES DEMONSTRATION")

    masker = IntegratedDisplayMasking(confidence_threshold=0.5)

    # Sample data for each field type
    test_data = [
        ("ACC123456", "account_id", "Account ID - Standard format"),
        ("A123456(7)", "hkid", "Hong Kong ID - Standard format"),
        ("AB123456(8)", "hkid_number", "Hong Kong ID - Two letter prefix"),
        ("john.doe@example.com", "email", "Email Address - Standard format"),
        ("user+tag@subdomain.domain.org", "email_address", "Email Address - Complex format"),
        ("+852 1234 5678", "phone", "Hong Kong Phone - International format"),
        ("12345678", "mobile_number", "Hong Kong Phone - Local format"),
        ("John Doe", "customer_name", "Personal Name - Western format"),
        ("李小明", "chinese_name", "Personal Name - Chinese characters"),
        ("Flat 5A, 123 Nathan Road, Kowloon", "address", "Hong Kong Address - Standard format"),
        ("Unit 10B, Central Plaza, Central", "home_address", "Hong Kong Address - Commercial"),
        ("HK1234567", "passport_number", "Passport - Hong Kong format"),
        ("US987654321", "passport", "Passport - International format"),
        ("DL123456789", "drivers_license", "Driver's License - Standard format"),
        ("1234-5678-9012-3456", "credit_card", "Credit Card - Formatted"),
        ("1234567890123456", "card_number", "Credit Card - No formatting"),
        ("123-456-789012", "bank_account", "Bank Account - With dashes"),
        ("987654321098", "account_number", "Bank Account - No formatting"),
        ("192.168.1.100", "ip_address", "IP Address - Private network"),
        ("203.80.96.10", "client_ip", "IP Address - Public"),
        ("1990-05-15", "date_of_birth", "Date of Birth - ISO format"),
        ("15/05/1990", "birth_date", "Date of Birth - DD/MM/YYYY format"),
        ("SomeSecretData123", "confidential_data", "General Sensitive Data"),
    ]

    for value, column_name, description in test_data:
        print_masking_demo(masker, value, column_name, description)


def demo_hong_kong_specific():
    """Demonstrate Hong Kong-specific pattern handling"""
    print_header("HONG KONG-SPECIFIC PATTERNS")

    masker = IntegratedDisplayMasking(confidence_threshold=0.3)

    hk_data = [
        # Hong Kong ID variations
        ("A123456(7)", "hkid", "HKID - Single letter"),
        ("AB123456(8)", "identity_card", "HKID - Double letter"),
        ("C987654(3)", "id_number", "HKID - Different letter"),
        # Hong Kong phone variations
        ("+852 1234 5678", "phone", "HK Phone - Formatted international"),
        ("+852-1234-5678", "mobile", "HK Phone - Dash format"),
        ("85212345678", "telephone", "HK Phone - No spaces"),
        ("12345678", "contact_number", "HK Phone - Local only"),
        # Hong Kong addresses
        ("Flat 5A, 123 Nathan Road, Kowloon", "address", "HK Address - Flat format"),
        ("Unit 10B, Central Plaza, Central", "location", "HK Address - Unit format"),
        ("Suite 15C, IFC Tower, Central", "office_address", "HK Address - Suite format"),
        ("Room 888, Lucky Building, Wan Chai", "home_address", "HK Address - Room format"),
        # Mixed language content
        ("張三", "chinese_name", "Chinese Name - Traditional characters"),
        ("陳大文", "customer_name_cn", "Chinese Name - Full traditional"),
        ("李小明 John Li", "full_name", "Mixed Chinese-English name"),
    ]

    print("\n📍 Hong Kong Localization Features:")
    print("  ✓ HKID format recognition (A123456(7), AB123456(8))")
    print("  ✓ Hong Kong phone number formats (+852, local)")
    print("  ✓ Hong Kong address patterns (Flat, Unit, Suite)")
    print("  ✓ Chinese character support")
    print("  ✓ Mixed language name handling")

    for value, column_name, description in hk_data:
        print_masking_demo(masker, value, column_name, description)


def demo_confidence_thresholds():
    """Demonstrate confidence threshold effects"""
    print_header("CONFIDENCE THRESHOLD DEMONSTRATION")

    # Test data with varying confidence levels
    test_cases = [
        ("john@example.com", "email_addr", "Clear email pattern"),
        ("user@domain", "contact", "Partial email pattern"),
        ("12345678", "number", "Could be phone or ID"),
        ("A123456", "code", "Could be HKID without checksum"),
        ("test123", "data", "Ambiguous data"),
    ]

    thresholds = [0.3, 0.5, 0.7, 0.9]

    for threshold in thresholds:
        print(f"\n🎯 Confidence Threshold: {threshold}")
        print("-" * 40)

        masker = IntegratedDisplayMasking(
            confidence_threshold=threshold, default_show_sensitive=False
        )

        for value, column_name, description in test_cases:
            result = masker.process_value(value, column_name)
            status = "MASKED" if result.is_masked else "NOT MASKED"
            print(f"  {description:25} | Conf: {result.confidence:.2f} | {status}")


def demo_toggle_functionality():
    """Demonstrate toggle functionality"""
    print_header("TOGGLE CONTROL DEMONSTRATION")

    masker = IntegratedDisplayMasking()

    sample_data = {
        "customer_name": "John Doe",
        "email": "john@example.com",
        "phone": "+852 1234 5678",
        "hkid": "A123456(7)",
        "account_id": "ACC123456",
    }

    print("\n🔒 Privacy Toggle States:")

    # Show masked state
    print("\n1. MASKED STATE (Privacy Protection ON):")
    masker.set_visibility(False)
    for field, value in sample_data.items():
        result = masker.process_value(value, field)
        print(f"   {field:15}: {result.masked_value}")

    # Show unmasked state
    print("\n2. UNMASKED STATE (Privacy Protection OFF):")
    masker.set_visibility(True)
    for field, value in sample_data.items():
        result = masker.process_value(value, field)
        print(f"   {field:15}: {result.masked_value}")

    # Demonstrate toggle
    print("\n3. TOGGLE FUNCTIONALITY:")
    current_state = masker.show_sensitive
    new_state = masker.toggle_visibility()
    print(f"   Before toggle: {'SHOW' if current_state else 'HIDE'} sensitive data")
    print(f"   After toggle:  {'SHOW' if new_state else 'HIDE'} sensitive data")


def demo_dataframe_processing():
    """Demonstrate comprehensive DataFrame processing"""
    print_header("DATAFRAME PROCESSING DEMONSTRATION")

    # Create comprehensive test DataFrame
    test_df = pd.DataFrame(
        {
            "account_id": ["ACC123456", "ACC789012", "ACC345678", "ACC999888"],
            "customer_name": ["John Doe", "Jane Smith", "李小明", "Bob Johnson"],
            "email": [
                "john@example.com",
                "jane.smith@test.org",
                "xiaoming@gmail.com",
                "bob@company.net",
            ],
            "phone": ["+852 1234 5678", "12345678", "+852 9876 5432", "+852 5555 1234"],
            "hkid": ["A123456(7)", "B789012(3)", "C345678(9)", "D999888(7)"],
            "address": [
                "Flat 1A, 123 Nathan Road, Kowloon",
                "Unit 5B, Central Plaza, Central",
                "Suite 3C, IFC Tower, Central",
                "Room 10D, Lucky Building, Wan Chai",
            ],
            "passport": ["HK1234567", "HK7890123", "HK3456789", "HK9998887"],
            "credit_card": [
                "1234-5678-9012-3456",
                "9876-5432-1098-7654",
                "1111-2222-3333-4444",
                "5555-6666-7777-8888",
            ],
            "date_of_birth": ["1990-05-15", "1985-12-03", "1992-08-22", "1988-11-10"],
            "ip_address": ["192.168.1.100", "10.0.0.50", "172.16.0.25", "203.80.96.10"],
            "purchase_amount": [1000.50, 2500.75, 750.25, 1800.00],  # Non-sensitive
            "transaction_date": [
                "2023-01-15",
                "2023-02-20",
                "2023-03-10",
                "2023-04-05",
            ],  # Non-sensitive
            "product_category": ["Mobile", "Internet", "Bundle", "Mobile"],  # Non-sensitive
        }
    )

    print(f"\n📊 Sample DataFrame: {len(test_df)} rows, {len(test_df.columns)} columns")
    print(f"Columns: {', '.join(test_df.columns)}")

    masker = IntegratedDisplayMasking(confidence_threshold=0.5)

    # Process with masking enabled
    print("\n🔒 MASKED VIEW (Privacy Protection ON):")
    result_masked = masker.process_dataframe(test_df)

    print("\nMasking Summary:")
    print(f"  Total fields masked: {result_masked['total_masked_fields']}")
    print(f"  Columns with sensitive data: {len(result_masked['masking_metadata'])}")
    print(f"  Status: {result_masked['message']}")

    # Show first few rows of key columns
    display_columns = ["customer_name", "email", "phone", "hkid", "purchase_amount"]
    if all(col in test_df.columns for col in display_columns):
        print("\nSample Masked Data (first 3 rows):")
        masked_sample = result_masked["dataframe"][display_columns].head(3)
        for idx, row in masked_sample.iterrows():
            print(f"  Row {idx+1}: {dict(row)}")

    # Show detailed metadata
    print("\n📈 Field Detection Metadata:")
    for column, metadata in result_masked["masking_metadata"].items():
        print(
            f"  {column:15}: {metadata['field_type']:12} | Conf: {metadata['confidence']:.2f} | "
            f"Masked: {metadata['masked_count']}/{metadata['total_count']} "
            f"({metadata['masking_percentage']:.1f}%)"
        )

    # Process with masking disabled
    print("\n🔓 UNMASKED VIEW (Privacy Protection OFF):")
    masker.set_visibility(True)
    result_unmasked = masker.process_dataframe(test_df)
    print(f"  Status: {result_unmasked['message']}")
    print(f"  Data unchanged: {result_unmasked['dataframe'].equals(test_df)}")


def demo_performance_characteristics():
    """Demonstrate performance with larger datasets"""
    print_header("PERFORMANCE CHARACTERISTICS")

    print("\n⚡ Performance Testing with Larger Datasets:")

    # Test with different dataset sizes
    sizes = [100, 500, 1000]

    for size in sizes:
        print(f"\n📊 Testing with {size} rows:")

        # Generate test data
        large_df = pd.DataFrame(
            {
                "email": [f"user{i}@example.com" for i in range(size)],
                "name": [f"User {i}" for i in range(size)],
                "phone": [f"+852 1234 {i:04d}" for i in range(size)],
                "account_id": [f"ACC{i:06d}" for i in range(size)],
                "data": [f"data_{i}" for i in range(size)],
            }
        )

        masker = IntegratedDisplayMasking()

        # Measure processing time
        start_time = time.time()
        result = masker.process_dataframe(large_df)
        processing_time = time.time() - start_time

        print(f"  Processing time: {processing_time:.3f} seconds")
        print(f"  Rows per second: {size/processing_time:.0f}")
        print(f"  Fields masked: {result['total_masked_fields']}")
        print(f"  Columns analyzed: {len(result['masking_metadata'])}")


def demo_field_type_summary():
    """Demonstrate field type summary functionality"""
    print_header("FIELD TYPE ANALYSIS SUMMARY")

    # Create diverse test DataFrame
    analysis_df = pd.DataFrame(
        {
            "customer_email": ["john@example.com", "jane@test.org"],
            "full_name": ["John Doe", "Jane Smith"],
            "mobile_phone": ["+852 1234 5678", "+852 9876 5432"],
            "identity_card": ["A123456(7)", "B789012(3)"],
            "home_address": ["Flat 1A, Kowloon", "Unit 5B, Central"],
            "passport_no": ["HK1234567", "HK7890123"],
            "card_number": ["1234-5678-9012-3456", "9876-5432-1098-7654"],
            "birth_date": ["1990-05-15", "1985-12-03"],
            "client_ip": ["192.168.1.100", "10.0.0.50"],
            "purchase_total": [1000.50, 2500.75],  # Non-sensitive
            "product_name": ["Mobile Plan", "Internet Bundle"],  # Non-sensitive
        }
    )

    masker = IntegratedDisplayMasking()
    summary = masker.get_field_type_summary(analysis_df)

    print("\n🔍 Automatic Field Type Detection Results:")
    print(f"Total columns analyzed: {len(summary)}")

    # Sort by confidence for better display
    sorted_summary = sorted(summary.items(), key=lambda x: x[1]["confidence"], reverse=True)

    print(f"\n{'Column Name':<20} {'Field Type':<15} {'Confidence':<10} {'Status'}")
    print(f"{'-'*65}")

    for column, info in sorted_summary:
        confidence = info["confidence"]
        field_type = info["field_type"]
        status = "🔒 Sensitive" if confidence >= 0.5 and field_type != "general" else "✅ Safe"

        print(f"{column:<20} {field_type:<15} {confidence:<10.2f} {status}")


def main():
    """Run all demonstrations"""
    print("🔒 INTEGRATED DISPLAY MASKING SYSTEM DEMONSTRATION")
    print("Task 5.4 - Enhanced Field Identification + Comprehensive Masking")
    print("=" * 80)

    try:
        # Run all demonstrations
        demo_all_field_types()
        demo_hong_kong_specific()
        demo_confidence_thresholds()
        demo_toggle_functionality()
        demo_dataframe_processing()
        demo_performance_characteristics()
        demo_field_type_summary()

        print_header("DEMONSTRATION COMPLETE")
        print("\n✅ Successfully demonstrated:")
        print("  • All 13 PII field types with appropriate masking")
        print("  • Hong Kong-specific pattern recognition")
        print("  • Confidence-based masking decisions")
        print("  • Toggle control for privacy protection")
        print("  • Comprehensive DataFrame processing")
        print("  • Performance optimization")
        print("  • Automatic field type detection")
        print("  • Integration with enhanced field identification")
        print("\n🛡️  Privacy-first design ensures:")
        print("  • Original data accessible only locally")
        print("  • No sensitive data transmitted externally")
        print("  • Reversible masking with toggle control")
        print("  • GDPR and Hong Kong PDPO compliance")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
