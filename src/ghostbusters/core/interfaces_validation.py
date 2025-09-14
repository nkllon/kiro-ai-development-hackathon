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
