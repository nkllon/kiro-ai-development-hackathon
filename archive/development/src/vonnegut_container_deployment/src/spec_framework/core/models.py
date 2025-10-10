"""
Core data models for the Spec Mode Framework.

These models define the fundamental data structures for systematic
specification-driven development, based on proven RM-DDD patterns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
import uuid


# Type aliases for clarity
SpecificationId = str
RequirementId = str
CriterionId = str
DesignComponentId = str
TaskId = str
SecurityRequirementId = str
PerformanceRequirementId = str
ThreatModelId = str
ComplianceRequirement = str


class SpecificationStatus(Enum):
    """Status of a specification in the systematic workflow."""
    DRAFT = "draft"
    REQUIREMENTS_COMPLETE = "requirements_complete"
    DESIGN_COMPLETE = "design_complete"
    TASKS_COMPLETE = "tasks_complete"
    IMPLEMENTATION_IN_PROGRESS = "implementation_in_progress"
    IMPLEMENTATION_COMPLETE = "implementation_complete"
    VALIDATED = "validated"


class RequirementStatus(Enum):
    """Status of individual requirements."""
    DRAFT = "draft"
    DEFINED = "defined"
    DESIGNED = "designed"
    IMPLEMENTED = "implemented"
    TESTED = "tested"
    VALIDATED = "validated"


class Priority(Enum):
    """Priority levels for requirements."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DependencyType(Enum):
    """Types of dependencies between specifications."""
    REQUIRES = "requires"
    BLOCKS = "blocks"
    INFLUENCES = "influences"
    CONFLICTS = "conflicts"


class DependencyResolutionStatus(Enum):
    """Status of dependency resolution."""
    UNRESOLVED = "unresolved"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CONFLICT = "conflict"


class ImpactSeverity(Enum):
    """Severity levels for cross-spec impact analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceValidationStatus(Enum):
    """Status of compliance validation."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class AuditReadinessStatus(Enum):
    """Audit readiness status."""
    NOT_READY = "not_ready"
    PARTIALLY_READY = "partially_ready"
    READY = "ready"
    AUDIT_COMPLETE = "audit_complete"


