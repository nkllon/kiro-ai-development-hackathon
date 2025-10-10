"""
Technical Debt Classification Module

This module provides classification and impact assessment capabilities for
technical debt patches, including severity assessment, component-level
aggregation, and automated alerting.
"""

from .debt_classifier import (
    DebtClassifier,
    ComponentImpact,
    DebtHotspot,
    MaintenanceBurden,
    RiskAssessment,
    ImpactAssessmentEngine
)

__all__ = [
    'DebtClassifier',
    'ComponentImpact', 
    'DebtHotspot',
    'MaintenanceBurden',
    'RiskAssessment',
    'ImpactAssessmentEngine'
]