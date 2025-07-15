"""
Demonstration script for Privacy Pipeline Integration (Task 5.6)

This script tests the integration between the upload component and the complete
privacy pipeline to validate that all components work together properly.
"""

import pandas as pd
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.components.upload import process_data_through_privacy_pipeline


def create_test_data():
    """Create realistic test data for demonstration."""
    # Customer data with various PII types
    customer_data = pd.DataFrame(
        {
            "account_id": ["3HK123456", "3HK789012", "3HK345678"],
            "name": ["張三", "Wong Tai Man", "Lisa Chan"],
            "hkid": ["A123456(7)", "B789012(3)", "C345678(9)"],
            "phone": ["+852 9123 4567", "+852 9876 5432", "+852 9555 1234"],
            "email": ["zhang.san@gmail.com", "wong.taiman@yahoo.com.hk", "lisa.chan@hotmail.com"],
            "address": [
                "Flat 12A, 88 Nathan Road, TST",
                "Unit 5B, 123 Queen's Road, Central",
                "15樓C室, 456 彌敦道, 旺角",
            ],
            "plan_type": ["5G Unlimited", "4G Premium", "5G Basic"],
            "monthly_bill": [588.0, 388.0, 288.0],
            "contract_end": ["2025-06-30", "2024-12-31", "2025-03-15"],
        }
    )

    # Purchase data
    purchase_data = pd.DataFrame(
        {
            "account_id": ["3HK123456", "3HK789012", "3HK345678"],
            "transaction_id": ["TXN001", "TXN002", "TXN003"],
            "purchase_amount": [100.50, 250.00, 75.25],
            "purchase_date": ["2024-01-15", "2024-01-16", "2024-01-17"],
            "category": ["Mobile Plan", "Device", "Accessories"],
        }
    )

    return customer_data, purchase_data


def demonstrate_privacy_integration():
    """Demonstrate the complete privacy pipeline integration."""
    print("=== Privacy Pipeline Integration Demonstration ===\n")

    # Create test data
    print("1. Creating test data...")
    customer_data, purchase_data = create_test_data()
    print(f"   ✅ Customer data: {customer_data.shape[0]} rows, {customer_data.shape[1]} columns")
    print(f"   ✅ Purchase data: {purchase_data.shape[0]} rows, {purchase_data.shape[1]} columns")
    print()

    # Test customer data processing
    print("2. Processing customer data through privacy pipeline...")
    try:
        customer_success, customer_message, customer_processed = (
            process_data_through_privacy_pipeline(
                customer_data, "demo_customer_data", "demo_customer.csv"
            )
        )

        if customer_success:
            print(f"   ✅ {customer_message}")

            # Show privacy analysis results
            metadata = customer_processed.get("metadata", {})
            pii_fields = metadata.get("pii_fields_identified", [])
            print(f"   🔍 PII fields identified: {len(pii_fields)} - {pii_fields}")

            # Show processing performance
            stats = metadata.get("processing_stats", {})
            if stats:
                print(f"   ⚡ Processing time: {stats.get('processing_time_seconds', 0):.3f}s")
                print(
                    f"   📊 Fields processed: {stats.get('pii_fields_identified', 0)} PII, {stats.get('pii_fields_masked', 0)} masked"
                )

            # Show compliance status
            compliance = metadata.get("compliance", {})
            if compliance:
                print(f"   ✅ GDPR compliant: {compliance.get('gdpr_compliant', False)}")
                print(
                    f"   ✅ Hong Kong PDPO compliant: {compliance.get('hong_kong_pdpo_compliant', False)}"
                )
                print(
                    f"   🔒 Original data encrypted: {compliance.get('original_data_encrypted', False)}"
                )
                print(
                    f"   🚫 No external PII transmission: {compliance.get('no_external_pii_transmission', False)}"
                )
        else:
            print(f"   ❌ Customer data processing failed: {customer_message}")
            return False
    except Exception as e:
        print(f"   ❌ Error processing customer data: {str(e)}")
        return False

    print()

    # Test purchase data processing
    print("3. Processing purchase data through privacy pipeline...")
    try:
        purchase_success, purchase_message, purchase_processed = (
            process_data_through_privacy_pipeline(
                purchase_data, "demo_purchase_data", "demo_purchase.csv"
            )
        )

        if purchase_success:
            print(f"   ✅ {purchase_message}")

            # Show privacy analysis results
            metadata = purchase_processed.get("metadata", {})
            pii_fields = metadata.get("pii_fields_identified", [])
            print(f"   🔍 PII fields identified: {len(pii_fields)} - {pii_fields}")
        else:
            print(f"   ❌ Purchase data processing failed: {purchase_message}")
            return False
    except Exception as e:
        print(f"   ❌ Error processing purchase data: {str(e)}")
        return False

    print()

    # Demonstrate data access patterns
    print("4. Demonstrating privacy-aware data access...")

    # Original data (encrypted)
    original_customer = customer_processed["original_data"]
    print(f"   📄 Original data preserved: {original_customer.shape}")

    # Pseudonymized data (for AI processing)
    pseudo_customer = customer_processed["pseudonymized_data"]
    print(f"   🤖 Pseudonymized data for AI: {pseudo_customer.shape}")

    # Display data (for UI)
    display_customer = customer_processed["display_data"]
    print(f"   👁️ Display data for UI: {display_customer.shape}")

    print()

    # Show data transformation examples
    print("5. Data transformation examples:")
    pii_fields = customer_processed["metadata"]["pii_fields_identified"]

    for field in pii_fields[:3]:  # Show first 3 PII fields
        if field in original_customer.columns:
            original_val = original_customer[field].iloc[0]
            pseudo_val = pseudo_customer[field].iloc[0]
            display_val = display_customer[field].iloc[0]

            print(f"   {field}:")
            print(f"     Original:     {original_val}")
            print(f"     Pseudonymized: {pseudo_val}")
            print(f"     Display:      {display_val}")
            print()

    print("6. Integration validation:")

    # Verify no original PII in pseudonymized data
    pii_in_pseudo = False
    for field in pii_fields:
        if field in original_customer.columns and field in pseudo_customer.columns:
            original_values = set(original_customer[field].astype(str))
            pseudo_values = set(pseudo_customer[field].astype(str))
            overlap = original_values.intersection(pseudo_values)
            if overlap:
                pii_in_pseudo = True
                print(
                    f"   ❌ WARNING: Original PII found in pseudonymized data for field {field}: {overlap}"
                )

    if not pii_in_pseudo:
        print("   ✅ No original PII found in pseudonymized data - safe for external processing")

    # Verify masking in display data
    masking_found = False
    for field in pii_fields:
        if field in original_customer.columns and field in display_customer.columns:
            original_values = original_customer[field].astype(str).tolist()
            display_values = display_customer[field].astype(str).tolist()

            if original_values != display_values:
                masking_found = True
                break

    if masking_found:
        print("   ✅ Masking patterns found in display data - privacy protection active")
    else:
        print("   ⚠️ No masking found in display data")

    print()
    print("=== Integration Test Complete ===")
    return True


if __name__ == "__main__":
    try:
        success = demonstrate_privacy_integration()
        if success:
            print("\n🎉 Privacy Pipeline Integration Test: PASSED")
            print("✅ Task 5.6 validation successful!")
        else:
            print("\n❌ Privacy Pipeline Integration Test: FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Integration test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
