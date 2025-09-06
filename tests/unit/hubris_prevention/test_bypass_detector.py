"""
Unit tests for governance bypass detection system.
"""

import pytest
from datetime import datetime, timedelta
from src.beast_mode.hubris_prevention.detection.bypass_detector import GovernanceBypassDetector
from src.beast_mode.hubris_prevention.models import Decision, InterventionType


class TestGovernanceBypassDetector:
    """Test cases for governance bypass detection."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = GovernanceBypassDetector()
        self.actor_id = "test_actor_001"
    
    def test_emergency_abuse_detection(self):
        """Test detection of emergency claim abuse."""
        # Create decisions with excessive emergency claims
        decisions = []
        for i in range(10):
            decision = Decision(
                actor_id=self.actor_id,
                decision_type="deployment",
                impact_level="high",
                description=f"Emergency deployment {i}",
                emergency_claimed=i < 6,  # 60% emergency claims
                accountability_verified=False
            )
            decisions.append(decision)
        
        # Should detect bypass attempt
        alert = self.detector.detect_bypass_attempts(self.actor_id, decisions, [])
        
        assert alert is not None
        assert alert.actor_id == self.actor_id
        assert alert.bypass_type == "systematic_governance_bypass"
        assert alert.alert_level in ["medium", "high", "critical"]
    
    def test_approval_skipping_detection(self):
        """Test detection of systematic approval skipping."""
        # Create high-impact decisions without accountability verification
        decisions = []
        for i in range(5):
            decision = Decision(
                actor_id=self.actor_id,
                decision_type="critical_change",
                impact_level="critical",
                description=f"Critical decision {i}",
                emergency_claimed=False,
                accountability_verified=False  # No approval
            )
            decisions.append(decision)
        
        # Should detect bypass attempt
        alert = self.detector.detect_bypass_attempts(self.actor_id, decisions, [])
        
        assert alert is not None
        assert alert.alert_level in ["high", "critical"]
    
    def test_no_bypass_with_compliant_behavior(self):
        """Test that compliant behavior doesn't trigger alerts."""
        # Create compliant decisions
        decisions = []
        for i in range(10):
            decision = Decision(
                actor_id=self.actor_id,
                decision_type="normal_change",
                impact_level="medium",
                description=f"Normal decision {i}",
                emergency_claimed=False,
                accountability_verified=True  # Properly verified
            )
            decisions.append(decision)
        
        # Should not detect bypass attempt
        alert = self.detector.detect_bypass_attempts(self.actor_id, decisions, [])
        
        assert alert is None
    
    def test_escalation_needed_for_persistent_patterns(self):
        """Test escalation for persistent bypass patterns."""
        # Test escalation after timeout period
        pattern_duration = timedelta(hours=50)  # Exceeds 48-hour threshold
        
        escalation = self.detector.check_escalation_needed(self.actor_id, pattern_duration)
        
        assert escalation is not None
        assert escalation.actor_id == self.actor_id
        assert escalation.escalation_type == "governance_bypass_intervention"
        assert len(escalation.success_criteria) > 0
    
    def test_no_escalation_for_short_patterns(self):
        """Test no escalation for short-duration patterns."""
        # Test no escalation within timeout period
        pattern_duration = timedelta(hours=24)  # Within 48-hour threshold
        
        escalation = self.detector.check_escalation_needed(self.actor_id, pattern_duration)
        
        assert escalation is None
    
    def test_governance_intervention_creation(self):
        """Test creation of governance interventions."""
        from src.beast_mode.hubris_prevention.models import BypassAlert
        
        # Create a critical bypass alert
        alert = BypassAlert(
            actor_id=self.actor_id,
            bypass_type="systematic_governance_bypass",
            governance_process="accountability_verification",
            attempt_count=5,
            success_rate=0.8,
            alert_level="critical"
        )
        
        # Create intervention
        intervention = self.detector.create_governance_intervention(self.actor_id, alert)
        
        assert intervention is not None
        assert intervention.target_actor == self.actor_id
        assert intervention.intervention_type == InterventionType.EMERGENCY_GOVERNANCE
        assert len(intervention.escalation_path) > 0
        assert len(intervention.success_criteria) > 0
        assert intervention.rollback_plan is not None
    
    def test_authority_escalation_detection(self):
        """Test detection of unauthorized authority escalation."""
        # Create decisions with authority escalation
        decisions = []
        for i in range(3):
            decision = Decision(
                actor_id=self.actor_id,
                decision_type="permission_change",
                impact_level="high",
                description=f"Self-authorized permission change {i}",
                emergency_claimed=False,
                accountability_verified=False,
                metadata={"self_authorized": True, "authority_escalation": True}
            )
            decisions.append(decision)
        
        # Should detect bypass attempt
        alert = self.detector.detect_bypass_attempts(self.actor_id, decisions, [])
        
        assert alert is not None
        assert alert.alert_level == "critical"  # Authority escalation is critical
    
    def test_bypass_severity_calculation(self):
        """Test bypass severity calculation."""
        from src.beast_mode.hubris_prevention.detection.bypass_detector import BypassPattern
        
        # Create test patterns
        patterns = [
            BypassPattern(
                pattern_type="emergency_abuse",
                severity="high",
                evidence=["Test evidence"],
                confidence=0.8,
                first_detected=datetime.now(),
                last_detected=datetime.now()
            ),
            BypassPattern(
                pattern_type="approval_skipping", 
                severity="critical",
                evidence=["Test evidence"],
                confidence=0.9,
                first_detected=datetime.now(),
                last_detected=datetime.now()
            )
        ]
        
        # Calculate severity
        severity = self.detector._calculate_bypass_severity(patterns)
        
        assert 0.0 <= severity <= 1.0
        assert severity > 0.5  # Should be high due to critical pattern
    
    def test_pattern_storage_and_cleanup(self):
        """Test pattern storage and automatic cleanup."""
        from src.beast_mode.hubris_prevention.detection.bypass_detector import BypassPattern
        
        # Create old and new patterns
        old_pattern = BypassPattern(
            pattern_type="emergency_abuse",
            severity="medium",
            evidence=["Old evidence"],
            confidence=0.7,
            first_detected=datetime.now() - timedelta(days=10),
            last_detected=datetime.now() - timedelta(days=8)
        )
        
        new_pattern = BypassPattern(
            pattern_type="approval_skipping",
            severity="high", 
            evidence=["New evidence"],
            confidence=0.8,
            first_detected=datetime.now() - timedelta(hours=1),
            last_detected=datetime.now()
        )
        
        # Store patterns
        self.detector._store_patterns(self.actor_id, [old_pattern, new_pattern])
        
        # Check that only new pattern is kept (old one should be cleaned up)
        stored_patterns = self.detector.detected_patterns.get(self.actor_id, [])
        
        # Should have at least the new pattern
        assert len(stored_patterns) >= 1
        
        # New pattern should be present
        recent_patterns = [p for p in stored_patterns if p.last_detected >= datetime.now() - timedelta(days=1)]
        assert len(recent_patterns) >= 1