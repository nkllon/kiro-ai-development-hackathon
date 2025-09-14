"""
Git Provider Core Core Utils

This module was extracted from git_provider_core_core.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from src.rm_ddd.core.health import ModuleHealth


def format_commit_message(self, message: str) -> str:
    """
        Format commit message according to best practices.
        
        Args:
            message: Raw commit message
            
        Returns:
            Formatted commit message
        """
    lines = message.strip().split('\n')
    if not lines:
        return ''
    first_line = lines[0][:72] if len(lines[0]) > 72 else lines[0]
    if len(lines) == 1:
        return first_line
    formatted_lines = [first_line]
    if len(lines) > 1 and lines[1].strip():
        formatted_lines.append('')
    formatted_lines.extend(lines[1:])
    return '\n'.join(formatted_lines)

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

