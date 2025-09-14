"""
Reality Checker Validation

This module was extracted from reality_checker.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import hashlib
from ..interfaces import RealityChecker
from ..models import Decision, ImpactValidation, EmergencyClaim, EmergencyValidation, VerificationRequirement, RealityCheckFailure, AuditEntry
from src.rm_ddd.core.health import ModuleHealth


class ValidateimpactthresholdClass:
    """Auto-generated class for functions."""

    def validate_impact_threshold(self, decision: Decision) -> ImpactValidation:
    """
    Validate decision impact against predefined thresholds.

    Implements objective criteria validation to prevent subjective
    impact assessment and ensure proper accountability verification.
    """
    self.logger.info(f'Validating impact threshold for decision {decision.decision_id}')
    financial_impact = decision.metadata.get('financial_impact', 0)
    user_impact = decision.metadata.get('user_impact', 0)
    system_downtime = decision.metadata.get('system_downtime', timedelta(0))
    actual_impact_level = self._calculate_impact_level(financial_impact, user_impact, system_downtime)
    claimed_impact = decision.impact_level
    threshold_compliance = self._validate_impact_consistency(claimed_impact, actual_impact_level)
    required_approvals = self.impact_thresholds[actual_impact_level]['required_approvals']
    validation_criteria = {'claimed_impact': claimed_impact, 'calculated_impact': actual_impact_level, 'financial_impact': financial_impact, 'user_impact': user_impact, 'system_downtime': str(system_downtime), 'threshold_met': threshold_compliance, 'validation_method': 'objective_criteria_analysis'}
    return ImpactValidation(decision_id=decision.decision_id, impact_level=actual_impact_level, threshold_compliance=threshold_compliance, required_approvals=required_approvals, validation_criteria=validation_criteria)

    def verify_emergency_claims(self, claim: EmergencyClaim) -> EmergencyValidation:
    """
    Verify emergency or exception claims against objective criteria.

    Prevents abuse of emergency status by validating claims against
    documented criteria and evidence requirements.
    """
    self.logger.info(f'Verifying emergency claim {claim.claim_id}')
    criteria = self.emergency_criteria.get(claim.claim_type, {})
    if not criteria:
    return EmergencyValidation(claim_id=claim.claim_id, is_valid=False, validation_criteria={'error': 'Unknown emergency claim type'}, approved_bypasses=[], conditions=['Manual review required'])
    claim_age = datetime.now() - claim.timestamp
    max_duration = criteria.get('max_duration', timedelta(hours=1))
    timing_valid = claim_age <= max_duration
    required_evidence = criteria.get('required_evidence', [])
    provided_evidence = claim.justification
    evidence_valid = len(required_evidence) == 0 or bool(provided_evidence)
    auto_approve_conditions = criteria.get('auto_approve_conditions', [])
    auto_approved = any((condition.lower() in claim.justification.lower() for condition in auto_approve_conditions))
    is_valid = timing_valid and evidence_valid
    approved_bypasses = []
    if is_valid:
    if auto_approved:
    approved_bypasses = claim.requested_bypasses
    else:
    approved_bypasses = [bypass for bypass in claim.requested_bypasses if 'low_risk' in bypass or 'monitoring' in bypass]
    conditions = []
    expiry = None
    if is_valid:
    conditions.append('Emergency status verified')
    if not auto_approved:
    conditions.append('Requires ongoing monitoring')
    conditions.append('Subject to post-incident review')
    expiry = datetime.now() + max_duration
    else:
    conditions.append('Emergency claim rejected')
    if not timing_valid:
    conditions.append('Claim submitted outside acceptable timeframe')
    if not evidence_valid:
    conditions.append('Insufficient supporting evidence')
    validation_criteria = {'claim_type': claim.claim_type, 'timing_valid': timing_valid, 'evidence_valid': evidence_valid, 'auto_approved': auto_approved, 'claim_age_minutes': int(claim_age.total_seconds() / 60), 'max_duration_minutes': int(max_duration.total_seconds() / 60)}
    return EmergencyValidation(claim_id=claim.claim_id, is_valid=is_valid, validation_criteria=validation_criteria, approved_bypasses=approved_bypasses, conditions=conditions, expiry=expiry)

    def log_reality_check_failures(self, failure: RealityCheckFailure) -> AuditEntry:
    """
    Log reality check failures for audit and oversight.

    Creates immutable audit entries for all reality check failures
    to ensure accountability and enable pattern analysis.
    """
    self.logger.warning(f'Logging reality check failure {failure.failure_id}')
    audit_data = {'failure_id': failure.failure_id, 'decision_id': failure.decision_id, 'actor_id': failure.actor_id, 'failure_type': failure.failure_type, 'failure_reason': failure.failure_reason, 'impact_assessment': failure.impact_assessment, 'failure_timestamp': failure.timestamp.isoformat(), 'system_state': self._capture_system_state(), 'accountability_chain_status': 'unknown'}
    audit_content = str(sorted(audit_data.items()))
    immutable_hash = hashlib.sha256(audit_content.encode()).hexdigest()
    audit_entry = AuditEntry(event_type='reality_check_failure', actor_id=failure.actor_id, description=f'Reality check failure: {failure.failure_type} - {failure.failure_reason}', data=audit_data, immutable_hash=immutable_hash)
    self.logger.error(f'REALITY CHECK FAILURE: Actor {failure.actor_id} - {failure.failure_type} - {failure.failure_reason}')
    return audit_entry

    def _validate_impact_consistency(self, claimed_impact: str, actual_impact: str) -> bool:
    """Validate consistency between claimed and calculated impact levels."""
    impact_hierarchy = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
    claimed_level = impact_hierarchy.get(claimed_impact, 0)
    actual_level = impact_hierarchy.get(actual_impact, 0)
    return abs(claimed_level - actual_level) <= 1

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

