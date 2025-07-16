"""
Tests for Secure File Operations Module

Tests the secure file read, write, and delete operations with strict access controls.
Validates atomic operations, secure permissions, path validation, and security features.
"""

import pytest
import tempfile
import os
import stat
from pathlib import Path
from unittest.mock import patch, MagicMock
import secrets
import platform

from src.utils.secure_file_operations import (
    SecureFileOperations,
    FileOperationResult,
    create_secure_file_ops,
    secure_write_file,
    secure_read_file,
    secure_delete_file
)


class TestSecureFileOperations:
    """Test cases for SecureFileOperations class"""

    @pytest.fixture
    def temp_base_dir(self):
        """Create temporary base directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def file_ops(self, temp_base_dir):
        """Create secure file operations instance"""
        return SecureFileOperations(temp_base_dir)

    @pytest.fixture
    def sample_data(self):
        """Sample binary data for testing"""
        return b"Test data for secure file operations\nWith multiple lines\nAnd special characters: \x00\x01\xff"

    @pytest.fixture
    def session_id(self):
        """Sample session ID for testing"""
        return "test_session_123"

    def test_init_creates_base_directory(self, temp_base_dir):
        """Test that initialization creates base directory"""
        test_dir = temp_base_dir / "test_subdir"
        ops = SecureFileOperations(test_dir)
        
        assert ops.base_directory == test_dir.resolve()
        assert test_dir.exists()

    def test_validate_path_relative(self, file_ops):
        """Test path validation with relative paths"""
        # Valid relative path
        validated = file_ops.validate_path("test_file.txt")
        expected = file_ops.base_directory / "test_file.txt"
        assert validated == expected.resolve()
        
        # Valid nested relative path
        validated = file_ops.validate_path("subdir/test_file.txt")
        expected = file_ops.base_directory / "subdir" / "test_file.txt"
        assert validated == expected.resolve()

    def test_validate_path_absolute_within_base(self, file_ops):
        """Test path validation with absolute paths within base directory"""
        test_file = file_ops.base_directory / "test_file.txt"
        validated = file_ops.validate_path(str(test_file))
        assert validated == test_file.resolve()

    def test_validate_path_traversal_attack(self, file_ops):
        """Test that path validation prevents directory traversal attacks"""
        # Directory traversal attempts should fail
        with pytest.raises(ValueError, match="Path outside allowed directory"):
            file_ops.validate_path("../../../etc/passwd")
        
        with pytest.raises(ValueError, match="Path outside allowed directory"):
            file_ops.validate_path("subdir/../../../sensitive_file")
        
        # Absolute path outside base directory should fail
        with pytest.raises(ValueError, match="Path outside allowed directory"):
            file_ops.validate_path("/etc/passwd")

    def test_validate_path_with_session(self, file_ops, session_id):
        """Test path validation with session-specific constraints"""
        # Create session directory
        session_dir = file_ops.base_directory / session_id
        session_dir.mkdir()
        
        # Valid path within session
        validated = file_ops.validate_path(f"{session_id}/test_file.txt", session_id)
        expected = session_dir / "test_file.txt"
        assert validated == expected.resolve()
        
        # Invalid path outside session
        with pytest.raises(ValueError, match="Path outside session directory"):
            file_ops.validate_path("other_session/test_file.txt", session_id)

    def test_atomic_write_basic(self, file_ops, sample_data):
        """Test basic atomic write operation"""
        file_path = "test_file.txt"
        
        result = file_ops.atomic_write(file_path, sample_data)
        
        assert result.success is True
        assert result.bytes_processed == len(sample_data)
        assert result.path is not None
        assert result.path.exists()
        
        # Verify content
        assert result.path.read_bytes() == sample_data

    def test_atomic_write_creates_directories(self, file_ops, sample_data):
        """Test that atomic write creates parent directories"""
        file_path = "subdir/nested/test_file.txt"
        
        result = file_ops.atomic_write(file_path, sample_data)
        
        assert result.success is True
        assert result.path.parent.exists()
        assert result.path.read_bytes() == sample_data

    def test_atomic_write_with_session(self, file_ops, sample_data, session_id):
        """Test atomic write with session validation"""
        # Create session directory
        session_dir = file_ops.base_directory / session_id
        session_dir.mkdir()
        
        file_path = f"{session_id}/test_file.txt"
        
        result = file_ops.atomic_write(file_path, sample_data, session_id)
        
        assert result.success is True
        assert result.path.read_bytes() == sample_data

    def test_secure_read_basic(self, file_ops, sample_data):
        """Test basic secure read operation"""
        file_path = "test_file.txt"
        
        # First write the file
        write_result = file_ops.atomic_write(file_path, sample_data)
        assert write_result.success is True
        
        # Then read it
        read_result = file_ops.secure_read(file_path)
        
        assert read_result.success is True
        assert read_result.bytes_processed == len(sample_data)
        assert read_result.path == write_result.path

    def test_secure_read_nonexistent_file(self, file_ops):
        """Test secure read of non-existent file"""
        result = file_ops.secure_read("nonexistent_file.txt")
        
        assert result.success is False
        assert "File not found" in result.message

    def test_secure_read_directory(self, file_ops):
        """Test secure read of directory (should fail)"""
        dir_path = "test_dir"
        (file_ops.base_directory / dir_path).mkdir()
        
        result = file_ops.secure_read(dir_path)
        
        assert result.success is False
        assert "Path is not a file" in result.message

    def test_secure_delete_basic(self, file_ops, sample_data):
        """Test basic secure delete operation"""
        file_path = "test_file.txt"
        
        # Create file
        write_result = file_ops.atomic_write(file_path, sample_data)
        assert write_result.success is True
        assert write_result.path.exists()
        
        # Delete file
        delete_result = file_ops.secure_delete(file_path)
        
        assert delete_result.success is True
        assert not write_result.path.exists()

    def test_secure_delete_with_overwrite(self, file_ops, sample_data):
        """Test secure delete with overwrite passes"""
        file_path = "test_file.txt"
        overwrite_passes = 5
        
        # Create file
        write_result = file_ops.atomic_write(file_path, sample_data)
        assert write_result.success is True
        
        # Delete with overwrite
        delete_result = file_ops.secure_delete(file_path, overwrite_passes)
        
        assert delete_result.success is True
        assert not write_result.path.exists()
        assert delete_result.bytes_processed == len(sample_data) * overwrite_passes

    def test_secure_delete_nonexistent_file(self, file_ops):
        """Test secure delete of non-existent file"""
        result = file_ops.secure_delete("nonexistent_file.txt")
        
        assert result.success is False
        assert "File not found" in result.message

    def test_set_secure_permissions(self, file_ops, sample_data):
        """Test setting secure file permissions"""
        file_path = "test_file.txt"
        
        # Create file
        result = file_ops.atomic_write(file_path, sample_data)
        assert result.success is True
        
        # Check permissions
        file_stat = result.path.stat()
        
        if not platform.system() == "Windows":
            # Unix-like: Check that only owner has read/write permissions
            mode = stat.filemode(file_stat.st_mode)
            assert mode[1:4] == "rw-"  # Owner: read/write
            assert mode[4:7] == "---"  # Group: no permissions
            assert mode[7:10] == "---"  # Other: no permissions

    def test_list_directory(self, file_ops, sample_data):
        """Test directory listing functionality"""
        # Create some test files
        files = ["file1.txt", "file2.txt", "file3.txt"]
        for filename in files:
            file_ops.atomic_write(filename, sample_data)
        
        # List directory
        result = file_ops.list_directory(".")
        
        assert result.success is True
        assert "3 files" in result.message

    def test_list_nonexistent_directory(self, file_ops):
        """Test listing non-existent directory"""
        result = file_ops.list_directory("nonexistent_dir")
        
        assert result.success is False
        assert "Directory not found" in result.message

    def test_file_exists(self, file_ops, sample_data):
        """Test file existence checking"""
        file_path = "test_file.txt"
        
        # File doesn't exist initially
        assert file_ops.file_exists(file_path) is False
        
        # Create file
        file_ops.atomic_write(file_path, sample_data)
        
        # File exists now
        assert file_ops.file_exists(file_path) is True

    def test_get_file_info(self, file_ops, sample_data):
        """Test getting file information"""
        file_path = "test_file.txt"
        
        # Non-existent file
        info = file_ops.get_file_info(file_path)
        assert info is None
        
        # Create file and get info
        file_ops.atomic_write(file_path, sample_data)
        info = file_ops.get_file_info(file_path)
        
        assert info is not None
        assert info["name"] == "test_file.txt"
        assert info["size"] == len(sample_data)
        assert "created" in info
        assert "modified" in info
        assert "permissions" in info

    def test_cleanup_directory(self, file_ops, sample_data):
        """Test directory cleanup functionality"""
        # Create test subdirectory with files
        subdir = "test_subdir"
        (file_ops.base_directory / subdir).mkdir()
        
        files = [f"{subdir}/file{i}.txt" for i in range(3)]
        for filename in files:
            file_ops.atomic_write(filename, sample_data)
        
        # Cleanup directory
        result = file_ops.cleanup_directory(subdir)
        
        assert result.success is True
        assert "3 files deleted" in result.message
        
        # Verify files are gone
        for filename in files:
            assert not file_ops.file_exists(filename)

    def test_large_file_operations(self, file_ops):
        """Test operations with large files"""
        # Create 1MB of data
        large_data = secrets.token_bytes(1024 * 1024)
        file_path = "large_file.dat"
        
        # Write large file
        write_result = file_ops.atomic_write(file_path, large_data)
        assert write_result.success is True
        assert write_result.bytes_processed == len(large_data)
        
        # Read large file
        read_result = file_ops.secure_read(file_path)
        assert read_result.success is True
        assert read_result.bytes_processed == len(large_data)
        
        # Delete large file with overwrite
        delete_result = file_ops.secure_delete(file_path, overwrite_passes=1)
        assert delete_result.success is True

    def test_concurrent_operations(self, file_ops, sample_data):
        """Test concurrent file operations"""
        import threading
        
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                file_path = f"thread_{thread_id}_file.txt"
                thread_data = sample_data + f"_thread_{thread_id}".encode()
                
                # Write file
                write_result = file_ops.atomic_write(file_path, thread_data)
                
                # Read file
                read_result = file_ops.secure_read(file_path)
                
                # Delete file
                delete_result = file_ops.secure_delete(file_path)
                
                results.append((thread_id, write_result.success, read_result.success, delete_result.success))
                
            except Exception as e:
                errors.append((thread_id, e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify no errors and all operations succeeded
        assert len(errors) == 0
        assert len(results) == 5
        
        for thread_id, write_ok, read_ok, delete_ok in results:
            assert write_ok is True
            assert read_ok is True
            assert delete_ok is True

    def test_error_handling_invalid_data(self, file_ops):
        """Test error handling with invalid operations"""
        # Try to write to invalid path
        result = file_ops.atomic_write("../../../invalid_path.txt", b"data")
        assert result.success is False
        assert "Invalid file path" in result.message

    def test_atomic_operation_failure_cleanup(self, file_ops, sample_data):
        """Test that failed atomic operations clean up properly"""
        file_path = "test_file.txt"
        
        # Mock file operations to simulate failure
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.side_effect = OSError("Simulated disk full")
            
            result = file_ops.atomic_write(file_path, sample_data)
            
            assert result.success is False
            assert "Write failed" in result.message
            
            # Ensure no partial files were left behind
            assert not file_ops.file_exists(file_path)

    @pytest.mark.skipif(platform.system() == "Windows", reason="Unix permissions test")
    def test_permissions_unix(self, file_ops, sample_data):
        """Test file permissions on Unix-like systems"""
        file_path = "test_permissions.txt"
        
        result = file_ops.atomic_write(file_path, sample_data)
        assert result.success is True
        
        # Check that permissions are set correctly (0o600)
        file_stat = result.path.stat()
        permissions = stat.S_IMODE(file_stat.st_mode)
        expected = stat.S_IRUSR | stat.S_IWUSR  # 0o600
        assert permissions == expected

    def test_overwrite_functionality(self, file_ops):
        """Test secure overwrite functionality"""
        # Create a file with known content
        original_data = b"A" * 1000  # 1KB of 'A' characters
        file_path = "test_overwrite.txt"
        
        write_result = file_ops.atomic_write(file_path, original_data)
        assert write_result.success is True
        
        # Overwrite and delete
        delete_result = file_ops.secure_delete(file_path, overwrite_passes=3)
        assert delete_result.success is True
        assert not write_result.path.exists()


class TestConvenienceFunctions:
    """Test convenience functions"""

    @pytest.fixture
    def temp_base_dir(self):
        """Create temporary base directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_data(self):
        """Sample binary data for testing"""
        return b"Test data for convenience functions"

    def test_create_secure_file_ops(self, temp_base_dir):
        """Test create_secure_file_ops convenience function"""
        ops = create_secure_file_ops(temp_base_dir)
        assert isinstance(ops, SecureFileOperations)
        assert ops.base_directory == temp_base_dir.resolve()

    def test_convenience_functions(self, temp_base_dir, sample_data):
        """Test convenience functions for file operations"""
        file_path = "convenience_test.txt"
        
        # Write file
        write_result = secure_write_file(file_path, sample_data, temp_base_dir)
        assert write_result.success is True
        
        # Read file
        read_result = secure_read_file(file_path, temp_base_dir)
        assert read_result.success is True
        
        # Delete file
        delete_result = secure_delete_file(file_path, overwrite_passes=1, base_directory=temp_base_dir)
        assert delete_result.success is True


class TestFileOperationResult:
    """Test FileOperationResult dataclass"""

    def test_file_operation_result_creation(self):
        """Test creating FileOperationResult objects"""
        result = FileOperationResult(
            success=True,
            message="Operation successful",
            path=Path("/test/path"),
            bytes_processed=1024
        )
        
        assert result.success is True
        assert result.message == "Operation successful"
        assert result.path == Path("/test/path")
        assert result.bytes_processed == 1024

    def test_file_operation_result_defaults(self):
        """Test FileOperationResult with default values"""
        result = FileOperationResult(
            success=False,
            message="Operation failed"
        )
        
        assert result.success is False
        assert result.message == "Operation failed"
        assert result.path is None
        assert result.bytes_processed is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 