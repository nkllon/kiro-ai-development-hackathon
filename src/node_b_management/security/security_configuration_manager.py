"""
Security Configuration Manager for Node B Management

Provides secure credential management, SSL/TLS configuration validation,
network authentication token handling, and security policy enforcement
for Node B instances.
"""

import os
import ssl
import json
import hashlib
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ..core.node_b_component import NodeBComponent
from ..core.interfaces import ISecurityConfiguration


@dataclass
class SecurityCredentials:
    """Secure credential storage with validation"""
    redis_password: str
    network_auth_token: str = ""
    ssl_cert_path: str = ""
    ssl_key_path: str = ""
    ssl_ca_path: str = ""
    encryption_key: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if credentials have expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def validate(self) -> List[str]:
        """Validate credential completeness and format"""
        issues = []
        
        if not self.redis_password:
            issues.append("Redis password is required")
        
        if len(self.redis_password) < 8:
            issues.append("Redis password must be at least 8 characters")
        
        if self.ssl_cert_path and not Path(self.ssl_cert_path).exists():
            issues.append(f"SSL certificate file not found: {self.ssl_cert_path}")
        
        if self.ssl_key_path and not Path(self.ssl_key_path).exists():
            issues.append(f"SSL key file not found: {self.ssl_key_path}")
        
        if self.ssl_ca_path and not Path(self.ssl_ca_path).exists():
            issues.append(f"SSL CA file not found: {self.ssl_ca_path}")
        
        return issues


@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    enforce_ssl: bool = True
    require_auth_tokens: bool = True
    audit_all_communications: bool = True
    encrypt_local_storage: bool = True
    max_failed_auth_attempts: int = 5
    auth_token_expiry_hours: int = 24
    password_min_length: int = 8
    require_certificate_validation: bool = True
    allowed_cipher_suites: List[str] = field(default_factory=lambda: [
        'TLS_AES_256_GCM_SHA384',
        'TLS_CHACHA20_POLY1305_SHA256',
        'TLS_AES_128_GCM_SHA256'
    ])
    
    def validate(self) -> List[str]:
        """Validate security policy configuration"""
        issues = []
        
        if self.max_failed_auth_attempts < 1:
            issues.append("max_failed_auth_attempts must be at least 1")
        
        if self.auth_token_expiry_hours < 1:
            issues.append("auth_token_expiry_hours must be at least 1")
        
        if self.password_min_length < 8:
            issues.append("password_min_length should be at least 8")
        
        return issues


@dataclass
class SecurityViolation:
    """Security violation record"""
    violation_id: str
    node_id: str
    violation_type: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    timestamp: datetime
    source_ip: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            "violation_id": self.violation_id,
            "node_id": self.node_id,
            "violation_type": self.violation_type,
            "description": self.description,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "source_ip": self.source_ip,
            "additional_data": self.additional_data,
            "resolved": self.resolved
        }


