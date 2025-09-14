#!/usr/bin/env python3
"""logging_infrastructure - Main module file"""

from .logging_infrastructure_methods import LogLevel, LoggingInfrastructure, LoggingConfig, get_logging_infrastructure
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

__all__ = ['LogLevel', 'LoggingInfrastructure', 'LoggingConfig', 'get_logging_infrastructure']