"""
Encrypted JSON Storage Module

Provides secure local storage for processed and pseudonymized data using AES-256-GCM encryption.
Ensures data is encrypted at rest with proper key management and atomic file operations.

Features:
- AES-256-GCM authenticated encryption
- PBKDF2 key derivation from passwords
- Atomic file operations
- Secure key management
- Support for demo data and analysis results
- Comprehensive error handling

Security considerations:
- Keys are derived using PBKDF2 with random salts
- Each file has unique encryption parameters
- Authenticated encryption prevents tampering
- No keys are stored on disk
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import secrets
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from loguru import logger


@dataclass
class EncryptionMetadata:
    """Metadata for encrypted storage"""
    salt: bytes
    nonce: bytes
    algorithm: str = "AES-256-GCM"
    kdf_iterations: int = 100000


class EncryptedJSONStorage:
    """
    Secure encrypted JSON storage for local data persistence.
    
    Uses AES-256-GCM for authenticated encryption with PBKDF2 key derivation.
    Provides atomic file operations and secure key management.
    """
    
    def __init__(self, storage_dir: Optional[Union[str, Path]] = None):
        """
        Initialize encrypted storage manager.
        
        Args:
            storage_dir: Directory for encrypted files (default: data/encrypted_storage)
        """
        if storage_dir is None:
            storage_dir = Path("data") / "encrypted_storage"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure directory has restricted permissions
        self._set_secure_permissions(self.storage_dir)
        
        logger.info(f"EncryptedJSONStorage initialized: {self.storage_dir}")

    def _set_secure_permissions(self, path: Path) -> None:
        """Set secure file permissions (owner read/write only)"""
        try:
            if os.name != 'nt':  # Unix-like systems
                os.chmod(path, 0o700)
            else:  # Windows - set restricted permissions using icacls if available
                # Windows permissions are more complex, use default for now
                pass
        except Exception as e:
            logger.warning(f"Could not set secure permissions on {path}: {e}")

    def _derive_key(self, password: str, salt: bytes, iterations: int = 100000) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: Password for key derivation
            salt: Random salt for key derivation
            iterations: Number of PBKDF2 iterations
            
        Returns:
            32-byte encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))

    def _encrypt_data(self, data: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
        """
        Encrypt data using AES-256-GCM.
        
        Args:
            data: Data to encrypt
            key: 32-byte encryption key
            
        Returns:
            Tuple of (encrypted_data, nonce, tag)
        """
        # Generate random nonce
        nonce = secrets.token_bytes(12)  # 96 bits for GCM
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return ciphertext, nonce, encryptor.tag

    def _decrypt_data(self, encrypted_data: bytes, key: bytes, nonce: bytes, tag: bytes) -> bytes:
        """
        Decrypt data using AES-256-GCM.
        
        Args:
            encrypted_data: Encrypted data
            key: 32-byte encryption key
            nonce: Nonce used for encryption
            tag: Authentication tag
            
        Returns:
            Decrypted data
            
        Raises:
            ValueError: If authentication fails
        """
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        return decryptor.update(encrypted_data) + decryptor.finalize()

    def store_json(self, 
                   data: Dict[str, Any], 
                   filename: str, 
                   password: str,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store JSON data in encrypted format.
        
        Args:
            data: Dictionary to store as JSON
            filename: Filename (without extension)
            password: Password for encryption
            metadata: Optional metadata to include
            
        Returns:
            Path to the encrypted file
            
        Raises:
            ValueError: If data cannot be serialized
            OSError: If file operations fail
        """
        try:
            # Prepare data structure
            storage_data = {
                "data": data,
                "metadata": metadata or {},
                "version": "1.0"
            }
            
            # Serialize to JSON
            json_data = json.dumps(storage_data, ensure_ascii=False, indent=None)
            data_bytes = json_data.encode('utf-8')
            
            # Generate salt and derive key
            salt = secrets.token_bytes(32)  # 256 bits
            key = self._derive_key(password, salt)
            
            # Encrypt data
            encrypted_data, nonce, tag = self._encrypt_data(data_bytes, key)
            
            # Create encryption metadata
            enc_metadata = EncryptionMetadata(salt=salt, nonce=nonce)
            
            # Prepare final structure
            file_structure = {
                "encrypted_data": base64.b64encode(encrypted_data).decode('ascii'),
                "salt": base64.b64encode(enc_metadata.salt).decode('ascii'),
                "nonce": base64.b64encode(enc_metadata.nonce).decode('ascii'),
                "tag": base64.b64encode(tag).decode('ascii'),
                "algorithm": enc_metadata.algorithm,
                "kdf_iterations": enc_metadata.kdf_iterations
            }
            
            # Write to file atomically
            file_path = self.storage_dir / f"{filename}.encrypted.json"
            temp_file = None
            
            try:
                # Create temporary file in same directory for atomic operation
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    dir=self.storage_dir, 
                    delete=False,
                    encoding='utf-8'
                ) as temp_file:
                    json.dump(file_structure, temp_file, indent=2)
                    temp_file_path = temp_file.name
                
                # Set secure permissions on temp file
                self._set_secure_permissions(Path(temp_file_path))
                
                # Atomic move
                os.replace(temp_file_path, file_path)
                
                logger.info(f"Successfully stored encrypted JSON: {file_path}")
                return str(file_path)
                
            except Exception as e:
                # Clean up temporary file on error
                if temp_file and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
                raise
                
        except Exception as e:
            logger.error(f"Failed to store encrypted JSON {filename}: {e}")
            raise

    def load_json(self, filename: str, password: str) -> Dict[str, Any]:
        """
        Load and decrypt JSON data.
        
        Args:
            filename: Filename (without extension) or full path
            password: Password for decryption
            
        Returns:
            Decrypted data dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If decryption fails or data is invalid
            OSError: If file operations fail
        """
        try:
            # Determine file path
            if filename.endswith('.encrypted.json'):
                file_path = Path(filename) if os.path.isabs(filename) else self.storage_dir / filename
            else:
                file_path = self.storage_dir / f"{filename}.encrypted.json"
            
            if not file_path.exists():
                raise FileNotFoundError(f"Encrypted file not found: {file_path}")
            
            # Read encrypted file
            with open(file_path, 'r', encoding='utf-8') as f:
                file_structure = json.load(f)
            
            # Extract encryption parameters
            encrypted_data = base64.b64decode(file_structure["encrypted_data"])
            salt = base64.b64decode(file_structure["salt"])
            nonce = base64.b64decode(file_structure["nonce"])
            tag = base64.b64decode(file_structure["tag"])
            iterations = file_structure.get("kdf_iterations", 100000)
            
            # Derive key
            key = self._derive_key(password, salt, iterations)
            
            # Decrypt data
            decrypted_bytes = self._decrypt_data(encrypted_data, key, nonce, tag)
            
            # Parse JSON
            json_str = decrypted_bytes.decode('utf-8')
            storage_data = json.loads(json_str)
            
            logger.info(f"Successfully loaded encrypted JSON: {file_path}")
            
            # Return the actual data
            return storage_data.get("data", storage_data)
            
        except Exception as e:
            logger.error(f"Failed to load encrypted JSON {filename}: {e}")
            raise

    def delete_file(self, filename: str) -> bool:
        """
        Securely delete encrypted file.
        
        Args:
            filename: Filename (without extension) or full path
            
        Returns:
            True if file was deleted, False if not found
        """
        try:
            # Determine file path
            if filename.endswith('.encrypted.json'):
                file_path = Path(filename) if os.path.isabs(filename) else self.storage_dir / filename
            else:
                file_path = self.storage_dir / f"{filename}.encrypted.json"
            
            if file_path.exists():
                os.unlink(file_path)
                logger.info(f"Deleted encrypted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete encrypted file {filename}: {e}")
            raise

    def list_files(self) -> list[str]:
        """
        List all encrypted files in storage directory.
        
        Returns:
            List of filenames (without .encrypted.json extension)
        """
        try:
            files = []
            for file_path in self.storage_dir.glob("*.encrypted.json"):
                # Remove .encrypted.json extension
                name = file_path.stem.replace('.encrypted', '')
                files.append(name)
            
            logger.info(f"Found {len(files)} encrypted files")
            return sorted(files)
            
        except Exception as e:
            logger.error(f"Failed to list encrypted files: {e}")
            return []

    def file_exists(self, filename: str) -> bool:
        """
        Check if encrypted file exists.
        
        Args:
            filename: Filename (without extension)
            
        Returns:
            True if file exists
        """
        file_path = self.storage_dir / f"{filename}.encrypted.json"
        return file_path.exists()

    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get information about encrypted file without decrypting.
        
        Args:
            filename: Filename (without extension)
            
        Returns:
            Dictionary with file information or None if not found
        """
        try:
            file_path = self.storage_dir / f"{filename}.encrypted.json"
            
            if not file_path.exists():
                return None
            
            # Get file stats
            stat = file_path.stat()
            
            # Read metadata only (without decrypting)
            with open(file_path, 'r', encoding='utf-8') as f:
                file_structure = json.load(f)
            
            return {
                "filename": filename,
                "path": str(file_path),
                "size_bytes": stat.st_size,
                "modified_time": stat.st_mtime,
                "algorithm": file_structure.get("algorithm", "unknown"),
                "kdf_iterations": file_structure.get("kdf_iterations", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {filename}: {e}")
            return None

    def cleanup_all(self) -> int:
        """
        Delete all encrypted files in storage directory.
        
        Returns:
            Number of files deleted
        """
        try:
            deleted_count = 0
            for file_path in self.storage_dir.glob("*.encrypted.json"):
                try:
                    os.unlink(file_path)
                    deleted_count += 1
                    logger.debug(f"Deleted: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")
            
            logger.info(f"Cleanup completed: {deleted_count} files deleted")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed during cleanup: {e}")
            return 0


# Convenience functions for common operations

def create_storage(storage_dir: Optional[Union[str, Path]] = None) -> EncryptedJSONStorage:
    """Create a new encrypted storage instance"""
    return EncryptedJSONStorage(storage_dir)


def store_data(data: Dict[str, Any], 
               filename: str, 
               password: str,
               storage_dir: Optional[Union[str, Path]] = None) -> str:
    """Convenience function to store data"""
    storage = create_storage(storage_dir)
    return storage.store_json(data, filename, password)


def load_data(filename: str, 
              password: str,
              storage_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Convenience function to load data"""
    storage = create_storage(storage_dir)
    return storage.load_json(filename, password) 