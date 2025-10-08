"""
Spec Mode Framework - Systematic Specification-Driven Development

A comprehensive framework for creating, managing, and executing feature specifications
with full traceability from requirements to implementation.

Based on the proven methodology demonstrated in the RM-DDD reference implementation.
"""

from .core.specification_engine import SpecificationEngine
from .core.models import (
    Specification,
    Requirement,
    AcceptanceCriterion,
    Design,
    Task,
    TraceabilityMatrix,
    ValidationResults
)
from .managers.requirements_manager import RequirementsManager
from .generators.design_generator import DesignGenerator
from .orchestrators.task_orchestrator import TaskOrchestrator
from .systems.traceability_system import TraceabilitySystem
from .engines.validation_engine import ValidationEngine

__version__ = "0.1.0"
__author__ = "Spec Mode Framework Team"

__all__ = [
    "SpecificationEngine",
    "Specification",
    "Requirement", 
    "AcceptanceCriterion",
    "Design",
    "Task",
    "TraceabilityMatrix",
    "ValidationResults",
    "RequirementsManager",
    "DesignGenerator",
    "TaskOrchestrator",
    "TraceabilitySystem",
    "ValidationEngine"
]