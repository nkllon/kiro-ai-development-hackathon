"""
Productivity Triage Data Models
==============================

Core data structures for the Ghostbusters Productivity Triage system.
These models define the shape of our supernatural productivity explosion!

Author: Beast Mode Framework + Ghostbusters  
Date: 2025-09-24
Purpose: Data models for coordinating coordinators
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid


class ArtifactType(Enum):
    """Types of work artifacts we can discover"""
    CODE = "code"
    TEST = "test" 
    SPEC = "spec"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    SCRIPT = "script"
    UNKNOWN = "unknown"


class DomainType(Enum):
    """Beast Mode domain classifications"""
    TASK_QUEUE = "task_queue"
    MCP_INTEGRATIONS = "mcp_integrations"
    RELEASE_AUTOMATION = "release_automation"
    GHOSTBUSTERS = "ghostbusters"
    BEAST_MODE_CORE = "beast_mode_core"
    QUALITY_GATES = "quality_gates"
    MONITORING = "monitoring"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"


class CompletionStatus(Enum):
    """How complete is this work?"""
    COMPLETE = "complete"
    PARTIAL = "partial"
    EXPERIMENTAL = "experimental"
    BROKEN = "broken"
    PLACEHOLDER = "placeholder"
    UNKNOWN = "unknown"


class ReadinessStatus(Enum):
    """How ready is this work for integration?"""
    READY = "ready"
    NEEDS_TESTS = "needs_tests"
    NEEDS_DOCS = "needs_docs"
    HAS_CONFLICTS = "has_conflicts"
    NEEDS_REVIEW = "needs_review"
    NOT_READY = "not_ready"


class ComplexityLevel(Enum):
    """Integration complexity assessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TriageStrategy(Enum):
    """Recommended triage strategies"""
    SYSTEMATIC_INTEGRATION = "systematic_integration"
    SELECTIVE_INTEGRATION = "selective_integration"
    EMERGENCY_PRESERVATION = "emergency_preservation"
    MANUAL_INTERVENTION = "manual_intervention"


class QualityGate(Enum):
    """Quality gates for integration"""
    TEST_SUITE = "test_suite"
    CODE_QUALITY = "code_quality"
    SPEC_COMPLIANCE = "spec_compliance"
    DOCUMENTATION = "documentation"
    SECURITY = "security"


@dataclass
class WorkArtifact:
    """A discovered work artifact in our productivity explosion"""
    path: str
    artifact_type: ArtifactType
    domain: DomainType
    completion_status: CompletionStatus
    integration_readiness: ReadinessStatus
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.now)
    file_size_bytes: int = 0
    last_modified: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate artifact data"""
        if not self.path:
            raise ValueError("WorkArtifact path cannot be empty")
        
        # Generate unique ID for tracking
        if 'artifact_id' not in self.metadata:
            self.metadata['artifact_id'] = str(uuid.uuid4())


@dataclass
class EmergencyThresholds:
    """Thresholds for activating emergency protocols"""
    max_conflicts: int = 10
    max_broken_artifacts: int = 5
    max_integration_time_minutes: int = 60
    min_test_coverage_percent: float = 80.0


@dataclass
class IntegrationStrategy:
    """Strategy configuration for integration"""
    prefer_atomic_commits: bool = True
    require_tests: bool = True
    require_documentation: bool = False
    allow_experimental: bool = False
    max_conflicts_per_group: int = 3


@dataclass
class TriageConfig:
    """Configuration for productivity triage operation"""
    scan_paths: List[str] = field(default_factory=lambda: ["src/", "tests/", ".kiro/specs/", "docs/"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.pyc", "__pycache__", ".git", "node_modules"])
    quality_gates: List[QualityGate] = field(default_factory=lambda: [QualityGate.TEST_SUITE, QualityGate.CODE_QUALITY])
    emergency_thresholds: EmergencyThresholds = field(default_factory=EmergencyThresholds)
    integration_strategy: IntegrationStrategy = field(default_factory=IntegrationStrategy)
    max_artifacts_to_process: int = 1000
    enable_emergency_protocols: bool = True
    
    def __post_init__(self):
        """Validate configuration"""
        if not self.scan_paths:
            raise ValueError("TriageConfig must have at least one scan path")


@dataclass
class FileConflict:
    """A detected file conflict between workstreams"""
    file_path: str
    conflicting_artifacts: List[str]
    conflict_type: str  # "modification", "deletion", "creation"
    severity: str  # "low", "medium", "high", "critical"
    resolution_suggestion: str = ""


@dataclass
class DependencyAnalysis:
    """Analysis of dependencies between artifacts"""
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    dependency_depth: Dict[str, int] = field(default_factory=dict)
    critical_path: List[str] = field(default_factory=list)


@dataclass
class CommitGroup:
    """A group of related changes for atomic commit"""
    group_id: str
    artifacts: List[WorkArtifact]
    commit_message: str
    dependencies: List[str] = field(default_factory=list)
    estimated_risk: ComplexityLevel = ComplexityLevel.LOW
    quality_checkpoints: List[QualityGate] = field(default_factory=list)
    
    def __post_init__(self):
        """Generate group ID if not provided"""
        if not self.group_id:
            self.group_id = f"commit_group_{uuid.uuid4().hex[:8]}"


@dataclass
class QualityCheckpoint:
    """A quality checkpoint in the integration plan"""
    checkpoint_id: str
    quality_gates: List[QualityGate]
    required_for_continuation: bool = True
    rollback_point: bool = False


@dataclass
class RollbackPoint:
    """A rollback point in case integration fails"""
    rollback_id: str
    git_commit_hash: Optional[str] = None
    backup_paths: List[str] = field(default_factory=list)
    restoration_commands: List[str] = field(default_factory=list)


@dataclass
class ExplosionAssessment:
    """Assessment of the productivity explosion situation"""
    total_artifacts: int
    domains_affected: List[DomainType]
    completion_distribution: Dict[CompletionStatus, int] = field(default_factory=dict)
    readiness_distribution: Dict[ReadinessStatus, int] = field(default_factory=dict)
    conflict_count: int = 0
    integration_complexity: ComplexityLevel = ComplexityLevel.LOW
    recommended_strategy: TriageStrategy = TriageStrategy.SYSTEMATIC_INTEGRATION
    assessment_timestamp: datetime = field(default_factory=datetime.now)
    critical_issues: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)


@dataclass
class IntegrationPlan:
    """Systematic plan for integrating all valuable work"""
    plan_id: str
    commit_groups: List[CommitGroup]
    execution_order: List[int]  # Indices into commit_groups
    quality_checkpoints: List[QualityCheckpoint]
    rollback_points: List[RollbackPoint]
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(hours=1))
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Generate plan ID if not provided"""
        if not self.plan_id:
            self.plan_id = f"integration_plan_{uuid.uuid4().hex[:8]}"


