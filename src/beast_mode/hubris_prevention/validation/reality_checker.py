"""
Reality Check Engine Implementation

Implements systematic reality checks for all high-impact decisions,
ensuring no actor believes they are the final arbiter.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import hashlib

from ..interfaces import RealityChecker
from ..models import (
    Decision, ImpactValidation, EmergencyClaim, EmergencyValidation,
    VerificationRequirement, RealityCheckFailure, AuditEntry
)


class RealityCheckerImpl(RealityChecker):
    """
    Implementation of systematic reality checking against objective criteria.
    
    Validates decisions against predefined thresholds and accountability chains
    to prevent actors from believing they are the final arbiter.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Impact thresholds configuration
        self.impact_thresholds = {
            'low': {
                'financial_limit': 1000,
                'user_impact': 100,
                'system_downtime': timedelta(minutes=5),
                'required_approvals': []
            },
            'medium': {
                'financial_limit': 10000,
                'user_impact': 1000,
                'system_downtime': timedelta(minutes=30),
                'required_approvals': ['team_lead']
            },
            'high': {
                'financial_limit': 100000,
                'user_impact': 10000,
                'system_downtime': timedelta(hours=2),
                'required_approvals': ['team_lead', 'department_head']
            },
            'critical': {
                'financial_limit': 1000000,
                'user_impact': 100000,
                'system_downtime': timedelta(hours=8),
                'required_approvals': ['team_lead', 'department_head', 'executive']
            }
        }
        
        # Emergency validation criteria
        self.emergency_criteria = {
            'security_incident': {
                'max_duration': timedelta(hours=4),
                'required_evidence': ['incident_report', 'threat_assessment'],
                'auto_approve_conditions': ['active_breach', 'data_exposure']
            },
            'system_outage': {
                'max_duration': timedelta(hours=2),
                'required_evidence': ['monitoring_alerts', 'impact_assessment'],
                'auto_approve_conditions': ['complete_service_failure']
            },
            'regulatory_compliance': {
                'max_duration': timedelta(hours=24),
                'required_evidence': ['regulatory_notice', 'legal_assessment'],
                'auto_approve_conditions': ['regulatory_deadline']
            }
        }
    
    def validate_impact_threshold(self, decision: Decision) -> ImpactValidation:
        """
        Validate decision impact against predefined thresholds.
        
        Implements objective criteria validation to prevent subjective
        impact assessment and ensure proper accountability verification.
        """
        self.logger.info(f"Validating impact threshold for decision {decision.decision_id}")
        
        # Extract impact metrics from decision metadata
        financial_impact = decision.metadata.get('financial_impact', 0)
        user_impact = decision.metadata.get('user_impact', 0)
        system_downtime = decision.metadata.get('system_downtime', timedelta(0))
        
        # Determine actual impact level based on objective criteria
        actual_impact_level = self._calculate_impact_level(
            financial_impact, user_impact, system_downtime
        )
        
        # Check if claimed impact level matches actual
        claimed_impact = decision.impact_level
        threshold_compliance = self._validate_impact_consistency(
            claimed_impact, actual_impact_level
        )
        
        # Determine required approvals
        required_approvals = self.impact_thresholds[actual_impact_level]['required_approvals']
        
        # Build validation criteria
        validation_criteria = {
            'claimed_impact': claimed_impact,
            'calculated_impact': actual_impact_level,
            'financial_impact': financial_impact,
            'user_impact': user_impact,
            'system_downtime': str(system_downtime),
            'threshold_met': threshold_compliance,
            'validation_method': 'objective_criteria_analysis'
        }
        
        return ImpactValidation(
            decision_id=decision.decision_id,
            impact_level=actual_impact_level,
            threshold_compliance=threshold_compliance,
            required_approvals=required_approvals,
            validation_criteria=validation_criteria
        )
    
    def verify_emergency_claims(self, claim: EmergencyClaim) -> EmergencyValidation:
        """
        Verify emergency or exception claims against objective criteria.
        
        Prevents abuse of emergency status by validating claims against
        documented criteria and evidence requirements.
        """
        self.logger.info(f"Verifying emergency claim {claim.claim_id}")
        
        # Get criteria for this claim type
        criteria = self.emergency_criteria.get(claim.claim_type, {})
        if not criteria:
            # Unknown claim type - default to strict validation
            return EmergencyValidation(
                claim_id=claim.claim_id,
                is_valid=False,
                validation_criteria={'error': 'Unknown emergency claim type'},
                approved_bypasses=[],
                conditions=['Manual review required']
            )
        
        # Validate claim timing
        claim_age = datetime.now() - claim.timestamp
        max_duration = criteria.get('max_duration', timedelta(hours=1))
        timing_valid = claim_age <= max_duration
        
        # Validate required evidence
        required_evidence = criteria.get('required_evidence', [])
        provided_evidence = claim.justification  # Simplified - would parse actual evidence
        evidence_valid = len(required_evidence) == 0 or bool(provided_evidence)
        
        # Check auto-approve conditions
        auto_approve_conditions = criteria.get('auto_approve_conditions', [])
        auto_approved = any(
            condition.lower() in claim.justification.lower() 
            for condition in auto_approve_conditions
        )
        
        # Determine validity
        is_valid = timing_valid and evidence_valid
        
        # Determine approved bypasses
        approved_bypasses = []
        if is_valid:
            if auto_approved:
                approved_bypasses = claim.requested_bypasses
            else:
                # Partial approval - only low-risk bypasses
                approved_bypasses = [
                    bypass for bypass in claim.requested_bypasses 
                    if 'low_risk' in bypass or 'monitoring' in bypass
                ]
        
        # Set conditions and expiry
        conditions = []
        expiry = None
        
        if is_valid:
            conditions.append("Emergency status verified")
            if not auto_approved:
                conditions.append("Requires ongoing monitoring")
                conditions.append("Subject to post-incident review")
            expiry = datetime.now() + max_duration
        else:
            conditions.append("Emergency claim rejected")
            if not timing_valid:
                conditions.append("Claim submitted outside acceptable timeframe")
            if not evidence_valid:
                conditions.append("Insufficient supporting evidence")
        
        validation_criteria = {
            'claim_type': claim.claim_type,
            'timing_valid': timing_valid,
            'evidence_valid': evidence_valid,
            'auto_approved': auto_approved,
            'claim_age_minutes': int(claim_age.total_seconds() / 60),
            'max_duration_minutes': int(max_duration.total_seconds() / 60)
        }
        
        return EmergencyValidation(
            claim_id=claim.claim_id,
            is_valid=is_valid,
            validation_criteria=validation_criteria,
            approved_bypasses=approved_bypasses,
            conditions=conditions,
            expiry=expiry
        )
    
    def require_accountability_verification(self, actor_id: str, decision: Decision) -> VerificationRequirement:
        """
        Determine accountability verification requirements for decisions.
        
        Implements the "everyone has a mama" principle by requiring
        appropriate accountability verification based on decision impact.
        """
        self.logger.info(f"Determining verification requirements for actor {actor_id}, decision {decision.decision_id}")
        
        # Validate impact first
        impact_validation = self.validate_impact_threshold(decision)
        
        # Determine required verifiers based on impact level
        required_verifiers = impact_validation.required_approvals.copy()
        
        # Add additional verifiers for specific decision types
        if decision.decision_type == 'deployment':
            required_verifiers.append('deployment_manager')
        elif decision.decision_type == 'security_change':
            required_verifiers.append('security_officer')
        elif decision.decision_type == 'data_access':
            required_verifiers.append('data_protection_officer')
        
        # Remove duplicates while preserving order
        required_verifiers = list(dict.fromkeys(required_verifiers))
        
        # Determine verification type
        verification_type = 'standard'
        if decision.emergency_claimed:
            verification_type = 'emergency'
        elif impact_validation.impact_level == 'critical':
            verification_type = 'critical'
        
        # Set deadline based on impact and type
        if verification_type == 'emergency':
            deadline = datetime.now() + timedelta(hours=2)
        elif impact_validation.impact_level == 'critical':
            deadline = datetime.now() + timedelta(hours=8)
        else:
            deadline = datetime.now() + timedelta(hours=24)
        
        # Define escalation path
        escalation_path = required_verifiers.copy()
        if 'governance_board' not in escalation_path:
            escalation_path.append('governance_board')
        
        # Define bypass conditions (very restrictive)
        bypass_conditions = []
        if verification_type == 'emergency':
            bypass_conditions = [
                'Active security breach with data exposure',
                'Complete system failure affecting all users',
                'Regulatory deadline with legal consequences'
            ]
        
        return VerificationRequirement(
            decision_id=decision.decision_id,
            required_verifiers=required_verifiers,
            verification_type=verification_type,
            deadline=deadline,
            escalation_path=escalation_path,
            bypass_conditions=bypass_conditions
        )
    
    def log_reality_check_failures(self, failure: RealityCheckFailure) -> AuditEntry:
        """
        Log reality check failures for audit and oversight.
        
        Creates immutable audit entries for all reality check failures
        to ensure accountability and enable pattern analysis.
        """
        self.logger.warning(f"Logging reality check failure {failure.failure_id}")
        
        # Create comprehensive audit data
        audit_data = {
            'failure_id': failure.failure_id,
            'decision_id': failure.decision_id,
            'actor_id': failure.actor_id,
            'failure_type': failure.failure_type,
            'failure_reason': failure.failure_reason,
            'impact_assessment': failure.impact_assessment,
            'failure_timestamp': failure.timestamp.isoformat(),
            'system_state': self._capture_system_state(),
            'accountability_chain_status': 'unknown'  # Would be populated by MamaDiscoverer
        }
        
        # Generate immutable hash
        audit_content = str(sorted(audit_data.items()))
        immutable_hash = hashlib.sha256(audit_content.encode()).hexdigest()
        
        audit_entry = AuditEntry(
            event_type="reality_check_failure",
            actor_id=failure.actor_id,
            description=f"Reality check failure: {failure.failure_type} - {failure.failure_reason}",
            data=audit_data,
            immutable_hash=immutable_hash
        )
        
        # Log for immediate alerting
        self.logger.error(
            f"REALITY CHECK FAILURE: Actor {failure.actor_id} - {failure.failure_type} - {failure.failure_reason}"
        )
        
        return audit_entry
    
    def _calculate_impact_level(self, financial_impact: float, user_impact: int, system_downtime: timedelta) -> str:
        """Calculate actual impact level based on objective criteria."""
        # Check each threshold level from highest to lowest
        for level in ['critical', 'high', 'medium', 'low']:
            thresholds = self.impact_thresholds[level]
            
            if (financial_impact >= thresholds['financial_limit'] or
                user_impact >= thresholds['user_impact'] or
                system_downtime >= thresholds['system_downtime']):
                return level
        
        return 'low'
    
    def _validate_impact_consistency(self, claimed_impact: str, actual_impact: str) -> bool:
        """Validate consistency between claimed and calculated impact levels."""
        # Define impact level hierarchy
        impact_hierarchy = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        
        claimed_level = impact_hierarchy.get(claimed_impact, 0)
        actual_level = impact_hierarchy.get(actual_impact, 0)
        
        # Allow claiming up to one level higher than calculated (for safety margin)
        # But flag significant under-reporting as potential hubris
        return abs(claimed_level - actual_level) <= 1
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """Capture current system state for audit purposes."""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_load': 'normal',  # Would integrate with monitoring
            'active_incidents': 0,    # Would integrate with incident management
            'governance_status': 'active'
        }