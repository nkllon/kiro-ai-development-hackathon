"""
Interfaces Services

This module was extracted from interfaces.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta
from .models import AccountabilityChain, HubrisScore, RealityCheckResult, GovernanceIntervention, Decision, Actor, VelocityAlert, BypassAlert, EscalationAction, ImpactValidation, EmergencyValidation, VerificationRequirement, AuditEntry, EmergencyClaim, RealityCheckFailure, IndependenceClaim, ResearchResult, ChainChange, MappingUpdate, HumanEscalation, SuccessMetrics, RequirementScaling, GrowthRate, ProtocolImplementation, FailureSimulation, EmergencyGovernance, Claim, Bypass

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
