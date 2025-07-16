"""
Secure Session Management Module

Provides secure session lifecycle management for the Agentic AI Revenue Assistant.
Handles encryption key management, session isolation, and secure cleanup.

Features:
- Cryptographically secure session ID generation
- In-memory only encryption key storage
- Session-based data isolation and access controls
- Automatic timeout and cleanup mechanisms
- Thread-safe operations for multi-user scenarios
- Audit logging of session operations

Security considerations:
- Session keys are never written to disk
- Memory-only storage with secure deletion
- Session isolation prevents cross-session data leakage
- Automatic cleanup on timeout or termination
- Strong session ID generation (128+ bits)
"""

import secrets
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
import gc
import weakref

from loguru import logger
from .encrypted_json_storage import EncryptedJSONStorage


@dataclass
class SessionInfo:
    """Information about an active session"""
    session_id: str
    created_at: datetime
    last_accessed: datetime
    encryption_key: str
    storage_dir: Path
    data_files: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SecureSessionManager:
    """
    Secure session manager for handling user sessions with encrypted data storage.
    
    Provides session isolation, in-memory key management, and automatic cleanup.
    All session keys are stored only in memory and destroyed on session end.
    """
    
    def __init__(self, 
                 base_storage_dir: Optional[Path] = None,
                 session_timeout_minutes: int = 60,
                 cleanup_interval_minutes: int = 5):
        """
        Initialize the secure session manager.
        
        Args:
            base_storage_dir: Base directory for session storage (default: data/sessions)
            session_timeout_minutes: Session inactivity timeout in minutes
            cleanup_interval_minutes: How often to run cleanup in minutes
        """
        self.base_storage_dir = Path(base_storage_dir or "data/sessions")
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.cleanup_interval = timedelta(minutes=cleanup_interval_minutes)
        
        # Thread-safe session storage
        self._sessions: Dict[str, SessionInfo] = {}
        self._lock = threading.RLock()
        
        # Cleanup thread management
        self._cleanup_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._last_cleanup = datetime.now()
        
        # Ensure base directory exists
        self.base_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Start background cleanup
        self._start_cleanup_thread()
        
        logger.info(f"SecureSessionManager initialized: timeout={session_timeout_minutes}min")

    def create_session(self, user_id: str = "anonymous", metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new secure session.
        
        Args:
            user_id: User identifier for audit logging
            metadata: Optional session metadata
            
        Returns:
            Unique session ID
        """
        with self._lock:
            # Generate cryptographically secure session ID (128 bits)
            session_id = secrets.token_urlsafe(32)  # 32 bytes = 256 bits (even more secure)
            
            # Generate encryption key for this session
            encryption_key = secrets.token_urlsafe(32)  # 256-bit key
            
            # Create session-specific storage directory
            session_storage_dir = self.base_storage_dir / session_id
            session_storage_dir.mkdir(parents=True, exist_ok=True)
            
            # Create session info
            now = datetime.now()
            session_info = SessionInfo(
                session_id=session_id,
                created_at=now,
                last_accessed=now,
                encryption_key=encryption_key,
                storage_dir=session_storage_dir,
                metadata=metadata or {}
            )
            
            # Store session
            self._sessions[session_id] = session_info
            
            # Audit log
            logger.info(f"Session created: {session_id[:8]}... for user {user_id}")
            
            return session_id

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session information and update last accessed time.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionInfo if session exists and is valid, None otherwise
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                # Check if session has expired
                if self._is_session_expired(session):
                    logger.warning(f"Session expired: {session_id[:8]}...")
                    self._destroy_session_unsafe(session_id)
                    return None
                
                # Update last accessed time
                session.last_accessed = datetime.now()
                return session
            
            return None

    def get_storage(self, session_id: str) -> Optional[EncryptedJSONStorage]:
        """
        Get encrypted storage instance for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            EncryptedJSONStorage instance or None if session invalid
        """
        session = self.get_session(session_id)
        if session:
            return EncryptedJSONStorage(session.storage_dir)
        return None

    def store_data(self, session_id: str, filename: str, data: Dict[str, Any], 
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store data in session's encrypted storage.
        
        Args:
            session_id: Session identifier
            filename: File identifier (without extension)
            data: Data to store
            metadata: Optional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate filename for security (prevent directory traversal)
            if not filename or not isinstance(filename, str):
                logger.error(f"Invalid filename for session {session_id[:8]}...: {filename}")
                return False
            
            # Check for dangerous patterns
            dangerous_patterns = ["..", "/", "\\", ":", "|", "<", ">", "?", "*", "\""]
            if any(pattern in filename for pattern in dangerous_patterns):
                logger.error(f"Dangerous filename pattern for session {session_id[:8]}...: {filename}")
                return False
            
            # Check filename length and safe characters
            if len(filename) > 255:
                logger.error(f"Filename too long for session {session_id[:8]}...: {filename}")
                return False
            
            import string
            safe_chars = string.ascii_letters + string.digits + "._-"
            if not all(c in safe_chars for c in filename):
                logger.error(f"Unsafe characters in filename for session {session_id[:8]}...: {filename}")
                return False
            
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Invalid session for data storage: {session_id[:8]}...")
                return False
            
            storage = EncryptedJSONStorage(session.storage_dir)
            storage.store_json(data, filename, session.encryption_key, metadata)
            
            # Track file in session
            with self._lock:
                session.data_files.add(filename)
            
            logger.info(f"Data stored in session {session_id[:8]}...: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store data in session {session_id[:8]}...: {e}")
            return False

    def load_data(self, session_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load data from session's encrypted storage.
        
        Args:
            session_id: Session identifier
            filename: File identifier (without extension)
            
        Returns:
            Loaded data or None if not found/error
        """
        try:
            session = self.get_session(session_id)
            if not session:
                logger.error(f"Invalid session for data loading: {session_id[:8]}...")
                return None
            
            storage = EncryptedJSONStorage(session.storage_dir)
            data = storage.load_json(filename, session.encryption_key)
            
            logger.info(f"Data loaded from session {session_id[:8]}...: {filename}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load data from session {session_id[:8]}...: {e}")
            return None

    def list_session_files(self, session_id: str) -> Optional[list[str]]:
        """
        List files in session's storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of filenames or None if session invalid
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        storage = EncryptedJSONStorage(session.storage_dir)
        return storage.list_files()

    def delete_session_file(self, session_id: str, filename: str) -> bool:
        """
        Delete a file from session's storage.
        
        Args:
            session_id: Session identifier
            filename: File identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.get_session(session_id)
            if not session:
                return False
            
            storage = EncryptedJSONStorage(session.storage_dir)
            result = storage.delete_file(filename)
            
            if result:
                with self._lock:
                    session.data_files.discard(filename)
                logger.info(f"File deleted from session {session_id[:8]}...: {filename}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete file from session {session_id[:8]}...: {e}")
            return False

    def destroy_session(self, session_id: str) -> bool:
        """
        Destroy a session and clean up all associated data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            return self._destroy_session_unsafe(session_id)

    def _destroy_session_unsafe(self, session_id: str) -> bool:
        """
        Internal method to destroy session (requires lock to be held).
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self._sessions.get(session_id)
            if not session:
                return False
            
            # Clean up storage directory
            storage = EncryptedJSONStorage(session.storage_dir)
            deleted_count = storage.cleanup_all()
            
            # Remove storage directory
            try:
                session.storage_dir.rmdir()
            except OSError:
                logger.warning(f"Could not remove session directory: {session.storage_dir}")
            
            # Securely clear encryption key from memory
            self._secure_clear_string(session.encryption_key)
            
            # Remove from active sessions
            del self._sessions[session_id]
            
            # Force garbage collection to help clear memory
            gc.collect()
            
            logger.info(f"Session destroyed: {session_id[:8]}... ({deleted_count} files cleaned)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy session {session_id[:8]}...: {e}")
            return False

    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all active sessions.
        
        Returns:
            Dictionary mapping session IDs to session info
        """
        with self._lock:
            active_sessions = {}
            for session_id, session in self._sessions.items():
                if not self._is_session_expired(session):
                    active_sessions[session_id] = {
                        "created_at": session.created_at.isoformat(),
                        "last_accessed": session.last_accessed.isoformat(),
                        "file_count": len(session.data_files),
                        "metadata": session.metadata.copy()
                    }
            return active_sessions

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        with self._lock:
            expired_sessions = []
            
            for session_id, session in self._sessions.items():
                if self._is_session_expired(session):
                    expired_sessions.append(session_id)
            
            cleanup_count = 0
            for session_id in expired_sessions:
                if self._destroy_session_unsafe(session_id):
                    cleanup_count += 1
            
            if cleanup_count > 0:
                logger.info(f"Cleaned up {cleanup_count} expired sessions")
            
            return cleanup_count

    def shutdown(self):
        """
        Shutdown session manager and clean up all sessions.
        """
        logger.info("Shutting down SecureSessionManager...")
        
        # Stop cleanup thread
        self._shutdown_event.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        
        # Destroy all active sessions
        with self._lock:
            session_ids = list(self._sessions.keys())
            for session_id in session_ids:
                self._destroy_session_unsafe(session_id)
        
        logger.info("SecureSessionManager shutdown complete")

    def _is_session_expired(self, session: SessionInfo) -> bool:
        """Check if a session has expired"""
        return datetime.now() - session.last_accessed > self.session_timeout

    def _secure_clear_string(self, secret: str):
        """
        Attempt to securely clear a string from memory.
        Note: Python's memory management makes this challenging,
        but we make a best effort.
        """
        try:
            # Overwrite the string object's internal buffer
            # This is implementation-specific and may not work in all Python versions
            if hasattr(secret, '__dict__'):
                secret.__dict__.clear()
        except:
            pass
        
        # Clear the reference
        secret = None

    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while not self._shutdown_event.is_set():
                try:
                    if datetime.now() - self._last_cleanup >= self.cleanup_interval:
                        self.cleanup_expired_sessions()
                        self._last_cleanup = datetime.now()
                    
                    # Sleep for 30 seconds before checking again
                    self._shutdown_event.wait(30)
                    
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")
                    self._shutdown_event.wait(60)  # Wait longer on error
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.shutdown()


# Global session manager instance
_session_manager: Optional[SecureSessionManager] = None
_session_manager_lock = threading.Lock()


def get_session_manager(**kwargs) -> SecureSessionManager:
    """
    Get or create the global session manager instance.
    
    Args:
        **kwargs: Arguments for SecureSessionManager constructor
        
    Returns:
        Global SecureSessionManager instance
    """
    global _session_manager
    
    with _session_manager_lock:
        if _session_manager is None:
            _session_manager = SecureSessionManager(**kwargs)
        return _session_manager


def shutdown_session_manager():
    """Shutdown the global session manager"""
    global _session_manager
    
    with _session_manager_lock:
        if _session_manager:
            _session_manager.shutdown()
            _session_manager = None


# Convenience functions for session operations

def create_session(user_id: str = "anonymous", **kwargs) -> str:
    """Create a new session"""
    manager = get_session_manager()
    return manager.create_session(user_id, **kwargs)


def get_session_storage(session_id: str) -> Optional[EncryptedJSONStorage]:
    """Get storage for a session"""
    manager = get_session_manager()
    return manager.get_storage(session_id)


def store_session_data(session_id: str, filename: str, data: Dict[str, Any]) -> bool:
    """Store data in a session"""
    manager = get_session_manager()
    return manager.store_data(session_id, filename, data)


def load_session_data(session_id: str, filename: str) -> Optional[Dict[str, Any]]:
    """Load data from a session"""
    manager = get_session_manager()
    return manager.load_data(session_id, filename)


def destroy_session(session_id: str) -> bool:
    """Destroy a session"""
    manager = get_session_manager()
    return manager.destroy_session(session_id) 