"""
Entities Core Core Validation

This module was extracted from entities_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID, uuid4
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import ModuleStatus, ModuleCapability, DomainBoundaries, AggregateBoundaries, EntityId, AggregateId, DomainException, InvariantViolationException
from ..core.health import ModuleHealth

class ValidateaggregateconstraintsClass:
    """Auto-generated class for functions."""

    def validate_aggregate_constraints(self) -> ValidationResult:
    """
    Validate aggregate-specific constraints.

    Returns:
    ValidationResult: Result of aggregate constraint validation
    """
    result = ValidationResult(is_valid=True)
    current_size = self.get_aggregate_size()
    if current_size > self._max_size:
    result.add_error(f'Aggregate size {current_size} exceeds maximum {self._max_size}', code='AGG_001', component=self.__class__.__name__, context={'current_size': current_size, 'max_size': self._max_size})
    try:
    boundaries = self.get_aggregate_boundaries()
    if not boundaries.aggregate_type:
    result.add_error('Aggregate boundaries must specify aggregate_type', code='AGG_002', component=self.__class__.__name__)
    except Exception as e:
    result.add_error(f'Failed to get aggregate boundaries: {str(e)}', code='AGG_002', component=self.__class__.__name__)
    for entity_type, entities in self._child_entities.items():
    for i, entity in enumerate(entities):
    try:
    child_validation = entity.validate_domain_invariants()
    if not child_validation.is_valid:
    result.add_error(f'Child entity {entity_type}[{i}] validation failed', code='AGG_003', component=self.__class__.__name__, context={'child_errors': child_validation.errors})
    except Exception as e:
    result.add_error(f'Child entity {entity_type}[{i}] validation error: {str(e)}', code='AGG_003', component=self.__class__.__name__)
    return result

    def validate_domain_invariants(self) -> ValidationResult:
    """
    Validate domain invariants including aggregate constraints.

    Returns:
    ValidationResult: Combined result of entity and aggregate validation
    """
    entity_result = super().validate_domain_invariants()
    aggregate_result = self.validate_aggregate_constraints()
    entity_result.merge(aggregate_result)
    return entity_result

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

