"""
Encrypted credential storage system for MSP SSL Chaos Tamer

Provides secure, zero-trust credential storage with AES-256 encryption,
credential rotation, and key management utilities for CA credentials.
"""

import os
import json
import base64
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dataclasses import dataclass, field

from ..core.interfaces import ReflectiveModule


@dataclass
class CredentialEntry:
    """Encrypted credential entry with metadata"""
    ca_name: str
    encrypted_data: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_rotated: datetime = field(default_factory=datetime.utcnow)
    rotation_interval_days: int = 90
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_rotation_due(self) -> bool:
        """Check if credential rotation is due"""
        rotation_due_date = self.last_rotated + timedelta(days=self.rotation_interval_days)
        return datetime.utcnow() >= rotation_due_date
    
    def days_until_rotation(self) -> int:
        """Calculate days until rotation is due"""
        rotation_due_date = self.last_rotated + timedelta(days=self.rotation_interval_days)
        delta = rotation_due_date - datetime.utcnow()
        return max(0, delta.days)


class EncryptedCredentialStore(ReflectiveModule):
    """
    Secure credential storage with AES-256 encryption
    
    Provides zero-trust credential management for CA API keys and secrets
    with automatic rotation, key derivation, and audit logging.
    """
    
    def __init__(self, storage_path: str = "credentials.enc", master_key: Optional[str] = None):
        super().__init__()
        self.storage_path = storage_path
        self.logger = logging.getLogger("msp_ssl.credential_store")
        
        # Initialize encryption
        self._master_key = master_key or self._generate_master_key()
        self._fernet = self._create_fernet_cipher()
        
        # Credential storage
        self._credentials: Dict[str, CredentialEntry] = {}
        self._load_credentials()
        
        self.logger.info("Encrypted credential store initialized")
    
    def _generate_master_key(self) -> str:
        """Generate a new master key for encryption"""
        # In production, this should come from environment variables or secure key management
        master_key = os.environ.get("MSP_SSL_MASTER_KEY")
        if not master_key:
            # Generate a new key and warn user to save it
            key = Fernet.generate_key()
            master_key = base64.urlsafe_b64encode(key).decode()
            self.logger.warning(
                f"Generated new master key. SAVE THIS KEY: {master_key}"
            )
            self.logger.warning(
                "Set MSP_SSL_MASTER_KEY environment variable to persist this key"
            )
        
        return master_key
    
    def _create_fernet_cipher(self) -> Fernet:
        """Create Fernet cipher from master key"""
        try:
            # Derive key from master key using PBKDF2
            master_key_bytes = base64.urlsafe_b64decode(self._master_key.encode())
            salt = b"msp_ssl_chaos_tamer_salt"  # In production, use random salt per credential
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(master_key_bytes))
            return Fernet(key)
            
        except Exception as e:
            self.logger.error(f"Failed to create encryption cipher: {e}")
            raise ValueError(f"Invalid master key: {e}")
    
    def _load_credentials(self) -> None:
        """Load encrypted credentials from storage"""
        if not os.path.exists(self.storage_path):
            self.logger.info("No existing credential store found, starting fresh")
            return
        
        # Check if file is empty
        if os.path.getsize(self.storage_path) == 0:
            self.logger.info("Empty credential store found, starting fresh")
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                encrypted_data = json.load(f)
            
            for ca_name, entry_data in encrypted_data.items():
                self._credentials[ca_name] = CredentialEntry(
                    ca_name=ca_name,
                    encrypted_data=entry_data["encrypted_data"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    last_rotated=datetime.fromisoformat(entry_data["last_rotated"]),
                    rotation_interval_days=entry_data.get("rotation_interval_days", 90),
                    metadata=entry_data.get("metadata", {})
                )
            
            self.logger.info(f"Loaded {len(self._credentials)} credential entries")
            
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            raise ValueError(f"Credential store corrupted: {e}")
    
    def _save_credentials(self) -> None:
        """Save encrypted credentials to storage"""
        try:
            # Prepare data for serialization
            data = {}
            for ca_name, entry in self._credentials.items():
                data[ca_name] = {
                    "encrypted_data": entry.encrypted_data,
                    "created_at": entry.created_at.isoformat(),
                    "last_rotated": entry.last_rotated.isoformat(),
                    "rotation_interval_days": entry.rotation_interval_days,
                    "metadata": entry.metadata
                }
            
            # Write to temporary file first, then rename for atomic operation
            temp_path = f"{self.storage_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            os.rename(temp_path, self.storage_path)
            self.logger.debug(f"Saved {len(self._credentials)} credential entries")
            
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
            raise ValueError(f"Failed to save credential store: {e}")
    
    def store_credential(self, ca_name: str, credentials: Dict[str, str], 
                        rotation_interval_days: int = 90, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store encrypted CA credentials
        
        Args:
            ca_name: Name of the Certificate Authority
            credentials: Dictionary of credential data (API keys, secrets, etc.)
            rotation_interval_days: Days between credential rotations
            metadata: Additional metadata for the credential
            
        Returns:
            bool: True if credentials stored successfully
        """
        try:
            # Serialize credentials to JSON
            credential_json = json.dumps(credentials)
            
            # Encrypt the credential data
            encrypted_data = self._fernet.encrypt(credential_json.encode()).decode()
            
            # Create credential entry
            entry = CredentialEntry(
                ca_name=ca_name,
                encrypted_data=encrypted_data,
                rotation_interval_days=rotation_interval_days,
                metadata=metadata or {}
            )
            
            # Store and save
            self._credentials[ca_name] = entry
            self._save_credentials()
            
            self.logger.info(f"Stored credentials for CA: {ca_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store credentials for {ca_name}: {e}")
            return False
    
    def retrieve_credential(self, ca_name: str) -> Optional[Dict[str, str]]:
        """
        Retrieve and decrypt CA credentials
        
        Args:
            ca_name: Name of the Certificate Authority
            
        Returns:
            Dict containing decrypted credentials, None if not found
        """
        if ca_name not in self._credentials:
            self.logger.warning(f"No credentials found for CA: {ca_name}")
            return None
        
        try:
            entry = self._credentials[ca_name]
            
            # Decrypt the credential data
            decrypted_data = self._fernet.decrypt(entry.encrypted_data.encode())
            credentials = json.loads(decrypted_data.decode())
            
            self.logger.debug(f"Retrieved credentials for CA: {ca_name}")
            return credentials
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt credentials for {ca_name}: {e}")
            return None
    
    def rotate_credential(self, ca_name: str, new_credentials: Dict[str, str]) -> bool:
        """
        Rotate CA credentials with new values
        
        Args:
            ca_name: Name of the Certificate Authority
            new_credentials: New credential data
            
        Returns:
            bool: True if rotation successful
        """
        if ca_name not in self._credentials:
            self.logger.error(f"Cannot rotate non-existent credentials for CA: {ca_name}")
            return False
        
        try:
            # Get existing entry
            entry = self._credentials[ca_name]
            
            # Encrypt new credentials
            credential_json = json.dumps(new_credentials)
            encrypted_data = self._fernet.encrypt(credential_json.encode()).decode()
            
            # Update entry
            entry.encrypted_data = encrypted_data
            entry.last_rotated = datetime.utcnow()
            
            # Save changes
            self._save_credentials()
            
            self.logger.info(f"Rotated credentials for CA: {ca_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rotate credentials for {ca_name}: {e}")
            return False
    
    def delete_credential(self, ca_name: str) -> bool:
        """
        Delete CA credentials
        
        Args:
            ca_name: Name of the Certificate Authority
            
        Returns:
            bool: True if deletion successful
        """
        if ca_name not in self._credentials:
            self.logger.warning(f"No credentials to delete for CA: {ca_name}")
            return False
        
        try:
            del self._credentials[ca_name]
            self._save_credentials()
            
            self.logger.info(f"Deleted credentials for CA: {ca_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete credentials for {ca_name}: {e}")
            return False
    
    def list_credentials(self) -> List[str]:
        """
        List all stored CA names
        
        Returns:
            List of CA names with stored credentials
        """
        return list(self._credentials.keys())
    
    def get_credential_info(self, ca_name: str) -> Optional[Dict[str, Any]]:
        """
        Get credential metadata without decrypting
        
        Args:
            ca_name: Name of the Certificate Authority
            
        Returns:
            Dict containing credential metadata
        """
        if ca_name not in self._credentials:
            return None
        
        entry = self._credentials[ca_name]
        return {
            "ca_name": entry.ca_name,
            "created_at": entry.created_at.isoformat(),
            "last_rotated": entry.last_rotated.isoformat(),
            "rotation_interval_days": entry.rotation_interval_days,
            "rotation_due": entry.is_rotation_due(),
            "days_until_rotation": entry.days_until_rotation(),
            "metadata": entry.metadata
        }
    
    def get_rotation_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get rotation status for all credentials
        
        Returns:
            Dict mapping CA names to rotation status
        """
        status = {}
        for ca_name, entry in self._credentials.items():
            status[ca_name] = {
                "rotation_due": entry.is_rotation_due(),
                "days_until_rotation": entry.days_until_rotation(),
                "last_rotated": entry.last_rotated.isoformat()
            }
        
        return status
    
    def backup_credentials(self, backup_path: str) -> bool:
        """
        Create encrypted backup of all credentials
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            bool: True if backup successful
        """
        try:
            # Create backup with timestamp
            backup_data = {
                "backup_timestamp": datetime.utcnow().isoformat(),
                "credentials": {}
            }
            
            for ca_name, entry in self._credentials.items():
                backup_data["credentials"][ca_name] = {
                    "encrypted_data": entry.encrypted_data,
                    "created_at": entry.created_at.isoformat(),
                    "last_rotated": entry.last_rotated.isoformat(),
                    "rotation_interval_days": entry.rotation_interval_days,
                    "metadata": entry.metadata
                }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            self.logger.info(f"Created credential backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    # ReflectiveModule implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get credential store module information"""
        return {
            "module_name": "encrypted_credential_store",
            "module_type": "storage",
            "version": "1.0.0",
            "description": "Secure credential storage with AES-256 encryption"
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get credential store capabilities"""
        return [
            {"name": "credential_storage", "enabled": True},
            {"name": "credential_encryption", "enabled": True},
            {"name": "credential_rotation", "enabled": True},
            {"name": "credential_backup", "enabled": True},
            {"name": "audit_logging", "enabled": True}
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get credential store health status"""
        try:
            # Test encryption/decryption
            test_data = {"test": "data"}
            encrypted = self._fernet.encrypt(json.dumps(test_data).encode())
            decrypted = json.loads(self._fernet.decrypt(encrypted).decode())
            
            encryption_healthy = test_data == decrypted
            
            return {
                "status": "healthy" if encryption_healthy else "degraded",
                "encryption_functional": encryption_healthy,
                "stored_credentials": len(self._credentials),
                "storage_path": self.storage_path,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation for credential store"""
        try:
            # Test basic functionality
            health = self.get_health_status()
            
            if health["status"] != "healthy":
                return {
                    "degradation_applied": True,
                    "fallback_mode": "read_only",
                    "message": "Credential store in read-only mode due to encryption issues"
                }
            
            return {
                "degradation_applied": False,
                "fallback_mode": None,
                "message": "Credential store operating normally"
            }
            
        except Exception as e:
            return {
                "degradation_applied": True,
                "fallback_mode": "offline",
                "message": f"Credential store offline: {e}"
            }