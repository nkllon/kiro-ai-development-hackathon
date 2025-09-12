"""
Interfaces Validation

This module was extracted from interfaces.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta
from .models import AccountabilityChain, HubrisScore, RealityCheckResult, GovernanceIntervention, Decision, Actor, VelocityAlert, BypassAlert, EscalationAction, ImpactValidation, EmergencyValidation, VerificationRequirement, AuditEntry, EmergencyClaim, RealityCheckFailure, IndependenceClaim, ResearchResult, ChainChange, MappingUpdate, HumanEscalation, SuccessMetrics, RequirementScaling, GrowthRate, ProtocolImplementation, FailureSimulation, EmergencyGovernance, Claim, Bypass

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
def log_reality_check_failures(self, failure: RealityCheckFailure) -> AuditEntry:
    """
        Log reality check failures for audit and oversight.
        
        Args:
            failure: Details of the reality check failure
            
        Returns:
            AuditEntry for governance tracking
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
