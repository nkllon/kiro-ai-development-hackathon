"""
Core interfaces for the Systematic Hubris Prevention framework.

These interfaces define the contracts for all hubris prevention components,
ensuring systematic accountability and humility enforcement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta

from .models import (
    AccountabilityChain, HubrisScore, RealityCheckResult, GovernanceIntervention,
    Decision, Actor, VelocityAlert, BypassAlert, EscalationAction,
    ImpactValidation, EmergencyValidation, VerificationRequirement, AuditEntry,
    EmergencyClaim, RealityCheckFailure, IndependenceClaim, ResearchResult,
    ChainChange, MappingUpdate, HumanEscalation, SuccessMetrics, RequirementScaling,
    GrowthRate, ProtocolImplementation, FailureSimulation, EmergencyGovernance,
    Claim, Bypass
)


class HubrisDetector(ABC):
    """
    Interface for detecting hubris patterns in actor decision-making.
    
    Implements automated detection of when actors begin to believe they operate
    outside accountability chains, triggering appropriate interventions.
    """
    
    @abstractmethod
    def detect_patterns(self, actor_id: str, decision_history: List[Decision]) -> HubrisScore:
        """
        Analyze decision patterns for hubris indicators.
        
        Args:
            actor_id: Unique identifier for the actor
            decision_history: Recent decisions made by the actor
            
        Returns:
            HubrisScore with risk assessment and recommended actions
        """
        pass
    
    @abstractmethod
    def analyze_velocity(self, decisions: List[Decision], timeframe: timedelta) -> VelocityAlert:
        """
        Analyze decision velocity for accountability verification gaps.
        
        Args:
            decisions: List of decisions to analyze
            timeframe: Time window for velocity analysis
            
        Returns:
            VelocityAlert if decision rate exceeds accountability verification rate
        """
        pass
    
    @abstractmethod
    def check_bypass_attempts(self, actor_id: str, governance_events: List) -> BypassAlert:
        """
        Detect attempts to bypass established governance processes.
        
        Args:
            actor_id: Actor to check for bypass attempts
            governance_events: Recent governance-related events
            
        Returns:
            BypassAlert if governance bypass patterns detected
        """
        pass
    
    @abstractmethod
    def escalate_persistent_patterns(self, actor_id: str, pattern_duration: timedelta) -> EscalationAction:
        """
        Escalate hubris patterns that persist beyond acceptable thresholds.
        
        Args:
            actor_id: Actor with persistent hubris patterns
            pattern_duration: How long the patterns have persisted
            
        Returns:
            EscalationAction for governance restoration
        """
        pass


class RealityChecker(ABC):
    """
    Interface for systematic reality checks on high-impact decisions.
    
    Ensures no actor believes they are the final arbiter by validating
    decisions against objective criteria and accountability chains.
    """
    
    @abstractmethod
    def validate_impact_threshold(self, decision: Decision) -> ImpactValidation:
        """
        Validate decision impact against predefined thresholds.
        
        Args:
            decision: Decision to validate
            
        Returns:
            ImpactValidation with threshold compliance assessment
        """
        pass
    
    @abstractmethod
    def verify_emergency_claims(self, claim: EmergencyClaim) -> EmergencyValidation:
        """
        Verify emergency or exception claims against objective criteria.
        
        Args:
            claim: Emergency claim to verify
            
        Returns:
            EmergencyValidation with authenticity assessment
        """
        pass
    
    @abstractmethod
    def require_accountability_verification(self, actor_id: str, decision: Decision) -> VerificationRequirement:
        """
        Determine accountability verification requirements for decisions.
        
        Args:
            actor_id: Actor making the decision
            decision: Decision requiring verification
            
        Returns:
            VerificationRequirement specifying needed accountability checks
        """
        pass
    
    @abstractmethod
    def log_reality_check_failures(self, failure: RealityCheckFailure) -> AuditEntry:
        """
        Log reality check failures for audit and oversight.
        
        Args:
            failure: Details of the reality check failure
            
        Returns:
            AuditEntry for governance tracking
        """
        pass


class MamaDiscoverer(ABC):
    """
    Interface for automatic discovery of accountability chains.
    
    Implements the "everyone has a mama" principle by systematically
    discovering and mapping accountability relationships.
    """
    
    @abstractmethod
    def discover_accountability_chain(self, actor_id: str) -> AccountabilityChain:
        """
        Discover the complete accountability chain for an actor.
        
        Args:
            actor_id: Actor to discover accountability chain for
            
        Returns:
            AccountabilityChain with complete relationship mapping
        """
        pass
    
    @abstractmethod
    def research_independence_claims(self, actor_id: str, claim: IndependenceClaim) -> ResearchResult:
        """
        Research and validate claims of independence from accountability.
        
        Args:
            actor_id: Actor claiming independence
            claim: Details of the independence claim
            
        Returns:
            ResearchResult with validation findings
        """
        pass
    
    @abstractmethod
    def update_governance_mappings(self, chain_changes: List[ChainChange]) -> MappingUpdate:
        """
        Update governance mappings when accountability chains change.
        
        Args:
            chain_changes: List of accountability chain modifications
            
        Returns:
            MappingUpdate with synchronization results
        """
        pass
    
    @abstractmethod
    def escalate_discovery_failures(self, actor_id: str, failure_reason: str) -> HumanEscalation:
        """
        Escalate accountability chain discovery failures to human oversight.
        
        Args:
            actor_id: Actor for whom discovery failed
            failure_reason: Reason for discovery failure
            
        Returns:
            HumanEscalation for manual investigation
        """
        pass


class HumilityEnforcer(ABC):
    """
    Interface for systematic humility enforcement mechanisms.
    
    Implements built-in humility mechanisms that scale with system growth,
    ensuring success doesn't breed dangerous overconfidence.
    """
    
    @abstractmethod
    def scale_accountability_requirements(self, success_metrics: SuccessMetrics) -> RequirementScaling:
        """
        Scale accountability requirements based on success metrics.
        
        Args:
            success_metrics: Current system success indicators
            
        Returns:
            RequirementScaling with updated accountability requirements
        """
        pass
    
    @abstractmethod
    def implement_reality_check_protocols(self, growth_rate: GrowthRate) -> ProtocolImplementation:
        """
        Implement additional reality check protocols during growth.
        
        Args:
            growth_rate: Current system growth rate
            
        Returns:
            ProtocolImplementation with enhanced reality check procedures
        """
        pass
    
    @abstractmethod
    def mandate_failure_simulation(self, infallibility_claims: List[Claim]) -> FailureSimulation:
        """
        Mandate failure simulation for components claiming infallibility.
        
        Args:
            infallibility_claims: Claims of infallibility to address
            
        Returns:
            FailureSimulation requirements for humility restoration
        """
        pass
    
    @abstractmethod
    def activate_emergency_governance(self, bypass_attempts: List[Bypass]) -> EmergencyGovernance:
        """
        Activate emergency governance protocols for persistent bypass attempts.
        
        Args:
            bypass_attempts: List of governance bypass attempts
            
        Returns:
            EmergencyGovernance protocols for system protection
        """
        pass


class BoundaryManager(ABC):
    """
    Interface for fort boundary management and enforcement.
    
    Maintains clear definition and enforcement of accountability boundaries,
    ensuring systematic governance within the "fort."
    """
    
    @abstractmethod
    def define_accountability_boundaries(self, actors: List[Actor]) -> dict:
        """Define clear accountability boundaries for system actors."""
        pass
    
    @abstractmethod
    def enforce_boundary_compliance(self, actor_id: str) -> bool:
        """Enforce accountability boundary compliance for actors."""
        pass
    
    @abstractmethod
    def implement_quarantine_protocols(self, violating_actors: List[str]) -> dict:
        """Implement quarantine protocols for boundary violations."""
        pass


class CorruptionPreventer(ABC):
    """
    Interface for proactive corruption detection and prevention.
    
    Maintains system integrity as power and influence grow by detecting
    and preventing corruption patterns before they cause damage.
    """
    
    @abstractmethod
    def monitor_power_concentration(self, actors: List[Actor]) -> dict:
        """Monitor and detect excessive power concentration."""
        pass
    
    @abstractmethod
    def detect_self_interest_bias(self, actor_id: str, decisions: List[Decision]) -> dict:
        """Detect decision patterns showing bias toward self-interest."""
        pass
    
    @abstractmethod
    def implement_emergency_intervention(self, corruption_indicators: dict) -> GovernanceIntervention:
        """Implement emergency governance intervention for critical corruption."""
        pass