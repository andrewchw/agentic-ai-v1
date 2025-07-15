"""
Tests for the Encrypted Storage System

This test suite validates the security, functionality, and compliance
of the local encrypted storage system for PII data.
"""

import os
import json
import tempfile
import shutil
import pytest
import pandas as pd
import base64
from datetime import datetime
from unittest.mock import patch

# Import the modules to test
from src.utils.encrypted_storage import (
    EncryptedStorage, EncryptionMetadata, StorageEntry,
    store_pii_dataframe, retrieve_pii_dataframe, get_storage_status
)


class TestEncryptedStorage:
    """Test suite for EncryptedStorage class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = EncryptedStorage(
            storage_path=self.temp_dir,
            master_password="test_password_123"
        )
        
        # Sample test data
        self.sample_df = pd.DataFrame({
            'account_id': ['ACC123456', 'ACC789012', 'ACC345678'],
            'name': ['John Doe', 'Jane Smith', 'Bob Wilson'],
            'email': ['john@example.com', 'jane@test.com', 'bob@company.com'],
            'hkid': ['A123456(7)', 'B789012(3)', 'C345678(9)'],
            'phone': ['+852 1234 5678', '+852 9876 5432', '+852 5555 1234'],
            'balance': [1000.50, 2500.75, 750.25]
        })
        
        self.sample_json = {
            'customer_profile': {
                'id': 'CUST001',
                'preferences': ['mobile', 'internet'],
                'risk_score': 0.25
            }
        }
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test storage system initialization."""
        assert os.path.exists(self.temp_dir)
        assert self.storage.storage_path == self.temp_dir
        assert self.storage.master_password == "test_password_123"
        
        # Check master key hash file was created
        password_file = os.path.join(self.temp_dir, ".master_key_hash")
        assert os.path.exists(password_file)
    
    def test_key_derivation(self):
        """Test key derivation functionality."""
        salt1 = b'test_salt_16byte'
        salt2 = b'different_salt16'
        password = "test_password"
        
        key1 = self.storage._derive_key(salt1, password)
        key2 = self.storage._derive_key(salt1, password)
        key3 = self.storage._derive_key(salt2, password)
        
        # Same salt and password should produce same key
        assert key1 == key2
        
        # Different salt should produce different key
        assert key1 != key3
        
        # Key should be 32 bytes (256 bits)
        assert len(key1) == 32
    
    def test_encryption_decryption_cycle(self):
        """Test basic encryption and decryption."""
        test_data = "This is sensitive PII data that must be encrypted"
        password = "encryption_password"
        
        # Encrypt data
        entry = self.storage._encrypt_data(test_data, password)
        
        # Verify entry structure
        assert isinstance(entry, StorageEntry)
        assert entry.encrypted_data
        assert entry.nonce
        assert entry.salt
        assert isinstance(entry.metadata, EncryptionMetadata)
        
        # Decrypt data
        decrypted_data = self.storage._decrypt_data(entry, password)
        
        # Verify decryption
        assert decrypted_data == test_data
    
    def test_dataframe_storage_retrieval(self):
        """Test DataFrame storage and retrieval."""
        identifier = "customer_data_test"
        metadata = {"source": "test", "processed_at": datetime.now().isoformat()}
        
        # Store DataFrame
        storage_key = self.storage.store_dataframe(self.sample_df, identifier, metadata)
        
        assert storage_key.startswith("df_")
        assert identifier in storage_key
        
        # Verify file was created
        file_path = os.path.join(self.temp_dir, f"{storage_key}.enc")
        assert os.path.exists(file_path)
        
        # Retrieve DataFrame
        retrieved_df, retrieved_metadata = self.storage.retrieve_dataframe(storage_key)
        
        # Verify data integrity
        pd.testing.assert_frame_equal(self.sample_df, retrieved_df)
        assert retrieved_metadata == metadata
    
    def test_json_storage_retrieval(self):
        """Test JSON data storage and retrieval."""
        identifier = "customer_profile_test"
        
        # Store JSON data
        storage_key = self.storage.store_json(self.sample_json, identifier)
        
        assert storage_key.startswith("json_")
        assert identifier in storage_key
        
        # Retrieve JSON data
        retrieved_json = self.storage.retrieve_json(storage_key)
        
        # Verify data integrity
        assert retrieved_json == self.sample_json
    
    def test_access_tracking(self):
        """Test access count and timestamp tracking."""
        storage_key = self.storage.store_json(self.sample_json, "access_test")
        
        # Initial access
        self.storage.retrieve_json(storage_key)
        
        # Load and check access count
        file_path = os.path.join(self.temp_dir, f"{storage_key}.enc")
        with open(file_path, 'r') as f:
            entry_dict = json.load(f)
        
        assert entry_dict['metadata']['access_count'] == 1
        assert entry_dict['metadata']['last_accessed'] is not None
        
        # Second access
        self.storage.retrieve_json(storage_key)
        
        with open(file_path, 'r') as f:
            entry_dict = json.load(f)
        
        assert entry_dict['metadata']['access_count'] == 2
    
    def test_list_stored_data(self):
        """Test listing stored data functionality."""
        # Store multiple items
        key1 = self.storage.store_dataframe(self.sample_df, "test1")
        key2 = self.storage.store_json(self.sample_json, "test2")
        
        # List stored data
        stored_data = self.storage.list_stored_data()
        
        assert len(stored_data) == 2
        
        storage_keys = [item['storage_key'] for item in stored_data]
        assert key1 in storage_keys
        assert key2 in storage_keys
        
        # Verify metadata structure
        for item in stored_data:
            assert 'storage_key' in item
            assert 'encrypted_at' in item
            assert 'data_type' in item
            assert 'file_size' in item
    
    def test_delete_stored_data(self):
        """Test secure deletion of stored data."""
        storage_key = self.storage.store_json(self.sample_json, "delete_test")
        
        # Verify file exists
        file_path = os.path.join(self.temp_dir, f"{storage_key}.enc")
        assert os.path.exists(file_path)
        
        # Delete data
        result = self.storage.delete_stored_data(storage_key)
        assert result is True
        
        # Verify file is deleted
        assert not os.path.exists(file_path)
        
        # Test deletion of non-existent key
        result = self.storage.delete_stored_data("nonexistent_key")
        assert result is False
    
    def test_encryption_integrity_verification(self):
        """Test encryption integrity verification."""
        storage_key = self.storage.store_json(self.sample_json, "integrity_test")
        
        # Verify integrity of valid data
        assert self.storage.verify_encryption_integrity(storage_key) is True
        
        # Test with corrupted data
        file_path = os.path.join(self.temp_dir, f"{storage_key}.enc")
        with open(file_path, 'r') as f:
            entry_dict = json.load(f)
        
        # Corrupt the encrypted data
        entry_dict['encrypted_data'] = entry_dict['encrypted_data'][:-10] + "corrupted"
        
        with open(file_path, 'w') as f:
            json.dump(entry_dict, f)
        
        # Verify integrity check fails
        assert self.storage.verify_encryption_integrity(storage_key) is False
    
    def test_wrong_password_fails(self):
        """Test that wrong password fails decryption."""
        test_data = "secret data"
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        # Encrypt with correct password
        entry = self.storage._encrypt_data(test_data, correct_password)
        
        # Try to decrypt with wrong password - should raise exception
        with pytest.raises(Exception):
            self.storage._decrypt_data(entry, wrong_password)
    
    def test_file_not_found_handling(self):
        """Test handling of missing storage files."""
        nonexistent_key = "nonexistent_storage_key"
        
        with pytest.raises(FileNotFoundError):
            self.storage.retrieve_dataframe(nonexistent_key)
        
        with pytest.raises(FileNotFoundError):
            self.storage.retrieve_json(nonexistent_key)
    
    def test_encryption_status(self):
        """Test encryption system status reporting."""
        # Store some test data
        self.storage.store_dataframe(self.sample_df, "status_test1")
        self.storage.store_json(self.sample_json, "status_test2")
        
        status = self.storage.get_encryption_status()
        
        assert status['encryption_algorithm'] == 'AES-256-GCM'
        assert status['key_derivation'] == 'PBKDF2-SHA256'
        assert status['storage_path'] == self.temp_dir
        assert status['total_stored_items'] == 2
        assert 'df' in status['storage_types']
        assert 'json' in status['storage_types']
        assert status['total_storage_size'] > 0
    
    def test_large_dataframe_storage(self):
        """Test storage of large DataFrame."""
        # Create larger test DataFrame
        large_df = pd.DataFrame({
            'id': range(1000),
            'name': [f'User_{i}' for i in range(1000)],
            'email': [f'user{i}@example.com' for i in range(1000)],
            'data': [f'sensitive_data_{i}' for i in range(1000)]
        })
        
        storage_key = self.storage.store_dataframe(large_df, "large_test")
        retrieved_df, _ = self.storage.retrieve_dataframe(storage_key)
        
        pd.testing.assert_frame_equal(large_df, retrieved_df)
        assert len(retrieved_df) == 1000
    
    def test_special_characters_and_unicode(self):
        """Test handling of special characters and Unicode."""
        unicode_df = pd.DataFrame({
            'chinese_name': ['李小明', '王大華', '陳美麗'],
            'special_chars': ['@#$%^&*()', '+=[]{}|\\', '~`!"'],
            'emoji': ['😀😃😄', '🎉🎊🎈', '💼💻📧']
        })
        
        storage_key = self.storage.store_dataframe(unicode_df, "unicode_test")
        retrieved_df, _ = self.storage.retrieve_dataframe(storage_key)
        
        pd.testing.assert_frame_equal(unicode_df, retrieved_df)
    
    def test_metadata_preservation(self):
        """Test that DataFrame metadata is preserved."""
        # Create DataFrame with specific dtypes
        typed_df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.1, 2.2, 3.3],
            'str_col': ['a', 'b', 'c'],
            'bool_col': [True, False, True]
        })
        
        # Ensure specific dtypes
        typed_df['int_col'] = typed_df['int_col'].astype('int64')
        typed_df['float_col'] = typed_df['float_col'].astype('float64')
        typed_df['str_col'] = typed_df['str_col'].astype('object')
        typed_df['bool_col'] = typed_df['bool_col'].astype('bool')
        
        storage_key = self.storage.store_dataframe(typed_df, "dtype_test")
        retrieved_df, _ = self.storage.retrieve_dataframe(storage_key)
        
        # Check that basic data is preserved
        pd.testing.assert_frame_equal(typed_df, retrieved_df, check_dtype=False)
        
        # Check shape preservation
        assert typed_df.shape == retrieved_df.shape


