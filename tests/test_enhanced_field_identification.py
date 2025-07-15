"""
Tests for Enhanced Field Identification Module

This test suite ensures that the enhanced field identification module correctly
identifies sensitive fields with improved accuracy and Hong Kong-specific support.
"""

import pytest
import pandas as pd
import json
import tempfile
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.enhanced_field_identification import (
    EnhancedFieldIdentifier,
    FieldType,
    FieldPattern,
    FieldIdentificationResult,
    create_field_identifier,
    analyze_dataframe_fields,
    get_sensitive_columns_enhanced,
)


class TestFieldType:
    """Test FieldType enum"""

    def test_field_type_values(self):
        """Test that all expected field types are available"""
        expected_types = [
            "account_id",
            "hkid",
            "email",
            "phone",
            "name",
            "address",
            "passport",
            "drivers_license",
            "credit_card",
            "bank_account",
            "ip_address",
            "date_of_birth",
            "general",
        ]

        for field_type in expected_types:
            assert hasattr(FieldType, field_type.upper())
            assert FieldType(field_type).value == field_type


class TestFieldPattern:
    """Test FieldPattern dataclass"""

    def test_field_pattern_creation(self):
        """Test creating a FieldPattern instance"""
        pattern = FieldPattern(
            field_type=FieldType.EMAIL,
            column_keywords=["email", "mail"],
            value_patterns=[r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"],
            confidence_weight=0.9,
            description="Email addresses",
        )

        assert pattern.field_type == FieldType.EMAIL
        assert pattern.column_keywords == ["email", "mail"]
        assert pattern.confidence_weight == 0.9
        assert pattern.description == "Email addresses"
        assert pattern.hong_kong_specific is False


class TestFieldIdentificationResult:
    """Test FieldIdentificationResult dataclass"""

    def test_result_creation(self):
        """Test creating a FieldIdentificationResult instance"""
        result = FieldIdentificationResult(
            field_type=FieldType.HKID,
            confidence=0.95,
            matched_pattern=r"^[A-Z]\d{6}\(\d\)$",
            method="value_pattern",
            is_sensitive=True,
        )

        assert result.field_type == FieldType.HKID
        assert result.confidence == 0.95
        assert result.matched_pattern == r"^[A-Z]\d{6}\(\d\)$"
        assert result.method == "value_pattern"
        assert result.is_sensitive


class TestEnhancedFieldIdentifier:
    """Test EnhancedFieldIdentifier class"""

    def test_initialization(self):
        """Test initializing EnhancedFieldIdentifier"""
        identifier = EnhancedFieldIdentifier()

        assert identifier.sensitivity_threshold == 0.6
        assert len(identifier.patterns) > 0
        assert isinstance(identifier.patterns[0], FieldPattern)

    def test_default_patterns_loaded(self):
        """Test that default patterns are loaded correctly"""
        identifier = EnhancedFieldIdentifier()

        # Check that all expected field types have patterns
        field_types = {pattern.field_type for pattern in identifier.patterns}
        expected_types = {
            FieldType.ACCOUNT_ID,
            FieldType.HKID,
            FieldType.EMAIL,
            FieldType.PHONE,
            FieldType.NAME,
            FieldType.ADDRESS,
            FieldType.PASSPORT,
            FieldType.DRIVERS_LICENSE,
            FieldType.CREDIT_CARD,
            FieldType.BANK_ACCOUNT,
            FieldType.IP_ADDRESS,
            FieldType.DATE_OF_BIRTH,
        }

        assert expected_types.issubset(field_types)

    def test_identify_field_hkid(self):
        """Test HKID identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with HKID values
        result = identifier.identify_field("hkid", ["A123456(7)", "B234567(8)"])

        assert result.field_type == FieldType.HKID
        assert result.confidence > 0.8
        assert result.is_sensitive

    def test_identify_field_email(self):
        """Test email identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with email values
        result = identifier.identify_field("email", ["john@example.com", "jane@test.org"])

        assert result.field_type == FieldType.EMAIL
        assert result.confidence > 0.8
        assert result.is_sensitive

    def test_identify_field_phone_hong_kong(self):
        """Test Hong Kong phone number identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with Hong Kong phone numbers
        result = identifier.identify_field("phone", ["+852 1234 5678", "23456789"])

        assert result.field_type == FieldType.PHONE
        assert result.confidence > 0.6
        assert result.is_sensitive

    def test_identify_field_name(self):
        """Test name identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with name values
        result = identifier.identify_field("customer_name", ["John Doe", "Jane Smith"])

        assert result.field_type == FieldType.NAME
        assert result.confidence > 0.5
        assert result.is_sensitive

    def test_identify_field_address_hong_kong(self):
        """Test Hong Kong address identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with Hong Kong addresses
        result = identifier.identify_field(
            "address", ["Flat 5A, 123 Nathan Road, Kowloon", "Suite 1001, Tower 2, Hong Kong"]
        )

        assert result.field_type == FieldType.ADDRESS
        assert result.confidence > 0.5
        assert result.is_sensitive

    def test_identify_field_passport(self):
        """Test passport identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with passport numbers
        result = identifier.identify_field("passport", ["A12345678", "B87654321"])

        assert result.field_type == FieldType.PASSPORT
        assert result.confidence > 0.7
        assert result.is_sensitive

    def test_identify_field_credit_card(self):
        """Test credit card identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with credit card numbers
        result = identifier.identify_field("credit_card", ["4111111111111111", "5555555555554444"])

        assert result.field_type == FieldType.CREDIT_CARD
        assert result.confidence > 0.8
        assert result.is_sensitive

    def test_identify_field_ip_address(self):
        """Test IP address identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with IP addresses
        result = identifier.identify_field("ip_address", ["192.168.1.1", "10.0.0.1"])

        assert result.field_type == FieldType.IP_ADDRESS
        assert result.confidence > 0.8
        assert result.is_sensitive

    def test_identify_field_date_of_birth(self):
        """Test date of birth identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with date of birth values
        result = identifier.identify_field("dob", ["1990-01-01", "1985-12-25"])

        assert result.field_type == FieldType.DATE_OF_BIRTH
        assert result.confidence > 0.6
        assert result.is_sensitive

    def test_identify_field_general(self):
        """Test general field identification"""
        identifier = EnhancedFieldIdentifier()

        # Test with non-sensitive values
        result = identifier.identify_field("plan_type", ["Premium", "Basic"])

        assert result.field_type == FieldType.GENERAL
        assert result.is_sensitive is False

    def test_analyze_dataframe(self):
        """Test analyzing a complete DataFrame"""
        identifier = EnhancedFieldIdentifier()

        # Create test DataFrame
        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002", "ACCT003"],
                "Customer_Name": ["John Doe", "Jane Smith", "Bob Johnson"],
                "Email": ["john@example.com", "jane@example.com", "bob@example.com"],
                "HKID": ["A123456(7)", "B234567(8)", "C345678(9)"],
                "Phone": ["+852 1234 5678", "+852 2345 6789", "+852 3456 7890"],
                "Plan_Type": ["Premium", "Basic", "Standard"],
                "Monthly_Fee": [500, 200, 300],
            }
        )

        results = identifier.analyze_dataframe(df)

        # Check that all columns are analyzed
        assert len(results) == len(df.columns)

        # Check sensitive fields
        sensitive_fields = ["Account_ID", "Customer_Name", "Email", "HKID", "Phone"]
        for field in sensitive_fields:
            assert results[field].is_sensitive

        # Check non-sensitive fields
        non_sensitive_fields = ["Plan_Type", "Monthly_Fee"]
        for field in non_sensitive_fields:
            assert results[field].is_sensitive is False

    def test_get_sensitive_columns(self):
        """Test getting sensitive columns from DataFrame"""
        identifier = EnhancedFieldIdentifier()

        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002"],
                "Customer_Name": ["John Doe", "Jane Smith"],
                "Email": ["john@example.com", "jane@example.com"],
                "Plan_Type": ["Premium", "Basic"],
                "Monthly_Fee": [500, 200],
            }
        )

        sensitive_columns = identifier.get_sensitive_columns(df)

        expected_sensitive = ["Account_ID", "Customer_Name", "Email"]
        assert set(sensitive_columns) == set(expected_sensitive)

    def test_get_field_summary(self):
        """Test getting field analysis summary"""
        identifier = EnhancedFieldIdentifier()

        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002"],
                "Customer_Name": ["John Doe", "Jane Smith"],
                "Email": ["john@example.com", "jane@example.com"],
                "Plan_Type": ["Premium", "Basic"],
            }
        )

        summary = identifier.get_field_summary(df)

        assert summary["total_columns"] == 4
        assert summary["sensitive_columns"] == 3
        assert "field_type_breakdown" in summary
        assert "analysis_details" in summary
        assert summary["sensitivity_threshold"] == 0.6

    def test_set_sensitivity_threshold(self):
        """Test setting sensitivity threshold"""
        identifier = EnhancedFieldIdentifier()

        # Test valid threshold
        identifier.set_sensitivity_threshold(0.8)
        assert identifier.sensitivity_threshold == 0.8

        # Test invalid threshold
        with pytest.raises(ValueError):
            identifier.set_sensitivity_threshold(1.5)

    def test_export_configuration(self):
        """Test exporting configuration"""
        identifier = EnhancedFieldIdentifier()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            identifier.export_configuration(temp_path)

            # Check that file was created and contains expected structure
            with open(temp_path, "r") as f:
                config = json.load(f)

            assert "sensitivity_threshold" in config
            assert "patterns" in config
            assert len(config["patterns"]) > 0

        finally:
            os.unlink(temp_path)

    def test_custom_patterns_loading(self):
        """Test loading custom patterns from configuration"""
        # Create temporary config file
        custom_config = {
            "custom_patterns": [
                {
                    "field_type": "account_id",
                    "column_keywords": ["custom_id", "special_account"],
                    "value_patterns": [r"^CUSTOM\d{6}$"],
                    "confidence_weight": 0.9,
                    "description": "Custom account pattern",
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(custom_config, f)
            temp_path = f.name

        try:
            identifier = EnhancedFieldIdentifier(config_path=temp_path)

            # Check that custom pattern was loaded
            custom_patterns = [p for p in identifier.patterns if "CUSTOM" in str(p.value_patterns)]
            assert len(custom_patterns) > 0

        finally:
            os.unlink(temp_path)


class TestUtilityFunctions:
    """Test utility functions"""

    def test_create_field_identifier(self):
        """Test field identifier creation utility"""
        identifier = create_field_identifier()
        assert isinstance(identifier, EnhancedFieldIdentifier)
        assert identifier.sensitivity_threshold == 0.6

    def test_analyze_dataframe_fields(self):
        """Test DataFrame field analysis utility"""
        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002"],
                "Email": ["john@example.com", "jane@example.com"],
                "Plan_Type": ["Premium", "Basic"],
            }
        )

        results = analyze_dataframe_fields(df)

        assert len(results) == 3
        assert results["Account_ID"].field_type == FieldType.ACCOUNT_ID
        assert results["Email"].field_type == FieldType.EMAIL
        assert results["Plan_Type"].field_type == FieldType.GENERAL

    def test_get_sensitive_columns_enhanced(self):
        """Test enhanced sensitive columns utility"""
        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002"],
                "Customer_Name": ["John Doe", "Jane Smith"],
                "Plan_Type": ["Premium", "Basic"],
            }
        )

        sensitive_columns = get_sensitive_columns_enhanced(df)

        expected_sensitive = ["Account_ID", "Customer_Name"]
        assert set(sensitive_columns) == set(expected_sensitive)


class TestHongKongSpecificPatterns:
    """Test Hong Kong-specific pattern recognition"""

    def test_hkid_patterns(self):
        """Test Hong Kong ID patterns"""
        identifier = EnhancedFieldIdentifier()

        # Test various HKID formats
        test_cases = [
            ("A123456(7)", True),
            ("B234567(8)", True),
            ("AB123456(9)", True),  # Two-letter format
            ("12345678", False),  # Invalid format
            ("A1234567", False),  # Missing check digit
        ]

        for hkid, should_match in test_cases:
            result = identifier.identify_field("hkid", [hkid])
            if should_match:
                assert result.field_type == FieldType.HKID
                assert result.confidence > 0.8
            else:
                assert result.field_type != FieldType.HKID or result.confidence < 0.8

    def test_hong_kong_phone_patterns(self):
        """Test Hong Kong phone number patterns"""
        identifier = EnhancedFieldIdentifier()

        # Test various Hong Kong phone formats
        test_cases = [
            ("+852 1234 5678", True),
            ("852 1234 5678", True),
            ("12345678", True),  # Local format
            ("+1 234 567 8901", True),  # International format
            ("123", False),  # Too short
        ]

        for phone, should_match in test_cases:
            result = identifier.identify_field("phone", [phone])
            if should_match:
                assert result.field_type == FieldType.PHONE
                assert result.confidence > 0.5

    def test_hong_kong_address_patterns(self):
        """Test Hong Kong address patterns"""
        identifier = EnhancedFieldIdentifier()

        # Test various Hong Kong address formats
        test_cases = [
            ("Flat 5A, 123 Nathan Road, Kowloon", True),
            ("Suite 1001, Tower 2, Hong Kong", True),
            ("123 Main St, New York", False),  # Non-HK address
        ]

        for address, should_match in test_cases:
            result = identifier.identify_field("address", [address])
            if should_match:
                assert result.field_type == FieldType.ADDRESS
                assert result.confidence > 0.5


class TestPerformanceAndAccuracy:
    """Test performance and accuracy of field identification"""

    def test_large_dataframe_performance(self):
        """Test performance with large DataFrame"""
        identifier = EnhancedFieldIdentifier()

        # Create large DataFrame
        large_df = pd.DataFrame(
            {
                "Account_ID": [f"ACCT{i:06d}" for i in range(1000)],
                "Email": [f"user{i}@example.com" for i in range(1000)],
                "Plan_Type": (["Premium", "Basic", "Standard"] * 334)[:1000],
            }
        )

        import time

        start_time = time.time()
        results = identifier.analyze_dataframe(large_df)
        end_time = time.time()

        # Should complete within reasonable time (< 5 seconds)
        assert end_time - start_time < 5.0
        assert len(results) == 3
        assert results["Account_ID"].is_sensitive
        assert results["Email"].is_sensitive
        assert results["Plan_Type"].is_sensitive is False

    def test_confidence_scoring_accuracy(self):
        """Test accuracy of confidence scoring"""
        identifier = EnhancedFieldIdentifier()

        # Test with high-confidence data
        high_confidence_result = identifier.identify_field(
            "email", ["john@example.com", "jane@test.org", "bob@company.net"]
        )

        # Test with low-confidence data
        low_confidence_result = identifier.identify_field("data", ["random", "text", "values"])

        assert high_confidence_result.confidence > 0.8
        assert low_confidence_result.confidence < 0.3

    def test_false_positive_reduction(self):
        """Test that false positives are minimized"""
        identifier = EnhancedFieldIdentifier()

        # Test with data that could be misidentified
        result = identifier.identify_field("monthly_fee", ["100", "200", "300"])

        # Should not be identified as sensitive
        assert result.is_sensitive is False
        assert result.field_type == FieldType.GENERAL


if __name__ == "__main__":
    pytest.main([__file__])
