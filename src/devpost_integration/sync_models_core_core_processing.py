"""
Sync Models Core Core Processing

This module was extracted from sync_models_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import SyncOperationType, ChangeType
from typing import Dict, List, Any, Optional

def add_processed_record(self) -> None:
    """Increment processed records count."""
    try:
        self.records_processed += 1
        self._operation_count += 1
    except Exception as e:
        logger.error(f'Failed to add processed record: {e}')
        self._errors += 1

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

