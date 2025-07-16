"""
Tests for Secure Session Management Module

Tests the secure session lifecycle management, encryption key handling,
session isolation, and cleanup procedures.
"""

import pytest
import tempfile
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.utils.session_manager import (
    SecureSessionManager,
    SessionInfo,
    get_session_manager,
    shutdown_session_manager,
    create_session,
    get_session_storage,
    store_session_data,
    load_session_data,
    destroy_session
)


class TestSecureSessionManager:
    """Test cases for SecureSessionManager class"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def session_manager(self, temp_storage_dir):
        """Create session manager with temporary directory"""
        manager = SecureSessionManager(
            base_storage_dir=temp_storage_dir,
            session_timeout_minutes=5,  # Short timeout for testing
            cleanup_interval_minutes=1  # Fast cleanup for testing
        )
        yield manager
        manager.shutdown()

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return {
            "customer_info": {"id": 123, "name": "Test Customer"},
            "analysis_results": {"score": 85.5, "category": "premium"},
            "metadata": {"processed_at": "2025-07-16T15:00:00Z"}
        }

    def test_create_session(self, session_manager):
        """Test session creation"""
        user_id = "test_user"
        metadata = {"source": "test", "version": "1.0"}
        
        session_id = session_manager.create_session(user_id, metadata)
        
        # Verify session ID format
        assert isinstance(session_id, str)
        assert len(session_id) > 20  # Should be long enough for security
        
        # Verify session exists
        session = session_manager.get_session(session_id)
        assert session is not None
        assert session.session_id == session_id
        assert session.metadata == metadata
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_accessed, datetime)
        assert len(session.encryption_key) > 20  # Strong encryption key
        assert session.storage_dir.exists()

    def test_session_isolation(self, session_manager, sample_data):
        """Test that sessions are isolated from each other"""
        # Create two sessions
        session1_id = session_manager.create_session("user1")
        session2_id = session_manager.create_session("user2")
        
        # Store data in session 1
        result1 = session_manager.store_data(session1_id, "test_file", sample_data)
        assert result1 is True
        
        # Verify session 1 can load its data
        loaded_data1 = session_manager.load_data(session1_id, "test_file")
        assert loaded_data1 == sample_data
        
        # Verify session 2 cannot load session 1's data
        loaded_data2 = session_manager.load_data(session2_id, "test_file")
        assert loaded_data2 is None

    def test_session_key_uniqueness(self, session_manager):
        """Test that each session gets unique encryption keys"""
        session1_id = session_manager.create_session("user1")
        session2_id = session_manager.create_session("user2")
        
        session1 = session_manager.get_session(session1_id)
        session2 = session_manager.get_session(session2_id)
        
        assert session1.encryption_key != session2.encryption_key
        assert session1.session_id != session2.session_id
        assert session1.storage_dir != session2.storage_dir

    def test_store_and_load_data(self, session_manager, sample_data):
        """Test storing and loading data in sessions"""
        session_id = session_manager.create_session("test_user")
        
        # Store data
        result = session_manager.store_data(session_id, "customer_data", sample_data)
        assert result is True
        
        # Load data
        loaded_data = session_manager.load_data(session_id, "customer_data")
        assert loaded_data == sample_data
        
        # Verify file is tracked in session
        session = session_manager.get_session(session_id)
        assert "customer_data" in session.data_files

    def test_get_storage(self, session_manager):
        """Test getting storage instance for session"""
        session_id = session_manager.create_session("test_user")
        
        storage = session_manager.get_storage(session_id)
        assert storage is not None
        
        # Invalid session should return None
        invalid_storage = session_manager.get_storage("invalid_session")
        assert invalid_storage is None

    def test_list_session_files(self, session_manager, sample_data):
        """Test listing files in session storage"""
        session_id = session_manager.create_session("test_user")
        
        # Initially empty
        files = session_manager.list_session_files(session_id)
        assert files == []
        
        # Store multiple files
        filenames = ["file1", "file2", "file3"]
        for filename in filenames:
            session_manager.store_data(session_id, filename, sample_data)
        
        # Check list
        files = session_manager.list_session_files(session_id)
        assert len(files) == 3
        assert set(files) == set(filenames)

    def test_delete_session_file(self, session_manager, sample_data):
        """Test deleting files from session storage"""
        session_id = session_manager.create_session("test_user")
        filename = "test_delete"
        
        # Store and verify file exists
        session_manager.store_data(session_id, filename, sample_data)
        files = session_manager.list_session_files(session_id)
        assert filename in files
        
        # Delete file
        result = session_manager.delete_session_file(session_id, filename)
        assert result is True
        
        # Verify file is gone
        files = session_manager.list_session_files(session_id)
        assert filename not in files
        
        # Try to delete again
        result = session_manager.delete_session_file(session_id, filename)
        assert result is False

    def test_destroy_session(self, session_manager, sample_data):
        """Test session destruction and cleanup"""
        session_id = session_manager.create_session("test_user")
        
        # Store some data
        session_manager.store_data(session_id, "test_data", sample_data)
        
        # Verify session exists
        session = session_manager.get_session(session_id)
        assert session is not None
        storage_dir = session.storage_dir
        assert storage_dir.exists()
        
        # Destroy session
        result = session_manager.destroy_session(session_id)
        assert result is True
        
        # Verify session is gone
        session = session_manager.get_session(session_id)
        assert session is None
        
        # Verify storage directory is cleaned up
        assert not storage_dir.exists()

    def test_session_timeout(self, temp_storage_dir):
        """Test session timeout functionality"""
        # Create manager with very short timeout
        manager = SecureSessionManager(
            base_storage_dir=temp_storage_dir,
            session_timeout_minutes=0.01,  # ~0.6 seconds
            cleanup_interval_minutes=1
        )
        
        try:
            session_id = manager.create_session("test_user")
            
            # Session should exist initially
            session = manager.get_session(session_id)
            assert session is not None
            
            # Wait for timeout
            time.sleep(1)
            
            # Session should be expired and removed
            session = manager.get_session(session_id)
            assert session is None
            
        finally:
            manager.shutdown()

    def test_last_accessed_update(self, session_manager):
        """Test that last accessed time is updated"""
        session_id = session_manager.create_session("test_user")
        
        # Get initial times
        session1 = session_manager.get_session(session_id)
        initial_time = session1.last_accessed
        
        # Wait a bit and access again
        time.sleep(0.1)
        session2 = session_manager.get_session(session_id)
        updated_time = session2.last_accessed
        
        assert updated_time > initial_time

    def test_get_active_sessions(self, session_manager):
        """Test getting active sessions information"""
        # Initially empty
        active = session_manager.get_active_sessions()
        assert len(active) == 0
        
        # Create sessions
        session1_id = session_manager.create_session("user1", {"role": "admin"})
        session2_id = session_manager.create_session("user2", {"role": "user"})
        
        # Check active sessions
        active = session_manager.get_active_sessions()
        assert len(active) == 2
        assert session1_id in active
        assert session2_id in active
        
        # Verify session info
        session1_info = active[session1_id]
        assert "created_at" in session1_info
        assert "last_accessed" in session1_info
        assert session1_info["metadata"]["role"] == "admin"

    def test_cleanup_expired_sessions(self, temp_storage_dir):
        """Test cleanup of expired sessions"""
        manager = SecureSessionManager(
            base_storage_dir=temp_storage_dir,
            session_timeout_minutes=0.01,  # ~0.6 seconds
            cleanup_interval_minutes=1
        )
        
        try:
            # Create sessions
            session1_id = manager.create_session("user1")
            session2_id = manager.create_session("user2")
            
            # Verify both exist
            assert manager.get_session(session1_id) is not None
            assert manager.get_session(session2_id) is not None
            
            # Wait for expiration
            time.sleep(1)
            
            # Run cleanup
            cleaned_count = manager.cleanup_expired_sessions()
            assert cleaned_count == 2
            
            # Verify sessions are gone
            assert manager.get_session(session1_id) is None
            assert manager.get_session(session2_id) is None
            
        finally:
            manager.shutdown()

    def test_invalid_session_operations(self, session_manager, sample_data):
        """Test operations on invalid sessions"""
        invalid_session_id = "invalid_session_123"
        
        # All operations should fail gracefully
        assert session_manager.get_session(invalid_session_id) is None
        assert session_manager.get_storage(invalid_session_id) is None
        assert session_manager.store_data(invalid_session_id, "file", sample_data) is False
        assert session_manager.load_data(invalid_session_id, "file") is None
        assert session_manager.list_session_files(invalid_session_id) is None
        assert session_manager.delete_session_file(invalid_session_id, "file") is False
        assert session_manager.destroy_session(invalid_session_id) is False

    def test_context_manager(self, temp_storage_dir, sample_data):
        """Test session manager as context manager"""
        session_id = None
        
        with SecureSessionManager(base_storage_dir=temp_storage_dir) as manager:
            session_id = manager.create_session("test_user")
            manager.store_data(session_id, "test_data", sample_data)
            
            # Verify session exists
            assert manager.get_session(session_id) is not None
        
        # After context exit, manager should be shut down
        # We can't easily test this without accessing internals

    def test_thread_safety(self, session_manager, sample_data):
        """Test thread safety of session operations"""
        session_id = session_manager.create_session("test_user")
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                # Each thread stores and loads data
                filename = f"thread_{thread_id}_data"
                thread_data = {**sample_data, "thread_id": thread_id}
                
                store_result = session_manager.store_data(session_id, filename, thread_data)
                load_result = session_manager.load_data(session_id, filename)
                
                results.append((thread_id, store_result, load_result))
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
        
        # Verify no errors
        assert len(errors) == 0
        assert len(results) == 5
        
        # Verify all operations succeeded
        for thread_id, store_result, load_result in results:
            assert store_result is True
            assert load_result is not None
            assert load_result["thread_id"] == thread_id


class TestGlobalSessionManager:
    """Test global session manager functions"""

    def teardown_method(self):
        """Clean up after each test"""
        shutdown_session_manager()

    def test_get_session_manager_singleton(self):
        """Test that get_session_manager returns singleton"""
        manager1 = get_session_manager()
        manager2 = get_session_manager()
        
        assert manager1 is manager2

    def test_convenience_functions(self):
        """Test convenience functions"""
        sample_data = {"test": "data"}
        
        # Create session
        session_id = create_session("test_user")
        assert isinstance(session_id, str)
        
        # Get storage
        storage = get_session_storage(session_id)
        assert storage is not None
        
        # Store and load data
        store_result = store_session_data(session_id, "test_file", sample_data)
        assert store_result is True
        
        loaded_data = load_session_data(session_id, "test_file")
        assert loaded_data == sample_data
        
        # Destroy session
        destroy_result = destroy_session(session_id)
        assert destroy_result is True

    def test_shutdown_session_manager(self):
        """Test shutdown of global session manager"""
        # Create and use manager
        session_id = create_session("test_user")
        assert get_session_storage(session_id) is not None
        
        # Shutdown
        shutdown_session_manager()
        
        # Should create new manager on next access
        new_session_id = create_session("test_user")
        assert isinstance(new_session_id, str)


class TestSessionInfo:
    """Test SessionInfo dataclass"""

    def test_session_info_creation(self):
        """Test creating SessionInfo objects"""
        now = datetime.now()
        session_info = SessionInfo(
            session_id="test_session",
            created_at=now,
            last_accessed=now,
            encryption_key="test_key",
            storage_dir=Path("/tmp/test"),
            metadata={"user": "test"}
        )
        
        assert session_info.session_id == "test_session"
        assert session_info.created_at == now
        assert session_info.last_accessed == now
        assert session_info.encryption_key == "test_key"
        assert session_info.storage_dir == Path("/tmp/test")
        assert session_info.metadata == {"user": "test"}
        assert len(session_info.data_files) == 0

    def test_session_info_defaults(self):
        """Test SessionInfo with default values"""
        now = datetime.now()
        session_info = SessionInfo(
            session_id="test",
            created_at=now,
            last_accessed=now,
            encryption_key="key",
            storage_dir=Path("/tmp")
        )
        
        assert isinstance(session_info.data_files, set)
        assert len(session_info.data_files) == 0
        assert isinstance(session_info.metadata, dict)
        assert len(session_info.metadata) == 0


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def session_manager(self, temp_storage_dir):
        """Create session manager with temporary directory"""
        manager = SecureSessionManager(base_storage_dir=temp_storage_dir)
        yield manager
        manager.shutdown()

    def test_storage_error_handling(self, session_manager):
        """Test handling of storage errors"""
        session_id = session_manager.create_session("test_user")
        
        # Mock storage error
        with patch('src.utils.session_manager.EncryptedJSONStorage') as mock_storage_class:
            mock_storage = MagicMock()
            mock_storage.store_json.side_effect = Exception("Storage error")
            mock_storage_class.return_value = mock_storage
            
            # Should handle error gracefully
            result = session_manager.store_data(session_id, "test", {"data": "test"})
            assert result is False

    def test_cleanup_thread_error_handling(self, temp_storage_dir):
        """Test cleanup thread error handling"""
        manager = SecureSessionManager(
            base_storage_dir=temp_storage_dir,
            cleanup_interval_minutes=0.01  # Very fast for testing
        )
        
        try:
            # Let cleanup thread run briefly
            time.sleep(0.1)
            
            # Manager should still be functional
            session_id = manager.create_session("test_user")
            assert manager.get_session(session_id) is not None
            
        finally:
            manager.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 