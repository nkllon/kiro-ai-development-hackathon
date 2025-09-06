"""
Core data models for the Systematic Hubris Prevention framework.

These models define the data structures used throughout the hubris prevention
system for accountability tracking, governance, and intervention management.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import uuid


class TrendDirection(Enum):
    """Direction of hubris trend analysis."""
    IMPROVING = "improving"
    STABLE = "stable" 
    WORSENING = "worsening"
    CRITICAL = "critical"


class RiskLevel(Enum):
    """Risk level assessment for hubris patterns."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionType(Enum):
    """Types of governance interventions."""
    WARNING = "warning"
    ACCOUNTABILITY_VERIFICATION = "accountability_verification"
    REALITY_CHECK = "reality_check"
    QUARANTINE = "quarantine"
    EMERGENCY_GOVERNANCE = "emergency_governance"


class RealityCheckOutcome(Enum):
    """Outcomes of reality check validation."""
    PASSED = "passed"
    FAILED = "failed"
    REQUIRES_ESCALATION = "requires_escalation"
    EMERGENCY_INTERVENTION = "emergency_intervention"


@dataclass
class Actor:
    """Represents a system actor subject to accountability."""
    actor_id: str
    name: str
    role: str
    permissions: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    last_active: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """Represents a decision made by an actor."""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = ""
    decision_type: str = ""
    impact_level: str = ""
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    accountability_verified: bool = False
    emergency_claimed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccountabilityRelationship:
    """Represents a single accountability relationship."""
    relationship_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    accountable_to: str = ""  # Actor ID they're accountable to
    relationship_type: str = ""  # organizational, financial, regulatory, etc.
    strength: float = 1.0  # 0.0 to 1.0, strength of accountability
    verified: bool = False
    last_verified: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstraintSource:
    """Represents a source of constraints on an actor."""
    source_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_type: str = ""  # legal, financial, organizational, social
    description: str = ""
    enforcement_mechanism: str = ""
    strength: float = 1.0
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccountabilityChain:
    """Complete accountability chain for an actor."""
    actor_id: str
    immediate_accountability: List[AccountabilityRelationship] = field(default_factory=list)
    ultimate_accountability: List[AccountabilityRelationship] = field(default_factory=list)
    constraint_sources: List[ConstraintSource] = field(default_factory=list)
    last_verified: Optional[datetime] = None
    verification_confidence: float = 0.0  # 0.0 to 1.0
    discovery_method: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HubrisFactor:
    """Individual factor contributing to hubris score."""
    factor_type: str
    description: str
    weight: float  # Contribution weight to overall score
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendedAction:
    """Recommended action for hubris mitigation."""
    action_type: str
    description: str
    priority: str  # low, medium, high, critical
    timeline: timedelta
    responsible_party: str
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class HubrisScore:
    """Hubris assessment score for an actor."""
    actor_id: str
    score: float  # 0.0 (humble) to 1.0 (dangerous hubris)
    contributing_factors: List[HubrisFactor] = field(default_factory=list)
    trend_direction: TrendDirection = TrendDirection.STABLE
    risk_level: RiskLevel = RiskLevel.LOW
    recommended_actions: List[RecommendedAction] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None


@dataclass
class VelocityAlert:
    """Alert for excessive decision velocity without accountability."""
    actor_id: str
    decision_count: int
    timeframe: timedelta
    accountability_verification_rate: float
    threshold_exceeded: bool
    alert_level: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BypassAlert:
    """Alert for governance process bypass attempts."""
    actor_id: str
    bypass_type: str
    governance_process: str
    attempt_count: int
    success_rate: float
    alert_level: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EscalationAction:
    """Action taken for escalating persistent hubris patterns."""
    actor_id: str
    escalation_type: str
    target_accountability_chain: List[str]
    action_description: str
    timeline: timedelta
    success_criteria: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ImpactValidation:
    """Validation result for decision impact assessment."""
    decision_id: str
    impact_level: str
    threshold_compliance: bool
    required_approvals: List[str]
    validation_criteria: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyClaim:
    """Claim of emergency or exception status."""
    claim_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = ""
    claim_type: str = ""  # emergency, exception, urgent
    justification: str = ""
    requested_bypasses: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyValidation:
    """Validation result for emergency claims."""
    claim_id: str
    is_valid: bool
    validation_criteria: Dict[str, Any]
    approved_bypasses: List[str]
    conditions: List[str]
    expiry: Optional[datetime] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VerificationRequirement:
    """Accountability verification requirement for a decision."""
    decision_id: str
    required_verifiers: List[str]
    verification_type: str
    deadline: datetime
    escalation_path: List[str]
    bypass_conditions: List[str] = field(default_factory=list)


@dataclass
class AuditEntry:
    """Audit log entry for governance tracking."""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    actor_id: str = ""
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    immutable_hash: Optional[str] = None


