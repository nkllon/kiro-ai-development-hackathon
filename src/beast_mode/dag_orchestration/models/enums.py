"""
Enums for DAG orchestration system.
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Task completion status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    SKIPPED = "skipped"


class RiskType(Enum):
    """Types of risks in execution planning."""
    DEPENDENCY_RISK = "dependency_risk"
    RESOURCE_RISK = "resource_risk"
    TECHNICAL_RISK = "technical_risk"
    TIMELINE_RISK = "timeline_risk"
    QUALITY_RISK = "quality_risk"
    INTEGRATION_RISK = "integration_risk"


class RiskImpact(Enum):
    """Impact levels for risks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExecutionStatus(Enum):
    """Execution status for orchestration."""
    PLANNED = "planned"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConsumptionAction(Enum):
    """Actions for consumption decisions."""
    ACCEPT = "accept"
    REJECT = "reject"
    ESCALATE = "escalate"


class OptimizationStrategy(Enum):
    """Optimization strategies for execution."""
    SPEED_OPTIMIZED = "speed_optimized"
    RESOURCE_OPTIMIZED = "resource_optimized"
    QUALITY_OPTIMIZED = "quality_optimized"
    BALANCED = "balanced"


class ParallelizationLevel(Enum):
    """Levels of parallelization."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"