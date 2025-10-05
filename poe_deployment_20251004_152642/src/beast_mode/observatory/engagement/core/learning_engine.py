"""
Learning Engine - Continuous Improvement and User Behavior Analysis
===================================================================

The Learning Engine provides continuous improvement through user behavior analysis,
A/B testing, and engagement optimization for the Live Dashboard Engagement System.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import statistics
import random

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .interfaces import (
    IUserBehaviorAnalyzer, 
    IEngagementOptimizer,
    EngagementContext,
    EngagementLevel
)

logger = logging.getLogger(__name__)


# Additional interfaces needed for LearningEngine
class IFeedbackProcessor(ABC):
    """Interface for incorporating user feedback into learning models."""
    
    @abstractmethod
    async def process_user_feedback(self, user_id: str, feedback: Dict[str, Any]) -> bool:
        """Process user feedback and incorporate into learning models."""
        pass
    
    @abstractmethod
    async def get_feedback_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of user feedback data."""
        pass
    
    @abstractmethod
    async def apply_feedback_insights(self, insights: Dict[str, Any]) -> bool:
        """Apply insights derived from feedback analysis."""
        pass


class IABTestManager(ABC):
    """Interface for A/B testing engagement techniques."""
    
    @abstractmethod
    async def create_ab_test(self, test_config: Dict[str, Any]) -> str:
        """Create a new A/B test with given configuration."""
        pass
    
    @abstractmethod
    async def assign_user_to_variant(self, test_id: str, user_id: str) -> str:
        """Assign user to A/B test variant."""
        pass
    
    @abstractmethod
    async def record_test_result(self, test_id: str, user_id: str, result: Dict[str, Any]) -> bool:
        """Record A/B test result for analysis."""
        pass
    
    @abstractmethod
    async def analyze_test_results(self, test_id: str) -> Dict[str, Any]:
        """Analyze A/B test results and determine winner."""
        pass
    
    @abstractmethod
    async def get_active_tests(self) -> List[Dict[str, Any]]:
        """Get list of currently active A/B tests."""
        pass


@dataclass
class UserBehaviorData:
    """User behavior tracking data."""
    user_id: str
    session_id: str
    timestamp: datetime
    interaction_type: str
    engagement_level: EngagementLevel
    duration_seconds: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngagementPattern:
    """Identified engagement pattern."""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: float
    effectiveness_score: float
    user_segments: List[str]
    conditions: Dict[str, Any]
    recommendations: List[str]


@dataclass
class ABTestVariant:
    """A/B test variant configuration."""
    variant_id: str
    name: str
    description: str
    config: Dict[str, Any]
    traffic_percentage: float
    success_metric: str


@dataclass
class ABTest:
    """A/B test configuration and tracking."""
    test_id: str
    name: str
    description: str
    variants: List[ABTestVariant]
    start_date: datetime
    end_date: Optional[datetime]
    status: str  # 'active', 'completed', 'paused'
    success_criteria: Dict[str, Any]
    results: Dict[str, Any] = field(default_factory=dict)


