"""
Shared Kernel Core Core Validation

This module was extracted from shared_kernel_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union
from uuid import UUID, uuid4
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, DomainBoundaries, ModuleStatus, ModuleCapability
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth

def validate_element(self) -> ValidationResult:
    """Validate the shared element."""
    result = ValidationResult(is_valid=True)
    if not self.name:
        result.add_error('Shared element name is required')
    if not self.description:
        result.add_warning('Shared element description is recommended')
    if not self.owner_context:
        result.add_error('Shared element must have an owner context')
    if not self.consumer_contexts:
        result.add_warning('Shared element has no consumer contexts')
    return result

def validate_change(self) -> ValidationResult:
    """Validate the change proposal."""
    result = ValidationResult(is_valid=True)
    if not self.change_type:
        result.add_error('Change type is required')
    if not self.description:
        result.add_error('Change description is required')
    if self.impact_level == ChangeImpact.BREAKING and (not self.migration_guide):
        result.add_error('Breaking changes must include migration guide')
    if not self.proposed_by:
        result.add_error('Change must specify who proposed it')
    return result

def validate_domain_invariants(self):
    """Validate domain invariants."""
    result = ValidationResult(is_valid=True)
    for element in self._elements.values():
        element_result = element.validate_element()
        if not element_result.is_valid:
            result.add_error(f'Invalid element {element.name}: {element_result.errors}')
    for change in self._changes.values():
        change_result = change.validate_change()
        if not change_result.is_valid:
            result.add_error(f'Invalid change {change.change_id}: {change_result.errors}')
    return result

def validate_domain_invariants(self):
    """Validate domain invariants."""
    result = ValidationResult(is_valid=True)
    conflicts = self.detect_conflicts()
    if conflicts:
        result.add_error(f'Conflicts detected: {len(conflicts)} conflicts found')
    return result
