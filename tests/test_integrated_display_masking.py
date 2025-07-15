"""
Comprehensive tests for Integrated Display Masking System - Task 5.4
Tests the integration of enhanced field identification with display masking
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import tempfile
import json
from pathlib import Path

from src.utils.integrated_display_masking import (
    IntegratedDisplayMasking,
    MaskingResult,
    integrated_display_masker,
    mask_for_display,
    process_dataframe_for_display
)
from src.utils.enhanced_field_identification import FieldType


class TestIntegratedDisplayMasking:
    """Test suite for IntegratedDisplayMasking class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.masker = IntegratedDisplayMasking(
            default_show_sensitive=False,
            confidence_threshold=0.5
        )
    
    def test_initialization(self):
        """Test proper initialization of the integrated masking system"""
        # Test default initialization
        masker = IntegratedDisplayMasking()
        assert masker.show_sensitive == False
        assert masker.confidence_threshold == 0.5
        assert masker.field_identifier is not None
        assert len(masker.masking_patterns) == 13
        
        # Test custom initialization
        masker = IntegratedDisplayMasking(
            default_show_sensitive=True,
            confidence_threshold=0.8
        )
        assert masker.show_sensitive == True
        assert masker.confidence_threshold == 0.8
    
    def test_visibility_control(self):
        """Test visibility toggle functionality"""
        # Initial state
        assert self.masker.show_sensitive == False
        
        # Set to show sensitive
        self.masker.set_visibility(True)
        assert self.masker.show_sensitive == True
        
        # Toggle
        result = self.masker.toggle_visibility()
        assert result == False
        assert self.masker.show_sensitive == False
    
    def test_confidence_threshold(self):
        """Test confidence threshold setting"""
        # Valid threshold
        self.masker.set_confidence_threshold(0.7)
        assert self.masker.confidence_threshold == 0.7
        
        # Invalid thresholds
        with pytest.raises(ValueError):
            self.masker.set_confidence_threshold(-0.1)
        
        with pytest.raises(ValueError):
            self.masker.set_confidence_threshold(1.1)


