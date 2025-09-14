#!/usr/bin/env python3
"""debugging_engine - Main module file"""

from .debugging_engine_methods import DebugLevel, DebuggingEngine, DebugInfo, ExecutionTrace, DiagnosticResult, get_debugging_engine
from src.rm_ddd.core.health import ModuleHealth



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

    __all__ = ['DebugLevel', 'DebuggingEngine', 'DebugInfo', 'ExecutionTrace', 'DiagnosticResult', 'get_debugging_engine']