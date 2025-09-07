"""
Core RM Layer for RM-DDD SDK.

This module provides the foundational Reflective Module (RM) functionality
that enables systematic development with built-in health monitoring,
registry integration, and compliance validation.
"""

from .base import ReflectiveModuleBase, DomainReflectiveModule
from .health import ModuleHealth, DomainHealth, HealthMonitor
from .registry import GlobalRegistry, get_global_registry, ModuleCapability
from .compliance import ComplianceValidator, ValidationResult

__all__ = [
    "ReflectiveModuleBase",
    "DomainReflectiveModule", 
    "ModuleHealth",
    "DomainHealth",
    "HealthMonitor",
    "GlobalRegistry",
    "get_global_registry",
    "ModuleCapability",
    "ComplianceValidator",
    "ValidationResult",
]