class TestMaskingFunctions:
    """Test individual masking functions for all field types"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.masker = IntegratedDisplayMasking()
    
    def test_mask_account_id(self):
        """Test account ID masking"""
        # Standard account ID
        result = self.masker.mask_account_id("ACC123456")
        assert result == "ACC****56"
        
        # Short account ID
        result = self.masker.mask_account_id("AC123")
        assert result == "AC***"
        
        # Very short
        result = self.masker.mask_account_id("A1")
        assert result == "A*"
    
    def test_mask_hkid(self):
        """Test Hong Kong ID masking"""
        # Standard HKID with parentheses
        result = self.masker.mask_hkid("A123456(7)")
        assert result == "A******(*)"
        
        # Two-letter prefix HKID
        result = self.masker.mask_hkid("AB123456(8)")
        assert result == "A******(*)"
        
        # HKID without parentheses
        result = self.masker.mask_hkid("A1234567")
        assert result == "A*******"
    
    def test_mask_email(self):
        """Test email masking"""
        # Standard email
        result = self.masker.mask_email("john.doe@example.com")
        assert result == "j*******@*******.com"
        
        # Short email
        result = self.masker.mask_email("a@b.co")
        assert result == "a@*.co"
        
        # Complex domain
        result = self.masker.mask_email("user@subdomain.domain.org")
        assert result == "u***@*********.domain.org"
    
    def test_mask_phone(self):
        """Test phone number masking"""
        # Hong Kong format with +852
        result = self.masker.mask_phone("+852 1234 5678")
        assert result == "+852 ****5678"
        
        # Local Hong Kong format
        result = self.masker.mask_phone("12345678")
        assert result == "****5678"
        
        # International format
        result = self.masker.mask_phone("+1 555 123 4567")
        assert result == "****4567"
        
        # Short number
        result = self.masker.mask_phone("123")
        assert result == "***"
    
    def test_mask_name(self):
        """Test name masking"""
        # Single name
        result = self.masker.mask_name("John")
        assert result == "J***"
        
        # Full name
        result = self.masker.mask_name("John Doe")
        assert result == "J*** D**"
        
        # Multiple names
        result = self.masker.mask_name("John Michael Doe")
        assert result == "J*** M****** D**"
        
        # Single character name
        result = self.masker.mask_name("A")
        assert result == "A"
    
    def test_mask_address(self):
        """Test address masking"""
        # Full address with commas
        result = self.masker.mask_address("Flat 5A, 123 Nathan Road, Kowloon")
        assert result == "*** Kowloon"
        
        # Address without commas
        result = self.masker.mask_address("123 Main Street Kowloon")
        assert result == "*** Kowloon"
        
        # Single word address
        result = self.masker.mask_address("Kowloon")
        assert result == "*** Kowloon"
    
    def test_mask_passport(self):
        """Test passport masking"""
        # Standard passport
        result = self.masker.mask_passport("HK1234567")
        assert result == "HK*****67"
        
        # Short passport
        result = self.masker.mask_passport("AB123")
        assert result == "AB***"
        
        # Very short
        result = self.masker.mask_passport("A1")
        assert result == "A*"
    
    def test_mask_drivers_license(self):
        """Test driver's license masking"""
        # Standard license
        result = self.masker.mask_drivers_license("DL123456789")
        assert result == "DL****789"
        
        # Short license
        result = self.masker.mask_drivers_license("DL123")
        assert result == "DL***"
    
    def test_mask_credit_card(self):
        """Test credit card masking"""
        # Standard format with dashes
        result = self.masker.mask_credit_card("1234-5678-9012-3456")
        assert result == "****-****-****-3456"
        
        # Format with spaces
        result = self.masker.mask_credit_card("1234 5678 9012 3456")
        assert result == "****-****-****-3456"  # May vary based on implementation
        
        # No formatting
        result = self.masker.mask_credit_card("1234567890123456")
        assert "3456" in result
        assert result.count('*') >= 12
    
    def test_mask_bank_account(self):
        """Test bank account masking"""
        # Standard format with dashes
        result = self.masker.mask_bank_account("123-456-789012")
        assert result == "***-***-789012"
        
        # No formatting
        result = self.masker.mask_bank_account("123456789012")
        assert result == "********9012"
    
    def test_mask_ip_address(self):
        """Test IP address masking"""
        # Standard IPv4
        result = self.masker.mask_ip_address("192.168.1.100")
        assert result == "192.168.***.***"
        
        # Different IP
        result = self.masker.mask_ip_address("10.0.0.1")
        assert result == "10.0.***.***"
    
    def test_mask_date_of_birth(self):
        """Test date of birth masking"""
        # ISO format
        result = self.masker.mask_date_of_birth("1990-05-15")
        assert result == "****-**-15"
        
        # Slash format
        result = self.masker.mask_date_of_birth("15/05/1990")
        assert result == "**/**/***"
        
        # Different format
        result = self.masker.mask_date_of_birth("05/15/1990")
        assert result == "**/**/***"
    
    def test_mask_general(self):
        """Test general/default masking"""
        # Standard text
        result = self.masker.mask_general("SomeData123")
        assert result == "So*****23"
        
        # Short text
        result = self.masker.mask_general("AB")
        assert result == "AB"
        
        # Medium text
        result = self.masker.mask_general("ABCD")
        assert result == "A***"


