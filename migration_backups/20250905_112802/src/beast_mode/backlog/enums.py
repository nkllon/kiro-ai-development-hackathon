"""Enums for OpenFlow Backlog Management System

This module defines all enums used throughout the backlog management system
for type safety and consistency.
"""

from enum import Enum


class StrategicTrack(Enum):
    """Strategic development tracks for OpenFlow-Playground"""
    PR_GATE = "pr_gate"
    ZERO_FRICTION = "zero_friction"
    COMMUNITY = "community"
    PROOF_ENGINE = "proof_engine"


class DependencyType(Enum):
    """Types of dependencies between backlog items"""
    BLOCKING = "blocking"
    INFORMATIONAL = "informational"
    RESOURCE_SHARED = "resource_shared"


class RiskLevel(Enum):
    """Risk levels for dependencies and backlog items"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BeastReadinessStatus(Enum):
    """Status levels for beast-readiness of backlog items"""
    DRAFT = "draft"
    MPM_REVIEW = "mpm_review"
    GHOSTBUSTERS_VALIDATION = "ghostbusters_validation"
    BEAST_READY = "beast_ready"
    IN_EXECUTION = "in_execution"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class ApprovalStatus(Enum):
    """Approval status for MPM validation"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class StakeholderType(Enum):
    """Types of stakeholders in the system"""
    MPM = "mpm"
    BEAST = "beast"
    STAKEHOLDER = "stakeholder"
    ADMIN = "admin"
    DEVELOPER = "developer"
    OPERATIONS = "operations"
    SECURITY = "security"