class PerformanceMetricType(Enum):
    """Types of performance metrics."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    RESOURCE_USAGE = "resource_usage"
    SCALABILITY = "scalability"


@dataclass
class EARSStatement:
    """
    EARS (Easy Approach to Requirements Syntax) formatted statement.
    
    Format: WHEN/IF [condition] THEN [system] SHALL [response]
    """
    condition: str
    system: str
    response: str
    statement_type: str = "WHEN"  # WHEN or IF
    
    def __str__(self) -> str:
        return f"{self.statement_type} {self.condition} THEN {self.system} SHALL {self.response}"


@dataclass
class UserStory:
    """
    User story in standard format.
    
    Format: As a [role], I want [feature], so that [benefit]
    """
    role: str
    feature: str
    benefit: str
    
    def __str__(self) -> str:
        return f"As a {self.role}, I want {self.feature}, so that {self.benefit}"


@dataclass
class ValidationMethod:
    """Method for validating acceptance criteria."""
    method_type: str  # "automated_test", "manual_test", "review", "measurement"
    description: str
    tools: List[str] = field(default_factory=list)
    success_criteria: str = ""


@dataclass
class SecurityValidation:
    """Security validation requirements."""
    security_tests: List[str] = field(default_factory=list)
    threat_analysis: Optional[str] = None
    compliance_check: Optional[str] = None


@dataclass
class PerformanceValidation:
    """Performance validation requirements."""
    performance_tests: List[str] = field(default_factory=list)
    scalability_analysis: Optional[str] = None
    optimization_recommendations: List[str] = field(default_factory=list)


@dataclass
class AcceptanceCriterion:
    """Individual acceptance criterion for a requirement."""
    id: CriterionId = field(default_factory=lambda: str(uuid.uuid4()))
    ears_format: EARSStatement = field(default_factory=lambda: EARSStatement("", "", ""))
    testable: bool = True
    validation_method: ValidationMethod = field(default_factory=lambda: ValidationMethod("", ""))
    security_validation: Optional[SecurityValidation] = None
    performance_validation: Optional[PerformanceValidation] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityImplication:
    """Security implications of a requirement."""
    threat_category: str
    risk_level: str
    mitigation_strategy: str
    compliance_requirements: List[str] = field(default_factory=list)


@dataclass
class PerformanceImplication:
    """Performance implications of a requirement."""
    metric_type: PerformanceMetricType
    expected_impact: str
    measurement_method: str
    target_values: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceTag:
    """Compliance tagging for requirements."""
    framework: str  # e.g., "SOX", "GDPR", "HIPAA"
    requirement_id: str
    compliance_level: str
    validation_required: bool = True


@dataclass
class Requirement:
    """Individual requirement with systematic structure."""
    id: RequirementId = field(default_factory=lambda: str(uuid.uuid4()))
    user_story: UserStory = field(default_factory=lambda: UserStory("", "", ""))
    acceptance_criteria: List[AcceptanceCriterion] = field(default_factory=list)
    business_value: str = ""
    priority: Priority = Priority.MEDIUM
    status: RequirementStatus = RequirementStatus.DRAFT
    security_implications: List[SecurityImplication] = field(default_factory=list)
    performance_implications: List[PerformanceImplication] = field(default_factory=list)
    compliance_tags: List[ComplianceTag] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_acceptance_criterion(self, criterion: AcceptanceCriterion) -> None:
        """Add an acceptance criterion to this requirement."""
        self.acceptance_criteria.append(criterion)
        self.updated_at = datetime.now()
    
    def is_complete(self) -> bool:
        """Check if requirement has all necessary components."""
        return (
            bool(self.user_story.role and self.user_story.feature and self.user_story.benefit) and
            len(self.acceptance_criteria) > 0 and
            all(ac.testable for ac in self.acceptance_criteria)
        )


@dataclass
class Design:
    """Design document structure."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    overview: str = ""
    architecture: str = ""
    components: Dict[str, Any] = field(default_factory=dict)
    interfaces: Dict[str, Any] = field(default_factory=dict)
    data_models: Dict[str, Any] = field(default_factory=dict)
    error_handling: str = ""
    testing_strategy: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Task:
    """Implementation task structure."""
    id: TaskId = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    requirements_references: List[RequirementId] = field(default_factory=list)
    design_references: List[DesignComponentId] = field(default_factory=list)
    dependencies: List[TaskId] = field(default_factory=list)
    status: str = "not_started"  # not_started, in_progress, completed
    estimated_effort: Optional[int] = None  # hours
    actual_effort: Optional[int] = None  # hours
    assignee: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DependencyRelationship:
    """Relationship between specifications."""
    source_spec: SpecificationId
    target_spec: SpecificationId
    dependency_type: DependencyType
    description: str
    requirements_mapping: Dict[RequirementId, RequirementId] = field(default_factory=dict)


@dataclass
class TraceabilityMatrix:
    """Complete traceability matrix for systematic validation."""
    requirement_to_design: Dict[RequirementId, List[DesignComponentId]] = field(default_factory=dict)
    design_to_tasks: Dict[DesignComponentId, List[TaskId]] = field(default_factory=dict)
    task_to_implementation: Dict[TaskId, List[str]] = field(default_factory=dict)  # implementation artifacts
    implementation_to_tests: Dict[str, List[str]] = field(default_factory=dict)  # test cases
    cross_spec_dependencies: Dict[SpecificationId, List[DependencyRelationship]] = field(default_factory=dict)
    compliance_traceability: Dict[ComplianceRequirement, List[RequirementId]] = field(default_factory=dict)
    
    def add_requirement_design_link(self, req_id: RequirementId, design_id: DesignComponentId) -> None:
        """Add traceability link from requirement to design component."""
        if req_id not in self.requirement_to_design:
            self.requirement_to_design[req_id] = []
        if design_id not in self.requirement_to_design[req_id]:
            self.requirement_to_design[req_id].append(design_id)
    
    def get_requirement_coverage(self) -> float:
        """Calculate percentage of requirements with design coverage."""
        if not self.requirement_to_design:
            return 0.0
        covered = sum(1 for designs in self.requirement_to_design.values() if designs)
        total = len(self.requirement_to_design)
        return (covered / total) * 100.0 if total > 0 else 0.0


@dataclass
class ValidationResults:
    """Results of systematic validation."""
    structural_validation: Dict[str, bool] = field(default_factory=dict)
    content_validation: Dict[str, bool] = field(default_factory=dict)
    traceability_validation: Dict[str, bool] = field(default_factory=dict)
    security_validation: Dict[str, bool] = field(default_factory=dict)
    performance_validation: Dict[str, bool] = field(default_factory=dict)
    compliance_validation: Dict[str, bool] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    overall_score: float = 0.0
    validated_at: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        """Check if all validations passed."""
        all_validations = [
            self.structural_validation,
            self.content_validation,
            self.traceability_validation,
            self.security_validation,
            self.performance_validation,
            self.compliance_validation
        ]
        return all(
            all(results.values()) if results else True
            for results in all_validations
        ) and len(self.validation_errors) == 0


