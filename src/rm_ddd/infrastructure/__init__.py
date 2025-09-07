"""
Infrastructure layer separation and anti-corruption utilities.

This module provides tools for enforcing proper layer separation between
domain and infrastructure concerns, preventing architectural violations
and maintaining clean domain boundaries.
"""

from .separation import (
    DependencyValidator,
    LayerViolation,
    LayerSeparationEnforcer,
    validate_dependency_direction,
)
from .anticorruption import (
    AntiCorruptionLayer,
    ContextTranslator,
    DomainAdapter,
    ExternalSystemAdapter,
)

__all__ = [
    "DependencyValidator",
    "LayerViolation", 
    "LayerSeparationEnforcer",
    "validate_dependency_direction",
    "AntiCorruptionLayer",
    "ContextTranslator",
    "DomainAdapter", 
    "ExternalSystemAdapter",
]