@dataclass
class RealityCheckFailure:
    """Details of a reality check failure."""
    failure_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str = ""
    actor_id: str = ""
    failure_type: str = ""
    failure_reason: str = ""
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class IndependenceClaim:
    """Claim of independence from accountability."""
    claim_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = ""
    claimed_independence_type: str = ""
    justification: str = ""
    supporting_evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchResult:
    """Result of independence claim research."""
    claim_id: str
    research_findings: Dict[str, Any]
    actual_constraints: List[ConstraintSource]
    independence_validity: bool
    confidence_score: float
    research_method: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChainChange:
    """Change to an accountability chain."""
    change_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = ""
    change_type: str = ""  # addition, removal, modification
    old_relationship: Optional[AccountabilityRelationship] = None
    new_relationship: Optional[AccountabilityRelationship] = None
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MappingUpdate:
    """Result of governance mapping update."""
    update_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    affected_actors: List[str] = field(default_factory=list)
    changes_applied: List[ChainChange] = field(default_factory=list)
    synchronization_status: str = ""
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HumanEscalation:
    """Escalation to human oversight."""
    escalation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    escalation_type: str = ""
    actor_id: str = ""
    issue_description: str = ""
    assigned_investigator: Optional[str] = None
    priority: str = "medium"
    deadline: Optional[datetime] = None
    status: str = "open"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SuccessMetrics:
    """System success metrics for accountability scaling."""
    metric_period: timedelta
    growth_rate: float
    user_satisfaction: float
    system_reliability: float
    governance_effectiveness: float
    baseline_comparison: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RequirementScaling:
    """Scaled accountability requirements."""
    scaling_factor: float
    new_requirements: Dict[str, Any]
    affected_processes: List[str]
    implementation_timeline: timedelta
    rollback_plan: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GrowthRate:
    """System growth rate metrics."""
    user_growth_rate: float
    transaction_growth_rate: float
    decision_volume_growth: float
    complexity_growth_rate: float
    period: timedelta
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProtocolImplementation:
    """Implementation of enhanced reality check protocols."""
    protocol_type: str
    enhanced_checks: List[str]
    frequency_increase: float
    resource_requirements: Dict[str, Any]
    success_criteria: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Claim:
    """Generic claim made by an actor."""
    claim_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = ""
    claim_type: str = ""
    description: str = ""
    supporting_evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FailureSimulation:
    """Mandatory failure simulation requirements."""
    simulation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_claims: List[Claim] = field(default_factory=list)
    simulation_scenarios: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    timeline: timedelta = timedelta(days=30)
    responsible_parties: List[str] = field(default_factory=list)


@dataclass
class Bypass:
    """Governance bypass attempt."""
    bypass_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = ""
    bypass_type: str = ""
    target_process: str = ""
    justification: str = ""
    success: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmergencyGovernance:
    """Emergency governance protocols."""
    protocol_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_events: List[Bypass] = field(default_factory=list)
    activated_measures: List[str] = field(default_factory=list)
    responsible_authorities: List[str] = field(default_factory=list)
    duration: timedelta = timedelta(hours=24)
    success_criteria: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TriggerEvent:
    """Event that triggers governance intervention."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    actor_id: str = ""
    severity: str = ""
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EscalationStep:
    """Step in governance escalation path."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_order: int = 0
    responsible_party: str = ""
    action_required: str = ""
    timeline: timedelta = timedelta(hours=24)
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class SuccessCriterion:
    """Criterion for measuring intervention success."""
    criterion_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    measurement_method: str = ""
    target_value: Union[str, float, int] = ""
    tolerance: float = 0.1


@dataclass
class RollbackPlan:
    """Plan for rolling back governance interventions."""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_conditions: List[str] = field(default_factory=list)
    rollback_steps: List[str] = field(default_factory=list)
    responsible_parties: List[str] = field(default_factory=list)
    timeline: timedelta = timedelta(hours=4)


@dataclass
class GovernanceIntervention:
    """Complete governance intervention specification."""
    intervention_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_event: TriggerEvent = field(default_factory=lambda: TriggerEvent())
    intervention_type: InterventionType = InterventionType.WARNING
    target_actor: str = ""
    accountability_chain: Optional[AccountabilityChain] = None
    escalation_path: List[EscalationStep] = field(default_factory=list)
    success_criteria: List[SuccessCriterion] = field(default_factory=list)
    rollback_plan: Optional[RollbackPlan] = None
    status: str = "planned"
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class RealityCheckResult:
    """Complete result of reality check validation."""
    decision_id: str
    actor_id: str
    impact_validation: ImpactValidation
    accountability_verification: Optional[VerificationRequirement] = None
    emergency_claim_validation: Optional[EmergencyValidation] = None
    overall_result: RealityCheckOutcome = RealityCheckOutcome.PASSED
    required_actions: List[RecommendedAction] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)