"""
Comprehensive Integration Testing Framework - Task 16
Tests the complete end-to-end workflow of the Agentic AI Revenue Assistant

This comprehensive test suite validates:
1. Complete data flow: Upload → Privacy Processing → Data Merging
2. Performance testing with realistic data volumes
3. Edge cases and error handling
4. Privacy compliance throughout the pipeline
5. UI integration with backend processing
6. Export functionality and data integrity
7. Cross-component communication and state management

Usage:
    python -m pytest tests/test_comprehensive_integration.py -v
    python -m pytest tests/test_comprehensive_integration.py::TestEndToEndWorkflow -v
    python -m pytest tests/test_comprehensive_integration.py::TestPerformanceIntegration -v
"""

import pytest
import pandas as pd
import tempfile
import shutil
import time
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from unittest.mock import patch, MagicMock

# Import all components for integration testing
from src.components.upload import process_data_through_privacy_pipeline, validate_csv_file
from src.utils.data_merging import DataMerger, MergeStrategy, MergeResult
from src.utils.privacy_pipeline import PrivacyPipeline
from src.utils.integrated_display_masking import process_dataframe_for_display
from src.utils.encrypted_storage import EncryptedStorage
from src.utils.enhanced_field_identification import EnhancedFieldIdentifier
from src.utils.security_pseudonymization import SecurityPseudonymizer


