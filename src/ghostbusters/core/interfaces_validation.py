"""
Interfaces Validation

This module was extracted from interfaces.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from .models import AnalysisResult, AnalysisContext, Delusion, RecoveryPlan, ValidationResult, ConsensusResult, MultiDimensionalResult, RecoveryAction, ValidationCertificate
from src.rm_ddd.core.health import ModuleHealth


@abstractmethod
class ValidateconfidenceClass:
    """Auto-generated class for functions."""

    def validate_confidence(self, result: AnalysisResult) -> bool:
    """
    Validate that confidence score accurately reflects analysis quality.

    Args:
    result: Analysis result to validate

    Returns:
    True if confidence score is accurate, False otherwise
    """
    pass

    @abstractmethod
    def validate_extension(self, extension: Any) -> ValidationResult:
    """Validate that extension meets framework requirements"""
    pass

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

