"""
Hubris Detection Implementation

Implements automated detection of hubris patterns in actor decision-making,
following the systematic principle that "everyone has a mama."
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from ..interfaces import HubrisDetector
from ..models import (
    Decision, HubrisScore, VelocityAlert, BypassAlert, EscalationAction,
    HubrisFactor, RecommendedAction, TrendDirection, RiskLevel
)


@dataclass
class HubrisPattern:
    """Detected hubris pattern with scoring."""
    pattern_type: str
    confidence: float
    evidence: List[str]
    weight: float


class HubrisDetectorImpl(HubrisDetector):
    """
    Implementation of hubris detection using systematic pattern analysis.
    
    Detects when actors begin to believe they operate outside accountability
    chains and triggers appropriate interventions.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Hubris detection thresholds
        self.velocity_threshold = self.config.get('velocity_threshold', 10)  # decisions per hour
        self.accountability_gap_threshold = self.config.get('accountability_gap_threshold', 0.3)
        self.bypass_threshold = self.config.get('bypass_threshold', 3)  # attempts per day
        self.escalation_timeout = timedelta(hours=self.config.get('escalation_timeout_hours', 48))
        
        # Pattern weights for hubris scoring
        self.pattern_weights = {
            'velocity_without_accountability': 0.3,
            'governance_bypass_attempts': 0.4,
            'emergency_claim_abuse': 0.2,
            'self_authorization_escalation': 0.5,
            'accountability_chain_avoidance': 0.4,
            'exception_pattern_abuse': 0.3
        }
    
    def detect_patterns(self, actor_id: str, decision_history: List[Decision]) -> HubrisScore:
        """
        Analyze decision patterns for hubris indicators.
        
        Implements systematic pattern recognition to identify when actors
        begin operating outside accountability chains.
        """
        self.logger.info(f"Analyzing hubris patterns for actor {actor_id}")
        
        detected_patterns = []
        
        # Pattern 1: High velocity without accountability verification
        velocity_pattern = self._detect_velocity_pattern(decision_history)
        if velocity_pattern:
            detected_patterns.append(velocity_pattern)
        
        # Pattern 2: Governance bypass attempts
        bypass_pattern = self._detect_bypass_pattern(decision_history)
        if bypass_pattern:
            detected_patterns.append(bypass_pattern)
        
        # Pattern 3: Emergency claim abuse
        emergency_pattern = self._detect_emergency_abuse_pattern(decision_history)
        if emergency_pattern:
            detected_patterns.append(emergency_pattern)
        
        # Pattern 4: Self-authorization escalation
        self_auth_pattern = self._detect_self_authorization_pattern(decision_history)
        if self_auth_pattern:
            detected_patterns.append(self_auth_pattern)
        
        # Calculate overall hubris score
        hubris_score = self._calculate_hubris_score(detected_patterns)
        
        # Determine trend direction
        trend = self._analyze_trend(actor_id, decision_history)
        
        # Assess risk level
        risk_level = self._assess_risk_level(hubris_score, detected_patterns)
        
        # Generate recommended actions
        recommended_actions = self._generate_recommendations(detected_patterns, risk_level)
        
        # Convert patterns to hubris factors
        hubris_factors = [
            HubrisFactor(
                factor_type=pattern.pattern_type,
                description=f"Detected {pattern.pattern_type} with {pattern.confidence:.2f} confidence",
                weight=pattern.weight,
                evidence=pattern.evidence
            )
            for pattern in detected_patterns
        ]
        
        return HubrisScore(
            actor_id=actor_id,
            score=hubris_score,
            contributing_factors=hubris_factors,
            trend_direction=trend,
            risk_level=risk_level,
            recommended_actions=recommended_actions,
            calculated_at=datetime.now(),
            valid_until=datetime.now() + timedelta(hours=24)
        )
    
    def analyze_velocity(self, decisions: List[Decision], timeframe: timedelta) -> VelocityAlert:
        """
        Analyze decision velocity for accountability verification gaps.
        """
        if not decisions:
            return None
        
        # Filter decisions within timeframe
        cutoff_time = datetime.now() - timeframe
        recent_decisions = [d for d in decisions if d.timestamp >= cutoff_time]
        
        if not recent_decisions:
            return None
        
        # Calculate metrics
        decision_count = len(recent_decisions)
        verified_count = sum(1 for d in recent_decisions if d.accountability_verified)
        verification_rate = verified_count / decision_count if decision_count > 0 else 0
        
        # Check if velocity threshold exceeded
        decisions_per_hour = decision_count / (timeframe.total_seconds() / 3600)
        threshold_exceeded = (
            decisions_per_hour > self.velocity_threshold and 
            verification_rate < (1 - self.accountability_gap_threshold)
        )
        
        if threshold_exceeded:
            alert_level = "critical" if verification_rate < 0.2 else "high"
            
            return VelocityAlert(
                actor_id=recent_decisions[0].actor_id,
                decision_count=decision_count,
                timeframe=timeframe,
                accountability_verification_rate=verification_rate,
                threshold_exceeded=True,
                alert_level=alert_level
            )
        
        return None
    
    def check_bypass_attempts(self, actor_id: str, governance_events: List) -> BypassAlert:
        """
        Detect attempts to bypass established governance processes.
        """
        # Filter bypass-related events
        bypass_events = [
            event for event in governance_events 
            if hasattr(event, 'event_type') and 'bypass' in event.event_type.lower()
        ]
        
        if not bypass_events:
            return None
        
        # Analyze bypass patterns
        recent_bypasses = [
            event for event in bypass_events 
            if event.timestamp >= datetime.now() - timedelta(days=1)
        ]
        
        if len(recent_bypasses) >= self.bypass_threshold:
            # Calculate success rate
            successful_bypasses = [
                event for event in recent_bypasses 
                if hasattr(event, 'success') and event.success
            ]
            success_rate = len(successful_bypasses) / len(recent_bypasses)
            
            alert_level = "critical" if success_rate > 0.5 else "high"
            
            return BypassAlert(
                actor_id=actor_id,
                bypass_type="governance_process",
                governance_process="systematic_accountability",
                attempt_count=len(recent_bypasses),
                success_rate=success_rate,
                alert_level=alert_level
            )
        
        return None
    
    def escalate_persistent_patterns(self, actor_id: str, pattern_duration: timedelta) -> EscalationAction:
        """
        Escalate hubris patterns that persist beyond acceptable thresholds.
        """
        if pattern_duration >= self.escalation_timeout:
            return EscalationAction(
                actor_id=actor_id,
                escalation_type="automatic_governance_restoration",
                target_accountability_chain=["immediate_supervisor", "governance_board"],
                action_description=f"Persistent hubris patterns detected for {pattern_duration}. Implementing automatic governance restoration.",
                timeline=timedelta(hours=4),
                success_criteria=[
                    "Accountability verification rate > 90%",
                    "Governance bypass attempts < 1 per day",
                    "Emergency claims validated against objective criteria"
                ]
            )
        
        return None
    
    def _detect_velocity_pattern(self, decisions: List[Decision]) -> HubrisPattern:
        """Detect high decision velocity without accountability verification."""
        if len(decisions) < 5:
            return None
        
        # Analyze recent decisions (last 24 hours)
        recent_decisions = [
            d for d in decisions 
            if d.timestamp >= datetime.now() - timedelta(hours=24)
        ]
        
        if not recent_decisions:
            return None
        
        verification_rate = sum(1 for d in recent_decisions if d.accountability_verified) / len(recent_decisions)
        
        if len(recent_decisions) >= self.velocity_threshold and verification_rate < 0.5:
            confidence = min(1.0, (len(recent_decisions) / self.velocity_threshold) * (1 - verification_rate))
            
            return HubrisPattern(
                pattern_type="velocity_without_accountability",
                confidence=confidence,
                evidence=[
                    f"{len(recent_decisions)} decisions in 24 hours",
                    f"Only {verification_rate:.1%} accountability verified",
                    f"Threshold: {self.velocity_threshold} decisions"
                ],
                weight=self.pattern_weights['velocity_without_accountability']
            )
        
        return None
    
    def _detect_bypass_pattern(self, decisions: List[Decision]) -> HubrisPattern:
        """Detect governance bypass patterns."""
        bypass_indicators = [
            d for d in decisions 
            if d.emergency_claimed and not d.accountability_verified
        ]
        
        if len(bypass_indicators) >= 3:
            confidence = min(1.0, len(bypass_indicators) / 5)
            
            return HubrisPattern(
                pattern_type="governance_bypass_attempts",
                confidence=confidence,
                evidence=[
                    f"{len(bypass_indicators)} emergency claims without verification",
                    "Pattern suggests systematic bypass attempts"
                ],
                weight=self.pattern_weights['governance_bypass_attempts']
            )
        
        return None
    
    def _detect_emergency_abuse_pattern(self, decisions: List[Decision]) -> HubrisPattern:
        """Detect emergency claim abuse patterns."""
        emergency_decisions = [d for d in decisions if d.emergency_claimed]
        
        if len(emergency_decisions) > len(decisions) * 0.3:  # More than 30% emergency claims
            confidence = len(emergency_decisions) / len(decisions)
            
            return HubrisPattern(
                pattern_type="emergency_claim_abuse",
                confidence=confidence,
                evidence=[
                    f"{len(emergency_decisions)} emergency claims out of {len(decisions)} decisions",
                    f"Emergency rate: {confidence:.1%}"
                ],
                weight=self.pattern_weights['emergency_claim_abuse']
            )
        
        return None
    
    def _detect_self_authorization_pattern(self, decisions: List[Decision]) -> HubrisPattern:
        """Detect self-authorization escalation patterns."""
        high_impact_decisions = [
            d for d in decisions 
            if d.impact_level in ['high', 'critical'] and not d.accountability_verified
        ]
        
        if len(high_impact_decisions) >= 2:
            confidence = min(1.0, len(high_impact_decisions) / 3)
            
            return HubrisPattern(
                pattern_type="self_authorization_escalation",
                confidence=confidence,
                evidence=[
                    f"{len(high_impact_decisions)} high-impact decisions without accountability",
                    "Self-authorization of critical decisions"
                ],
                weight=self.pattern_weights['self_authorization_escalation']
            )
        
        return None
    
    def _calculate_hubris_score(self, patterns: List[HubrisPattern]) -> float:
        """Calculate overall hubris score from detected patterns."""
        if not patterns:
            return 0.0
        
        weighted_score = sum(pattern.confidence * pattern.weight for pattern in patterns)
        total_weight = sum(pattern.weight for pattern in patterns)
        
        return min(1.0, weighted_score / total_weight if total_weight > 0 else 0.0)
    
    def _analyze_trend(self, actor_id: str, decisions: List[Decision]) -> TrendDirection:
        """Analyze trend direction for hubris patterns."""
        if len(decisions) < 10:
            return TrendDirection.STABLE
        
        # Compare recent vs older decisions
        mid_point = len(decisions) // 2
        recent_decisions = decisions[mid_point:]
        older_decisions = decisions[:mid_point]
        
        recent_verification_rate = sum(1 for d in recent_decisions if d.accountability_verified) / len(recent_decisions)
        older_verification_rate = sum(1 for d in older_decisions if d.accountability_verified) / len(older_decisions)
        
        difference = recent_verification_rate - older_verification_rate
        
        if difference < -0.2:
            return TrendDirection.WORSENING
        elif difference < -0.1:
            return TrendDirection.CRITICAL if recent_verification_rate < 0.3 else TrendDirection.WORSENING
        elif difference > 0.1:
            return TrendDirection.IMPROVING
        else:
            return TrendDirection.STABLE
    
    def _assess_risk_level(self, hubris_score: float, patterns: List[HubrisPattern]) -> RiskLevel:
        """Assess risk level based on hubris score and patterns."""
        if hubris_score >= 0.8:
            return RiskLevel.CRITICAL
        elif hubris_score >= 0.6:
            return RiskLevel.HIGH
        elif hubris_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_recommendations(self, patterns: List[HubrisPattern], risk_level: RiskLevel) -> List[RecommendedAction]:
        """Generate recommended actions based on detected patterns."""
        recommendations = []
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append(RecommendedAction(
                action_type="immediate_accountability_verification",
                description="Require immediate accountability chain verification for all decisions",
                priority="critical",
                timeline=timedelta(hours=4),
                responsible_party="governance_system",
                success_criteria=["100% accountability verification", "Zero bypass attempts"]
            ))
        
        if any(p.pattern_type == "velocity_without_accountability" for p in patterns):
            recommendations.append(RecommendedAction(
                action_type="velocity_throttling",
                description="Implement decision velocity throttling with mandatory accountability checks",
                priority="high",
                timeline=timedelta(hours=8),
                responsible_party="system_administrator",
                success_criteria=["Decision rate < 5 per hour", "Accountability verification > 95%"]
            ))
        
        if any(p.pattern_type == "governance_bypass_attempts" for p in patterns):
            recommendations.append(RecommendedAction(
                action_type="bypass_prevention",
                description="Strengthen governance bypass prevention mechanisms",
                priority="critical",
                timeline=timedelta(hours=2),
                responsible_party="security_team",
                success_criteria=["Zero successful bypasses", "All attempts logged and escalated"]
            ))
        
        return recommendations