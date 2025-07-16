"""
Tests for Encrypted JSON Storage Module

Tests the secure local storage system for processed and pseudonymized data.
Validates encryption, decryption, key management, and security features.
"""

import pytest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import secrets
import base64

from src.utils.encrypted_json_storage import (
    EncryptedJSONStorage,
    EncryptionMetadata,
    create_storage,
    store_data,
    load_data
)


class TestEncryptedJSONStorage:
    """Test cases for EncryptedJSONStorage class"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def storage(self, temp_storage_dir):
        """Create storage instance with temporary directory"""
        return EncryptedJSONStorage(temp_storage_dir)

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return {
            "customer_data": [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
            ],
            "metadata": {
                "created_at": "2025-07-16T15:00:00Z",
                "version": "1.0",
                "records_count": 2
            },
            "analysis_results": {
                "total_customers": 2,
                "avg_age": 35.5,
                "demographics": {"male": 1, "female": 1}
            }
        }

    def test_init_creates_storage_directory(self, temp_storage_dir):
        """Test storage directory creation during initialization"""
        storage_path = temp_storage_dir / "encrypted_storage"
        storage = EncryptedJSONStorage(storage_path)
        
        assert storage.storage_dir == storage_path
        assert storage_path.exists()
        assert storage_path.is_dir()

    def test_init_with_default_directory(self):
        """Test initialization with default directory"""
        storage = EncryptedJSONStorage()
        expected_path = Path("data") / "encrypted_storage"
        assert storage.storage_dir == expected_path

    def test_store_and_load_json_basic(self, storage, sample_data):
        """Test basic store and load functionality"""
        password = "test_password_123"
        filename = "test_data"
        
        # Store data
        file_path = storage.store_json(sample_data, filename, password)
        assert file_path.endswith("test_data.encrypted.json")
        assert Path(file_path).exists()
        
        # Load data
        loaded_data = storage.load_json(filename, password)
        assert loaded_data == sample_data

    def test_store_and_load_with_metadata(self, storage, sample_data):
        """Test storing data with additional metadata"""
        password = "test_password_123"
        filename = "test_with_metadata"
        metadata = {"source": "test", "processed_by": "test_user"}
        
        # Store with metadata
        storage.store_json(sample_data, filename, password, metadata)
        
        # Load and verify
        loaded_data = storage.load_json(filename, password)
        assert loaded_data == sample_data

    def test_encryption_with_different_passwords(self, storage, sample_data):
        """Test that different passwords produce different encrypted files"""
        filename1 = "test_pass1"
        filename2 = "test_pass2"
        password1 = "password_one"
        password2 = "password_two"
        
        # Store same data with different passwords
        storage.store_json(sample_data, filename1, password1)
        storage.store_json(sample_data, filename2, password2)
        
        # Read raw encrypted files
        file1_path = storage.storage_dir / f"{filename1}.encrypted.json"
        file2_path = storage.storage_dir / f"{filename2}.encrypted.json"
        
        with open(file1_path) as f1, open(file2_path) as f2:
            content1 = json.load(f1)
            content2 = json.load(f2)
        
        # Encrypted data should be different
        assert content1["encrypted_data"] != content2["encrypted_data"]
        assert content1["salt"] != content2["salt"]
        assert content1["nonce"] != content2["nonce"]

    def test_wrong_password_fails_decryption(self, storage, sample_data):
        """Test that wrong password fails to decrypt data"""
        filename = "test_wrong_password"
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        # Store data
        storage.store_json(sample_data, filename, correct_password)
        
        # Try to load with wrong password
        with pytest.raises(Exception):  # Should raise cryptographic error
            storage.load_json(filename, wrong_password)

    def test_file_not_found_error(self, storage):
        """Test loading non-existent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            storage.load_json("non_existent_file", "password")

    def test_delete_file(self, storage, sample_data):
        """Test file deletion functionality"""
        filename = "test_delete"
        password = "test_password"
        
        # Store and verify file exists
        storage.store_json(sample_data, filename, password)
        assert storage.file_exists(filename)
        
        # Delete file
        result = storage.delete_file(filename)
        assert result is True
        assert not storage.file_exists(filename)
        
        # Try to delete again
        result = storage.delete_file(filename)
        assert result is False

    def test_list_files(self, storage, sample_data):
        """Test listing encrypted files"""
        password = "test_password"
        filenames = ["file1", "file2", "file3"]
        
        # Initially empty
        assert storage.list_files() == []
        
        # Store multiple files
        for filename in filenames:
            storage.store_json(sample_data, filename, password)
        
        # Check list
        file_list = storage.list_files()
        assert len(file_list) == 3
        assert set(file_list) == set(filenames)

    def test_file_exists(self, storage, sample_data):
        """Test file existence checking"""
        filename = "test_exists"
        password = "test_password"
        
        # Initially doesn't exist
        assert not storage.file_exists(filename)
        
        # Store file
        storage.store_json(sample_data, filename, password)
        assert storage.file_exists(filename)
        
        # Delete file
        storage.delete_file(filename)
        assert not storage.file_exists(filename)

    def test_get_file_info(self, storage, sample_data):
        """Test getting file information"""
        filename = "test_info"
        password = "test_password"
        
        # No info for non-existent file
        assert storage.get_file_info(filename) is None
        
        # Store file and get info
        storage.store_json(sample_data, filename, password)
        info = storage.get_file_info(filename)
        
        assert info is not None
        assert info["filename"] == filename
        assert info["algorithm"] == "AES-256-GCM"
        assert info["kdf_iterations"] == 100000
        assert info["size_bytes"] > 0
        assert "path" in info
        assert "modified_time" in info

    def test_cleanup_all(self, storage, sample_data):
        """Test cleanup of all files"""
        password = "test_password"
        filenames = ["cleanup1", "cleanup2", "cleanup3"]
        
        # Store multiple files
        for filename in filenames:
            storage.store_json(sample_data, filename, password)
        
        assert len(storage.list_files()) == 3
        
        # Cleanup all
        deleted_count = storage.cleanup_all()
        assert deleted_count == 3
        assert len(storage.list_files()) == 0

    def test_atomic_file_operations(self, storage, sample_data):
        """Test that file operations are atomic"""
        filename = "test_atomic"
        password = "test_password"
        
        # Mock file operations to simulate failure during write
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.side_effect = OSError("Simulated disk full")
            
            with pytest.raises(OSError):
                storage.store_json(sample_data, filename, password)
            
            # Ensure no partial file was created
            assert not storage.file_exists(filename)

    def test_load_with_full_path(self, storage, sample_data):
        """Test loading file using full path"""
        filename = "test_full_path"
        password = "test_password"
        
        # Store data
        file_path = storage.store_json(sample_data, filename, password)
        
        # Load using full path
        loaded_data = storage.load_json(file_path, password)
        assert loaded_data == sample_data

    def test_large_data_storage(self, storage):
        """Test storing and loading large data sets"""
        # Create large dataset
        large_data = {
            "customers": [
                {
                    "id": i,
                    "name": f"Customer {i}",
                    "email": f"customer{i}@example.com",
                    "data": "x" * 1000  # 1KB per customer
                }
                for i in range(1000)  # 1MB total
            ]
        }
        
        filename = "large_dataset"
        password = "test_password"
        
        # Store and load
        storage.store_json(large_data, filename, password)
        loaded_data = storage.load_json(filename, password)
        
        assert loaded_data == large_data
        assert len(loaded_data["customers"]) == 1000

    def test_unicode_data_handling(self, storage):
        """Test handling of Unicode data"""
        unicode_data = {
            "chinese_names": ["王小明", "李华", "张三"],
            "emojis": ["😀", "🎉", "💼"],
            "special_chars": "åäöñüéè",
            "mixed": "Hello 世界 🌍"
        }
        
        filename = "unicode_test"
        password = "test_password"
        
        # Store and load
        storage.store_json(unicode_data, filename, password)
        loaded_data = storage.load_json(filename, password)
        
        assert loaded_data == unicode_data

    def test_empty_data_storage(self, storage):
        """Test storing empty data structures"""
        empty_data = {}
        filename = "empty_test"
        password = "test_password"
        
        storage.store_json(empty_data, filename, password)
        loaded_data = storage.load_json(filename, password)
        
        assert loaded_data == empty_data

    def test_security_key_derivation(self, storage):
        """Test that key derivation produces different keys for same password with different salts"""
        password = "same_password"
        salt1 = secrets.token_bytes(32)
        salt2 = secrets.token_bytes(32)
        
        key1 = storage._derive_key(password, salt1)
        key2 = storage._derive_key(password, salt2)
        
        assert key1 != key2
        assert len(key1) == 32  # 256 bits
        assert len(key2) == 32  # 256 bits

    def test_encryption_produces_different_outputs(self, storage):
        """Test that encrypting same data produces different outputs due to random nonce"""
        data = b"test data for encryption"
        key = secrets.token_bytes(32)
        
        # Encrypt same data twice
        encrypted1, nonce1, tag1 = storage._encrypt_data(data, key)
        encrypted2, nonce2, tag2 = storage._encrypt_data(data, key)
        
        # Should be different due to random nonce
        assert encrypted1 != encrypted2
        assert nonce1 != nonce2
        assert tag1 != tag2

    def test_encryption_decryption_roundtrip(self, storage):
        """Test encryption and decryption roundtrip"""
        original_data = b"sensitive customer data that needs encryption"
        key = secrets.token_bytes(32)
        
        # Encrypt
        encrypted_data, nonce, tag = storage._encrypt_data(original_data, key)
        
        # Decrypt
        decrypted_data = storage._decrypt_data(encrypted_data, key, nonce, tag)
        
        assert decrypted_data == original_data

    def test_authentication_tag_tampering(self, storage):
        """Test that tampering with authentication tag is detected"""
        data = b"authenticated data"
        key = secrets.token_bytes(32)
        
        # Encrypt data
        encrypted_data, nonce, tag = storage._encrypt_data(data, key)
        
        # Tamper with tag
        tampered_tag = bytearray(tag)
        tampered_tag[0] ^= 1  # Flip one bit
        tampered_tag = bytes(tampered_tag)
        
        # Decryption should fail
        with pytest.raises(Exception):  # InvalidTag or similar
            storage._decrypt_data(encrypted_data, key, nonce, tampered_tag)


