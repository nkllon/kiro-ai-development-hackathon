#!/usr/bin/env python3
"""
Base ReflectiveModule class for SCA systems
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

class ReflectiveModule(ABC):
    """Base ReflectiveModule class for RDI compliance."""
    
    def __init__(self):
        self.module_id = self.__class__.__name__
        self.health_status = "healthy"
        self.registry_metadata = {}
        
    def get_interface_metadata(self) -> Dict[str, Any]:
        """Get interface metadata for registry."""
        return {
            'module_id': self.module_id,
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            'status': self.health_status,
            'timestamp': datetime.now().isoformat(),
            'module_id': self.module_id
        }
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return self.health_check()
