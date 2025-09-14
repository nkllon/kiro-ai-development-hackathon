#!/usr/bin/env python3
"""auth_models - Main module file"""

from .auth_models_methods import AuthCredentials, AuthSession, AuthResult, AuthConfig
from src.rm_ddd.core.health import ModuleHealth



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

__all__ = ['AuthCredentials', 'AuthSession', 'AuthResult', 'AuthConfig']