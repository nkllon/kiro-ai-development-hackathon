"""
Governance Bypass Detection System

Implements systematic detection of attempts to bypass established governance
processes, with escalation for persistent hubris patterns.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from ..models import (
    Decision, Actor, BypassAlert, EscalationAction, 
    GovernanceIntervention, InterventionType
)


@dataclass
class BypassPattern:
    """Detected bypass pattern with metadata."""
    pattern_type: str
    severity: str
    evidence: List[str]
    confidence: float
    first_detected: datetime
    last_detected: datetime


class GovernanceBypassDetector:
    """
    Detects systematic attempts to bypass governance processes.
    
    Monitors for patterns indicating actors believe they operate
    outside accountability chains.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Detection thresholds
        self.bypass_threshold = self.config.get('bypass_threshold', 3)
        self.escalation_timeout = timedelta(hours=self.config.get('escalation_hours', 48))
        self.pattern_memory = timedelta(days=self.config.get('pattern_memory_days', 7))
        
        # Pattern tracking
        self.detected_patterns = {}
        self.escalation_history = {}
        
        # Bypass indicators
        self.bypass_indicators = {
            'emergency_abuse': {
                'weight': 0.8,
                'description': 'Excessive emergency claims without validation'
            },
            'approval_skipping': {
                'weight': 0.9,
                'description': 'Skipping required approval processes'
            },
            'process_circumvention': {
                'weight': 0.7,
                'description': 'Using alternative paths to avoid governance'
            },
            'authority_escalation': {
                'weight': 0.85,
                'description': 'Self-granting elevated permissions'
            },
            'documentation_avoidance': {
                'weight': 0.6,
                'description': 'Avoiding required documentation processes'
            }
        }
    
    def detect_bypass_attempts(self, actor_id: str, recent_decisions: List[Decision], 
                             governance_events: List[Dict]) -> Optional[BypassAlert]:
        """
        Detect governance bypass attempts for an actor.
        
        Analyzes decision patterns and governance events to identify
        systematic attempts to operate outside accountability chains.
        """
        self.logger.info(f"Analyzing bypass patterns for actor {actor_id}")
        
        # Analyze different bypass patterns
        patterns = []
        
        # Pattern 1: Emergency abuse
        emergency_pattern = self._detect_emergency_abuse(actor_id, recent_decisions)
        if emergency_pattern:
            patterns.append(emergency_pattern)
        
        # Pattern 2: Approval skipping
        approval_pattern = self._detect_approval_skipping(actor_id, recent_decisions)
        if approval_pattern:
            patterns.append(approval_pattern)
        
        # Pattern 3: Process circumvention
        circumvention_pattern = self._detect_process_circumvention(actor_id, governance_events)
        if circumvention_pattern:
            patterns.append(circumvention_pattern)
        
        # Pattern 4: Authority escalation
        escalation_pattern = self._detect_authority_escalation(actor_id, recent_decisions)
        if escalation_pattern:
            patterns.append(escalation_pattern)
        
        if not patterns:
            return None
        
        # Calculate overall bypass severity
        bypass_severity = self._calculate_bypass_severity(patterns)
        
        # Check if threshold exceeded
        if len(patterns) >= self.bypass_threshold or bypass_severity > 0.7:
            return self._create_bypass_alert(actor_id, patterns, bypass_severity)
        
        # Store patterns for trend analysis
        self._store_patterns(actor_id, patterns)
        
        return None
    
    def check_escalation_needed(self, actor_id: str, pattern_duration: timedelta) -> Optional[EscalationAction]:
        """
        Check if escalation is needed for persistent bypass patterns.
        
        Implements automatic governance restoration when bypass attempts
        persist beyond acceptable thresholds.
        """
        if pattern_duration >= self.escalation_timeout:
            self.logger.warning(f"Escalating persistent bypass patterns for {actor_id}")
            
            return EscalationAction(
                actor_id=actor_id,
                escalation_type="governance_bypass_intervention",
                target_accountability_chain=self._get_accountability_chain(actor_id),
                action_description=f"Persistent governance bypass patterns detected for {pattern_duration}. Implementing systematic intervention.",
                timeline=timedelta(hours=4),
                success_criteria=[
                    "All bypass attempts cease",
                    "Governance compliance restored to >95%",
                    "Accountability verification implemented",
                    "Pattern monitoring continues for 30 days"
                ]
            )
        
        return None
    
    def create_governance_intervention(self, actor_id: str, bypass_alert: BypassAlert) -> GovernanceIntervention:
        """
        Create systematic governance intervention for bypass attempts.
        
        Implements graduated response based on bypass severity and
        actor's accountability chain status.
        """
        self.logger.critical(f"Creating governance intervention for {actor_id}")
        
        # Determine intervention type based on severity
        if bypass_alert.alert_level == "critical":
            intervention_type = InterventionType.EMERGENCY_GOVERNANCE
        elif bypass_alert.alert_level == "high":
            intervention_type = InterventionType.QUARANTINE
        else:
            intervention_type = InterventionType.ACCOUNTABILITY_VERIFICATION
        
        # Create intervention
        intervention = GovernanceIntervention(
            intervention_type=intervention_type,
            target_actor=actor_id,
            trigger_event=self._create_trigger_event(bypass_alert),
            escalation_path=self._create_escalation_path(actor_id, intervention_type),
            success_criteria=self._create_success_criteria(intervention_type),
            rollback_plan=self._create_rollback_plan(intervention_type)
        )
        
        return intervention
    
    def _detect_emergency_abuse(self, actor_id: str, decisions: List[Decision]) -> Optional[BypassPattern]:
        """Detect excessive emergency claims without proper validation."""
        emergency_decisions = [d for d in decisions if d.emergency_claimed]
        
        if len(emergency_decisions) > len(decisions) * 0.3:  # More than 30% emergency
            return BypassPattern(
                pattern_type="emergency_abuse",
                severity="high" if len(emergency_decisions) > len(decisions) * 0.5 else "medium",
                evidence=[
                    f"{len(emergency_decisions)} emergency claims out of {len(decisions)} decisions",
                    f"Emergency rate: {len(emergency_decisions)/len(decisions):.1%}",
                    "Pattern suggests systematic emergency abuse"
                ],
                confidence=min(1.0, len(emergency_decisions) / 5),
                first_detected=min(d.timestamp for d in emergency_decisions),
                last_detected=max(d.timestamp for d in emergency_decisions)
            )
        
        return None
    
    def _detect_approval_skipping(self, actor_id: str, decisions: List[Decision]) -> Optional[BypassPattern]:
        """Detect systematic skipping of required approvals."""
        high_impact_decisions = [
            d for d in decisions 
            if d.impact_level in ['high', 'critical'] and not d.accountability_verified
        ]
        
        if len(high_impact_decisions) >= 2:
            return BypassPattern(
                pattern_type="approval_skipping",
                severity="critical" if len(high_impact_decisions) >= 4 else "high",
                evidence=[
                    f"{len(high_impact_decisions)} high-impact decisions without approval",
                    "Systematic avoidance of accountability verification",
                    "Pattern indicates governance bypass intent"
                ],
                confidence=min(1.0, len(high_impact_decisions) / 3),
                first_detected=min(d.timestamp for d in high_impact_decisions),
                last_detected=max(d.timestamp for d in high_impact_decisions)
            )
        
        return None
    
    def _detect_process_circumvention(self, actor_id: str, governance_events: List[Dict]) -> Optional[BypassPattern]:
        """Detect attempts to circumvent established processes."""
        circumvention_events = [
            event for event in governance_events
            if event.get('event_type') in ['process_skip', 'alternative_path', 'unauthorized_access']
        ]
        
        if len(circumvention_events) >= 3:
            return BypassPattern(
                pattern_type="process_circumvention",
                severity="high",
                evidence=[
                    f"{len(circumvention_events)} process circumvention attempts",
                    "Multiple alternative paths used to avoid governance",
                    "Pattern suggests systematic process avoidance"
                ],
                confidence=0.8,
                first_detected=datetime.now() - timedelta(days=1),  # Simplified
                last_detected=datetime.now()
            )
        
        return None
    
    def _detect_authority_escalation(self, actor_id: str, decisions: List[Decision]) -> Optional[BypassPattern]:
        """Detect unauthorized authority escalation attempts."""
        escalation_decisions = [
            d for d in decisions
            if d.metadata.get('authority_escalation', False) or 
               d.metadata.get('self_authorized', False)
        ]
        
        if len(escalation_decisions) >= 2:
            return BypassPattern(
                pattern_type="authority_escalation",
                severity="critical",
                evidence=[
                    f"{len(escalation_decisions)} authority escalation attempts",
                    "Self-authorization of elevated permissions",
                    "Bypassing normal authority chains"
                ],
                confidence=0.9,
                first_detected=min(d.timestamp for d in escalation_decisions),
                last_detected=max(d.timestamp for d in escalation_decisions)
            )
        
        return None
    
    def _calculate_bypass_severity(self, patterns: List[BypassPattern]) -> float:
        """Calculate overall bypass severity from detected patterns."""
        if not patterns:
            return 0.0
        
        # Weight by pattern type and confidence
        weighted_severity = 0.0
        total_weight = 0.0
        
        for pattern in patterns:
            pattern_weight = self.bypass_indicators.get(pattern.pattern_type, {}).get('weight', 0.5)
            severity_score = {'low': 0.3, 'medium': 0.6, 'high': 0.8, 'critical': 1.0}.get(pattern.severity, 0.5)
            
            weighted_severity += severity_score * pattern_weight * pattern.confidence
            total_weight += pattern_weight
        
        return weighted_severity / total_weight if total_weight > 0 else 0.0
    
    def _create_bypass_alert(self, actor_id: str, patterns: List[BypassPattern], severity: float) -> BypassAlert:
        """Create bypass alert from detected patterns."""
        # Determine alert level
        if severity >= 0.8:
            alert_level = "critical"
        elif severity >= 0.6:
            alert_level = "high"
        elif severity >= 0.4:
            alert_level = "medium"
        else:
            alert_level = "low"
        
        # Calculate success rate (simplified)
        success_rate = min(0.8, severity)  # Higher severity = higher success rate
        
        return BypassAlert(
            actor_id=actor_id,
            bypass_type="systematic_governance_bypass",
            governance_process="accountability_verification",
            attempt_count=len(patterns),
            success_rate=success_rate,
            alert_level=alert_level
        )
    
    def _store_patterns(self, actor_id: str, patterns: List[BypassPattern]):
        """Store patterns for trend analysis."""
        if actor_id not in self.detected_patterns:
            self.detected_patterns[actor_id] = []
        
        self.detected_patterns[actor_id].extend(patterns)
        
        # Clean old patterns
        cutoff_time = datetime.now() - self.pattern_memory
        self.detected_patterns[actor_id] = [
            p for p in self.detected_patterns[actor_id]
            if p.last_detected >= cutoff_time
        ]
    
    def _get_accountability_chain(self, actor_id: str) -> List[str]:
        """Get accountability chain for actor (simplified)."""
        # In real implementation, would integrate with MamaDiscoverer
        return [f"manager_{actor_id}", f"director_{actor_id}", "governance_board"]
    
    def _create_trigger_event(self, bypass_alert: BypassAlert) -> Dict[str, Any]:
        """Create trigger event from bypass alert."""
        from ..models import TriggerEvent
        
        return TriggerEvent(
            event_type="governance_bypass_detected",
            actor_id=bypass_alert.actor_id,
            severity=bypass_alert.alert_level,
            description=f"Systematic governance bypass detected: {bypass_alert.bypass_type}",
            data={
                'attempt_count': bypass_alert.attempt_count,
                'success_rate': bypass_alert.success_rate,
                'bypass_type': bypass_alert.bypass_type
            }
        )
    
    def _create_escalation_path(self, actor_id: str, intervention_type: InterventionType) -> List[Dict]:
        """Create escalation path for intervention."""
        from ..models import EscalationStep
        
        base_path = [
            EscalationStep(
                step_order=1,
                responsible_party=f"immediate_supervisor_{actor_id}",
                action_required="Immediate accountability verification",
                timeline=timedelta(hours=2),
                success_criteria=["Bypass attempts cease", "Compliance restored"]
            )
        ]
        
        if intervention_type in [InterventionType.QUARANTINE, InterventionType.EMERGENCY_GOVERNANCE]:
            base_path.append(EscalationStep(
                step_order=2,
                responsible_party="governance_board",
                action_required="Emergency governance review",
                timeline=timedelta(hours=8),
                success_criteria=["Full governance restoration", "Systematic compliance"]
            ))
        
        return base_path
    
    def _create_success_criteria(self, intervention_type: InterventionType) -> List[Dict]:
        """Create success criteria for intervention."""
        from ..models import SuccessCriterion
        
        base_criteria = [
            SuccessCriterion(
                description="All bypass attempts cease",
                measurement_method="governance_event_monitoring",
                target_value=0,
                tolerance=0.0
            ),
            SuccessCriterion(
                description="Accountability verification rate restored",
                measurement_method="decision_compliance_rate",
                target_value=0.95,
                tolerance=0.05
            )
        ]
        
        if intervention_type == InterventionType.EMERGENCY_GOVERNANCE:
            base_criteria.append(SuccessCriterion(
                description="Emergency governance protocols successful",
                measurement_method="intervention_effectiveness",
                target_value=1.0,
                tolerance=0.0
            ))
        
        return base_criteria
    
    def _create_rollback_plan(self, intervention_type: InterventionType) -> Dict[str, Any]:
        """Create rollback plan for intervention."""
        from ..models import RollbackPlan
        
        if intervention_type == InterventionType.EMERGENCY_GOVERNANCE:
            timeline = timedelta(hours=2)
            trigger_conditions = ["Intervention proves ineffective", "Actor compliance restored"]
        else:
            timeline = timedelta(hours=8)
            trigger_conditions = ["Voluntary compliance restored", "Alternative resolution found"]
        
        return RollbackPlan(
            trigger_conditions=trigger_conditions,
            rollback_steps=[
                "Assess intervention effectiveness",
                "Verify compliance restoration", 
                "Gradually restore normal operations",
                "Maintain enhanced monitoring"
            ],
            responsible_parties=["governance_team", "system_administrator"],
            timeline=timeline
        )