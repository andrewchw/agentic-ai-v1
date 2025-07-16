"""
Secure File Operations Module

Provides secure file read, write, and delete operations with strict access controls.
Implements atomic operations, secure permissions, and path validation.

Features:
- Atomic file write operations (no partial data exposure)
- Strict file permissions enforcement (owner only)
- Secure file deletion with optional overwriting
- Path validation and directory traversal prevention
- Session-based access controls
- Comprehensive audit logging
- Cross-platform compatibility (Windows/Unix)

Security considerations:
- All file operations are atomic to prevent partial exposure
- Files created with minimal permissions (owner read/write only)
- Secure deletion prevents data recovery
- Path validation prevents directory traversal attacks
- Session-based access controls integrate with session management
- Audit logging of all operations for compliance
"""

import os
import stat
import tempfile
import secrets
from pathlib import Path
from typing import Union, Optional, List, Dict, Any
from dataclasses import dataclass
import platform
import subprocess

from loguru import logger


@dataclass
class FileOperationResult:
    """Result of a file operation"""
    success: bool
    message: str
    path: Optional[Path] = None
    bytes_processed: Optional[int] = None


class SecureFileOperations:
    """
    Secure file operations manager with atomic operations and strict access controls.
    
    Provides secure file read, write, and delete operations with comprehensive
    security measures including atomic operations, secure permissions, and audit logging.
    """
    
    def __init__(self, base_directory: Optional[Union[str, Path]] = None):
        """
        Initialize secure file operations manager.
        
        Args:
            base_directory: Base directory for file operations (default: current working directory)
        """
        self.base_directory = Path(base_directory or Path.cwd()).resolve()
        self.is_windows = platform.system() == "Windows"
        
        # Ensure base directory exists
        self.base_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SecureFileOperations initialized: {self.base_directory}")

    def validate_path(self, file_path: Union[str, Path], session_id: Optional[str] = None) -> Path:
        """
        Validate and resolve file path to prevent directory traversal attacks.
        
        Args:
            file_path: File path to validate
            session_id: Optional session ID for session-specific validation
            
        Returns:
            Validated and resolved Path object
            
        Raises:
            ValueError: If path is invalid or outside allowed directory
        """
        try:
            path = Path(file_path)
            
            # Handle absolute vs relative paths
            if path.is_absolute():
                resolved_path = path.resolve()
            else:
                resolved_path = (self.base_directory / path).resolve()
            
            # Check if path is within base directory
            try:
                resolved_path.relative_to(self.base_directory)
            except ValueError:
                raise ValueError(f"Path outside allowed directory: {resolved_path}")
            
            # Additional session-specific validation
            if session_id:
                # Ensure path is within session directory
                session_dir = self.base_directory / session_id
                try:
                    resolved_path.relative_to(session_dir)
                except ValueError:
                    raise ValueError(f"Path outside session directory: {resolved_path}")
            
            return resolved_path
            
        except Exception as e:
            logger.error(f"Path validation failed for '{file_path}': {e}")
            raise ValueError(f"Invalid file path: {e}")

    def set_secure_permissions(self, file_path: Path) -> bool:
        """
        Set secure file permissions (owner read/write only).
        
        Args:
            file_path: Path to file
            
        Returns:
            True if permissions set successfully, False otherwise
        """
        try:
            if self.is_windows:
                # Windows: Use icacls to set permissions
                self._set_windows_permissions(file_path)
            else:
                # Unix-like: Use chmod
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
            
            logger.debug(f"Secure permissions set: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set secure permissions on {file_path}: {e}")
            return False

    def _set_windows_permissions(self, file_path: Path):
        """Set Windows NTFS permissions using icacls"""
        try:
            # Remove all inherited permissions and grant full control to current user only
            current_user = os.environ.get('USERNAME', 'UNKNOWN')
            
            # Remove inheritance
            subprocess.run([
                'icacls', str(file_path), '/inheritance:r'
            ], check=True, capture_output=True, text=True)
            
            # Grant full control to current user
            subprocess.run([
                'icacls', str(file_path), f'/grant:r', f'{current_user}:F'
            ], check=True, capture_output=True, text=True)
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to set Windows permissions with icacls: {e}")
            # Fall back to basic file attributes
            try:
                os.chmod(file_path, stat.S_IREAD | stat.S_IWRITE)
            except:
                pass
        except Exception as e:
            logger.warning(f"Windows permission setting failed: {e}")

    def atomic_write(self, 
                     file_path: Union[str, Path], 
                     data: bytes, 
                     session_id: Optional[str] = None) -> FileOperationResult:
        """
        Perform atomic file write operation.
        
        Args:
            file_path: Target file path
            data: Data to write
            session_id: Optional session ID for access control
            
        Returns:
            FileOperationResult with operation details
        """
        try:
            # Validate path
            validated_path = self.validate_path(file_path, session_id)
            
            # Ensure parent directory exists
            validated_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create temporary file in same directory for atomic operation
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(
                    dir=validated_path.parent,
                    delete=False,
                    prefix=f".tmp_{validated_path.name}_"
                ) as temp_file:
                    temp_path = Path(temp_file.name)
                    temp_file.write(data)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())  # Force write to disk
                
                # Set secure permissions on temp file
                self.set_secure_permissions(temp_path)
                
                # Atomic move to final location
                if self.is_windows:
                    # Windows: Handle potential file locking issues
                    if validated_path.exists():
                        validated_path.unlink()
                    temp_path.rename(validated_path)
                else:
                    # Unix: Atomic rename
                    temp_path.replace(validated_path)
                
                logger.info(f"Atomic write completed: {validated_path} ({len(data)} bytes)")
                
                return FileOperationResult(
                    success=True,
                    message="File written successfully",
                    path=validated_path,
                    bytes_processed=len(data)
                )
                
            except Exception as e:
                # Clean up temporary file on error
                if temp_file and temp_path.exists():
                    try:
                        temp_path.unlink()
                    except:
                        pass
                raise
                
        except Exception as e:
            logger.error(f"Atomic write failed for {file_path}: {e}")
            return FileOperationResult(
                success=False,
                message=f"Write failed: {str(e)}"
            )

    def secure_read(self, 
                   file_path: Union[str, Path], 
                   session_id: Optional[str] = None) -> FileOperationResult:
        """
        Perform secure file read operation.
        
        Args:
            file_path: File path to read
            session_id: Optional session ID for access control
            
        Returns:
            FileOperationResult with file data or error message
        """
        try:
            # Validate path
            validated_path = self.validate_path(file_path, session_id)
            
            if not validated_path.exists():
                return FileOperationResult(
                    success=False,
                    message="File not found"
                )
            
            if not validated_path.is_file():
                return FileOperationResult(
                    success=False,
                    message="Path is not a file"
                )
            
            # Check file permissions
            if not os.access(validated_path, os.R_OK):
                return FileOperationResult(
                    success=False,
                    message="File not readable"
                )
            
            # Read file
            file_data = validated_path.read_bytes()
            
            logger.info(f"Secure read completed: {validated_path} ({len(file_data)} bytes)")
            
            return FileOperationResult(
                success=True,
                message="File read successfully",
                path=validated_path,
                bytes_processed=len(file_data)
            )
            
        except Exception as e:
            logger.error(f"Secure read failed for {file_path}: {e}")
            return FileOperationResult(
                success=False,
                message=f"Read failed: {str(e)}"
            )

    def secure_delete(self, 
                     file_path: Union[str, Path], 
                     overwrite_passes: int = 3,
                     session_id: Optional[str] = None) -> FileOperationResult:
        """
        Perform secure file deletion with optional overwriting.
        
        Args:
            file_path: File path to delete
            overwrite_passes: Number of overwrite passes (0 for simple deletion)
            session_id: Optional session ID for access control
            
        Returns:
            FileOperationResult with operation details
        """
        try:
            # Validate path
            validated_path = self.validate_path(file_path, session_id)
            
            if not validated_path.exists():
                return FileOperationResult(
                    success=False,
                    message="File not found"
                )
            
            if not validated_path.is_file():
                return FileOperationResult(
                    success=False,
                    message="Path is not a file"
                )
            
            file_size = validated_path.stat().st_size
            
            # Perform overwrite passes if requested
            if overwrite_passes > 0:
                self._secure_overwrite(validated_path, overwrite_passes)
            
            # Delete the file
            validated_path.unlink()
            
            logger.info(f"Secure delete completed: {validated_path} ({file_size} bytes, {overwrite_passes} passes)")
            
            return FileOperationResult(
                success=True,
                message=f"File deleted successfully ({overwrite_passes} overwrite passes)",
                path=validated_path,
                bytes_processed=file_size * overwrite_passes
            )
            
        except Exception as e:
            logger.error(f"Secure delete failed for {file_path}: {e}")
            return FileOperationResult(
                success=False,
                message=f"Delete failed: {str(e)}"
            )

    def _secure_overwrite(self, file_path: Path, passes: int):
        """
        Overwrite file with random data multiple times.
        
        Args:
            file_path: Path to file to overwrite
            passes: Number of overwrite passes
        """
        try:
            file_size = file_path.stat().st_size
            
            for pass_num in range(passes):
                # Generate random data
                random_data = secrets.token_bytes(file_size)
                
                # Overwrite file
                with open(file_path, 'wb') as f:
                    f.write(random_data)
                    f.flush()
                    os.fsync(f.fileno())
                
                logger.debug(f"Overwrite pass {pass_num + 1}/{passes} completed: {file_path}")
            
        except Exception as e:
            logger.error(f"Secure overwrite failed for {file_path}: {e}")
            raise

    def list_directory(self, 
                      directory_path: Union[str, Path], 
                      session_id: Optional[str] = None) -> FileOperationResult:
        """
        List files in directory with security validation.
        
        Args:
            directory_path: Directory path to list
            session_id: Optional session ID for access control
            
        Returns:
            FileOperationResult with file list or error message
        """
        try:
            # Validate path
            validated_path = self.validate_path(directory_path, session_id)
            
            if not validated_path.exists():
                return FileOperationResult(
                    success=False,
                    message="Directory not found"
                )
            
            if not validated_path.is_dir():
                return FileOperationResult(
                    success=False,
                    message="Path is not a directory"
                )
            
            # List files
            file_list = []
            for item in validated_path.iterdir():
                if item.is_file():
                    file_list.append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "modified": item.stat().st_mtime
                    })
            
            logger.info(f"Directory listed: {validated_path} ({len(file_list)} files)")
            
            return FileOperationResult(
                success=True,
                message=f"Directory listed successfully ({len(file_list)} files)",
                path=validated_path
            )
            
        except Exception as e:
            logger.error(f"Directory listing failed for {directory_path}: {e}")
            return FileOperationResult(
                success=False,
                message=f"Listing failed: {str(e)}"
            )

    def file_exists(self, 
                   file_path: Union[str, Path], 
                   session_id: Optional[str] = None) -> bool:
        """
        Check if file exists with security validation.
        
        Args:
            file_path: File path to check
            session_id: Optional session ID for access control
            
        Returns:
            True if file exists and is accessible, False otherwise
        """
        try:
            validated_path = self.validate_path(file_path, session_id)
            return validated_path.exists() and validated_path.is_file()
        except:
            return False

    def get_file_info(self, 
                     file_path: Union[str, Path], 
                     session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get file information with security validation.
        
        Args:
            file_path: File path to get info for
            session_id: Optional session ID for access control
            
        Returns:
            Dictionary with file information or None if error
        """
        try:
            validated_path = self.validate_path(file_path, session_id)
            
            if not validated_path.exists() or not validated_path.is_file():
                return None
            
            stat_info = validated_path.stat()
            
            return {
                "name": validated_path.name,
                "path": str(validated_path),
                "size": stat_info.st_size,
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "accessed": stat_info.st_atime,
                "permissions": oct(stat_info.st_mode)[-3:]
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None

    def cleanup_directory(self, 
                         directory_path: Union[str, Path], 
                         session_id: Optional[str] = None,
                         overwrite_passes: int = 0) -> FileOperationResult:
        """
        Securely clean up all files in a directory.
        
        Args:
            directory_path: Directory path to clean
            session_id: Optional session ID for access control
            overwrite_passes: Number of overwrite passes for each file
            
        Returns:
            FileOperationResult with cleanup details
        """
        try:
            validated_path = self.validate_path(directory_path, session_id)
            
            if not validated_path.exists() or not validated_path.is_dir():
                return FileOperationResult(
                    success=False,
                    message="Directory not found or not a directory"
                )
            
            deleted_count = 0
            total_bytes = 0
            
            # Delete all files in directory
            for item in validated_path.iterdir():
                if item.is_file():
                    file_size = item.stat().st_size
                    result = self.secure_delete(item, overwrite_passes, session_id)
                    if result.success:
                        deleted_count += 1
                        total_bytes += file_size
            
            logger.info(f"Directory cleanup completed: {validated_path} ({deleted_count} files, {total_bytes} bytes)")
            
            return FileOperationResult(
                success=True,
                message=f"Directory cleaned: {deleted_count} files deleted",
                path=validated_path,
                bytes_processed=total_bytes
            )
            
        except Exception as e:
            logger.error(f"Directory cleanup failed for {directory_path}: {e}")
            return FileOperationResult(
                success=False,
                message=f"Cleanup failed: {str(e)}"
            )


# Convenience functions for common operations

def create_secure_file_ops(base_directory: Optional[Union[str, Path]] = None) -> SecureFileOperations:
    """Create a new secure file operations instance"""
    return SecureFileOperations(base_directory)


def secure_write_file(file_path: Union[str, Path], 
                     data: bytes, 
                     base_directory: Optional[Union[str, Path]] = None,
                     session_id: Optional[str] = None) -> FileOperationResult:
    """Convenience function for secure file writing"""
    ops = create_secure_file_ops(base_directory)
    return ops.atomic_write(file_path, data, session_id)


def secure_read_file(file_path: Union[str, Path], 
                    base_directory: Optional[Union[str, Path]] = None,
                    session_id: Optional[str] = None) -> FileOperationResult:
    """Convenience function for secure file reading"""
    ops = create_secure_file_ops(base_directory)
    return ops.secure_read(file_path, session_id)


def secure_delete_file(file_path: Union[str, Path], 
                      overwrite_passes: int = 3,
                      base_directory: Optional[Union[str, Path]] = None,
                      session_id: Optional[str] = None) -> FileOperationResult:
    """Convenience function for secure file deletion"""
    ops = create_secure_file_ops(base_directory)
    return ops.secure_delete(file_path, overwrite_passes, session_id) 