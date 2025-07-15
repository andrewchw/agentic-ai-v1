"""
Test suite for Privacy Pipeline Integration with Upload Component (Task 5.6)

This test validates the integration between the upload component and the complete
privacy pipeline, ensuring all uploaded data is properly processed through:
- Encrypted storage
- Security pseudonymization
- Enhanced field identification
- Integrated display masking
"""

import pytest
import pandas as pd
import tempfile
import shutil

# Import components to test
from src.components.upload import process_data_through_privacy_pipeline


class TestPrivacyPipelineIntegration:
    """Test integration of privacy pipeline with upload component."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

        # Create test customer data with various PII types
        self.customer_data = pd.DataFrame(
            {
                "account_id": ["3HK123456", "3HK789012", "3HK345678"],
                "name": ["張三", "Wong Tai Man", "Lisa Chan"],
                "hkid": ["A123456(7)", "B789012(3)", "C345678(9)"],
                "phone": ["+852 9123 4567", "+852 9876 5432", "+852 9555 1234"],
                "email": [
                    "zhang.san@gmail.com",
                    "wong.taiman@yahoo.com.hk",
                    "lisa.chan@hotmail.com",
                ],
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

        # Create test purchase data
        self.purchase_data = pd.DataFrame(
            {
                "account_id": ["3HK123456", "3HK789012", "3HK345678"],
                "transaction_id": ["TXN001", "TXN002", "TXN003"],
                "purchase_amount": [100.50, 250.00, 75.25],
                "purchase_date": ["2024-01-15", "2024-01-16", "2024-01-17"],
                "category": ["Mobile Plan", "Device", "Accessories"],
            }
        )

        # Create non-PII data for testing
        self.non_pii_data = pd.DataFrame(
            {
                "product_category": ["Electronics", "Software", "Hardware"],
                "price_range": ["Low", "Medium", "High"],
                "availability": ["In Stock", "Limited", "Out of Stock"],
                "rating": [4.5, 3.8, 4.2],
            }
        )

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_customer_data_pipeline_integration(self):
        """Test customer data processing through complete privacy pipeline."""
        identifier = "test_customer_data"
        filename = "test_customer.csv"

        # Process through privacy pipeline
        success, message, processed_data = process_data_through_privacy_pipeline(
            self.customer_data, identifier, filename
        )

        # Verify successful processing
        assert success is True
        assert "Successfully processed" in message
        assert isinstance(processed_data, dict)

        # Verify all required data components are present
        assert "original_data" in processed_data
        assert "pseudonymized_data" in processed_data
        assert "display_data" in processed_data
        assert "storage_key" in processed_data
        assert "metadata" in processed_data
        assert "filename" in processed_data
        assert "processed_at" in processed_data

        # Verify data integrity
        original_df = processed_data["original_data"]
        pseudonymized_df = processed_data["pseudonymized_data"]
        display_df = processed_data["display_data"]

        assert original_df.shape == self.customer_data.shape
        assert pseudonymized_df.shape == self.customer_data.shape
        assert display_df.shape == self.customer_data.shape

        # Verify PII was identified
        metadata = processed_data["metadata"]
        pii_fields = metadata.get("pii_fields_identified", [])
        assert len(pii_fields) > 0

        # Expected PII fields for customer data
        expected_pii_fields = ["account_id", "name", "hkid", "phone", "email", "address"]
        identified_pii_fields = set(pii_fields)
        expected_pii_set = set(expected_pii_fields)

        # Should identify at least some of the expected PII fields
        assert len(identified_pii_fields.intersection(expected_pii_set)) >= 4

        # Verify filename is preserved
        assert processed_data["filename"] == filename

    def test_purchase_data_pipeline_integration(self):
        """Test purchase data processing through complete privacy pipeline."""
        identifier = "test_purchase_data"
        filename = "test_purchase.csv"

        # Process through privacy pipeline
        success, message, processed_data = process_data_through_privacy_pipeline(
            self.purchase_data, identifier, filename
        )

        # Verify successful processing
        assert success is True
        assert isinstance(processed_data, dict)

        # Verify structure
        assert all(
            key in processed_data
            for key in [
                "original_data",
                "pseudonymized_data",
                "display_data",
                "storage_key",
                "metadata",
                "filename",
            ]
        )

        # Verify data shapes preserved
        assert processed_data["original_data"].shape == self.purchase_data.shape
        assert processed_data["pseudonymized_data"].shape == self.purchase_data.shape
        assert processed_data["display_data"].shape == self.purchase_data.shape

    def test_non_pii_data_processing(self):
        """Test processing of data with minimal PII."""
        identifier = "test_non_pii_data"
        filename = "test_non_pii.csv"

        # Process through privacy pipeline
        success, message, processed_data = process_data_through_privacy_pipeline(
            self.non_pii_data, identifier, filename
        )

        # Should still succeed even with no PII
        assert success is True
        assert isinstance(processed_data, dict)

        # Verify minimal or no PII detected
        metadata = processed_data["metadata"]
        pii_fields = metadata.get("pii_fields_identified", [])
        assert len(pii_fields) <= 1  # Should detect very little or no PII

    def test_pseudonymized_data_has_no_original_pii(self):
        """Test that pseudonymized data contains no original PII values."""
        identifier = "test_pii_removal"
        filename = "test_pii_removal.csv"

        # Process data
        success, message, processed_data = process_data_through_privacy_pipeline(
            self.customer_data, identifier, filename
        )
        assert success is True

        # Get original and pseudonymized data
        original_df = processed_data["original_data"]
        pseudonymized_df = processed_data["pseudonymized_data"]
        metadata = processed_data["metadata"]
        pii_fields = metadata.get("pii_fields_identified", [])

        # Verify that PII fields in pseudonymized data don't contain original values
        for field in pii_fields:
            if field in original_df.columns and field in pseudonymized_df.columns:
                original_values = set(original_df[field].astype(str).tolist())
                pseudonymized_values = set(pseudonymized_df[field].astype(str).tolist())

                # Should have no overlap between original and pseudonymized values
                overlap = original_values.intersection(pseudonymized_values)
                assert (
                    len(overlap) == 0
                ), f"Field {field} still contains original PII values: {overlap}"

    def test_display_masking_functionality(self):
        """Test that display masking works correctly."""
        identifier = "test_display_masking"
        filename = "test_display_masking.csv"

        # Process data
        success, message, processed_data = process_data_through_privacy_pipeline(
            self.customer_data, identifier, filename
        )
        assert success is True

        # Get original and display data
        original_df = processed_data["original_data"]
        display_df = processed_data["display_data"]
        metadata = processed_data["metadata"]
        pii_fields = metadata.get("pii_fields_identified", [])

        # Verify that some fields are masked in display data
        masked_fields_found = False
        for field in pii_fields:
            if field in original_df.columns and field in display_df.columns:
                original_values = original_df[field].astype(str).tolist()
                display_values = display_df[field].astype(str).tolist()

                if original_values != display_values:
                    masked_fields_found = True

                    # Check for masking patterns
                    for display_val in display_values:
                        if "*" in display_val:  # Common masking character
                            assert len(display_val) > 0, "Masked value should not be empty"

        # Should find at least some masked fields
        assert masked_fields_found, "No masking patterns found in display data"

    def test_error_handling_empty_dataframe(self):
        """Test error handling with empty DataFrame."""
        empty_df = pd.DataFrame()
        identifier = "test_empty"
        filename = "empty.csv"

        # Should handle gracefully
        success, message, processed_data = process_data_through_privacy_pipeline(
            empty_df, identifier, filename
        )

        # May succeed or fail gracefully - both are acceptable
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert isinstance(processed_data, dict)

    def test_metadata_completeness(self):
        """Test that metadata contains all required information."""
        identifier = "test_metadata"
        filename = "test_metadata.csv"

        # Process data
        success, message, processed_data = process_data_through_privacy_pipeline(
            self.customer_data, identifier, filename
        )
        assert success is True

        metadata = processed_data["metadata"]

        # Verify required metadata fields
        required_fields = [
            "storage_key",
            "pii_fields_identified",
            "identification_results",
            "processing_stats",
            "compliance",
        ]

        for field in required_fields:
            assert field in metadata, f"Missing required metadata field: {field}"

        # Verify compliance information
        compliance = metadata["compliance"]
        assert compliance["gdpr_compliant"] is True
        assert compliance["hong_kong_pdpo_compliant"] is True
        assert compliance["original_data_encrypted"] is True
        assert compliance["no_external_pii_transmission"] is True

        # Verify processing stats
        stats = metadata["processing_stats"]
        assert "total_rows" in stats
        assert "total_columns" in stats
        assert "pii_fields_identified" in stats
        assert "processing_time_seconds" in stats

    def test_storage_key_uniqueness(self):
        """Test that different uploads get unique storage keys."""
        # Process same data twice with different identifiers
        success1, _, processed_data1 = process_data_through_privacy_pipeline(
            self.customer_data, "test_unique_1", "file1.csv"
        )
        success2, _, processed_data2 = process_data_through_privacy_pipeline(
            self.customer_data, "test_unique_2", "file2.csv"
        )

        assert success1 is True
        assert success2 is True

        # Storage keys should be different
        storage_key1 = processed_data1["storage_key"]
        storage_key2 = processed_data2["storage_key"]

        assert storage_key1 != storage_key2, "Storage keys should be unique"
        assert storage_key1 is not None
        assert storage_key2 is not None

    def test_hong_kong_specific_pii_detection(self):
        """Test that Hong Kong-specific PII patterns are correctly identified."""
        identifier = "test_hk_pii"
        filename = "test_hk_pii.csv"

        # Process customer data (contains HK-specific data)
        success, message, processed_data = process_data_through_privacy_pipeline(
            self.customer_data, identifier, filename
        )
        assert success is True

        metadata = processed_data["metadata"]
        identification_results = metadata.get("identification_results", {})

        # Check for Hong Kong-specific field detection
        hk_specific_fields = ["hkid", "phone", "address"]

        for field in hk_specific_fields:
            if field in identification_results:
                result = identification_results[field]
                assert (
                    result["is_sensitive"] is True
                ), f"HK-specific field {field} should be identified as sensitive"
                assert (
                    result["confidence"] > 0.5
                ), f"HK-specific field {field} should have good confidence score"

    def test_performance_within_reasonable_bounds(self):
        """Test that processing completes within reasonable time bounds."""
        import time

        identifier = "test_performance"
        filename = "test_performance.csv"

        start_time = time.time()
        success, message, processed_data = process_data_through_privacy_pipeline(
            self.customer_data, identifier, filename
        )
        end_time = time.time()

        processing_time = end_time - start_time

        assert success is True
        assert processing_time < 30.0, f"Processing took too long: {processing_time:.2f} seconds"

        # Check reported processing time in metadata
        metadata = processed_data["metadata"]
        stats = metadata["processing_stats"]
        reported_time = stats["processing_time_seconds"]

        assert reported_time > 0, "Processing time should be positive"
        assert reported_time < 30.0, "Reported processing time should be reasonable"


# Integration test to verify the full workflow
class TestEndToEndIntegration:
    """Test end-to-end integration scenarios."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_customer_and_purchase_workflow(self):
        """Test complete workflow with both customer and purchase data."""
        # Create test data
        customer_data = pd.DataFrame(
            {
                "account_id": ["ACC001", "ACC002"],
                "name": ["John Doe", "Jane Smith"],
                "email": ["john@test.com", "jane@test.com"],
                "phone": ["+852 1234 5678", "+852 8765 4321"],
            }
        )

        purchase_data = pd.DataFrame(
            {
                "account_id": ["ACC001", "ACC002"],
                "amount": [100.0, 200.0],
                "date": ["2024-01-01", "2024-01-02"],
            }
        )

        # Process customer data
        customer_success, customer_message, customer_processed = (
            process_data_through_privacy_pipeline(
                customer_data, "integration_customer", "customer.csv"
            )
        )

        # Process purchase data
        purchase_success, purchase_message, purchase_processed = (
            process_data_through_privacy_pipeline(
                purchase_data, "integration_purchase", "purchase.csv"
            )
        )

        # Both should succeed
        assert customer_success is True
        assert purchase_success is True

        # Verify we can access pseudonymized data for AI processing
        customer_pseudo = customer_processed["pseudonymized_data"]
        purchase_pseudo = purchase_processed["pseudonymized_data"]

        assert customer_pseudo is not None
        assert purchase_pseudo is not None
        assert "account_id" in customer_pseudo.columns
        assert "account_id" in purchase_pseudo.columns

        # Verify privacy compliance
        customer_compliance = customer_processed["metadata"]["compliance"]
        purchase_compliance = purchase_processed["metadata"]["compliance"]

        assert customer_compliance["no_external_pii_transmission"] is True
        assert purchase_compliance["no_external_pii_transmission"] is True


if __name__ == "__main__":
    pytest.main([__file__])
