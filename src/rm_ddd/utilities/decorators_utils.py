"""
Decorators Utils

This module was extracted from decorators.py
as part of RM-DDD compliance refactoring.
"""

import functools
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from ..core.compliance import ValidationResult
from ..models import DomainException, ValidationException, InvariantViolationException
from ..domain.entities import Entity, AggregateRoot
from ..domain.services import DomainService
from ..domain.value_objects import ValueObject
from ..domain.events import DomainEvent
from datetime import datetime
from src.rm_ddd.core.health import ModuleHealth


def _add_validation_helpers(cls: Type):
    """Add validation helper methods to a class."""

    def validate_state(self) -> ValidationResult:
        """Validate current state of the object."""
        result = ValidationResult(is_valid=True)
        if hasattr(self, 'id') and (not self.id):
            result.add_error('Entity ID is required')
        return result
    cls._validate_state = validate_state

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

