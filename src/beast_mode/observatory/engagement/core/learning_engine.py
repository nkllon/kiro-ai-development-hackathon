"""
Learning Engine - Continuous Improvement and User Behavior Analysis
===================================================================

The Learning Engine provides user behavior analysis, engagement optimization,
and A/B testing framework for continuous system improvement.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .interfaces import (
    IUserBehaviorAnalyzer, 
    IEngagementOptimizer,
    EngagementContext,
    EngagementLevel
)

logger = logging.getLogger(__name__)


class LearningStrategy(Enum):
    """Learning strategy types."""
    REINFORCEMENT = "reinforcement"
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    A_B_TESTING = "ab_testing"


@dataclass
class UserBehaviorPattern:
    """User behavior pattern data."""
    pattern_id: str
    user_id: str
    pattern_type: str
    frequency: int
    confidence_score: float
    discovered_at: datetime
    last_observed: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTestConfig:
    """A/B test configuration."""
    test_id: str
    name: str
    description: str
    variants: List[Dict[str, Any]]
    traffic_split: Dict[str, float]
    success_metrics: List[str]
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"


class UserBehaviorAnalyzer(IUserBehaviorAnalyzer):
    """Implementation of user behavior tracking and analysis."""
    
    def __init__(self):
        self.user_behaviors: Dict[str, List[Dict[str, Any]]] = {}
        self.behavior_patterns: List[UserBehaviorPattern] = []
        self.engagement_history: Dict[str, List[EngagementContext]] = {}
        
    async def track_user_behavior(self, user_id: str, behavior_data: Dict[str, Any]) -> bool:
        """Track user behavior data."""
        try:
            if user_id not in self.user_behaviors:
                self.user_behaviors[user_id] = []
            
            # Add timestamp to behavior data
            behavior_entry = behavior_data.copy()
            behavior_entry["timestamp"] = datetime.now().isoformat()
            behavior_entry["user_id"] = user_id
            
            self.user_behaviors[user_id].append(behavior_entry)
            
            # Analyze for new patterns
            await self._analyze_behavior_patterns(user_id)
            
            logger.info(f"Behavior tracked for user {user_id}: {behavior_data.get('action', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Behavior tracking failed: {e}")
            return False
    
    async def analyze_engagement_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user engagement patterns."""
        try:
            if user_id not in self.user_behaviors:
                return {"error": "No behavior data for user"}
            
            behaviors = self.user_behaviors[user_id]
            
            # Analyze engagement patterns
            engagement_analysis = {
                "total_interactions": len(behaviors),
                "session_count": await self._count_sessions(behaviors),
                "average_session_duration": await self._calculate_avg_session_duration(behaviors),
                "preferred_interaction_types": await self._analyze_interaction_preferences(behaviors),
                "engagement_trends": await self._analyze_engagement_trends(behaviors),
                "peak_activity_hours": await self._analyze_activity_patterns(behaviors)
            }
            
            return engagement_analysis
            
        except Exception as e:
            logger.error(f"Engagement pattern analysis failed: {e}")
            return {"error": str(e)}
    
    async def predict_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Predict user preferences based on behavior."""
        try:
            if user_id not in self.user_behaviors:
                return {"preferences": {}, "confidence": 0.0}
            
            behaviors = self.user_behaviors[user_id]
            
            # Analyze preferences from behavior patterns
            preferences = {
                "preferred_engagement_level": await self._predict_engagement_level(behaviors),
                "preferred_interaction_modes": await self._predict_interaction_modes(behaviors),
                "optimal_session_length": await self._predict_session_length(behaviors),
                "preferred_visual_complexity": await self._predict_visual_preferences(behaviors),
                "notification_preferences": await self._predict_notification_preferences(behaviors)
            }
            
            # Calculate overall confidence
            confidence = await self._calculate_prediction_confidence(behaviors)
            
            return {
                "user_id": user_id,
                "preferences": preferences,
                "confidence": confidence,
                "based_on_interactions": len(behaviors),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"User preference prediction failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_behavior_patterns(self, user_id: str) -> None:
        """Analyze behavior patterns for a user."""
        try:
            behaviors = self.user_behaviors[user_id]
            
            # Look for repeated patterns
            action_sequences = []
            for i in range(len(behaviors) - 2):
                sequence = [behaviors[i]["action"], behaviors[i+1]["action"], behaviors[i+2]["action"]]
                action_sequences.append(sequence)
            
            # Find common sequences
            sequence_counts = {}
            for seq in action_sequences:
                seq_key = "->".join(seq)
                sequence_counts[seq_key] = sequence_counts.get(seq_key, 0) + 1
            
            # Create patterns for frequent sequences
            for seq_key, count in sequence_counts.items():
                if count >= 3:  # Pattern threshold
                    pattern = UserBehaviorPattern(
                        pattern_id=f"{user_id}_{seq_key}_{datetime.now().strftime('%Y%m%d')}",
                        user_id=user_id,
                        pattern_type="action_sequence",
                        frequency=count,
                        confidence_score=min(1.0, count / 10),  # Simple confidence calculation
                        discovered_at=datetime.now(),
                        last_observed=datetime.now(),
                        metadata={"sequence": seq_key, "actions": seq_key.split("->")}
                    )
                    self.behavior_patterns.append(pattern)
                    
        except Exception as e:
            logger.error(f"Behavior pattern analysis failed: {e}")
    
    async def _count_sessions(self, behaviors: List[Dict[str, Any]]) -> int:
        """Count user sessions from behavior data."""
        if not behaviors:
            return 0
        
        sessions = 1
        last_timestamp = None
        
        for behavior in behaviors:
            timestamp = datetime.fromisoformat(behavior["timestamp"])
            if last_timestamp and (timestamp - last_timestamp).total_seconds() > 1800:  # 30 min gap = new session
                sessions += 1
            last_timestamp = timestamp
        
        return sessions
    
    async def _calculate_avg_session_duration(self, behaviors: List[Dict[str, Any]]) -> float:
        """Calculate average session duration."""
        if len(behaviors) < 2:
            return 0.0
        
        first_timestamp = datetime.fromisoformat(behaviors[0]["timestamp"])
        last_timestamp = datetime.fromisoformat(behaviors[-1]["timestamp"])
        
        total_duration = (last_timestamp - first_timestamp).total_seconds()
        session_count = await self._count_sessions(behaviors)
        
        return total_duration / session_count if session_count > 0 else 0.0
    
    async def _analyze_interaction_preferences(self, behaviors: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze preferred interaction types."""
        interaction_counts = {}
        for behavior in behaviors:
            action = behavior.get("action", "unknown")
            interaction_counts[action] = interaction_counts.get(action, 0) + 1
        
        return dict(sorted(interaction_counts.items(), key=lambda x: x[1], reverse=True))
    
    async def _analyze_engagement_trends(self, behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement trends over time."""
        if len(behaviors) < 10:
            return {"trend": "insufficient_data"}
        
        # Simple trend analysis - compare first half vs second half
        mid_point = len(behaviors) // 2
        first_half = behaviors[:mid_point]
        second_half = behaviors[mid_point:]
        
        first_half_rate = len(first_half) / (len(first_half) * 60)  # interactions per minute
        second_half_rate = len(second_half) / (len(second_half) * 60)
        
        if second_half_rate > first_half_rate * 1.1:
            trend = "increasing"
        elif second_half_rate < first_half_rate * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "first_half_rate": first_half_rate,
            "second_half_rate": second_half_rate,
            "change_percentage": ((second_half_rate - first_half_rate) / first_half_rate * 100) if first_half_rate > 0 else 0
        }
    
    async def _analyze_activity_patterns(self, behaviors: List[Dict[str, Any]]) -> List[int]:
        """Analyze peak activity hours."""
        hour_counts = [0] * 24
        
        for behavior in behaviors:
            timestamp = datetime.fromisoformat(behavior["timestamp"])
            hour_counts[timestamp.hour] += 1
        
        # Return top 3 peak hours
        peak_hours = sorted(range(24), key=lambda x: hour_counts[x], reverse=True)[:3]
        return peak_hours
    
    async def _predict_engagement_level(self, behaviors: List[Dict[str, Any]]) -> str:
        """Predict preferred engagement level."""
        interaction_rate = len(behaviors) / max(1, len(behaviors) * 0.1)  # Simplified calculation
        
        if interaction_rate > 10:
            return EngagementLevel.IMMERSIVE.value
        elif interaction_rate > 5:
            return EngagementLevel.ACTIVE.value
        else:
            return EngagementLevel.PASSIVE.value
    
    async def _predict_interaction_modes(self, behaviors: List[Dict[str, Any]]) -> List[str]:
        """Predict preferred interaction modes."""
        interaction_prefs = await self._analyze_interaction_preferences(behaviors)
        return list(interaction_prefs.keys())[:3]  # Top 3
    
    async def _predict_session_length(self, behaviors: List[Dict[str, Any]]) -> float:
        """Predict optimal session length."""
        return await self._calculate_avg_session_duration(behaviors)
    
    async def _predict_visual_preferences(self, behaviors: List[Dict[str, Any]]) -> str:
        """Predict visual complexity preferences."""
        # Simplified prediction based on interaction frequency
        interaction_rate = len(behaviors) / max(1, len(behaviors) * 0.1)
        
        if interaction_rate > 8:
            return "high_complexity"
        elif interaction_rate > 4:
            return "medium_complexity"
        else:
            return "low_complexity"
    
    async def _predict_notification_preferences(self, behaviors: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Predict notification preferences."""
        return {
            "real_time_updates": len(behaviors) > 20,
            "achievement_notifications": len(behaviors) > 50,
            "system_alerts": True,  # Default to true for safety
            "engagement_reminders": len(behaviors) < 10
        }
    
    async def _calculate_prediction_confidence(self, behaviors: List[Dict[str, Any]]) -> float:
        """Calculate confidence in predictions."""
        # Simple confidence based on data volume and recency
        data_volume_score = min(1.0, len(behaviors) / 100)  # 100 interactions = full confidence
        
        if behaviors:
            last_interaction = datetime.fromisoformat(behaviors[-1]["timestamp"])
            recency_score = max(0.0, 1.0 - (datetime.now() - last_interaction).days / 30)  # Decay over 30 days
        else:
            recency_score = 0.0
        
        return (data_volume_score + recency_score) / 2


class EngagementOptimizer(IEngagementOptimizer):
    """Implementation of engagement strategy optimization."""
    
    def __init__(self):
        self.optimization_history: List[Dict[str, Any]] = []
        self.active_ab_tests: Dict[str, ABTestConfig] = {}
        self.optimization_strategies: Dict[str, Dict[str, Any]] = {}
        
    async def optimize_engagement_strategy(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize engagement strategy based on analytics."""
        try:
            # Analyze current performance
            current_performance = await self._analyze_current_performance(analytics_data)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(analytics_data)
            
            # Create optimization strategy
            strategy = {
                "strategy_id": f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "current_performance": current_performance,
                "recommendations": recommendations,
                "expected_improvements": await self._calculate_expected_improvements(recommendations),
                "implementation_priority": await self._prioritize_recommendations(recommendations),
                "created_at": datetime.now().isoformat()
            }
            
            self.optimization_history.append(strategy)
            
            logger.info(f"Engagement strategy optimized: {len(recommendations)} recommendations")
            return strategy
            
        except Exception as e:
            logger.error(f"Engagement optimization failed: {e}")
            return {"error": str(e)}
    
    async def run_ab_test(self, test_config: Dict[str, Any]) -> str:
        """Run A/B test for engagement strategies."""
        try:
            test_id = f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            ab_test = ABTestConfig(
                test_id=test_id,
                name=test_config.get("name", "Engagement A/B Test"),
                description=test_config.get("description", ""),
                variants=test_config.get("variants", []),
                traffic_split=test_config.get("traffic_split", {"A": 0.5, "B": 0.5}),
                success_metrics=test_config.get("success_metrics", ["engagement_rate", "session_duration"]),
                start_date=datetime.now(),
                end_date=test_config.get("end_date")
            )
            
            self.active_ab_tests[test_id] = ab_test
            
            logger.info(f"A/B test started: {test_id}")
            return test_id
            
        except Exception as e:
            logger.error(f"A/B test creation failed: {e}")
            return ""
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get current optimization recommendations."""
        try:
            if not self.optimization_history:
                return []
            
            latest_optimization = self.optimization_history[-1]
            return latest_optimization.get("recommendations", [])
            
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return []
    
    async def _analyze_current_performance(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current engagement performance."""
        return {
            "engagement_rate": analytics_data.get("engagement_rate", 0.0),
            "session_duration": analytics_data.get("average_session_duration", 0.0),
            "interaction_frequency": analytics_data.get("interaction_frequency", 0.0),
            "user_retention": analytics_data.get("user_retention", 0.0),
            "performance_score": await self._calculate_performance_score(analytics_data)
        }
    
    async def _generate_optimization_recommendations(self, analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Analyze engagement rate
        engagement_rate = analytics_data.get("engagement_rate", 0.0)
        if engagement_rate < 0.5:
            recommendations.append({
                "type": "engagement_boost",
                "priority": "high",
                "description": "Increase visual animations and interactive elements",
                "expected_impact": 0.2,
                "implementation_effort": "medium"
            })
        
        # Analyze session duration
        session_duration = analytics_data.get("average_session_duration", 0.0)
        if session_duration < 300:  # Less than 5 minutes
            recommendations.append({
                "type": "retention_improvement",
                "priority": "high",
                "description": "Add progressive disclosure and achievement systems",
                "expected_impact": 0.3,
                "implementation_effort": "high"
            })
        
        # Analyze interaction patterns
        interaction_diversity = analytics_data.get("interaction_diversity", 0)
        if interaction_diversity < 3:
            recommendations.append({
                "type": "interaction_diversification",
                "priority": "medium",
                "description": "Add more interaction modes (voice, gesture, etc.)",
                "expected_impact": 0.15,
                "implementation_effort": "high"
            })
        
        return recommendations
    
    async def _calculate_expected_improvements(self, recommendations: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate expected improvements from recommendations."""
        total_engagement_improvement = sum(r.get("expected_impact", 0.0) for r in recommendations)
        
        return {
            "engagement_rate_improvement": total_engagement_improvement,
            "session_duration_improvement": total_engagement_improvement * 0.5,
            "user_satisfaction_improvement": total_engagement_improvement * 0.7,
            "overall_performance_improvement": total_engagement_improvement * 0.8
        }
    
    async def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize recommendations by impact and effort."""
        def priority_score(rec):
            impact = rec.get("expected_impact", 0.0)
            effort_multiplier = {"low": 1.0, "medium": 0.7, "high": 0.4}.get(rec.get("implementation_effort", "medium"), 0.7)
            return impact * effort_multiplier
        
        return sorted(recommendations, key=priority_score, reverse=True)
    
    async def _calculate_performance_score(self, analytics_data: Dict[str, Any]) -> float:
        """Calculate overall performance score."""
        engagement_rate = analytics_data.get("engagement_rate", 0.0)
        session_duration = min(1.0, analytics_data.get("average_session_duration", 0.0) / 1800)  # Normalize to 30 min
        interaction_frequency = min(1.0, analytics_data.get("interaction_frequency", 0.0) / 10)  # Normalize to 10 per session
        
        return (engagement_rate + session_duration + interaction_frequency) / 3


class LearningEngine(ReflectiveModule):
    """
    Main Learning Engine that provides user behavior analysis,
    engagement optimization, and A/B testing for continuous improvement.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "learning_engine"
        
        # Core components
        self.behavior_analyzer = UserBehaviorAnalyzer()
        self.engagement_optimizer = EngagementOptimizer()
        
        # State management
        self.is_initialized = False
        self.learning_strategies: Dict[str, LearningStrategy] = {}
        
        logger.info("Learning Engine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Learning Engine."""
        try:
            # Initialize default learning strategies
            self.learning_strategies["user_behavior"] = LearningStrategy.UNSUPERVISED
            self.learning_strategies["engagement_optimization"] = LearningStrategy.REINFORCEMENT
            self.learning_strategies["ab_testing"] = LearningStrategy.A_B_TESTING
            
            self.is_initialized = True
            logger.info("Learning Engine initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Learning Engine initialization failed: {e}")
            return False
    
    async def learn_from_user_behavior(self, user_id: str, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from user behavior data."""
        try:
            # Track behavior
            tracked = await self.behavior_analyzer.track_user_behavior(user_id, behavior_data)
            
            if tracked:
                # Analyze patterns
                patterns = await self.behavior_analyzer.analyze_engagement_patterns(user_id)
                
                # Predict preferences
                preferences = await self.behavior_analyzer.predict_user_preferences(user_id)
                
                return {
                    "user_id": user_id,
                    "behavior_tracked": True,
                    "patterns_analyzed": patterns,
                    "preferences_updated": preferences,
                    "learning_strategy": self.learning_strategies["user_behavior"].value
                }
            else:
                return {"error": "Failed to track behavior"}
                
        except Exception as e:
            logger.error(f"Learning from user behavior failed: {e}")
            return {"error": str(e)}
    
    async def optimize_engagement(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize engagement based on analytics."""
        try:
            optimization_result = await self.engagement_optimizer.optimize_engagement_strategy(analytics_data)
            
            return {
                "optimization_completed": True,
                "strategy": optimization_result,
                "learning_strategy": self.learning_strategies["engagement_optimization"].value,
                "recommendations_count": len(optimization_result.get("recommendations", []))
            }
            
        except Exception as e:
            logger.error(f"Engagement optimization failed: {e}")
            return {"error": str(e)}
    
    async def start_ab_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Start an A/B test for engagement strategies."""
        try:
            test_id = await self.engagement_optimizer.run_ab_test(test_config)
            
            if test_id:
                return {
                    "test_started": True,
                    "test_id": test_id,
                    "learning_strategy": self.learning_strategies["ab_testing"].value,
                    "test_config": test_config
                }
            else:
                return {"error": "Failed to start A/B test"}
                
        except Exception as e:
            logger.error(f"A/B test start failed: {e}")
            return {"error": str(e)}
    
    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get learning insights and analytics."""
        try:
            return {
                "behavior_patterns": len(self.behavior_analyzer.behavior_patterns),
                "tracked_users": len(self.behavior_analyzer.user_behaviors),
                "optimization_history": len(self.engagement_optimizer.optimization_history),
                "active_ab_tests": len(self.engagement_optimizer.active_ab_tests),
                "learning_strategies": {k: v.value for k, v in self.learning_strategies.items()},
                "learning_effectiveness": await self._calculate_learning_effectiveness()
            }
            
        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            return {"error": str(e)}
    
    async def _calculate_learning_effectiveness(self) -> Dict[str, float]:
        """Calculate learning system effectiveness."""
        return {
            "pattern_discovery_rate": len(self.behavior_analyzer.behavior_patterns) / max(1, len(self.behavior_analyzer.user_behaviors)),
            "optimization_success_rate": 0.8,  # Placeholder
            "prediction_accuracy": 0.75,  # Placeholder
            "overall_effectiveness": 0.77
        }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Learning Engine capabilities."""
        return [
            "user_behavior_analysis",
            "engagement_optimization",
            "ab_testing",
            "pattern_discovery",
            "preference_prediction"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Learning Engine health status."""
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "tracked_users": len(self.behavior_analyzer.user_behaviors),
            "behavior_patterns": len(self.behavior_analyzer.behavior_patterns),
            "active_optimizations": len(self.engagement_optimizer.optimization_history),
            "active_ab_tests": len(self.engagement_optimizer.active_ab_tests)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Learning Engine module information."""
        return {
            "module_id": self.module_id,
            "name": "Learning Engine",
            "version": "1.0.0",
            "description": "User behavior analysis and engagement optimization with continuous learning"
        }