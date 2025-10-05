"""
Cryptographic utilities for WebSocket validation framework.
"""

import hashlib
import hmac
import secrets
from typing import Union, Optional


def hash_data(data: Union[str, bytes, dict]) -> str:
    """
    Generate SHA256 hash of data.
    
    Args:
        data: Data to hash (string, bytes, or dict)
        
    Returns:
        Hexadecimal hash string
    """
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    elif isinstance(data, dict):
        import json
        data_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
    elif isinstance(data, bytes):
        data_bytes = data
    else:
        data_bytes = str(data).encode('utf-8')
    
    return hashlib.sha256(data_bytes).hexdigest()


def encrypt_data(data: Union[str, bytes], key: bytes) -> bytes:
    """
    Encrypt data using AES encryption.
    
    Note: This is a placeholder implementation.
    In production, use proper encryption libraries like cryptography.
    
    Args:
        data: Data to encrypt
        key: Encryption key
        
    Returns:
        Encrypted data
    """
    # Placeholder implementation - in production use proper AES encryption
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = data
    
    # Simple XOR encryption for placeholder (NOT secure for production)
    encrypted = bytearray()
    key_len = len(key)
    
    for i, byte in enumerate(data_bytes):
        encrypted.append(byte ^ key[i % key_len])
    
    return bytes(encrypted)


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Decrypt data using AES decryption.
    
    Note: This is a placeholder implementation.
    In production, use proper encryption libraries like cryptography.
    
    Args:
        encrypted_data: Data to decrypt
        key: Decryption key
        
    Returns:
        Decrypted data
    """
    # Placeholder implementation - in production use proper AES decryption
    # Simple XOR decryption for placeholder (matches encrypt_data)
    decrypted = bytearray()
    key_len = len(key)
    
    for i, byte in enumerate(encrypted_data):
        decrypted.append(byte ^ key[i % key_len])
    
    return bytes(decrypted)


def generate_key() -> bytes:
    """
    Generate a random encryption key.
    
    Returns:
        Random 32-byte key
    """
    return secrets.token_bytes(32)


def verify_hmac(data: bytes, signature: str, key: bytes) -> bool:
    """
    Verify HMAC signature of data.
    
    Args:
        data: Data to verify
        signature: HMAC signature to verify
        key: HMAC key
        
    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = hmac.new(key, data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


def create_hmac(data: bytes, key: bytes) -> str:
    """
    Create HMAC signature for data.
    
    Args:
        data: Data to sign
        key: HMAC key
        
    Returns:
        HMAC signature as hexadecimal string
    """
    return hmac.new(key, data, hashlib.sha256).hexdigest()