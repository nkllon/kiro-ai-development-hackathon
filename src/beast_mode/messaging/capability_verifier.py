"""
Beast Mode Agent Capability Verification System

Implements capability validation through interaction testing, trust scoring,
and reputation tracking for agent collaboration.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .models import BeastModeMessage, MessageType, AgentCapabilities
from .agent_registry import AgentRegistry, DiscoveredAgent
from .help_system import HelpWantedSystem, CollaborationSession, CollaborationStatus


logger = logging.getLogger(__name__)


class VerificationStatus(str, Enum):
    """Status of capability verification tests"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    EXPIRED = "expired"


class TrustLevel(str, Enum):
    """Trust levels for agent reputation"""
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXPERT = "expert"


@dataclass
class CapabilityTest:
    """Information about a capability verification test"""
    test_id: str
    agent_id: str
    capability: str
    test_type: str  # "interaction", "collaboration", "performance"
    test_description: str
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: VerificationStatus = VerificationStatus.PENDING
    
    # Test parameters
    timeout_minutes: int = 30
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Results
    result_data: Dict[str, Any] = field(default_factory=dict)
    success_score: float = 0.0  # 0.0 to 1.0
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)


@dataclass
class TrustScore:
    """Trust scoring information for an agent's capability"""
    agent_id: str
    capability: str
    
    # Core metrics
    total_interactions: int = 0
    successful_interactions: int = 0
    failed_interactions: int = 0
    
    # Verification results
    verification_tests_passed: int = 0
    verification_tests_failed: int = 0
    last_verification: Optional[datetime] = None
    
    # Performance metrics
    average_response_time: float = 0.0
    average_success_rate: float = 0.0
    consistency_score: float = 0.0  # How consistent the agent's performance is
    
    # Reputation
    trust_level: TrustLevel = TrustLevel.UNKNOWN
    trust_score: float = 0.0  # 0.0 to 1.0
    reputation_points: int = 0
    
    # Metadata
    first_interaction: Optional[datetime] = None
    last_interaction: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CapabilityRecommendation:
    """Recommendation for capability matching"""
    agent_id: str
    capability: str
    confidence: float  # 0.0 to 1.0
    trust_score: float
    recommendation_reason: str
    estimated_success_rate: float
    estimated_response_time: float
    risk_factors: List[str] = field(default_factory=list)
    supporting_evidence: Dict[str, Any] = field(default_factory=dict)