@dataclass
class SpecificationDependency:
    """Dependency between specifications."""
    dependent_spec: SpecificationId
    dependency_spec: SpecificationId
    dependency_type: DependencyType
    requirements_mapping: Dict[RequirementId, RequirementId] = field(default_factory=dict)
    resolution_status: DependencyResolutionStatus = DependencyResolutionStatus.UNRESOLVED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendedAction:
    """Recommended action for impact resolution."""
    action_type: str
    description: str
    priority: Priority
    estimated_effort: Optional[int] = None


@dataclass
class SpecificationChange:
    """Record of a specification change."""
    change_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    specification_id: SpecificationId = ""
    change_type: str = ""  # "requirement_added", "requirement_modified", etc.
    description: str = ""
    changed_by: str = ""
    changed_at: datetime = field(default_factory=datetime.now)
    impact_analysis: Optional['CrossSpecImpactAnalysis'] = None


@dataclass
class CrossSpecImpactAnalysis:
    """Analysis of cross-specification impacts."""
    source_change: SpecificationChange
    impacted_specs: List[SpecificationId] = field(default_factory=list)
    impact_severity: ImpactSeverity = ImpactSeverity.LOW
    recommended_actions: List[RecommendedAction] = field(default_factory=list)
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class DesignDecision:
    """Record of a design decision."""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    rationale: str = ""
    alternatives_considered: List[str] = field(default_factory=list)
    decision_maker: str = ""
    decided_at: datetime = field(default_factory=datetime.now)
    requirements_references: List[RequirementId] = field(default_factory=list)


@dataclass
class ApprovalRecord:
    """Record of specification approval."""
    approval_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    specification_id: SpecificationId = ""
    phase: str = ""  # "requirements", "design", "tasks"
    approver: str = ""
    approved_at: datetime = field(default_factory=datetime.now)
    comments: str = ""


@dataclass
class ComplianceValidation:
    """Record of compliance validation."""
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework: str = ""
    requirements_checked: List[RequirementId] = field(default_factory=list)
    validation_status: ComplianceValidationStatus = ComplianceValidationStatus.NOT_STARTED
    findings: List[str] = field(default_factory=list)
    validated_by: str = ""
    validated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditTrail:
    """Complete audit trail for specification."""
    changes: List[SpecificationChange] = field(default_factory=list)
    decisions: List[DesignDecision] = field(default_factory=list)
    approvals: List[ApprovalRecord] = field(default_factory=list)
    compliance_validations: List[ComplianceValidation] = field(default_factory=list)
    
    def add_change(self, change: SpecificationChange) -> None:
        """Add a change record to the audit trail."""
        self.changes.append(change)
    
    def get_changes_by_type(self, change_type: str) -> List[SpecificationChange]:
        """Get all changes of a specific type."""
        return [change for change in self.changes if change.change_type == change_type]


@dataclass
class RegulatoryFramework:
    """Regulatory framework definition."""
    name: str
    version: str
    requirements: List[str] = field(default_factory=list)
    validation_procedures: List[str] = field(default_factory=list)


@dataclass
class ComplianceMetadata:
    """Compliance metadata for specification."""
    regulatory_frameworks: List[RegulatoryFramework] = field(default_factory=list)
    compliance_requirements: List[ComplianceRequirement] = field(default_factory=list)
    validation_status: ComplianceValidationStatus = ComplianceValidationStatus.NOT_STARTED
    audit_readiness: AuditReadinessStatus = AuditReadinessStatus.NOT_READY
    last_audit_date: Optional[datetime] = None
    next_audit_date: Optional[datetime] = None


@dataclass
class SecurityControl:
    """Security control definition."""
    control_id: str
    name: str
    description: str
    implementation_guidance: str
    validation_method: str


@dataclass
class SecurityComplianceMapping:
    """Mapping between security requirements and compliance frameworks."""
    framework: str
    control_id: str
    compliance_level: str


@dataclass
class SecurityTest:
    """Security test definition."""
    test_id: str
    name: str
    description: str
    test_type: str  # "static", "dynamic", "manual"
    expected_outcome: str


@dataclass
class ThreatAnalysis:
    """Threat analysis results."""
    threats_identified: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, str] = field(default_factory=dict)
    mitigation_strategies: List[str] = field(default_factory=list)


@dataclass
class SecurityComplianceCheck:
    """Security compliance check results."""
    framework: str
    compliance_status: str
    controls_checked: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)


