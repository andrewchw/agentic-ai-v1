"""
Data Cleanup Procedures Module

Provides comprehensive data cleanup procedures for secure session termination.
Integrates with session management, encrypted storage, and secure file operations.

Features:
- Multi-layered cleanup approach (memory, files, session data)
- Automatic and manual cleanup triggers
- Secure memory clearing procedures
- Comprehensive audit logging and verification
- Emergency cleanup procedures for security incidents
- Thread-safe operations for concurrent scenarios
- Integration with all secure storage components

Security considerations:
- Complete memory clearing of sensitive data
- Secure file deletion with overwrite operations
- Session data isolation during cleanup
- Verification of cleanup completeness
- Audit logging of all operations
- Emergency procedures for immediate data purging
"""

import gc
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import psutil
import weakref

from loguru import logger
from .session_manager import get_session_manager, SecureSessionManager
from .encrypted_json_storage import EncryptedJSONStorage
from .secure_file_operations import SecureFileOperations


class CleanupLevel(Enum):
    """Levels of cleanup intensity"""
    MINIMAL = "minimal"          # Basic session cleanup
    STANDARD = "standard"        # Standard secure cleanup
    THOROUGH = "thorough"        # Comprehensive cleanup with verification
    EMERGENCY = "emergency"      # Immediate complete data purging


