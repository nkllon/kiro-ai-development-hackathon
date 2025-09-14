"""
Emergency Validator Validation

This module was extracted from emergency_validator.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import re
from dataclasses import dataclass
from ..models import EmergencyClaim, EmergencyValidation, Decision
from src.rm_ddd.core.health import ModuleHealth


class ValidateemergencyclaimClass:
    """Auto-generated class for functions."""

    def validate_emergency_claim(self, claim: EmergencyClaim) -> EmergencyValidation:
    """
    Validate an emergency claim against systematic criteria.

    Implements comprehensive validation including timing, evidence,
    and objective criteria verification.
    """
    self.logger.info(f'Validating emergency claim {claim.claim_id} of type {claim.claim_type}')
    emergency_config = self.emergency_types.get(claim.claim_type)
    if not emergency_config:
    return self._create_invalid_validation(claim.claim_id, f'Unknown emergency type: {claim.claim_type}')
    timing_valid = self._validate_timing(claim, emergency_config)
    evidence_validation = self._validate_evidence(claim, emergency_config)
    auto_approved = self._check_auto_approve_conditions(claim, emergency_config)
    criteria_validation = self._validate_objective_criteria(claim, emergency_config)
    is_valid = timing_valid and evidence_validation['valid'] and criteria_validation['valid']
    approved_bypasses = self._determine_approved_bypasses(claim, is_valid, auto_approved, emergency_config)
    conditions = self._generate_conditions(timing_valid, evidence_validation, criteria_validation, auto_approved)
    expiry = self._calculate_expiry(claim, emergency_config, is_valid)
    validation_criteria = {'emergency_type': claim.claim_type, 'timing_valid': timing_valid, 'evidence_valid': evidence_validation['valid'], 'evidence_score': evidence_validation['score'], 'criteria_valid': criteria_validation['valid'], 'auto_approved': auto_approved, 'escalation_required': emergency_config.get('escalation_required', False), 'validation_timestamp': datetime.now().isoformat()}
    return EmergencyValidation(claim_id=claim.claim_id, is_valid=is_valid, validation_criteria=validation_criteria, approved_bypasses=approved_bypasses, conditions=conditions, expiry=expiry)

    def validate_emergency_evidence(self, evidence_text: str, evidence_type: str) -> EmergencyEvidence:
    """
    Validate specific emergency evidence against patterns.

    Checks evidence format and content against expected patterns
    for the specified evidence type.
    """
    pattern = self.evidence_patterns.get(evidence_type)
    if not pattern:
    return EmergencyEvidence(evidence_type=evidence_type, description='Unknown evidence type', confidence=0.0, timestamp=datetime.now(), source='validation_system')
    match = re.search(pattern, evidence_text, re.IGNORECASE)
    confidence = 0.7 if match else 0.3
    if len(evidence_text) > 50:
    confidence += 0.1
    if any((keyword in evidence_text.lower() for keyword in ['confirmed', 'verified', 'validated'])):
    confidence += 0.1
    confidence = min(1.0, confidence)
    description = f'Evidence pattern match: {bool(match)}, confidence: {confidence:.2f}'
    return EmergencyEvidence(evidence_type=evidence_type, description=description, confidence=confidence, timestamp=datetime.now(), source='pattern_validation')

    def _validate_timing(self, claim: EmergencyClaim, config: Dict[str, Any]) -> bool:
    """Validate emergency claim timing."""
    max_duration = config.get('max_duration', timedelta(hours=1))
    claim_age = datetime.now() - claim.timestamp
    return claim_age <= max_duration

    def _validate_evidence(self, claim: EmergencyClaim, config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate emergency evidence."""
    required_evidence = config.get('required_evidence', [])
    if not required_evidence:
    return {'valid': True, 'score': 1.0, 'missing': []}
    justification_lower = claim.justification.lower()
    evidence_scores = []
    missing_evidence = []
    for evidence_type in required_evidence:
    evidence_validation = self.validate_emergency_evidence(claim.justification, evidence_type)
    if evidence_validation.confidence >= 0.4:
    evidence_scores.append(evidence_validation.confidence)
    else:
    missing_evidence.append(evidence_type)
    if evidence_scores:
    avg_score = sum(evidence_scores) / len(evidence_scores)
    valid = len(evidence_scores) >= len(required_evidence) * 0.5
    else:
    avg_score = 0.0
    valid = False
    return {'valid': valid, 'score': avg_score, 'missing': missing_evidence, 'provided_count': len(evidence_scores), 'required_count': len(required_evidence)}

    def _check_auto_approve_conditions(self, claim: EmergencyClaim, config: Dict[str, Any]) -> bool:
    """Check if claim meets auto-approve conditions."""
    auto_conditions = config.get('auto_approve_conditions', [])
    if not auto_conditions:
    return False
    justification_lower = claim.justification.lower()
    for condition in auto_conditions:
    condition_words = condition.lower().replace('_', ' ').split()
    if all((word in justification_lower for word in condition_words)):
    return True
    return False

    def _validate_objective_criteria(self, claim: EmergencyClaim, config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate against objective criteria."""
    criteria = config.get('validation_criteria', {})
    if not criteria:
    return {'valid': True, 'details': {}}
    validation_results = {}
    overall_valid = True
    for criterion, expected_value in criteria.items():
    if isinstance(expected_value, str):
    criterion_met = expected_value.lower() in claim.justification.lower() or any((keyword in claim.justification.lower() for keyword in ['critical', 'severe', 'high', 'urgent', 'immediate', 'confirmed']))
    elif isinstance(expected_value, (int, float)):
    numbers = re.findall('\\d+', claim.justification)
    criterion_met = any((int(num) >= expected_value for num in numbers)) or any((keyword in claim.justification.lower() for keyword in ['many', 'multiple', 'significant', 'major', 'extensive']))
    elif isinstance(expected_value, timedelta):
    criterion_met = any((keyword in claim.justification.lower() for keyword in ['urgent', 'immediate', 'asap', 'critical', 'emergency', 'now']))
    else:
    criterion_met = True
    validation_results[criterion] = criterion_met
    met_criteria = sum((1 for met in validation_results.values() if met))
    total_criteria = len(validation_results)
    overall_valid = total_criteria == 0 or met_criteria >= total_criteria * 0.5
    return {'valid': overall_valid, 'details': validation_results}

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

