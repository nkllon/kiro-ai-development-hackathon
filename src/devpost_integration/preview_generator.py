#!/usr/bin/env python3
"""
preview_generator - Simplified for size compliance
"""

from .preview_generator_methods import DevpostPreviewGenerator, RealtimePreviewManager
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from src.rm_ddd.core.health import ModuleHealth


logger = logging.getLogger(__name__)

# Export the main classes
__all__ = ['DevpostPreviewGenerator', 'RealtimePreviewManager']

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