class CapabilityVerifier:
    """Core capability verification and trust scoring system"""
    
    def __init__(self, agent_registry: AgentRegistry, help_system: HelpWantedSystem):
        self.agent_registry = agent_registry
        self.help_system = help_system
        
        # Verification data
        self.capability_tests: Dict[str, CapabilityTest] = {}
        self.trust_scores: Dict[Tuple[str, str], TrustScore] = {}  # (agent_id, capability) -> TrustScore
        
        # Configuration
        self.verification_timeout = timedelta(minutes=30)
        self.trust_decay_rate = 0.95  # Daily decay for inactive agents
        self.min_interactions_for_trust = 3
        self.expert_threshold = 0.9
        self.high_trust_threshold = 0.7
        self.medium_trust_threshold = 0.4
        
        # Statistics
        self.stats = {
            'tests_created': 0,
            'tests_completed': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'trust_scores_updated': 0,
            'recommendations_generated': 0,
            'average_verification_time': 0.0
        }
    
    def create_capability_test(
        self,
        agent_id: str,
        capability: str,
        test_type: str = "interaction",
        test_description: str = "",
        timeout_minutes: int = 30,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> CapabilityTest:
        """
        Create a new capability verification test.
        
        Args:
            agent_id: Agent to test
            capability: Capability to verify
            test_type: Type of test (interaction, collaboration, performance)
            test_description: Description of what the test validates
            timeout_minutes: Test timeout in minutes
            success_criteria: Criteria for test success
            
        Returns:
            CapabilityTest: The created test
        """
        test_id = str(uuid.uuid4())
        
        test = CapabilityTest(
            test_id=test_id,
            agent_id=agent_id,
            capability=capability,
            test_type=test_type,
            test_description=test_description or f"Verify {capability} capability for {agent_id}",
            timeout_minutes=timeout_minutes,
            success_criteria=success_criteria or {}
        )
        
        self.capability_tests[test_id] = test
        self.stats['tests_created'] += 1
        
        logger.info(f"Created capability test {test_id} for {agent_id}:{capability}")
        
        return test
    
    def start_capability_test(self, test_id: str) -> bool:
        """
        Start a capability verification test.
        
        Args:
            test_id: ID of the test to start
            
        Returns:
            bool: True if test was started successfully
        """
        if test_id not in self.capability_tests:
            return False
        
        test = self.capability_tests[test_id]
        
        if test.status != VerificationStatus.PENDING:
            logger.warning(f"Cannot start test {test_id} in status {test.status}")
            return False
        
        test.status = VerificationStatus.IN_PROGRESS
        test.started_at = datetime.now()
        
        logger.info(f"Started capability test {test_id} for {test.agent_id}:{test.capability}")
        
        return True
    
    def complete_capability_test(
        self,
        test_id: str,
        success: bool,
        result_data: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, float]] = None,
        error_messages: Optional[List[str]] = None
    ) -> bool:
        """
        Complete a capability verification test.
        
        Args:
            test_id: ID of the test to complete
            success: Whether the test passed
            result_data: Test result data
            performance_metrics: Performance measurements
            error_messages: Any error messages from the test
            
        Returns:
            bool: True if test was completed successfully
        """
        if test_id not in self.capability_tests:
            return False
        
        test = self.capability_tests[test_id]
        
        if test.status != VerificationStatus.IN_PROGRESS:
            logger.warning(f"Cannot complete test {test_id} in status {test.status}")
            return False
        
        test.status = VerificationStatus.PASSED if success else VerificationStatus.FAILED
        test.completed_at = datetime.now()
        test.result_data = result_data or {}
        test.performance_metrics = performance_metrics or {}
        test.error_messages = error_messages or []
        
        # Calculate success score based on results
        if success:
            test.success_score = 1.0
            # Adjust based on performance metrics if available
            if performance_metrics:
                response_time = performance_metrics.get('response_time', 0)
                if response_time > 0:
                    # Penalize slow responses (assuming 5 seconds is ideal)
                    time_penalty = max(0, min(0.3, (response_time - 5.0) / 20.0))
                    test.success_score = max(0.7, 1.0 - time_penalty)
        else:
            test.success_score = 0.0
        
        # Update trust scores
        self._update_trust_score_from_test(test)
        
        # Update statistics
        self.stats['tests_completed'] += 1
        if success:
            self.stats['tests_passed'] += 1
        else:
            self.stats['tests_failed'] += 1
        
        # Update average verification time
        if test.started_at:
            duration = (test.completed_at - test.started_at).total_seconds()
            current_avg = self.stats['average_verification_time']
            total_tests = self.stats['tests_completed']
            self.stats['average_verification_time'] = (
                (current_avg * (total_tests - 1) + duration) / total_tests
            )
        
        logger.info(f"Completed capability test {test_id} (success: {success}, score: {test.success_score:.2f})")
        
        return True
    
    def record_interaction_result(
        self,
        agent_id: str,
        capability: str,
        success: bool,
        response_time: Optional[float] = None,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record the result of a capability interaction for trust scoring.
        
        Args:
            agent_id: Agent that performed the interaction
            capability: Capability that was used
            success: Whether the interaction was successful
            response_time: Time taken for the interaction (seconds)
            interaction_data: Additional interaction metadata
        """
        trust_key = (agent_id, capability)
        
        # Get or create trust score
        if trust_key not in self.trust_scores:
            self.trust_scores[trust_key] = TrustScore(
                agent_id=agent_id,
                capability=capability,
                first_interaction=datetime.now()
            )
        
        trust_score = self.trust_scores[trust_key]
        
        # Update interaction counts
        trust_score.total_interactions += 1
        if success:
            trust_score.successful_interactions += 1
        else:
            trust_score.failed_interactions += 1
        
        # Update response time
        if response_time is not None:
            if trust_score.average_response_time == 0.0:
                trust_score.average_response_time = response_time
            else:
                # Exponential moving average
                alpha = 0.3
                trust_score.average_response_time = (
                    alpha * response_time + (1 - alpha) * trust_score.average_response_time
                )
        
        # Update success rate
        trust_score.average_success_rate = (
            trust_score.successful_interactions / trust_score.total_interactions
        )
        
        # Update consistency score (how consistent the success rate is)
        if trust_score.total_interactions >= 5:
            # Calculate variance in recent results (simplified)
            recent_success_rate = trust_score.average_success_rate
            consistency_factor = min(1.0, trust_score.total_interactions / 20.0)
            trust_score.consistency_score = recent_success_rate * consistency_factor
        
        # Update timestamps
        trust_score.last_interaction = datetime.now()
        trust_score.updated_at = datetime.now()
        
        # Recalculate trust level and score
        self._calculate_trust_level(trust_score)
        
        self.stats['trust_scores_updated'] += 1
        
        logger.debug(f"Recorded interaction for {agent_id}:{capability} (success: {success})")
    
    def record_collaboration_result(self, collaboration_session: CollaborationSession) -> None:
        """
        Record collaboration results for trust scoring.
        
        Args:
            collaboration_session: Completed collaboration session
        """
        success = collaboration_session.status == CollaborationStatus.COMPLETED
        
        # Calculate response time from session duration
        if collaboration_session.started_at:
            response_time = (datetime.now() - collaboration_session.started_at).total_seconds()
        else:
            response_time = None
        
        # Record interaction for each capability used
        for capability in collaboration_session.capabilities_used:
            self.record_interaction_result(
                collaboration_session.helper_id,
                capability,
                success,
                response_time,
                {
                    'collaboration_session_id': collaboration_session.session_id,
                    'messages_exchanged': collaboration_session.messages_exchanged,
                    'success_metrics': collaboration_session.success_metrics
                }
            )
    
    def get_capability_recommendations(
        self,
        required_capabilities: List[str],
        min_trust_score: float = 0.3,
        max_recommendations: int = 5
    ) -> List[CapabilityRecommendation]:
        """
        Get capability recommendations for help requests.
        
        Args:
            required_capabilities: List of required capabilities
            min_trust_score: Minimum trust score to include
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List[CapabilityRecommendation]: Sorted recommendations
        """
        recommendations = []
        
        # Get all agents with matching capabilities
        matching_agents = self.help_system.find_matching_agents(required_capabilities)
        
        for agent, match_score in matching_agents:
            agent_recommendations = []
            
            # Generate recommendations for each matching capability
            for capability in required_capabilities:
                if capability in agent.capabilities.capabilities:
                    trust_key = (agent.agent_id, capability)
                    trust_score = self.trust_scores.get(trust_key)
                    
                    if trust_score and trust_score.trust_score >= min_trust_score:
                        recommendation = self._create_capability_recommendation(
                            agent, capability, trust_score, match_score
                        )
                        agent_recommendations.append(recommendation)
            
            recommendations.extend(agent_recommendations)
        
        # Sort by confidence and trust score
        recommendations.sort(
            key=lambda r: (r.confidence, r.trust_score, r.estimated_success_rate),
            reverse=True
        )
        
        # Limit results
        recommendations = recommendations[:max_recommendations]
        
        self.stats['recommendations_generated'] += len(recommendations)
        
        return recommendations
    
    def get_agent_reputation(self, agent_id: str) -> Dict[str, Any]:
        """
        Get comprehensive reputation information for an agent.
        
        Args:
            agent_id: Agent to get reputation for
            
        Returns:
            Dict: Reputation information
        """
        agent_trust_scores = {
            capability: trust_score
            for (aid, capability), trust_score in self.trust_scores.items()
            if aid == agent_id
        }
        
        if not agent_trust_scores:
            return {
                'agent_id': agent_id,
                'overall_trust_level': TrustLevel.UNKNOWN,
                'overall_trust_score': 0.0,
                'total_interactions': 0,
                'capabilities': {},
                'reputation_summary': 'No interaction history available'
            }
        
        # Calculate overall metrics
        total_interactions = sum(ts.total_interactions for ts in agent_trust_scores.values())
        total_successful = sum(ts.successful_interactions for ts in agent_trust_scores.values())
        overall_success_rate = total_successful / total_interactions if total_interactions > 0 else 0.0
        
        # Calculate weighted trust score
        weighted_trust_score = 0.0
        total_weight = 0.0
        
        for trust_score in agent_trust_scores.values():
            weight = trust_score.total_interactions
            weighted_trust_score += trust_score.trust_score * weight
            total_weight += weight
        
        if total_weight > 0:
            overall_trust_score = weighted_trust_score / total_weight
        else:
            overall_trust_score = 0.0
        
        # Determine overall trust level
        if overall_trust_score >= self.expert_threshold:
            overall_trust_level = TrustLevel.EXPERT
        elif overall_trust_score >= self.high_trust_threshold:
            overall_trust_level = TrustLevel.HIGH
        elif overall_trust_score >= self.medium_trust_threshold:
            overall_trust_level = TrustLevel.MEDIUM
        elif total_interactions >= self.min_interactions_for_trust:
            overall_trust_level = TrustLevel.LOW
        else:
            overall_trust_level = TrustLevel.UNKNOWN
        
        # Create reputation summary
        reputation_summary = self._generate_reputation_summary(
            overall_trust_level, overall_success_rate, total_interactions, len(agent_trust_scores)
        )
        
        return {
            'agent_id': agent_id,
            'overall_trust_level': overall_trust_level,
            'overall_trust_score': overall_trust_score,
            'overall_success_rate': overall_success_rate,
            'total_interactions': total_interactions,
            'capabilities': {
                capability: {
                    'trust_level': ts.trust_level,
                    'trust_score': ts.trust_score,
                    'success_rate': ts.average_success_rate,
                    'total_interactions': ts.total_interactions,
                    'average_response_time': ts.average_response_time,
                    'consistency_score': ts.consistency_score,
                    'last_interaction': ts.last_interaction.isoformat() if ts.last_interaction else None
                }
                for capability, ts in agent_trust_scores.items()
            },
            'reputation_summary': reputation_summary
        }
    
    def cleanup_expired_tests(self) -> int:
        """
        Clean up expired capability tests.
        
        Returns:
            int: Number of tests cleaned up
        """
        now = datetime.now()
        expired_tests = []
        
        for test_id, test in self.capability_tests.items():
            if (test.status == VerificationStatus.IN_PROGRESS and 
                test.started_at and 
                now - test.started_at > timedelta(minutes=test.timeout_minutes)):
                expired_tests.append(test_id)
        
        # Mark tests as expired
        for test_id in expired_tests:
            test = self.capability_tests[test_id]
            test.status = VerificationStatus.EXPIRED
            test.completed_at = now
            test.error_messages.append("Test expired due to timeout")
            
            logger.info(f"Marked capability test {test_id} as expired")
        
        return len(expired_tests)
    
    def _update_trust_score_from_test(self, test: CapabilityTest) -> None:
        """Update trust score based on verification test results"""
        trust_key = (test.agent_id, test.capability)
        
        # Get or create trust score
        if trust_key not in self.trust_scores:
            self.trust_scores[trust_key] = TrustScore(
                agent_id=test.agent_id,
                capability=test.capability
            )
        
        trust_score = self.trust_scores[trust_key]
        
        # Update verification counts
        if test.status == VerificationStatus.PASSED:
            trust_score.verification_tests_passed += 1
        elif test.status == VerificationStatus.FAILED:
            trust_score.verification_tests_failed += 1
        
        trust_score.last_verification = test.completed_at
        
        # Recalculate trust level
        self._calculate_trust_level(trust_score)
    
    def _calculate_trust_level(self, trust_score: TrustScore) -> None:
        """Calculate and update trust level and score"""
        # Base score from success rate
        base_score = trust_score.average_success_rate
        
        # Verification bonus (up to 0.2)
        verification_bonus = 0.0
        total_verifications = trust_score.verification_tests_passed + trust_score.verification_tests_failed
        if total_verifications > 0:
            verification_success_rate = trust_score.verification_tests_passed / total_verifications
            verification_bonus = min(0.2, verification_success_rate * 0.2)
        
        # Consistency bonus (up to 0.1)
        consistency_bonus = min(0.1, trust_score.consistency_score * 0.1)
        
        # Experience bonus based on interaction count (up to 0.1)
        experience_bonus = min(0.1, trust_score.total_interactions / 100.0 * 0.1)
        
        # Calculate final trust score
        trust_score.trust_score = min(1.0, base_score + verification_bonus + consistency_bonus + experience_bonus)
        
        # Determine trust level
        if trust_score.total_interactions < self.min_interactions_for_trust:
            trust_score.trust_level = TrustLevel.UNKNOWN
        elif trust_score.trust_score >= self.expert_threshold:
            trust_score.trust_level = TrustLevel.EXPERT
        elif trust_score.trust_score >= self.high_trust_threshold:
            trust_score.trust_level = TrustLevel.HIGH
        elif trust_score.trust_score >= self.medium_trust_threshold:
            trust_score.trust_level = TrustLevel.MEDIUM
        else:
            trust_score.trust_level = TrustLevel.LOW
        
        # Update reputation points (simplified system)
        trust_score.reputation_points = int(
            trust_score.trust_score * 100 + 
            trust_score.total_interactions * 2 + 
            trust_score.verification_tests_passed * 10
        )
    
    def _create_capability_recommendation(
        self,
        agent: DiscoveredAgent,
        capability: str,
        trust_score: TrustScore,
        match_score: float
    ) -> CapabilityRecommendation:
        """Create a capability recommendation"""
        # Calculate confidence based on trust score and match score
        confidence = (trust_score.trust_score * 0.7 + match_score * 0.3)
        
        # Generate recommendation reason
        reason_parts = []
        if trust_score.trust_level == TrustLevel.EXPERT:
            reason_parts.append("Expert-level capability")
        elif trust_score.trust_level == TrustLevel.HIGH:
            reason_parts.append("High trust level")
        
        if trust_score.average_success_rate > 0.8:
            reason_parts.append(f"{trust_score.average_success_rate:.0%} success rate")
        
        if trust_score.total_interactions >= 10:
            reason_parts.append(f"{trust_score.total_interactions} interactions")
        
        recommendation_reason = "; ".join(reason_parts) if reason_parts else "Limited interaction history"
        
        # Identify risk factors
        risk_factors = []
        if trust_score.average_success_rate < 0.7:
            risk_factors.append("Below average success rate")
        if trust_score.total_interactions < 5:
            risk_factors.append("Limited interaction history")
        if trust_score.average_response_time > 30.0:
            risk_factors.append("Slow response time")
        
        return CapabilityRecommendation(
            agent_id=agent.agent_id,
            capability=capability,
            confidence=confidence,
            trust_score=trust_score.trust_score,
            recommendation_reason=recommendation_reason,
            estimated_success_rate=trust_score.average_success_rate,
            estimated_response_time=trust_score.average_response_time,
            risk_factors=risk_factors,
            supporting_evidence={
                'total_interactions': trust_score.total_interactions,
                'verification_tests_passed': trust_score.verification_tests_passed,
                'consistency_score': trust_score.consistency_score,
                'last_interaction': trust_score.last_interaction.isoformat() if trust_score.last_interaction else None
            }
        )
    
    def _generate_reputation_summary(
        self,
        trust_level: TrustLevel,
        success_rate: float,
        total_interactions: int,
        capability_count: int
    ) -> str:
        """Generate a human-readable reputation summary"""
        if trust_level == TrustLevel.UNKNOWN:
            return "New agent with no interaction history"
        
        level_descriptions = {
            TrustLevel.EXPERT: "Highly experienced and reliable",
            TrustLevel.HIGH: "Trusted and dependable",
            TrustLevel.MEDIUM: "Moderately reliable",
            TrustLevel.LOW: "Limited reliability"
        }
        
        base_description = level_descriptions[trust_level]
        
        details = []
        if success_rate >= 0.9:
            details.append("excellent track record")
        elif success_rate >= 0.7:
            details.append("good track record")
        else:
            details.append("mixed track record")
        
        if total_interactions >= 50:
            details.append("extensive experience")
        elif total_interactions >= 20:
            details.append("solid experience")
        elif total_interactions >= 10:
            details.append("moderate experience")
        else:
            details.append("limited experience")
        
        if capability_count > 5:
            details.append("versatile capabilities")
        elif capability_count > 2:
            details.append("multiple capabilities")
        
        return f"{base_description} with {', '.join(details)}"
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get capability verification system statistics"""
        return {
            **self.stats,
            'active_tests': len([t for t in self.capability_tests.values() if t.status == VerificationStatus.IN_PROGRESS]),
            'total_trust_scores': len(self.trust_scores),
            'trust_level_distribution': {
                level.value: len([ts for ts in self.trust_scores.values() if ts.trust_level == level])
                for level in TrustLevel
            }
        }