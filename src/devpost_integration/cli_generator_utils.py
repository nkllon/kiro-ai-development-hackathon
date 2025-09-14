"""
Cli Generator Utils

This module was extracted from cli_generator.py
as part of RM-DDD compliance refactoring.
"""

import ast
import inspect
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, ModuleConfiguration, register_module
from .reflective_module import ReflectiveModuleRegistry

class DetectformatClass:
    """Auto-generated class for functions."""

    def detect_format(self, input_data: bytes) -> str:
        """Auto-detect input format"""
        try:
            json.loads(input_data.decode('utf-8'))
            return 'json'
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                input_data.decode('utf-8')
                return 'text'
            except UnicodeDecodeError:
                return 'binary'

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

