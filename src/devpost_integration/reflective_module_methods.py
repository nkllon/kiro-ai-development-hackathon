"""
DEPRECATED: This ReflectiveModule interface is deprecated.

RDI Compliance Notice:
This file contains a duplicate ReflectiveModule interface that violates
Requirements-Driven Implementation (RDI) principles.

MIGRATION REQUIRED:
- Use the unified interface: src/rm_ddd/core/unified_reflective_module.py
- Update all imports to use the unified interface
- This file will be removed in a future version

Original file backed up to: src/devpost_integration/reflective_module_methods.py.backup_20250912_105305
Deprecated on: 2025-09-12T10:53:05.795816
"""

# Import the unified interface
from rm_ddd.core.unified_reflective_module import (
ReflectiveModule,
ModuleHealth,
ModuleStatus,
ModuleCapability,
GracefulDegradationResult
)

# Re-export for backward compatibility (temporary)
__all__ = [
'ReflectiveModule',
'ModuleHealth',
'ModuleStatus',
'ModuleCapability',
'GracefulDegradationResult'
]

class RegistermoduleClass:
    """Auto-generated class for functions."""

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

