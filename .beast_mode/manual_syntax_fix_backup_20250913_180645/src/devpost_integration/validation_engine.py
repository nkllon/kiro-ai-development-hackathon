#!/usr/bin/env python3
"""
validation_engine - Simplified for size compliance
"""

from .validation_engine_methods import ValidationEngine, ValidationRule, ValidationReport, ValidationIssue, ValidationContext, ValidationSeverity, ValidationCategory, RequiredFieldRule, ContentQualityRule, LinkValidationRule, TeamValidationRule, TagValidationRule
from .reflective_module import ReflectiveModule, register_module
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

def create_default_validation_engine() -> ValidationEngine:
    """Create a default validation engine instance"""
    return ValidationEngine()

def validate_project_metadata(metadata: Dict[str, Any]) -> ValidationReport:
    """Validate project metadata and return validation report"""
    engine = create_default_validation_engine()
    return engine.validate_project(metadata)

# Export all classes and functions
__all__ = [
    'ValidationEngine',
    'ValidationRule', 
    'ValidationReport',
    'ValidationIssue',
    'ValidationContext',
    'ValidationSeverity',
    'ValidationCategory',
    'RequiredFieldRule',
    'ContentQualityRule',
    'LinkValidationRule',
    'TeamValidationRule',
    'TagValidationRule',
    'create_default_validation_engine',
    'validate_project_metadata'
]
