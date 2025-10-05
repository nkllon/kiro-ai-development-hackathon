"""
Cleanup orchestration module for Technical Debt Patch Annotation System.

This module provides systematic cleanup planning and execution for technical debt patches,
including component-based grouping, dependency-aware ordering, and validation frameworks.
"""

from .orchestrator import (
    ForwardPassOrchestrator,
    CleanupPlan,
    CleanupTask,
    CleanupCriteria,
    RollbackPlan,
    CleanupStatus,
    RiskLevel,
    ValidationResult as CleanupValidationResult
)

__all__ = [
    'ForwardPassOrchestrator',
    'CleanupPlan', 
    'CleanupTask',
    'CleanupCriteria',
    'RollbackPlan',
    'CleanupStatus',
    'RiskLevel',
    'CleanupValidationResult'
]