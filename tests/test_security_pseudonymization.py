"""
Tests for Security Pseudonymization Module

This test suite ensures that the security pseudonymization module correctly
implements SHA-256 hashing with salt for irreversible anonymization of sensitive
customer data before external LLM processing.
"""

import pytest
import pandas as pd
from unittest.mock import patch
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.security_pseudonymization import (
    SecurityPseudonymizer,
    create_pseudonymizer,
    anonymize_for_llm,
    get_salt_from_config,
)


class TestSecurityPseudonymizer:
    """Test suite for SecurityPseudonymizer class"""

    def test_init_with_salt(self):
        """Test initialization with provided salt"""
        test_salt = "test_salt_123"
        pseudonymizer = SecurityPseudonymizer(salt=test_salt)
        assert pseudonymizer.salt == test_salt

    def test_init_without_salt(self):
        """Test initialization without salt generates secure salt"""
        pseudonymizer = SecurityPseudonymizer()
        assert pseudonymizer.salt is not None
        assert len(pseudonymizer.salt) == 64  # 32 bytes as hex = 64 characters

    def test_hash_value_consistency(self):
        """Test that hashing is consistent for the same input"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")
        value = "test_value"

        hash1 = pseudonymizer._hash_value(value)
        hash2 = pseudonymizer._hash_value(value)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_hash_value_different_salts(self):
        """Test that different salts produce different hashes"""
        value = "test_value"

        pseudonymizer1 = SecurityPseudonymizer(salt="salt1")
        pseudonymizer2 = SecurityPseudonymizer(salt="salt2")

        hash1 = pseudonymizer1._hash_value(value)
        hash2 = pseudonymizer2._hash_value(value)

        assert hash1 != hash2

    def test_anonymize_field_basic(self):
        """Test basic field anonymization"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        original_value = "John Doe"
        anonymized = pseudonymizer.anonymize_field(original_value, "name")

        assert anonymized.startswith("NAME_")
        assert anonymized != original_value
        assert len(anonymized) == 21  # "NAME_" + 16 chars

    def test_anonymize_field_types(self):
        """Test anonymization with different field types"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        test_cases = [
            ("ACCT12345", "account_id", "ACCT_"),
            ("A123456(7)", "hkid", "HKID_"),
            ("test@example.com", "email", "EMAIL_"),
            ("+852 1234 5678", "phone", "PHONE_"),
            ("John Doe", "name", "NAME_"),
            ("123 Main St", "address", "ADDR_"),
            ("other_data", "general", "DATA_"),
        ]

        for value, field_type, expected_prefix in test_cases:
            anonymized = pseudonymizer.anonymize_field(value, field_type)
            assert anonymized.startswith(expected_prefix)
            assert anonymized != value

    def test_anonymize_field_null_values(self):
        """Test anonymization of null/empty values"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        test_cases = [None, "", pd.NA, float("nan")]

        for value in test_cases:
            anonymized = pseudonymizer.anonymize_field(value)
            assert anonymized == ""

    def test_identify_field_type_column_names(self):
        """Test field type identification by column name"""
        pseudonymizer = SecurityPseudonymizer()

        test_cases = [
            ("Account_ID", "test_value", "account_id"),
            ("customer_email", "test_value", "email"),
            ("Phone_Number", "test_value", "phone"),
            ("Customer_Name", "test_value", "name"),
            ("Home_Address", "test_value", "address"),
            ("HKID_Number", "test_value", "hkid"),
            ("Random_Column", "test_value", "general"),
        ]

        for column_name, sample_value, expected_type in test_cases:
            field_type = pseudonymizer.identify_field_type(column_name, sample_value)
            assert field_type == expected_type

    def test_identify_field_type_value_patterns(self):
        """Test field type identification by value patterns"""
        pseudonymizer = SecurityPseudonymizer()

        test_cases = [
            ("unknown_col", "A123456(7)", "hkid"),
            ("unknown_col", "test@example.com", "email"),
            ("unknown_col", "+852 1234 5678", "phone"),
            ("unknown_col", "ACCT12345", "account_id"),
            ("unknown_col", "random_text", "general"),
        ]

        for column_name, sample_value, expected_type in test_cases:
            field_type = pseudonymizer.identify_field_type(column_name, sample_value)
            assert field_type == expected_type

    def test_anonymize_dataframe_basic(self):
        """Test basic DataFrame anonymization"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        # Create test DataFrame
        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002", "ACCT003"],
                "Customer_Name": ["John Doe", "Jane Smith", "Bob Johnson"],
                "Email": ["john@example.com", "jane@example.com", "bob@example.com"],
                "Plan_Type": ["Premium", "Basic", "Standard"],  # Non-sensitive
            }
        )

        anonymized_df = pseudonymizer.anonymize_dataframe(df)

        # Check structure is preserved
        assert anonymized_df.shape == df.shape
        assert list(anonymized_df.columns) == list(df.columns)

        # Check sensitive columns are anonymized
        assert all(anonymized_df["Account_ID"].str.startswith("ACCT_"))
        assert all(anonymized_df["Customer_Name"].str.startswith("NAME_"))
        assert all(anonymized_df["Email"].str.startswith("EMAIL_"))

        # Check non-sensitive column is unchanged
        assert anonymized_df["Plan_Type"].equals(df["Plan_Type"])

    def test_anonymize_dataframe_specific_columns(self):
        """Test DataFrame anonymization with specific columns"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002"],
                "Customer_Name": ["John Doe", "Jane Smith"],
                "Plan_Type": ["Premium", "Basic"],
            }
        )

        # Only anonymize Account_ID
        anonymized_df = pseudonymizer.anonymize_dataframe(df, ["Account_ID"])

        assert all(anonymized_df["Account_ID"].str.startswith("ACCT_"))
        assert anonymized_df["Customer_Name"].equals(df["Customer_Name"])  # Unchanged
        assert anonymized_df["Plan_Type"].equals(df["Plan_Type"])  # Unchanged

    def test_anonymize_dataframe_empty(self):
        """Test anonymization of empty DataFrame"""
        pseudonymizer = SecurityPseudonymizer()

        df = pd.DataFrame()
        anonymized_df = pseudonymizer.anonymize_dataframe(df)

        assert anonymized_df.empty
        assert anonymized_df.shape == df.shape

    def test_detect_sensitive_columns(self):
        """Test automatic detection of sensitive columns"""
        pseudonymizer = SecurityPseudonymizer()

        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002"],
                "Customer_Name": ["John Doe", "Jane Smith"],
                "Email": ["john@example.com", "jane@example.com"],
                "Plan_Type": ["Premium", "Basic"],
                "Monthly_Fee": [100, 50],
            }
        )

        sensitive_columns = pseudonymizer._detect_sensitive_columns(df)

        expected_sensitive = ["Account_ID", "Customer_Name", "Email"]
        assert set(sensitive_columns) == set(expected_sensitive)

    def test_get_anonymization_summary(self):
        """Test anonymization summary generation"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002"],
                "Customer_Name": ["John Doe", "Jane Smith"],
                "Plan_Type": ["Premium", "Basic"],
            }
        )

        summary = pseudonymizer.get_anonymization_summary(df)

        assert summary["total_columns"] == 3
        assert summary["sensitive_columns"] == 2
        assert "Account_ID" in summary["sensitive_column_names"]
        assert "Customer_Name" in summary["sensitive_column_names"]
        assert summary["total_rows"] == 2
        assert summary["anonymization_method"] == "SHA-256 with salt"
        assert summary["reversible"] is False
        assert "GDPR" in summary["compliance"]
        assert "Hong Kong PDPO" in summary["compliance"]

    def test_validate_anonymization(self):
        """Test anonymization validation"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        original_df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002"],
                "Customer_Name": ["John Doe", "Jane Smith"],
                "Plan_Type": ["Premium", "Basic"],
            }
        )

        anonymized_df = pseudonymizer.anonymize_dataframe(original_df)
        validation = pseudonymizer.validate_anonymization(original_df, anonymized_df)

        assert validation["structure_preserved"]
        assert validation["columns_preserved"]
        assert validation["no_original_pii"]
        assert validation["consistent_hashing"]

    def test_irreversibility(self):
        """Test that anonymization is truly irreversible"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        original_values = ["John Doe", "Jane Smith", "Bob Johnson"]
        anonymized_values = [pseudonymizer.anonymize_field(val, "name") for val in original_values]

        # Should not be able to reverse the values
        for original, anonymized in zip(original_values, anonymized_values):
            assert original != anonymized
            assert original not in anonymized
            # Hash should be consistent
            assert pseudonymizer.anonymize_field(original, "name") == anonymized


class TestUtilityFunctions:
    """Test utility functions"""

    def test_create_pseudonymizer(self):
        """Test pseudonymizer creation utility"""
        pseudonymizer = create_pseudonymizer()
        assert isinstance(pseudonymizer, SecurityPseudonymizer)
        assert pseudonymizer.salt is not None

    def test_create_pseudonymizer_with_salt(self):
        """Test pseudonymizer creation with salt"""
        test_salt = "test_salt_123"
        pseudonymizer = create_pseudonymizer(salt=test_salt)
        assert isinstance(pseudonymizer, SecurityPseudonymizer)
        assert pseudonymizer.salt == test_salt

    def test_anonymize_for_llm(self):
        """Test convenience function for LLM anonymization"""
        df = pd.DataFrame(
            {
                "Account_ID": ["ACCT001", "ACCT002"],
                "Customer_Name": ["John Doe", "Jane Smith"],
                "Plan_Type": ["Premium", "Basic"],
            }
        )

        anonymized_df = anonymize_for_llm(df, salt="test_salt")

        assert anonymized_df.shape == df.shape
        assert all(anonymized_df["Account_ID"].str.startswith("ACCT_"))
        assert all(anonymized_df["Customer_Name"].str.startswith("NAME_"))
        assert anonymized_df["Plan_Type"].equals(df["Plan_Type"])

    @patch.dict(os.environ, {"PSEUDONYMIZATION_SALT": "env_salt_123"})
    def test_get_salt_from_config_env(self):
        """Test getting salt from environment"""
        salt = get_salt_from_config()
        assert salt == "env_salt_123"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_salt_from_config_generate(self):
        """Test salt generation when not in environment"""
        salt = get_salt_from_config()
        assert salt is not None
        assert len(salt) == 64  # 32 bytes as hex


class TestSecurityProperties:
    """Test security properties of the pseudonymization"""

    def test_salt_entropy(self):
        """Test that generated salts have sufficient entropy"""
        pseudonymizer1 = SecurityPseudonymizer()
        pseudonymizer2 = SecurityPseudonymizer()

        # Different instances should have different salts
        assert pseudonymizer1.salt != pseudonymizer2.salt

        # Salts should be proper length
        assert len(pseudonymizer1.salt) == 64
        assert len(pseudonymizer2.salt) == 64

    def test_hash_collision_resistance(self):
        """Test that different inputs produce different hashes"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        values = ["John Doe", "Jane Doe", "John Smith", "Jane Smith"]
        hashes = [pseudonymizer._hash_value(val) for val in values]

        # All hashes should be different
        assert len(set(hashes)) == len(hashes)

    def test_anonymization_consistency_across_dataframes(self):
        """Test that same value gets same hash across different DataFrames"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        df1 = pd.DataFrame({"Account_ID": ["ACCT001", "ACCT002"]})
        df2 = pd.DataFrame({"Account_ID": ["ACCT001", "ACCT003"]})

        anonymized_df1 = pseudonymizer.anonymize_dataframe(df1)
        anonymized_df2 = pseudonymizer.anonymize_dataframe(df2)

        # Same account ID should have same anonymized value
        assert anonymized_df1.loc[0, "Account_ID"] == anonymized_df2.loc[0, "Account_ID"]

    def test_no_pii_leakage(self):
        """Test that no original PII appears in anonymized output"""
        pseudonymizer = SecurityPseudonymizer(salt="test_salt")

        sensitive_data = [
            "John Doe",
            "jane@example.com",
            "A123456(7)",
            "+852 1234 5678",
            "ACCT12345",
        ]

        for data in sensitive_data:
            anonymized = pseudonymizer.anonymize_field(data)

            # Original value should not appear in anonymized output
            assert data not in anonymized
            assert data.lower() not in anonymized.lower()

            # Should not contain recognizable patterns
            assert "@" not in anonymized if "@" in data else True
            assert "(" not in anonymized if "(" in data else True


if __name__ == "__main__":
    pytest.main([__file__])
