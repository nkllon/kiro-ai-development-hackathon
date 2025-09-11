#!/usr/bin/env python3
"""
Auth Models - Authentication data models and credentials

Extracted from auth_service.py for RM-DDD compliance.
Single responsibility: Authentication data models and credential management.
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class AuthCredentials(ReflectiveModule):
    """DevPost authentication credentials"""
    username: str
    password: str
    api_key: Optional[str] = None
    session_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if credentials are valid and not expired"""
        if not self.username or not self.password:
            return False
        
        if self.session_token and self.expires_at:
            return datetime.now() < self.expires_at
        
        return True
    
    def is_expired(self) -> bool:
        """Check if session token is expired"""
        if not self.expires_at:
            return True
        return datetime.now() >= self.expires_at
    
    def hash_password(self) -> str:
        """Hash password for secure storage"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            self.password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            salt, password_hash = hashed_password.split(':')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                self.password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return new_hash.hex() == password_hash
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert credentials to dictionary"""
        return {
            'username': self.username,
            'api_key': self.api_key,
            'session_token': self.session_token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthCredentials':
        """Create credentials from dictionary"""
        expires_at = None
        if data.get('expires_at'):
            expires_at = datetime.fromisoformat(data['expires_at'])
        
        return cls(
            username=data['username'],
            password='',  # Never store password in dict
            api_key=data.get('api_key'),
            session_token=data.get('session_token'),
            expires_at=expires_at
        )


@dataclass
class AuthSession:
    """Active authentication session"""
    session_id: str
    user_id: str
    username: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_valid(self) -> bool:
        """Check if session is valid and not expired"""
        if not self.is_active:
            return False
        
        return datetime.now() < self.expires_at
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() >= self.expires_at
    
    def extend_session(self, duration_minutes: int = 30) -> None:
        """Extend session duration"""
        self.expires_at = datetime.now() + timedelta(minutes=duration_minutes)
        self.last_activity = datetime.now()
    
    def invalidate(self) -> None:
        """Invalidate the session"""
        self.is_active = False
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def get_remaining_time(self) -> timedelta:
        """Get remaining session time"""
        if self.is_expired():
            return timedelta(0)
        return self.expires_at - datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthSession':
        """Create session from dictionary"""
        return cls(
            session_id=data['session_id'],
            user_id=data['user_id'],
            username=data['username'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_activity=datetime.fromisoformat(data['last_activity']),
            expires_at=datetime.fromisoformat(data['expires_at']),
            is_active=data.get('is_active', True),
            metadata=data.get('metadata', {})
        )


@dataclass
class AuthResult:
    """Authentication operation result"""
    success: bool
    message: str
    session: Optional[AuthSession] = None
    credentials: Optional[AuthCredentials] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_successful(self) -> bool:
        """Check if authentication was successful"""
        return self.success and self.session is not None
    
    def get_error_message(self) -> str:
        """Get error message for failed authentication"""
        if self.success:
            return ""
        return f"{self.message} (Code: {self.error_code})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'success': self.success,
            'message': self.message,
            'session': self.session.to_dict() if self.session else None,
            'credentials': self.credentials.to_dict() if self.credentials else None,
            'error_code': self.error_code,
            'metadata': self.metadata
        }

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Auth Models',
            'description': 'auth_models module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


@dataclass
class AuthConfig:
    """Authentication configuration"""
    session_timeout_minutes: int = 30
    max_sessions_per_user: int = 5
    password_min_length: int = 8
    require_strong_password: bool = True
    enable_session_persistence: bool = True
    auto_logout_inactive_minutes: int = 60
    enable_two_factor: bool = False
    api_rate_limit_per_minute: int = 100
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password against configuration"""
        if len(password) < self.password_min_length:
            return False, f"Password must be at least {self.password_min_length} characters"
        
        if self.require_strong_password:
            if not any(c.isupper() for c in password):
                return False, "Password must contain at least one uppercase letter"
            if not any(c.islower() for c in password):
                return False, "Password must contain at least one lowercase letter"
            if not any(c.isdigit() for c in password):
                return False, "Password must contain at least one digit"
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'session_timeout_minutes': self.session_timeout_minutes,
            'max_sessions_per_user': self.max_sessions_per_user,
            'password_min_length': self.password_min_length,
            'require_strong_password': self.require_strong_password,
            'enable_session_persistence': self.enable_session_persistence,
            'auto_logout_inactive_minutes': self.auto_logout_inactive_minutes,
            'enable_two_factor': self.enable_two_factor,
            'api_rate_limit_per_minute': self.api_rate_limit_per_minute,
            'max_login_attempts': self.max_login_attempts,
            'lockout_duration_minutes': self.lockout_duration_minutes
        }
    
    @classmethod

    # Registry Integration Enhancements
    def _register_with_registry(self):
        """Register module with RM registry."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            ReflectiveModuleRegistry.register(self)
            logger.info(f"Module {self.module_id} registered with RM registry")
        except Exception as e:
            logger.error(f"Failed to register module {self.module_id}: {e}")
    
    def _unregister_from_registry(self):
        """Unregister module from RM registry."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            ReflectiveModuleRegistry.unregister(self.module_id)
            logger.info(f"Module {self.module_id} unregistered from RM registry")
        except Exception as e:
            logger.error(f"Failed to unregister module {self.module_id}: {e}")
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry integration status."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            is_registered = ReflectiveModuleRegistry.get_module(self.module_id) is not None
            all_modules = list(ReflectiveModuleRegistry.get_all_modules().keys())
            
            return {
                'is_registered': is_registered,
                'module_id': self.module_id,
                'total_registered_modules': len(all_modules),
                'all_module_ids': all_modules,
                'registry_available': True
            }
        except Exception as e:
            return {
                'is_registered': False,
                'module_id': self.module_id,
                'total_registered_modules': 0,
                'all_module_ids': [],
                'registry_available': False,
                'error': str(e)
            }
    
    def discover_related_modules(self) -> List[str]:
        """Discover related modules in the registry."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            all_modules = ReflectiveModuleRegistry.get_all_modules()
            related_modules = []
            
            # Find modules with similar names or dependencies
            for module_id, module in all_modules.items():
                if module_id != self.module_id:
                    # Check if modules are related by name similarity
                    if any(word in module_id.lower() for word in module_name.lower().split('_')):
                        related_modules.append(module_id)
                    # Check if modules are related by dependencies
                    elif module_id in self.get_dependencies():
                        related_modules.append(module_id)
            
            return related_modules
        except Exception as e:
            logger.error(f"Failed to discover related modules: {e}")
            return []
    
    def get_registry_health(self) -> Dict[str, Any]:
        """Get registry health information."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            all_modules = ReflectiveModuleRegistry.get_all_modules()
            
            healthy_modules = 0
            degraded_modules = 0
            unhealthy_modules = 0
            
            for module_id, module in all_modules.items():
                try:
                    health = module.check_health()
                    if health.status.value == 'healthy':
                        healthy_modules += 1
                    elif health.status.value == 'degraded':
                        degraded_modules += 1
                    else:
                        unhealthy_modules += 1
                except Exception:
                    unhealthy_modules += 1
            
            total_modules = len(all_modules)
            health_percentage = (healthy_modules / total_modules * 100) if total_modules > 0 else 0
            
            return {
                'total_modules': total_modules,
                'healthy_modules': healthy_modules,
                'degraded_modules': degraded_modules,
                'unhealthy_modules': unhealthy_modules,
                'health_percentage': health_percentage,
                'registry_status': 'healthy' if health_percentage >= 80 else 'degraded' if health_percentage >= 60 else 'unhealthy'
            }
        except Exception as e:
            return {
                'total_modules': 0,
                'healthy_modules': 0,
                'degraded_modules': 0,
                'unhealthy_modules': 0,
                'health_percentage': 0,
                'registry_status': 'error',
                'error': str(e)
            }

    def from_dict(cls, data: Dict[str, Any]) -> 'AuthConfig':
        """Create configuration from dictionary"""
        return cls(**data)
