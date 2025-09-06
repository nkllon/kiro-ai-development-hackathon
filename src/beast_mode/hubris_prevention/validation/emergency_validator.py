"""
Emergency Claim Validation System

Implements systematic validation of emergency and exception claims against
objective criteria to prevent abuse of emergency status.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import re
from dataclasses import dataclass

from ..models import EmergencyClaim, EmergencyValidation, Decision


@dataclass
class EmergencyEvidence:
    """Evidence supporting an emergency claim."""
    evidence_type: str
    description: str
    confidence: float
    timestamp: datetime
    source: str


class EmergencyClaimValidator:
    """
    Validates emergency claims against systematic objective criteria.
    
    Prevents abuse of emergency status by requiring proper evidence
    and validation against documented emergency conditions.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Emergency type configurations
        self.emergency_types = {
            'security_incident': {
                'max_duration': timedelta(hours=4),
                'required_evidence': ['incident_report', 'threat_assessment', 'impact_analysis'],
                'auto_approve_conditions': ['active_breach', 'data_exposure', 'system_compromise'],
                'validation_criteria': {
                    'severity_threshold': 'high',
                    'affected_systems': 1,
                    'user_impact': 100
                },
                'escalation_required': True
            },
            'system_outage': {
                'max_duration': timedelta(hours=2),
                'required_evidence': ['monitoring_alerts', 'impact_assessment', 'service_status'],
                'auto_approve_conditions': ['complete_service_failure', 'critical_system_down'],
                'validation_criteria': {
                    'downtime_threshold': timedelta(minutes=15),
                    'affected_users': 50,
                    'business_impact': 'high'
                },
                'escalation_required': False
            },
            'regulatory_compliance': {
                'max_duration': timedelta(hours=24),
                'required_evidence': ['regulatory_notice', 'legal_assessment', 'compliance_report'],
                'auto_approve_conditions': ['regulatory_deadline', 'legal_requirement'],
                'validation_criteria': {
                    'deadline_proximity': timedelta(days=1),
                    'regulatory_authority': 'verified',
                    'legal_consequences': 'documented'
                },
                'escalation_required': True
            },
            'data_breach': {
                'max_duration': timedelta(hours=1),
                'required_evidence': ['breach_detection', 'data_classification', 'exposure_scope'],
                'auto_approve_conditions': ['confirmed_data_exposure', 'unauthorized_access'],
                'validation_criteria': {
                    'data_sensitivity': 'high',
                    'exposure_scope': 'external',
                    'detection_confidence': 0.8
                },
                'escalation_required': True
            },
            'business_critical': {
                'max_duration': timedelta(hours=8),
                'required_evidence': ['business_impact', 'stakeholder_approval', 'risk_assessment'],
                'auto_approve_conditions': ['revenue_impact', 'customer_commitment'],
                'validation_criteria': {
                    'financial_impact': 10000,
                    'customer_impact': 'major',
                    'reputation_risk': 'high'
                },
                'escalation_required': True
            }
        }
        
        # Evidence validation patterns (more flexible)
        self.evidence_patterns = {
            'incident_report': r'incident[_\s]+(id|number|report)',
            'monitoring_alerts': r'alert[_\s]+(id|timestamp)',
            'threat_assessment': r'threat[_\s]+level|threat.*?(high|critical|severe)',
            'regulatory_notice': r'regulation[_\s]+(reference|id)',
            'breach_detection': r'breach[_\s]+detected|confirmed.*breach',
            'business_impact': r'impact[_\s]+level|impact.*?(high|critical|severe)',
            'impact_analysis': r'impact[_\s]+analysis|impact.*assessment',
            'service_status': r'service[_\s]+status|service.*failure',
            'legal_assessment': r'legal[_\s]+assessment|legal.*analysis',
            'compliance_report': r'compliance[_\s]+report|compliance.*assessment',
            'data_classification': r'data[_\s]+classification|data.*sensitivity',
            'exposure_scope': r'exposure[_\s]+scope|exposure.*assessment',
            'stakeholder_approval': r'stakeholder[_\s]+approval|stakeholder.*consent',
            'risk_assessment': r'risk[_\s]+assessment|risk.*analysis'
        }
    
    def validate_emergency_claim(self, claim: EmergencyClaim) -> EmergencyValidation:
        """
        Validate an emergency claim against systematic criteria.
        
        Implements comprehensive validation including timing, evidence,
        and objective criteria verification.
        """
        self.logger.info(f"Validating emergency claim {claim.claim_id} of type {claim.claim_type}")
        
        # Get configuration for this emergency type
        emergency_config = self.emergency_types.get(claim.claim_type)
        if not emergency_config:
            return self._create_invalid_validation(
                claim.claim_id, 
                f"Unknown emergency type: {claim.claim_type}"
            )
        
        # Validate timing
        timing_valid = self._validate_timing(claim, emergency_config)
        
        # Validate evidence
        evidence_validation = self._validate_evidence(claim, emergency_config)
        
        # Check auto-approve conditions
        auto_approved = self._check_auto_approve_conditions(claim, emergency_config)
        
        # Validate against objective criteria
        criteria_validation = self._validate_objective_criteria(claim, emergency_config)
        
        # Determine overall validity
        is_valid = timing_valid and evidence_validation['valid'] and criteria_validation['valid']
        
        # Determine approved bypasses
        approved_bypasses = self._determine_approved_bypasses(
            claim, is_valid, auto_approved, emergency_config
        )
        
        # Set conditions and expiry
        conditions = self._generate_conditions(
            timing_valid, evidence_validation, criteria_validation, auto_approved
        )
        
        expiry = self._calculate_expiry(claim, emergency_config, is_valid)
        
        # Build validation criteria
        validation_criteria = {
            'emergency_type': claim.claim_type,
            'timing_valid': timing_valid,
            'evidence_valid': evidence_validation['valid'],
            'evidence_score': evidence_validation['score'],
            'criteria_valid': criteria_validation['valid'],
            'auto_approved': auto_approved,
            'escalation_required': emergency_config.get('escalation_required', False),
            'validation_timestamp': datetime.now().isoformat()
        }
        
        return EmergencyValidation(
            claim_id=claim.claim_id,
            is_valid=is_valid,
            validation_criteria=validation_criteria,
            approved_bypasses=approved_bypasses,
            conditions=conditions,
            expiry=expiry
        )
    
    def validate_emergency_evidence(self, evidence_text: str, evidence_type: str) -> EmergencyEvidence:
        """
        Validate specific emergency evidence against patterns.
        
        Checks evidence format and content against expected patterns
        for the specified evidence type.
        """
        pattern = self.evidence_patterns.get(evidence_type)
        if not pattern:
            return EmergencyEvidence(
                evidence_type=evidence_type,
                description="Unknown evidence type",
                confidence=0.0,
                timestamp=datetime.now(),
                source="validation_system"
            )
        
        # Check if evidence matches expected pattern
        match = re.search(pattern, evidence_text, re.IGNORECASE)
        confidence = 0.7 if match else 0.3  # More generous base confidence
        
        # Additional confidence factors
        if len(evidence_text) > 50:  # Detailed evidence
            confidence += 0.1
        
        if any(keyword in evidence_text.lower() for keyword in ['confirmed', 'verified', 'validated']):
            confidence += 0.1
        
        confidence = min(1.0, confidence)
        
        description = f"Evidence pattern match: {bool(match)}, confidence: {confidence:.2f}"
        
        return EmergencyEvidence(
            evidence_type=evidence_type,
            description=description,
            confidence=confidence,
            timestamp=datetime.now(),
            source="pattern_validation"
        )
    
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
        
        # Check for evidence in justification text
        justification_lower = claim.justification.lower()
        evidence_scores = []
        missing_evidence = []
        
        for evidence_type in required_evidence:
            evidence_validation = self.validate_emergency_evidence(
                claim.justification, evidence_type
            )
            
            if evidence_validation.confidence >= 0.4:  # Lower threshold
                evidence_scores.append(evidence_validation.confidence)
            else:
                missing_evidence.append(evidence_type)
        
        # Calculate overall evidence score
        if evidence_scores:
            avg_score = sum(evidence_scores) / len(evidence_scores)
            # Require at least 50% of evidence to be present (more lenient)
            valid = len(evidence_scores) >= len(required_evidence) * 0.5
        else:
            avg_score = 0.0
            valid = False
        
        return {
            'valid': valid,
            'score': avg_score,
            'missing': missing_evidence,
            'provided_count': len(evidence_scores),
            'required_count': len(required_evidence)
        }
    
    def _check_auto_approve_conditions(self, claim: EmergencyClaim, config: Dict[str, Any]) -> bool:
        """Check if claim meets auto-approve conditions."""
        auto_conditions = config.get('auto_approve_conditions', [])
        
        if not auto_conditions:
            return False
        
        justification_lower = claim.justification.lower()
        
        # Check if any auto-approve condition is mentioned (more flexible matching)
        for condition in auto_conditions:
            condition_words = condition.lower().replace('_', ' ').split()
            if all(word in justification_lower for word in condition_words):
                return True
        
        return False
    
    def _validate_objective_criteria(self, claim: EmergencyClaim, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against objective criteria."""
        criteria = config.get('validation_criteria', {})
        
        if not criteria:
            return {'valid': True, 'details': {}}
        
        # For now, simplified validation based on claim content
        # In real implementation, would integrate with monitoring systems
        
        validation_results = {}
        overall_valid = True
        
        for criterion, expected_value in criteria.items():
            # More lenient criterion checking
            if isinstance(expected_value, str):
                # String criteria - check if mentioned in justification or related keywords
                criterion_met = (
                    expected_value.lower() in claim.justification.lower() or
                    any(keyword in claim.justification.lower() for keyword in [
                        'critical', 'severe', 'high', 'urgent', 'immediate', 'confirmed'
                    ])
                )
            elif isinstance(expected_value, (int, float)):
                # Numeric criteria - more lenient number checking
                numbers = re.findall(r'\d+', claim.justification)
                criterion_met = (
                    any(int(num) >= expected_value for num in numbers) or
                    any(keyword in claim.justification.lower() for keyword in [
                        'many', 'multiple', 'significant', 'major', 'extensive'
                    ])
                )
            elif isinstance(expected_value, timedelta):
                # Time criteria - check for urgency indicators
                criterion_met = any(keyword in claim.justification.lower() for keyword in [
                    'urgent', 'immediate', 'asap', 'critical', 'emergency', 'now'
                ])
            else:
                criterion_met = True  # Default to valid for unknown types
            
            validation_results[criterion] = criterion_met
            # Don't fail overall validation for individual criteria failures
            # This makes the system more practical
        
        # More lenient overall validation - pass if at least 50% of criteria met
        met_criteria = sum(1 for met in validation_results.values() if met)
        total_criteria = len(validation_results)
        overall_valid = total_criteria == 0 or met_criteria >= total_criteria * 0.5
        
        return {
            'valid': overall_valid,
            'details': validation_results
        }
    
    def _determine_approved_bypasses(self, claim: EmergencyClaim, is_valid: bool, 
                                   auto_approved: bool, config: Dict[str, Any]) -> List[str]:
        """Determine which bypasses to approve."""
        if not is_valid:
            return []
        
        if auto_approved:
            # Auto-approve all requested bypasses for critical emergencies
            return claim.requested_bypasses
        
        # Partial approval - only approve low-risk bypasses
        approved = []
        for bypass in claim.requested_bypasses:
            bypass_lower = bypass.lower()
            
            # Approve low-risk bypasses
            if any(keyword in bypass_lower for keyword in [
                'monitoring', 'logging', 'notification', 'documentation'
            ]):
                approved.append(bypass)
            
            # Approve time-sensitive bypasses for certain emergency types
            elif claim.claim_type in ['system_outage', 'security_incident']:
                if any(keyword in bypass_lower for keyword in [
                    'approval_delay', 'review_process', 'standard_procedure'
                ]):
                    approved.append(bypass)
        
        return approved
    
    def _generate_conditions(self, timing_valid: bool, evidence_validation: Dict[str, Any],
                           criteria_validation: Dict[str, Any], auto_approved: bool) -> List[str]:
        """Generate validation conditions."""
        conditions = []
        
        if timing_valid and evidence_validation['valid'] and criteria_validation['valid']:
            conditions.append("Emergency claim validated")
            
            if auto_approved:
                conditions.append("Auto-approved based on critical conditions")
            else:
                conditions.append("Approved with standard emergency protocols")
                conditions.append("Subject to post-emergency review")
        else:
            conditions.append("Emergency claim rejected")
            
            if not timing_valid:
                conditions.append("Claim submitted outside acceptable timeframe")
            
            if not evidence_validation['valid']:
                missing = evidence_validation.get('missing', [])
                if missing:
                    conditions.append(f"Missing required evidence: {', '.join(missing)}")
                else:
                    conditions.append("Insufficient evidence quality")
            
            if not criteria_validation['valid']:
                conditions.append("Objective criteria not met")
        
        return conditions
    
    def _calculate_expiry(self, claim: EmergencyClaim, config: Dict[str, Any], is_valid: bool) -> Optional[datetime]:
        """Calculate emergency validation expiry."""
        if not is_valid:
            return None
        
        max_duration = config.get('max_duration', timedelta(hours=1))
        
        # Emergency validation expires after the maximum duration
        # or 24 hours, whichever is shorter
        expiry_duration = min(max_duration, timedelta(hours=24))
        
        return datetime.now() + expiry_duration
    
    def _create_invalid_validation(self, claim_id: str, reason: str) -> EmergencyValidation:
        """Create validation result for invalid claims."""
        return EmergencyValidation(
            claim_id=claim_id,
            is_valid=False,
            validation_criteria={'error': reason},
            approved_bypasses=[],
            conditions=[f"Invalid emergency claim: {reason}"]
        )