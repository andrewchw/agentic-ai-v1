"""
Tests for Data Cleanup Procedures Module

Tests the comprehensive data cleanup procedures for secure session termination.
Validates integration with session management, encrypted storage, and secure file operations.
"""

import pytest
import tempfile
import time
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.utils.data_cleanup import (
    DataCleanupManager,
    CleanupLevel,
    CleanupStatus,
    CleanupResult,
    get_cleanup_manager,
    shutdown_cleanup_manager,
    cleanup_session,
    emergency_cleanup,
    schedule_cleanup
)
from src.utils.session_manager import get_session_manager, shutdown_session_manager
from src.utils.encrypted_json_storage import EncryptedJSONStorage


class TestDataCleanupManager:
    """Test cases for DataCleanupManager class"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def cleanup_manager(self, temp_storage_dir):
        """Create cleanup manager with temporary directory"""
        manager = DataCleanupManager(
            base_storage_dir=temp_storage_dir,
            default_cleanup_level=CleanupLevel.STANDARD,
            enable_automatic_cleanup=True
        )
        yield manager
        manager.shutdown()

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return {
            "customer_data": {"id": 123, "name": "Test Customer"},
            "analysis_results": {"score": 85.5, "category": "premium"}
        }

    @pytest.fixture
    def session_with_data(self, temp_storage_dir, sample_data):
        """Create session with data for testing cleanup"""
        # Get session manager
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        
        # Create session and store data
        session_id = session_manager.create_session("test_user")
        session_manager.store_data(session_id, "test_file", sample_data)
        
        yield session_id
        
        # Cleanup
        try:
            session_manager.destroy_session(session_id)
        except:
            pass
        shutdown_session_manager()

    def test_init_cleanup_manager(self, temp_storage_dir):
        """Test cleanup manager initialization"""
        manager = DataCleanupManager(
            base_storage_dir=temp_storage_dir,
            default_cleanup_level=CleanupLevel.THOROUGH,
            enable_automatic_cleanup=False
        )
        
        assert manager.base_storage_dir == temp_storage_dir
        assert manager.default_cleanup_level == CleanupLevel.THOROUGH
        assert manager.enable_automatic_cleanup is False

    def test_cleanup_session_basic(self, cleanup_manager, session_with_data):
        """Test basic session cleanup"""
        session_id = session_with_data
        
        result = cleanup_manager.cleanup_session(session_id, CleanupLevel.STANDARD)
        
        assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]
        assert result.level == CleanupLevel.STANDARD
        assert result.session_id == session_id
        assert isinstance(result.started_at, datetime)
        assert result.completed_at is not None

    def test_cleanup_session_minimal(self, cleanup_manager, session_with_data):
        """Test minimal session cleanup"""
        session_id = session_with_data
        
        result = cleanup_manager.cleanup_session(session_id, CleanupLevel.MINIMAL)
        
        assert result.level == CleanupLevel.MINIMAL
        assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]

    def test_cleanup_session_thorough(self, cleanup_manager, session_with_data):
        """Test thorough session cleanup with verification"""
        session_id = session_with_data
        
        result = cleanup_manager.cleanup_session(session_id, CleanupLevel.THOROUGH)
        
        assert result.level == CleanupLevel.THOROUGH
        assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]
        assert result.memory_cleared is True

    def test_cleanup_session_emergency(self, cleanup_manager, session_with_data):
        """Test emergency session cleanup"""
        session_id = session_with_data
        
        result = cleanup_manager.cleanup_session(session_id, CleanupLevel.EMERGENCY)
        
        assert result.level == CleanupLevel.EMERGENCY
        assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]
        assert result.memory_cleared is True

    def test_cleanup_nonexistent_session(self, cleanup_manager):
        """Test cleanup of non-existent session"""
        result = cleanup_manager.cleanup_session("nonexistent_session", CleanupLevel.STANDARD)
        
        assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]
        assert len(result.warnings) > 0

    def test_cleanup_concurrent_protection(self, cleanup_manager, session_with_data):
        """Test protection against concurrent cleanup of same session"""
        session_id = session_with_data
        
        # Mock long-running cleanup
        with patch.object(cleanup_manager, '_cleanup_session_data') as mock_cleanup:
            mock_cleanup.side_effect = lambda *args: time.sleep(0.1)  # Simulate delay
            
            # Start first cleanup in thread
            def start_cleanup():
                cleanup_manager.cleanup_session(session_id)
            
            thread = threading.Thread(target=start_cleanup)
            thread.start()
            
            # Try to start second cleanup immediately
            time.sleep(0.05)  # Let first cleanup start
            result = cleanup_manager.cleanup_session(session_id)
            
            thread.join()
            
            # Second cleanup should fail due to concurrent protection
            assert result.status == CleanupStatus.FAILED
            assert "already in progress" in str(result.errors)

    def test_cleanup_force_override(self, cleanup_manager, session_with_data):
        """Test force cleanup overrides concurrent protection"""
        session_id = session_with_data
        
        # Start cleanup and immediately force another
        with patch.object(cleanup_manager, '_cleanup_session_data') as mock_cleanup:
            mock_cleanup.side_effect = lambda *args: time.sleep(0.1)
            
            def start_cleanup():
                cleanup_manager.cleanup_session(session_id)
            
            thread = threading.Thread(target=start_cleanup)
            thread.start()
            
            time.sleep(0.05)
            result = cleanup_manager.cleanup_session(session_id, force=True)
            
            thread.join()
            
            # Force cleanup should succeed
            assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL, CleanupStatus.IN_PROGRESS]

    def test_cleanup_all_sessions(self, cleanup_manager, temp_storage_dir, sample_data):
        """Test cleanup of all active sessions"""
        # Create multiple sessions
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        session_ids = []
        
        for i in range(3):
            session_id = session_manager.create_session(f"user_{i}")
            session_manager.store_data(session_id, f"file_{i}", sample_data)
            session_ids.append(session_id)
        
        # Cleanup all sessions
        results = cleanup_manager.cleanup_all_sessions(CleanupLevel.STANDARD)
        
        assert len(results) == 3
        for result in results:
            assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]
            assert result.session_id in session_ids

    def test_emergency_cleanup(self, cleanup_manager, temp_storage_dir, sample_data):
        """Test emergency cleanup procedure"""
        # Create sessions and data
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        
        for i in range(2):
            session_id = session_manager.create_session(f"user_{i}")
            session_manager.store_data(session_id, f"file_{i}", sample_data)
        
        # Perform emergency cleanup
        result = cleanup_manager.emergency_cleanup()
        
        assert result.level == CleanupLevel.EMERGENCY
        assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]
        assert result.memory_cleared is True
        assert result.session_id is None  # Emergency cleanup doesn't target specific session

    def test_register_cleanup_callback(self, cleanup_manager, session_with_data):
        """Test registering and calling cleanup callbacks"""
        callback_called = []
        
        def test_callback(result: CleanupResult):
            callback_called.append(result)
        
        cleanup_manager.register_cleanup_callback(test_callback)
        
        # Perform cleanup
        session_id = session_with_data
        cleanup_manager.cleanup_session(session_id)
        
        # Verify callback was called
        assert len(callback_called) == 1
        assert callback_called[0].session_id == session_id

    def test_register_emergency_procedure(self, cleanup_manager):
        """Test registering and executing emergency procedures"""
        procedure_called = []
        
        def test_procedure():
            procedure_called.append("called")
        
        cleanup_manager.register_emergency_procedure(test_procedure)
        
        # Perform emergency cleanup
        cleanup_manager.emergency_cleanup()
        
        # Verify procedure was called
        assert len(procedure_called) == 1

    def test_get_cleanup_status(self, cleanup_manager, session_with_data):
        """Test getting cleanup status during operation"""
        session_id = session_with_data
        
        # No cleanup initially
        status = cleanup_manager.get_cleanup_status(session_id)
        assert status is None
        
        # Mock long-running cleanup to check status
        with patch.object(cleanup_manager, '_cleanup_session_data') as mock_cleanup:
            mock_cleanup.side_effect = lambda *args: time.sleep(0.1)
            
            def start_cleanup():
                cleanup_manager.cleanup_session(session_id)
            
            thread = threading.Thread(target=start_cleanup)
            thread.start()
            
            # Check status during cleanup
            time.sleep(0.05)
            status = cleanup_manager.get_cleanup_status(session_id)
            
            thread.join()
            
            assert status is not None
            assert status.session_id == session_id

    def test_get_active_cleanups(self, cleanup_manager, session_with_data):
        """Test getting all active cleanups"""
        session_id = session_with_data
        
        # No active cleanups initially
        active = cleanup_manager.get_active_cleanups()
        assert len(active) == 0
        
        # Mock cleanup to check active status
        with patch.object(cleanup_manager, '_cleanup_session_data') as mock_cleanup:
            mock_cleanup.side_effect = lambda *args: time.sleep(0.1)
            
            def start_cleanup():
                cleanup_manager.cleanup_session(session_id)
            
            thread = threading.Thread(target=start_cleanup)
            thread.start()
            
            time.sleep(0.05)
            active = cleanup_manager.get_active_cleanups()
            
            thread.join()
            
            assert len(active) >= 1
            assert session_id in active

    def test_schedule_automatic_cleanup(self, cleanup_manager, session_with_data):
        """Test scheduling automatic cleanup"""
        session_id = session_with_data
        
        # Schedule cleanup with short delay
        cleanup_manager.schedule_automatic_cleanup(session_id, delay_seconds=0.1)
        
        # Wait for cleanup to complete
        time.sleep(0.5)
        
        # Session should be cleaned up
        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)
        assert session is None  # Session should be gone

    def test_automatic_cleanup_disabled(self, temp_storage_dir, session_with_data):
        """Test behavior when automatic cleanup is disabled"""
        manager = DataCleanupManager(
            base_storage_dir=temp_storage_dir,
            enable_automatic_cleanup=False
        )
        
        session_id = session_with_data
        
        # Schedule cleanup (should be ignored)
        manager.schedule_automatic_cleanup(session_id, delay_seconds=0.1)
        
        # Wait and verify session still exists
        time.sleep(0.2)
        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)
        assert session is not None  # Session should still exist

    def test_get_system_memory_info(self, cleanup_manager):
        """Test getting system memory information"""
        memory_info = cleanup_manager.get_system_memory_info()
        
        if memory_info:  # May fail on some systems
            assert "total" in memory_info
            assert "available" in memory_info
            assert "percent" in memory_info
            assert isinstance(memory_info["total"], int)

    def test_get_storage_usage(self, cleanup_manager, temp_storage_dir, sample_data):
        """Test getting storage usage information"""
        # Create some test data
        storage = EncryptedJSONStorage(temp_storage_dir / "test_storage")
        storage.store_json(sample_data, "test_file", "password")
        
        usage_info = cleanup_manager.get_storage_usage()
        
        assert "total_bytes" in usage_info
        assert "file_count" in usage_info
        assert "base_directory" in usage_info

    def test_cleanup_verification(self, cleanup_manager, session_with_data):
        """Test cleanup verification procedures"""
        session_id = session_with_data
        
        # Perform cleanup with verification
        result = cleanup_manager.cleanup_session(session_id, CleanupLevel.THOROUGH)
        
        # Verification should be performed for thorough cleanup
        assert hasattr(result, 'verification_passed')
        
        # Session should not exist after cleanup
        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)
        assert session is None

    def test_error_handling_during_cleanup(self, cleanup_manager, session_with_data):
        """Test error handling during cleanup operations"""
        session_id = session_with_data
        
        # Mock error in session cleanup
        with patch.object(cleanup_manager, '_cleanup_session_data') as mock_cleanup:
            mock_cleanup.side_effect = Exception("Simulated error")
            
            result = cleanup_manager.cleanup_session(session_id)
            
            assert result.status == CleanupStatus.FAILED
            assert len(result.errors) > 0
            assert "Simulated error" in str(result.errors)

    def test_callback_error_handling(self, cleanup_manager, session_with_data):
        """Test error handling in cleanup callbacks"""
        def failing_callback(result):
            raise Exception("Callback error")
        
        cleanup_manager.register_cleanup_callback(failing_callback)
        
        session_id = session_with_data
        
        # Cleanup should complete despite callback error
        result = cleanup_manager.cleanup_session(session_id)
        assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]

    def test_shutdown_cleanup_manager(self, cleanup_manager, temp_storage_dir, sample_data):
        """Test cleanup manager shutdown procedure"""
        # Create sessions
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        
        for i in range(2):
            session_id = session_manager.create_session(f"user_{i}")
            session_manager.store_data(session_id, f"file_{i}", sample_data)
        
        # Shutdown should clean up active sessions
        cleanup_manager.shutdown()
        
        # Sessions should be cleaned up
        active_sessions = session_manager.get_active_sessions()
        assert len(active_sessions) == 0


class TestGlobalCleanupManager:
    """Test global cleanup manager functions"""

    def teardown_method(self):
        """Clean up after each test"""
        shutdown_cleanup_manager()
        shutdown_session_manager()

    def test_get_cleanup_manager_singleton(self):
        """Test that get_cleanup_manager returns singleton"""
        manager1 = get_cleanup_manager()
        manager2 = get_cleanup_manager()
        
        assert manager1 is manager2

    def test_convenience_functions(self):
        """Test convenience functions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create session with data
            session_manager = get_session_manager(base_storage_dir=Path(temp_dir) / "sessions")
            session_id = session_manager.create_session("test_user")
            session_manager.store_data(session_id, "test_file", {"test": "data"})
            
            # Use convenience function
            result = cleanup_session(session_id, CleanupLevel.STANDARD)
            assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]
            
            # Test emergency cleanup
            emergency_result = emergency_cleanup()
            assert emergency_result.level == CleanupLevel.EMERGENCY

    def test_schedule_cleanup_convenience(self):
        """Test schedule cleanup convenience function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            session_manager = get_session_manager(base_storage_dir=Path(temp_dir) / "sessions")
            session_id = session_manager.create_session("test_user")
            
            # Schedule cleanup
            schedule_cleanup(session_id, delay_seconds=0.1)
            
            # Wait for cleanup
            time.sleep(0.2)
            
            # Session should be gone
            session = session_manager.get_session(session_id)
            assert session is None


class TestCleanupResult:
    """Test CleanupResult dataclass"""

    def test_cleanup_result_creation(self):
        """Test creating CleanupResult objects"""
        started = datetime.now()
        result = CleanupResult(
            status=CleanupStatus.COMPLETED,
            level=CleanupLevel.STANDARD,
            session_id="test_session",
            started_at=started,
            files_deleted=5,
            bytes_cleaned=1024,
            memory_cleared=True
        )
        
        assert result.status == CleanupStatus.COMPLETED
        assert result.level == CleanupLevel.STANDARD
        assert result.session_id == "test_session"
        assert result.started_at == started
        assert result.files_deleted == 5
        assert result.bytes_cleaned == 1024
        assert result.memory_cleared is True

    def test_cleanup_result_defaults(self):
        """Test CleanupResult with default values"""
        result = CleanupResult(
            status=CleanupStatus.PENDING,
            level=CleanupLevel.MINIMAL,
            session_id="test",
            started_at=datetime.now()
        )
        
        assert result.completed_at is None
        assert result.files_deleted == 0
        assert result.bytes_cleaned == 0
        assert result.memory_cleared is False
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.verification_passed is False


class TestCleanupLevels:
    """Test different cleanup levels"""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory for tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_all_cleanup_levels(self, temp_storage_dir):
        """Test all cleanup levels work correctly"""
        cleanup_manager = DataCleanupManager(base_storage_dir=temp_storage_dir)
        
        # Create session
        session_manager = get_session_manager(base_storage_dir=temp_storage_dir / "sessions")
        session_id = session_manager.create_session("test_user")
        session_manager.store_data(session_id, "test_file", {"test": "data"})
        
        # Test each cleanup level
        for level in CleanupLevel:
            # Recreate session for each test
            new_session_id = session_manager.create_session(f"test_user_{level.value}")
            session_manager.store_data(new_session_id, "test_file", {"test": "data"})
            
            result = cleanup_manager.cleanup_session(new_session_id, level)
            assert result.level == level
            assert result.status in [CleanupStatus.COMPLETED, CleanupStatus.PARTIAL]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 