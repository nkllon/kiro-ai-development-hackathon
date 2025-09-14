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

def _add_validation_helpers(cls: Type):
    """Add validation helper methods to a class."""

    def validate_state(self) -> ValidationResult:
        """Validate current state of the object."""
        result = ValidationResult(is_valid=True)
        if hasattr(self, 'id') and (not self.id):
            result.add_error('Entity ID is required')
        return result
    cls._validate_state = validate_state
