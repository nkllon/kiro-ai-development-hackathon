"""
Systematic PDCA Orchestrator - Core Data Models

Foundational data structures for Plan-Do-Check-Act cycle execution
with systematic validation and model-driven intelligence.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
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
    """Systematic validation confidence levels"""
    HIGH = "high"          # Full systematic validation with model registry
    MEDIUM = "medium"      # Basic systematic validation
    LOW = "low"           # Degraded validation mode
    UNKNOWN = "unknown"   # Validation not performed


@dataclass
class Requirement:
    """Individual requirement specification"""
    req_id: str
    description: str
    domain: str
    priority: int
    acceptance_criteria: List[str]
    validation_method: str


@dataclass
class Constraint:
    """System or domain constraint"""
    constraint_id: str
    description: str
    constraint_type: str  # "technical", "business", "regulatory"
    impact_level: int     # 1-5 scale
    mitigation_strategy: Optional[str] = None


@dataclass
class Criterion:
    """Success criterion for validation"""
    criterion_id: str
    description: str
    measurement_method: str
    target_value: Any
    tolerance: Optional[float] = None


@dataclass
class Pattern:
    """Systematic pattern for reuse"""
    pattern_id: str
    name: str
    domain: str
    description: str
    implementation_steps: List[str]
    success_metrics: Dict[str, float]
    confidence_score: float


@dataclass
class Tool:
    """Domain-specific tool specification"""
    tool_id: str
    name: str
    domain: str
    purpose: str
    command_template: str
    validation_method: str


@dataclass
class PDCATask:
    """Core PDCA task specification"""
    task_id: str
    description: str
    domain: str
    requirements: List[Requirement]
    constraints: List[Constraint]
    success_criteria: List[Criterion]
    estimated_complexity: int  # 1-10 scale
    created_at: datetime = field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.PENDING
    
    def __post_init__(self):
        """Validate task specification"""
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.description:
            raise ValueError("description is required")
        if not self.domain:
            raise ValueError("domain is required")


@dataclass
class PlanResult:
    """Result of PDCA Plan phase"""
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
    """Result of PDCA Do phase"""
    task_id: str
    implementation_artifacts: List[str]
    systematic_compliance: float  # 0.0-1.0 score
    execution_metrics: Dict[str, Any]
    tools_used: List[str]
    deviations_from_plan: List[str]
    actual_duration: timedelta
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CheckResult:
    """Result of PDCA Check phase"""
    task_id: str
    validation_results: Dict[str, bool]
    systematic_score: float  # 0.0-1.0 systematic vs ad-hoc
    rca_findings: List[str]
    quality_metrics: Dict[str, float]
    validation_level: ValidationLevel
    ghostbusters_consensus: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ActResult:
    """Result of PDCA Act phase"""
    task_id: str
    learning_patterns: List[Pattern]
    model_registry_updates: List[str]
    improvement_recommendations: List[str]
    success_rate_improvement: float
    knowledge_artifacts: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PDCAResult:
    """Complete PDCA cycle result"""
    task_id: str
    plan_result: PlanResult
    do_result: DoResult
    check_result: CheckResult
    act_result: ActResult
    cycle_duration: timedelta
    systematic_score: float  # Overall systematic vs ad-hoc score
    success_rate: float      # Task success rate
    improvement_factor: float # Improvement over ad-hoc approach
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_phase_result(self, phase: PDCAPhase) -> Any:
        """Get result for specific PDCA phase"""
        phase_map = {
            PDCAPhase.PLAN: self.plan_result,
            PDCAPhase.DO: self.do_result,
            PDCAPhase.CHECK: self.check_result,
            PDCAPhase.ACT: self.act_result
        }
        return phase_map.get(phase)


@dataclass
class ModelIntelligence:
    """Model registry intelligence for domain"""
    domain: str
    requirements: List[Requirement]
    patterns: List[Pattern]
    tools: Dict[str, Tool]
    success_metrics: Dict[str, float]
    confidence_score: float
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_tool_by_purpose(self, purpose: str) -> Optional[Tool]:
        """Get tool by purpose description"""
        for tool in self.tools.values():
            if purpose.lower() in tool.purpose.lower():
                return tool
        return None


class ReflectiveModule(ABC):
    """
    Base interface for systematic health monitoring
    
    All Beast Mode components inherit from this to provide
    systematic health reporting and status interfaces.
    """
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Return current health status"""
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, float]:
        """Return performance metrics"""
        pass
    
    @abstractmethod
    def validate_systematic_compliance(self) -> ValidationLevel:
        """Validate systematic approach compliance"""
        pass
    
    def get_module_info(self) -> Dict[str, str]:
        """Return module identification info"""
        return {
            "module_name": self.__class__.__name__,
            "module_type": "ReflectiveModule",
            "systematic_approach": "PDCA-driven",
            "created_at": datetime.now().isoformat()
        }


# Utility functions for PDCA data model operations

def create_basic_task(task_id: str, description: str, domain: str) -> PDCATask:
    """Create a basic PDCA task with minimal requirements"""
    return PDCATask(
        task_id=task_id,
        description=description,
        domain=domain,
        requirements=[],
        constraints=[],
        success_criteria=[],
        estimated_complexity=5  # Medium complexity default
    )


def calculate_systematic_score(plan_score: float, do_score: float, 
                             check_score: float, act_score: float) -> float:
    """Calculate overall systematic score from phase scores"""
    weights = {"plan": 0.25, "do": 0.35, "check": 0.25, "act": 0.15}
    return (plan_score * weights["plan"] + 
            do_score * weights["do"] + 
            check_score * weights["check"] + 
            act_score * weights["act"])


def validate_pdca_result(result: PDCAResult) -> List[str]:
    """Validate PDCA result completeness and consistency"""
    issues = []
    
    if not result.task_id:
        issues.append("Missing task_id")
    
    if result.systematic_score < 0.0 or result.systematic_score > 1.0:
        issues.append("systematic_score must be between 0.0 and 1.0")
    
    if result.success_rate < 0.0 or result.success_rate > 1.0:
        issues.append("success_rate must be between 0.0 and 1.0")
    
    if result.cycle_duration.total_seconds() <= 0:
        issues.append("cycle_duration must be positive")
    
    return issues