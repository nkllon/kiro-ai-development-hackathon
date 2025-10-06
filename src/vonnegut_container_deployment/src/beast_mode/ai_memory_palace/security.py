"""
Security and Privacy Protection for AI Memory Palace.

Implements sensitive information filtering, encryption at rest, access logging,
and retention policies for secure context management.
"""

import re
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid

from src.beast_mode.core.beastly_module import BeastlyModule
from .models import SessionContext, ContextEvent


class SensitivityLevel(Enum):
    """Sensitivity levels for information classification"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"


class RedactionType(Enum):
    """Types of redaction applied to sensitive data"""
    MASK = "mask"  # Replace with asterisks
    HASH = "hash"  # Replace with hash
    REMOVE = "remove"  # Remove entirely
    TOKEN = "token"  # Replace with token reference


@dataclass
class SensitivePattern:
    """Pattern for detecting sensitive information"""
    name: str
    pattern: str
    sensitivity: SensitivityLevel
    redaction_type: RedactionType
    description: str


@dataclass
class RedactionResult:
    """Result of data redaction operation"""
    original_text: str
    redacted_text: str
    redactions_applied: List[Dict[str, Any]]
    sensitivity_score: float


@dataclass
class AccessLogEntry:
    """Access log entry for audit trail"""
    timestamp: datetime
    user_id: Optional[str]
    session_id: str
    operation: str
    resource: str
    success: bool
    details: Dict[str, Any]


class ContextSecurityManager(BeastlyModule):
    """Security and privacy protection for context data"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        super().__init__()
        
        # Encryption setup
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self._setup_encryption()
        
        # Sensitive patterns for detection
        self.sensitive_patterns = self._initialize_sensitive_patterns()
        
        # Access logging
        self._access_log: List[AccessLogEntry] = []
        self._max_log_entries = 10000
        
        # Security metrics
        self._redactions_performed = 0
        self._access_attempts = 0
        self._access_denied = 0
        self._encryption_operations = 0
        self._retention_cleanups = 0
        
        # Token store for reversible redaction
        self._token_store: Dict[str, str] = {}
        
        self.logger.info("🔒 ContextSecurityManager initialized with encryption")
    
    def filter_sensitive_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and redact sensitive information from context data"""
        try:
            # Create deep copy for modification
            filtered_data = json.loads(json.dumps(data))
            
            # Apply redaction to all text fields
            redaction_summary = []
            
            def redact_recursive(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        obj[key] = redact_recursive(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        obj[i] = redact_recursive(item, f"{path}[{i}]")
                elif isinstance(obj, str):
                    redaction_result = self._redact_text(obj)
                    if redaction_result.redactions_applied:
                        redaction_summary.extend([
                            {**redaction, "field_path": path} 
                            for redaction in redaction_result.redactions_applied
                        ])
                    return redaction_result.redacted_text
                return obj
            
            redact_recursive(filtered_data)
            
            # Log redaction summary
            if redaction_summary:
                self._redactions_performed += len(redaction_summary)
                self.logger.info(f"🔒 Applied {len(redaction_summary)} redactions to context data")
                
                # Emit security observation
                self.emit_observation({
                    "type": "sensitive_data_redacted",
                    "redaction_count": len(redaction_summary),
                    "redaction_types": list(set(r["type"] for r in redaction_summary)),
                    "timestamp": datetime.now().isoformat()
                })
            
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"💥 Error filtering sensitive information: {e}")
            return data  # Return original data if filtering fails
    
    def _redact_text(self, text: str) -> RedactionResult:
        """Redact sensitive information from text"""
        redacted_text = text
        redactions_applied = []
        sensitivity_score = 0.0
        
        for pattern in self.sensitive_patterns:
            matches = re.finditer(pattern.pattern, text, re.IGNORECASE)
            
            for match in matches:
                original_value = match.group()
                
                # Apply redaction based on type
                if pattern.redaction_type == RedactionType.MASK:
                    redacted_value = "*" * len(original_value)
                elif pattern.redaction_type == RedactionType.HASH:
                    redacted_value = f"[HASH:{hashlib.sha256(original_value.encode()).hexdigest()[:8]}]"
                elif pattern.redaction_type == RedactionType.REMOVE:
                    redacted_value = "[REDACTED]"
                elif pattern.redaction_type == RedactionType.TOKEN:
                    token = str(uuid.uuid4())[:8]
                    self._token_store[token] = original_value
                    redacted_value = f"[TOKEN:{token}]"
                else:
                    redacted_value = "[REDACTED]"
                
                # Replace in text
                redacted_text = redacted_text.replace(original_value, redacted_value)
                
                # Record redaction
                redactions_applied.append({
                    "pattern_name": pattern.name,
                    "type": pattern.redaction_type.value,
                    "sensitivity": pattern.sensitivity.value,
                    "original_length": len(original_value),
                    "position": match.start()
                })
                
                # Update sensitivity score
                sensitivity_score = max(sensitivity_score, self._get_sensitivity_score(pattern.sensitivity))
        
        return RedactionResult(
            original_text=text,
            redacted_text=redacted_text,
            redactions_applied=redactions_applied,
            sensitivity_score=sensitivity_score
        )
    
    def encrypt_context_data(self, context_data: str) -> str:
        """Encrypt context data for storage"""
        try:
            if not self.cipher_suite:
                self.logger.warning("⚠️ Encryption not available, storing data in plain text")
                return context_data
            
            # Encrypt the data
            encrypted_data = self.cipher_suite.encrypt(context_data.encode())
            self._encryption_operations += 1
            
            # Emit encryption observation
            self.emit_observation({
                "type": "context_data_encrypted",
                "data_size_bytes": len(context_data),
                "encrypted_size_bytes": len(encrypted_data),
                "timestamp": datetime.now().isoformat()
            })
            
            return encrypted_data.decode('latin1')  # Store as string
            
        except Exception as e:
            self.logger.error(f"💥 Encryption error: {e}")
            return context_data  # Fallback to plain text
    
    def decrypt_context_data(self, encrypted_data: str) -> str:
        """Decrypt context data from storage"""
        try:
            if not self.cipher_suite:
                return encrypted_data  # Return as-is if no encryption
            
            # Decrypt the data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode('latin1'))
            self._encryption_operations += 1
            
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"💥 Decryption error: {e}")
            return encrypted_data  # Return as-is if decryption fails
    
    def log_access(self, user_id: Optional[str], session_id: str, operation: str, 
                   resource: str, success: bool, details: Dict[str, Any] = None):
        """Log access attempt for audit trail"""
        try:
            log_entry = AccessLogEntry(
                timestamp=datetime.now(),
                user_id=user_id,
                session_id=session_id,
                operation=operation,
                resource=resource,
                success=success,
                details=details or {}
            )
            
            self._access_log.append(log_entry)
            self._access_attempts += 1
            
            if not success:
                self._access_denied += 1
            
            # Trim log if too large
            if len(self._access_log) > self._max_log_entries:
                self._access_log = self._access_log[-self._max_log_entries:]
            
            # Emit access log observation
            self.emit_observation({
                "type": "context_access_logged",
                "operation": operation,
                "resource": resource,
                "success": success,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": log_entry.timestamp.isoformat()
            })
            
            # Log security events
            if not success:
                self.logger.warning(f"🚫 Access denied: {operation} on {resource} by {user_id}")
            else:
                self.logger.debug(f"✅ Access granted: {operation} on {resource} by {user_id}")
                
        except Exception as e:
            self.logger.error(f"💥 Access logging error: {e}")
    
    def apply_retention_policy(self, retention_days: int = 90) -> int:
        """Apply retention policy and purge old data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # This would integrate with the ContextRegistry to purge old data
            # For now, we'll simulate the operation
            
            purged_count = 0
            
            # Purge old access logs
            original_log_count = len(self._access_log)
            self._access_log = [
                entry for entry in self._access_log 
                if entry.timestamp > cutoff_date
            ]
            log_purged = original_log_count - len(self._access_log)
            
            # Purge old tokens
            # (In a real implementation, tokens would have timestamps)
            
            purged_count += log_purged
            self._retention_cleanups += 1
            
            self.logger.info(f"🧹 Retention policy applied: {purged_count} items purged")
            
            # Emit retention observation
            self.emit_observation({
                "type": "retention_policy_applied",
                "retention_days": retention_days,
                "items_purged": purged_count,
                "cutoff_date": cutoff_date.isoformat(),
                "timestamp": datetime.now().isoformat()
            })
            
            return purged_count
            
        except Exception as e:
            self.logger.error(f"💥 Retention policy error: {e}")
            return 0
    
    def validate_access_permissions(self, user_id: Optional[str], session_id: str, 
                                  operation: str, resource: str) -> bool:
        """Validate access permissions for context operations"""
        try:
            # Basic permission validation
            # In a real implementation, this would check against user roles, ACLs, etc.
            
            # For now, allow all operations but log them
            allowed = True
            
            # Log the access attempt
            self.log_access(user_id, session_id, operation, resource, allowed)
            
            return allowed
            
        except Exception as e:
            self.logger.error(f"💥 Permission validation error: {e}")
            self.log_access(user_id, session_id, operation, resource, False, {"error": str(e)})
            return False
    
    def get_access_audit_trail(self, session_id: Optional[str] = None, 
                             hours: int = 24) -> List[Dict[str, Any]]:
        """Get access audit trail for security review"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            filtered_logs = [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "user_id": entry.user_id,
                    "session_id": entry.session_id,
                    "operation": entry.operation,
                    "resource": entry.resource,
                    "success": entry.success,
                    "details": entry.details
                }
                for entry in self._access_log
                if entry.timestamp > cutoff_time and (not session_id or entry.session_id == session_id)
            ]
            
            return filtered_logs
            
        except Exception as e:
            self.logger.error(f"💥 Audit trail error: {e}")
            return []
    
    def _initialize_sensitive_patterns(self) -> List[SensitivePattern]:
        """Initialize patterns for detecting sensitive information"""
        return [
            # API Keys and Tokens
            SensitivePattern(
                name="api_key",
                pattern=r'\b[A-Za-z0-9]{32,}\b',
                sensitivity=SensitivityLevel.SECRET,
                redaction_type=RedactionType.HASH,
                description="API keys and long tokens"
            ),
            
            # Email addresses
            SensitivePattern(
                name="email",
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                sensitivity=SensitivityLevel.CONFIDENTIAL,
                redaction_type=RedactionType.MASK,
                description="Email addresses"
            ),
            
            # Phone numbers
            SensitivePattern(
                name="phone",
                pattern=r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                sensitivity=SensitivityLevel.CONFIDENTIAL,
                redaction_type=RedactionType.MASK,
                description="Phone numbers"
            ),
            
            # Credit card numbers
            SensitivePattern(
                name="credit_card",
                pattern=r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                sensitivity=SensitivityLevel.SECRET,
                redaction_type=RedactionType.REMOVE,
                description="Credit card numbers"
            ),
            
            # Social Security Numbers
            SensitivePattern(
                name="ssn",
                pattern=r'\b\d{3}-\d{2}-\d{4}\b',
                sensitivity=SensitivityLevel.SECRET,
                redaction_type=RedactionType.REMOVE,
                description="Social Security Numbers"
            ),
            
            # IP Addresses (internal)
            SensitivePattern(
                name="internal_ip",
                pattern=r'\b(?:10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\b',
                sensitivity=SensitivityLevel.INTERNAL,
                redaction_type=RedactionType.TOKEN,
                description="Internal IP addresses"
            ),
            
            # Passwords (common patterns)
            SensitivePattern(
                name="password",
                pattern=r'(?i)(?:password|passwd|pwd)[\s=:]+[^\s]+',
                sensitivity=SensitivityLevel.SECRET,
                redaction_type=RedactionType.REMOVE,
                description="Password fields"
            ),
            
            # AWS Access Keys
            SensitivePattern(
                name="aws_access_key",
                pattern=r'\bAKIA[0-9A-Z]{16}\b',
                sensitivity=SensitivityLevel.SECRET,
                redaction_type=RedactionType.HASH,
                description="AWS Access Keys"
            ),
            
            # GitHub Tokens
            SensitivePattern(
                name="github_token",
                pattern=r'\bghp_[A-Za-z0-9]{36}\b',
                sensitivity=SensitivityLevel.SECRET,
                redaction_type=RedactionType.HASH,
                description="GitHub Personal Access Tokens"
            )
        ]
    
    def _get_sensitivity_score(self, sensitivity: SensitivityLevel) -> float:
        """Get numeric sensitivity score"""
        scores = {
            SensitivityLevel.PUBLIC: 0.0,
            SensitivityLevel.INTERNAL: 0.3,
            SensitivityLevel.CONFIDENTIAL: 0.7,
            SensitivityLevel.SECRET: 1.0
        }
        return scores.get(sensitivity, 0.0)
    
    def _generate_encryption_key(self) -> str:
        """Generate encryption key from environment or create new one"""
        # Try to get key from environment
        env_key = os.getenv('CONTEXT_ENCRYPTION_KEY')
        if env_key:
            return env_key
        
        # Generate new key (in production, this should be stored securely)
        import secrets
        key = secrets.token_urlsafe(32)
        
        self.logger.warning("🔑 Generated new encryption key - store securely!")
        return key
    
    def _setup_encryption(self):
        """Setup encryption cipher"""
        try:
            from cryptography.fernet import Fernet
            import base64
            
            # Create key from our encryption key
            key_bytes = self.encryption_key.encode()[:32].ljust(32, b'0')
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            
            self.cipher_suite = Fernet(fernet_key)
            self.logger.info("🔐 Encryption initialized successfully")
            
        except ImportError:
            self.logger.warning("⚠️ Cryptography library not available - encryption disabled")
            self.cipher_suite = None
        except Exception as e:
            self.logger.error(f"💥 Encryption setup error: {e}")
            self.cipher_suite = None
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        return {
            "redactions_performed": self._redactions_performed,
            "access_attempts": self._access_attempts,
            "access_denied": self._access_denied,
            "access_success_rate": (self._access_attempts - self._access_denied) / max(1, self._access_attempts),
            "encryption_operations": self._encryption_operations,
            "retention_cleanups": self._retention_cleanups,
            "active_tokens": len(self._token_store),
            "audit_log_entries": len(self._access_log),
            "encryption_enabled": self.cipher_suite is not None,
            "sensitive_patterns": len(self.sensitive_patterns)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for security manager"""
        try:
            stats = self.get_security_stats()
            
            return {
                "status": "healthy",
                "encryption_available": self.cipher_suite is not None,
                "security_stats": stats,
                "patterns_loaded": len(self.sensitive_patterns)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        stats = self.get_security_stats()
        
        return {
            "context_security_redactions_total": self._redactions_performed,
            "context_security_access_attempts_total": self._access_attempts,
            "context_security_access_denied_total": self._access_denied,
            "context_security_access_success_rate": stats["access_success_rate"],
            "context_security_encryption_operations_total": self._encryption_operations,
            "context_security_retention_cleanups_total": self._retention_cleanups,
            "context_security_active_tokens": len(self._token_store),
            "context_security_audit_log_entries": len(self._access_log),
            "context_security_encryption_enabled": 1 if self.cipher_suite else 0
        }