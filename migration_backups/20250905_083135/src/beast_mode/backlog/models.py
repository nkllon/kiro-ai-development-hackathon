"""Data models for OpenFlow Backlog Management System

This module defines immutable dataclasses for all core data structures
used in the backlog management system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from .enums import (
    StrategicTrack,
    DependencyType,
    RiskLevel,
    BeastReadinessStatus,
    ApprovalStatus,
    StakeholderType,
)


@dataclass(frozen=True)
class Requirement:
    """A single requirement for a backlog item"""
    requirement_id: str
    description: str
    priority: int
    acceptance_criteria: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.requirement_id.strip():
            raise ValueError("Requirement ID cannot be empty")
        if not self.description.strip():
            raise ValueError("Requirement description cannot be empty")
        if self.priority < 1:
            raise ValueError("Priority must be positive")


@dataclass(frozen=True)
class AcceptanceCriterion:
    """A testable acceptance criterion for a backlog item"""
    criterion_id: str
    description: str
    testable: bool = True
    measurable: bool = True
    
    def __post_init__(self):
        if not self.criterion_id.strip():
            raise ValueError("Criterion ID cannot be empty")
        if not self.description.strip():
            raise ValueError("Criterion description cannot be empty")

@dataclass(frozen=True)
class DependencyReference:
    """Reference to a dependency from a backlog item"""
    dependency_id: str
    target_item_id: str
    description: str
    
    def __post_init__(self):
        if not self.dependency_id.strip():
            raise ValueError("Dependency ID cannot be empty")
        if not self.target_item_id.strip():
            raise ValueError("Target item ID cannot be empty")


@dataclass(frozen=True)
class GhostbustersValidation:
    """Ghostbusters multi-perspective validation result"""
    validation_id: str
    validated_by: str
    validation_timestamp: datetime
    perspectives_validated: List[StakeholderType]
    gaps_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    overall_score: float = 0.0
    passed: bool = False
    
    def __post_init__(self):
        if not self.validation_id.strip():
            raise ValueError("Validation ID cannot be empty")
        if not (0.0 <= self.overall_score <= 1.0):
            raise ValueError("Overall score must be between 0.0 and 1.0")


@dataclass(frozen=True)
class MPMValidation:
    """MPM validation result for backlog item quality"""
    validation_id: str
    validated_by: str
    validation_timestamp: datetime
    completeness_score: float
    dependency_confidence: float
    business_alignment: float
    beast_readiness_assessment: str
    required_improvements: List[str] = field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    
    def __post_init__(self):
        if not self.validation_id.strip():
            raise ValueError("Validation ID cannot be empty")
        if not self.validated_by.strip():
            raise ValueError("Validated by cannot be empty")
        if not (0.0 <= self.completeness_score <= 1.0):
            raise ValueError("Completeness score must be between 0.0 and 1.0")
        if not (0.0 <= self.dependency_confidence <= 1.0):
            raise ValueError("Dependency confidence must be between 0.0 and 1.0")
        if not (0.0 <= self.business_alignment <= 1.0):
            raise ValueError("Business alignment must be between 0.0 and 1.0")
        if not self.beast_readiness_assessment.strip():
            raise ValueError("Beast readiness assessment cannot be empty")


@dataclass(frozen=True)
class DependencySpec:
    """Specification for a dependency between backlog items"""
    dependency_id: str
    dependency_type: DependencyType
    target_item_id: str
    target_track: Optional[StrategicTrack]
    satisfaction_criteria: str
    estimated_completion: Optional[datetime]
    risk_level: RiskLevel
    mitigation_strategy: Optional[str] = None
    
    def __post_init__(self):
        if not self.dependency_id.strip():
            raise ValueError("Dependency ID cannot be empty")
        if not self.target_item_id.strip():
            raise ValueError("Target item ID cannot be empty")
        if not self.satisfaction_criteria.strip():
            raise ValueError("Satisfaction criteria cannot be empty")


@dataclass(frozen=True)
class BacklogItem:
    """Core backlog item with all required metadata"""
    item_id: str
    title: str
    track: StrategicTrack
    requirements: List[Requirement]
    acceptance_criteria: List[AcceptanceCriterion]
    dependencies: List[DependencyReference]
    beast_readiness_status: BeastReadinessStatus
    created_by: str
    created_at: datetime
    last_updated: datetime
    mpm_validation: Optional[MPMValidation] = None
    ghostbusters_validation: Optional[GhostbustersValidation] = None
    
    def __post_init__(self):
        if not self.item_id.strip():
            raise ValueError("Item ID cannot be empty")
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.created_by.strip():
            raise ValueError("Created by cannot be empty")
        if self.created_at > datetime.now():
            raise ValueError("Created at cannot be in the future")
        if self.last_updated < self.created_at:
            raise ValueError("Last updated cannot be before created at")