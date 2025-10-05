#!/usr/bin/env python3
"""
PDCA Models - Core Data Models for Plan-Do-Check-Act Cycles

This module provides the core data models and interfaces for systematic
PDCA cycle execution in the Beast Mode framework.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Core PDCA data models and validation
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class PDCAPhase(Enum):
    """PDCA cycle phases"""
    PLAN = "plan"
    DO = "do"
    CHECK = "check"
    ACT = "act"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationLevel(Enum):
    """Validation rigor levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Requirement:
    """A requirement for a task"""
    req_id: str
    description: str
    priority: int = 1
    domain: str = "general"
    validation_criteria: List[str] = field(default_factory=list)


@dataclass
class Constraint:
    """A constraint for a task"""
    constraint_id: str
    description: str
    constraint_type: str = "general"
    severity: str = "medium"
    domain: str = "general"


@dataclass
class Criterion:
    """A success criterion for a task"""
    criterion_id: str
    description: str
    measurement_type: str = "boolean"
    threshold: Optional[float] = None
    domain: str = "general"


@dataclass
class Pattern:
    """A pattern for systematic implementation"""
    pattern_id: str
    name: str
    description: str
    domain: str
    confidence_score: float = 0.8
    usage_count: int = 0


@dataclass
class Tool:
    """A tool for task execution"""
    tool_id: str
    name: str
    domain: str
    purpose: str
    command_template: str
    validation_method: str = "exit_code"
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class ModelIntelligence:
    """Model intelligence for systematic planning"""
    domain: str
    requirements: List[Requirement]
    patterns: List[Pattern]
    tools: Dict[str, Tool]
    success_metrics: Dict[str, float]
    confidence_score: float

    def get_tool_by_purpose(self, purpose: str) -> Optional[Tool]:
        """Find tool by purpose (exact or partial match)"""
        for tool in self.tools.values():
            if purpose.lower() in tool.purpose.lower():
                return tool
        return None


@dataclass
class PDCATask:
    """A task for PDCA cycle execution"""
    task_id: str
    description: str
    domain: str
    requirements: List[Requirement]
    constraints: List[Constraint]
    success_criteria: List[Criterion]
    estimated_complexity: int = 5
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task data after initialization"""
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.description:
            raise ValueError("description is required")
        if not self.domain:
            raise ValueError("domain is required")


@dataclass
class PlanResult:
    """Result of the PLAN phase"""
    task_id: str
    systematic_approach: str
    implementation_steps: List[str]
    resource_requirements: List[str]
    risk_assessment: Dict[str, str]
    model_intelligence_used: List[str]
    confidence_score: float
    estimated_duration: timedelta
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DoResult:
    """Result of the DO phase"""
    task_id: str
    implementation_artifacts: List[str]
    systematic_compliance: float
    execution_metrics: Dict[str, Union[int, float]]
    tools_used: List[str]
    deviations_from_plan: List[str]
    actual_duration: timedelta
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CheckResult:
    """Result of the CHECK phase"""
    task_id: str
    validation_results: Dict[str, bool]
    systematic_score: float
    rca_findings: List[str]
    quality_metrics: Dict[str, float]
    validation_level: ValidationLevel
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ActResult:
    """Result of the ACT phase"""
    task_id: str
    learning_patterns: List[str]
    model_registry_updates: List[str]
    improvement_recommendations: List[str]
    success_rate_improvement: float
    knowledge_artifacts: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PDCAResult:
    """Complete result of a PDCA cycle"""
    task_id: str
    plan_result: PlanResult
    do_result: DoResult
    check_result: CheckResult
    act_result: ActResult
    cycle_duration: timedelta
    systematic_score: float
    success_rate: float
    improvement_factor: float
    created_at: datetime = field(default_factory=datetime.now)

    def get_phase_result(self, phase: PDCAPhase) -> Union[PlanResult, DoResult, CheckResult, ActResult]:
        """Get result for a specific PDCA phase"""
        if phase == PDCAPhase.PLAN:
            return self.plan_result
        elif phase == PDCAPhase.DO:
            return self.do_result
        elif phase == PDCAPhase.CHECK:
            return self.check_result
        elif phase == PDCAPhase.ACT:
            return self.act_result
        else:
            raise ValueError(f"Unknown PDCA phase: {phase}")


class ReflectiveModule(ABC):
    """Abstract base class for reflective modules"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module_id = f"{module_name}_{id(self)}"
        self.logger = logging.getLogger(f"{__name__}.{module_name}")

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get module health status"""
        pass

    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get module performance metrics"""
        pass

    @abstractmethod
    def validate_systematic_compliance(self) -> ValidationLevel:
        """Validate systematic compliance"""
        pass

    def get_module_info(self) -> Dict[str, Any]:
        """Get basic module information"""
        return {
            "module_name": self.module_name,
            "module_type": self.__class__.__name__,
            "systematic_approach": "PDCA-driven"
        }

    def register_module(self, registry: Any) -> None:
        """Register module with registry"""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)

    def get_interface_metadata(self) -> Dict[str, Any]:
        """Get interface metadata for registry"""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }


# Utility Functions

def create_basic_task(task_id: str, description: str, domain: str, 
                     complexity: int = 5) -> PDCATask:
    """Create a basic PDCA task with minimal requirements"""
    return PDCATask(
        task_id=task_id,
        description=description,
        domain=domain,
        requirements=[],
        constraints=[],
        success_criteria=[],
        estimated_complexity=complexity
    )


def calculate_systematic_score(plan_score: float, do_score: float, 
                              check_score: float, act_score: float) -> float:
    """Calculate weighted systematic score from phase scores"""
    # Weighted average: plan(25%), do(35%), check(25%), act(15%)
    weights = [0.25, 0.35, 0.25, 0.15]
    scores = [plan_score, do_score, check_score, act_score]
    
    return sum(score * weight for score, weight in zip(scores, weights))


def validate_pdca_result(result: PDCAResult) -> List[str]:
    """Validate PDCA result and return list of issues"""
    issues = []
    
    # Validate task_id
    if not result.task_id:
        issues.append("task_id is required")
    
    # Validate cycle duration
    if result.cycle_duration.total_seconds() < 0:
        issues.append("cycle_duration cannot be negative")
    
    # Validate systematic score
    if not 0.0 <= result.systematic_score <= 1.0:
        issues.append("systematic_score must be between 0.0 and 1.0")
    
    # Validate success rate
    if not 0.0 <= result.success_rate <= 1.0:
        issues.append("success_rate must be between 0.0 and 1.0")
    
    # Validate improvement factor
    if result.improvement_factor < 0.0:
        issues.append("improvement_factor cannot be negative")
    
    # Validate phase results have matching task_ids
    phase_results = [
        result.plan_result,
        result.do_result,
        result.check_result,
        result.act_result
    ]
    
    for phase_result in phase_results:
        if hasattr(phase_result, 'task_id') and phase_result.task_id != result.task_id:
            issues.append(f"Phase result task_id mismatch: {phase_result.task_id} != {result.task_id}")
    
    return issues


# Module Health Interface
class ModuleHealth:
    """Mixin for modules that provide health monitoring"""
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status - to be implemented by subclasses"""
        return {"status": "unknown", "uptime": "0h"}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics - to be implemented by subclasses"""
        return {"response_time": 0.0, "throughput": 0.0}
    
    def validate_systematic_compliance(self) -> ValidationLevel:
        """Validate systematic compliance - to be implemented by subclasses"""
        return ValidationLevel.MEDIUM