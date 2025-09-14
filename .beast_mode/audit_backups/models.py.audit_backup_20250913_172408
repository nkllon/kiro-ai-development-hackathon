"""
Core data models for the Domain Index System

This module defines all the data structures used throughout the domain index system,
including domain representations, health status, metrics, and operation results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum


class HealthStatusType(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class IssueCategory(Enum):
    """Issue categories"""
    DEPENDENCY = "dependency"
    PATTERN = "pattern"
    FILE = "file"
    MAKEFILE = "makefile"
    VALIDATION = "validation"
    SYNC = "sync"


@dataclass
class PackagePotential:
    """PyPI packaging potential assessment"""
    score: float  # 0.0 to 1.0
    reasons: List[str]
    dependencies: List[str]
    estimated_effort: str  # "low", "medium", "high"
    blockers: List[str]


@dataclass
class DomainTools:
    """Domain-specific tooling configuration"""
    linter: str
    formatter: str
    validator: str
    exclusions: List[str] = field(default_factory=list)
    custom_tools: Dict[str, str] = field(default_factory=dict)


@dataclass
class DomainMetadata:
    """Extended domain metadata"""
    demo_role: str
    extraction_candidate: str
    package_potential: PackagePotential
    completion_date: Optional[str] = None
    status: str = "active"
    tags: List[str] = field(default_factory=list)
    maintainers: List[str] = field(default_factory=list)
    last_updated: Optional[datetime] = None


@dataclass
class HealthIssue:
    """Individual health issue"""
    severity: IssueSeverity
    category: IssueCategory
    description: str
    suggested_fix: str
    affected_files: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HealthMetrics:
    """Health-related metrics"""
    dependency_health_score: float  # 0.0 to 1.0
    pattern_coverage_score: float   # 0.0 to 1.0
    file_accessibility_score: float # 0.0 to 1.0
    makefile_integration_score: float # 0.0 to 1.0
    overall_health_score: float     # 0.0 to 1.0
    last_calculated: datetime = field(default_factory=datetime.now)


@dataclass
class HealthStatus:
    """Complete health status for a domain"""
    status: HealthStatusType
    last_check: datetime
    issues: List[HealthIssue]
    metrics: HealthMetrics
    check_duration_ms: int = 0
    next_check: Optional[datetime] = None


@dataclass
class Domain:
    """Core domain model"""
    name: str
    description: str
    patterns: List[str]
    content_indicators: List[str]
    requirements: List[str]
    dependencies: List[str]
    tools: DomainTools
    metadata: DomainMetadata
    health_status: Optional[HealthStatus] = None
    
    # Computed properties
    file_count: int = 0
    line_count: int = 0
    last_modified: Optional[datetime] = None


@dataclass
class DependencyGraph:
    """Domain dependency relationships"""
    domain: str
    direct_dependencies: List[str]
    transitive_dependencies: List[str]
    dependents: List[str]
    circular_dependencies: List[List[str]]
    dependency_depth: int
    coupling_score: float  # 0.0 to 1.0


@dataclass
class QueryResult:
    """Result of a domain query"""
    domains: List[Domain]
    total_count: int
    query_time_ms: float
    suggestions: List[str] = field(default_factory=list)
    filters_applied: Dict[str, Any] = field(default_factory=dict)
    relevance_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class DomainMetrics:
    """Comprehensive domain metrics"""
    file_count: int
    line_count: int
    complexity_score: float      # 0.0 to 1.0
    dependency_depth: int
    coupling_score: float        # 0.0 to 1.0
    extraction_score: float      # 0.0 to 1.0
    maintainability_score: float # 0.0 to 1.0
    test_coverage: float         # 0.0 to 1.0
    documentation_score: float   # 0.0 to 1.0
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExtractionCandidate:
    """Domain suitable for extraction/packaging"""
    domain: Domain
    score: float  # 0.0 to 1.0
    reasons: List[str]
    dependencies: List[str]
    estimated_effort: str
    potential_benefits: List[str]
    blockers: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of domain validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    validation_time_ms: float = 0.0


@dataclass
class DomainSuggestion:
    """Suggestion for domain assignment"""
    domain_name: str
    confidence: float  # 0.0 to 1.0
    reasons: List[str]
    pattern_matches: List[str]
    content_matches: List[str]


@dataclass
class PatternChange:
    """Detected change in domain patterns"""
    domain_name: str
    change_type: str  # "added", "removed", "modified"
    old_pattern: Optional[str]
    new_pattern: Optional[str]
    affected_files: List[str]
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class DomainChange:
    """Proposed change to domain registry"""
    domain_name: str
    change_type: str  # "create", "update", "delete"
    changes: Dict[str, Any]
    reason: str
    confidence: float  # 0.0 to 1.0
    requires_approval: bool = True


@dataclass
class UpdateResult:
    """Result of domain registry update"""
    success: bool
    changes_applied: List[DomainChange]
    errors: List[str] = field(default_factory=list)
    backup_created: Optional[str] = None
    rollback_available: bool = False


@dataclass
class SyncResult:
    """Result of synchronization operation"""
    success: bool
    domains_updated: List[str]
    new_files_found: List[str]
    orphaned_files: List[str]
    pattern_changes: List[PatternChange]
    suggestions: List[DomainSuggestion]
    sync_time_ms: float = 0.0


@dataclass
class ComplexityReport:
    """Domain complexity analysis report"""
    total_domains: int
    complexity_distribution: Dict[str, int]  # "low", "medium", "high"
    most_complex_domains: List[str]
    coupling_hotspots: List[str]
    refactoring_opportunities: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvolutionReport:
    """Domain evolution tracking report"""
    timeframe: str
    domains_added: List[str]
    domains_removed: List[str]
    domains_modified: List[str]
    complexity_trends: Dict[str, float]
    health_trends: Dict[str, float]
    extraction_candidates_identified: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class MakeTarget:
    """Makefile target information"""
    name: str
    description: str
    dependencies: List[str]
    commands: List[str]
    domain_specific: bool = False
    estimated_duration: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result of makefile target execution"""
    success: bool
    target: str
    output: str
    error_output: str = ""
    execution_time_ms: int = 0
    exit_code: int = 0
    executed_at: datetime = field(default_factory=datetime.now)


# Type aliases for common collections
DomainCollection = Dict[str, Domain]
HealthStatusCollection = Dict[str, HealthStatus]
MetricsCollection = Dict[str, DomainMetrics]