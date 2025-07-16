"""
Comprehensive Tests for Privacy Masking in Merged Data Outputs - Task 6.4
Tests that verify privacy masking toggle works correctly in all merged and aligned data outputs.

Test Coverage:
- Privacy toggle functionality (show_sensitive True/False)
- Sensitive field masking (email, names, HKID, phone numbers)
- Merged data structure privacy compliance
- Cross-dataset masking consistency
- Edge cases and error handling
"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.data_merging import DataMerger, MergeStrategy
from src.utils.privacy_pipeline import privacy_pipeline
from src.utils.enhanced_field_identification import FieldType


class TestPrivacyMaskingInMergedOutputs:
    """Comprehensive tests for privacy masking in merged data outputs"""

    def setup_method(self):
        """Set up comprehensive test data with various sensitive field types"""
        self.merger = DataMerger()
        
        # Create customer data with comprehensive PII coverage
        self.customer_df = pd.DataFrame({
            'Account ID': ['ACC001', 'ACC002', 'ACC003', 'ACC004', 'ACC005'],
            'Given Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'Family Name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson'],
            'Email': ['john.doe@example.com', 'jane.smith@gmail.com', 'bob.johnson@yahoo.com', 
                     'alice.brown@hotmail.com', 'charlie.wilson@outlook.com'],
            'Phone Number': ['+852 9876 5432', '+852 2345 6789', '+852 3456 7890', 
                           '+852 4567 8901', '+852 5678 9012'],
            'HKID': ['A123456(7)', 'B234567(8)', 'C345678(9)', 'D456789(0)', 'E567890(1)'],
            'Customer Type': ['Individual', 'Corporate', 'Individual', 'Individual', 'Corporate'],
            'Registration Date': ['2020-01-15', '2019-05-20', '2021-03-10', '2020-08-22', '2018-12-05']
        })
        
        # Create purchase data with some PII and transaction details
        self.purchase_df = pd.DataFrame({
            'Account ID': ['ACC001', 'ACC002', 'ACC003', 'ACC004', 'ACC006'],  # ACC006 not in customer data
            'Purchase Date': ['2024-01-15', '2024-01-20', '2024-01-25', '2024-01-30', '2024-02-01'],
            'Amount': [299.99, 599.99, 199.99, 399.99, 799.99],
            'Plan Type': ['5G Basic', '5G Premium', 'Data Add-on', '5G Pro', '5G Enterprise'],
            'Contact Email': ['john.doe@example.com', 'jane.smith@gmail.com', 'bob.johnson@yahoo.com',
                            'alice.brown@hotmail.com', 'unknown@example.com'],
            'Service Address': ['123 Main St, HK', '456 Queen Rd, HK', '789 Nathan Rd, HK',
                              '321 Des Voeux Rd, HK', '654 Canton Rd, HK']
        })
        
        # Process through privacy pipeline
        customer_result = privacy_pipeline.process_upload(self.customer_df, "test_customer_privacy", {})
        purchase_result = privacy_pipeline.process_upload(self.purchase_df, "test_purchase_privacy", {})
        
        # Create session state format
        self.customer_data_dict = {
            "original_data": self.customer_df,
            "pseudonymized_data": customer_result.pseudonymized_data,
            "display_data": customer_result.display_data,
            "storage_key": customer_result.storage_key,
            "metadata": customer_result.metadata,
        }
        
        self.purchase_data_dict = {
            "original_data": self.purchase_df,
            "pseudonymized_data": purchase_result.pseudonymized_data,
            "display_data": purchase_result.display_data,
            "storage_key": purchase_result.storage_key,
            "metadata": purchase_result.metadata,
        }

    def test_privacy_toggle_disabled_shows_sensitive_data(self):
        """Test that setting show_sensitive=True reveals actual sensitive data"""
        result = self.merger.merge_datasets(
            self.customer_data_dict,
            self.purchase_data_dict,
            strategy=MergeStrategy.INNER,
            show_sensitive=True
        )
        
        assert result.success == True
        assert result.metadata["show_sensitive"] == True
        
        # Verify original sensitive data is visible
        merged_data = result.merged_data
        assert merged_data is not None
        
        # Check that actual email addresses are present (not masked)
        if 'customer_Email' in merged_data.columns:
            email_values = merged_data['customer_Email'].tolist()
            assert any('@example.com' in str(email) for email in email_values)
            assert any('@gmail.com' in str(email) for email in email_values)
            # Should NOT contain masking patterns when show_sensitive=True
            assert not any('***' in str(email) for email in email_values)
        
        # Check that actual names are present (not masked)
        if 'customer_Given Name' in merged_data.columns:
            name_values = merged_data['customer_Given Name'].tolist()
            assert 'John' in name_values
            assert 'Jane' in name_values
            # Should NOT contain masking patterns when show_sensitive=True
            assert not any('***' in str(name) for name in name_values)

    def test_privacy_toggle_enabled_masks_sensitive_data(self):
        """Test that setting show_sensitive=False masks all sensitive data"""
        result = self.merger.merge_datasets(
            self.customer_data_dict,
            self.purchase_data_dict,
            strategy=MergeStrategy.INNER,
            show_sensitive=False
        )
        
        assert result.success == True
        assert result.metadata["show_sensitive"] == False
        
        # Verify sensitive data is masked in display_data
        display_data = result.display_data
        assert display_data is not None
        
        # Check email masking
        if 'customer_Email' in display_data.columns:
            email_values = display_data['customer_Email'].tolist()
            # Should contain masked email patterns
            masked_emails = [email for email in email_values if '***' in str(email)]
            assert len(masked_emails) > 0, f"Expected masked emails, got: {email_values}"
            
            # Should NOT contain original domain names when masked
            unmasked_emails = [email for email in email_values if '@example.com' in str(email) or '@gmail.com' in str(email)]
            assert len(unmasked_emails) == 0, f"Found unmasked emails: {unmasked_emails}"
        
        # Check name masking
        if 'customer_Given Name' in display_data.columns:
            name_values = display_data['customer_Given Name'].tolist()
            # Should contain masked name patterns
            masked_names = [name for name in name_values if '***' in str(name)]
            assert len(masked_names) > 0, f"Expected masked names, got: {name_values}"
            
            # Should NOT contain full original names when masked
            assert 'John' not in name_values
            assert 'Jane' not in name_values

    def test_hkid_masking_in_merged_data(self):
        """Test that HKID numbers are properly masked in merged outputs"""
        result = self.merger.merge_datasets(
            self.customer_data_dict,
            self.purchase_data_dict,
            strategy=MergeStrategy.INNER,
            show_sensitive=False
        )
        
        assert result.success == True
        display_data = result.display_data
        
        # Check HKID masking
        if 'customer_HKID' in display_data.columns:
            hkid_values = display_data['customer_HKID'].tolist()
            
            # Should contain masked HKID patterns
            for hkid in hkid_values:
                hkid_str = str(hkid)
                # HKID masking pattern should hide middle digits
                assert '***' in hkid_str or '*' in hkid_str, f"HKID not masked: {hkid_str}"
                
            # Should NOT contain full original HKIDs when masked
            original_hkids = ['A123456(7)', 'B234567(8)', 'C345678(9)', 'D456789(0)']
            for original_hkid in original_hkids:
                assert original_hkid not in hkid_values, f"Original HKID found in masked data: {original_hkid}"

    def test_phone_number_masking_in_merged_data(self):
        """Test that phone numbers are properly masked in merged outputs"""
        result = self.merger.merge_datasets(
            self.customer_data_dict,
            self.purchase_data_dict,
            strategy=MergeStrategy.INNER,
            show_sensitive=False
        )
        
        assert result.success == True
        display_data = result.display_data
        
        # Check phone number masking
        if 'customer_Phone Number' in display_data.columns:
            phone_values = display_data['customer_Phone Number'].tolist()
            
            # Should contain masked phone patterns
            for phone in phone_values:
                phone_str = str(phone)
                # Phone masking should hide some digits
                assert '***' in phone_str or '*' in phone_str, f"Phone not masked: {phone_str}"
                
            # Should NOT contain full original phone numbers when masked
            original_phones = ['+852 9876 5432', '+852 2345 6789', '+852 3456 7890']
            for original_phone in original_phones:
                assert original_phone not in phone_values, f"Original phone found in masked data: {original_phone}"

    def test_cross_dataset_masking_consistency(self):
        """Test that masking is consistent across customer and purchase datasets in merged output"""
        result = self.merger.merge_datasets(
            self.customer_data_dict,
            self.purchase_data_dict,
            strategy=MergeStrategy.INNER,
            show_sensitive=False
        )
        
        assert result.success == True
        display_data = result.display_data
        
        # Check that emails appear in both datasets and are consistently masked
        customer_emails = []
        purchase_emails = []
        
        if 'customer_Email' in display_data.columns:
            customer_emails = display_data['customer_Email'].tolist()
            
        if 'purchase_Contact Email' in display_data.columns:
            purchase_emails = display_data['purchase_Contact Email'].tolist()
        
        # Both email columns should be masked (contain ***)
        if customer_emails:
            assert all('***' in str(email) for email in customer_emails), f"Customer emails not all masked: {customer_emails}"
            
        if purchase_emails:
            assert all('***' in str(email) for email in purchase_emails), f"Purchase emails not all masked: {purchase_emails}"

    def test_merge_strategy_preserves_privacy_settings(self):
        """Test that different merge strategies preserve privacy settings"""
        strategies = [MergeStrategy.INNER, MergeStrategy.LEFT, MergeStrategy.RIGHT, MergeStrategy.OUTER]
        
        for strategy in strategies:
            # Test with masking enabled
            result_masked = self.merger.merge_datasets(
                self.customer_data_dict,
                self.purchase_data_dict,
                strategy=strategy,
                show_sensitive=False
            )
            
            # Test with masking disabled  
            result_unmasked = self.merger.merge_datasets(
                self.customer_data_dict,
                self.purchase_data_dict,
                strategy=strategy,
                show_sensitive=True
            )
            
            assert result_masked.success == True
            assert result_unmasked.success == True
            
            # Verify privacy settings are preserved in metadata
            assert result_masked.metadata["show_sensitive"] == False
            assert result_unmasked.metadata["show_sensitive"] == True
            
            # Verify masking behavior is consistent across strategies
            if result_masked.display_data is not None and 'customer_Email' in result_masked.display_data.columns:
                masked_emails = result_masked.display_data['customer_Email'].tolist()
                assert any('***' in str(email) for email in masked_emails), f"Strategy {strategy} - emails not masked"
                
            if result_unmasked.merged_data is not None and 'customer_Email' in result_unmasked.merged_data.columns:
                unmasked_emails = result_unmasked.merged_data['customer_Email'].tolist()
                assert any('@' in str(email) and '***' not in str(email) for email in unmasked_emails), f"Strategy {strategy} - emails incorrectly masked"

    def test_account_id_masking_behavior(self):
        """Test that Account ID masking preserves merging capability while protecting sensitive data"""
        result = self.merger.merge_datasets(
            self.customer_data_dict,
            self.purchase_data_dict,
            strategy=MergeStrategy.INNER,
            show_sensitive=False
        )
        
        assert result.success == True
        
        # Account ID should still allow merging to work
        # The merge is done on original data, but display shows masked Account IDs
        merged_data = result.merged_data
        display_data = result.display_data
        
        assert merged_data is not None
        assert display_data is not None
        
        # Should have successfully merged records (inner join of matching Account IDs)
        assert len(merged_data) > 0
        assert len(display_data) > 0
        
        # Account IDs in display data should be masked but merge should still work
        if 'Account ID' in display_data.columns:
            account_ids = display_data['Account ID'].tolist()
            # Account IDs may be masked (depending on field identification)
            # But merge operation should have been successful
            assert len(account_ids) > 0

    def test_merged_data_structure_integrity(self):
        """Test that privacy masking doesn't break the merged data structure"""
        result = self.merger.merge_datasets(
            self.customer_data_dict,
            self.purchase_data_dict,
            strategy=MergeStrategy.INNER,
            show_sensitive=False
        )
        
        assert result.success == True
        
        merged_data = result.merged_data
        display_data = result.display_data
        
        # Both versions should exist and have same structure
        assert merged_data is not None
        assert display_data is not None
        assert merged_data.shape == display_data.shape
        assert list(merged_data.columns) == list(display_data.columns)
        
        # Both should have Account ID column for reference
        assert 'Account ID' in merged_data.columns
        assert 'Account ID' in display_data.columns
        
        # Should have columns from both customer and purchase datasets
        customer_columns = [col for col in merged_data.columns if col.startswith('customer_')]
        purchase_columns = [col for col in merged_data.columns if col.startswith('purchase_')]
        
        assert len(customer_columns) > 0, f"No customer columns found: {list(merged_data.columns)}"
        assert len(purchase_columns) > 0, f"No purchase columns found: {list(merged_data.columns)}"

    def test_edge_case_empty_sensitive_fields(self):
        """Test privacy masking behavior with empty or null sensitive fields"""
        # Create data with some empty/null sensitive fields
        customer_df_with_nulls = self.customer_df.copy()
        customer_df_with_nulls.loc[0, 'Email'] = None
        customer_df_with_nulls.loc[1, 'Email'] = ''
        customer_df_with_nulls.loc[2, 'Phone Number'] = None
        
        # Process through privacy pipeline
        customer_result = privacy_pipeline.process_upload(customer_df_with_nulls, "test_customer_nulls", {})
        
        customer_data_dict_nulls = {
            "original_data": customer_df_with_nulls,
            "pseudonymized_data": customer_result.pseudonymized_data,
            "display_data": customer_result.display_data,
            "storage_key": customer_result.storage_key,
            "metadata": customer_result.metadata,
        }
        
        result = self.merger.merge_datasets(
            customer_data_dict_nulls,
            self.purchase_data_dict,
            strategy=MergeStrategy.INNER,
            show_sensitive=False
        )
        
        assert result.success == True
        
        # Should handle null/empty values gracefully without crashing
        display_data = result.display_data
        assert display_data is not None
        
        # Null values should remain null, not be masked
        if 'customer_Email' in display_data.columns:
            email_values = display_data['customer_Email'].tolist()
            # First row should be null/empty, others should be masked
            assert pd.isna(email_values[0]) or email_values[0] == '' or email_values[0] is None
            # Non-null values should be masked
            non_null_emails = [email for email in email_values[2:] if pd.notna(email) and email != '']
            if non_null_emails:
                assert any('***' in str(email) for email in non_null_emails)

    def test_privacy_masking_performance_with_large_dataset(self):
        """Test that privacy masking performance is acceptable with larger datasets"""
        import time
        
        # Create larger test dataset
        large_customer_df = pd.concat([self.customer_df] * 100, ignore_index=True)
        large_purchase_df = pd.concat([self.purchase_df] * 100, ignore_index=True)
        
        # Update Account IDs to maintain uniqueness
        large_customer_df['Account ID'] = [f'ACC{i:06d}' for i in range(len(large_customer_df))]
        large_purchase_df['Account ID'] = [f'ACC{i:06d}' for i in range(len(large_purchase_df))]
        
        # Process through privacy pipeline
        start_time = time.time()
        customer_result = privacy_pipeline.process_upload(large_customer_df, "test_customer_large", {})
        purchase_result = privacy_pipeline.process_upload(large_purchase_df, "test_purchase_large", {})
        
        customer_data_dict_large = {
            "original_data": large_customer_df,
            "pseudonymized_data": customer_result.pseudonymized_data,
            "display_data": customer_result.display_data,
            "storage_key": customer_result.storage_key,
            "metadata": customer_result.metadata,
        }
        
        purchase_data_dict_large = {
            "original_data": large_purchase_df,
            "pseudonymized_data": purchase_result.pseudonymized_data,
            "display_data": purchase_result.display_data,
            "storage_key": purchase_result.storage_key,
            "metadata": purchase_result.metadata,
        }
        
        # Perform merge with privacy masking
        result = self.merger.merge_datasets(
            customer_data_dict_large,
            purchase_data_dict_large,
            strategy=MergeStrategy.INNER,
            show_sensitive=False
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert result.success == True
        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 30.0, f"Privacy masking took too long: {processing_time}s"
        
        # Verify masking still works correctly with large dataset
        display_data = result.display_data
        if display_data is not None and 'customer_Email' in display_data.columns:
            email_values = display_data['customer_Email'].tolist()
            masked_count = sum(1 for email in email_values if '***' in str(email))
            assert masked_count > 0, "No emails were masked in large dataset"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 