class CleanupStatus(Enum):
    """Status of cleanup operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class CleanupResult:
    """Result of cleanup operation"""
    status: CleanupStatus
    level: CleanupLevel
    session_id: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime] = None
    files_deleted: int = 0
    bytes_cleaned: int = 0
    memory_cleared: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    verification_passed: bool = False


class DataCleanupManager:
    """
    Comprehensive data cleanup manager for secure session termination.
    
    Provides multi-layered cleanup procedures with integration across all
    secure storage components and comprehensive audit logging.
    """
    
    def __init__(self, 
                 base_storage_dir: Optional[Path] = None,
                 default_cleanup_level: CleanupLevel = CleanupLevel.STANDARD,
                 enable_automatic_cleanup: bool = True):
        """
        Initialize data cleanup manager.
        
        Args:
            base_storage_dir: Base directory for storage operations
            default_cleanup_level: Default level of cleanup intensity
            enable_automatic_cleanup: Enable automatic cleanup on session end
        """
        self.base_storage_dir = Path(base_storage_dir or "data")
        self.default_cleanup_level = default_cleanup_level
        self.enable_automatic_cleanup = enable_automatic_cleanup
        
        # Thread safety
        self._lock = threading.RLock()
        self._active_cleanups: Dict[str, CleanupResult] = {}
        
        # Cleanup callbacks
        self._cleanup_callbacks: List[Callable[[CleanupResult], None]] = []
        
        # Emergency procedures
        self._emergency_procedures: List[Callable[[], None]] = []
        
        logger.info(f"DataCleanupManager initialized: level={default_cleanup_level.value}")

    def register_cleanup_callback(self, callback: Callable[[CleanupResult], None]):
        """Register callback to be called after cleanup operations"""
        self._cleanup_callbacks.append(callback)
        logger.debug(f"Cleanup callback registered: {callback.__name__}")

    def register_emergency_procedure(self, procedure: Callable[[], None]):
        """Register emergency procedure for security incidents"""
        self._emergency_procedures.append(procedure)
        logger.debug(f"Emergency procedure registered: {procedure.__name__}")

    def cleanup_session(self, 
                       session_id: str, 
                       level: Optional[CleanupLevel] = None,
                       force: bool = False) -> CleanupResult:
        """
        Perform comprehensive cleanup of a specific session.
        
        Args:
            session_id: Session identifier to clean up
            level: Cleanup intensity level (uses default if None)
            force: Force cleanup even if session is active
            
        Returns:
            CleanupResult with operation details
        """
        level = level or self.default_cleanup_level
        result = CleanupResult(
            status=CleanupStatus.PENDING,
            level=level,
            session_id=session_id,
            started_at=datetime.now()
        )
        
        with self._lock:
            if session_id in self._active_cleanups and not force:
                logger.warning(f"Cleanup already in progress for session {session_id}")
                result.status = CleanupStatus.FAILED
                result.errors.append("Cleanup already in progress")
                return result
            
            self._active_cleanups[session_id] = result
        
        try:
            result.status = CleanupStatus.IN_PROGRESS
            logger.info(f"Starting cleanup for session {session_id} (level: {level.value})")
            
            # Get session manager
            session_manager = get_session_manager()
            
            # Phase 1: Session data cleanup
            self._cleanup_session_data(session_id, session_manager, result)
            
            # Phase 2: File system cleanup
            self._cleanup_session_files(session_id, result, level)
            
            # Phase 3: Memory cleanup
            if level in [CleanupLevel.THOROUGH, CleanupLevel.EMERGENCY]:
                self._cleanup_memory(result)
            
            # Phase 4: Verification
            if level in [CleanupLevel.STANDARD, CleanupLevel.THOROUGH, CleanupLevel.EMERGENCY]:
                self._verify_cleanup(session_id, result)
            
            # Mark completion
            result.completed_at = datetime.now()
            result.status = CleanupStatus.COMPLETED if not result.errors else CleanupStatus.PARTIAL
            
            logger.info(f"Cleanup completed for session {session_id}: {result.status.value}")
            
        except Exception as e:
            result.status = CleanupStatus.FAILED
            result.errors.append(f"Cleanup failed: {str(e)}")
            logger.error(f"Cleanup failed for session {session_id}: {e}")
        
        finally:
            with self._lock:
                self._active_cleanups.pop(session_id, None)
            
            # Call registered callbacks
            for callback in self._cleanup_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    logger.error(f"Cleanup callback failed: {e}")
        
        return result

    def _cleanup_session_data(self, 
                             session_id: str, 
                             session_manager: SecureSessionManager, 
                             result: CleanupResult):
        """Clean up session data from session manager"""
        try:
            # Get session info before destruction
            session = session_manager.get_session(session_id)
            if session:
                result.files_deleted += len(session.data_files)
                
                # Destroy session (includes secure key clearing)
                if session_manager.destroy_session(session_id):
                    logger.debug(f"Session data cleaned: {session_id}")
                else:
                    result.warnings.append("Session destruction may have been incomplete")
            else:
                result.warnings.append("Session not found in session manager")
                
        except Exception as e:
            result.errors.append(f"Session data cleanup failed: {str(e)}")
            logger.error(f"Session data cleanup failed for {session_id}: {e}")

    def _cleanup_session_files(self, 
                              session_id: str, 
                              result: CleanupResult, 
                              level: CleanupLevel):
        """Clean up session files from file system"""
        try:
            session_dir = self.base_storage_dir / "sessions" / session_id
            
            if not session_dir.exists():
                logger.debug(f"Session directory not found: {session_dir}")
                return
            
            # Determine overwrite passes based on cleanup level
            overwrite_passes = {
                CleanupLevel.MINIMAL: 0,
                CleanupLevel.STANDARD: 1,
                CleanupLevel.THOROUGH: 3,
                CleanupLevel.EMERGENCY: 5
            }.get(level, 1)
            
            # Use secure file operations for cleanup
            file_ops = SecureFileOperations(session_dir.parent)
            cleanup_result = file_ops.cleanup_directory(session_id, overwrite_passes=overwrite_passes)
            
            if cleanup_result.success:
                result.bytes_cleaned += cleanup_result.bytes_processed or 0
                
                # Remove session directory
                try:
                    session_dir.rmdir()
                    logger.debug(f"Session directory removed: {session_dir}")
                except OSError as e:
                    result.warnings.append(f"Could not remove session directory: {e}")
            else:
                result.errors.append(f"File cleanup failed: {cleanup_result.message}")
                
        except Exception as e:
            result.errors.append(f"File cleanup failed: {str(e)}")
            logger.error(f"File cleanup failed for {session_id}: {e}")

    def _cleanup_memory(self, result: CleanupResult):
        """Perform aggressive memory cleanup"""
        try:
            # Force garbage collection multiple times
            for _ in range(3):
                gc.collect()
            
            # Clear module-level caches if possible
            try:
                # Clear various Python caches
                import sys
                if hasattr(sys, '_clear_type_cache'):
                    sys._clear_type_cache()
            except:
                pass
            
            result.memory_cleared = True
            logger.debug("Memory cleanup completed")
            
        except Exception as e:
            result.errors.append(f"Memory cleanup failed: {str(e)}")
            logger.error(f"Memory cleanup failed: {e}")

    def _verify_cleanup(self, session_id: str, result: CleanupResult):
        """Verify that cleanup was successful"""
        try:
            verification_passed = True
            
            # Check session manager
            session_manager = get_session_manager()
            if session_manager.get_session(session_id) is not None:
                result.errors.append("Session still exists in session manager")
                verification_passed = False
            
            # Check file system
            session_dir = self.base_storage_dir / "sessions" / session_id
            if session_dir.exists():
                result.errors.append("Session directory still exists")
                verification_passed = False
            
            # Check for any remaining encrypted files
            encrypted_storage_dir = self.base_storage_dir / "encrypted_storage"
            if encrypted_storage_dir.exists():
                session_files = list(encrypted_storage_dir.glob(f"*{session_id}*"))
                if session_files:
                    result.warnings.append(f"Found {len(session_files)} potential session files")
            
            result.verification_passed = verification_passed
            
            if verification_passed:
                logger.debug(f"Cleanup verification passed for session {session_id}")
            else:
                logger.warning(f"Cleanup verification failed for session {session_id}")
                
        except Exception as e:
            result.errors.append(f"Cleanup verification failed: {str(e)}")
            logger.error(f"Cleanup verification failed for {session_id}: {e}")

    def cleanup_all_sessions(self, level: Optional[CleanupLevel] = None) -> List[CleanupResult]:
        """
        Clean up all active sessions.
        
        Args:
            level: Cleanup intensity level
            
        Returns:
            List of CleanupResult for each session
        """
        level = level or self.default_cleanup_level
        results = []
        
        try:
            session_manager = get_session_manager()
            active_sessions = session_manager.get_active_sessions()
            
            logger.info(f"Cleaning up {len(active_sessions)} active sessions (level: {level.value})")
            
            for session_id in active_sessions.keys():
                result = self.cleanup_session(session_id, level)
                results.append(result)
            
        except Exception as e:
            logger.error(f"Failed to cleanup all sessions: {e}")
        
        return results

    def emergency_cleanup(self) -> CleanupResult:
        """
        Perform emergency cleanup of all data.
        
        Returns:
            CleanupResult with emergency cleanup details
        """
        result = CleanupResult(
            status=CleanupStatus.PENDING,
            level=CleanupLevel.EMERGENCY,
            session_id=None,
            started_at=datetime.now()
        )
        
        try:
            result.status = CleanupStatus.IN_PROGRESS
            logger.critical("EMERGENCY CLEANUP INITIATED")
            
            # Phase 1: Execute registered emergency procedures
            for procedure in self._emergency_procedures:
                try:
                    procedure()
                except Exception as e:
                    result.errors.append(f"Emergency procedure failed: {str(e)}")
            
            # Phase 2: Clean up all sessions
            session_results = self.cleanup_all_sessions(CleanupLevel.EMERGENCY)
            for session_result in session_results:
                result.files_deleted += session_result.files_deleted
                result.bytes_cleaned += session_result.bytes_cleaned
                result.errors.extend(session_result.errors)
            
            # Phase 3: Clean up base storage directories
            self._emergency_cleanup_storage(result)
            
            # Phase 4: Aggressive memory cleanup
            self._cleanup_memory(result)
            
            result.completed_at = datetime.now()
            result.status = CleanupStatus.COMPLETED if not result.errors else CleanupStatus.PARTIAL
            
            logger.critical(f"EMERGENCY CLEANUP COMPLETED: {result.status.value}")
            
        except Exception as e:
            result.status = CleanupStatus.FAILED
            result.errors.append(f"Emergency cleanup failed: {str(e)}")
            logger.critical(f"EMERGENCY CLEANUP FAILED: {e}")
        
        return result

    def _emergency_cleanup_storage(self, result: CleanupResult):
        """Emergency cleanup of all storage directories"""
        try:
            storage_dirs = [
                self.base_storage_dir / "sessions",
                self.base_storage_dir / "encrypted_storage",
                self.base_storage_dir / "pipeline_storage"
            ]
            
            for storage_dir in storage_dirs:
                if storage_dir.exists():
                    file_ops = SecureFileOperations(storage_dir.parent)
                    cleanup_result = file_ops.cleanup_directory(
                        storage_dir.name, 
                        overwrite_passes=5  # Maximum security
                    )
                    
                    if cleanup_result.success:
                        result.bytes_cleaned += cleanup_result.bytes_processed or 0
                        
                        # Remove directory
                        try:
                            storage_dir.rmdir()
                        except OSError:
                            pass  # Directory may not be empty
                    else:
                        result.errors.append(f"Emergency storage cleanup failed: {cleanup_result.message}")
                        
        except Exception as e:
            result.errors.append(f"Emergency storage cleanup failed: {str(e)}")

    def get_cleanup_status(self, session_id: str) -> Optional[CleanupResult]:
        """Get status of ongoing cleanup operation"""
        with self._lock:
            return self._active_cleanups.get(session_id)

    def get_active_cleanups(self) -> Dict[str, CleanupResult]:
        """Get all active cleanup operations"""
        with self._lock:
            return self._active_cleanups.copy()

    def schedule_automatic_cleanup(self, session_id: str, delay_seconds: int = 0):
        """
        Schedule automatic cleanup for a session.
        
        Args:
            session_id: Session to clean up
            delay_seconds: Delay before cleanup (0 for immediate)
        """
        if not self.enable_automatic_cleanup:
            return
        
        def delayed_cleanup():
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            self.cleanup_session(session_id)
        
        cleanup_thread = threading.Thread(target=delayed_cleanup, daemon=True)
        cleanup_thread.start()
        
        logger.debug(f"Automatic cleanup scheduled for session {session_id} (delay: {delay_seconds}s)")

    def get_system_memory_info(self) -> Dict[str, Any]:
        """Get system memory information for monitoring"""
        try:
            memory = psutil.virtual_memory()
            return {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            }
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return {}

    def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage information"""
        try:
            usage_info = {}
            
            if self.base_storage_dir.exists():
                total_size = 0
                file_count = 0
                
                for root, dirs, files in os.walk(self.base_storage_dir):
                    for file in files:
                        file_path = Path(root) / file
                        try:
                            total_size += file_path.stat().st_size
                            file_count += 1
                        except:
                            pass
                
                usage_info = {
                    "total_bytes": total_size,
                    "file_count": file_count,
                    "base_directory": str(self.base_storage_dir)
                }
            
            return usage_info
            
        except Exception as e:
            logger.error(f"Failed to get storage usage: {e}")
            return {}

    def shutdown(self):
        """Shutdown cleanup manager and perform final cleanup"""
        logger.info("Shutting down DataCleanupManager...")
        
        # Clean up all active sessions
        if self.enable_automatic_cleanup:
            results = self.cleanup_all_sessions(CleanupLevel.STANDARD)
            successful_cleanups = sum(1 for r in results if r.status == CleanupStatus.COMPLETED)
            logger.info(f"Final cleanup: {successful_cleanups}/{len(results)} sessions cleaned")


