#!/usr/bin/env python3
"""
PDCA Orchestrator Validation
============================

Data classes and validation logic for the Systematic PDCA Orchestrator.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Define PDCA cycle data structures and validation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class PDCATask:
    """Represents a development task for PDCA execution."""

    task_id: str
    name: str
    description: str
    domain: str
    complexity: str = "medium"
    priority: str = "normal"
    estimated_duration: Optional[timedelta] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanResult:
    """Result of the PLAN phase."""

    task_id: str
    plan_items: List[str]
    estimated_complexity: str
    domain_requirements: Dict[str, Any]
    systematic_score: float
    summary: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DoResult:
    """Result of the DO phase."""

    task_id: str
    implementation_steps: List[str]
    quality_metrics: Dict[str, Any]
    systematic_score: float
    summary: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CheckResult:
    """Result of the CHECK phase."""

    task_id: str
    validation_results: Dict[str, Any]
    success_rate: float
    issues: List[str]
    rca_findings: List[str]
    systematic_score: float
    summary: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ActResult:
    """Result of the ACT phase."""

    task_id: str
    lessons_learned: List[str]
    registry_updates: Dict[str, Any]
    improvements: List[str]
    systematic_score: float
    summary: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PDCAResult:
    """Complete result of a PDCA cycle."""

    task_id: str
    plan_result: PlanResult
    do_result: DoResult
    check_result: CheckResult
    act_result: ActResult
    cycle_duration: timedelta
    systematic_score: float
    success_rate: float
    improvement_factor: float
    lessons_learned: List[str]
    created_at: datetime = field(default_factory=datetime.now)


class PDCAValidator:
    """Validation logic for PDCA cycles."""

    @staticmethod
    def validate_task(task: PDCATask) -> List[str]:
        """Validate a PDCA task."""
        issues = []

        if not task.task_id:
            issues.append("Task ID is required")

        if not task.name:
            issues.append("Task name is required")

        if not task.description:
            issues.append("Task description is required")

        if not task.domain:
            issues.append("Task domain is required")

        if task.complexity not in ["low", "medium", "high", "critical"]:
            issues.append("Task complexity must be low, medium, high, or critical")

        return issues

    @staticmethod
    def validate_plan_result(plan_result: PlanResult) -> List[str]:
        """Validate a plan result."""
        issues = []

        if not plan_result.plan_items:
            issues.append("Plan items are required")

        if plan_result.systematic_score < 0.0 or plan_result.systematic_score > 1.0:
            issues.append("Systematic score must be between 0.0 and 1.0")

        if not plan_result.summary:
            issues.append("Plan summary is required")

        return issues

    @staticmethod
    def validate_do_result(do_result: DoResult) -> List[str]:
        """Validate a do result."""
        issues = []

        if not do_result.implementation_steps:
            issues.append("Implementation steps are required")

        if do_result.systematic_score < 0.0 or do_result.systematic_score > 1.0:
            issues.append("Systematic score must be between 0.0 and 1.0")

        return issues

    @staticmethod
    def validate_check_result(check_result: CheckResult) -> List[str]:
        """Validate a check result."""
        issues = []

        if check_result.success_rate < 0.0 or check_result.success_rate > 1.0:
            issues.append("Success rate must be between 0.0 and 1.0")

        if check_result.systematic_score < 0.0 or check_result.systematic_score > 1.0:
            issues.append("Systematic score must be between 0.0 and 1.0")

        return issues

    @staticmethod
    def validate_act_result(act_result: ActResult) -> List[str]:
        """Validate an act result."""
        issues = []

        if not act_result.lessons_learned:
            issues.append("Lessons learned are required")

        if act_result.systematic_score < 0.0 or act_result.systematic_score > 1.0:
            issues.append("Systematic score must be between 0.0 and 1.0")

        return issues

    @staticmethod
    def validate_pdca_result(pdca_result: PDCAResult) -> List[str]:
        """Validate a complete PDCA result."""
        issues = []

        # Validate individual phase results
        issues.extend(PDCAValidator.validate_plan_result(pdca_result.plan_result))
        issues.extend(PDCAValidator.validate_do_result(pdca_result.do_result))
        issues.extend(PDCAValidator.validate_check_result(pdca_result.check_result))
        issues.extend(PDCAValidator.validate_act_result(pdca_result.act_result))

        # Validate overall result
        if pdca_result.systematic_score < 0.0 or pdca_result.systematic_score > 1.0:
            issues.append("Overall systematic score must be between 0.0 and 1.0")

        if pdca_result.success_rate < 0.0 or pdca_result.success_rate > 1.0:
            issues.append("Overall success rate must be between 0.0 and 1.0")

        if pdca_result.improvement_factor < 0.0:
            issues.append("Improvement factor must be non-negative")

        if not pdca_result.lessons_learned:
            issues.append("Lessons learned are required")

        return issues
