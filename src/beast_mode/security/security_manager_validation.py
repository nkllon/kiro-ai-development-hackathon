"""
Security Manager Validation

This module was extracted from security_manager.py
as part of RM-DDD compliance refactoring.
"""

import hashlib
import secrets
import base64
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import logging
from ..core.reflective_module import ReflectiveModule, HealthStatus
from src.rm_ddd.core.health import ModuleHealth


def validate_api_key(self, api_key: str, required_access: str='read_only') -> Dict[str, Any]:
    """
        Validate API key and check access permissions
        Implements authentication and authorization
        """
    try:
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        for client_name, key_info in self.api_keys.items():
            if key_info['key_hash'] == key_hash:
                if not key_info['active']:
                    self._log_security_violation('inactive_api_key_used', client_name, 'medium')
                    return {'valid': False, 'reason': 'API key inactive'}
                if datetime.now() > key_info['expires']:
                    self._log_security_violation('expired_api_key_used', client_name, 'medium')
                    return {'valid': False, 'reason': 'API key expired'}
                access_levels = {'read_only': 1, 'read_write': 2, 'full_access': 3}
                user_level = access_levels.get(key_info['access_level'], 0)
                required_level = access_levels.get(required_access, 1)
                if user_level < required_level:
                    self._log_security_violation('insufficient_access_level', f"{client_name}: {key_info['access_level']} < {required_access}", 'medium')
                    return {'valid': False, 'reason': 'Insufficient access level'}
                self._log_security_event('api_key_validated', {'client': client_name, 'access_level': key_info['access_level'], 'required_access': required_access})
                return {'valid': True, 'client_name': client_name, 'access_level': key_info['access_level']}
        self._log_security_violation('invalid_api_key_used', 'Unknown key', 'high')
        return {'valid': False, 'reason': 'Invalid API key'}
    except Exception as e:
        self._log_security_violation('api_key_validation_error', str(e), 'high')
        return {'valid': False, 'reason': 'Validation error'}

def validate_security_compliance(self) -> Dict[str, Any]:
    """Validate security compliance for testing"""
    compliance_score = self._calculate_compliance_score()
    return {'compliance_score': compliance_score, 'security_checks_passed': compliance_score >= 0.9, 'encryption_enabled': self.encryption_enabled, 'authentication_configured': len(self.api_keys) > 0}

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

