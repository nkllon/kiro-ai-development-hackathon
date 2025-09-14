"""
Event Sourcing Core Core Validation

This module was extracted from event_sourcing_core_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, DomainBoundaries, ModuleStatus, ModuleCapability
from .events import DomainEvent, EventStream
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth
from ..core.health import ModuleHealth

def validate_domain_invariants(self):
    """Validate domain invariants."""
    result = ValidationResult(is_valid=True)
    if self.snapshot_frequency <= 0:
        result.add_error('Snapshot frequency must be positive')
    return result
