"""
Local Data Storage System Integration and Security Tests

Comprehensive validation of the complete local data storage system including:
- Encrypted JSON Storage
- Session Management  
- Secure File Operations
- Data Cleanup Procedures

Tests cover integration, security vulnerabilities, performance, and compliance.
"""

import pytest
import tempfile
import time
import threading
import secrets
import os
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from src.utils.encrypted_json_storage import EncryptedJSONStorage
from src.utils.session_manager import get_session_manager, shutdown_session_manager
from src.utils.secure_file_operations import SecureFileOperations
from src.utils.data_cleanup import (
    get_cleanup_manager, 
    shutdown_cleanup_manager,
    CleanupLevel,
    CleanupStatus
)


class TestLocalStorageIntegration:
    """Integration tests for the complete local data storage system"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def storage_system(self, temp_storage_dir):
        """Set up complete storage system"""
        # Initialize all components
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        cleanup_manager = get_cleanup_manager(base_storage_dir=temp_storage_dir)
        
        yield {
            'session_manager': session_manager,
            'cleanup_manager': cleanup_manager,
            'base_dir': temp_storage_dir
        }
        
        # Cleanup
        shutdown_cleanup_manager()
        shutdown_session_manager()

    @pytest.fixture
    def sample_sensitive_data(self):
        """Sample sensitive data for testing"""
        return {
            "customer_data": {
                "pii": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "hkid": "A123456(7)",
                    "phone": "+852-9876-5432"
                },
                "financial": {
                    "account_number": "1234567890",
                    "balance": 50000.00,
                    "credit_limit": 10000.00
                }
            },
            "analysis_results": {
                "risk_score": 2.5,
                "recommendations": ["increase_limit", "premium_service"],
                "processed_at": datetime.now().isoformat()
            },
            "session_metadata": {
                "user_id": "user_123",
                "session_start": datetime.now().isoformat(),
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0..."
            }
        }

    def test_end_to_end_workflow(self, storage_system, sample_sensitive_data):
        """Test complete end-to-end workflow with all components"""
        session_manager = storage_system['session_manager']
        cleanup_manager = storage_system['cleanup_manager']
        
        # Phase 1: Create session and store data
        session_id = session_manager.create_session("test_user", {"role": "admin"})
        assert session_id is not None
        
        # Store multiple data files
        files_to_store = {
            "customer_profile": sample_sensitive_data["customer_data"],
            "analysis_results": sample_sensitive_data["analysis_results"],
            "session_metadata": sample_sensitive_data["session_metadata"]
        }
        
        for filename, data in files_to_store.items():
            success = session_manager.store_data(session_id, filename, data)
            assert success is True
        
        # Phase 2: Verify data storage and retrieval
        for filename, original_data in files_to_store.items():
            retrieved_data = session_manager.load_data(session_id, filename)
            assert retrieved_data == original_data
        
        # Verify session exists and has data
        session_files = session_manager.list_session_files(session_id)
        assert len(session_files) == len(files_to_store)
        
        # Phase 3: Perform cleanup and verification
        cleanup_result = cleanup_manager.cleanup_session(session_id, CleanupLevel.THOROUGH)
        assert cleanup_result.status == CleanupStatus.COMPLETED
        assert cleanup_result.verification_passed is True
        
        # Phase 4: Verify complete data removal
        # Session should no longer exist
        session = session_manager.get_session(session_id)
        assert session is None
        
        # Files should be gone
        for filename in files_to_store.keys():
            data = session_manager.load_data(session_id, filename)
            assert data is None

    def test_multi_session_isolation(self, storage_system, sample_sensitive_data):
        """Test isolation between multiple concurrent sessions"""
        session_manager = storage_system['session_manager']
        
        # Create multiple sessions
        sessions = []
        for i in range(3):
            session_id = session_manager.create_session(f"user_{i}")
            sessions.append(session_id)
            
            # Store unique data in each session
            unique_data = {**sample_sensitive_data["customer_data"], "user_id": i}
            session_manager.store_data(session_id, "user_data", unique_data)
        
        # Verify session isolation
        for i, session_id in enumerate(sessions):
            data = session_manager.load_data(session_id, "user_data")
            assert data is not None
            assert data["user_id"] == i
            
            # Verify cannot access other sessions' data
            for j, other_session_id in enumerate(sessions):
                if i != j:
                    # Should not be able to access with wrong session ID
                    other_data = session_manager.load_data(other_session_id, "user_data")
                    assert other_data["user_id"] != i

    def test_concurrent_operations_stress(self, storage_system, sample_sensitive_data):
        """Test system under concurrent load"""
        session_manager = storage_system['session_manager']
        
        def worker_thread(thread_id):
            """Worker function for concurrent testing"""
            try:
                # Create session
                session_id = session_manager.create_session(f"user_{thread_id}")
                
                # Store data
                thread_data = {**sample_sensitive_data, "thread_id": thread_id}
                success = session_manager.store_data(session_id, "thread_data", thread_data)
                assert success is True
                
                # Read data multiple times
                for _ in range(5):
                    data = session_manager.load_data(session_id, "thread_data")
                    assert data is not None
                    assert data["thread_id"] == thread_id
                
                return session_id, True
                
            except Exception as e:
                return thread_id, f"Error: {e}"
        
        # Run concurrent operations
        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all operations succeeded
        successful_sessions = []
        for result in results:
            if isinstance(result[1], bool) and result[1] is True:
                successful_sessions.append(result[0])
            else:
                pytest.fail(f"Thread {result[0]} failed: {result[1]}")
        
        assert len(successful_sessions) == num_threads

    def test_encryption_strength_validation(self, storage_system, sample_sensitive_data):
        """Test encryption strength and security"""
        session_manager = storage_system['session_manager']
        base_dir = storage_system['base_dir']
        
        # Create session and store data
        session_id = session_manager.create_session("security_test_user")
        session_manager.store_data(session_id, "sensitive_data", sample_sensitive_data)
        
        # Find the encrypted file
        encrypted_files = list(base_dir.rglob("*.encrypted.json"))
        assert len(encrypted_files) > 0
        
        encrypted_file = encrypted_files[0]
        
        # Read raw encrypted file content
        with open(encrypted_file, 'r') as f:
            encrypted_content = json.load(f)
        
        # Verify encrypted data structure
        assert "encrypted_data" in encrypted_content
        assert "salt" in encrypted_content
        assert "nonce" in encrypted_content
        assert "tag" in encrypted_content
        assert "algorithm" in encrypted_content
        assert encrypted_content["algorithm"] == "AES-256-GCM"
        
        # Verify encrypted data doesn't contain plaintext
        encrypted_data_bytes = encrypted_content["encrypted_data"]
        assert "John Doe" not in encrypted_data_bytes
        assert "john.doe@example.com" not in encrypted_data_bytes
        assert "A123456(7)" not in encrypted_data_bytes

    def test_attack_vector_directory_traversal(self, storage_system):
        """Test protection against directory traversal attacks"""
        session_manager = storage_system['session_manager']
        
        session_id = session_manager.create_session("attacker")
        
        # Attempt directory traversal attacks
        attack_patterns = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config",
            "../sensitive_file.txt",
            "/etc/passwd",
            "C:\\Windows\\System32\\config",
            "subdir/../../../sensitive_data"
        ]
        
        for pattern in attack_patterns:
            # Should fail to store data outside allowed directory
            success = session_manager.store_data(session_id, pattern, {"attack": "data"})
            assert success is False
            
            # Should fail to load data from outside allowed directory
            data = session_manager.load_data(session_id, pattern)
            assert data is None

    def test_memory_cleanup_verification(self, storage_system, sample_sensitive_data):
        """Test memory cleanup and data destruction"""
        session_manager = storage_system['session_manager']
        cleanup_manager = storage_system['cleanup_manager']
        
        # Create session with sensitive data
        session_id = session_manager.create_session("memory_test_user")
        session_manager.store_data(session_id, "sensitive_data", sample_sensitive_data)
        
        # Get session object reference
        session = session_manager.get_session(session_id)
        encryption_key = session.encryption_key
        
        # Perform thorough cleanup
        cleanup_result = cleanup_manager.cleanup_session(session_id, CleanupLevel.THOROUGH)
        assert cleanup_result.status == CleanupStatus.COMPLETED
        assert cleanup_result.memory_cleared is True
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Verify session is destroyed
        assert session_manager.get_session(session_id) is None

    def test_emergency_cleanup_procedures(self, storage_system, sample_sensitive_data):
        """Test emergency cleanup procedures"""
        session_manager = storage_system['session_manager']
        cleanup_manager = storage_system['cleanup_manager']
        
        # Create multiple sessions with data
        session_ids = []
        for i in range(3):
            session_id = session_manager.create_session(f"emergency_user_{i}")
            session_manager.store_data(session_id, "data", sample_sensitive_data)
            session_ids.append(session_id)
        
        # Verify sessions exist
        for session_id in session_ids:
            assert session_manager.get_session(session_id) is not None
        
        # Perform emergency cleanup
        emergency_result = cleanup_manager.emergency_cleanup()
        assert emergency_result.level == CleanupLevel.EMERGENCY
        assert emergency_result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]
        
        # Verify all sessions are destroyed
        for session_id in session_ids:
            assert session_manager.get_session(session_id) is None

    def test_performance_benchmarks(self, storage_system):
        """Test performance under various loads"""
        session_manager = storage_system['session_manager']
        
        # Test 1: Large data storage and retrieval
        session_id = session_manager.create_session("performance_user")
        
        # Generate 1MB of data
        large_data = {
            "bulk_data": "x" * (1024 * 1024),  # 1MB string
            "metadata": {"size": "1MB", "test": "performance"}
        }
        
        # Measure storage time
        start_time = time.time()
        success = session_manager.store_data(session_id, "large_data", large_data)
        storage_time = time.time() - start_time
        
        assert success is True
        assert storage_time < 5.0  # Should complete within 5 seconds
        
        # Measure retrieval time
        start_time = time.time()
        retrieved_data = session_manager.load_data(session_id, "large_data")
        retrieval_time = time.time() - start_time
        
        assert retrieved_data is not None
        assert retrieval_time < 5.0  # Should complete within 5 seconds
        assert retrieved_data == large_data
        
        # Test 2: Multiple small files
        files_count = 100
        small_data = {"test": "data", "index": 0}
        
        start_time = time.time()
        for i in range(files_count):
            small_data["index"] = i
            success = session_manager.store_data(session_id, f"file_{i}", small_data)
            assert success is True
        bulk_storage_time = time.time() - start_time
        
        # Should handle 100 small files efficiently
        assert bulk_storage_time < 30.0  # Should complete within 30 seconds

    def test_data_integrity_validation(self, storage_system, sample_sensitive_data):
        """Test data integrity through multiple operations"""
        session_manager = storage_system['session_manager']
        
        session_id = session_manager.create_session("integrity_user")
        
        # Store data
        session_manager.store_data(session_id, "integrity_test", sample_sensitive_data)
        
        # Retrieve and verify multiple times
        for _ in range(10):
            retrieved_data = session_manager.load_data(session_id, "integrity_test")
            assert retrieved_data == sample_sensitive_data
        
        # Modify and store again
        modified_data = {**sample_sensitive_data, "modified": True}
        session_manager.store_data(session_id, "integrity_test", modified_data)
        
        # Verify modification
        final_data = session_manager.load_data(session_id, "integrity_test")
        assert final_data == modified_data
        assert final_data != sample_sensitive_data

    def test_session_timeout_security(self, temp_storage_dir, sample_sensitive_data):
        """Test session timeout security measures"""
        # Create session manager with very short timeout
        session_manager = get_session_manager(
            base_storage_dir=temp_storage_dir / "sessions",
            session_timeout_minutes=0.01  # ~0.6 seconds
        )
        
        try:
            session_id = session_manager.create_session("timeout_user")
            session_manager.store_data(session_id, "test_data", sample_sensitive_data)
            
            # Verify session exists
            session = session_manager.get_session(session_id)
            assert session is not None
            
            # Wait for timeout
            time.sleep(1)
            
            # Session should be expired and inaccessible
            session = session_manager.get_session(session_id)
            assert session is None
            
            # Data should be inaccessible
            data = session_manager.load_data(session_id, "test_data")
            assert data is None
            
        finally:
            shutdown_session_manager()

    def test_cleanup_verification_completeness(self, storage_system, sample_sensitive_data):
        """Test completeness of cleanup verification"""
        session_manager = storage_system['session_manager']
        cleanup_manager = storage_system['cleanup_manager']
        base_dir = storage_system['base_dir']
        
        # Create session and store multiple files
        session_id = session_manager.create_session("cleanup_verification_user")
        
        test_files = {
            "file1": sample_sensitive_data,
            "file2": {"test": "data2"},
            "file3": {"test": "data3"}
        }
        
        for filename, data in test_files.items():
            session_manager.store_data(session_id, filename, data)
        
        # Get initial file count
        initial_files = list(base_dir.rglob("*.encrypted.json"))
        initial_count = len(initial_files)
        assert initial_count >= len(test_files)
        
        # Perform cleanup
        cleanup_result = cleanup_manager.cleanup_session(session_id, CleanupLevel.THOROUGH)
        assert cleanup_result.status == CleanupStatus.COMPLETED
        assert cleanup_result.verification_passed is True
        
        # Verify files are gone
        remaining_files = list(base_dir.rglob("*.encrypted.json"))
        # Should have fewer files (session files should be deleted)
        assert len(remaining_files) < initial_count

    def test_error_resilience(self, storage_system, sample_sensitive_data):
        """Test system resilience to various error conditions"""
        session_manager = storage_system['session_manager']
        cleanup_manager = storage_system['cleanup_manager']
        
        # Test 1: Invalid data handling
        session_id = session_manager.create_session("error_test_user")
        
        # Try to store invalid data (non-serializable)
        invalid_data = {"function": lambda x: x}
        success = session_manager.store_data(session_id, "invalid", invalid_data)
        assert success is False
        
        # System should still be functional
        success = session_manager.store_data(session_id, "valid", sample_sensitive_data)
        assert success is True
        
        # Test 2: Cleanup resilience
        cleanup_result = cleanup_manager.cleanup_session(session_id, CleanupLevel.STANDARD)
        # Should complete despite previous errors
        assert cleanup_result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]


class TestSecurityVulnerabilities:
    """Specific security vulnerability tests"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_encryption_key_exposure(self, temp_storage_dir):
        """Test that encryption keys are never exposed"""
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        
        try:
            session_id = session_manager.create_session("key_exposure_test")
            session = session_manager.get_session(session_id)
            
            # Encryption key should exist but not be logged or exposed
            assert hasattr(session, 'encryption_key')
            assert len(session.encryption_key) > 20  # Should be substantial length
            
            # Key should not appear in any files
            for root, dirs, files in os.walk(temp_storage_dir):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix in ['.json', '.txt', '.log']:
                        content = file_path.read_text(errors='ignore')
                        assert session.encryption_key not in content
                        
        finally:
            shutdown_session_manager()

    def test_data_recovery_prevention(self, temp_storage_dir):
        """Test that deleted data cannot be recovered"""
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        cleanup_manager = get_cleanup_manager(base_storage_dir=temp_storage_dir)
        
        try:
            # Create session and store sensitive data
            session_id = session_manager.create_session("recovery_test")
            sensitive_data = {
                "secret": "super_secret_data_that_should_not_be_recoverable",
                "password": "this_is_a_test_password_12345"
            }
            session_manager.store_data(session_id, "secrets", sensitive_data)
            
            # Get file location
            session = session_manager.get_session(session_id)
            session_dir = session.storage_dir
            
            # Perform secure cleanup
            cleanup_result = cleanup_manager.cleanup_session(session_id, CleanupLevel.EMERGENCY)
            assert cleanup_result.status == CleanupStatus.COMPLETED
            
            # Verify directory is gone
            assert not session_dir.exists()
            
            # Scan entire storage area for sensitive strings
            for root, dirs, files in os.walk(temp_storage_dir):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        content = file_path.read_text(errors='ignore')
                        assert "super_secret_data" not in content
                        assert "test_password_12345" not in content
                    except:
                        # Binary files - read as bytes
                        content = file_path.read_bytes()
                        assert b"super_secret_data" not in content
                        assert b"test_password_12345" not in content
                        
        finally:
            shutdown_cleanup_manager()
            shutdown_session_manager()

    def test_concurrent_access_security(self, temp_storage_dir):
        """Test security under concurrent access scenarios"""
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        
        try:
            # Create sessions from different "users"
            user1_session = session_manager.create_session("user1")
            user2_session = session_manager.create_session("user2")
            
            # Store different data in each session
            user1_data = {"user": "user1", "secret": "user1_secret"}
            user2_data = {"user": "user2", "secret": "user2_secret"}
            
            session_manager.store_data(user1_session, "user_data", user1_data)
            session_manager.store_data(user2_session, "user_data", user2_data)
            
            def concurrent_access_test(session_id, expected_user):
                """Test concurrent access from specific session"""
                for _ in range(10):
                    data = session_manager.load_data(session_id, "user_data")
                    assert data is not None
                    assert data["user"] == expected_user
                    time.sleep(0.01)  # Small delay to encourage race conditions
            
            # Run concurrent access tests
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(concurrent_access_test, user1_session, "user1"),
                    executor.submit(concurrent_access_test, user2_session, "user2"),
                    executor.submit(concurrent_access_test, user1_session, "user1"),
                    executor.submit(concurrent_access_test, user2_session, "user2")
                ]
                
                # All should complete without cross-contamination
                for future in as_completed(futures):
                    future.result()  # Will raise exception if any failed
                    
        finally:
            shutdown_session_manager()


