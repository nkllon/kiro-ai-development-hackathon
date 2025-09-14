"""
DevPost Integration Reflective Module
====================================

Reflective module interface for DevPost integration components.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Provide reflective module interface for DevPost integration
"""

# Import the unified interface
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)
from typing import Dict, Any, List


class ModuleConfiguration:
    """Module configuration class."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value


class ReflectiveModuleRegistry:
    """Registry for reflective modules."""
    
    def __init__(self):
        self.modules = {}
    
    def register(self, metadata: Dict[str, Any]):
        """Register a module."""
        module_id = metadata.get('module_id', 'unknown')
        self.modules[module_id] = metadata
    
    def get(self, module_id: str) -> Dict[str, Any]:
        """Get module metadata."""
        return self.modules.get(module_id)
    
    def list_modules(self) -> List[str]:
        """List all registered module IDs."""
        return list(self.modules.keys())

# Alias for backward compatibility
HealthStatus = ModuleStatus

# Re-export for backward compatibility
__all__ = [
    "ReflectiveModule",
    "ModuleHealth", 
    "ModuleStatus",
    "HealthStatus",
    "ModuleCapability",
    "ModuleConfiguration",
    "ReflectiveModuleRegistry",
    "GracefulDegradationResult"
]

def register_module(registry):
    """Register module with registry."""
    if hasattr(registry, 'register'):
        registry.register()