@dataclass
class IntegrationResult:
    """Result of executing an integration step"""
    step_id: str
    success: bool
    commit_hash: Optional[str] = None
    error_message: Optional[str] = None
    artifacts_integrated: List[str] = field(default_factory=list)
    quality_results: Dict[str, Any] = field(default_factory=dict)
    execution_time: timedelta = field(default_factory=lambda: timedelta(0))
    rollback_performed: bool = False


@dataclass
class QualityResults:
    """Results from quality gate validation"""
    gates_passed: List[QualityGate] = field(default_factory=list)
    gates_failed: List[QualityGate] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    code_quality_score: float = 0.0
    spec_compliance_score: float = 0.0
    overall_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class TriageReport:
    """Comprehensive report of the triage operation"""
    report_id: str
    assessment: ExplosionAssessment
    integration_plan: IntegrationPlan
    execution_results: List[IntegrationResult] = field(default_factory=list)
    quality_results: QualityResults = field(default_factory=QualityResults)
    artifacts_integrated: int = 0
    artifacts_deferred: int = 0
    conflicts_resolved: int = 0
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    total_duration: timedelta = field(default_factory=lambda: timedelta(0))
    emergency_protocols_activated: bool = False
    
    def __post_init__(self):
        """Generate report ID if not provided"""
        if not self.report_id:
            self.report_id = f"triage_report_{uuid.uuid4().hex[:8]}"


# Validation functions for data integrity
def validate_work_artifact(artifact: WorkArtifact) -> List[str]:
    """Validate a work artifact and return any issues"""
    issues = []
    
    if not artifact.path:
        issues.append("Path cannot be empty")
    
    if artifact.file_size_bytes < 0:
        issues.append("File size cannot be negative")
    
    if artifact.completion_status == CompletionStatus.COMPLETE and artifact.integration_readiness == ReadinessStatus.NOT_READY:
        issues.append("Complete artifacts should not be marked as not ready")
    
    return issues


def validate_triage_config(config: TriageConfig) -> List[str]:
    """Validate triage configuration and return any issues"""
    issues = []
    
    if not config.scan_paths:
        issues.append("Must specify at least one scan path")
    
    if config.max_artifacts_to_process <= 0:
        issues.append("Max artifacts to process must be positive")
    
    if config.emergency_thresholds.max_conflicts < 0:
        issues.append("Max conflicts threshold cannot be negative")
    
    return issues