class TestConvenienceFunctions:
    """Test convenience functions"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return {"test": "data", "number": 42}

    def test_create_storage(self, temp_storage_dir):
        """Test create_storage convenience function"""
        storage = create_storage(temp_storage_dir)
        assert isinstance(storage, EncryptedJSONStorage)
        assert storage.storage_dir == temp_storage_dir

    def test_store_and_load_data_functions(self, temp_storage_dir, sample_data):
        """Test store_data and load_data convenience functions"""
        filename = "convenience_test"
        password = "test_password"
        
        # Store data
        file_path = store_data(sample_data, filename, password, temp_storage_dir)
        assert file_path.endswith("convenience_test.encrypted.json")
        
        # Load data
        loaded_data = load_data(filename, password, temp_storage_dir)
        assert loaded_data == sample_data


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def storage(self, temp_storage_dir):
        """Create storage instance with temporary directory"""
        return EncryptedJSONStorage(temp_storage_dir)

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return {"test": "data", "number": 42}

    def test_invalid_json_data(self, storage):
        """Test handling of non-serializable data"""
        # Data that can't be JSON serialized
        invalid_data = {"function": lambda x: x}
        
        with pytest.raises(TypeError):
            storage.store_json(invalid_data, "invalid", "password")

    def test_corrupted_file_handling(self, storage, sample_data):
        """Test handling of corrupted encrypted files"""
        filename = "test_corrupted"
        password = "test_password"
        
        # Store valid data
        storage.store_json(sample_data, filename, password)
        
        # Corrupt the file
        file_path = storage.storage_dir / f"{filename}.encrypted.json"
        with open(file_path, 'w') as f:
            f.write("corrupted data")
        
        # Loading should fail gracefully
        with pytest.raises(Exception):
            storage.load_json(filename, password)

    def test_permission_errors(self, storage, sample_data):
        """Test handling of permission errors"""
        filename = "permission_test"
        password = "test_password"
        
        # Store data normally
        storage.store_json(sample_data, filename, password)
        
        # Simulate permission error on delete
        file_path = storage.storage_dir / f"{filename}.encrypted.json"
        
        with patch('os.unlink') as mock_unlink:
            mock_unlink.side_effect = PermissionError("Permission denied")
            
            with pytest.raises(PermissionError):
                storage.delete_file(filename)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 