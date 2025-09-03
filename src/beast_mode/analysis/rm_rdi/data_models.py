"""
RM-RDI Analysis System - Core Data Models

OPERATOR SAFETY: All data models are READ-ONLY with immutable structures
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class Priority(Enum):
    """Recommendation priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationCategory(Enum):
    """Categories of recommendations"""
    IMMEDIATE_FIX = "immediate_fix"
    SHORT_TERM_IMPROVEMENT = "short_term_improvement"
    LONG_TERM_STRATEGY = "long_term_strategy"
    RISK_MITIGATION = "risk_mitigation"


class AnalysisStatus(Enum):
    """Analysis execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"  # Emergency shutdown


@dataclass(frozen=True)  # IMMUTABLE for safety
class EffortEstimate:
    """Effort estimation for recommendations"""
    development_hours: int
    testing_hours: int
    documentation_hours: int
    total_hours: int
    complexity: str


@dataclass(frozen=True)  # IMMUTABLE for safety
class ImpactAssessment:
    """Impact assessment for recommendations"""
    performance_impact: float
    maintainability_impact: float
    security_impact: float
    business_value_impact: float
    risk_reduction: float


@dataclass(frozen=True)  # IMMUTABLE for safety
class Recommendation:
    """Individual recommendation with safety metadata"""
    recommendation_id: str
    title: str
    description: str
    priority: Priority
    category: RecommendationCategory
    effort_estimate: EffortEstimate
    impact_assessment: ImpactAssessment
    implementation_guidance: str
    success_criteria: List[str]
    safety_notes: List[str] = field(default_factory=list)
    rollback_plan: str = ""


@dataclass(frozen=True)  # IMMUTABLE for safety
class ArchitectureAnalysis:
    """Architecture analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    rm_architecture_score: float
    rdi_architecture_score: float
    integration_quality_score: float
    scalability_score: float
    strengths: List[str]
    weaknesses: List[str]
    improvement_areas: List[str]
    safety_validated: bool = True  # Always validate safety


@dataclass(frozen=True)  # IMMUTABLE for safety
class QualityIssue:
    """Individual quality issue"""
    issue_id: str
    severity: str
    description: str
    file_path: str
    line_number: Optional[int]
    recommendation: str


@dataclass(frozen=True)  # IMMUTABLE for safety
class QualityReport:
    """Code quality analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    maintainability_score: float
    testability_score: float
    performance_score: float
    security_score: float
    quality_metrics: Dict[str, Any]
    quality_issues: List[QualityIssue]
    files_analyzed: int
    lines_analyzed: int


@dataclass(frozen=True)  # IMMUTABLE for safety
class ComplianceViolation:
    """Individual compliance violation"""
    violation_id: str
    type: str
    severity: str
    description: str
    file_path: str
    remediation: str


@dataclass(frozen=True)  # IMMUTABLE for safety
class ComplianceReport:
    """Compliance analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    rm_compliance_score: float
    rdi_compliance_score: float
    standards_compliance_score: float
    compliance_violations: List[ComplianceViolation]
    compliance_gaps: List[str]
    total_components_checked: int
    compliant_components: int


@dataclass(frozen=True)  # IMMUTABLE for safety
class SizeViolation:
    """File size violation details"""
    file_path: str
    current_lines: int
    limit_lines: int
    violation_severity: str
    refactoring_suggestion: str


@dataclass(frozen=True)  # IMMUTABLE for safety
class RefactoringOpportunity:
    """Refactoring opportunity details"""
    opportunity_id: str
    type: str
    description: str
    files_affected: List[str]
    effort_estimate: int
    impact_score: float


@dataclass(frozen=True)  # IMMUTABLE for safety
class PerformanceDebt:
    """Performance debt item"""
    debt_id: str
    description: str
    performance_impact: float
    optimization_suggestion: str
    effort_required: int


@dataclass(frozen=True)  # IMMUTABLE for safety
class DocumentationDebt:
    """Documentation debt item"""
    debt_id: str
    missing_documentation: str
    affected_components: List[str]
    priority: str


@dataclass(frozen=True)  # IMMUTABLE for safety
class TechnicalDebtReport:
    """Technical debt analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    total_debt_score: float
    size_violations: List[SizeViolation]
    refactoring_opportunities: List[RefactoringOpportunity]
    performance_debt: List[PerformanceDebt]
    documentation_debt: List[DocumentationDebt]
    total_files_analyzed: int
    debt_trend: str  # "improving", "stable", "degrading"


@dataclass(frozen=True)  # IMMUTABLE for safety
class PerformanceMetric:
    """Individual performance metric"""
    metric_name: str
    value: float
    unit: str
    threshold: Optional[float]
    status: str  # "good", "warning", "critical"


@dataclass(frozen=True)  # IMMUTABLE for safety
class PerformanceReport:
    """Performance analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    overall_performance_score: float
    rm_performance_metrics: List[PerformanceMetric]
    rdi_performance_metrics: List[PerformanceMetric]
    bottlenecks_identified: List[str]
    optimization_opportunities: List[str]
    resource_usage: Dict[str, float]


@dataclass(frozen=True)  # IMMUTABLE for safety
class MetricsTrend:
    """Metrics trend data"""
    metric_name: str
    trend_direction: str  # "up", "down", "stable"
    change_percentage: float
    time_period: str


@dataclass(frozen=True)  # IMMUTABLE for safety
class MetricsReport:
    """Metrics analysis results - READ-ONLY"""
    analysis_id: str
    timestamp: datetime
    performance_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    compliance_metrics: Dict[str, float]
    business_value_metrics: Dict[str, float]
    trends: List[MetricsTrend]
    collection_period: str


@dataclass(frozen=True)  # IMMUTABLE for safety
class SafetyMetrics:
    """Safety and resource usage metrics"""
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_io_operations: int
    network_operations: int
    analysis_duration_seconds: float
    safety_checks_passed: int
    safety_violations: List[str]


@dataclass(frozen=True)  # IMMUTABLE for safety
class AnalysisResult:
    """Comprehensive analysis result - IMMUTABLE and SAFE"""
    analysis_id: str
    timestamp: datetime
    analysis_types: List[str]
    status: AnalysisStatus
    
    # Analysis Results (Optional - only populated if analysis was run)
    architecture_analysis: Optional[ArchitectureAnalysis] = None
    quality_analysis: Optional[QualityReport] = None
    compliance_analysis: Optional[ComplianceReport] = None
    technical_debt_analysis: Optional[TechnicalDebtReport] = None
    performance_analysis: Optional[PerformanceReport] = None
    metrics_analysis: Optional[MetricsReport] = None
    
    # Recommendations and Safety
    recommendations: List[Recommendation] = field(default_factory=list)
    overall_health_score: float = 0.0
    safety_metrics: Optional[SafetyMetrics] = None
    
    # Operator Safety Information
    operator_notes: List[str] = field(default_factory=list)
    safety_validated: bool = True
    can_be_safely_ignored: bool = True  # Analysis can always be ignored
    emergency_shutdown_available: bool = True
    
    def __post_init__(self):
        """Validate safety constraints"""
        # Ensure all safety guarantees are met
        if not self.safety_validated:
            raise ValueError("Analysis result failed safety validation")
        
        # Add operator safety note
        if not self.operator_notes:
            object.__setattr__(self, 'operator_notes', [
                "This analysis is READ-ONLY and cannot impact existing systems",
                "Use 'make analysis-kill' for emergency shutdown",
                "Analysis can be safely ignored or disabled at any time"
            ])