class UserBehaviorAnalyzer(IUserBehaviorAnalyzer):
    """Implementation of user behavior tracking and analysis."""
    
    def __init__(self):
        self.behavior_data: List[UserBehaviorData] = []
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.engagement_patterns: List[EngagementPattern] = []
        
    async def track_user_behavior(self, user_id: str, behavior_data: Dict[str, Any]) -> bool:
        """Track user behavior data."""
        try:
            # Create behavior data record
            behavior_record = UserBehaviorData(
                user_id=user_id,
                session_id=behavior_data.get("session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                timestamp=datetime.now(),
                interaction_type=behavior_data.get("interaction_type", "unknown"),
                engagement_level=EngagementLevel(behavior_data.get("engagement_level", "passive")),
                duration_seconds=behavior_data.get("duration_seconds", 0.0),
                success=behavior_data.get("success", True),
                metadata=behavior_data.get("metadata", {})
            )
            
            # Store behavior data
            self.behavior_data.append(behavior_record)
            
            # Update user profile
            await self._update_user_profile(user_id, behavior_record)
            
            # Analyze for new patterns
            await self._analyze_behavior_patterns(user_id)
            
            logger.info(f"Tracked behavior for user {user_id}: {behavior_record.interaction_type}")
            return True
            
        except Exception as e:
            logger.error(f"Behavior tracking failed: {e}")
            return False
    
    async def analyze_engagement_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user engagement patterns."""
        try:
            # Get user behavior data
            user_behaviors = [b for b in self.behavior_data if b.user_id == user_id]
            
            if not user_behaviors:
                return {"patterns": [], "insights": [], "recommendations": []}
            
            # Analyze patterns
            patterns = await self._identify_engagement_patterns(user_behaviors)
            insights = await self._generate_engagement_insights(user_behaviors, patterns)
            recommendations = await self._generate_engagement_recommendations(insights)
            
            return {
                "user_id": user_id,
                "total_interactions": len(user_behaviors),
                "patterns": [self._pattern_to_dict(p) for p in patterns],
                "insights": insights,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Engagement pattern analysis failed: {e}")
            return {"error": str(e)}
    
    async def predict_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Predict user preferences based on behavior."""
        try:
            # Get user profile
            profile = self.user_profiles.get(user_id, {})
            user_behaviors = [b for b in self.behavior_data if b.user_id == user_id]
            
            if not user_behaviors:
                return {"preferences": {}, "confidence": 0.0}
            
            # Analyze preferences
            preferences = {}
            
            # Preferred engagement level
            engagement_levels = [b.engagement_level.value for b in user_behaviors]
            if engagement_levels:
                preferences["preferred_engagement_level"] = max(set(engagement_levels), key=engagement_levels.count)
            
            # Preferred interaction types
            interaction_types = [b.interaction_type for b in user_behaviors]
            if interaction_types:
                preferences["preferred_interactions"] = list(set(interaction_types))[:3]  # Top 3
            
            # Optimal session duration
            successful_sessions = [b.duration_seconds for b in user_behaviors if b.success]
            if successful_sessions:
                preferences["optimal_session_duration"] = statistics.mean(successful_sessions)
            
            # Time preferences
            session_hours = [b.timestamp.hour for b in user_behaviors]
            if session_hours:
                preferences["preferred_hours"] = list(set(session_hours))
            
            # Calculate confidence based on data volume
            confidence = min(1.0, len(user_behaviors) / 50.0)  # Full confidence at 50+ interactions
            
            return {
                "user_id": user_id,
                "preferences": preferences,
                "confidence": confidence,
                "data_points": len(user_behaviors),
                "prediction_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"User preference prediction failed: {e}")
            return {"error": str(e)}
    
    async def _update_user_profile(self, user_id: str, behavior: UserBehaviorData) -> None:
        """Update user profile with new behavior data."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "first_seen": behavior.timestamp,
                "total_interactions": 0,
                "successful_interactions": 0,
                "total_duration": 0.0,
                "engagement_levels": {},
                "interaction_types": {}
            }
        
        profile = self.user_profiles[user_id]
        profile["last_seen"] = behavior.timestamp
        profile["total_interactions"] += 1
        profile["total_duration"] += behavior.duration_seconds
        
        if behavior.success:
            profile["successful_interactions"] += 1
        
        # Track engagement levels
        level = behavior.engagement_level.value
        profile["engagement_levels"][level] = profile["engagement_levels"].get(level, 0) + 1
        
        # Track interaction types
        interaction = behavior.interaction_type
        profile["interaction_types"][interaction] = profile["interaction_types"].get(interaction, 0) + 1
    
    async def _analyze_behavior_patterns(self, user_id: str) -> None:
        """Analyze behavior patterns for pattern identification."""
        try:
            user_behaviors = [b for b in self.behavior_data if b.user_id == user_id]
            
            if len(user_behaviors) < 5:  # Need minimum data for pattern analysis
                return
            
            # Look for time-based patterns
            await self._identify_time_patterns(user_behaviors)
            
            # Look for engagement progression patterns
            await self._identify_engagement_progression(user_behaviors)
            
            # Look for success patterns
            await self._identify_success_patterns(user_behaviors)
            
        except Exception as e:
            logger.error(f"Behavior pattern analysis failed: {e}")
    
    async def _identify_engagement_patterns(self, behaviors: List[UserBehaviorData]) -> List[EngagementPattern]:
        """Identify engagement patterns from behavior data."""
        patterns = []
        
        try:
            # Pattern 1: Engagement level progression
            if len(behaviors) >= 3:
                levels = [b.engagement_level for b in behaviors[-10:]]  # Last 10 interactions
                if len(set(levels)) > 1:  # Multiple engagement levels
                    pattern = EngagementPattern(
                        pattern_id=f"engagement_progression_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        pattern_type="engagement_progression",
                        description="User shows varying engagement levels",
                        frequency=len(set(levels)) / len(levels),
                        effectiveness_score=sum(1 for b in behaviors[-10:] if b.success) / min(10, len(behaviors)),
                        user_segments=[behaviors[0].user_id],
                        conditions={"min_interactions": 3, "engagement_variety": True},
                        recommendations=["Adapt engagement level based on user state", "Provide engagement level controls"]
                    )
                    patterns.append(pattern)
            
            # Pattern 2: Time-based engagement
            if len(behaviors) >= 5:
                hours = [b.timestamp.hour for b in behaviors]
                hour_counts = {}
                for hour in hours:
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                
                if hour_counts:
                    peak_hour = max(hour_counts, key=hour_counts.get)
                    pattern = EngagementPattern(
                        pattern_id=f"time_preference_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        pattern_type="time_preference",
                        description=f"User most active during hour {peak_hour}",
                        frequency=hour_counts[peak_hour] / len(behaviors),
                        effectiveness_score=sum(1 for b in behaviors if b.timestamp.hour == peak_hour and b.success) / hour_counts[peak_hour],
                        user_segments=[behaviors[0].user_id],
                        conditions={"peak_hour": peak_hour},
                        recommendations=[f"Optimize engagement for hour {peak_hour}", "Provide time-based customization"]
                    )
                    patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"Pattern identification failed: {e}")
        
        return patterns
    
    async def _identify_time_patterns(self, behaviors: List[UserBehaviorData]) -> None:
        """Identify time-based behavior patterns."""
        # Implementation for time pattern analysis
        pass
    
    async def _identify_engagement_progression(self, behaviors: List[UserBehaviorData]) -> None:
        """Identify engagement progression patterns."""
        # Implementation for engagement progression analysis
        pass
    
    async def _identify_success_patterns(self, behaviors: List[UserBehaviorData]) -> None:
        """Identify patterns that lead to successful interactions."""
        # Implementation for success pattern analysis
        pass
    
    async def _generate_engagement_insights(self, behaviors: List[UserBehaviorData], patterns: List[EngagementPattern]) -> List[str]:
        """Generate insights from behavior analysis."""
        insights = []
        
        if not behaviors:
            return insights
        
        # Success rate insight
        success_rate = sum(1 for b in behaviors if b.success) / len(behaviors)
        if success_rate > 0.8:
            insights.append("User has high engagement success rate")
        elif success_rate < 0.5:
            insights.append("User engagement could be improved")
        
        # Duration insight
        avg_duration = sum(b.duration_seconds for b in behaviors) / len(behaviors)
        if avg_duration > 300:  # 5 minutes
            insights.append("User prefers longer engagement sessions")
        elif avg_duration < 60:  # 1 minute
            insights.append("User prefers quick interactions")
        
        # Pattern insights
        for pattern in patterns:
            if pattern.effectiveness_score > 0.7:
                insights.append(f"Effective pattern identified: {pattern.description}")
        
        return insights
    
    async def _generate_engagement_recommendations(self, insights: List[str]) -> List[str]:
        """Generate engagement recommendations from insights."""
        recommendations = []
        
        for insight in insights:
            if "high engagement success rate" in insight:
                recommendations.append("Continue current engagement strategies")
            elif "engagement could be improved" in insight:
                recommendations.append("Experiment with different engagement techniques")
            elif "longer engagement sessions" in insight:
                recommendations.append("Provide deeper content and extended interactions")
            elif "quick interactions" in insight:
                recommendations.append("Focus on concise, immediate value interactions")
        
        return recommendations
    
    def _pattern_to_dict(self, pattern: EngagementPattern) -> Dict[str, Any]:
        """Convert engagement pattern to dictionary."""
        return {
            "pattern_id": pattern.pattern_id,
            "pattern_type": pattern.pattern_type,
            "description": pattern.description,
            "frequency": pattern.frequency,
            "effectiveness_score": pattern.effectiveness_score,
            "user_segments": pattern.user_segments,
            "conditions": pattern.conditions,
            "recommendations": pattern.recommendations
        }


class EngagementOptimizer(IEngagementOptimizer):
    """Implementation of engagement strategy optimization."""
    
    def __init__(self):
        self.optimization_history: List[Dict[str, Any]] = []
        self.current_strategies: Dict[str, Dict[str, Any]] = {}
        self.performance_metrics: Dict[str, List[float]] = {}
        
    async def optimize_engagement_strategy(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize engagement strategy based on analytics."""
        try:
            # Analyze current performance
            current_performance = await self._analyze_current_performance(analytics_data)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(current_performance)
            
            # Apply optimizations
            applied_optimizations = await self._apply_optimizations(recommendations)
            
            # Record optimization
            optimization_record = {
                "timestamp": datetime.now().isoformat(),
                "analytics_data": analytics_data,
                "current_performance": current_performance,
                "recommendations": recommendations,
                "applied_optimizations": applied_optimizations
            }
            self.optimization_history.append(optimization_record)
            
            logger.info(f"Engagement strategy optimized: {len(applied_optimizations)} changes applied")
            
            return {
                "optimization_id": f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "performance_improvement": current_performance.get("improvement_potential", 0.0),
                "recommendations": recommendations,
                "applied_optimizations": applied_optimizations,
                "next_review": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Engagement optimization failed: {e}")
            return {"error": str(e)}
    
    async def run_ab_test(self, test_config: Dict[str, Any]) -> str:
        """Run A/B test for engagement strategies."""
        try:
            test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # This is a placeholder implementation
            # In a real system, this would integrate with the ABTestManager
            logger.info(f"A/B test initiated: {test_id}")
            
            return test_id
            
        except Exception as e:
            logger.error(f"A/B test creation failed: {e}")
            return ""
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations."""
        try:
            recommendations = []
            
            # Analyze recent performance
            if self.performance_metrics:
                for metric_name, values in self.performance_metrics.items():
                    if len(values) >= 5:  # Need minimum data
                        recent_avg = statistics.mean(values[-5:])
                        overall_avg = statistics.mean(values)
                        
                        if recent_avg < overall_avg * 0.9:  # 10% decline
                            recommendations.append({
                                "type": "performance_decline",
                                "metric": metric_name,
                                "description": f"{metric_name} has declined recently",
                                "recommendation": f"Review and optimize {metric_name} strategies",
                                "priority": "high",
                                "expected_impact": "medium"
                            })
                        elif recent_avg > overall_avg * 1.1:  # 10% improvement
                            recommendations.append({
                                "type": "performance_improvement",
                                "metric": metric_name,
                                "description": f"{metric_name} is improving",
                                "recommendation": f"Scale successful {metric_name} strategies",
                                "priority": "medium",
                                "expected_impact": "high"
                            })
            
            # Add general recommendations
            if not recommendations:
                recommendations.append({
                    "type": "baseline",
                    "description": "Continue monitoring engagement metrics",
                    "recommendation": "Maintain current strategies and collect more data",
                    "priority": "low",
                    "expected_impact": "low"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Get optimization recommendations failed: {e}")
            return []
    
    async def _analyze_current_performance(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current engagement performance."""
        performance = {
            "overall_score": 0.5,  # Default neutral score
            "improvement_potential": 0.0,
            "key_metrics": {},
            "trends": {}
        }
        
        try:
            # Analyze key metrics from analytics data
            if "engagement_rate" in analytics_data:
                engagement_rate = analytics_data["engagement_rate"]
                performance["key_metrics"]["engagement_rate"] = engagement_rate
                performance["overall_score"] = engagement_rate
                
                # Store for trend analysis
                if "engagement_rate" not in self.performance_metrics:
                    self.performance_metrics["engagement_rate"] = []
                self.performance_metrics["engagement_rate"].append(engagement_rate)
            
            if "user_satisfaction" in analytics_data:
                satisfaction = analytics_data["user_satisfaction"]
                performance["key_metrics"]["user_satisfaction"] = satisfaction
                
                if "user_satisfaction" not in self.performance_metrics:
                    self.performance_metrics["user_satisfaction"] = []
                self.performance_metrics["user_satisfaction"].append(satisfaction)
            
            # Calculate improvement potential
            if performance["overall_score"] < 0.8:
                performance["improvement_potential"] = 0.8 - performance["overall_score"]
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
        
        return performance
    
    async def _generate_optimization_recommendations(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on performance."""
        recommendations = []
        
        try:
            overall_score = performance.get("overall_score", 0.5)
            
            if overall_score < 0.6:
                recommendations.append({
                    "type": "engagement_boost",
                    "description": "Overall engagement is below target",
                    "action": "Increase visual feedback and interactivity",
                    "expected_impact": 0.2,
                    "priority": "high"
                })
            
            if overall_score > 0.8:
                recommendations.append({
                    "type": "maintain_excellence",
                    "description": "Engagement is performing well",
                    "action": "Continue current strategies with minor optimizations",
                    "expected_impact": 0.05,
                    "priority": "low"
                })
            
            # Add metric-specific recommendations
            for metric, value in performance.get("key_metrics", {}).items():
                if isinstance(value, (int, float)) and value < 0.7:
                    recommendations.append({
                        "type": "metric_improvement",
                        "description": f"{metric} needs improvement",
                        "action": f"Focus optimization efforts on {metric}",
                        "expected_impact": 0.15,
                        "priority": "medium"
                    })
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
        
        return recommendations
    
    async def _apply_optimizations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply optimization recommendations."""
        applied = []
        
        try:
            for rec in recommendations:
                if rec.get("priority") == "high":
                    # Apply high priority optimizations
                    optimization = {
                        "recommendation_id": rec.get("type", "unknown"),
                        "action_taken": rec.get("action", "No action specified"),
                        "applied_at": datetime.now().isoformat(),
                        "expected_impact": rec.get("expected_impact", 0.0)
                    }
                    applied.append(optimization)
                    
                    # Update current strategies
                    strategy_key = rec.get("type", "default")
                    self.current_strategies[strategy_key] = {
                        "action": rec.get("action"),
                        "applied_at": datetime.now(),
                        "expected_impact": rec.get("expected_impact", 0.0)
                    }
            
        except Exception as e:
            logger.error(f"Optimization application failed: {e}")
        
        return applied


class FeedbackProcessor(IFeedbackProcessor):
    """Implementation of user feedback processing."""
    
    def __init__(self):
        self.feedback_data: List[Dict[str, Any]] = []
        self.feedback_insights: Dict[str, Any] = {}
        
    async def process_user_feedback(self, user_id: str, feedback: Dict[str, Any]) -> bool:
        """Process user feedback and incorporate into learning models."""
        try:
            # Create feedback record
            feedback_record = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "feedback_type": feedback.get("type", "general"),
                "rating": feedback.get("rating", 0),
                "comments": feedback.get("comments", ""),
                "feature": feedback.get("feature", "general"),
                "metadata": feedback.get("metadata", {})
            }
            
            # Store feedback
            self.feedback_data.append(feedback_record)
            
            # Process feedback for insights
            await self._extract_feedback_insights(feedback_record)
            
            logger.info(f"Processed feedback from user {user_id}: {feedback.get('type', 'general')}")
            return True
            
        except Exception as e:
            logger.error(f"Feedback processing failed: {e}")
            return False
    
    async def get_feedback_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of user feedback data."""
        try:
            # Filter feedback data
            if user_id:
                feedback_subset = [f for f in self.feedback_data if f["user_id"] == user_id]
            else:
                feedback_subset = self.feedback_data
            
            if not feedback_subset:
                return {"total_feedback": 0, "average_rating": 0.0, "insights": []}
            
            # Calculate summary statistics
            total_feedback = len(feedback_subset)
            ratings = [f["rating"] for f in feedback_subset if f["rating"] > 0]
            average_rating = statistics.mean(ratings) if ratings else 0.0
            
            # Categorize feedback
            feedback_by_type = {}
            for feedback in feedback_subset:
                feedback_type = feedback["feedback_type"]
                if feedback_type not in feedback_by_type:
                    feedback_by_type[feedback_type] = []
                feedback_by_type[feedback_type].append(feedback)
            
            return {
                "user_id": user_id,
                "total_feedback": total_feedback,
                "average_rating": average_rating,
                "feedback_by_type": {k: len(v) for k, v in feedback_by_type.items()},
                "recent_feedback": feedback_subset[-5:],  # Last 5 feedback items
                "insights": list(self.feedback_insights.values())[-10:],  # Last 10 insights
                "summary_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Feedback summary generation failed: {e}")
            return {"error": str(e)}
    
    async def apply_feedback_insights(self, insights: Dict[str, Any]) -> bool:
        """Apply insights derived from feedback analysis."""
        try:
            # Store insights
            insight_id = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.feedback_insights[insight_id] = {
                **insights,
                "applied_at": datetime.now().isoformat(),
                "status": "applied"
            }
            
            logger.info(f"Applied feedback insights: {insight_id}")
            return True
            
        except Exception as e:
            logger.error(f"Feedback insights application failed: {e}")
            return False
    
    async def _extract_feedback_insights(self, feedback: Dict[str, Any]) -> None:
        """Extract insights from feedback data."""
        try:
            # Simple insight extraction based on feedback patterns
            if feedback["rating"] >= 4:
                insight = {
                    "type": "positive_feedback",
                    "feature": feedback["feature"],
                    "insight": f"Users appreciate {feedback['feature']} feature",
                    "recommendation": f"Continue and enhance {feedback['feature']} functionality"
                }
                
                insight_key = f"positive_{feedback['feature']}_{datetime.now().strftime('%Y%m%d')}"
                self.feedback_insights[insight_key] = insight
            
            elif feedback["rating"] <= 2:
                insight = {
                    "type": "negative_feedback",
                    "feature": feedback["feature"],
                    "insight": f"Users have issues with {feedback['feature']} feature",
                    "recommendation": f"Review and improve {feedback['feature']} functionality"
                }
                
                insight_key = f"negative_{feedback['feature']}_{datetime.now().strftime('%Y%m%d')}"
                self.feedback_insights[insight_key] = insight
            
        except Exception as e:
            logger.error(f"Feedback insight extraction failed: {e}")


class ABTestManager(IABTestManager):
    """Implementation of A/B testing for engagement techniques."""
    
    def __init__(self):
        self.active_tests: Dict[str, ABTest] = {}
        self.test_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {test_id: variant_id}
        self.test_results: Dict[str, List[Dict[str, Any]]] = {}
        
    async def create_ab_test(self, test_config: Dict[str, Any]) -> str:
        """Create a new A/B test with given configuration."""
        try:
            test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create variants
            variants = []
            for variant_config in test_config.get("variants", []):
                variant = ABTestVariant(
                    variant_id=variant_config["id"],
                    name=variant_config["name"],
                    description=variant_config.get("description", ""),
                    config=variant_config.get("config", {}),
                    traffic_percentage=variant_config.get("traffic_percentage", 50.0),
                    success_metric=variant_config.get("success_metric", "engagement_rate")
                )
                variants.append(variant)
            
            # Create A/B test
            ab_test = ABTest(
                test_id=test_id,
                name=test_config["name"],
                description=test_config.get("description", ""),
                variants=variants,
                start_date=datetime.now(),
                end_date=None,
                status="active",
                success_criteria=test_config.get("success_criteria", {}),
                results={}
            )
            
            # Store test
            self.active_tests[test_id] = ab_test
            self.test_results[test_id] = []
            
            logger.info(f"Created A/B test: {test_id} - {ab_test.name}")
            return test_id
            
        except Exception as e:
            logger.error(f"A/B test creation failed: {e}")
            return ""
    
    async def assign_user_to_variant(self, test_id: str, user_id: str) -> str:
        """Assign user to A/B test variant."""
        try:
            if test_id not in self.active_tests:
                return ""
            
            # Check if user already assigned
            if user_id in self.test_assignments and test_id in self.test_assignments[user_id]:
                return self.test_assignments[user_id][test_id]
            
            # Assign user to variant based on traffic percentage
            test = self.active_tests[test_id]
            random.seed(hash(user_id + test_id))  # Consistent assignment
            
            cumulative_percentage = 0.0
            random_value = random.random() * 100
            
            for variant in test.variants:
                cumulative_percentage += variant.traffic_percentage
                if random_value <= cumulative_percentage:
                    # Assign user to this variant
                    if user_id not in self.test_assignments:
                        self.test_assignments[user_id] = {}
                    self.test_assignments[user_id][test_id] = variant.variant_id
                    
                    logger.info(f"Assigned user {user_id} to variant {variant.variant_id} in test {test_id}")
                    return variant.variant_id
            
            # Fallback to first variant
            if test.variants:
                variant_id = test.variants[0].variant_id
                if user_id not in self.test_assignments:
                    self.test_assignments[user_id] = {}
                self.test_assignments[user_id][test_id] = variant_id
                return variant_id
            
            return ""
            
        except Exception as e:
            logger.error(f"User variant assignment failed: {e}")
            return ""
    
    async def record_test_result(self, test_id: str, user_id: str, result: Dict[str, Any]) -> bool:
        """Record A/B test result for analysis."""
        try:
            if test_id not in self.active_tests:
                return False
            
            # Get user's variant assignment
            variant_id = ""
            if user_id in self.test_assignments and test_id in self.test_assignments[user_id]:
                variant_id = self.test_assignments[user_id][test_id]
            
            # Record result
            result_record = {
                "user_id": user_id,
                "variant_id": variant_id,
                "timestamp": datetime.now().isoformat(),
                "result_data": result,
                "success_metric_value": result.get("success_metric_value", 0.0)
            }
            
            if test_id not in self.test_results:
                self.test_results[test_id] = []
            self.test_results[test_id].append(result_record)
            
            logger.info(f"Recorded A/B test result for test {test_id}, user {user_id}, variant {variant_id}")
            return True
            
        except Exception as e:
            logger.error(f"A/B test result recording failed: {e}")
            return False
    
    async def analyze_test_results(self, test_id: str) -> Dict[str, Any]:
        """Analyze A/B test results and determine winner."""
        try:
            if test_id not in self.active_tests or test_id not in self.test_results:
                return {"error": "Test not found"}
            
            test = self.active_tests[test_id]
            results = self.test_results[test_id]
            
            if not results:
                return {"error": "No results to analyze"}
            
            # Analyze results by variant
            variant_analysis = {}
            for variant in test.variants:
                variant_results = [r for r in results if r["variant_id"] == variant.variant_id]
                
                if variant_results:
                    success_values = [r["success_metric_value"] for r in variant_results]
                    variant_analysis[variant.variant_id] = {
                        "name": variant.name,
                        "sample_size": len(variant_results),
                        "mean_success_metric": statistics.mean(success_values),
                        "median_success_metric": statistics.median(success_values),
                        "std_dev": statistics.stdev(success_values) if len(success_values) > 1 else 0.0
                    }
                else:
                    variant_analysis[variant.variant_id] = {
                        "name": variant.name,
                        "sample_size": 0,
                        "mean_success_metric": 0.0,
                        "median_success_metric": 0.0,
                        "std_dev": 0.0
                    }
            
            # Determine winner (simple approach - highest mean)
            winner_variant_id = ""
            highest_mean = -1.0
            for variant_id, analysis in variant_analysis.items():
                if analysis["mean_success_metric"] > highest_mean:
                    highest_mean = analysis["mean_success_metric"]
                    winner_variant_id = variant_id
            
            # Calculate statistical significance (simplified)
            statistical_significance = "low"
            total_sample_size = sum(a["sample_size"] for a in variant_analysis.values())
            if total_sample_size > 100:
                statistical_significance = "medium"
            if total_sample_size > 500:
                statistical_significance = "high"
            
            return {
                "test_id": test_id,
                "test_name": test.name,
                "total_results": len(results),
                "variant_analysis": variant_analysis,
                "winner_variant_id": winner_variant_id,
                "winner_improvement": highest_mean,
                "statistical_significance": statistical_significance,
                "analysis_timestamp": datetime.now().isoformat(),
                "recommendation": f"Consider implementing variant {winner_variant_id}" if winner_variant_id else "Collect more data"
            }
            
        except Exception as e:
            logger.error(f"A/B test analysis failed: {e}")
            return {"error": str(e)}
    
    async def get_active_tests(self) -> List[Dict[str, Any]]:
        """Get list of currently active A/B tests."""
        try:
            active_tests = []
            
            for test_id, test in self.active_tests.items():
                if test.status == "active":
                    test_info = {
                        "test_id": test_id,
                        "name": test.name,
                        "description": test.description,
                        "start_date": test.start_date.isoformat(),
                        "variants": [
                            {
                                "variant_id": v.variant_id,
                                "name": v.name,
                                "traffic_percentage": v.traffic_percentage
                            }
                            for v in test.variants
                        ],
                        "total_results": len(self.test_results.get(test_id, [])),
                        "status": test.status
                    }
                    active_tests.append(test_info)
            
            return active_tests
            
        except Exception as e:
            logger.error(f"Get active tests failed: {e}")
            return []


class LearningEngine(ReflectiveModule):
    """
    Main Learning Engine that provides continuous improvement through user behavior analysis,
    A/B testing, and engagement optimization for the Live Dashboard Engagement System.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "learning_engine"
        
        # Core components
        self.behavior_analyzer = UserBehaviorAnalyzer()
        self.engagement_optimizer = EngagementOptimizer()
        self.feedback_processor = FeedbackProcessor()
        self.ab_test_manager = ABTestManager()
        
        # State management
        self.is_initialized = False
        self.learning_enabled = True
        self.optimization_interval = timedelta(hours=6)  # Optimize every 6 hours
        self.last_optimization = datetime.now()
        
        logger.info("Learning Engine initialized")
    
    async def initialize(self, observatory_core=None) -> bool:
        """Initialize the Learning Engine with Observatory integration."""
        try:
            # Store Observatory core reference
            self.observatory_core = observatory_core
            
            # Initialize learning components
            await self._initialize_learning_components()
            
            # Set up Observatory-specific learning patterns
            await self._setup_observatory_learning()
            
            self.is_initialized = True
            logger.info("Learning Engine initialization complete with Observatory integration")
            return True
            
        except Exception as e:
            logger.error(f"Learning Engine initialization failed: {e}")
            return False
    
    async def track_user_behavior(self, user_id: str, behavior_data: Dict[str, Any]) -> bool:
        """Track user behavior data."""
        if not self.learning_enabled:
            return False
        
        return await self.behavior_analyzer.track_user_behavior(user_id, behavior_data)
    
    async def analyze_engagement_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user engagement patterns."""
        return await self.behavior_analyzer.analyze_engagement_patterns(user_id)
    
    async def predict_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Predict user preferences based on behavior."""
        return await self.behavior_analyzer.predict_user_preferences(user_id)
    
    async def optimize_engagement_strategy(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize engagement strategy based on analytics."""
        return await self.engagement_optimizer.optimize_engagement_strategy(analytics_data)
    
    async def run_ab_test(self, test_config: Dict[str, Any]) -> str:
        """Run A/B test for engagement strategies."""
        return await self.ab_test_manager.create_ab_test(test_config)
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations."""
        return await self.engagement_optimizer.get_optimization_recommendations()
    
    async def process_user_feedback(self, user_id: str, feedback: Dict[str, Any]) -> bool:
        """Process user feedback and incorporate into learning models."""
        return await self.feedback_processor.process_user_feedback(user_id, feedback)
    
    async def get_feedback_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of user feedback data."""
        return await self.feedback_processor.get_feedback_summary(user_id)
    
    async def create_ab_test(self, test_config: Dict[str, Any]) -> str:
        """Create a new A/B test with given configuration."""
        return await self.ab_test_manager.create_ab_test(test_config)
    
    async def assign_user_to_variant(self, test_id: str, user_id: str) -> str:
        """Assign user to A/B test variant."""
        return await self.ab_test_manager.assign_user_to_variant(test_id, user_id)
    
    async def record_test_result(self, test_id: str, user_id: str, result: Dict[str, Any]) -> bool:
        """Record A/B test result for analysis."""
        return await self.ab_test_manager.record_test_result(test_id, user_id, result)
    
    async def analyze_test_results(self, test_id: str) -> Dict[str, Any]:
        """Analyze A/B test results and determine winner."""
        return await self.ab_test_manager.analyze_test_results(test_id)
    
    async def get_active_tests(self) -> List[Dict[str, Any]]:
        """Get list of currently active A/B tests."""
        return await self.ab_test_manager.get_active_tests()
    
    async def get_learning_analytics(self) -> Dict[str, Any]:
        """Get comprehensive learning analytics."""
        try:
            # Collect analytics from all components
            behavior_stats = await self._get_behavior_analytics()
            optimization_stats = await self._get_optimization_analytics()
            feedback_stats = await self._get_feedback_analytics()
            ab_test_stats = await self._get_ab_test_analytics()
            
            return {
                "learning_engine_status": "active" if self.learning_enabled else "disabled",
                "last_optimization": self.last_optimization.isoformat(),
                "next_optimization": (self.last_optimization + self.optimization_interval).isoformat(),
                "behavior_analytics": behavior_stats,
                "optimization_analytics": optimization_stats,
                "feedback_analytics": feedback_stats,
                "ab_test_analytics": ab_test_stats,
                "analytics_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Learning analytics generation failed: {e}")
            return {"error": str(e)}
    
    async def enable_learning(self) -> bool:
        """Enable learning and optimization."""
        try:
            self.learning_enabled = True
            logger.info("Learning Engine enabled")
            return True
        except Exception as e:
            logger.error(f"Learning enable failed: {e}")
            return False
    
    async def disable_learning(self) -> bool:
        """Disable learning and optimization."""
        try:
            self.learning_enabled = False
            logger.info("Learning Engine disabled")
            return True
        except Exception as e:
            logger.error(f"Learning disable failed: {e}")
            return False
    
    async def run_periodic_optimization(self) -> Dict[str, Any]:
        """Run periodic optimization if interval has passed."""
        try:
            if not self.learning_enabled:
                return {"status": "disabled", "message": "Learning is disabled"}
            
            now = datetime.now()
            if now - self.last_optimization < self.optimization_interval:
                return {
                    "status": "skipped",
                    "message": "Optimization interval not reached",
                    "next_optimization": (self.last_optimization + self.optimization_interval).isoformat()
                }
            
            # Run optimization
            analytics_data = await self.get_learning_analytics()
            optimization_result = await self.optimize_engagement_strategy(analytics_data)
            
            self.last_optimization = now
            
            return {
                "status": "completed",
                "optimization_result": optimization_result,
                "next_optimization": (now + self.optimization_interval).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Periodic optimization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _initialize_learning_components(self) -> None:
        """Initialize learning components."""
        # Initialize behavior analyzer with default patterns
        # Initialize optimizer with default strategies
        # Initialize feedback processor with default insights
        # Initialize A/B test manager with default configurations
        pass
    
    async def _setup_observatory_learning(self) -> None:
        """Set up Observatory-specific learning patterns."""
        # Set up learning patterns specific to Observatory engagement
        # Configure optimization strategies for Observatory metrics
        # Set up A/B testing for Observatory features
        pass
    
    async def _get_behavior_analytics(self) -> Dict[str, Any]:
        """Get behavior analytics summary."""
        try:
            total_users = len(self.behavior_analyzer.user_profiles)
            total_behaviors = len(self.behavior_analyzer.behavior_data)
            total_patterns = len(self.behavior_analyzer.engagement_patterns)
            
            return {
                "total_users_tracked": total_users,
                "total_behavior_records": total_behaviors,
                "identified_patterns": total_patterns,
                "active_user_profiles": total_users
            }
        except Exception as e:
            logger.error(f"Behavior analytics failed: {e}")
            return {}
    
    async def _get_optimization_analytics(self) -> Dict[str, Any]:
        """Get optimization analytics summary."""
        try:
            total_optimizations = len(self.engagement_optimizer.optimization_history)
            active_strategies = len(self.engagement_optimizer.current_strategies)
            
            return {
                "total_optimizations": total_optimizations,
                "active_strategies": active_strategies,
                "performance_metrics_tracked": len(self.engagement_optimizer.performance_metrics)
            }
        except Exception as e:
            logger.error(f"Optimization analytics failed: {e}")
            return {}
    
    async def _get_feedback_analytics(self) -> Dict[str, Any]:
        """Get feedback analytics summary."""
        try:
            total_feedback = len(self.feedback_processor.feedback_data)
            total_insights = len(self.feedback_processor.feedback_insights)
            
            return {
                "total_feedback_received": total_feedback,
                "insights_generated": total_insights
            }
        except Exception as e:
            logger.error(f"Feedback analytics failed: {e}")
            return {}
    
    async def _get_ab_test_analytics(self) -> Dict[str, Any]:
        """Get A/B test analytics summary."""
        try:
            total_tests = len(self.ab_test_manager.active_tests)
            active_tests = len([t for t in self.ab_test_manager.active_tests.values() if t.status == "active"])
            total_assignments = sum(len(assignments) for assignments in self.ab_test_manager.test_assignments.values())
            
            return {
                "total_tests_created": total_tests,
                "active_tests": active_tests,
                "total_user_assignments": total_assignments
            }
        except Exception as e:
            logger.error(f"A/B test analytics failed: {e}")
            return {}
    
    async def graceful_degradation(self) -> Dict[str, Any]:
        """Implement graceful degradation for the Learning Engine."""
        try:
            # Disable learning to reduce resource usage
            await self.disable_learning()
            
            # Clear non-essential data
            self.behavior_analyzer.behavior_data = self.behavior_analyzer.behavior_data[-100:]  # Keep last 100
            self.engagement_optimizer.optimization_history = self.engagement_optimizer.optimization_history[-10:]  # Keep last 10
            
            return {
                "status": "degraded",
                "message": "Learning Engine operating in degraded mode",
                "available_functions": [
                    "get_learning_analytics",
                    "get_feedback_summary", 
                    "get_active_tests"
                ],
                "disabled_functions": [
                    "track_user_behavior",
                    "optimize_engagement_strategy",
                    "run_ab_test"
                ]
            }
            
        except Exception as e:
            logger.error(f"Graceful degradation failed: {e}")
            return {"status": "error", "error": str(e)}