class TestValueProcessing:
    """Test individual value processing with field identification"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.masker = IntegratedDisplayMasking(confidence_threshold=0.5)
    
    def test_process_value_with_masking(self):
        """Test value processing when masking is enabled"""
        self.masker.set_visibility(False)  # Enable masking
        
        # Test email processing
        result = self.masker.process_value("john@example.com", "email")
        assert isinstance(result, MaskingResult)
        assert result.original_value == "john@example.com"
        assert result.masked_value != "john@example.com"
        assert result.field_type == FieldType.EMAIL
        assert result.is_masked == True
        assert result.confidence > 0.5
    
    def test_process_value_without_masking(self):
        """Test value processing when masking is disabled"""
        self.masker.set_visibility(True)  # Disable masking
        
        # Test email processing
        result = self.masker.process_value("john@example.com", "email")
        assert result.original_value == "john@example.com"
        assert result.masked_value == "john@example.com"
        assert result.is_masked == False
    
    def test_process_value_low_confidence(self):
        """Test value processing with low confidence"""
        self.masker.set_visibility(False)  # Enable masking
        self.masker.set_confidence_threshold(0.9)  # High threshold
        
        # Test with ambiguous data that might have low confidence
        result = self.masker.process_value("test123", "data")
        assert result.is_masked == False  # Should not mask due to low confidence
    
    def test_process_value_forced_field_type(self):
        """Test value processing with forced field type"""
        self.masker.set_visibility(False)  # Enable masking
        
        # Force treatment as email even if it doesn't look like one
        result = self.masker.process_value("notanemail", force_field_type=FieldType.EMAIL)
        assert result.field_type == FieldType.EMAIL
        assert result.confidence == 1.0
        assert result.is_masked == True
    
    def test_process_empty_values(self):
        """Test processing of empty or null values"""
        # Empty string
        result = self.masker.process_value("")
        assert result.original_value == ""
        assert result.masked_value == ""
        assert result.is_masked == False
        
        # None value
        result = self.masker.process_value(None)
        assert result.original_value == ""
        assert result.masked_value == ""
        assert result.is_masked == False


class TestDataFrameProcessing:
    """Test DataFrame processing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.masker = IntegratedDisplayMasking(confidence_threshold=0.5)
        
        # Create test DataFrame with multiple PII types
        self.test_df = pd.DataFrame({
            'account_id': ['ACC123456', 'ACC789012', 'ACC345678'],
            'customer_name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'email': ['john@example.com', 'jane@test.org', 'bob@company.net'],
            'phone': ['+852 1234 5678', '+852 9876 5432', '+852 5555 1234'],
            'hkid': ['A123456(7)', 'B789012(3)', 'C345678(9)'],
            'address': ['Flat 1A, 123 Nathan Road, Kowloon', 'Unit 5B, 456 Queen Street, Central', 'Suite 3C, 789 King Road, Wan Chai'],
            'amount': [1000.50, 2500.75, 750.25],  # Non-sensitive
            'date': ['2023-01-15', '2023-02-20', '2023-03-10']  # Non-sensitive
        })
    
    def test_dataframe_processing_with_masking(self):
        """Test DataFrame processing with masking enabled"""
        self.masker.set_visibility(False)  # Enable masking
        
        result = self.masker.process_dataframe(self.test_df)
        
        # Check result structure
        assert 'dataframe' in result
        assert 'original_dataframe' in result
        assert 'is_masked' in result
        assert 'masking_metadata' in result
        assert 'total_masked_fields' in result
        
        # Check that masking occurred
        assert result['is_masked'] == True
        assert result['total_masked_fields'] > 0
        
        # Check that sensitive data is masked
        masked_df = result['dataframe']
        assert masked_df['email'].iloc[0] != self.test_df['email'].iloc[0]
        assert masked_df['customer_name'].iloc[0] != self.test_df['customer_name'].iloc[0]
        
        # Check that non-sensitive data is unchanged
        assert masked_df['amount'].equals(self.test_df['amount'])
    
    def test_dataframe_processing_without_masking(self):
        """Test DataFrame processing with masking disabled"""
        self.masker.set_visibility(True)  # Disable masking
        
        result = self.masker.process_dataframe(self.test_df)
        
        # Check that no masking occurred
        assert result['is_masked'] == False
        assert result['total_masked_fields'] == 0
        
        # Check that data is unchanged
        pd.testing.assert_frame_equal(result['dataframe'], self.test_df)
    
    def test_dataframe_processing_specific_columns(self):
        """Test DataFrame processing with specific sensitive columns"""
        self.masker.set_visibility(False)  # Enable masking
        
        # Process only email and name columns
        result = self.masker.process_dataframe(
            self.test_df, 
            sensitive_columns=['email', 'customer_name']
        )
        
        masked_df = result['dataframe']
        
        # Check that specified columns are masked
        assert masked_df['email'].iloc[0] != self.test_df['email'].iloc[0]
        assert masked_df['customer_name'].iloc[0] != self.test_df['customer_name'].iloc[0]
        
        # Check that other columns are unchanged
        assert masked_df['phone'].equals(self.test_df['phone'])
        assert masked_df['account_id'].equals(self.test_df['account_id'])
    
    def test_dataframe_processing_with_forced_types(self):
        """Test DataFrame processing with forced field types"""
        self.masker.set_visibility(False)  # Enable masking
        
        # Force specific field types
        column_field_types = {
            'date': FieldType.DATE_OF_BIRTH,  # Force date to be treated as DOB
            'amount': FieldType.ACCOUNT_ID     # Force amount to be treated as account ID
        }
        
        result = self.masker.process_dataframe(
            self.test_df,
            column_field_types=column_field_types
        )
        
        masked_df = result['dataframe']
        
        # Check that forced types are processed
        assert masked_df['date'].iloc[0] != self.test_df['date'].iloc[0]
        assert masked_df['amount'].iloc[0] != self.test_df['amount'].iloc[0]
    
    def test_dataframe_processing_with_nan_values(self):
        """Test DataFrame processing with NaN values"""
        # Add NaN values to test DataFrame
        test_df_with_nan = self.test_df.copy()
        test_df_with_nan.loc[0, 'email'] = None
        test_df_with_nan.loc[1, 'phone'] = pd.NA
        
        self.masker.set_visibility(False)  # Enable masking
        
        result = self.masker.process_dataframe(test_df_with_nan)
        
        # Check that NaN values are handled properly
        masked_df = result['dataframe']
        assert pd.isna(masked_df.loc[0, 'email'])
        assert pd.isna(masked_df.loc[1, 'phone'])
    
    def test_dataframe_metadata(self):
        """Test masking metadata generation"""
        self.masker.set_visibility(False)  # Enable masking
        
        result = self.masker.process_dataframe(self.test_df)
        metadata = result['masking_metadata']
        
        # Check metadata structure
        for column in ['email', 'customer_name', 'hkid', 'phone']:
            if column in metadata:
                assert 'field_type' in metadata[column]
                assert 'confidence' in metadata[column]
                assert 'masked_count' in metadata[column]
                assert 'total_count' in metadata[column]
                assert 'masking_percentage' in metadata[column]
    
    def test_field_type_summary(self):
        """Test field type summary generation"""
        summary = self.masker.get_field_type_summary(self.test_df)
        
        # Check summary structure
        assert len(summary) == len(self.test_df.columns)
        
        for column, info in summary.items():
            assert 'field_type' in info
            assert 'confidence' in info
            assert 'sample_count' in info
            assert 'total_count' in info


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_mask_for_display_function(self):
        """Test convenience function for single value masking"""
        # Test with masking enabled
        result = mask_for_display("john@example.com", show_sensitive=False, column_name="email")
        assert result != "john@example.com"
        assert "@" in result  # Email structure preserved
        
        # Test with masking disabled
        result = mask_for_display("john@example.com", show_sensitive=True, column_name="email")
        assert result == "john@example.com"
    
    def test_process_dataframe_for_display_function(self):
        """Test convenience function for DataFrame processing"""
        test_df = pd.DataFrame({
            'email': ['john@example.com', 'jane@test.org'],
            'name': ['John Doe', 'Jane Smith'],
            'amount': [100, 200]
        })
        
        # Test with masking enabled
        result = process_dataframe_for_display(test_df, show_sensitive=False)
        assert result['is_masked'] == True
        assert result['total_masked_fields'] > 0
        
        # Test with masking disabled
        result = process_dataframe_for_display(test_df, show_sensitive=True)
        assert result['is_masked'] == False
        assert result['total_masked_fields'] == 0


