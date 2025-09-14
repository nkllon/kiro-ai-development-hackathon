"""
Complexity Core Core Validation

This module was extracted from complexity_core_core.py
as part of RM-DDD compliance refactoring.
"""

import ast
import inspect
import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, ModuleStatus, ModuleCapability
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
from ..models import DomainBoundaries
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
from ..models import DomainBoundaries
from ..models import DomainBoundaries
from ..core.health import ModuleHealth
from ..models import DomainBoundaries

def validate_domain_invariants(self):
    """Validate domain invariants."""
    result = ValidationResult(is_valid=True)
    summary = self.get_complexity_summary()
    critical_count = len(summary.get('critical_elements', []))
    if critical_count > 0:
        result.add_error(f'Found {critical_count} elements with critical complexity issues')
    avg_score = summary.get('average_score', 0.0)
    if avg_score > 80:
        result.add_warning(f'High average complexity score: {avg_score:.1f}')
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

