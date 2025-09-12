"""
Contexts Core Validation

This module was extracted from contexts_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, DomainBoundaries, ContextMap, ModuleStatus, ModuleCapability
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth

def validate_boundary(self) -> ValidationResult:
    """Validate the context boundary definition."""
    result = ValidationResult(is_valid=True)
    if not self.context_name:
        result.add_error('Context name is required')
    if not self.description:
        result.add_error('Context description is required')
    if not self.core_concepts:
        result.add_warning('No core concepts defined for context')
    if not self.business_capabilities:
        result.add_warning('No business capabilities defined for context')
    return result

def validate_integration(self) -> ValidationResult:
    """Validate the context integration definition."""
    result = ValidationResult(is_valid=True)
    if not self.upstream_context:
        result.add_error('Upstream context is required')
    if not self.downstream_context:
        result.add_error('Downstream context is required')
    if self.upstream_context == self.downstream_context:
        result.add_error('Upstream and downstream contexts cannot be the same')
    if self.relationship_type == ContextRelationshipType.SHARED_KERNEL and self.translation_required:
        result.add_warning("Shared kernel typically doesn't require translation")
    return result

def validate_boundary_integrity(self) -> ValidationResult:
    """
        Validate that the context boundary is properly maintained.
        
        Returns:
            ValidationResult: Validation results
        """
    result = ValidationResult(is_valid=True)
    boundary_result = self._boundary.validate_boundary()
    result.merge(boundary_result)
    for other_context, integration in self._integrations.items():
        integration_result = integration.validate_integration()
        if not integration_result.is_valid:
            result.add_error(f'Invalid integration with {other_context}: {integration_result.errors}')
    if self._boundary_violations:
        result.add_error(f'Boundary violations detected: {self._boundary_violations}')
    return result

def validate_domain_invariants(self):
    """Validate domain invariants."""
    return self.validate_boundary_integrity()

def validate_context_map(self) -> ValidationResult:
    """
        Validate the entire context map.
        
        Returns:
            ValidationResult: Validation results for the context map
        """
    result = ValidationResult(is_valid=True)
    for context_name, context in self._contexts.items():
        context_result = context.validate_boundary_integrity()
        if not context_result.is_valid:
            result.add_error(f'Context {context_name} validation failed: {context_result.errors}')
    for integration in self._global_integrations:
        integration_result = integration.validate_integration()
        if not integration_result.is_valid:
            result.add_error(f'Integration validation failed: {integration_result.errors}')
    circular_deps = self._detect_circular_dependencies()
    if circular_deps:
        result.add_warning(f'Circular dependencies detected: {circular_deps}')
    return result

def validate_domain_invariants(self):
    """Validate domain invariants."""
    return self.validate_context_map()
