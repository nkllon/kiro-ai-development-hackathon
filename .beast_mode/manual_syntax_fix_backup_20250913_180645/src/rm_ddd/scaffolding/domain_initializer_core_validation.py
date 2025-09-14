"""
Domain Initializer Core Validation

This module was extracted from domain_initializer_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException
from ..core.health import ModuleHealth
from ..models import ModuleStatus
from ..models import ModuleCapability
from ..models import DomainBoundaries
from ..models import DomainBoundaries
from ..core.health import ModuleHealth
from ..models import ModuleStatus
from ..models import ModuleCapability
from ..models import DomainBoundaries

def validate_config(self) -> ValidationResult:
    """Validate bounded context configuration."""
    result = ValidationResult(is_valid=True)
    if not self.context_name:
        result.add_error('Context name is required')
    elif not self.context_name.replace('_', '').isalnum():
        result.add_error('Context name must be alphanumeric with underscores')
    if not self.entities and (not self.value_objects):
        result.add_warning('Context has no entities or value objects defined')
    return result

def validate_domain_invariants(self):
    """Validate domain invariants."""
    result = ValidationResult(is_valid=True)
    for context_result in self._initialized_contexts:
        if not context_result.success:
            result.add_warning(f'Context {context_result.context_name} initialization had errors')
    return result
