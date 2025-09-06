"""
Unit tests for emergency claim validation system.
"""

import pytest
from datetime import datetime, timedelta
from src.beast_mode.hubris_prevention.validation.emergency_validator import EmergencyClaimValidator
from src.beast_mode.hubris_prevention.models import EmergencyClaim


class TestEmergencyClaimValidator:
    """Test cases for emergency claim validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = EmergencyClaimValidator()
    
    def test_valid_security_incident_claim(self):
        """Test validation of valid security incident claim."""
        claim = EmergencyClaim(
            claim_type="security_incident",
            justification="Active breach detected with confirmed data exposure. Incident report: INC-2024-001. Threat level: critical. Immediate response required.",
            requested_bypasses=["approval_delay", "standard_procedure"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(claim)
        
        assert validation.is_valid is True
        assert validation.claim_id == claim.claim_id
        assert len(validation.approved_bypasses) > 0
        assert validation.expiry is not None
        assert "Emergency claim validated" in validation.conditions
    
    def test_valid_system_outage_claim(self):
        """Test validation of valid system outage claim."""
        claim = EmergencyClaim(
            claim_type="system_outage",
            justification="Complete service failure detected. Alert ID: ALT-2024-001. Impact assessment shows 500+ affected users. Critical system down.",
            requested_bypasses=["monitoring", "notification"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(claim)
        
        assert validation.is_valid is True
        assert len(validation.approved_bypasses) > 0
        assert validation.validation_criteria['auto_approved'] is True  # Should auto-approve due to "complete service failure"
    
    def test_invalid_claim_unknown_type(self):
        """Test validation of claim with unknown emergency type."""
        claim = EmergencyClaim(
            claim_type="unknown_emergency",
            justification="Some emergency situation",
            requested_bypasses=["some_bypass"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(claim)
        
        assert validation.is_valid is False
        assert "Unknown emergency type" in validation.validation_criteria['error']
        assert len(validation.approved_bypasses) == 0
    
    def test_invalid_claim_timing(self):
        """Test validation of claim submitted too late."""
        # Create claim that's too old for security incident (max 4 hours)
        old_timestamp = datetime.now() - timedelta(hours=6)
        
        claim = EmergencyClaim(
            claim_type="security_incident",
            justification="Security incident with proper evidence",
            requested_bypasses=["approval_delay"],
            timestamp=old_timestamp
        )
        
        validation = self.validator.validate_emergency_claim(claim)
        
        assert validation.is_valid is False
        assert validation.validation_criteria['timing_valid'] is False
        assert "outside acceptable timeframe" in ' '.join(validation.conditions)
    
    def test_invalid_claim_insufficient_evidence(self):
        """Test validation of claim with insufficient evidence."""
        claim = EmergencyClaim(
            claim_type="security_incident",
            justification="There's some kind of security problem",  # Vague, no proper evidence
            requested_bypasses=["approval_delay"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(claim)
        
        assert validation.is_valid is False
        assert validation.validation_criteria['evidence_valid'] is False
        assert validation.validation_criteria['evidence_score'] < 0.5
    
    def test_regulatory_compliance_claim(self):
        """Test validation of regulatory compliance claim."""
        claim = EmergencyClaim(
            claim_type="regulatory_compliance",
            justification="Regulatory deadline approaching. Regulation reference: REG-2024-001. Legal assessment confirms compliance requirement.",
            requested_bypasses=["standard_review", "documentation"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(claim)
        
        assert validation.is_valid is True
        assert validation.validation_criteria['escalation_required'] is True
        assert validation.expiry is not None
    
    def test_data_breach_auto_approval(self):
        """Test auto-approval for confirmed data breach."""
        claim = EmergencyClaim(
            claim_type="data_breach",
            justification="Confirmed data exposure detected. Breach detected: true. Unauthorized access to customer data confirmed.",
            requested_bypasses=["all_procedures", "approval_chain"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(claim)
        
        assert validation.is_valid is True
        assert validation.validation_criteria['auto_approved'] is True
        assert len(validation.approved_bypasses) == len(claim.requested_bypasses)  # All bypasses approved
    
    def test_business_critical_partial_approval(self):
        """Test partial approval for business critical claim."""
        claim = EmergencyClaim(
            claim_type="business_critical",
            justification="Major customer commitment at risk. Business impact level: high. Revenue impact estimated at $50,000.",
            requested_bypasses=["monitoring", "high_risk_procedure", "documentation"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(claim)
        
        assert validation.is_valid is True
        assert validation.validation_criteria['auto_approved'] is False  # No auto-approve keywords
        # Should approve low-risk bypasses only
        approved_low_risk = [b for b in validation.approved_bypasses if 'monitoring' in b or 'documentation' in b]
        assert len(approved_low_risk) > 0
    
    def test_evidence_validation_patterns(self):
        """Test evidence validation against patterns."""
        # Test incident report pattern
        evidence = self.validator.validate_emergency_evidence(
            "Security incident report ID: INC-2024-001 shows critical breach",
            "incident_report"
        )
        assert evidence.confidence >= 0.5
        
        # Test monitoring alert pattern
        evidence = self.validator.validate_emergency_evidence(
            "Alert timestamp: 2024-01-01T10:00:00Z triggered",
            "monitoring_alerts"
        )
        assert evidence.confidence >= 0.5
        
        # Test invalid evidence
        evidence = self.validator.validate_emergency_evidence(
            "Something bad happened",
            "incident_report"
        )
        assert evidence.confidence < 0.5
    
    def test_evidence_confidence_factors(self):
        """Test evidence confidence calculation factors."""
        # Detailed evidence should get higher confidence
        detailed_evidence = "This is a very detailed incident report with comprehensive information about the security breach including timeline, affected systems, and impact assessment. Incident ID: INC-2024-001. Confirmed and verified by security team."
        
        evidence = self.validator.validate_emergency_evidence(detailed_evidence, "incident_report")
        
        # Should get bonus points for length and confirmation keywords
        assert evidence.confidence > 0.8
    
    def test_emergency_expiry_calculation(self):
        """Test emergency validation expiry calculation."""
        # Short duration emergency (system outage - 2 hours max)
        claim = EmergencyClaim(
            claim_type="system_outage",
            justification="Complete service failure with proper evidence",
            requested_bypasses=["monitoring"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(claim)
        
        if validation.is_valid and validation.expiry:
            # Should expire within 2 hours (system outage max duration)
            time_until_expiry = validation.expiry - datetime.now()
            assert time_until_expiry <= timedelta(hours=2)
    
    def test_conditions_generation(self):
        """Test generation of validation conditions."""
        # Valid claim should have positive conditions
        valid_claim = EmergencyClaim(
            claim_type="system_outage",
            justification="Complete service failure. Alert ID: ALT-001. Impact assessment complete.",
            requested_bypasses=["monitoring"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(valid_claim)
        
        assert any("validated" in condition.lower() for condition in validation.conditions)
        
        # Invalid claim should have rejection conditions
        invalid_claim = EmergencyClaim(
            claim_type="security_incident",
            justification="Something happened",  # Insufficient evidence
            requested_bypasses=["approval_delay"],
            timestamp=datetime.now()
        )
        
        validation = self.validator.validate_emergency_claim(invalid_claim)
        
        assert any("rejected" in condition.lower() for condition in validation.conditions)