class TestHongKongSpecificPatterns:
    """Test Hong Kong-specific pattern handling"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.masker = IntegratedDisplayMasking()
    
    def test_hk_phone_patterns(self):
        """Test Hong Kong phone number patterns"""
        hk_phones = [
            "+852 1234 5678",
            "+852-1234-5678", 
            "85212345678",
            "12345678"
        ]
        
        for phone in hk_phones:
            result = self.masker.process_value(phone, "phone")
            if result.is_masked:
                # Should preserve Hong Kong format where possible
                assert "5678" in result.masked_value or "****" in result.masked_value
    
    def test_hkid_patterns(self):
        """Test Hong Kong ID patterns"""
        hkids = [
            "A123456(7)",
            "AB123456(8)",
            "C987654(3)"
        ]
        
        for hkid in hkids:
            result = self.masker.process_value(hkid, "hkid")
            if result.is_masked:
                # Should preserve HKID structure
                assert result.masked_value.startswith(hkid[0])
                assert "(*)" in result.masked_value
    
    def test_hk_address_patterns(self):
        """Test Hong Kong address patterns"""
        hk_addresses = [
            "Flat 5A, 123 Nathan Road, Kowloon",
            "Unit 10B, 456 Queen's Road Central, Central",
            "Suite 15C, 789 Hennessy Road, Wan Chai"
        ]
        
        for address in hk_addresses:
            result = self.masker.process_value(address, "address")
            if result.is_masked:
                # Should preserve area information
                last_part = address.split(',')[-1].strip()
                assert last_part in result.masked_value


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.masker = IntegratedDisplayMasking()
    
    def test_invalid_dataframe_columns(self):
        """Test handling of invalid column specifications"""
        test_df = pd.DataFrame({'col1': [1, 2, 3]})
        
        # Should handle non-existent columns gracefully
        result = self.masker.process_dataframe(
            test_df, 
            sensitive_columns=['nonexistent_column']
        )
        
        # Should not crash and return valid result
        assert 'dataframe' in result
        pd.testing.assert_frame_equal(result['dataframe'], test_df)
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrames"""
        empty_df = pd.DataFrame()
        
        result = self.masker.process_dataframe(empty_df)
        
        assert 'dataframe' in result
        assert len(result['dataframe']) == 0
        assert result['total_masked_fields'] == 0
    
    def test_malformed_values(self):
        """Test handling of malformed values"""
        malformed_values = [
            "",           # Empty string
            "   ",        # Whitespace only
            "a",          # Single character
            "123",        # Numbers only
            "!@#$%",      # Special characters only
        ]
        
        for value in malformed_values:
            # Should not crash on any input
            result = self.masker.process_value(value, "test_column")
            assert isinstance(result, MaskingResult)
            assert result.original_value == value


class TestPerformance:
    """Test performance characteristics"""
    
    def test_large_dataframe_processing(self):
        """Test processing of large DataFrames"""
        import time
        
        # Create a larger test DataFrame
        large_df = pd.DataFrame({
            'email': [f'user{i}@example.com' for i in range(1000)],
            'name': [f'User {i}' for i in range(1000)],
            'phone': [f'+852 1234 {i:04d}' for i in range(1000)],
            'data': [f'data_{i}' for i in range(1000)]
        })
        
        masker = IntegratedDisplayMasking()
        
        start_time = time.time()
        result = masker.process_dataframe(large_df)
        processing_time = time.time() - start_time
        
        # Should complete in reasonable time (less than 10 seconds for 1000 rows)
        assert processing_time < 10.0
        assert result['total_masked_fields'] > 0
        
        # Verify data integrity
        assert len(result['dataframe']) == len(large_df)
        assert list(result['dataframe'].columns) == list(large_df.columns)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 