@dataclass
class SecurityRequirement:
    """Security requirement definition."""
    id: SecurityRequirementId = field(default_factory=lambda: str(uuid.uuid4()))
    threat_model_reference: Optional[ThreatModelId] = None
    security_control: SecurityControl = field(default_factory=lambda: SecurityControl("", "", "", "", ""))
    validation_method: str = ""
    compliance_mapping: List[SecurityComplianceMapping] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceTarget:
    """Performance target definition."""
    metric: str
    target_value: Union[int, float]
    unit: str
    tolerance: Optional[Union[int, float]] = None


@dataclass
class ScalabilityImplications:
    """Scalability implications analysis."""
    scaling_factors: List[str] = field(default_factory=list)
    bottlenecks: List[str] = field(default_factory=list)
    scaling_strategies: List[str] = field(default_factory=list)


@dataclass
class PerformanceTest:
    """Performance test definition."""
    test_id: str
    name: str
    description: str
    test_type: str  # "load", "stress", "volume", "spike"
    success_criteria: str


@dataclass
class ScalabilityAnalysis:
    """Scalability analysis results."""
    current_capacity: Dict[str, Any] = field(default_factory=dict)
    projected_capacity: Dict[str, Any] = field(default_factory=dict)
    scaling_recommendations: List[str] = field(default_factory=list)


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation."""
    area: str
    recommendation: str
    expected_improvement: str
    implementation_effort: str


@dataclass
class PerformanceRequirement:
    """Performance requirement definition."""
    id: PerformanceRequirementId = field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: PerformanceMetricType = PerformanceMetricType.LATENCY
    target_value: PerformanceTarget = field(default_factory=lambda: PerformanceTarget("", 0, ""))
    measurement_method: str = ""
    scalability_implications: ScalabilityImplications = field(default_factory=ScalabilityImplications)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Specification:
    """
    Complete specification with systematic structure.
    
    This is the root entity that contains all aspects of a feature specification
    following the systematic approach proven by RM-DDD.
    """
    id: SpecificationId = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    requirements: List[Requirement] = field(default_factory=list)
    design: Optional[Design] = None
    tasks: List[Task] = field(default_factory=list)
    status: SpecificationStatus = SpecificationStatus.DRAFT
    traceability_matrix: TraceabilityMatrix = field(default_factory=TraceabilityMatrix)
    validation_results: ValidationResults = field(default_factory=ValidationResults)
    dependencies: List[SpecificationDependency] = field(default_factory=list)
    security_requirements: List[SecurityRequirement] = field(default_factory=list)
    performance_requirements: List[PerformanceRequirement] = field(default_factory=list)
    compliance_metadata: ComplianceMetadata = field(default_factory=ComplianceMetadata)
    audit_trail: AuditTrail = field(default_factory=AuditTrail)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    
    def add_requirement(self, requirement: Requirement) -> None:
        """Add a requirement to this specification."""
        self.requirements.append(requirement)
        self.updated_at = datetime.now()
        
        # Add to audit trail
        change = SpecificationChange(
            specification_id=self.id,
            change_type="requirement_added",
            description=f"Added requirement: {requirement.user_story}",
            changed_at=datetime.now()
        )
        self.audit_trail.add_change(change)
    
    def get_requirements_by_status(self, status: RequirementStatus) -> List[Requirement]:
        """Get all requirements with a specific status."""
        return [req for req in self.requirements if req.status == status]
    
    def get_completion_percentage(self) -> float:
        """Calculate overall completion percentage."""
        if not self.requirements:
            return 0.0
        
        completed_requirements = len(self.get_requirements_by_status(RequirementStatus.VALIDATED))
        return (completed_requirements / len(self.requirements)) * 100.0
    
    def is_ready_for_design(self) -> bool:
        """Check if specification is ready to move to design phase."""
        return (
            self.status == SpecificationStatus.DRAFT and
            len(self.requirements) > 0 and
            all(req.is_complete() for req in self.requirements) and
            self.validation_results.is_valid()
        )
    
    def is_ready_for_tasks(self) -> bool:
        """Check if specification is ready to move to tasks phase."""
        return (
            self.status == SpecificationStatus.DESIGN_COMPLETE and
            self.design is not None and
            self.validation_results.is_valid()
        )
    
    def is_ready_for_implementation(self) -> bool:
        """Check if specification is ready for implementation."""
        return (
            self.status == SpecificationStatus.TASKS_COMPLETE and
            len(self.tasks) > 0 and
            self.validation_results.is_valid()
        )