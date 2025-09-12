"""
Models Core

This module was extracted from models.py
as part of RM-DDD compliance refactoring.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class ThreatLevel(Enum):
    """Competitive threat severity levels"""
    IMMEDIATE = 'immediate'
    URGENT = 'urgent'
    MONITOR = 'monitor'

class PlatformType(Enum):
    """Supported platform types"""
    GKE = 'gke'
    TIDB = 'tidb'
    KIRO = 'kiro'

@dataclass
class CompetitorMove:
    """Represents a competitive move by a competitor"""
    competitor: str
    move_type: str
    announcement_date: datetime
    description: str
    market_impact: float
    response_urgency: ThreatLevel

@dataclass
class MarketTrend:
    """Represents a market trend or opportunity"""
    trend_name: str
    description: str
    impact_score: float
    alignment_with_systematic: float
    opportunity_size: str

@dataclass
class CustomerFeedback:
    """Customer feedback mentioning competitors"""
    customer_id: str
    feedback_text: str
    mentioned_competitors: List[str]
    sentiment: str
    competitive_insights: List[str]

@dataclass
class DeadlinePressure:
    """Current deadline pressure metrics"""
    days_remaining: int
    critical_path_risk: float
    scope_reduction_needed: bool
    acceleration_required: bool

@dataclass
class ResourceConstraints:
    """Current resource constraints"""
    team_capacity: int
    budget_remaining: float
    platform_quotas: Dict[PlatformType, int]
    technical_debt_level: float

@dataclass
class MarketConditions:
    """Current market conditions affecting competitive strategy"""
    competitor_moves: List[CompetitorMove]
    market_trends: List[MarketTrend]
    customer_feedback: List[CustomerFeedback]
    deadline_pressure: DeadlinePressure
    resource_constraints: ResourceConstraints

@dataclass
class CompetitiveThreat:
    """A specific competitive threat requiring response"""
    competitor: str
    threat_type: str
    impact_level: float
    response_urgency: ThreatLevel
    market_impact: Dict[str, Any]
    detection_time: datetime
    response_deadline: datetime

@dataclass
class GKEResources:
    """GKE platform resource allocation"""
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    auto_scaling_enabled: bool
    cost_budget: float

@dataclass
class TiDBResources:
    """TiDB platform resource allocation"""
    nodes: int
    storage_gb: int
    htap_enabled: bool
    analytics_workloads: int
    cost_budget: float

@dataclass
class KiroResources:
    """Kiro platform resource allocation"""
    ai_agents: int
    spec_processing_capacity: int
    automation_workflows: int
    cost_budget: float

@dataclass
class CoordinationPlan:
    """Cross-platform coordination plan"""
    sync_frequency: str
    data_consistency_requirements: List[str]
    failover_protocols: List[str]
    monitoring_strategy: str

@dataclass
class CostOptimization:
    """Cost optimization strategy"""
    platform_priorities: List[PlatformType]
    cost_reduction_targets: Dict[PlatformType, float]
    efficiency_metrics: Dict[str, float]

@dataclass
class PlatformAllocation:
    """Resource allocation across all platforms"""
    gke_resources: GKEResources
    tidb_resources: TiDBResources
    kiro_resources: KiroResources
    cross_platform_coordination: CoordinationPlan
    cost_optimization: CostOptimization

@dataclass
class GKEDeploymentSpec:
    """GKE deployment specification"""
    cluster_name: str
    node_pools: List[Dict[str, Any]]
    services: List[str]
    scaling_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]

@dataclass
class TiDBDeploymentSpec:
    """TiDB deployment specification"""
    cluster_name: str
    pd_nodes: int
    tikv_nodes: int
    tidb_nodes: int
    storage_config: Dict[str, Any]
    analytics_config: Dict[str, Any]

@dataclass
class KiroDeploymentSpec:
    """Kiro deployment specification"""
    workspace_name: str
    ai_agents: List[str]
    automation_workflows: List[str]
    spec_processing_config: Dict[str, Any]
    quality_gates: List[str]

@dataclass
class SyncStrategy:
    """Cross-platform synchronization strategy"""
    data_sync_method: str
    conflict_resolution: str
    consistency_guarantees: List[str]
    performance_requirements: Dict[str, Any]

@dataclass
class FailoverPlan:
    """Platform failure recovery plan"""
    primary_platforms: List[PlatformType]
    failover_triggers: List[str]
    recovery_procedures: List[str]
    degraded_mode_capabilities: List[str]

@dataclass
class MultiPlatformDeployment:
    """Multi-platform deployment configuration"""
    gke_deployment: GKEDeploymentSpec
    tidb_deployment: TiDBDeploymentSpec
    kiro_deployment: KiroDeploymentSpec
    synchronization_strategy: SyncStrategy
    failover_plan: FailoverPlan

@dataclass
class SystematicMetrics:
    """Systematic superiority metrics"""
    development_speed: float
    quality_score: float
    reliability_score: float
    maintainability_score: float
    test_coverage: float

@dataclass
class FMHImplementation:
    """FMH principles implementation metrics"""
    accountability_chains: int
    decision_traceability: float
    systematic_governance: float
    human_oversight: float

@dataclass
class AccountabilityImplementation:
    """Accountability implementation metrics"""
    decision_audit_trail: float
    responsibility_assignment: float
    escalation_protocols: float
    performance_tracking: float

@dataclass
class RequirementsDrivenEvidence:
    """Evidence of requirements-driven development"""
    requirements_coverage: float
    implementation_traceability: float
    validation_automation: float
    change_propagation: float

@dataclass
class TimeToMarketAdvantage:
    """Time to market competitive advantage"""
    development_velocity: float
    deployment_speed: float
    feature_delivery: float
    market_response: float

@dataclass
class CompetitiveAdvantage:
    """Overall competitive advantage metrics"""
    systematic_superiority: SystematicMetrics
    fmh_principles: FMHImplementation
    accountability_chains: AccountabilityImplementation
    requirements_driven: RequirementsDrivenEvidence
    time_to_market: TimeToMarketAdvantage

@dataclass
class StrategyExecution:
    """Result of competitive strategy execution"""
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime]
    platforms_deployed: List[PlatformType]
    success_metrics: Dict[str, float]
    issues_encountered: List[str]
    adaptations_made: List[str]

@dataclass
class ResponsePlan:
    """Plan for responding to competitive threats"""
    plan_id: str
    threat_id: str
    response_strategy: str
    timeline: Dict[str, datetime]
    resources_required: PlatformAllocation
    success_criteria: List[str]
    risk_mitigation: List[str]

@dataclass
class AllocationPlan:
    """Resource allocation plan"""
    plan_id: str
    allocation_strategy: str
    platform_allocations: PlatformAllocation
    optimization_goals: List[str]
    constraints: List[str]
    expected_outcomes: Dict[str, float]
