"""
DEPRECATED: This ReflectiveModule interface is deprecated.

RDI Compliance Notice:
This file contains a duplicate ReflectiveModule interface that violates
Requirements-Driven Implementation (RDI) principles.

MIGRATION REQUIRED:
- Use the unified interface: src/rm_ddd/core/unified_reflective_module.py
- Update all imports to use the unified interface
- This file will be removed in a future version

Original file backed up to: src/beast_mode/core/reflective_module.py.backup_20250912_105104
Deprecated on: 2025-09-12T10:51:04.491081
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
    "ReflectiveModule",
    "ModuleHealth",
    "ModuleStatus", 
    "ModuleCapability",
    "GracefulDegradationResult"
]
