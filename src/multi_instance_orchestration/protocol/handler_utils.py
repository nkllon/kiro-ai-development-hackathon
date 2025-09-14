"""
Handler Utils

This module was extracted from handler.py
as part of RM-DDD compliance refactoring.
"""

import re
from datetime import datetime
from typing import Callable, Optional
from ..core.reflective_module import HealthIndicator, ModuleStatus, ReflectiveModule
from .models import ActionResult, CommandPattern, StructuredAction, ValidationResult
from src.rm_ddd.core.health import ModuleHealth


def format_response(self, result: ActionResult) -> str:
    """Format result as human-readable text."""
    return result.to_response_string()

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