class TestConvenienceFunctions:
    """Test convenience functions for PII storage."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        # Use a temporary storage for testing
        global encrypted_storage
        from src.utils.encrypted_storage import encrypted_storage
        encrypted_storage.storage_path = self.temp_dir
        
        self.sample_df = pd.DataFrame({
            'pii_data': ['sensitive1', 'sensitive2', 'sensitive3']
        })
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_convenience_functions(self):
        """Test convenience functions for PII storage."""
        metadata = {"type": "customer_pii", "classification": "confidential"}
        
        # Store using convenience function
        storage_key = store_pii_dataframe(self.sample_df, "pii_test", metadata)
        
        assert storage_key.startswith("df_")
        
        # Retrieve using convenience function
        retrieved_df, retrieved_metadata = retrieve_pii_dataframe(storage_key)
        
        pd.testing.assert_frame_equal(self.sample_df, retrieved_df)
        assert retrieved_metadata == metadata
    
    def test_storage_status_function(self):
        """Test storage status convenience function."""
        # Store some data first
        store_pii_dataframe(self.sample_df, "status_test")
        
        status = get_storage_status()
        
        assert isinstance(status, dict)
        assert 'encryption_algorithm' in status
        assert 'total_stored_items' in status
        assert status['total_stored_items'] >= 1


class TestSecurityCompliance:
    """Test security and compliance features."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = EncryptedStorage(self.temp_dir, "secure_password_123")
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_no_plaintext_storage(self):
        """Test that no plaintext PII is stored on disk."""
        sensitive_data = "HKID: A123456(7), Email: john@example.com"
        storage_key = self.storage.store_json({"data": sensitive_data}, "sensitive_test")
        
        # Read the encrypted file
        file_path = os.path.join(self.temp_dir, f"{storage_key}.enc")
        with open(file_path, 'r') as f:
            file_content = f.read()
        
        # Verify sensitive data is not visible in plaintext
        assert "A123456(7)" not in file_content
        assert "john@example.com" not in file_content
        assert "encrypted_data" in file_content
    
    def test_salt_uniqueness(self):
        """Test that each encryption uses a unique salt."""
        data = "same data"
        
        entry1 = self.storage._encrypt_data(data, "password")
        entry2 = self.storage._encrypt_data(data, "password")
        
        # Different salts should be used
        assert entry1.salt != entry2.salt
        
        # Different encrypted outputs despite same input
        assert entry1.encrypted_data != entry2.encrypted_data
    
    def test_nonce_uniqueness(self):
        """Test that each encryption uses a unique nonce."""
        data = "same data"
        
        entry1 = self.storage._encrypt_data(data, "password")
        entry2 = self.storage._encrypt_data(data, "password")
        
        # Different nonces should be used
        assert entry1.nonce != entry2.nonce
    
    def test_key_derivation_iterations(self):
        """Test that key derivation uses sufficient iterations."""
        # This test ensures PBKDF2 uses enough iterations (100,000+)
        # The actual iteration count is set in the _derive_key method
        salt = b'test_salt_16byte'
        password = "test_password"
        
        import time
        start_time = time.time()
        key = self.storage._derive_key(salt, password)
        derivation_time = time.time() - start_time
        
        # Key derivation should take some time (indicating sufficient iterations)
        # On modern hardware, 100,000 iterations should take at least a few milliseconds
        assert derivation_time > 0.001  # At least 1ms
        assert len(key) == 32  # 256-bit key
    
    def test_authentication_tag_verification(self):
        """Test that GCM authentication tag prevents tampering."""
        data = "important data"
        entry = self.storage._encrypt_data(data, "password")
        
        # Tamper with encrypted data
        encrypted_bytes = base64.b64decode(entry.encrypted_data)
        tampered_bytes = encrypted_bytes[:-1] + b'\x00'  # Change last byte
        entry.encrypted_data = base64.b64encode(tampered_bytes).decode()
        
        # Decryption should fail due to authentication tag mismatch
        with pytest.raises(Exception):
            self.storage._decrypt_data(entry, "password")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 