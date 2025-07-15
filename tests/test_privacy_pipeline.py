"""
Tests for Privacy Data Processing Pipeline

This test suite validates the integrated privacy pipeline that coordinates
all privacy components for secure, end-to-end data processing.
"""

import os
import tempfile
import shutil
import pytest
import pandas as pd
from datetime import datetime
import sys

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.privacy_pipeline import (
    PrivacyPipeline, PipelineResult, PipelineStats,
    process_customer_data, get_display_data, get_llm_safe_data
)


class TestPrivacyPipeline:
    """Test suite for PrivacyPipeline integration."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.pipeline = PrivacyPipeline(
            storage_path=self.temp_dir,
            master_password="test_pipeline_password"
        )
        
        # Sample customer data with various PII types
        self.customer_data = pd.DataFrame({
            'account_id': ['ACC123456', 'ACC789012', 'ACC345678'],
            'name': ['John Doe', 'Jane Smith', '李小明'],
            'email': ['john@example.com', 'jane@test.com', 'xiaoming@test.hk'],
            'hkid': ['A123456(7)', 'B789012(3)', 'C345678(9)'],
            'phone': ['+852 1234 5678', '+852 9876 5432', '+852 5555 1234'],
            'address': ['Flat 5A, Nathan Rd, TST', 'Unit 10B, Queen Rd, Central', '15樓A室, 旺角道, 旺角'],
            'balance': [1000.50, 2500.75, 750.25],
            'credit_score': [750, 820, 690],
            'last_login': ['2024-01-15', '2024-01-14', '2024-01-13']
        })
        
        self.non_pii_data = pd.DataFrame({
            'product_id': ['PROD001', 'PROD002', 'PROD003'],
            'category': ['mobile', 'internet', 'tv'],
            'price': [100.0, 200.0, 150.0],
            'availability': [True, False, True]
        })
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization with all components."""
        assert self.pipeline.storage_path == self.temp_dir
        assert self.pipeline.encrypted_storage is not None
        assert self.pipeline.field_identifier is not None
        assert self.pipeline.security_pseudonymizer is not None
        assert self.pipeline.display_masker is not None
        assert isinstance(self.pipeline.current_session, dict)
        assert isinstance(self.pipeline.processing_stats, list)
    
    def test_complete_data_processing_workflow(self):
        """Test complete end-to-end data processing workflow."""
        identifier = "customer_test_data"
        metadata = {"source": "test_system", "classification": "confidential"}
        
        # Process upload through complete pipeline
        result = self.pipeline.process_upload(self.customer_data, identifier, metadata)
        
        # Verify successful processing
        assert result.success is True
        assert result.storage_key is not None
        assert result.pseudonymized_data is not None
        assert result.display_data is not None
        assert result.metadata is not None
        
        # Verify data shapes are preserved
        original_shape = self.customer_data.shape
        assert result.pseudonymized_data.shape == original_shape
        assert result.display_data.shape == original_shape
        
        # Verify PII fields were identified
        assert result.metadata['pii_fields_identified'] > 0
        pii_fields = result.metadata['pii_fields_identified']
        expected_pii_fields = ['account_id', 'name', 'email', 'hkid', 'phone', 'address']
        assert len(pii_fields) >= 4  # At least some PII fields identified
        
        # Verify session was created
        assert identifier in self.pipeline.current_session
        session_info = self.pipeline.current_session[identifier]
        assert session_info['storage_key'] == result.storage_key
        assert 'pii_fields' in session_info
        assert 'stats' in session_info
    
    def test_pseudonymized_data_security(self):
        """Test that pseudonymized data contains no original PII."""
        identifier = "security_test_data"
        
        # Process data
        result = self.pipeline.process_upload(self.customer_data, identifier)
        assert result.success is True
        
        # Get pseudonymized data for LLM
        llm_result = self.pipeline.get_pseudonymized_for_llm(result.storage_key)
        assert llm_result.success is True
        
        pseudonymized_df = llm_result.pseudonymized_data
        
        # Verify no original PII values exist in pseudonymized data
        original_values = set()
        for column in self.customer_data.columns:
            original_values.update(self.customer_data[column].astype(str).tolist())
        
        pseudonymized_values = set()
        for column in pseudonymized_df.columns:
            pseudonymized_values.update(pseudonymized_df[column].astype(str).tolist())
        
        # Check for overlapping sensitive values
        sensitive_columns = ['name', 'email', 'hkid', 'phone', 'address']
        overlap_found = False
        
        for column in sensitive_columns:
            if column in self.customer_data.columns and column in pseudonymized_df.columns:
                original_col_values = set(self.customer_data[column].astype(str))
                pseudo_col_values = set(pseudonymized_df[column].astype(str))
                overlap = original_col_values.intersection(pseudo_col_values)
                if overlap:
                    overlap_found = True
                    break
        
        assert not overlap_found, "Original PII values found in pseudonymized data"
        
        # Verify pseudonymization patterns
        for column in sensitive_columns:
            if column in pseudonymized_df.columns:
                values = pseudonymized_df[column].astype(str)
                # Check for pseudonymization pattern (TYPE_hash)
                pattern_matches = values.str.contains(r'^[A-Z_]+_[a-f0-9]{16}$').sum()
                total_values = len(values.dropna())
                if total_values > 0:
                    assert pattern_matches > 0, f"No pseudonymized patterns found in {column}"
    
    def test_display_masking_toggle(self):
        """Test display masking toggle functionality."""
        identifier = "display_test_data"
        
        # Process data
        result = self.pipeline.process_upload(self.customer_data, identifier)
        assert result.success is True
        storage_key = result.storage_key
        
        # Test with privacy enabled (default)
        display_result_masked = self.pipeline.retrieve_for_display(storage_key, privacy_enabled=True)
        assert display_result_masked.success is True
        masked_df = display_result_masked.display_data
        
        # Test with privacy disabled
        display_result_unmasked = self.pipeline.retrieve_for_display(storage_key, privacy_enabled=False)
        assert display_result_unmasked.success is True
        unmasked_df = display_result_unmasked.display_data
        
        # Verify shapes are the same
        assert masked_df.shape == unmasked_df.shape == self.customer_data.shape
        
        # Verify that masked and unmasked versions are different for PII fields
        pii_columns = ['name', 'email', 'hkid', 'phone']
        differences_found = False
        
        for column in pii_columns:
            if column in masked_df.columns and column in unmasked_df.columns:
                masked_values = masked_df[column].astype(str).tolist()
                unmasked_values = unmasked_df[column].astype(str).tolist()
                if masked_values != unmasked_values:
                    differences_found = True
                    break
        
        assert differences_found, "No differences found between masked and unmasked data"
        
        # Verify unmasked data matches original
        pd.testing.assert_frame_equal(unmasked_df, self.customer_data, check_dtype=False)
    
    def test_non_pii_data_processing(self):
        """Test processing of non-PII data."""
        identifier = "non_pii_test"
        
        # Process non-PII data
        result = self.pipeline.process_upload(self.non_pii_data, identifier)
        assert result.success is True
        
        # Verify minimal PII fields identified
        pii_fields = result.metadata['pii_fields_identified']
        assert len(pii_fields) == 0 or len(pii_fields) < 2  # Should be minimal or none
        
        # Verify data preservation
        pd.testing.assert_frame_equal(
            result.pseudonymized_data, 
            self.non_pii_data, 
            check_dtype=False
        )
    
    def test_error_handling(self):
        """Test error handling in pipeline."""
        # Test with invalid storage key
        invalid_result = self.pipeline.retrieve_for_display("invalid_key")
        assert invalid_result.success is False
        assert invalid_result.errors is not None
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        result = self.pipeline.process_upload(empty_df, "empty_test")
        # Should handle gracefully (may succeed with empty data)
        assert isinstance(result, PipelineResult)
    
    def test_pipeline_statistics(self):
        """Test pipeline statistics tracking."""
        identifier = "stats_test_data"
        
        # Process data
        result = self.pipeline.process_upload(self.customer_data, identifier)
        assert result.success is True
        
        # Verify statistics in result
        stats = result.metadata['processing_stats']
        assert stats['total_rows'] == self.customer_data.shape[0]
        assert stats['total_columns'] == self.customer_data.shape[1]
        assert stats['pii_fields_identified'] > 0
        assert stats['processing_time_seconds'] > 0
        assert stats['encryption_time_seconds'] > 0
        
        # Verify pipeline status
        status = self.pipeline.get_pipeline_status()
        assert status['total_processed_datasets'] == 1
        assert status['current_sessions'] == 1
        assert status['compliance']['gdpr_compliant'] is True
        assert status['compliance']['hong_kong_pdpo_compliant'] is True
    
    def test_data_lifecycle_management(self):
        """Test complete data lifecycle including cleanup."""
        identifier = "lifecycle_test"
        
        # Process data
        result = self.pipeline.process_upload(self.customer_data, identifier)
        assert result.success is True
        
        # Verify data exists
        stored_datasets = self.pipeline.list_stored_datasets()
        assert len(stored_datasets) > 0
        
        # Cleanup session
        cleanup_success = self.pipeline.cleanup_session(identifier)
        assert cleanup_success is True
        
        # Verify session removed
        assert identifier not in self.pipeline.current_session
    
    def test_compliance_verification(self):
        """Test GDPR and Hong Kong PDPO compliance features."""
        identifier = "compliance_test"
        
        # Process data
        result = self.pipeline.process_upload(self.customer_data, identifier)
        assert result.success is True
        
        # Verify compliance metadata
        compliance = result.metadata['compliance']
        assert compliance['gdpr_compliant'] is True
        assert compliance['hong_kong_pdpo_compliant'] is True
        assert compliance['original_data_encrypted'] is True
        assert compliance['no_external_pii_transmission'] is True
        
        # Verify LLM-safe data
        llm_result = self.pipeline.get_pseudonymized_for_llm(result.storage_key)
        assert llm_result.success is True
        
        verification = llm_result.metadata['verification_details']
        assert verification['safe_for_external_use'] is True
        assert len(verification['checks_performed']) > 0
    
    def test_performance_benchmarks(self):
        """Test pipeline performance with larger datasets."""
        # Create larger test dataset
        large_data = pd.DataFrame({
            'account_id': [f'ACC{i:06d}' for i in range(100)],
            'name': [f'Customer {i}' for i in range(100)],
            'email': [f'customer{i}@test.com' for i in range(100)],
            'balance': [1000.0 + i for i in range(100)]
        })
        
        identifier = "performance_test"
        
        # Process large dataset
        start_time = datetime.now()
        result = self.pipeline.process_upload(large_data, identifier)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert result.success is True
        assert processing_time < 10.0  # Should complete within 10 seconds
        
        # Verify all data processed correctly
        assert result.pseudonymized_data.shape == large_data.shape
        assert result.display_data.shape == large_data.shape


