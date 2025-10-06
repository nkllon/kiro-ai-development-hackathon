"""
Core components of the Spec Mode Framework.

This module contains the fundamental building blocks of the systematic
specification-driven development framework.
"""

from .specification_engine import SpecificationEngine
from .models import (
    Specification,
    Requirement,
    AcceptanceCriterion,
    Design,
    Task,
    TraceabilityMatrix,
    ValidationResults,
    SpecificationDependency,
    CrossSpecImpactAnalysis,
    ComplianceMetadata,
    AuditTrail,
    SecurityRequirement,
    PerformanceRequirement
)

__all__ = [
    "SpecificationEngine",
    "Specification",
    "Requirement",
    "AcceptanceCriterion", 
    "Design",
    "Task",
    "TraceabilityMatrix",
    "ValidationResults",
    "SpecificationDependency",
    "CrossSpecImpactAnalysis",
    "ComplianceMetadata",
    "AuditTrail",
    "SecurityRequirement",
    "PerformanceRequirement"
]