class TestEndToEndWorkflow:
    """Test complete end-to-end data processing workflows"""

    def setup_method(self):
        """Set up test environment with realistic data"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create realistic customer data (medium scale)
        self.customer_data = self._create_realistic_customer_data(100)
        self.purchase_data = self._create_realistic_purchase_data(200)
        
        # Track processing times for performance analysis
        self.processing_times = {}
        
        # Initialize components
        self.data_merger = DataMerger()
        self.privacy_pipeline = PrivacyPipeline()

    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_realistic_customer_data(self, num_records: int) -> pd.DataFrame:
        """Create realistic customer dataset with Hong Kong-specific data"""
        import random
        from datetime import datetime, timedelta
        
        # Hong Kong specific names and data patterns
        family_names = ["Wong", "Chan", "Li", "Cheung", "Lau", "Ng", "Ma", "Tang", "Leung", "Ho"]
        given_names = ["Wai Ming", "Siu Fung", "Ka Man", "Chi Keung", "Mei Ling", "Pak Ho", "Wing Yi", "Kin Chung"]
        chinese_names = ["偉明", "小鳳", "嘉文", "志強", "美玲", "柏豪", "詠儀", "建忠"]
        
        districts = ["Central", "TST", "Mong Kok", "Causeway Bay", "Wan Chai", "Sha Tin", "Tuen Mun", "Tai Po"]
        customer_types = ["Individual", "Business", "Corporate", "SME"]
        customer_classes = ["Premium", "Standard", "Basic", "VIP"]
        
        data = []
        for i in range(num_records):
            account_id = f"3HK{str(i+1).zfill(6)}"
            family_name = random.choice(family_names)
            given_name = random.choice(given_names)
            chinese_name = random.choice(chinese_names)
            
            # Realistic Hong Kong data patterns
            email_domains = ["gmail.com", "yahoo.com.hk", "hotmail.com", "netvigator.com", "pccw.com"]
            email = f"{given_name.lower().replace(' ', '.')}.{family_name.lower()}@{random.choice(email_domains)}"
            
            # HKID pattern: 1-2 letters + 6 digits + (check digit)
            hkid_letters = random.choice(["A", "B", "C", "D", "E", "G", "H", "K", "L", "M", "N", "P", "R", "S", "T", "U", "W", "X", "Y", "Z"])
            hkid_number = f"{hkid_letters}{random.randint(100000, 999999)}({random.randint(0, 9)})"
            
            phone = f"+852 {random.randint(2000, 9999)} {random.randint(1000, 9999)}"
            
            # Birth date (18-80 years old)
            birth_year = datetime.now().year - random.randint(18, 80)
            birth_date = f"{birth_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            
            data.append({
                "Account ID": account_id,
                "Family Name": family_name,
                "Given Name": given_name,
                "Chinese Given Name": chinese_name,
                "Gender": random.choice(["M", "F"]),
                "Date of Birth": birth_date,
                "Email": email,
                "ID Number": hkid_number,
                "Phone Number": phone,
                "District": random.choice(districts),
                "Customer Type": random.choice(customer_types),
                "Customer Class": random.choice(customer_classes),
                "Company Name": f"{family_name} {random.choice(['Trading', 'Holdings', 'Enterprise', 'International'])}" if random.random() > 0.7 else ""
            })
        
        return pd.DataFrame(data)

    def _create_realistic_purchase_data(self, num_records: int) -> pd.DataFrame:
        """Create realistic purchase history with Three HK products"""
        import random
        from datetime import datetime, timedelta
        
        # Three HK specific products and pricing
        products = [
            "5G Infinite Plan", "4G Unlimited", "5G Premium", "4G Standard",
            "IoT SIM Card", "Roaming Package", "IDD Service", "Mobile Broadband",
            "Family Plan", "Business Plan", "Prepaid Card", "Device Insurance"
        ]
        
        categories = [
            "Mobile Plans", "Roaming Services", "Device & Accessories", 
            "Value Added Services", "Business Solutions", "IoT Services"
        ]
        
        # Get account IDs from customer data for realistic relationships
        customer_account_ids = self.customer_data["Account ID"].tolist()
        
        data = []
        for i in range(num_records):
            # Use existing customer IDs to ensure some matches, add some unmatched for testing
            if i < len(customer_account_ids) * 1.5:  # 150% coverage for some mismatches
                account_id = random.choice(customer_account_ids)
            else:
                account_id = f"3HK{random.randint(900000, 999999)}"  # Some unmatched accounts
            
            product = random.choice(products)
            category = random.choice(categories)
            
            # Realistic Three HK pricing (HKD)
            if "5G" in product:
                amount = random.uniform(388, 988)
            elif "4G" in product:
                amount = random.uniform(188, 588)
            elif "Roaming" in product:
                amount = random.uniform(88, 388)
            else:
                amount = random.uniform(38, 288)
            
            # Purchase date within last 2 years
            days_ago = random.randint(1, 730)
            purchase_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            data.append({
                "Account ID": account_id,
                "Product Name": product,
                "Category": category,
                "Amount": round(amount, 2),
                "Purchase Date": purchase_date,
                "Quantity": random.randint(1, 5),
                "Payment Method": random.choice(["Credit Card", "Bank Transfer", "Auto-Pay", "Cash"])
            })
        
        return pd.DataFrame(data)

    def test_complete_upload_to_merge_workflow(self):
        """Test the complete workflow from CSV upload through privacy processing to data merging"""
        print(f"\n🔄 Testing complete upload-to-merge workflow with {len(self.customer_data)} customers, {len(self.purchase_data)} purchases")
        
        # Step 1: Validate and process customer data through privacy pipeline
        start_time = time.time()
        
        customer_success, customer_message, customer_processed = process_data_through_privacy_pipeline(
            self.customer_data, "integration_customer", "customer_test.csv"
        )
        
        customer_processing_time = time.time() - start_time
        self.processing_times["customer_processing"] = customer_processing_time
        
        assert customer_success is True, f"Customer processing failed: {customer_message}"
        assert customer_processed is not None
        assert "original_data" in customer_processed
        assert "display_data" in customer_processed  
        assert "pseudonymized_data" in customer_processed
        assert "metadata" in customer_processed
        
        print(f"✅ Customer data processed in {customer_processing_time:.3f}s")
        
        # Step 2: Validate and process purchase data through privacy pipeline
        start_time = time.time()
        
        purchase_success, purchase_message, purchase_processed = process_data_through_privacy_pipeline(
            self.purchase_data, "integration_purchase", "purchase_test.csv"
        )
        
        purchase_processing_time = time.time() - start_time
        self.processing_times["purchase_processing"] = purchase_processing_time
        
        assert purchase_success is True, f"Purchase processing failed: {purchase_message}"
        assert purchase_processed is not None
        
        print(f"✅ Purchase data processed in {purchase_processing_time:.3f}s")
        
        # Step 3: Perform data merging with privacy masking disabled (show sensitive)
        start_time = time.time()
        
        merge_result_unmasked = self.data_merger.merge_datasets(
            customer_processed,
            purchase_processed,
            strategy=MergeStrategy.LEFT,
            show_sensitive=True
        )
        
        merge_time_unmasked = time.time() - start_time
        self.processing_times["merge_unmasked"] = merge_time_unmasked
        
        assert merge_result_unmasked.success is True, f"Unmasked merge failed: {merge_result_unmasked.message}"
        assert merge_result_unmasked.merged_data is not None
        assert len(merge_result_unmasked.merged_data) > 0
        
        print(f"✅ Unmasked data merge completed in {merge_time_unmasked:.3f}s - {len(merge_result_unmasked.merged_data)} records")
        
        # Step 4: Perform data merging with privacy masking enabled (hide sensitive)
        start_time = time.time()
        
        merge_result_masked = self.data_merger.merge_datasets(
            customer_processed,
            purchase_processed,
            strategy=MergeStrategy.LEFT,
            show_sensitive=False
        )
        
        merge_time_masked = time.time() - start_time
        self.processing_times["merge_masked"] = merge_time_masked
        
        assert merge_result_masked.success is True, f"Masked merge failed: {merge_result_masked.message}"
        assert merge_result_masked.display_data is not None
        assert len(merge_result_masked.display_data) > 0
        
        print(f"✅ Masked data merge completed in {merge_time_masked:.3f}s - {len(merge_result_masked.display_data)} records")
        
        # Step 5: Validate privacy compliance
        self._validate_privacy_compliance(merge_result_unmasked, merge_result_masked)
        
        # Step 6: Validate data quality and integrity
        self._validate_data_quality(merge_result_unmasked, customer_processed, purchase_processed)
        
        # Step 7: Test real-time privacy toggle functionality
        self._test_realtime_privacy_toggle(merge_result_unmasked.merged_data)
        
        total_time = sum(self.processing_times.values())
        print(f"🎉 Complete workflow successful in {total_time:.3f}s total")
        
        # Performance assertions
        assert customer_processing_time < 2.0, f"Customer processing too slow: {customer_processing_time:.3f}s"
        assert purchase_processing_time < 2.0, f"Purchase processing too slow: {purchase_processing_time:.3f}s"
        assert merge_time_unmasked < 1.0, f"Unmasked merge too slow: {merge_time_unmasked:.3f}s"
        assert merge_time_masked < 1.0, f"Masked merge too slow: {merge_time_masked:.3f}s"

    def _validate_privacy_compliance(self, unmasked_result: MergeResult, masked_result: MergeResult):
        """Validate that privacy settings are properly enforced"""
        print("🔒 Validating privacy compliance...")
        
        # Check unmasked result has original sensitive data
        unmasked_data = unmasked_result.merged_data
        if 'customer_Email' in unmasked_data.columns:
            emails = unmasked_data['customer_Email'].dropna()
            assert any('@' in str(email) and '***' not in str(email) for email in emails), \
                "Unmasked data should contain original emails"
        
        if 'customer_Given Name' in unmasked_data.columns:
            names = unmasked_data['customer_Given Name'].dropna()
            assert any(len(str(name)) > 3 and '***' not in str(name) for name in names), \
                "Unmasked data should contain original names"
        
        # Check masked result has masked sensitive data  
        masked_data = masked_result.display_data
        if 'customer_Email' in masked_data.columns:
            emails = masked_data['customer_Email'].dropna()
            assert any('***' in str(email) for email in emails), \
                "Masked data should contain masked emails"
        
        if 'customer_Given Name' in masked_data.columns:
            names = masked_data['customer_Given Name'].dropna()
            assert any('***' in str(name) for name in names), \
                "Masked data should contain masked names"
        
        print("✅ Privacy compliance validated")

    def _validate_data_quality(self, merge_result: MergeResult, customer_data: Dict, purchase_data: Dict):
        """Validate data quality and integrity after merging"""
        print("📊 Validating data quality...")
        
        merged_data = merge_result.merged_data
        quality_report = merge_result.quality_report
        
        # Basic data integrity
        assert len(merged_data) > 0, "Merged data should not be empty"
        assert len(merged_data.columns) > 10, "Merged data should have columns from both datasets"
        
        # Quality metrics
        assert quality_report is not None, "Quality report should be available"
        assert "quality_score" in quality_report, "Quality score should be calculated"
        assert 0 <= quality_report["quality_score"] <= 1, "Quality score should be between 0 and 1"
        
        # Data relationships
        customer_count = len(customer_data["original_data"])
        purchase_count = len(purchase_data["original_data"])
        merged_count = len(merged_data)
        
        # For LEFT join, we should have at least as many records as customers (some may have multiple purchases)
        assert merged_count >= customer_count * 0.5, \
            f"Merged count {merged_count} seems too low for {customer_count} customers"
        
        print(f"✅ Data quality validated - {merged_count} records from {customer_count} customers + {purchase_count} purchases")

    def _test_realtime_privacy_toggle(self, merged_data: pd.DataFrame):
        """Test real-time privacy toggle functionality"""
        print("🔀 Testing real-time privacy toggle...")
        
        # Test masking application
        masked_result = process_dataframe_for_display(merged_data, show_sensitive=False)
        assert "dataframe" in masked_result
        assert masked_result["show_sensitive"] is False
        
        # Test unmasking 
        unmasked_result = process_dataframe_for_display(merged_data, show_sensitive=True)
        assert "dataframe" in unmasked_result  
        assert unmasked_result["show_sensitive"] is True
        
        # Data should be different when masked vs unmasked
        if 'customer_Email' in merged_data.columns:
            masked_emails = masked_result["dataframe"]['customer_Email'].tolist()
            unmasked_emails = unmasked_result["dataframe"]['customer_Email'].tolist()
            
            # Should have different representations
            assert masked_emails != unmasked_emails, "Masked and unmasked emails should be different"
        
        print("✅ Real-time privacy toggle validated")

    def test_error_handling_and_edge_cases(self):
        """Test error handling and edge cases in the integration workflow"""
        print("\n⚠️  Testing error handling and edge cases...")
        
        # Test empty dataframes
        empty_customer = pd.DataFrame(columns=["Account ID", "Given Name", "Email"])
        empty_purchase = pd.DataFrame(columns=["Account ID", "Product Name", "Amount"])
        
        # Should handle empty data gracefully
        customer_success, customer_message, customer_processed = process_data_through_privacy_pipeline(
            empty_customer, "empty_customer", "empty.csv"
        )
        
        # Could succeed with empty data (depends on implementation)
        if not customer_success:
            assert "empty" in customer_message.lower() or "no data" in customer_message.lower()
        
        # Test mismatched schemas
        mismatched_customer = pd.DataFrame({
            "AccountID": ["ACC001"],  # Wrong column name
            "CustomerName": ["John Doe"],  # Wrong column name
            "EmailAddress": ["john@test.com"]  # Wrong column name
        })
        
        # Should handle schema mismatches
        schema_success, schema_message, schema_processed = process_data_through_privacy_pipeline(
            mismatched_customer, "mismatched_customer", "mismatched.csv"
        )
        
        # May succeed (depending on flexibility) or provide helpful error message
        print(f"Schema mismatch handling: {schema_message}")
        
        # Test very large field values
        large_data_customer = pd.DataFrame({
            "Account ID": ["ACC001"],
            "Given Name": ["A" * 1000],  # Very long name
            "Email": ["test@" + "x" * 100 + ".com"],  # Very long email
        })
        
        large_success, large_message, large_processed = process_data_through_privacy_pipeline(
            large_data_customer, "large_data_customer", "large.csv"
        )
        
        print(f"Large data handling: {large_message}")
        
        print("✅ Error handling tests completed")

    def test_cross_merge_strategy_consistency(self):
        """Test that privacy settings work consistently across all merge strategies"""
        print("\n🔄 Testing cross-merge strategy consistency...")
        
        # Process smaller datasets for faster testing
        small_customer = self.customer_data.head(20)
        small_purchase = self.purchase_data.head(40)
        
        customer_success, _, customer_processed = process_data_through_privacy_pipeline(
            small_customer, "strategy_customer", "customer.csv"
        )
        purchase_success, _, purchase_processed = process_data_through_privacy_pipeline(
            small_purchase, "strategy_purchase", "purchase.csv"
        )
        
        assert customer_success and purchase_success
        
        strategies = [MergeStrategy.INNER, MergeStrategy.LEFT, MergeStrategy.RIGHT, MergeStrategy.OUTER]
        
        for strategy in strategies:
            print(f"  Testing {strategy.value} merge strategy...")
            
            # Test with masking enabled
            masked_result = self.data_merger.merge_datasets(
                customer_processed, purchase_processed, strategy=strategy, show_sensitive=False
            )
            
            # Test with masking disabled  
            unmasked_result = self.data_merger.merge_datasets(
                customer_processed, purchase_processed, strategy=strategy, show_sensitive=True
            )
            
            assert masked_result.success, f"{strategy.value} masked merge failed"
            assert unmasked_result.success, f"{strategy.value} unmasked merge failed"
            
            # Verify privacy settings are recorded correctly
            assert masked_result.metadata["show_sensitive"] is False
            assert unmasked_result.metadata["show_sensitive"] is True
            
            print(f"    ✅ {strategy.value}: {len(masked_result.display_data) if masked_result.display_data is not None else 0} masked, {len(unmasked_result.merged_data) if unmasked_result.merged_data is not None else 0} unmasked")
        
        print("✅ Cross-merge strategy consistency validated")


class TestPerformanceIntegration:
    """Test performance characteristics of the integrated system"""

    def setup_method(self):
        """Set up performance testing environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.performance_metrics = {}

    def teardown_method(self):
        """Clean up performance test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_large_dataset_performance(self):
        """Test system performance with larger, realistic datasets"""
        print(f"\n🚀 Testing large dataset performance...")
        
        # Create larger datasets (realistic scale)
        large_customer_data = self._create_performance_customer_data(1000)  # 1K customers
        large_purchase_data = self._create_performance_purchase_data(5000)  # 5K purchases
        
        print(f"Created {len(large_customer_data)} customers, {len(large_purchase_data)} purchases")
        
        # Time the complete workflow
        workflow_start = time.time()
        
        # Step 1: Process customer data
        customer_start = time.time()
        customer_success, customer_message, customer_processed = process_data_through_privacy_pipeline(
            large_customer_data, "perf_customer", "large_customer.csv"
        )
        customer_time = time.time() - customer_start
        self.performance_metrics["large_customer_processing"] = customer_time
        
        assert customer_success, f"Large customer processing failed: {customer_message}"
        print(f"  Customer processing: {customer_time:.3f}s")
        
        # Step 2: Process purchase data
        purchase_start = time.time()
        purchase_success, purchase_message, purchase_processed = process_data_through_privacy_pipeline(
            large_purchase_data, "perf_purchase", "large_purchase.csv"
        )
        purchase_time = time.time() - purchase_start
        self.performance_metrics["large_purchase_processing"] = purchase_time
        
        assert purchase_success, f"Large purchase processing failed: {purchase_message}"
        print(f"  Purchase processing: {purchase_time:.3f}s")
        
        # Step 3: Data merging
        merge_start = time.time()
        data_merger = DataMerger()
        merge_result = data_merger.merge_datasets(
            customer_processed, purchase_processed, 
            strategy=MergeStrategy.LEFT, show_sensitive=False
        )
        merge_time = time.time() - merge_start
        self.performance_metrics["large_merge"] = merge_time
        
        assert merge_result.success, f"Large merge failed: {merge_result.message}"
        print(f"  Data merging: {merge_time:.3f}s")
        
        # Step 4: Privacy toggle performance
        toggle_start = time.time()
        if merge_result.merged_data is not None:
            masked_result = process_dataframe_for_display(merge_result.merged_data, show_sensitive=False)
            unmasked_result = process_dataframe_for_display(merge_result.merged_data, show_sensitive=True)
        toggle_time = time.time() - toggle_start
        self.performance_metrics["privacy_toggle"] = toggle_time
        
        print(f"  Privacy toggle: {toggle_time:.3f}s")
        
        total_time = time.time() - workflow_start
        self.performance_metrics["total_workflow"] = total_time
        
        print(f"🎉 Large dataset workflow completed in {total_time:.3f}s")
        
        # Performance assertions (reasonable thresholds for 1K+5K records)
        assert customer_time < 10.0, f"Customer processing too slow: {customer_time:.3f}s"
        assert purchase_time < 10.0, f"Purchase processing too slow: {purchase_time:.3f}s"
        assert merge_time < 5.0, f"Merge too slow: {merge_time:.3f}s"
        assert toggle_time < 2.0, f"Privacy toggle too slow: {toggle_time:.3f}s"
        assert total_time < 20.0, f"Total workflow too slow: {total_time:.3f}s"
        
        # Data integrity with large dataset
        merged_count = len(merge_result.merged_data) if merge_result.merged_data is not None else 0
        customer_count = len(large_customer_data)
        
        assert merged_count > customer_count * 0.3, \
            f"Merged count {merged_count} seems too low for {customer_count} customers"
        
        print(f"✅ Performance validated: {merged_count} records merged")

    def _create_performance_customer_data(self, num_records: int) -> pd.DataFrame:
        """Create large-scale customer data for performance testing"""
        import random
        import string
        from datetime import datetime, timedelta
        
        print(f"  Generating {num_records} customer records...")
        
        data = []
        for i in range(num_records):
            # Use more realistic data generation for performance testing
            account_id = f"3HK{str(i+1).zfill(7)}"
            
            # Random names (faster generation)
            family_name = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
            given_name = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
            
            email = f"{given_name.lower()}.{family_name.lower()}@test{random.randint(1,100)}.com"
            hkid = f"{random.choice(['A','B','C','D'])}{random.randint(100000,999999)}({random.randint(0,9)})"
            phone = f"+852 {random.randint(2000,9999)} {random.randint(1000,9999)}"
            
            data.append({
                "Account ID": account_id,
                "Family Name": family_name,
                "Given Name": given_name,
                "Chinese Given Name": f"中文{i}",
                "Gender": random.choice(["M", "F"]),
                "Email": email,
                "ID Number": hkid,
                "Phone Number": phone,
                "Customer Type": random.choice(["Individual", "Business"]),
                "Customer Class": random.choice(["Premium", "Standard", "Basic"]),
                "District": f"District{random.randint(1,18)}",
                "Company Name": f"Company{i}" if random.random() > 0.8 else ""
            })
        
        return pd.DataFrame(data)

    def _create_performance_purchase_data(self, num_records: int) -> pd.DataFrame:
        """Create large-scale purchase data for performance testing"""
        import random
        from datetime import datetime, timedelta
        
        print(f"  Generating {num_records} purchase records...")
        
        products = [f"Product{i}" for i in range(1, 21)]  # 20 different products
        categories = [f"Category{i}" for i in range(1, 6)]  # 5 categories
        
        data = []
        for i in range(num_records):
            # Link to customer accounts (with some unmatched for realism)
            if i < num_records * 0.8:  # 80% matched
                customer_id = random.randint(1, min(1000, num_records // 5))  # Reference customers
                account_id = f"3HK{str(customer_id).zfill(7)}"
            else:  # 20% unmatched
                account_id = f"3HK{random.randint(900000, 999999)}"
            
            data.append({
                "Account ID": account_id,
                "Product Name": random.choice(products),
                "Category": random.choice(categories), 
                "Amount": round(random.uniform(50, 1000), 2),
                "Purchase Date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
                "Quantity": random.randint(1, 5),
                "Payment Method": random.choice(["Credit Card", "Bank Transfer", "Auto-Pay"])
            })
        
        return pd.DataFrame(data)

    def test_memory_usage_monitoring(self):
        """Monitor memory usage during processing"""
        import psutil
        import os
        
        print(f"\n💾 Testing memory usage...")
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"  Initial memory: {initial_memory:.1f} MB")
        
        # Create moderate dataset and process
        customer_data = self._create_performance_customer_data(500)
        memory_after_customer = process.memory_info().rss / 1024 / 1024
        
        purchase_data = self._create_performance_purchase_data(1000)
        memory_after_purchase = process.memory_info().rss / 1024 / 1024
        
        # Process through pipeline
        customer_success, _, customer_processed = process_data_through_privacy_pipeline(
            customer_data, "memory_customer", "customer.csv"
        )
        memory_after_processing = process.memory_info().rss / 1024 / 1024
        
        purchase_success, _, purchase_processed = process_data_through_privacy_pipeline(
            purchase_data, "memory_purchase", "purchase.csv"
        )
        memory_after_both = process.memory_info().rss / 1024 / 1024
        
        # Merge data
        data_merger = DataMerger()
        merge_result = data_merger.merge_datasets(
            customer_processed, purchase_processed, 
            strategy=MergeStrategy.LEFT, show_sensitive=False
        )
        final_memory = process.memory_info().rss / 1024 / 1024
        
        print(f"  After customer generation: {memory_after_customer:.1f} MB")
        print(f"  After purchase generation: {memory_after_purchase:.1f} MB") 
        print(f"  After customer processing: {memory_after_processing:.1f} MB")
        print(f"  After purchase processing: {memory_after_both:.1f} MB")
        print(f"  After merging: {final_memory:.1f} MB")
        
        total_memory_increase = final_memory - initial_memory
        print(f"  Total memory increase: {total_memory_increase:.1f} MB")
        
        # Memory usage should be reasonable (less than 500MB increase for this dataset size)
        assert total_memory_increase < 500, f"Memory usage too high: {total_memory_increase:.1f} MB"
        
        assert customer_success and purchase_success and merge_result.success
        
        print("✅ Memory usage within acceptable limits")


class TestComplianceIntegration:
    """Test privacy and compliance aspects of the integrated system"""

    def test_gdpr_compliance_workflow(self):
        """Test GDPR compliance throughout the complete workflow"""
        print(f"\n🔒 Testing GDPR compliance workflow...")
        
        # Create test data with clear PII
        customer_data = pd.DataFrame({
            "Account ID": ["3HK000001", "3HK000002"],
            "Given Name": ["John", "Jane"],
            "Family Name": ["Doe", "Smith"],
            "Email": ["john.doe@example.com", "jane.smith@test.com"],
            "ID Number": ["A123456(7)", "B789012(3)"],
            "Phone Number": ["+852 9123 4567", "+852 9876 5432"]
        })
        
        purchase_data = pd.DataFrame({
            "Account ID": ["3HK000001", "3HK000002"], 
            "Product Name": ["5G Plan", "4G Plan"],
            "Amount": [588.0, 388.0]
        })
        
        # Process through privacy pipeline
        customer_success, _, customer_processed = process_data_through_privacy_pipeline(
            customer_data, "gdpr_customer", "customer.csv"
        )
        purchase_success, _, purchase_processed = process_data_through_privacy_pipeline(
            purchase_data, "gdpr_purchase", "purchase.csv" 
        )
        
        assert customer_success and purchase_success
        
        # Verify GDPR compliance in processed data
        customer_metadata = customer_processed["metadata"]
        assert "compliance" in customer_metadata
        assert customer_metadata["compliance"]["no_external_pii_transmission"] is True
        
        # Verify pseudonymized data contains no original PII
        pseudonymized = customer_processed["pseudonymized_data"]
        pseudo_emails = pseudonymized["Email"].tolist()
        
        # Should not contain original email domains
        assert not any("@example.com" in str(email) for email in pseudo_emails)
        assert not any("@test.com" in str(email) for email in pseudo_emails)
        
        # Original names should not be in pseudonymized data
        pseudo_names = pseudonymized["Given Name"].tolist()
        assert "John" not in pseudo_names
        assert "Jane" not in pseudo_names
        
        print("✅ GDPR compliance validated")

    def test_hong_kong_pdpo_compliance(self):
        """Test Hong Kong PDPO compliance"""
        print(f"\n🇭🇰 Testing Hong Kong PDPO compliance...")
        
        # Test with Hong Kong specific PII patterns
        hk_customer_data = pd.DataFrame({
            "Account ID": ["3HK000001"],
            "Chinese Given Name": ["偉明"],
            "ID Number": ["A123456(7)"],  # Hong Kong ID format
            "Phone Number": ["+852 9123 4567"],  # Hong Kong phone
            "Email": ["weiming@netvigator.com"]  # Hong Kong ISP
        })
        
        success, message, processed = process_data_through_privacy_pipeline(
            hk_customer_data, "pdpo_test", "hk_customer.csv"
        )
        
        assert success, f"Hong Kong data processing failed: {message}"
        
        # Verify Hong Kong specific patterns are detected and handled
        metadata = processed["metadata"]
        pii_fields = metadata.get("pii_fields_identified", [])
        
        # Should detect Hong Kong ID pattern
        assert "ID Number" in pii_fields
        
        # Verify masking handles Hong Kong patterns correctly
        display_data = processed["display_data"]
        masked_hkid = display_data["ID Number"].iloc[0]
        assert "A******" in str(masked_hkid) or "***" in str(masked_hkid)
        
        print("✅ Hong Kong PDPO compliance validated")


if __name__ == "__main__":
    # Run comprehensive integration tests
    pytest.main([__file__, "-v", "--tb=short"]) 