# Global cleanup manager instance
_cleanup_manager: Optional[DataCleanupManager] = None
_cleanup_manager_lock = threading.Lock()


def get_cleanup_manager(**kwargs) -> DataCleanupManager:
    """Get or create the global cleanup manager instance"""
    global _cleanup_manager
    
    with _cleanup_manager_lock:
        if _cleanup_manager is None:
            _cleanup_manager = DataCleanupManager(**kwargs)
        return _cleanup_manager


def shutdown_cleanup_manager():
    """Shutdown the global cleanup manager"""
    global _cleanup_manager
    
    with _cleanup_manager_lock:
        if _cleanup_manager:
            _cleanup_manager.shutdown()
            _cleanup_manager = None


# Convenience functions for cleanup operations

def cleanup_session(session_id: str, level: Optional[CleanupLevel] = None) -> CleanupResult:
    """Convenience function to clean up a session"""
    manager = get_cleanup_manager()
    return manager.cleanup_session(session_id, level)


def emergency_cleanup() -> CleanupResult:
    """Convenience function for emergency cleanup"""
    manager = get_cleanup_manager()
    return manager.emergency_cleanup()


def schedule_cleanup(session_id: str, delay_seconds: int = 0):
    """Convenience function to schedule automatic cleanup"""
    manager = get_cleanup_manager()
    manager.schedule_automatic_cleanup(session_id, delay_seconds) 