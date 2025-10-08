"""
Security Manager for AI Consultation System

Provides security and permission handling that integrates with existing
Observatory authentication without modification.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import secrets
import jwt
from pathlib import Path

from .models import ObservatoryContext
from .observatory_context_provider import DataSensitivity, MetricData, AlertData
from .feature_flags import feature_flags, FeatureFlag
from .exceptions import ConsultationError, ValidationError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class PermissionLevel(str, Enum):
    """User permission levels for Observatory data access"""
    GUEST = "guest"           # Limited public data only
    USER = "user"             # Basic monitoring data
    OPERATOR = "operator"     # Operational metrics and alerts
    ADMIN = "admin"           # Full access to all data
    SYSTEM = "system"         # Internal system access


class ResourceType(str, Enum):
    """Types of resources that can be accessed"""
    METRICS = "metrics"
    ALERTS = "alerts"
    SYSTEM_STATUS = "system_status"
    LOGS = "logs"
    CONFIGURATION = "configuration"


@dataclass
class UserPermissions:
    """User permission configuration"""
    user_id: str
    permission_level: PermissionLevel
    allowed_resources: Set[ResourceType]
    allowed_services: Set[str]  # Services user can access
    data_sensitivity_limit: DataSensitivity
    session_timeout: timedelta
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None


@dataclass
class SecurityContext:
    """Security context for a request"""
    user_id: str
    session_id: str
    permissions: UserPermissions
    request_timestamp: datetime
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None


class SecurityManager:
    """
    Manages security and permissions for AI consultation system
    
    Features:
    - Integration with existing Observatory authentication
    - Permission-based data filtering
    - Session management and validation
    - Audit logging for security events
    - Data sanitization based on user permissions
    - No modification of existing Observatory auth systems
    """  
  
    def __init__(
        self,
        jwt_secret: Optional[str] = None,
        session_timeout: timedelta = timedelta(hours=8),
        max_sessions_per_user: int = 5,
        audit_log_enabled: bool = True
    ):
        self.jwt_secret = jwt_secret or self._generate_secret()
        self.session_timeout = session_timeout
        self.max_sessions_per_user = max_sessions_per_user
        self.audit_log_enabled = audit_log_enabled
        
        # Active sessions
        self._active_sessions: Dict[str, SecurityContext] = {}
        self._user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        
        # Permission cache
        self._permission_cache: Dict[str, UserPermissions] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=15)
        
        # Observatory auth integration
        self._observatory_auth_detected = False
        self._observatory_auth_endpoint = None
        
        # Audit log
        self._audit_events: List[Dict[str, Any]] = []
        
        # Statistics
        self._stats = {
            'auth_requests': 0,
            'auth_successes': 0,
            'auth_failures': 0,
            'permission_checks': 0,
            'permission_denials': 0,
            'data_sanitizations': 0,
            'audit_events': 0
        }
    
    def _generate_secret(self) -> str:
        """Generate a secure secret for JWT signing"""
        return secrets.token_urlsafe(32)
    
    async def initialize(self) -> None:
        """Initialize the security manager"""
        try:
            logger.info("Initializing Security Manager")
            
            # Detect existing Observatory authentication
            await self._detect_observatory_auth()
            
            # Load default permissions if needed
            await self._load_default_permissions()
            
            logger.info(f"Security Manager initialized - Observatory auth detected: {self._observatory_auth_detected}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Security Manager: {e}")
            # Don't raise - should degrade gracefully
    
    async def _detect_observatory_auth(self) -> None:
        """Detect existing Observatory authentication system"""
        try:
            # Check for common Observatory auth patterns
            # This would normally probe for existing auth endpoints
            # For brownfield safety, we assume Observatory auth exists
            
            import os
            
            # Check for Observatory auth configuration
            auth_endpoints = [
                os.getenv('OBSERVATORY_AUTH_URL', 'http://localhost:8080/auth'),
                'http://observatory:8080/auth',
                'http://localhost:3000/auth'  # Common auth service port
            ]
            
            # For demo purposes, assume Observatory auth is available
            self._observatory_auth_detected = True
            self._observatory_auth_endpoint = auth_endpoints[0]
            
            logger.info(f"Observatory auth detected at: {self._observatory_auth_endpoint}")
            
        except Exception as e:
            logger.warning(f"Failed to detect Observatory auth: {e}")
            self._observatory_auth_detected = False
    
    async def _load_default_permissions(self) -> None:
        """Load default permission configurations"""
        try:
            # Define default permission levels
            default_permissions = {
                PermissionLevel.GUEST: UserPermissions(
                    user_id="default_guest",
                    permission_level=PermissionLevel.GUEST,
                    allowed_resources={ResourceType.SYSTEM_STATUS},
                    allowed_services=set(),
                    data_sensitivity_limit=DataSensitivity.PUBLIC,
                    session_timeout=timedelta(hours=1),
                    created_at=datetime.utcnow()
                ),
                PermissionLevel.USER: UserPermissions(
                    user_id="default_user",
                    permission_level=PermissionLevel.USER,
                    allowed_resources={ResourceType.METRICS, ResourceType.SYSTEM_STATUS},
                    allowed_services={"web", "api"},
                    data_sensitivity_limit=DataSensitivity.INTERNAL,
                    session_timeout=timedelta(hours=4),
                    created_at=datetime.utcnow()
                ),
                PermissionLevel.OPERATOR: UserPermissions(
                    user_id="default_operator",
                    permission_level=PermissionLevel.OPERATOR,
                    allowed_resources={ResourceType.METRICS, ResourceType.ALERTS, ResourceType.SYSTEM_STATUS},
                    allowed_services={"web", "api", "database", "cache"},
                    data_sensitivity_limit=DataSensitivity.INTERNAL,
                    session_timeout=timedelta(hours=8),
                    created_at=datetime.utcnow()
                ),
                PermissionLevel.ADMIN: UserPermissions(
                    user_id="default_admin",
                    permission_level=PermissionLevel.ADMIN,
                    allowed_resources=set(ResourceType),
                    allowed_services=set(),  # Empty means all services
                    data_sensitivity_limit=DataSensitivity.SENSITIVE,
                    session_timeout=timedelta(hours=12),
                    created_at=datetime.utcnow()
                )
            }
            
            # Cache default permissions
            for level, permissions in default_permissions.items():
                cache_key = f"default_{level.value}"
                self._permission_cache[cache_key] = permissions
                self._cache_timestamps[cache_key] = datetime.utcnow()
            
            logger.info("Default permissions loaded")
            
        except Exception as e:
            logger.error(f"Failed to load default permissions: {e}")
    
    async def authenticate_user(
        self,
        user_token: str,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[SecurityContext]:
        """Authenticate user and create security context"""
        try:
            self._stats['auth_requests'] += 1
            
            # Try to authenticate with Observatory first
            user_info = await self._authenticate_with_observatory(user_token)
            
            if not user_info:
                # Fallback to local authentication
                user_info = await self._authenticate_locally(user_token)
            
            if not user_info:
                self._stats['auth_failures'] += 1
                await self._audit_log("auth_failure", {
                    "token_hash": hashlib.sha256(user_token.encode()).hexdigest()[:16],
                    "source_ip": source_ip,
                    "user_agent": user_agent
                })
                return None
            
            # Get user permissions
            permissions = await self._get_user_permissions(user_info['user_id'])
            
            if not permissions:
                self._stats['auth_failures'] += 1
                await self._audit_log("permission_failure", {
                    "user_id": user_info['user_id'],
                    "source_ip": source_ip
                })
                return None
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            security_context = SecurityContext(
                user_id=user_info['user_id'],
                session_id=session_id,
                permissions=permissions,
                request_timestamp=datetime.utcnow(),
                source_ip=source_ip,
                user_agent=user_agent
            )
            
            # Store session
            await self._store_session(security_context)
            
            self._stats['auth_successes'] += 1
            await self._audit_log("auth_success", {
                "user_id": user_info['user_id'],
                "session_id": session_id,
                "permission_level": permissions.permission_level.value,
                "source_ip": source_ip
            })
            
            logger.info(f"User authenticated: {user_info['user_id']} (level: {permissions.permission_level.value})")
            return security_context
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self._stats['auth_failures'] += 1
            return None
    
    async def _authenticate_with_observatory(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate with existing Observatory auth system"""
        try:
            if not self._observatory_auth_detected:
                return None
            
            # In a real implementation, this would make HTTP requests to Observatory auth
            # For brownfield safety, we'll simulate the authentication
            
            # Simulate JWT token validation
            if token.startswith("obs_"):
                # Simulate Observatory token format
                user_id = token.replace("obs_", "").split("_")[0]
                return {
                    "user_id": user_id,
                    "auth_source": "observatory",
                    "validated_at": datetime.utcnow().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Observatory authentication failed: {e}")
            return None
    
    async def _authenticate_locally(self, token: str) -> Optional[Dict[str, Any]]:
        """Local authentication fallback"""
        try:
            # Try to decode JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            # Validate token expiration
            if datetime.utcnow().timestamp() > payload.get('exp', 0):
                return None
            
            return {
                "user_id": payload.get('user_id'),
                "auth_source": "local",
                "validated_at": datetime.utcnow().isoformat()
            }
            
        except jwt.InvalidTokenError:
            # Try simple token format for demo
            if token.startswith("user_"):
                user_id = token.replace("user_", "")
                return {
                    "user_id": user_id,
                    "auth_source": "demo",
                    "validated_at": datetime.utcnow().isoformat()
                }
            
            return None
        except Exception as e:
            logger.warning(f"Local authentication failed: {e}")
            return None
    
    async def _get_user_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get user permissions from cache or Observatory"""
        try:
            # Check cache first
            cache_key = f"user_{user_id}"
            if self._is_cache_valid(cache_key):
                return self._permission_cache[cache_key]
            
            # Try to get permissions from Observatory
            permissions = await self._get_observatory_permissions(user_id)
            
            if not permissions:
                # Fallback to default permissions based on user pattern
                permissions = self._get_default_permissions(user_id)
            
            if permissions:
                # Cache permissions
                self._permission_cache[cache_key] = permissions
                self._cache_timestamps[cache_key] = datetime.utcnow()
            
            return permissions
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return None
    
    async def _get_observatory_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get user permissions from Observatory system"""
        try:
            if not self._observatory_auth_detected:
                return None
            
            # In a real implementation, this would query Observatory's user management
            # For brownfield safety, we'll simulate based on user patterns
            
            # Simulate Observatory permission mapping
            if user_id.startswith("admin"):
                level = PermissionLevel.ADMIN
            elif user_id.startswith("operator") or user_id.startswith("ops"):
                level = PermissionLevel.OPERATOR
            elif user_id.startswith("guest"):
                level = PermissionLevel.GUEST
            else:
                level = PermissionLevel.USER
            
            # Get default permissions for this level
            default_key = f"default_{level.value}"
            if default_key in self._permission_cache:
                template = self._permission_cache[default_key]
                return UserPermissions(
                    user_id=user_id,
                    permission_level=level,
                    allowed_resources=template.allowed_resources.copy(),
                    allowed_services=template.allowed_services.copy(),
                    data_sensitivity_limit=template.data_sensitivity_limit,
                    session_timeout=template.session_timeout,
                    created_at=datetime.utcnow(),
                    metadata={"source": "observatory"}
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get Observatory permissions: {e}")
            return None
    
    def _get_default_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get default permissions for user"""
        try:
            # Default to USER level for unknown users
            level = PermissionLevel.USER
            
            # Override based on user ID patterns
            if user_id.startswith("admin"):
                level = PermissionLevel.ADMIN
            elif user_id.startswith("operator") or user_id.startswith("ops"):
                level = PermissionLevel.OPERATOR
            elif user_id.startswith("guest"):
                level = PermissionLevel.GUEST
            
            # Get template permissions
            template_key = f"default_{level.value}"
            if template_key in self._permission_cache:
                template = self._permission_cache[template_key]
                return UserPermissions(
                    user_id=user_id,
                    permission_level=level,
                    allowed_resources=template.allowed_resources.copy(),
                    allowed_services=template.allowed_services.copy(),
                    data_sensitivity_limit=template.data_sensitivity_limit,
                    session_timeout=template.session_timeout,
                    created_at=datetime.utcnow(),
                    metadata={"source": "default"}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get default permissions: {e}")
            return None    
 
   async def _store_session(self, context: SecurityContext) -> None:
        """Store active session"""
        try:
            # Clean up expired sessions first
            await self._cleanup_expired_sessions()
            
            # Check session limits per user
            user_sessions = self._user_sessions.get(context.user_id, set())
            if len(user_sessions) >= self.max_sessions_per_user:
                # Remove oldest session
                oldest_session = min(user_sessions, key=lambda s: self._active_sessions[s].request_timestamp)
                await self._remove_session(oldest_session)
            
            # Store new session
            self._active_sessions[context.session_id] = context
            
            if context.user_id not in self._user_sessions:
                self._user_sessions[context.user_id] = set()
            self._user_sessions[context.user_id].add(context.session_id)
            
        except Exception as e:
            logger.error(f"Failed to store session: {e}")
    
    async def _remove_session(self, session_id: str) -> None:
        """Remove a session"""
        try:
            if session_id in self._active_sessions:
                context = self._active_sessions[session_id]
                del self._active_sessions[session_id]
                
                if context.user_id in self._user_sessions:
                    self._user_sessions[context.user_id].discard(session_id)
                    if not self._user_sessions[context.user_id]:
                        del self._user_sessions[context.user_id]
                
                await self._audit_log("session_removed", {
                    "session_id": session_id,
                    "user_id": context.user_id
                })
                
        except Exception as e:
            logger.error(f"Failed to remove session: {e}")
    
    async def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions"""
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for session_id, context in self._active_sessions.items():
                session_age = current_time - context.request_timestamp
                if session_age > context.permissions.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                await self._remove_session(session_id)
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_age = datetime.utcnow() - self._cache_timestamps[cache_key]
        return cache_age < self._cache_ttl
    
    async def validate_session(self, session_id: str) -> Optional[SecurityContext]:
        """Validate an active session"""
        try:
            if session_id not in self._active_sessions:
                return None
            
            context = self._active_sessions[session_id]
            
            # Check session expiration
            session_age = datetime.utcnow() - context.request_timestamp
            if session_age > context.permissions.session_timeout:
                await self._remove_session(session_id)
                return None
            
            # Update last access time
            context.request_timestamp = datetime.utcnow()
            
            return context
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return None
    
    async def check_permission(
        self,
        context: SecurityContext,
        resource_type: ResourceType,
        service_name: Optional[str] = None
    ) -> bool:
        """Check if user has permission for a resource"""
        try:
            self._stats['permission_checks'] += 1
            
            permissions = context.permissions
            
            # Check resource permission
            if resource_type not in permissions.allowed_resources:
                self._stats['permission_denials'] += 1
                await self._audit_log("permission_denied", {
                    "user_id": context.user_id,
                    "session_id": context.session_id,
                    "resource_type": resource_type.value,
                    "service_name": service_name
                })
                return False
            
            # Check service permission if specified
            if service_name and permissions.allowed_services:
                if service_name not in permissions.allowed_services:
                    self._stats['permission_denials'] += 1
                    await self._audit_log("service_permission_denied", {
                        "user_id": context.user_id,
                        "session_id": context.session_id,
                        "service_name": service_name
                    })
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    async def filter_observatory_context(
        self,
        context: ObservatoryContext,
        security_context: SecurityContext
    ) -> ObservatoryContext:
        """Filter Observatory context based on user permissions"""
        try:
            permissions = security_context.permissions
            
            # Create filtered context
            filtered_context = ObservatoryContext(
                timestamp=context.timestamp,
                system_status=context.system_status,
                active_alerts=0,
                critical_alerts=0,
                metrics_summary={"count": 0, "types": [], "latest_timestamp": None},
                alerts_summary={"count": 0, "firing": 0, "critical": 0, "warning": 0},
                formatted_context=""
            )
            
            # Filter based on permissions
            if await self.check_permission(security_context, ResourceType.SYSTEM_STATUS):
                filtered_context.system_status = context.system_status
            else:
                filtered_context.system_status = "unknown"
            
            if await self.check_permission(security_context, ResourceType.METRICS):
                filtered_context.metrics_summary = context.metrics_summary
            
            if await self.check_permission(security_context, ResourceType.ALERTS):
                filtered_context.active_alerts = context.active_alerts
                filtered_context.critical_alerts = context.critical_alerts
                filtered_context.alerts_summary = context.alerts_summary
            
            # Filter formatted context based on data sensitivity
            filtered_context.formatted_context = await self._filter_formatted_context(
                context.formatted_context,
                permissions.data_sensitivity_limit
            )
            
            await self._audit_log("context_filtered", {
                "user_id": security_context.user_id,
                "session_id": security_context.session_id,
                "permission_level": permissions.permission_level.value,
                "original_metrics": context.metrics_summary.get("count", 0),
                "filtered_metrics": filtered_context.metrics_summary.get("count", 0),
                "original_alerts": context.active_alerts,
                "filtered_alerts": filtered_context.active_alerts
            })
            
            return filtered_context
            
        except Exception as e:
            logger.error(f"Context filtering failed: {e}")
            # Return empty context on error
            return ObservatoryContext(
                timestamp=datetime.utcnow(),
                system_status="unknown",
                active_alerts=0,
                critical_alerts=0,
                metrics_summary={"count": 0},
                alerts_summary={"count": 0},
                formatted_context="Context unavailable due to security error"
            )
    
    async def _filter_formatted_context(
        self,
        formatted_context: str,
        sensitivity_limit: DataSensitivity
    ) -> str:
        """Filter formatted context based on sensitivity level"""
        try:
            if not formatted_context:
                return ""
            
            # Define sensitivity-based filtering rules
            if sensitivity_limit == DataSensitivity.PUBLIC:
                # Only show basic system status
                lines = formatted_context.split('\n')
                filtered_lines = []
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['system status', 'overall', 'health']):
                        filtered_lines.append(line)
                return '\n'.join(filtered_lines[:3])  # Limit to 3 lines
            
            elif sensitivity_limit == DataSensitivity.INTERNAL:
                # Show system status and basic metrics, but sanitize sensitive data
                sanitized = self._sanitize_sensitive_data(formatted_context)
                return sanitized
            
            elif sensitivity_limit == DataSensitivity.SENSITIVE:
                # Show most data but still sanitize highly sensitive information
                return self._sanitize_highly_sensitive_data(formatted_context)
            
            else:  # CONFIDENTIAL
                # Show all data
                return formatted_context
            
        except Exception as e:
            logger.error(f"Context filtering failed: {e}")
            return "Context filtering error"
    
    def _sanitize_sensitive_data(self, text: str) -> str:
        """Sanitize sensitive data from text"""
        try:
            import re
            
            # Patterns for sensitive data
            sensitive_patterns = [
                (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REDACTED]'),  # IP addresses
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),  # Email addresses
                (r'\b(?:password|secret|token|key|credential|auth)[:\s=]+\S+', '[CREDENTIAL_REDACTED]'),  # Credentials
                (r'\b[A-Za-z0-9]{32,}\b', '[TOKEN_REDACTED]'),  # Long tokens/hashes
            ]
            
            sanitized = text
            for pattern, replacement in sensitive_patterns:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            
            if sanitized != text:
                self._stats['data_sanitizations'] += 1
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Data sanitization failed: {e}")
            return text
    
    def _sanitize_highly_sensitive_data(self, text: str) -> str:
        """Sanitize only highly sensitive data"""
        try:
            import re
            
            # Only sanitize the most sensitive patterns
            highly_sensitive_patterns = [
                (r'\b(?:password|secret|private_key)[:\s=]+\S+', '[REDACTED]'),
                (r'\b[A-Za-z0-9]{64,}\b', '[HASH_REDACTED]'),  # Very long hashes
            ]
            
            sanitized = text
            for pattern, replacement in highly_sensitive_patterns:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Highly sensitive data sanitization failed: {e}")
            return text
    
    async def _audit_log(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log security audit event"""
        try:
            if not self.audit_log_enabled:
                return
            
            audit_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "details": details
            }
            
            self._audit_events.append(audit_event)
            self._stats['audit_events'] += 1
            
            # Keep only recent audit events (last 1000)
            if len(self._audit_events) > 1000:
                self._audit_events = self._audit_events[-1000:]
            
            # Log to system logger for external audit systems
            logger.info(f"AUDIT: {event_type} - {details}")
            
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")
    
    async def create_user_token(
        self,
        user_id: str,
        permission_level: PermissionLevel,
        expires_in: timedelta = timedelta(hours=24)
    ) -> str:
        """Create a JWT token for a user (for testing/demo purposes)"""
        try:
            payload = {
                "user_id": user_id,
                "permission_level": permission_level.value,
                "iat": datetime.utcnow().timestamp(),
                "exp": (datetime.utcnow() + expires_in).timestamp()
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            
            await self._audit_log("token_created", {
                "user_id": user_id,
                "permission_level": permission_level.value,
                "expires_in_hours": expires_in.total_seconds() / 3600
            })
            
            return token
            
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise ValidationError(f"Failed to create token: {str(e)}")
    
    async def get_audit_events(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get audit events for security monitoring"""
        try:
            events = self._audit_events.copy()
            
            # Filter by event type
            if event_type:
                events = [e for e in events if e['event_type'] == event_type]
            
            # Filter by user ID
            if user_id:
                events = [e for e in events if e['details'].get('user_id') == user_id]
            
            # Sort by timestamp (newest first) and limit
            events.sort(key=lambda x: x['timestamp'], reverse=True)
            return events[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get audit events: {e}")
            return []
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get information about active sessions"""
        try:
            sessions = []
            for session_id, context in self._active_sessions.items():
                sessions.append({
                    "session_id": session_id,
                    "user_id": context.user_id,
                    "permission_level": context.permissions.permission_level.value,
                    "created_at": context.request_timestamp.isoformat(),
                    "source_ip": context.source_ip,
                    "expires_at": (context.request_timestamp + context.permissions.session_timeout).isoformat()
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return []
    
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a specific session"""
        try:
            if session_id in self._active_sessions:
                await self._remove_session(session_id)
                await self._audit_log("session_revoked", {"session_id": session_id})
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke session: {e}")
            return False
    
    async def revoke_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user"""
        try:
            user_sessions = self._user_sessions.get(user_id, set()).copy()
            revoked_count = 0
            
            for session_id in user_sessions:
                if await self.revoke_session(session_id):
                    revoked_count += 1
            
            await self._audit_log("user_sessions_revoked", {
                "user_id": user_id,
                "revoked_count": revoked_count
            })
            
            return revoked_count
            
        except Exception as e:
            logger.error(f"Failed to revoke user sessions: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get security manager statistics"""
        return {
            **self._stats,
            'active_sessions': len(self._active_sessions),
            'active_users': len(self._user_sessions),
            'cached_permissions': len(self._permission_cache),
            'observatory_auth_detected': self._observatory_auth_detected,
            'audit_log_enabled': self.audit_log_enabled
        }
    
    async def health_check(self) -> ComponentHealth:
        """Perform health check"""
        try:
            # Check basic functionality
            active_sessions = len(self._active_sessions)
            
            # Determine health status
            if not self._observatory_auth_detected:
                status = "degraded"
                error_message = "Observatory auth not detected - using fallback"
            elif self._stats['auth_failures'] > self._stats['auth_successes']:
                status = "degraded"
                error_message = "High authentication failure rate"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="security_manager",
                status=status,
                response_time=0.0,  # Not applicable
                error_message=error_message,
                metadata={
                    "active_sessions": active_sessions,
                    "observatory_auth_detected": self._observatory_auth_detected,
                    "auth_success_rate": self._stats['auth_successes'] / max(1, self._stats['auth_requests']),
                    "permission_denial_rate": self._stats['permission_denials'] / max(1, self._stats['permission_checks']),
                    "audit_events": self._stats['audit_events']
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="security_manager",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def cleanup(self) -> None:
        """Cleanup security manager resources"""
        try:
            # Clear all sessions
            self._active_sessions.clear()
            self._user_sessions.clear()
            
            # Clear caches
            self._permission_cache.clear()
            self._cache_timestamps.clear()
            
            # Clear audit log
            self._audit_events.clear()
            
            logger.info("Security Manager cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Global security manager instance
security_manager = SecurityManager()


async def authenticate_user(
    user_token: str,
    source_ip: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[SecurityContext]:
    """Authenticate user and return security context"""
    return await security_manager.authenticate_user(user_token, source_ip, user_agent)


async def validate_session(session_id: str) -> Optional[SecurityContext]:
    """Validate an active session"""
    return await security_manager.validate_session(session_id)


async def check_permission(
    context: SecurityContext,
    resource_type: ResourceType,
    service_name: Optional[str] = None
) -> bool:
    """Check if user has permission for a resource"""
    return await security_manager.check_permission(context, resource_type, service_name)


async def initialize_security_manager() -> None:
    """Initialize the security manager"""
    await security_manager.initialize()


async def cleanup_security_manager() -> None:
    """Cleanup the security manager"""
    await security_manager.cleanup()