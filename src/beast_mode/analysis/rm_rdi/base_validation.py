"""
Base Validation

This module was extracted from base.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import logging
from pathlib import Path
from ...core.reflective_module import ReflectiveModule, HealthStatus
from .data_models import AnalysisResult, AnalysisStatus
from .safety import get_safety_manager, is_safe_to_proceed, SafetyStatus

def validate_analysis_parameters(**kwargs) -> bool:
    """Validate that analysis parameters are safe"""
    unsafe_params = ['write', 'modify', 'delete', 'update', 'create']
    for key, value in kwargs.items():
        key_lower = key.lower()
        if any((unsafe in key_lower for unsafe in unsafe_params)):
            return False
        if isinstance(value, str) and any((unsafe in value.lower() for unsafe in unsafe_params)):
            return False
    return True

def _validate_result_safety(self, result: AnalysisResult) -> bool:
    """Validate that analysis result is safe"""
    if not result.safety_validated:
        return False
    if not result.emergency_shutdown_available:
        return False
    if not result.can_be_safely_ignored:
        return False
    return True

def validate_read_only_access(self, file_path: Path) -> bool:
    """Validate read-only access to a file"""
    return self.safety_manager.safety_validator.validate_read_only_access(file_path)
