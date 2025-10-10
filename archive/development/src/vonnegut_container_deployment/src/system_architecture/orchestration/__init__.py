#!/usr/bin/env python3
"""
System Architecture Orchestration Package

Phase 5: Documentation Orchestration and Validation

This package provides comprehensive orchestration and validation capabilities
for the system architecture documentation generation system.
"""

from .documentation_orchestrator import DocumentationOrchestrator, DocumentationConfig
from .real_time_validator import RealTimeValidator, ValidationRule, ValidationResult
from .validation_checklist_system import (
    ValidationChecklistSystem, 
    ValidationChecklist, 
    ChecklistItem,
    ChecklistItemType,
    ChecklistStatus
)
from .performance_monitor import (
    PerformanceMonitor,
    PerformanceMetric,
    PerformanceBenchmark,
    OptimizationRecommendation
)

__all__ = [
    # Documentation Orchestrator
    'DocumentationOrchestrator',
    'DocumentationConfig',
    
    # Real-time Validator
    'RealTimeValidator',
    'ValidationRule',
    'ValidationResult',
    
    # Validation Checklist System
    'ValidationChecklistSystem',
    'ValidationChecklist',
    'ChecklistItem',
    'ChecklistItemType',
    'ChecklistStatus',
    
    # Performance Monitor
    'PerformanceMonitor',
    'PerformanceMetric',
    'PerformanceBenchmark',
    'OptimizationRecommendation'
]

__version__ = "1.0.0"
__author__ = "System Architecture Team"
__description__ = "Documentation orchestration and validation system"