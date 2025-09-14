"""
Project Generator Validation

This module was extracted from project_generator.py
as part of RM-DDD compliance refactoring.
"""

import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, ModuleStatus, ModuleCapability
import jinja2
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
from jinja2 import Template

def validate_config(self) -> ValidationResult:
    """Validate project configuration."""
    result = ValidationResult(is_valid=True)
    if not self.project_name:
        result.add_error('Project name is required')
    elif not self.project_name.replace('_', '').replace('-', '').isalnum():
        result.add_error('Project name must be alphanumeric with underscores or hyphens')
    if not self.domain_contexts:
        result.add_warning('No domain contexts specified - will create default context')
    if self.python_version and (not self.python_version.replace('.', '').isdigit()):
        result.add_error('Invalid Python version format')
    return result

def _get_conftest_template(self) -> str:
    return '"""Pytest configuration."""\nimport pytest\n'

def _get_test_entities_template(self) -> str:
    return '"""Tests for domain entities."""\nimport pytest\nfrom src.domain.entities import ExampleEntity\n\ndef test_example_entity_creation():\n    entity = ExampleEntity(name="Test")\n    assert entity.name == "Test"\n'

def _get_test_repositories_template(self) -> str:
    return '"""Integration tests for repositories."""\npass  # Implementation here\n'

def validate_domain_invariants(self):
    """Validate domain invariants."""
    result = ValidationResult(is_valid=True)
    if not self._templates:
        result.add_error('No project templates available')
    for name, template in self._templates.items():
        if not template.get_file_templates():
            result.add_warning(f'Template {name} has no file templates')
    return result

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

