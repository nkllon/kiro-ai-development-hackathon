"""
Model Registry Utils

This module was extracted from model_registry.py
as part of RM-DDD compliance refactoring.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from .pdca_models import ModelIntelligence, Requirement, Pattern, Tool, ValidationLevel, ReflectiveModule
from src.rm_ddd.core.health import ModuleHealth


class GettoolmappingsClass:
    """Auto-generated class for functions."""

    def get_tool_mappings(self, domain: str) -> Dict[str, Tool]:
    """Get domain-specific tool mappings"""
    if domain in self.intelligence_cache:
    return self.intelligence_cache[domain].tools
    tools = {}
    if 'testing' in domain.lower() or 'test' in domain.lower():
    tools['pytest'] = Tool(tool_id=f'{domain}-pytest', name='pytest', domain=domain, purpose='systematic unit testing', command_template='pytest {test_path} -v --cov={module}', validation_method='exit_code_and_coverage')
    if 'code' in domain.lower() or 'implementation' in domain.lower():
    tools['black'] = Tool(tool_id=f'{domain}-black', name='black', domain=domain, purpose='systematic code formatting', command_template='black {file_path} --check', validation_method='exit_code')
    tools['mypy'] = Tool(tool_id=f'{domain}-mypy', name='mypy', domain=domain, purpose='systematic type checking', command_template='mypy {file_path}', validation_method='exit_code_and_output')
    return tools

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