class TestConvenienceFunctions:
    """Test convenience functions for pipeline access."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        # Update global pipeline for testing
        from src.utils.privacy_pipeline import privacy_pipeline
        privacy_pipeline.storage_path = self.temp_dir
        privacy_pipeline.encrypted_storage.storage_path = self.temp_dir
        
        self.sample_data = pd.DataFrame({
            'customer_id': ['CUST001', 'CUST002'],
            'name': ['John Doe', 'Jane Smith'],
            'email': ['john@test.com', 'jane@test.com']
        })
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_convenience_functions(self):
        """Test convenience functions for pipeline operations."""
        identifier = "convenience_test"
        metadata = {"test": "convenience"}
        
        # Test process_customer_data convenience function
        result = process_customer_data(self.sample_data, identifier, metadata)
        assert result.success is True
        assert result.storage_key is not None
        
        storage_key = result.storage_key
        
        # Test get_display_data convenience function
        display_result = get_display_data(storage_key, privacy_enabled=True)
        assert display_result.success is True
        assert display_result.display_data is not None
        
        # Test get_llm_safe_data convenience function
        llm_result = get_llm_safe_data(storage_key)
        assert llm_result.success is True
        assert llm_result.pseudonymized_data is not None
        
        # Verify LLM data is different from original
        original_names = set(self.sample_data['name'].astype(str))
        pseudo_names = set(llm_result.pseudonymized_data['name'].astype(str))
        assert original_names != pseudo_names  # Should be pseudonymized


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.pipeline = PrivacyPipeline(self.temp_dir, "integration_test_password")
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_telecom_customer_scenario(self):
        """Test realistic telecom customer data scenario."""
        # Simulate Three HK customer data
        telecom_data = pd.DataFrame({
            'account_id': ['3HK123456', '3HK789012', '3HK345678'],
            'customer_name': ['張三', 'Wong Tai Man', 'Lisa Chan'],
            'hkid': ['A123456(7)', 'B789012(3)', 'C345678(9)'],
            'mobile_number': ['+852 9123 4567', '+852 9876 5432', '+852 9555 1234'],
            'email': ['zhang.san@gmail.com', 'wong.taiman@yahoo.com.hk', 'lisa.chan@hotmail.com'],
            'address': ['Flat 12A, 88 Nathan Road, Tsim Sha Tsui', 'Unit 5B, 123 Queen\'s Road, Central', '15樓C室, 456 彌敦道, 旺角'],
            'plan_type': ['5G Unlimited', '4G Premium', '5G Basic'],
            'monthly_bill': [588.0, 388.0, 288.0],
            'contract_end': ['2025-06-30', '2024-12-31', '2025-03-15'],
            'credit_score': [750, 820, 690],
            'last_payment': ['2024-01-15', '2024-01-14', '2024-01-13']
        })
        
        # Process through pipeline
        result = self.pipeline.process_upload(telecom_data, "three_hk_customers")
        assert result.success is True
        
        # Verify PII protection for Hong Kong data
        pii_fields = result.metadata['pii_fields_identified']
        expected_pii = ['account_id', 'customer_name', 'hkid', 'mobile_number', 'email', 'address']
        
        # Should identify most HK-specific PII fields
        assert len(pii_fields) >= 4
        
        # Verify display masking works with Chinese characters
        display_result = self.pipeline.retrieve_for_display(result.storage_key, privacy_enabled=True)
        assert display_result.success is True
        
        # Verify pseudonymized data is safe for external processing
        llm_result = self.pipeline.get_pseudonymized_for_llm(result.storage_key)
        assert llm_result.success is True
        assert llm_result.metadata['pseudonymization_verified'] is True
    
    def test_multi_dataset_processing(self):
        """Test processing multiple datasets in sequence."""
        datasets = [
            ("customer_profiles", pd.DataFrame({
                'id': ['C001', 'C002'], 
                'name': ['User 1', 'User 2'],
                'email': ['user1@test.com', 'user2@test.com']
            })),
            ("purchase_history", pd.DataFrame({
                'customer_id': ['C001', 'C002'],
                'purchase_date': ['2024-01-01', '2024-01-02'],
                'amount': [100.0, 200.0]
            })),
            ("support_tickets", pd.DataFrame({
                'ticket_id': ['T001', 'T002'],
                'customer_id': ['C001', 'C002'],
                'issue': ['billing', 'technical']
            }))
        ]
        
        results = []
        for identifier, data in datasets:
            result = self.pipeline.process_upload(data, identifier)
            assert result.success is True
            results.append(result)
        
        # Verify all datasets processed
        assert len(results) == 3
        
        # Verify pipeline tracks multiple sessions
        status = self.pipeline.get_pipeline_status()
        assert status['current_sessions'] == 3
        assert status['total_processed_datasets'] == 3
        
        # Verify each dataset can be retrieved independently
        for result in results:
            display_result = self.pipeline.retrieve_for_display(result.storage_key)
            assert display_result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 