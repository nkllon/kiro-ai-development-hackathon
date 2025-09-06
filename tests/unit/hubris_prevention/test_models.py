"""
Unit tests for hubris prevention data models.
"""

import pytest
from datetime import datetime, timedelta
from src.beast_mode.hubris_prevention.models import (
    Actor, Decision, AccountabilityChain, HubrisScore, RealityCheckResult,
    TrendDirection, RiskLevel, InterventionType, RealityCheckOutcome
)


class TestActor:
    """Test cases for Actor model."""
    
    def test_actor_creation(self):
        """Test basic actor creation."""
        actor = Actor(
            actor_id="test_actor_001",
            name="Test Actor",
            role="developer",
            permissions=["read", "write"]
        )
        
        assert actor.actor_id == "test_actor_001"
        assert actor.name == "Test Actor"
        assert actor.role == "developer"
        assert actor.permissions == ["read", "write"]
        assert isinstance(actor.created_at, datetime)
        assert actor.last_active is None
        assert actor.metadata == {}
    
    def test_actor_with_metadata(self):
        """Test actor creation with metadata."""
        metadata = {"department": "engineering", "level": "senior"}
        actor = Actor(
            actor_id="test_actor_002",
            name="Senior Developer",
            role="senior_developer",
            permissions=["read", "write", "admin"],
            metadata=metadata
        )
        
        assert actor.metadata == metadata


class TestDecision:
    """Test cases for Decision model."""
    
    def test_decision_creation(self):
        """Test basic decision creation."""
        decision = Decision(
            actor_id="test_actor_001",
            decision_type="deployment",
            impact_level="high",
            description="Deploy to production"
        )
        
        assert decision.actor_id == "test_actor_001"
        assert decision.decision_type == "deployment"
        assert decision.impact_level == "high"
        assert decision.description == "Deploy to production"
        assert isinstance(decision.timestamp, datetime)
        assert decision.accountability_verified is False
        assert decision.emergency_claimed is False
        assert len(decision.decision_id) > 0  # UUID generated
    
    def test_decision_with_emergency_claim(self):
        """Test decision with emergency claim."""
        decision = Decision(
            actor_id="test_actor_001",
            decision_type="hotfix",
            impact_level="critical",
            description="Emergency security patch",
            emergency_claimed=True
        )
        
        assert decision.emergency_claimed is True


class TestAccountabilityChain:
    """Test cases for AccountabilityChain model."""
    
    def test_empty_accountability_chain(self):
        """Test creation of empty accountability chain."""
        chain = AccountabilityChain(actor_id="test_actor_001")
        
        assert chain.actor_id == "test_actor_001"
        assert chain.immediate_accountability == []
        assert chain.ultimate_accountability == []
        assert chain.constraint_sources == []
        assert chain.last_verified is None
        assert chain.verification_confidence == 0.0
        assert chain.discovery_method == ""


class TestHubrisScore:
    """Test cases for HubrisScore model."""
    
    def test_hubris_score_creation(self):
        """Test basic hubris score creation."""
        score = HubrisScore(
            actor_id="test_actor_001",
            score=0.3,
            trend_direction=TrendDirection.STABLE,
            risk_level=RiskLevel.LOW
        )
        
        assert score.actor_id == "test_actor_001"
        assert score.score == 0.3
        assert score.trend_direction == TrendDirection.STABLE
        assert score.risk_level == RiskLevel.LOW
        assert isinstance(score.calculated_at, datetime)
        assert score.valid_until is None
    
    def test_high_hubris_score(self):
        """Test high hubris score with critical risk."""
        score = HubrisScore(
            actor_id="test_actor_002",
            score=0.9,
            trend_direction=TrendDirection.WORSENING,
            risk_level=RiskLevel.CRITICAL
        )
        
        assert score.score == 0.9
        assert score.risk_level == RiskLevel.CRITICAL
        assert score.trend_direction == TrendDirection.WORSENING


class TestRealityCheckResult:
    """Test cases for RealityCheckResult model."""
    
    def test_reality_check_result_creation(self):
        """Test basic reality check result creation."""
        from src.beast_mode.hubris_prevention.models import ImpactValidation
        
        impact_validation = ImpactValidation(
            decision_id="decision_001",
            impact_level="medium",
            threshold_compliance=True,
            required_approvals=["manager"],
            validation_criteria={"threshold": 0.5}
        )
        
        result = RealityCheckResult(
            decision_id="decision_001",
            actor_id="test_actor_001",
            impact_validation=impact_validation,
            overall_result=RealityCheckOutcome.PASSED
        )
        
        assert result.decision_id == "decision_001"
        assert result.actor_id == "test_actor_001"
        assert result.overall_result == RealityCheckOutcome.PASSED
        assert isinstance(result.timestamp, datetime)


class TestEnums:
    """Test cases for enum values."""
    
    def test_trend_direction_values(self):
        """Test TrendDirection enum values."""
        assert TrendDirection.IMPROVING.value == "improving"
        assert TrendDirection.STABLE.value == "stable"
        assert TrendDirection.WORSENING.value == "worsening"
        assert TrendDirection.CRITICAL.value == "critical"
    
    def test_risk_level_values(self):
        """Test RiskLevel enum values."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"
    
    def test_intervention_type_values(self):
        """Test InterventionType enum values."""
        assert InterventionType.WARNING.value == "warning"
        assert InterventionType.ACCOUNTABILITY_VERIFICATION.value == "accountability_verification"
        assert InterventionType.REALITY_CHECK.value == "reality_check"
        assert InterventionType.QUARANTINE.value == "quarantine"
        assert InterventionType.EMERGENCY_GOVERNANCE.value == "emergency_governance"
    
    def test_reality_check_outcome_values(self):
        """Test RealityCheckOutcome enum values."""
        assert RealityCheckOutcome.PASSED.value == "passed"
        assert RealityCheckOutcome.FAILED.value == "failed"
        assert RealityCheckOutcome.REQUIRES_ESCALATION.value == "requires_escalation"
        assert RealityCheckOutcome.EMERGENCY_INTERVENTION.value == "emergency_intervention"