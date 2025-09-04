"""
Data models for compliance checking system.

Defines all data structures used throughout the compliance checking system
to ensure consistent data representation and type safety.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime


class ComplianceIssueType(Enum):
    """Types of compliance issues that can be detected."""
    RDI_VIOLATION = "rdi_violation"
    RM_NON_COMPLIANCE = "rm_non_compliance"
    TEST_FAILURE = "test_failure"
    DESIGN_MISALIGNMENT = "design_misalignment"
    REQUIREMENT_TRACEABILITY = "requirement_traceability"
    ARCHITECTURAL_VIOLATION = "architectural_violation"


class IssueSeverity(Enum):
    """Severity levels for compliance issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ComplianceIssue:
    """Individual compliance issue with severity and remediation."""
    issue_type: ComplianceIssueType
    severity: IssueSeverity
    description: str
    affected_files: List[str] = field(default_factory=list)
    remediation_steps: List[str] = field(default_factory=list)
    estimated_effort: str = "unknown"
    blocking_merge: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommitInfo:
    """Information about a git commit."""
    commit_hash: str
    author: str
    timestamp: datetime
    message: str
    modified_files: List[str] = field(default_factory=list)
    added_files: List[str] = field(default_factory=list)
    deleted_files: List[str] = field(default_factory=list)


@dataclass
class FileChangeAnalysis:
    """Analysis of file changes in commits."""
    total_files_changed: int
    files_added: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    lines_added: int = 0
    lines_deleted: int = 0


@dataclass
class RDIComplianceStatus:
    """Status of RDI methodology compliance."""
    requirements_traced: bool = False
    design_aligned: bool = False
    implementation_complete: bool = False
    test_coverage_adequate: bool = False
    compliance_score: float = 0.0
    issues: List[ComplianceIssue] = field(default_factory=list)


@dataclass
class RMComplianceStatus:
    """Status of RM architectural compliance."""
    interface_implemented: bool = False
    size_constraints_met: bool = False
    health_monitoring_present: bool = False
    registry_integrated: bool = False
    compliance_score: float = 0.0
    issues: List[ComplianceIssue] = field(default_factory=list)


@dataclass
class TestCoverageStatus:
    """Status of test coverage compliance."""
    current_coverage: float = 0.0
    baseline_coverage: float = 96.7
    coverage_adequate: bool = False
    failing_tests: List[str] = field(default_factory=list)
    missing_tests: List[str] = field(default_factory=list)
    issues: List[ComplianceIssue] = field(default_factory=list)


@dataclass
class TaskReconciliationStatus:
    """Status of task completion reconciliation."""
    claimed_complete_tasks: List[str] = field(default_factory=list)
    actually_implemented_tasks: List[str] = field(default_factory=list)
    missing_implementations: List[str] = field(default_factory=list)
    reconciliation_score: float = 0.0
    issues: List[ComplianceIssue] = field(default_factory=list)


@dataclass
class ComplianceAnalysisResult:
    """Results of comprehensive compliance analysis."""
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    commits_analyzed: List[CommitInfo] = field(default_factory=list)
    rdi_compliance: RDIComplianceStatus = field(default_factory=RDIComplianceStatus)
    rm_compliance: RMComplianceStatus = field(default_factory=RMComplianceStatus)
    test_coverage_status: TestCoverageStatus = field(default_factory=TestCoverageStatus)
    task_completion_reconciliation: TaskReconciliationStatus = field(default_factory=TaskReconciliationStatus)
    overall_compliance_score: float = 0.0
    critical_issues: List[ComplianceIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    phase3_ready: bool = False


@dataclass
class Phase2ValidationResult:
    """Results of Phase 2 completion validation."""
    validation_timestamp: datetime = field(default_factory=datetime.now)
    claimed_complete_tasks: List[str] = field(default_factory=list)
    actually_implemented_tasks: List[str] = field(default_factory=list)
    missing_implementations: List[str] = field(default_factory=list)
    test_failures_count: int = 0
    phase3_readiness_score: float = 0.0
    blocking_issues: List[ComplianceIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class RemediationStep:
    """Individual remediation step for compliance issues."""
    step_id: str
    description: str
    priority: IssueSeverity
    estimated_effort: str
    affected_components: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    validation_criteria: List[str] = field(default_factory=list)