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
from typing import Optional, Dict, Any, Tuple, List
import logging
from datetime import datetime

from .auth_models import AuthCredentials, AuthSession, AuthResult, AuthConfig
from .auth_session_manager import AuthSessionManager
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)

logger = logging.getLogger(__name__)


class DevpostAuthService(ReflectiveModule):
    """Main authentication service with RM-DDD compliance"""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        """Initialize authentication service"""
        super().__init__(module_id="auth_service", version="1.0.0")
        self.config = config or AuthConfig()
        self.session_manager = AuthSessionManager(self.config)
        self._start_time = datetime.now()
        self._auth_attempts = 0
        self._successful_auths = 0
        self._failed_auths = 0
        register_module(self)
    
    def authenticate(self, credentials: AuthCredentials) -> AuthResult:
        """Authenticate with DevPost using provided credentials"""
        try:
            self._auth_attempts += 1
            
            # Validate credentials
            if not credentials.is_valid():
                self._failed_auths += 1
                return AuthResult(
                    success=False,
                    message="Invalid credentials provided",
                    session=None
                )
            
            # Attempt authentication
            result = self.session_manager.authenticate(credentials)
            
            if result.success:
                self._successful_auths += 1
                logger.info(f"Authentication successful for user: {credentials.username}")
            else:
                self._failed_auths += 1
                logger.warning(f"Authentication failed for user: {credentials.username}")
            
            return result
            
        except Exception as e:
            self._failed_auths += 1
            logger.error(f"Authentication error: {e}")
            return AuthResult(
                success=False,
                message=f"Authentication error: {str(e)}",
                session=None
            )
    
    def get_current_session(self) -> Optional[AuthSession]:
        """Get current active session"""
        return self.session_manager.get_current_session()
    
    def refresh_session(self) -> AuthResult:
        """Refresh current session"""
        try:
            current_session = self.get_current_session()
            if not current_session:
                return AuthResult(
                    success=False,
                    message="No active session to refresh",
                    session=None
                )
            
            return self.session_manager.refresh_session(current_session)
            
        except Exception as e:
            logger.error(f"Session refresh error: {e}")
            return AuthResult(
                success=False,
                message=f"Session refresh error: {str(e)}",
                session=None
            )
    
    def logout(self) -> bool:
        """Logout current session"""
        try:
            success = self.session_manager.logout()
            if success:
                logger.info("Successfully logged out")
            return success
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        session = self.get_current_session()
        return session is not None and session.is_valid()
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication status information"""
        session = self.get_current_session()
        return {
            'authenticated': self.is_authenticated(),
            'session': session.to_dict() if session else None,
            'config': self.config.to_dict(),
            'metrics': self.get_metrics()
        }
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'DevPost Auth Service',
            'description': 'Authentication service for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.HEALTH_MONITORING,
            ModuleCapability.CONFIGURATION,
            ModuleCapability.LOGGING,
            ModuleCapability.METRICS,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return [
            'auth_models',
            'auth_session_manager'
        ]
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Check session manager
            if not hasattr(self, 'session_manager'):
                issues.append("Missing session manager")
                health_score -= 0.3
            
            # Check configuration
            if not hasattr(self, 'config'):
                issues.append("Missing configuration")
                health_score -= 0.2
            
            # Check authentication success rate
            if self._auth_attempts > 0:
                success_rate = self._successful_auths / self._auth_attempts
                if success_rate < 0.5:  # Less than 50% success rate
                    issues.append(f"Low authentication success rate: {success_rate:.1%}")
                    health_score -= 0.2
            
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
            parameters=self.config.to_dict(),
            required_parameters=['api_base_url', 'timeout'],
            optional_parameters=['retry_attempts', 'session_timeout'],
            validation_rules={
                'api_base_url': 'string',
                'timeout': 'integer',
                'retry_attempts': 'integer',
                'session_timeout': 'integer'
            },
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                return False
            
            # Update auth config
            if 'api_base_url' in config.parameters:
                self.config.api_base_url = config.parameters['api_base_url']
            if 'timeout' in config.parameters:
                self.config.timeout = config.parameters['timeout']
            if 'retry_attempts' in config.parameters:
                self.config.retry_attempts = config.parameters['retry_attempts']
            if 'session_timeout' in config.parameters:
                self.config.session_timeout = config.parameters['session_timeout']
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration update error: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        success_rate = (self._successful_auths / self._auth_attempts) if self._auth_attempts > 0 else 0.0
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'auth_attempts': self._auth_attempts,
            'successful_auths': self._successful_auths,
            'failed_auths': self._failed_auths,
            'success_rate': success_rate,
            'is_authenticated': self.is_authenticated(),
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._auth_attempts = 0
        self._successful_auths = 0
        self._failed_auths = 0
        self._start_time = datetime.now()
        logger.info("Metrics reset for auth service module")