class SecurityConfigurationManager(NodeBComponent, ISecurityConfiguration):
    """
    Security Configuration Manager for Node B instances
    
    Provides comprehensive security management including credential handling,
    SSL/TLS configuration, authentication tokens, and security policy enforcement.
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7
    """

    def __init__(self, node_id: str = None):
        """
        Initialize Security Configuration Manager
        
        Args:
            node_id: Node B instance ID for security context
        """
        super().__init__("security_config_manager", node_id)
        
        # Security state
        self._credentials: Optional[SecurityCredentials] = None
        self._security_policy: Optional[SecurityPolicy] = None
        self._encryption_key: Optional[bytes] = None
        self._cipher_suite: Optional[Fernet] = None
        
        # Security monitoring
        self._security_violations: List[SecurityViolation] = []
        self._failed_auth_attempts: Dict[str, int] = {}
        self._audit_log: List[Dict[str, Any]] = []
        
        # SSL context cache
        self._ssl_context: Optional[ssl.SSLContext] = None
        self._ssl_context_created_at: Optional[datetime] = None
        
        self._logger.info(f"SecurityConfigurationManager initialized for node {self.node_id}")

    async def load_credentials(self) -> Dict[str, str]:
        """
        Load credentials from environment variables
        
        Returns:
            Dict[str, str]: Loaded credentials (sanitized for logging)
            
        Requirements: 4.1, 4.2
        """
        try:
            # Load credentials from environment variables - NEVER hardcode
            redis_password = os.getenv('REDIS_PASSWORD') or os.getenv('BEAST_MODE_REDIS_PASSWORD')
            
            if not redis_password:
                raise ValueError(
                    "Redis password must be set in environment variables. "
                    "Set REDIS_PASSWORD or BEAST_MODE_REDIS_PASSWORD"
                )
            
            # Load other security credentials
            network_auth_token = os.getenv('NODE_B_AUTH_TOKEN', '')
            ssl_cert_path = os.getenv('NODE_B_SSL_CERT_PATH', '')
            ssl_key_path = os.getenv('NODE_B_SSL_KEY_PATH', '')
            ssl_ca_path = os.getenv('NODE_B_SSL_CA_PATH', '')
            encryption_key = os.getenv('NODE_B_ENCRYPTION_KEY', '')
            
            # Create credentials object
            self._credentials = SecurityCredentials(
                redis_password=redis_password,
                network_auth_token=network_auth_token,
                ssl_cert_path=ssl_cert_path,
                ssl_key_path=ssl_key_path,
                ssl_ca_path=ssl_ca_path,
                encryption_key=encryption_key
            )
            
            # Validate credentials
            validation_issues = self._credentials.validate()
            if validation_issues:
                self._logger.warning(f"Credential validation issues: {validation_issues}")
                for issue in validation_issues:
                    await self._record_security_violation(
                        "credential_validation",
                        f"Credential validation failed: {issue}",
                        "medium"
                    )
            
            # Setup encryption if key is provided
            if encryption_key:
                await self._setup_encryption(encryption_key)
            
            # Audit log credential loading
            await self._audit_log_event("credentials_loaded", {
                "has_redis_password": bool(redis_password),
                "has_auth_token": bool(network_auth_token),
                "has_ssl_cert": bool(ssl_cert_path),
                "validation_issues_count": len(validation_issues)
            })
            
            self._logger.info("Security credentials loaded successfully")
            
            # Return sanitized credential info for logging
            return {
                "redis_password": "***REDACTED***" if redis_password else "",
                "network_auth_token": "***REDACTED***" if network_auth_token else "",
                "ssl_cert_path": ssl_cert_path,
                "ssl_key_path": ssl_key_path,
                "ssl_ca_path": ssl_ca_path,
                "encryption_key": "***REDACTED***" if encryption_key else "",
                "loaded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self._increment_error_count()
            await self._record_security_violation(
                "credential_loading_failed",
                f"Failed to load credentials: {str(e)}",
                "high"
            )
            self._logger.error(f"Failed to load security credentials: {e}")
            raise

    async def validate_ssl_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate SSL/TLS configuration
        
        Args:
            config: SSL/TLS configuration to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
            
        Requirements: 4.2, 4.3
        """
        try:
            validation_results = {
                "cert_file_exists": False,
                "key_file_exists": False,
                "ca_file_exists": False,
                "cert_key_match": False,
                "cert_not_expired": False,
                "ssl_context_valid": False
            }
            
            # Check certificate file
            cert_path = config.get('cert_path') or (self._credentials.ssl_cert_path if self._credentials else '')
            if cert_path and Path(cert_path).exists():
                validation_results["cert_file_exists"] = True
                
                # Check certificate expiry
                try:
                    from cryptography import x509
                    from cryptography.hazmat.backends import default_backend
                    
                    with open(cert_path, 'rb') as cert_file:
                        cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
                        if cert.not_valid_after > datetime.now():
                            validation_results["cert_not_expired"] = True
                        else:
                            await self._record_security_violation(
                                "ssl_cert_expired",
                                f"SSL certificate expired: {cert.not_valid_after}",
                                "high"
                            )
                except Exception as e:
                    self._logger.warning(f"Could not validate certificate expiry: {e}")
            
            # Check key file
            key_path = config.get('key_path') or (self._credentials.ssl_key_path if self._credentials else '')
            if key_path and Path(key_path).exists():
                validation_results["key_file_exists"] = True
            
            # Check CA file
            ca_path = config.get('ca_path') or (self._credentials.ssl_ca_path if self._credentials else '')
            if ca_path and Path(ca_path).exists():
                validation_results["ca_file_exists"] = True
            
            # Validate SSL context creation
            try:
                ssl_context = await self._create_ssl_context(config)
                if ssl_context:
                    validation_results["ssl_context_valid"] = True
                    self._ssl_context = ssl_context
                    self._ssl_context_created_at = datetime.now()
            except Exception as e:
                self._logger.error(f"SSL context validation failed: {e}")
                await self._record_security_violation(
                    "ssl_context_invalid",
                    f"SSL context creation failed: {str(e)}",
                    "high"
                )
            
            # Overall validation result
            is_valid = all([
                validation_results["cert_file_exists"],
                validation_results["key_file_exists"],
                validation_results["cert_not_expired"],
                validation_results["ssl_context_valid"]
            ])
            
            # Audit log SSL validation
            await self._audit_log_event("ssl_config_validated", {
                "validation_results": validation_results,
                "is_valid": is_valid,
                "config_provided": bool(config)
            })
            
            if is_valid:
                self._logger.info("SSL/TLS configuration validation passed")
            else:
                self._logger.warning(f"SSL/TLS configuration validation failed: {validation_results}")
            
            return is_valid
            
        except Exception as e:
            self._increment_error_count()
            await self._record_security_violation(
                "ssl_validation_error",
                f"SSL validation error: {str(e)}",
                "medium"
            )
            self._logger.error(f"SSL configuration validation error: {e}")
            return False

    async def enforce_security_policies(self, node_id: str) -> bool:
        """
        Enforce security policies and audit logging
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            bool: True if policies enforced successfully, False otherwise
            
        Requirements: 4.4, 4.6, 4.7
        """
        try:
            # Load security policy if not already loaded
            if self._security_policy is None:
                self._security_policy = await self._load_security_policy()
            
            policy_enforcement_results = {
                "ssl_enforcement": False,
                "auth_token_validation": False,
                "audit_logging_enabled": False,
                "local_storage_encryption": False,
                "certificate_validation": False
            }
            
            # Enforce SSL requirement
            if self._security_policy.enforce_ssl:
                if self._ssl_context is not None:
                    policy_enforcement_results["ssl_enforcement"] = True
                else:
                    await self._record_security_violation(
                        "ssl_policy_violation",
                        "SSL required by policy but not configured",
                        "high"
                    )
            else:
                policy_enforcement_results["ssl_enforcement"] = True
            
            # Enforce authentication token requirement
            if self._security_policy.require_auth_tokens:
                if self._credentials and self._credentials.network_auth_token:
                    policy_enforcement_results["auth_token_validation"] = True
                else:
                    await self._record_security_violation(
                        "auth_token_policy_violation",
                        "Authentication token required by policy but not configured",
                        "high"
                    )
            else:
                policy_enforcement_results["auth_token_validation"] = True
            
            # Enable audit logging
            if self._security_policy.audit_all_communications:
                policy_enforcement_results["audit_logging_enabled"] = True
                # Audit logging is always enabled in this implementation
            
            # Enforce local storage encryption
            if self._security_policy.encrypt_local_storage:
                if self._cipher_suite is not None:
                    policy_enforcement_results["local_storage_encryption"] = True
                else:
                    await self._record_security_violation(
                        "encryption_policy_violation",
                        "Local storage encryption required by policy but not configured",
                        "medium"
                    )
            else:
                policy_enforcement_results["local_storage_encryption"] = True
            
            # Enforce certificate validation
            if self._security_policy.require_certificate_validation:
                if self._ssl_context and self._ssl_context.check_hostname:
                    policy_enforcement_results["certificate_validation"] = True
                else:
                    await self._record_security_violation(
                        "cert_validation_policy_violation",
                        "Certificate validation required by policy but not enabled",
                        "medium"
                    )
            else:
                policy_enforcement_results["certificate_validation"] = True
            
            # Overall enforcement result
            all_policies_enforced = all(policy_enforcement_results.values())
            
            # Audit log policy enforcement
            await self._audit_log_event("security_policies_enforced", {
                "node_id": node_id,
                "enforcement_results": policy_enforcement_results,
                "all_policies_enforced": all_policies_enforced,
                "policy_config": {
                    "enforce_ssl": self._security_policy.enforce_ssl,
                    "require_auth_tokens": self._security_policy.require_auth_tokens,
                    "audit_all_communications": self._security_policy.audit_all_communications,
                    "encrypt_local_storage": self._security_policy.encrypt_local_storage
                }
            })
            
            if all_policies_enforced:
                self._logger.info(f"All security policies enforced successfully for node {node_id}")
            else:
                failed_policies = [k for k, v in policy_enforcement_results.items() if not v]
                self._logger.warning(f"Security policy enforcement failed for node {node_id}: {failed_policies}")
            
            return all_policies_enforced
            
        except Exception as e:
            self._increment_error_count()
            await self._record_security_violation(
                "policy_enforcement_error",
                f"Security policy enforcement error: {str(e)}",
                "high"
            )
            self._logger.error(f"Security policy enforcement error: {e}")
            return False

    async def detect_security_violations(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Detect security violations and isolation requirements
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            List[Dict[str, Any]]: List of detected security violations
            
        Requirements: 4.5, 4.6
        """
        try:
            current_violations = []
            
            # Check for expired credentials
            if self._credentials and self._credentials.is_expired():
                violation = await self._record_security_violation(
                    "expired_credentials",
                    "Node credentials have expired",
                    "high"
                )
                current_violations.append(violation.to_dict())
            
            # Check for excessive failed authentication attempts
            failed_attempts = self._failed_auth_attempts.get(node_id, 0)
            if failed_attempts >= self._security_policy.max_failed_auth_attempts:
                violation = await self._record_security_violation(
                    "excessive_auth_failures",
                    f"Excessive authentication failures: {failed_attempts}",
                    "critical"
                )
                current_violations.append(violation.to_dict())
            
            # Check SSL context expiry
            if self._ssl_context_created_at:
                ssl_age = datetime.now() - self._ssl_context_created_at
                if ssl_age > timedelta(hours=24):  # SSL context should be refreshed daily
                    violation = await self._record_security_violation(
                        "stale_ssl_context",
                        f"SSL context is {ssl_age.total_seconds()/3600:.1f} hours old",
                        "medium"
                    )
                    current_violations.append(violation.to_dict())
            
            # Check for unresolved security violations
            unresolved_violations = [v for v in self._security_violations if not v.resolved]
            critical_unresolved = [v for v in unresolved_violations if v.severity == "critical"]
            
            if len(critical_unresolved) > 0:
                violation = await self._record_security_violation(
                    "unresolved_critical_violations",
                    f"Critical security violations remain unresolved: {len(critical_unresolved)}",
                    "critical"
                )
                current_violations.append(violation.to_dict())
            
            # Audit log violation detection
            await self._audit_log_event("security_violations_detected", {
                "node_id": node_id,
                "violations_found": len(current_violations),
                "total_unresolved": len(unresolved_violations),
                "critical_unresolved": len(critical_unresolved)
            })
            
            if current_violations:
                self._logger.warning(f"Detected {len(current_violations)} security violations for node {node_id}")
            else:
                self._logger.debug(f"No new security violations detected for node {node_id}")
            
            return current_violations
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Security violation detection error: {e}")
            return []

    async def get_authentication_token(self, node_id: str) -> Optional[str]:
        """
        Get or generate authentication token for network communications
        
        Args:
            node_id: Node B instance ID
            
        Returns:
            Optional[str]: Authentication token if available
        """
        try:
            if self._credentials and self._credentials.network_auth_token:
                # Return existing token
                return self._credentials.network_auth_token
            
            # Generate new token if none exists
            token = await self._generate_auth_token(node_id)
            
            # Update credentials
            if self._credentials:
                self._credentials.network_auth_token = token
            
            await self._audit_log_event("auth_token_generated", {
                "node_id": node_id,
                "token_length": len(token) if token else 0
            })
            
            return token
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to get authentication token: {e}")
            return None

    async def validate_network_authentication(self, token: str, source_node: str) -> bool:
        """
        Validate network authentication token
        
        Args:
            token: Authentication token to validate
            source_node: Source node ID for the token
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            # Basic token validation
            if not token or len(token) < 32:
                self._failed_auth_attempts[source_node] = self._failed_auth_attempts.get(source_node, 0) + 1
                await self._record_security_violation(
                    "invalid_auth_token",
                    f"Invalid authentication token from {source_node}",
                    "medium"
                )
                return False
            
            # Token format validation (should be base64 encoded)
            try:
                decoded = base64.b64decode(token)
                if len(decoded) < 16:
                    raise ValueError("Token too short")
            except Exception:
                self._failed_auth_attempts[source_node] = self._failed_auth_attempts.get(source_node, 0) + 1
                await self._record_security_violation(
                    "malformed_auth_token",
                    f"Malformed authentication token from {source_node}",
                    "medium"
                )
                return False
            
            # Reset failed attempts on successful validation
            if source_node in self._failed_auth_attempts:
                del self._failed_auth_attempts[source_node]
            
            await self._audit_log_event("auth_token_validated", {
                "source_node": source_node,
                "token_valid": True
            })
            
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Authentication validation error: {e}")
            return False

    async def encrypt_sensitive_data(self, data: str) -> Optional[str]:
        """
        Encrypt sensitive data for local storage
        
        Args:
            data: Data to encrypt
            
        Returns:
            Optional[str]: Encrypted data if successful, None otherwise
        """
        try:
            if not self._cipher_suite:
                self._logger.warning("Encryption not available - no cipher suite configured")
                return None
            
            encrypted_data = self._cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Data encryption failed: {e}")
            return None

    async def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """
        Decrypt sensitive data from local storage
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Optional[str]: Decrypted data if successful, None otherwise
        """
        try:
            if not self._cipher_suite:
                self._logger.warning("Decryption not available - no cipher suite configured")
                return None
            
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = self._cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Data decryption failed: {e}")
            return None

    async def get_security_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get security audit log entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List[Dict[str, Any]]: Audit log entries
        """
        return self._audit_log[-limit:] if self._audit_log else []

    async def get_security_violations(self, resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Get security violations
        
        Args:
            resolved: Filter by resolution status (None for all)
            
        Returns:
            List[Dict[str, Any]]: Security violations
        """
        violations = self._security_violations
        
        if resolved is not None:
            violations = [v for v in violations if v.resolved == resolved]
        
        return [v.to_dict() for v in violations]

    async def resolve_security_violation(self, violation_id: str) -> bool:
        """
        Mark a security violation as resolved
        
        Args:
            violation_id: ID of the violation to resolve
            
        Returns:
            bool: True if resolved successfully, False otherwise
        """
        try:
            for violation in self._security_violations:
                if violation.violation_id == violation_id:
                    violation.resolved = True
                    
                    await self._audit_log_event("security_violation_resolved", {
                        "violation_id": violation_id,
                        "violation_type": violation.violation_type,
                        "severity": violation.severity
                    })
                    
                    self._logger.info(f"Security violation resolved: {violation_id}")
                    return True
            
            self._logger.warning(f"Security violation not found: {violation_id}")
            return False
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to resolve security violation: {e}")
            return False

    # Private helper methods

    async def _setup_encryption(self, encryption_key: str):
        """Setup encryption cipher suite"""
        try:
            # Derive key from provided key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'node_b_salt',  # In production, use random salt
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
            self._encryption_key = key
            self._cipher_suite = Fernet(key)
            
            self._logger.info("Encryption cipher suite initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to setup encryption: {e}")
            raise

    async def _create_ssl_context(self, config: Dict[str, Any]) -> Optional[ssl.SSLContext]:
        """Create SSL context from configuration"""
        try:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            
            # Configure certificate verification
            if self._security_policy and self._security_policy.require_certificate_validation:
                context.check_hostname = True
                context.verify_mode = ssl.CERT_REQUIRED
            else:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            # Load certificates if provided
            cert_path = config.get('cert_path') or (self._credentials.ssl_cert_path if self._credentials else '')
            key_path = config.get('key_path') or (self._credentials.ssl_key_path if self._credentials else '')
            ca_path = config.get('ca_path') or (self._credentials.ssl_ca_path if self._credentials else '')
            
            if cert_path and key_path:
                context.load_cert_chain(cert_path, key_path)
            
            if ca_path:
                context.load_verify_locations(ca_path)
            
            return context
            
        except Exception as e:
            self._logger.error(f"Failed to create SSL context: {e}")
            return None

    async def _load_security_policy(self) -> SecurityPolicy:
        """Load security policy from environment or defaults"""
        try:
            policy = SecurityPolicy(
                enforce_ssl=os.getenv('NODE_B_ENFORCE_SSL', 'true').lower() == 'true',
                require_auth_tokens=os.getenv('NODE_B_REQUIRE_AUTH_TOKENS', 'true').lower() == 'true',
                audit_all_communications=os.getenv('NODE_B_AUDIT_ALL_COMMS', 'true').lower() == 'true',
                encrypt_local_storage=os.getenv('NODE_B_ENCRYPT_LOCAL_STORAGE', 'true').lower() == 'true',
                max_failed_auth_attempts=int(os.getenv('NODE_B_MAX_FAILED_AUTH', '5')),
                auth_token_expiry_hours=int(os.getenv('NODE_B_AUTH_TOKEN_EXPIRY_HOURS', '24')),
                password_min_length=int(os.getenv('NODE_B_PASSWORD_MIN_LENGTH', '8')),
                require_certificate_validation=os.getenv('NODE_B_REQUIRE_CERT_VALIDATION', 'true').lower() == 'true'
            )
            
            # Validate policy
            validation_issues = policy.validate()
            if validation_issues:
                self._logger.warning(f"Security policy validation issues: {validation_issues}")
            
            self._logger.info("Security policy loaded successfully")
            return policy
            
        except Exception as e:
            self._logger.error(f"Failed to load security policy: {e}")
            return SecurityPolicy()  # Return default policy

    async def _generate_auth_token(self, node_id: str) -> str:
        """Generate authentication token for node"""
        try:
            # Create token data
            token_data = {
                "node_id": node_id,
                "issued_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=self._security_policy.auth_token_expiry_hours)).isoformat()
            }
            
            # Create token hash
            token_string = json.dumps(token_data, sort_keys=True)
            token_hash = hashlib.sha256(token_string.encode()).hexdigest()
            
            # Encode token
            token = base64.b64encode(f"{token_string}:{token_hash}".encode()).decode()
            
            return token
            
        except Exception as e:
            self._logger.error(f"Failed to generate auth token: {e}")
            raise

    async def _record_security_violation(self, violation_type: str, description: str, severity: str) -> SecurityViolation:
        """Record a security violation"""
        violation_id = hashlib.md5(f"{violation_type}:{description}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        violation = SecurityViolation(
            violation_id=violation_id,
            node_id=self.node_id,
            violation_type=violation_type,
            description=description,
            severity=severity,
            timestamp=datetime.now()
        )
        
        self._security_violations.append(violation)
        
        # Log violation
        self._logger.warning(f"Security violation recorded: {violation_type} - {description} (severity: {severity})")
        
        return violation

    async def _audit_log_event(self, event_type: str, event_data: Dict[str, Any]):
        """Record audit log event"""
        audit_entry = {
            "event_id": hashlib.md5(f"{event_type}:{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "node_id": self.node_id,
            "event_data": event_data
        }
        
        self._audit_log.append(audit_entry)
        
        # Keep audit log size manageable
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-500:]  # Keep last 500 entries
        
        self._logger.debug(f"Audit event recorded: {event_type}")

    def get_security_status(self) -> Dict[str, Any]:
        """
        Get comprehensive security status
        
        Returns:
            Dict[str, Any]: Security status information
        """
        return {
            "credentials_loaded": self._credentials is not None,
            "credentials_valid": self._credentials is not None and not self._credentials.is_expired(),
            "ssl_context_available": self._ssl_context is not None,
            "encryption_available": self._cipher_suite is not None,
            "security_policy_loaded": self._security_policy is not None,
            "total_violations": len(self._security_violations),
            "unresolved_violations": len([v for v in self._security_violations if not v.resolved]),
            "critical_violations": len([v for v in self._security_violations if v.severity == "critical" and not v.resolved]),
            "audit_log_entries": len(self._audit_log),
            "failed_auth_attempts": dict(self._failed_auth_attempts),
            "ssl_context_age_hours": (
                (datetime.now() - self._ssl_context_created_at).total_seconds() / 3600
                if self._ssl_context_created_at else None
            )
        }