#!/usr/bin/env python3
"""
Auth Service - Main authentication service orchestration

Refactored from auth_service.py for RM-DDD compliance.
Single responsibility: Authentication service orchestration and coordination.
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import logging

from .auth_models import AuthCredentials, AuthSession, AuthResult, AuthConfig
from .auth_session_manager import AuthSessionManager
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Auth Service',
            'description': 'auth_service module for DevPost integration',
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


class DevPostAuthService(ReflectiveModule):
    """
    DevPost Authentication Service
    
    Provides secure authentication, session management, and API access
    for DevPost integration. Handles credential management and token-based
    authentication with session persistence.
    """
    
    def __init__(self, config: Optional[AuthConfig] = None, storage_path: Optional[Path] = None):
        super().__init__(module_id="auth_service", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize authentication service"""
        self.config = config or AuthConfig()
        self.storage_path = storage_path or Path("devpost_auth.json")
        self.session_manager = AuthSessionManager(self.config, storage_path)
        self.login_attempts: Dict[str, int] = {}
        self.lockout_until: Dict[str, float] = {}
        
        # Load stored credentials
        self._load_credentials()
    
    def authenticate(self, username: str, password: str, api_key: Optional[str] = None) -> AuthResult:
        """Authenticate user with DevPost"""
        try:
            # Check if user is locked out
            if self._is_user_locked_out(username):
                return AuthResult(
                    success=False,
                    message="Account is temporarily locked due to too many failed attempts",
                    error_code="ACCOUNT_LOCKED"
                )
            
            # Validate credentials
            credentials = AuthCredentials(
                username=username,
                password=password,
                api_key=api_key
            )
            
            # Validate password strength
            is_valid_password, password_message = self.config.validate_password(password)
            if not is_valid_password:
                self._record_failed_attempt(username)
                return AuthResult(
                    success=False,
                    message=f"Password validation failed: {password_message}",
                    error_code="INVALID_PASSWORD"
                )
            
            # Simulate DevPost API authentication
            auth_success = self._simulate_devpost_auth(credentials)
            if not auth_success:
                self._record_failed_attempt(username)
                return AuthResult(
                    success=False,
                    message="Invalid credentials",
                    error_code="INVALID_CREDENTIALS"
                )
            
            # Reset failed attempts on successful login
            self._reset_failed_attempts(username)
            
            # Create session
            user_id = self._generate_user_id(username)
            session_result = self.session_manager.create_session(user_id, username, credentials)
            
            if session_result.success:
                # Store credentials
                self._store_credentials(credentials)
                logger.info(f"User {username} authenticated successfully")
            
            return session_result
            
        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            return AuthResult(
                success=False,
                message=f"Authentication failed: {str(e)}",
                error_code="AUTH_ERROR"
            )
    
    def validate_session(self, session_token: str) -> AuthResult:
        """Validate an active session"""
        return self.session_manager.validate_session(session_token)
    
    def refresh_session(self, session_token: str) -> AuthResult:
        """Refresh an active session"""
        return self.session_manager.refresh_session(session_token)
    
    def logout(self, session_token: str) -> AuthResult:
        """Logout user and invalidate session"""
        try:
            result = self.session_manager.invalidate_session(session_token)
            if result.success:
                logger.info("User logged out successfully")
            return result
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return AuthResult(
                success=False,
                message=f"Logout failed: {str(e)}",
                error_code="LOGOUT_ERROR"
            )
    
    def get_user_sessions(self, username: str) -> List[AuthSession]:
        """Get all active sessions for a user"""
        user_id = self._generate_user_id(username)
        return self.session_manager.get_user_sessions(user_id)
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        return self.session_manager.cleanup_expired_sessions()
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """Get authentication statistics"""
        session_stats = self.session_manager.get_session_stats()
        return {
            'session_stats': session_stats,
            'config': self.config.to_dict(),
            'locked_users': len(self.lockout_until),
            'failed_attempts': len(self.login_attempts)
        }
    
    def _simulate_devpost_auth(self, credentials: AuthCredentials) -> bool:
        """Simulate DevPost API authentication"""
        # In a real implementation, this would make an API call to DevPost
        # For now, we'll simulate with basic validation
        
        # Check if credentials are not empty
        if not credentials.username or not credentials.password:
            return False
        
        # Simulate API delay
        time.sleep(0.1)
        
        # For demo purposes, accept any non-empty credentials
        # In production, this would validate against DevPost API
        return True
    
    def _is_user_locked_out(self, username: str) -> bool:
        """Check if user is currently locked out"""
        if username not in self.lockout_until:
            return False
        
        lockout_time = self.lockout_until[username]
        if time.time() > lockout_time:
            # Lockout expired
            del self.lockout_until[username]
            return False
        
        return True
    
    def _record_failed_attempt(self, username: str) -> None:
        """Record a failed login attempt"""
        self.login_attempts[username] = self.login_attempts.get(username, 0) + 1
        
        # Check if user should be locked out
        if self.login_attempts[username] >= self.config.max_login_attempts:
            lockout_duration = self.config.lockout_duration_minutes * 60
            self.lockout_until[username] = time.time() + lockout_duration
            logger.warning(f"User {username} locked out for {self.config.lockout_duration_minutes} minutes")
    
    def _reset_failed_attempts(self, username: str) -> None:
        """Reset failed login attempts for user"""
        if username in self.login_attempts:
            del self.login_attempts[username]
        if username in self.lockout_until:
            del self.lockout_until[username]
    
    def _generate_user_id(self, username: str) -> str:
        """Generate user ID from username"""
        return f"user_{hash(username) % 1000000}"
    
    def _load_credentials(self) -> None:
        """Load stored credentials from file"""
        try:
            if not self.storage_path.exists():
                return
            
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Load configuration if available
            if 'config' in data:
                self.config = AuthConfig.from_dict(data['config'])
            
            logger.info("Loaded stored credentials and configuration")
            
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
    
    def _store_credentials(self, credentials: AuthCredentials) -> None:
        """Store credentials to file"""
        try:
            data = {
                'config': self.config.to_dict(),
                'stored_at': time.time()
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error storing credentials: {e}")
    
    def update_config(self, new_config: AuthConfig) -> None:
        """Update authentication configuration"""
        self.config = new_config
        self.session_manager.config = new_config
        self._store_credentials(AuthCredentials("", ""))  # Just to save config
    
    def is_healthy(self) -> bool:
        """Check if authentication service is healthy"""
        try:
            # Check if session manager is working
            stats = self.session_manager.get_session_stats()
            
            # Check if storage is accessible
            if self.config.enable_session_persistence:
                storage_accessible = self.storage_path.parent.exists()
                if not storage_accessible:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        try:
            stats = self.session_manager.get_session_stats()
            
            return {
                'service_healthy': self.is_healthy(),
                'session_manager_stats': stats,
                'config': self.config.to_dict(),
                'storage_accessible': self.storage_path.parent.exists() if self.config.enable_session_persistence else True,
                'locked_users_count': len(self.lockout_until),
                'failed_attempts_count': len(self.login_attempts)
            }
            
        except Exception as e:
            logger.error(f"Error getting health indicators: {e}")
            return {
                'service_healthy': False,
                'error': str(e)
            }
