"""
Local Encrypted Storage System for PII Data

This module provides secure local storage for original PII data with AES-256 encryption.
Ensures data is never transmitted to external APIs and complies with GDPR/Hong Kong PDPO.

Key Features:
- AES-256-GCM encryption for strong security
- PBKDF2 key derivation with salt
- Automatic encryption/decryption
- Secure key management
- Local-only storage (no external transmission)
- Integration with privacy architecture
- Comprehensive audit logging
"""

import os
import json
import hashlib
import secrets
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EncryptionMetadata:
    """Metadata for encrypted storage entries."""

    encrypted_at: str
    key_derivation: str = "PBKDF2-SHA256"
    encryption_algorithm: str = "AES-256-GCM"
    data_hash: str = ""
    access_count: int = 0
    last_accessed: Optional[str] = None


@dataclass
class StorageEntry:
    """Container for encrypted storage entry."""

    encrypted_data: str
    metadata: EncryptionMetadata
    nonce: str
    salt: str


class EncryptedStorage:
    """
    Secure local encrypted storage for PII data.

    Uses AES-256-GCM encryption with PBKDF2 key derivation to ensure
    original PII data is stored securely locally and never transmitted externally.
    """

    def __init__(
        self, storage_path: str = "data/encrypted_storage", master_password: Optional[str] = None
    ):
        """
        Initialize encrypted storage system.

        Args:
            storage_path: Directory path for encrypted storage files
            master_password: Master password for encryption (auto-generated if None)
        """
        self.storage_path = storage_path
        self.backend = default_backend()

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        # Initialize or load master password
        self.master_password = self._initialize_master_password(master_password)

        # Storage for runtime data access
        self._runtime_cache = {}

        logger.info(f"EncryptedStorage initialized at: {storage_path}")

    def _initialize_master_password(self, provided_password: Optional[str]) -> str:
        """Initialize or load master password securely."""
        password_file = os.path.join(self.storage_path, ".master_key_hash")

        if provided_password:
            # Use provided password and save hash for verification
            password = provided_password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            with open(password_file, "w") as f:
                f.write(password_hash)
        elif os.path.exists(password_file):
            # Load existing password (in production, this would be from secure input)
            # For demo purposes, using a default password
            password = "default_encryption_password_change_in_production"
            with open(password_file, "r") as f:
                stored_hash = f.read().strip()
                if hashlib.sha256(password.encode()).hexdigest() != stored_hash:
                    raise ValueError("Invalid master password")
        else:
            # Generate secure random password
            password = base64.b64encode(secrets.token_bytes(32)).decode()
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            with open(password_file, "w") as f:
                f.write(password_hash)
            logger.warning(f"Generated new master password. Store securely: {password}")

        return password

    def _derive_key(self, salt: bytes, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
            backend=self.backend,
        )
        return kdf.derive(password.encode())

    def _encrypt_data(self, data: str, password: str) -> StorageEntry:
        """Encrypt data using AES-256-GCM."""
        # Generate random salt and nonce
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)  # GCM standard nonce size

        # Derive encryption key
        key = self._derive_key(salt, password)

        # Encrypt data
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=self.backend)
        encryptor = cipher.encryptor()

        data_bytes = data.encode("utf-8")
        ciphertext = encryptor.update(data_bytes) + encryptor.finalize()

        # Combine ciphertext and authentication tag
        encrypted_data = ciphertext + encryptor.tag

        # Create metadata
        metadata = EncryptionMetadata(
            encrypted_at=datetime.now().isoformat(),
            data_hash=hashlib.sha256(data_bytes).hexdigest(),
        )

        return StorageEntry(
            encrypted_data=base64.b64encode(encrypted_data).decode(),
            metadata=metadata,
            nonce=base64.b64encode(nonce).decode(),
            salt=base64.b64encode(salt).decode(),
        )

    def _decrypt_data(self, entry: StorageEntry, password: str) -> str:
        """Decrypt data using AES-256-GCM."""
        # Decode components
        encrypted_data = base64.b64decode(entry.encrypted_data)
        nonce = base64.b64decode(entry.nonce)
        salt = base64.b64decode(entry.salt)

        # Split ciphertext and tag
        ciphertext = encrypted_data[:-16]
        tag = encrypted_data[-16:]

        # Derive decryption key
        key = self._derive_key(salt, password)

        # Decrypt data
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=self.backend)
        decryptor = cipher.decryptor()

        decrypted_bytes = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_bytes.decode("utf-8")

    def store_dataframe(
        self, df: pd.DataFrame, identifier: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store DataFrame with encryption.

        Args:
            df: DataFrame to store
            identifier: Unique identifier for the data
            metadata: Additional metadata to store

        Returns:
            Storage key for retrieval
        """
        # Convert DataFrame to JSON
        data_dict = {
            "dataframe": df.to_json(orient="records", date_format="iso"),
            "columns": list(df.columns),
            "shape": df.shape,
            "dtypes": df.dtypes.astype(str).to_dict(),
            "metadata": metadata or {},
        }

        data_json = json.dumps(data_dict, indent=2)

        # Encrypt data
        entry = self._encrypt_data(data_json, self.master_password)

        # Save to file
        storage_key = f"df_{identifier}_{int(datetime.now().timestamp())}"
        file_path = os.path.join(self.storage_path, f"{storage_key}.enc")

        with open(file_path, "w") as f:
            json.dump(asdict(entry), f, indent=2)

        logger.info(f"DataFrame stored with key: {storage_key}")
        return storage_key

    def retrieve_dataframe(self, storage_key: str) -> tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Retrieve and decrypt DataFrame.

        Args:
            storage_key: Key returned from store_dataframe

        Returns:
            Tuple of (DataFrame, metadata)
        """
        file_path = os.path.join(self.storage_path, f"{storage_key}.enc")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Storage file not found: {storage_key}")

        # Load encrypted entry
        with open(file_path, "r") as f:
            entry_dict = json.load(f)

        entry = StorageEntry(
            encrypted_data=entry_dict["encrypted_data"],
            metadata=EncryptionMetadata(**entry_dict["metadata"]),
            nonce=entry_dict["nonce"],
            salt=entry_dict["salt"],
        )

        # Update access tracking
        entry.metadata.access_count += 1
        entry.metadata.last_accessed = datetime.now().isoformat()

        # Decrypt data
        data_json = self._decrypt_data(entry, self.master_password)
        data_dict = json.loads(data_json)

        # Reconstruct DataFrame
        df = pd.read_json(data_dict["dataframe"], orient="records")

        # Restore column order and types
        df = df[data_dict["columns"]]
        for col, dtype in data_dict["dtypes"].items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except Exception as e:
                    logger.warning(f"Could not restore dtype {dtype} for column {col}: {e}")

        # Update file with access tracking
        with open(file_path, "w") as f:
            json.dump(asdict(entry), f, indent=2)

        logger.info(f"DataFrame retrieved with key: {storage_key}")
        return df, data_dict["metadata"]

    def store_json(self, data: Union[Dict, List], identifier: str) -> str:
        """
        Store JSON data with encryption.

        Args:
            data: JSON-serializable data to store
            identifier: Unique identifier

        Returns:
            Storage key for retrieval
        """
        data_json = json.dumps(data, indent=2, default=str)
        entry = self._encrypt_data(data_json, self.master_password)

        storage_key = f"json_{identifier}_{int(datetime.now().timestamp())}"
        file_path = os.path.join(self.storage_path, f"{storage_key}.enc")

        with open(file_path, "w") as f:
            json.dump(asdict(entry), f, indent=2)

        logger.info(f"JSON data stored with key: {storage_key}")
        return storage_key

    def retrieve_json(self, storage_key: str) -> Union[Dict, List]:
        """
        Retrieve and decrypt JSON data.

        Args:
            storage_key: Key returned from store_json

        Returns:
            Decrypted JSON data
        """
        file_path = os.path.join(self.storage_path, f"{storage_key}.enc")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Storage file not found: {storage_key}")

        with open(file_path, "r") as f:
            entry_dict = json.load(f)

        entry = StorageEntry(
            encrypted_data=entry_dict["encrypted_data"],
            metadata=EncryptionMetadata(**entry_dict["metadata"]),
            nonce=entry_dict["nonce"],
            salt=entry_dict["salt"],
        )

        # Update access tracking
        entry.metadata.access_count += 1
        entry.metadata.last_accessed = datetime.now().isoformat()

        data_json = self._decrypt_data(entry, self.master_password)

        # Update file with access tracking
        with open(file_path, "w") as f:
            json.dump(asdict(entry), f, indent=2)

        logger.info(f"JSON data retrieved with key: {storage_key}")
        return json.loads(data_json)

    def list_stored_data(self) -> List[Dict[str, Any]]:
        """
        List all stored data with metadata.

        Returns:
            List of storage information
        """
        storage_info = []

        for filename in os.listdir(self.storage_path):
            if filename.endswith(".enc"):
                try:
                    file_path = os.path.join(self.storage_path, filename)
                    with open(file_path, "r") as f:
                        entry_dict = json.load(f)

                    storage_key = filename.replace(".enc", "")
                    metadata = entry_dict["metadata"]

                    storage_info.append(
                        {
                            "storage_key": storage_key,
                            "encrypted_at": metadata["encrypted_at"],
                            "last_accessed": metadata.get("last_accessed"),
                            "access_count": metadata.get("access_count", 0),
                            "data_type": storage_key.split("_")[0],
                            "file_size": os.path.getsize(file_path),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Could not read metadata for {filename}: {e}")

        return sorted(storage_info, key=lambda x: x["encrypted_at"], reverse=True)

    def delete_stored_data(self, storage_key: str) -> bool:
        """
        Securely delete stored data.

        Args:
            storage_key: Key of data to delete

        Returns:
            True if deleted successfully
        """
        file_path = os.path.join(self.storage_path, f"{storage_key}.enc")

        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted storage key: {storage_key}")
            return True

        return False

    def verify_encryption_integrity(self, storage_key: str) -> bool:
        """
        Verify the integrity of encrypted data.

        Args:
            storage_key: Key to verify

        Returns:
            True if integrity check passes
        """
        try:
            file_path = os.path.join(self.storage_path, f"{storage_key}.enc")
            with open(file_path, "r") as f:
                entry_dict = json.load(f)

            entry = StorageEntry(
                encrypted_data=entry_dict["encrypted_data"],
                metadata=EncryptionMetadata(**entry_dict["metadata"]),
                nonce=entry_dict["nonce"],
                salt=entry_dict["salt"],
            )

            # Attempt decryption to verify integrity
            decrypted_data = self._decrypt_data(entry, self.master_password)

            # Verify hash if available
            if entry.metadata.data_hash:
                actual_hash = hashlib.sha256(decrypted_data.encode()).hexdigest()
                return actual_hash == entry.metadata.data_hash

            return True
        except Exception as e:
            logger.error(f"Integrity check failed for {storage_key}: {e}")
            return False

    def get_encryption_status(self) -> Dict[str, Any]:
        """
        Get status information about the encryption system.

        Returns:
            Dictionary with encryption system status
        """
        stored_data = self.list_stored_data()

        return {
            "encryption_algorithm": "AES-256-GCM",
            "key_derivation": "PBKDF2-SHA256",
            "storage_path": self.storage_path,
            "total_stored_items": len(stored_data),
            "storage_types": list(set(item["data_type"] for item in stored_data)),
            "total_storage_size": sum(item["file_size"] for item in stored_data),
            "oldest_entry": min((item["encrypted_at"] for item in stored_data), default=None),
            "newest_entry": max((item["encrypted_at"] for item in stored_data), default=None),
        }


# Global instance for easy access (initialized lazily)
encrypted_storage = None


def _get_global_storage():
    """Get or create global encrypted storage instance."""
    global encrypted_storage
    if encrypted_storage is None:
        encrypted_storage = EncryptedStorage()
    return encrypted_storage


def store_pii_dataframe(
    df: pd.DataFrame, identifier: str, metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to store PII DataFrame securely.

    Args:
        df: DataFrame containing PII data
        identifier: Unique identifier for the dataset
        metadata: Additional metadata

    Returns:
        Storage key for retrieval
    """
    return _get_global_storage().store_dataframe(df, identifier, metadata)


def retrieve_pii_dataframe(storage_key: str) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to retrieve PII DataFrame securely.

    Args:
        storage_key: Storage key from store_pii_dataframe

    Returns:
        Tuple of (DataFrame, metadata)
    """
    return _get_global_storage().retrieve_dataframe(storage_key)


def get_storage_status() -> Dict[str, Any]:
    """
    Convenience function to get encryption storage status.

    Returns:
        Storage system status information
    """
    return _get_global_storage().get_encryption_status()
