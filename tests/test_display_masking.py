"""
Test suite for display masking functionality
Part of Task 5.1 - Display Masking Algorithms
"""

import unittest
import pandas as pd
from src.utils.display_masking import DisplayMasking, FieldType, mask_for_display


class TestDisplayMasking(unittest.TestCase):
    """Test cases for DisplayMasking class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.masker = DisplayMasking()
    
    def test_field_type_identification(self):
        """Test automatic field type identification"""
        # Test email identification
        self.assertEqual(
            self.masker.identify_field_type("john@example.com"),
            FieldType.EMAIL
        )
        
        # Test name identification
        self.assertEqual(
            self.masker.identify_field_type("John Doe"),
            FieldType.NAME
        )
        
        # Test HKID identification
        self.assertEqual(
            self.masker.identify_field_type("A123456(7)"),
            FieldType.HKID
        )
        
        # Test phone identification
        self.assertEqual(
            self.masker.identify_field_type("+852 2345 6789"),
            FieldType.PHONE
        )
        
        # Test column name context
        self.assertEqual(
            self.masker.identify_field_type("John Doe", "customer_name"),
            FieldType.NAME
        )
    
    def test_name_masking(self):
        """Test name masking functionality"""
        # Single name
        self.assertEqual(self.masker.mask_name("John"), "J***")
        
        # Full name
        self.assertEqual(self.masker.mask_name("John Doe"), "J*** D***")
        
        # Three names
        self.assertEqual(self.masker.mask_name("John Michael Doe"), "J*** M****** D***")
        
        # Single character names
        self.assertEqual(self.masker.mask_name("A B"), "A B")
        
        # Empty string
        self.assertEqual(self.masker.mask_name(""), "")
    
    def test_email_masking(self):
        """Test email masking functionality"""
        # Standard email
        self.assertEqual(
            self.masker.mask_email("john@example.com"),
            "j***@*******.com"
        )
        
        # Short local part
        self.assertEqual(
            self.masker.mask_email("a@test.com"),
            "a@****.com"
        )
        
        # Complex domain
        self.assertEqual(
            self.masker.mask_email("user@subdomain.example.com"),
            "u***@*********.example.com"
        )
        
        # Invalid email
        self.assertEqual(self.masker.mask_email("invalid-email"), "invalid-email")
    
    def test_hkid_masking(self):
        """Test HKID masking functionality"""
        # Standard HKID
        self.assertEqual(self.masker.mask_hkid("A123456(7)"), "A******(*)")
        
        # Two-letter prefix
        self.assertEqual(self.masker.mask_hkid("AB123456(7)"), "A******(*)")
        
        # Without parentheses
        self.assertEqual(self.masker.mask_hkid("A123456"), "A******")
        
        # Short string
        self.assertEqual(self.masker.mask_hkid("AB"), "A*")
    
    def test_phone_masking(self):
        """Test phone masking functionality"""
        # Hong Kong format with +852
        self.assertEqual(
            self.masker.mask_phone("+852 2345 6789"),
            "+852 ****6789"
        )
        
        # Without country code
        self.assertEqual(
            self.masker.mask_phone("2345 6789"),
            "****6789"
        )
        
        # Different format
        self.assertEqual(
            self.masker.mask_phone("23456789"),
            "****6789"
        )
        
        # Short phone
        self.assertEqual(self.masker.mask_phone("123"), "***")
    
    def test_account_id_masking(self):
        """Test account ID masking functionality"""
        # Standard account ID
        self.assertEqual(self.masker.mask_account_id("ACC123456"), "ACC***56")
        
        # Short account ID
        self.assertEqual(self.masker.mask_account_id("AC123"), "AC**3")
        
        # Very short
        self.assertEqual(self.masker.mask_account_id("ABC"), "AB*")
    
    def test_address_masking(self):
        """Test address masking functionality"""
        # With commas
        self.assertEqual(
            self.masker.mask_address("123 Main St, Tsim Sha Tsui, Kowloon"),
            "*** Kowloon"
        )
        
        # Without commas
        self.assertEqual(
            self.masker.mask_address("123 Main Street"),
            "*** Street"
        )
        
        # Single word
        self.assertEqual(self.masker.mask_address("Kowloon"), "*** Kowloon")
    
    def test_visibility_toggle(self):
        """Test visibility toggle functionality"""
        # Default is hidden
        self.assertFalse(self.masker.show_sensitive)
        
        result = self.masker.process_value("John Doe", FieldType.NAME)
        self.assertEqual(result, "J*** D***")
        
        # Show sensitive
        self.masker.set_visibility(True)
        result = self.masker.process_value("John Doe", FieldType.NAME)
        self.assertEqual(result, "John Doe")
        
        # Hide again
        self.masker.set_visibility(False)
        result = self.masker.process_value("John Doe", FieldType.NAME)
        self.assertEqual(result, "J*** D***")
    
    def test_dataframe_processing(self):
        """Test dataframe processing with masking"""
        # Create test dataframe
        df = pd.DataFrame({
            'Name': ['John Doe', 'Jane Smith'],
            'Email': ['john@example.com', 'jane@test.com'],
            'Phone': ['+852 2345 6789', '+852 9876 5432'],
            'Amount': [1000.00, 2000.00]
        })
        
        # Test with masking
        self.masker.set_visibility(False)
        result = self.masker.process_dataframe(df)
        
        self.assertTrue(result['masked'])
        self.assertIn('masked data', result['message'])
        
        # Check that sensitive data is masked
        masked_df = result['dataframe']
        self.assertEqual(masked_df.loc[0, 'Name'], 'J*** D***')
        self.assertEqual(masked_df.loc[0, 'Email'], 'j***@*******.com')
        self.assertEqual(masked_df.loc[0, 'Phone'], '+852 ****6789')
        
        # Non-sensitive data should remain unchanged
        self.assertEqual(masked_df.loc[0, 'Amount'], 1000.00)
        
        # Test without masking
        self.masker.set_visibility(True)
        result = self.masker.process_dataframe(df)
        
        self.assertFalse(result['masked'])
        self.assertIn('original data', result['message'])
        
        # Check that data is not masked
        unmasked_df = result['dataframe']
        self.assertEqual(unmasked_df.loc[0, 'Name'], 'John Doe')
        self.assertEqual(unmasked_df.loc[0, 'Email'], 'john@example.com')
    
    def test_convenience_function(self):
        """Test convenience function mask_for_display"""
        # Test with masking
        result = mask_for_display("John Doe", show_sensitive=False, field_type=FieldType.NAME)
        self.assertEqual(result, "J*** D***")
        
        # Test without masking
        result = mask_for_display("John Doe", show_sensitive=True, field_type=FieldType.NAME)
        self.assertEqual(result, "John Doe")
        
        # Test with auto-detection
        result = mask_for_display("john@example.com", show_sensitive=False)
        self.assertEqual(result, "j***@*******.com")


if __name__ == '__main__':
    unittest.main() 