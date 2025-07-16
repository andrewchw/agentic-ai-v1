"""
Unit tests for data merging functionality - Task 6.3
Tests the DataMerger class and its integration with privacy masking
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.data_merging import DataMerger, MergeStrategy, MergeResult, DataQualityReport
from src.utils.privacy_pipeline import privacy_pipeline


class TestDataMerger:
    """Test the DataMerger class functionality"""

    def setup_method(self):
        """Set up test data for each test"""
        self.merger = DataMerger()
        
        # Sample customer data
        self.customer_df = pd.DataFrame({
            'Account ID': ['ACC001', 'ACC002', 'ACC003', 'ACC004', 'ACC005'],
            'Given Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'Family Name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson'],
            'Email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'],
            'Customer Type': ['Individual', 'Corporate', 'Individual', 'Individual', 'Corporate']
        })
        
        # Sample purchase data (partial overlap with customer data)
        self.purchase_df = pd.DataFrame({
            'Account ID': ['ACC001', 'ACC002', 'ACC003', 'ACC006', 'ACC007'],
            'Purchase Date': ['2024-01-15', '2024-01-20', '2024-01-25', '2024-01-30', '2024-02-01'],
            'Amount': [299.99, 599.99, 199.99, 399.99, 799.99],
            'Plan Type': ['5G Basic', '5G Premium', 'Data Add-on', '5G Pro', '5G Enterprise']
        })

    def test_merger_initialization(self):
        """Test DataMerger initialization"""
        merger = DataMerger()
        assert merger.account_id_column == "Account ID"

    def test_dataset_validation_success(self):
        """Test successful dataset validation"""
        result = self.merger._validate_datasets(self.customer_df, self.purchase_df)
        assert result["valid"] == True
        assert result["message"] == "Validation passed"
        assert len(result["errors"]) == 0

    def test_dataset_validation_missing_account_id(self):
        """Test validation failure when Account ID column is missing"""
        # Remove Account ID from customer data
        invalid_customer_df = self.customer_df.drop(columns=['Account ID'])
        
        result = self.merger._validate_datasets(invalid_customer_df, self.purchase_df)
        assert result["valid"] == False
        assert "missing 'Account ID' column" in result["errors"][0]

    def test_quality_report_generation(self):
        """Test data quality report generation"""
        report = self.merger._generate_quality_report(self.customer_df, self.purchase_df)
        
        assert isinstance(report, DataQualityReport)
        assert report.total_customer_records == 5
        assert report.total_purchase_records == 5
        assert report.matched_records == 3  # ACC001, ACC002, ACC003
        assert len(report.unmatched_customer_ids) == 2  # ACC004, ACC005
        assert len(report.unmatched_purchase_ids) == 2  # ACC006, ACC007
        assert 0.0 <= report.quality_score <= 1.0

    def test_inner_merge_strategy(self):
        """Test inner merge strategy (only matching records)"""
        merge_result = self.merger._perform_merge(self.customer_df, self.purchase_df, MergeStrategy.INNER)
        
        assert merge_result["success"] == True
        merged_df = merge_result["merged_data"]
        assert len(merged_df) == 3  # Only ACC001, ACC002, ACC003 should match

    def test_left_merge_strategy(self):
        """Test left merge strategy (all customer records + matching purchase data)"""
        merge_result = self.merger._perform_merge(self.customer_df, self.purchase_df, MergeStrategy.LEFT)
        
        assert merge_result["success"] == True
        merged_df = merge_result["merged_data"]
        assert len(merged_df) == 5  # All customer records

    def test_outer_merge_strategy(self):
        """Test outer merge strategy (all records from both datasets)"""
        merge_result = self.merger._perform_merge(self.customer_df, self.purchase_df, MergeStrategy.OUTER)
        
        assert merge_result["success"] == True
        merged_df = merge_result["merged_data"]
        assert len(merged_df) == 7  # All unique Account IDs

    def test_merge_with_missing_data(self):
        """Test merge behavior when dataset is None"""
        # Create mock data dict with missing original_data
        customer_data_dict = {"original_data": None, "display_data": None}
        purchase_data_dict = {"original_data": self.purchase_df, "display_data": self.purchase_df}
        
        result = self.merger.merge_datasets(customer_data_dict, purchase_data_dict)
        
        assert result.success == False
        assert "Missing customer or purchase data" in result.message

    def test_merge_with_duplicates(self):
        """Test merge handling of duplicate Account IDs"""
        # Add duplicate Account ID to customer data
        duplicate_customer_df = pd.concat([
            self.customer_df,
            pd.DataFrame({'Account ID': ['ACC001'], 'Given Name': ['John2'], 'Family Name': ['Doe2'], 
                         'Email': ['john2@example.com'], 'Customer Type': ['Individual']})
        ])
        
        report = self.merger._generate_quality_report(duplicate_customer_df, self.purchase_df)
        assert len(report.duplicate_customer_ids) > 0

    def test_merge_with_null_account_ids(self):
        """Test merge handling of null Account IDs"""
        # Add null Account ID to customer data
        null_customer_df = self.customer_df.copy()
        null_customer_df.loc[len(null_customer_df)] = [None, 'Test', 'User', 'test@example.com', 'Individual']
        
        merge_result = self.merger._perform_merge(null_customer_df, self.purchase_df, MergeStrategy.INNER)
        
        # Should still succeed but exclude null records
        assert merge_result["success"] == True


class TestDataMergingWithPrivacy:
    """Test data merging integration with privacy pipeline"""

    def setup_method(self):
        """Set up test data with privacy processing"""
        self.merger = DataMerger()
        
        # Create sample data
        self.customer_df = pd.DataFrame({
            'Account ID': ['ACC001', 'ACC002', 'ACC003'],
            'Given Name': ['John', 'Jane', 'Bob'],
            'Email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
        })
        
        self.purchase_df = pd.DataFrame({
            'Account ID': ['ACC001', 'ACC002', 'ACC003'],
            'Purchase Date': ['2024-01-15', '2024-01-20', '2024-01-25'],
            'Amount': [299.99, 599.99, 199.99],
        })
        
        # Process through privacy pipeline
        customer_result = privacy_pipeline.process_upload(self.customer_df, "test_customer", {})
        purchase_result = privacy_pipeline.process_upload(self.purchase_df, "test_purchase", {})
        
        # Create session state format (similar to upload component)
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

    def test_merge_with_privacy_masking_disabled(self):
        """Test merge with privacy masking disabled (show sensitive data)"""
        result = self.merger.merge_datasets(
            self.customer_data_dict, 
            self.purchase_data_dict, 
            strategy=MergeStrategy.INNER,
            show_sensitive=True
        )
        
        assert result.success == True
        assert result.metadata["show_sensitive"] == True
        assert result.merged_data is not None
        assert len(result.merged_data) == 3  # All should match

    def test_merge_with_privacy_masking_enabled(self):
        """Test merge with privacy masking enabled (hide sensitive data)"""
        result = self.merger.merge_datasets(
            self.customer_data_dict, 
            self.purchase_data_dict, 
            strategy=MergeStrategy.INNER,
            show_sensitive=False
        )
        
        assert result.success == True
        assert result.metadata["show_sensitive"] == False
        
        # Check that display data contains masked values
        if result.display_data is not None and 'customer_Email' in result.display_data.columns:
            email_values = result.display_data['customer_Email'].tolist()
            # Should contain masked email format (e.g., "j***@*******.com")
            assert any("***" in str(email) for email in email_values)

    def test_merge_quality_metrics(self):
        """Test merge quality metrics and reporting"""
        result = self.merger.merge_datasets(self.customer_data_dict, self.purchase_data_dict)
        
        assert result.success == True
        assert "quality_score" in result.quality_report
        assert "matched_records" in result.quality_report
        assert "total_customer_records" in result.quality_report
        assert "total_purchase_records" in result.quality_report
        
        # Quality score should be reasonable (perfect match expected)
        assert result.quality_report["quality_score"] > 0.8 