class TestComplianceValidation:
    """Tests for compliance with data protection requirements"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_data_encryption_compliance(self, temp_storage_dir):
        """Test compliance with encryption requirements"""
        storage = EncryptedJSONStorage(temp_storage_dir)
        
        # Test data
        pii_data = {
            "name": "John Doe",
            "hkid": "A123456(7)",
            "email": "john@example.com"
        }
        
        # Store encrypted data
        storage.store_json(pii_data, "pii_test", "test_password")
        
        # Verify encryption compliance
        encrypted_files = list(temp_storage_dir.glob("*.encrypted.json"))
        assert len(encrypted_files) == 1
        
        # Read and verify encryption metadata
        with open(encrypted_files[0]) as f:
            file_content = json.load(f)
        
        assert file_content["algorithm"] == "AES-256-GCM"
        assert file_content["kdf_iterations"] >= 100000  # Strong key derivation
        
        # Verify data is encrypted
        encrypted_data = file_content["encrypted_data"]
        assert "John Doe" not in encrypted_data
        assert "A123456(7)" not in encrypted_data

    def test_audit_logging_compliance(self, temp_storage_dir):
        """Test audit logging for compliance"""
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        cleanup_manager = get_cleanup_manager(base_storage_dir=temp_storage_dir)
        
        try:
            # Create session and perform operations
            session_id = session_manager.create_session("audit_user")
            session_manager.store_data(session_id, "test_data", {"test": "data"})
            
            # Perform cleanup
            cleanup_result = cleanup_manager.cleanup_session(session_id, CleanupLevel.STANDARD)
            
            # Verify audit trail exists
            assert cleanup_result.started_at is not None
            assert cleanup_result.completed_at is not None
            assert isinstance(cleanup_result.files_deleted, int)
            
        finally:
            shutdown_cleanup_manager()
            shutdown_session_manager()

    def test_data_retention_compliance(self, temp_storage_dir):
        """Test data retention and deletion compliance"""
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        cleanup_manager = get_cleanup_manager(base_storage_dir=temp_storage_dir)
        
        try:
            # Create session with data
            session_id = session_manager.create_session("retention_user")
            test_data = {"sensitive": "data", "timestamp": datetime.now().isoformat()}
            session_manager.store_data(session_id, "retention_test", test_data)
            
            # Verify data exists
            stored_data = session_manager.load_data(session_id, "retention_test")
            assert stored_data == test_data
            
            # Perform deletion
            cleanup_result = cleanup_manager.cleanup_session(session_id, CleanupLevel.THOROUGH)
            assert cleanup_result.status == CleanupStatus.COMPLETED
            
            # Verify complete deletion
            assert session_manager.get_session(session_id) is None
            assert session_manager.load_data(session_id, "retention_test") is None
            
        finally:
            shutdown_cleanup_manager()
            shutdown_session_manager()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 