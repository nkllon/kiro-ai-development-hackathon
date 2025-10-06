"""
Personality Engine - Adaptive Dashboard Behavior and Emotional Intelligence
===========================================================================

The Personality Engine provides adaptive dashboard behavior with mood management,
emotional intelligence, and context-aware personality transitions.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .interfaces import (
    IPersonalityProvider, 
    IContextAnalyzer, 
    IThemeManager,
    EngagementContext,
    EngagementLevel
)

logger = logging.getLogger(__name__)


class PersonalityState(Enum):
    """Available personality states."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ENERGETIC = "energetic"
    CALM = "calm"
    FOCUSED = "focused"
    CELEBRATORY = "celebratory"
    ANALYTICAL = "analytical"


@dataclass
class PersonalityProfile:
    """Personality profile configuration."""
    current_state: PersonalityState = PersonalityState.PROFESSIONAL
    energy_level: float = 0.5  # 0.0 to 1.0
    formality_level: float = 0.7  # 0.0 to 1.0
    responsiveness: float = 0.8  # 0.0 to 1.0
    visual_intensity: float = 0.5  # 0.0 to 1.0
    last_transition: datetime = field(default_factory=datetime.now)


@dataclass
class EmotionalContext:
    """Emotional context and team state information."""
    team_stress_level: float = 0.5  # 0.0 to 1.0
    team_morale: float = 0.7  # 0.0 to 1.0
    recent_achievements: List[Dict[str, Any]] = field(default_factory=list)
    error_frequency: float = 0.0  # errors per hour
    workload_intensity: float = 0.5  # 0.0 to 1.0
    collaboration_activity: float = 0.5  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UserPreferences:
    """User preferences for personality customization."""
    preferred_personality_states: List[str] = field(default_factory=lambda: ["professional"])
    preferred_themes: List[str] = field(default_factory=lambda: ["professional"])
    visual_intensity_preference: float = 0.5  # 0.0 to 1.0
    animation_speed_preference: str = "normal"  # slow, normal, fast
    celebration_level_preference: str = "moderate"  # minor, moderate, major
    stress_response_preference: str = "calm"  # calm, focused, professional
    morale_boost_preference: str = "energetic"  # energetic, friendly, celebratory
    auto_adaptation_enabled: bool = True
    learning_enabled: bool = True
    last_updated: datetime = field(default_factory=datetime.now)


class UserPreferenceManager:
    """Manages user preferences and learning for personality customization."""
    
    def __init__(self):
        self.user_preferences: Dict[str, UserPreferences] = {}
        self.interaction_history: Dict[str, List[Dict[str, Any]]] = {}
        self.preference_learning_data: Dict[str, Dict[str, float]] = {}
        
    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences, creating defaults if not found."""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreferences()
        return self.user_preferences[user_id]
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences with new settings."""
        try:
            user_prefs = await self.get_user_preferences(user_id)
            
            # Update preferences
            if "preferred_personality_states" in preferences:
                user_prefs.preferred_personality_states = preferences["preferred_personality_states"]
            if "preferred_themes" in preferences:
                user_prefs.preferred_themes = preferences["preferred_themes"]
            if "visual_intensity_preference" in preferences:
                user_prefs.visual_intensity_preference = preferences["visual_intensity_preference"]
            if "animation_speed_preference" in preferences:
                user_prefs.animation_speed_preference = preferences["animation_speed_preference"]
            if "celebration_level_preference" in preferences:
                user_prefs.celebration_level_preference = preferences["celebration_level_preference"]
            if "stress_response_preference" in preferences:
                user_prefs.stress_response_preference = preferences["stress_response_preference"]
            if "morale_boost_preference" in preferences:
                user_prefs.morale_boost_preference = preferences["morale_boost_preference"]
            if "auto_adaptation_enabled" in preferences:
                user_prefs.auto_adaptation_enabled = preferences["auto_adaptation_enabled"]
            if "learning_enabled" in preferences:
                user_prefs.learning_enabled = preferences["learning_enabled"]
            
            user_prefs.last_updated = datetime.now()
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            return False
    
    async def learn_from_interaction(self, user_id: str, interaction_data: Dict[str, Any]) -> None:
        """Learn user preferences from their interactions."""
        try:
            user_prefs = await self.get_user_preferences(user_id)
            
            if not user_prefs.learning_enabled:
                return
            
            # Initialize learning data for user if not exists
            if user_id not in self.preference_learning_data:
                self.preference_learning_data[user_id] = {
                    "personality_satisfaction": {},
                    "theme_satisfaction": {},
                    "interaction_patterns": {}
                }
            
            learning_data = self.preference_learning_data[user_id]
            
            # Record interaction
            if user_id not in self.interaction_history:
                self.interaction_history[user_id] = []
            
            interaction_record = {
                "timestamp": datetime.now().isoformat(),
                "personality_state": interaction_data.get("personality_state"),
                "theme": interaction_data.get("theme"),
                "user_satisfaction": interaction_data.get("user_satisfaction", 0.5),
                "interaction_duration": interaction_data.get("interaction_duration", 0),
                "engagement_level": interaction_data.get("engagement_level", "active")
            }
            
            self.interaction_history[user_id].append(interaction_record)
            
            # Learn personality preferences
            personality_state = interaction_data.get("personality_state")
            satisfaction = interaction_data.get("user_satisfaction", 0.5)
            
            if personality_state:
                if personality_state not in learning_data["personality_satisfaction"]:
                    learning_data["personality_satisfaction"][personality_state] = []
                learning_data["personality_satisfaction"][personality_state].append(satisfaction)
                
                # Update preferred personality states based on satisfaction
                await self._update_personality_preferences(user_id, learning_data["personality_satisfaction"])
            
            # Learn theme preferences
            theme = interaction_data.get("theme")
            if theme:
                if theme not in learning_data["theme_satisfaction"]:
                    learning_data["theme_satisfaction"][theme] = []
                learning_data["theme_satisfaction"][theme].append(satisfaction)
                
                # Update preferred themes based on satisfaction
                await self._update_theme_preferences(user_id, learning_data["theme_satisfaction"])
            
            # Learn interaction patterns
            engagement_level = interaction_data.get("engagement_level", "active")
            duration = interaction_data.get("interaction_duration", 0)
            
            if engagement_level not in learning_data["interaction_patterns"]:
                learning_data["interaction_patterns"][engagement_level] = []
            learning_data["interaction_patterns"][engagement_level].append(duration)
            
        except Exception as e:
            logger.error(f"Learning from interaction failed: {e}")
    
    async def get_personalized_recommendations(self, user_id: str, context: EngagementContext) -> Dict[str, Any]:
        """Get personalized personality and theme recommendations."""
        try:
            user_prefs = await self.get_user_preferences(user_id)
            
            # Start with user's preferred personality states
            personality_recommendations = user_prefs.preferred_personality_states.copy()
            theme_recommendations = user_prefs.preferred_themes.copy()
            
            # Adjust based on context if auto-adaptation is enabled
            if user_prefs.auto_adaptation_enabled:
                # High stress - prefer user's stress response preference
                if context.system_load > 0.7:
                    if user_prefs.stress_response_preference not in personality_recommendations:
                        personality_recommendations.insert(0, user_prefs.stress_response_preference)
                
                # Low engagement - prefer energetic options
                if context.engagement_level == EngagementLevel.PASSIVE:
                    if user_prefs.morale_boost_preference not in personality_recommendations:
                        personality_recommendations.insert(0, user_prefs.morale_boost_preference)
            
            # Apply learning data if available
            if user_id in self.preference_learning_data:
                learning_data = self.preference_learning_data[user_id]
                
                # Sort by satisfaction scores
                personality_scores = learning_data.get("personality_satisfaction", {})
                if personality_scores:
                    sorted_personalities = sorted(
                        personality_scores.items(),
                        key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
                        reverse=True
                    )
                    learned_personalities = [p[0] for p in sorted_personalities[:3]]
                    
                    # Merge with preferences, prioritizing learned preferences
                    personality_recommendations = learned_personalities + [
                        p for p in personality_recommendations if p not in learned_personalities
                    ]
                
                # Same for themes
                theme_scores = learning_data.get("theme_satisfaction", {})
                if theme_scores:
                    sorted_themes = sorted(
                        theme_scores.items(),
                        key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
                        reverse=True
                    )
                    learned_themes = [t[0] for t in sorted_themes[:3]]
                    
                    theme_recommendations = learned_themes + [
                        t for t in theme_recommendations if t not in learned_themes
                    ]
            
            return {
                "personality_recommendations": personality_recommendations[:5],  # Top 5
                "theme_recommendations": theme_recommendations[:5],  # Top 5
                "visual_intensity": user_prefs.visual_intensity_preference,
                "animation_speed": user_prefs.animation_speed_preference,
                "celebration_level": user_prefs.celebration_level_preference,
                "auto_adaptation": user_prefs.auto_adaptation_enabled,
                "learning_enabled": user_prefs.learning_enabled
            }
            
        except Exception as e:
            logger.error(f"Personalized recommendations failed: {e}")
            return {
                "personality_recommendations": ["professional"],
                "theme_recommendations": ["professional"],
                "visual_intensity": 0.5,
                "animation_speed": "normal",
                "celebration_level": "moderate"
            }
    
    async def get_learning_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics about user preference learning."""
        try:
            if user_id not in self.preference_learning_data:
                return {"status": "no_learning_data"}
            
            learning_data = self.preference_learning_data[user_id]
            interaction_count = len(self.interaction_history.get(user_id, []))
            
            # Calculate personality satisfaction averages
            personality_satisfaction = {}
            for personality, scores in learning_data.get("personality_satisfaction", {}).items():
                if scores:
                    personality_satisfaction[personality] = {
                        "average_satisfaction": sum(scores) / len(scores),
                        "interaction_count": len(scores)
                    }
            
            # Calculate theme satisfaction averages
            theme_satisfaction = {}
            for theme, scores in learning_data.get("theme_satisfaction", {}).items():
                if scores:
                    theme_satisfaction[theme] = {
                        "average_satisfaction": sum(scores) / len(scores),
                        "interaction_count": len(scores)
                    }
            
            # Calculate engagement patterns
            engagement_patterns = {}
            for engagement, durations in learning_data.get("interaction_patterns", {}).items():
                if durations:
                    engagement_patterns[engagement] = {
                        "average_duration": sum(durations) / len(durations),
                        "session_count": len(durations)
                    }
            
            return {
                "total_interactions": interaction_count,
                "personality_satisfaction": personality_satisfaction,
                "theme_satisfaction": theme_satisfaction,
                "engagement_patterns": engagement_patterns,
                "learning_confidence": min(interaction_count / 50.0, 1.0),  # Confidence based on interaction count
                "most_preferred_personality": max(personality_satisfaction.items(), 
                                                key=lambda x: x[1]["average_satisfaction"])[0] if personality_satisfaction else None,
                "most_preferred_theme": max(theme_satisfaction.items(), 
                                          key=lambda x: x[1]["average_satisfaction"])[0] if theme_satisfaction else None
            }
            
        except Exception as e:
            logger.error(f"Learning analytics failed: {e}")
            return {"error": str(e)}
    
    async def _update_personality_preferences(self, user_id: str, satisfaction_data: Dict[str, List[float]]) -> None:
        """Update user's preferred personality states based on satisfaction data."""
        try:
            # Calculate average satisfaction for each personality
            avg_satisfaction = {}
            for personality, scores in satisfaction_data.items():
                if scores and len(scores) >= 3:  # Need at least 3 interactions to learn
                    avg_satisfaction[personality] = sum(scores) / len(scores)
            
            if avg_satisfaction:
                # Sort by satisfaction and update preferences
                sorted_personalities = sorted(
                    avg_satisfaction.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Update top 3 preferred personalities
                user_prefs = await self.get_user_preferences(user_id)
                user_prefs.preferred_personality_states = [p[0] for p in sorted_personalities[:3]]
                user_prefs.last_updated = datetime.now()
                
        except Exception as e:
            logger.error(f"Failed to update personality preferences: {e}")
    
    async def _update_theme_preferences(self, user_id: str, satisfaction_data: Dict[str, List[float]]) -> None:
        """Update user's preferred themes based on satisfaction data."""
        try:
            # Calculate average satisfaction for each theme
            avg_satisfaction = {}
            for theme, scores in satisfaction_data.items():
                if scores and len(scores) >= 3:  # Need at least 3 interactions to learn
                    avg_satisfaction[theme] = sum(scores) / len(scores)
            
            if avg_satisfaction:
                # Sort by satisfaction and update preferences
                sorted_themes = sorted(
                    avg_satisfaction.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Update top 3 preferred themes
                user_prefs = await self.get_user_preferences(user_id)
                user_prefs.preferred_themes = [t[0] for t in sorted_themes[:3]]
                user_prefs.last_updated = datetime.now()
                
        except Exception as e:
            logger.error(f"Failed to update theme preferences: {e}")


class EmotionalIntelligenceEngine:
    """Engine for monitoring team stress, morale, and emotional context."""
    
    def __init__(self):
        self.emotional_history: List[EmotionalContext] = []
        self.achievements: List[Dict[str, Any]] = []
        self.stress_indicators: Dict[str, float] = {}
        self.morale_indicators: Dict[str, float] = {}
        
    async def monitor_team_stress(self, system_metrics: Dict[str, Any]) -> float:
        """Monitor and calculate team stress level based on system metrics."""
        try:
            stress_factors = []
            
            # High error rate increases stress
            error_rate = system_metrics.get("error_rate", 0.0)
            if error_rate > 0.05:
                stress_factors.append(min(error_rate * 10, 1.0))
            
            # High system load increases stress
            system_load = system_metrics.get("system_load", 0.5)
            if system_load > 0.8:
                stress_factors.append((system_load - 0.8) * 5)
            
            # Long response times increase stress
            response_time = system_metrics.get("response_time_ms", 100)
            if response_time > 1000:
                stress_factors.append(min((response_time - 1000) / 5000, 1.0))
            
            # Calculate overall stress level
            if stress_factors:
                stress_level = min(sum(stress_factors) / len(stress_factors), 1.0)
            else:
                stress_level = 0.2  # Baseline stress
            
            # Store stress indicators
            self.stress_indicators.update({
                "error_rate_stress": error_rate * 10,
                "system_load_stress": max(0, (system_load - 0.8) * 5),
                "response_time_stress": min((response_time - 1000) / 5000, 1.0) if response_time > 1000 else 0,
                "overall_stress": stress_level
            })
            
            return stress_level
            
        except Exception as e:
            logger.error(f"Team stress monitoring failed: {e}")
            return 0.5  # Default moderate stress
    
    async def monitor_team_morale(self, activity_metrics: Dict[str, Any]) -> float:
        """Monitor and calculate team morale based on activity metrics."""
        try:
            morale_factors = []
            
            # Recent achievements boost morale
            recent_achievements = len([a for a in self.achievements 
                                    if (datetime.now() - datetime.fromisoformat(a["timestamp"])).days < 7])
            if recent_achievements > 0:
                morale_factors.append(min(recent_achievements * 0.2, 0.5))
            
            # Stable system performance boosts morale
            uptime = activity_metrics.get("uptime_hours", 24)
            if uptime > 48:
                morale_factors.append(0.3)
            
            # Active collaboration boosts morale
            active_users = activity_metrics.get("active_users", 1)
            if active_users > 2:
                morale_factors.append(min(active_users * 0.1, 0.4))
            
            # Low error rates boost morale
            error_rate = activity_metrics.get("error_rate", 0.0)
            if error_rate < 0.01:
                morale_factors.append(0.3)
            
            # Calculate overall morale
            base_morale = 0.6  # Baseline morale
            if morale_factors:
                morale_boost = sum(morale_factors)
                morale_level = min(base_morale + morale_boost, 1.0)
            else:
                morale_level = base_morale
            
            # Store morale indicators
            self.morale_indicators.update({
                "achievement_morale": min(recent_achievements * 0.2, 0.5),
                "stability_morale": 0.3 if uptime > 48 else 0,
                "collaboration_morale": min(active_users * 0.1, 0.4),
                "performance_morale": 0.3 if error_rate < 0.01 else 0,
                "overall_morale": morale_level
            })
            
            return morale_level
            
        except Exception as e:
            logger.error(f"Team morale monitoring failed: {e}")
            return 0.7  # Default good morale
    
    async def recognize_achievement(self, achievement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recognize and celebrate team achievements."""
        try:
            achievement = {
                "id": f"achievement_{len(self.achievements) + 1}",
                "type": achievement_data.get("type", "milestone"),
                "description": achievement_data.get("description", "Team achievement"),
                "significance": achievement_data.get("significance", "medium"),  # low, medium, high
                "timestamp": datetime.now().isoformat(),
                "celebration_level": self._calculate_celebration_level(achievement_data),
                "team_impact": achievement_data.get("team_impact", "positive")
            }
            
            self.achievements.append(achievement)
            
            # Generate celebration response
            celebration_response = await self._generate_celebration_response(achievement)
            
            logger.info(f"Achievement recognized: {achievement['description']}")
            
            return {
                "achievement": achievement,
                "celebration": celebration_response,
                "morale_impact": 0.2 * (1.0 if achievement["significance"] == "high" else 
                                     0.7 if achievement["significance"] == "medium" else 0.4)
            }
            
        except Exception as e:
            logger.error(f"Achievement recognition failed: {e}")
            return {"error": str(e)}
    
    async def get_adaptive_response_strategy(self, emotional_context: EmotionalContext) -> Dict[str, Any]:
        """Get adaptive response strategy based on emotional context."""
        try:
            strategy = {
                "response_type": "balanced",
                "personality_recommendation": "professional",
                "theme_recommendation": "professional",
                "interaction_style": "standard",
                "support_actions": [],
                "celebration_actions": []
            }
            
            # High stress response
            if emotional_context.team_stress_level > 0.7:
                strategy.update({
                    "response_type": "stress_reduction",
                    "personality_recommendation": "calm",
                    "theme_recommendation": "calm",
                    "interaction_style": "supportive",
                    "support_actions": [
                        "reduce_visual_intensity",
                        "simplify_interface",
                        "provide_calming_animations",
                        "highlight_positive_metrics"
                    ]
                })
            
            # Low morale response
            elif emotional_context.team_morale < 0.4:
                strategy.update({
                    "response_type": "morale_boost",
                    "personality_recommendation": "friendly",
                    "theme_recommendation": "energetic",
                    "interaction_style": "encouraging",
                    "support_actions": [
                        "highlight_achievements",
                        "show_progress_indicators",
                        "provide_motivational_messages",
                        "celebrate_small_wins"
                    ]
                })
            
            # High morale and low stress - celebration mode
            elif emotional_context.team_morale > 0.8 and emotional_context.team_stress_level < 0.3:
                strategy.update({
                    "response_type": "celebration",
                    "personality_recommendation": "celebratory",
                    "theme_recommendation": "celebratory",
                    "interaction_style": "enthusiastic",
                    "celebration_actions": [
                        "show_achievement_animations",
                        "display_success_metrics",
                        "provide_congratulatory_messages",
                        "enhance_visual_effects"
                    ]
                })
            
            # Recent achievements - recognition mode
            elif len(emotional_context.recent_achievements) > 0:
                strategy.update({
                    "response_type": "achievement_recognition",
                    "personality_recommendation": "celebratory",
                    "theme_recommendation": "celebratory",
                    "interaction_style": "appreciative",
                    "celebration_actions": [
                        "highlight_recent_achievements",
                        "show_milestone_progress",
                        "provide_recognition_animations"
                    ]
                })
            
            return strategy
            
        except Exception as e:
            logger.error(f"Adaptive response strategy failed: {e}")
            return {"response_type": "error", "error": str(e)}
    
    async def get_emotional_analytics(self) -> Dict[str, Any]:
        """Get emotional intelligence analytics and insights."""
        try:
            recent_context = self.emotional_history[-1] if self.emotional_history else None
            
            return {
                "current_emotional_state": {
                    "team_stress_level": recent_context.team_stress_level if recent_context else 0.5,
                    "team_morale": recent_context.team_morale if recent_context else 0.7,
                    "emotional_balance": self._calculate_emotional_balance(recent_context) if recent_context else 0.6
                },
                "stress_indicators": self.stress_indicators,
                "morale_indicators": self.morale_indicators,
                "recent_achievements": self.achievements[-5:],  # Last 5 achievements
                "emotional_trends": await self._analyze_emotional_trends(),
                "support_recommendations": await self._get_support_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Emotional analytics failed: {e}")
            return {"error": str(e)}
    
    def _calculate_celebration_level(self, achievement_data: Dict[str, Any]) -> str:
        """Calculate appropriate celebration level for achievement."""
        significance = achievement_data.get("significance", "medium")
        team_impact = achievement_data.get("team_impact", "positive")
        
        if significance == "high" and team_impact == "positive":
            return "major"
        elif significance == "medium":
            return "moderate"
        else:
            return "minor"
    
    async def _generate_celebration_response(self, achievement: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate celebration response for achievement."""
        celebration_level = achievement["celebration_level"]
        
        responses = {
            "major": {
                "message": f"🎉 Outstanding achievement: {achievement['description']}!",
                "animation": "fireworks",
                "duration": 5000,
                "visual_intensity": 1.0
            },
            "moderate": {
                "message": f"✨ Great work: {achievement['description']}!",
                "animation": "sparkles",
                "duration": 3000,
                "visual_intensity": 0.7
            },
            "minor": {
                "message": f"👍 Nice: {achievement['description']}",
                "animation": "gentle_glow",
                "duration": 2000,
                "visual_intensity": 0.4
            }
        }
        
        return responses.get(celebration_level, responses["minor"])
    
    def _calculate_emotional_balance(self, context: EmotionalContext) -> float:
        """Calculate overall emotional balance score."""
        if not context:
            return 0.6
        
        # Balance is good when morale is high and stress is low
        balance = (context.team_morale * 0.6) + ((1.0 - context.team_stress_level) * 0.4)
        return min(max(balance, 0.0), 1.0)
    
    async def _analyze_emotional_trends(self) -> Dict[str, Any]:
        """Analyze emotional trends over time."""
        if len(self.emotional_history) < 2:
            return {"trend": "insufficient_data"}
        
        recent = self.emotional_history[-5:]  # Last 5 entries
        
        stress_trend = "stable"
        morale_trend = "stable"
        
        if len(recent) >= 2:
            stress_change = recent[-1].team_stress_level - recent[0].team_stress_level
            morale_change = recent[-1].team_morale - recent[0].team_morale
            
            stress_trend = "increasing" if stress_change > 0.1 else "decreasing" if stress_change < -0.1 else "stable"
            morale_trend = "increasing" if morale_change > 0.1 else "decreasing" if morale_change < -0.1 else "stable"
        
        return {
            "stress_trend": stress_trend,
            "morale_trend": morale_trend,
            "emotional_stability": "stable" if stress_trend == "stable" and morale_trend == "stable" else "changing"
        }
    
    async def _get_support_recommendations(self) -> List[str]:
        """Get recommendations for supporting team emotional well-being."""
        recommendations = []
        
        if self.stress_indicators.get("overall_stress", 0.5) > 0.6:
            recommendations.extend([
                "Consider reducing visual complexity",
                "Implement calming color schemes",
                "Provide stress-reduction features"
            ])
        
        if self.morale_indicators.get("overall_morale", 0.7) < 0.5:
            recommendations.extend([
                "Highlight recent achievements",
                "Show progress indicators",
                "Implement motivational features"
            ])
        
        if len(self.achievements) == 0:
            recommendations.append("Set up achievement recognition system")
        
        return recommendations


class PersonalityProvider(IPersonalityProvider):
    """Implementation of personality states and transitions."""
    
    def __init__(self):
        self.current_profile = PersonalityProfile()
        self.personality_history: List[Dict[str, Any]] = []
        
    async def get_current_personality(self) -> Dict[str, Any]:
        """Get current personality state."""
        return {
            "state": self.current_profile.current_state.value,
            "energy_level": self.current_profile.energy_level,
            "formality_level": self.current_profile.formality_level,
            "responsiveness": self.current_profile.responsiveness,
            "visual_intensity": self.current_profile.visual_intensity,
            "last_transition": self.current_profile.last_transition.isoformat()
        }
    
    async def transition_personality(self, new_state: str, context: EngagementContext) -> bool:
        """Transition to new personality state."""
        try:
            # Validate new state
            try:
                new_personality_state = PersonalityState(new_state)
            except ValueError:
                logger.warning(f"Invalid personality state: {new_state}")
                return False
            
            # Record transition
            old_state = self.current_profile.current_state
            self.personality_history.append({
                "from_state": old_state.value,
                "to_state": new_state,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "engagement_level": context.engagement_level.value,
                    "session_duration": context.session_duration,
                    "system_load": context.system_load
                }
            })
            
            # Apply transition
            self.current_profile.current_state = new_personality_state
            self.current_profile.last_transition = datetime.now()
            
            # Adjust personality parameters based on new state
            await self._adjust_personality_parameters(new_personality_state, context)
            
            logger.info(f"Personality transitioned: {old_state.value} -> {new_state}")
            return True
            
        except Exception as e:
            logger.error(f"Personality transition failed: {e}")
            return False
    
    async def get_personality_recommendations(self, context: EngagementContext) -> List[str]:
        """Get personality recommendations for given context."""
        recommendations = []
        
        try:
            # Analyze context for personality recommendations
            if context.system_load > 0.8:
                recommendations.append("calm")
                recommendations.append("focused")
            elif context.engagement_level == EngagementLevel.IMMERSIVE:
                recommendations.append("energetic")
                recommendations.append("friendly")
            elif context.session_duration > 3600:  # > 1 hour
                recommendations.append("celebratory")
                recommendations.append("energetic")
            else:
                recommendations.append("professional")
                recommendations.append("analytical")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get personality recommendations: {e}")
            return ["professional"]  # Safe default
    
    async def _adjust_personality_parameters(self, state: PersonalityState, context: EngagementContext) -> None:
        """Adjust personality parameters based on state and context."""
        if state == PersonalityState.ENERGETIC:
            self.current_profile.energy_level = 0.9
            self.current_profile.visual_intensity = 0.8
            self.current_profile.responsiveness = 0.9
        elif state == PersonalityState.CALM:
            self.current_profile.energy_level = 0.3
            self.current_profile.visual_intensity = 0.4
            self.current_profile.responsiveness = 0.6
        elif state == PersonalityState.PROFESSIONAL:
            self.current_profile.formality_level = 0.8
            self.current_profile.energy_level = 0.5
            self.current_profile.visual_intensity = 0.5
        elif state == PersonalityState.CELEBRATORY:
            self.current_profile.energy_level = 1.0
            self.current_profile.visual_intensity = 0.9
            self.current_profile.responsiveness = 1.0


class ThemeManager(IThemeManager):
    """Implementation of visual themes and moods based on system state."""
    
    def __init__(self):
        self.current_theme_name = "professional"
        self.current_theme_config = self._get_default_theme()
        self.theme_history: List[Dict[str, Any]] = []
        
        # Define available themes
        self.available_themes = {
            "professional": {
                "primary_color": "#2563eb",
                "secondary_color": "#64748b",
                "accent_color": "#0ea5e9",
                "background_color": "#f8fafc",
                "text_color": "#1e293b",
                "animation_speed": "normal",
                "visual_intensity": 0.5,
                "mood": "focused"
            },
            "energetic": {
                "primary_color": "#dc2626",
                "secondary_color": "#f59e0b",
                "accent_color": "#10b981",
                "background_color": "#fef3c7",
                "text_color": "#1f2937",
                "animation_speed": "fast",
                "visual_intensity": 0.9,
                "mood": "dynamic"
            },
            "calm": {
                "primary_color": "#059669",
                "secondary_color": "#6b7280",
                "accent_color": "#3b82f6",
                "background_color": "#f0fdf4",
                "text_color": "#374151",
                "animation_speed": "slow",
                "visual_intensity": 0.3,
                "mood": "serene"
            },
            "celebratory": {
                "primary_color": "#7c3aed",
                "secondary_color": "#f59e0b",
                "accent_color": "#ec4899",
                "background_color": "#fdf4ff",
                "text_color": "#581c87",
                "animation_speed": "very_fast",
                "visual_intensity": 1.0,
                "mood": "joyful"
            },
            "analytical": {
                "primary_color": "#475569",
                "secondary_color": "#94a3b8",
                "accent_color": "#0ea5e9",
                "background_color": "#f1f5f9",
                "text_color": "#334155",
                "animation_speed": "slow",
                "visual_intensity": 0.4,
                "mood": "contemplative"
            }
        }
    
    async def get_current_theme(self) -> Dict[str, Any]:
        """Get current visual theme configuration."""
        return {
            "theme_name": self.current_theme_name,
            "config": self.current_theme_config.copy(),
            "applied_at": datetime.now().isoformat()
        }
    
    async def apply_theme(self, theme_name: str, context: EngagementContext) -> bool:
        """Apply visual theme based on personality and context."""
        try:
            if theme_name not in self.available_themes:
                logger.warning(f"Unknown theme: {theme_name}")
                return False
            
            # Record theme change
            old_theme = self.current_theme_name
            self.theme_history.append({
                "from_theme": old_theme,
                "to_theme": theme_name,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "engagement_level": context.engagement_level.value,
                    "system_load": context.system_load,
                    "user_id": context.user_id
                }
            })
            
            # Apply new theme
            self.current_theme_name = theme_name
            self.current_theme_config = self.available_themes[theme_name].copy()
            
            # Adjust theme based on context
            await self._adjust_theme_for_context(context)
            
            logger.info(f"Theme applied: {old_theme} -> {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"Theme application failed: {e}")
            return False
    
    async def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        return list(self.available_themes.keys())
    
    async def create_dynamic_theme(self, personality_state: str, system_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create dynamic theme based on personality and system state."""
        try:
            # Start with base theme for personality
            base_theme_map = {
                "professional": "professional",
                "friendly": "professional",
                "energetic": "energetic",
                "calm": "calm",
                "focused": "analytical",
                "celebratory": "celebratory",
                "analytical": "analytical"
            }
            
            base_theme_name = base_theme_map.get(personality_state, "professional")
            dynamic_theme = self.available_themes[base_theme_name].copy()
            
            # Adjust based on system context
            system_load = system_context.get("system_load", 0.5)
            error_rate = system_context.get("error_rate", 0.0)
            
            # High system load - reduce visual intensity
            if system_load > 0.8:
                dynamic_theme["visual_intensity"] *= 0.7
                dynamic_theme["animation_speed"] = "slow"
            
            # High error rate - add warning indicators
            if error_rate > 0.1:
                dynamic_theme["accent_color"] = "#f59e0b"  # Warning orange
                dynamic_theme["visual_intensity"] = min(dynamic_theme["visual_intensity"] * 1.2, 1.0)
            
            return {
                "theme_name": f"dynamic_{personality_state}",
                "config": dynamic_theme,
                "base_theme": base_theme_name,
                "adjustments": {
                    "system_load_factor": system_load,
                    "error_rate_factor": error_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Dynamic theme creation failed: {e}")
            return await self.get_current_theme()
    
    def _get_default_theme(self) -> Dict[str, Any]:
        """Get default professional theme."""
        return {
            "primary_color": "#2563eb",
            "secondary_color": "#64748b",
            "accent_color": "#0ea5e9",
            "background_color": "#f8fafc",
            "text_color": "#1e293b",
            "animation_speed": "normal",
            "visual_intensity": 0.5,
            "mood": "focused"
        }
    
    async def _adjust_theme_for_context(self, context: EngagementContext) -> None:
        """Adjust current theme based on engagement context."""
        # Adjust visual intensity based on engagement level
        if context.engagement_level == EngagementLevel.IMMERSIVE:
            self.current_theme_config["visual_intensity"] = min(
                self.current_theme_config["visual_intensity"] * 1.3, 1.0
            )
        elif context.engagement_level == EngagementLevel.PASSIVE:
            self.current_theme_config["visual_intensity"] *= 0.8
        
        # Adjust animation speed based on system load
        if context.system_load > 0.8:
            self.current_theme_config["animation_speed"] = "slow"
        elif context.system_load < 0.3:
            self.current_theme_config["animation_speed"] = "fast"


class ContextAnalyzer(IContextAnalyzer):
    """Implementation of system and user context analysis."""
    
    def __init__(self):
        self.context_history: List[EngagementContext] = []
        
    async def analyze_user_context(self, user_id: str) -> EngagementContext:
        """Analyze current user context."""
        try:
            # Placeholder user context analysis
            # In a real implementation, this would analyze user behavior, preferences, etc.
            context = EngagementContext(
                user_id=user_id,
                session_duration=0.0,  # Would be calculated from session start
                interaction_count=0,   # Would be tracked from user interactions
                current_focus=None,    # Would be determined from UI state
                engagement_level=EngagementLevel.ACTIVE,
                system_load=0.5,       # Would be measured from system metrics
                data_freshness=1.0     # Would be calculated from data timestamps
            )
            
            self.context_history.append(context)
            return context
            
        except Exception as e:
            logger.error(f"User context analysis failed: {e}")
            # Return safe default context
            return EngagementContext(
                user_id=user_id,
                engagement_level=EngagementLevel.PASSIVE
            )
    
    async def analyze_system_context(self) -> Dict[str, Any]:
        """Analyze current system context."""
        try:
            return {
                "system_load": 0.5,
                "memory_usage": 0.6,
                "active_users": 1,
                "data_freshness": 1.0,
                "error_rate": 0.0,
                "response_time_ms": 100,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"System context analysis failed: {e}")
            return {"error": str(e)}
    
    async def predict_engagement_needs(self, context: EngagementContext) -> List[str]:
        """Predict engagement needs based on context."""
        needs = []
        
        try:
            # Analyze context for engagement needs
            if context.engagement_level == EngagementLevel.PASSIVE:
                needs.append("attention_grabbing_animations")
                needs.append("interactive_elements")
            elif context.engagement_level == EngagementLevel.IMMERSIVE:
                needs.append("detailed_information_layers")
                needs.append("advanced_visualizations")
            
            if context.session_duration > 1800:  # > 30 minutes
                needs.append("achievement_recognition")
                needs.append("progress_celebration")
            
            if context.system_load > 0.7:
                needs.append("performance_optimization")
                needs.append("simplified_interface")
            
            return needs
            
        except Exception as e:
            logger.error(f"Engagement needs prediction failed: {e}")
            return []


class PersonalityEngine(ReflectiveModule):
    """
    Main Personality Engine that provides adaptive dashboard behavior
    with mood management and emotional intelligence.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "personality_engine"
        
        # Core components
        self.personality_provider = PersonalityProvider()
        self.context_analyzer = ContextAnalyzer()
        self.theme_manager = ThemeManager()
        self.emotional_intelligence = EmotionalIntelligenceEngine()
        self.preference_manager = UserPreferenceManager()
        
        # State management
        self.is_initialized = False
        self.active_contexts: Dict[str, EngagementContext] = {}
        
        logger.info("Personality Engine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Personality Engine."""
        try:
            # Initialize with default professional personality
            default_context = EngagementContext(
                user_id="system",
                engagement_level=EngagementLevel.ACTIVE
            )
            
            await self.personality_provider.transition_personality(
                PersonalityState.PROFESSIONAL.value, 
                default_context
            )
            
            self.is_initialized = True
            logger.info("Personality Engine initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Personality Engine initialization failed: {e}")
            return False
    
    async def adapt_to_context(self, user_id: str) -> Dict[str, Any]:
        """Adapt personality to current user context."""
        try:
            # Analyze current context
            context = await self.context_analyzer.analyze_user_context(user_id)
            self.active_contexts[user_id] = context
            
            # Get personality recommendations
            recommendations = await self.personality_provider.get_personality_recommendations(context)
            
            # Apply best recommendation if different from current
            current_personality = await self.personality_provider.get_current_personality()
            if recommendations and recommendations[0] != current_personality["state"]:
                await self.personality_provider.transition_personality(recommendations[0], context)
                
                # Update theme to match new personality
                await self.theme_manager.apply_theme(recommendations[0], context)
            
            # Predict engagement needs
            engagement_needs = await self.context_analyzer.predict_engagement_needs(context)
            
            # Get current theme
            current_theme = await self.theme_manager.get_current_theme()
            
            return {
                "user_id": user_id,
                "context": {
                    "engagement_level": context.engagement_level.value,
                    "session_duration": context.session_duration,
                    "system_load": context.system_load
                },
                "personality": await self.personality_provider.get_current_personality(),
                "theme": current_theme,
                "recommendations": recommendations,
                "engagement_needs": engagement_needs
            }
            
        except Exception as e:
            logger.error(f"Context adaptation failed: {e}")
            return {"error": str(e)}
    
    async def apply_mood_theme(self, mood: str, context: EngagementContext) -> Dict[str, Any]:
        """Apply visual theme based on mood and context."""
        try:
            # Map mood to personality state for theme selection
            mood_to_personality = {
                "happy": "celebratory",
                "focused": "analytical", 
                "energetic": "energetic",
                "calm": "calm",
                "professional": "professional",
                "excited": "energetic",
                "contemplative": "analytical"
            }
            
            personality_state = mood_to_personality.get(mood, "professional")
            
            # Apply theme
            theme_applied = await self.theme_manager.apply_theme(personality_state, context)
            
            if theme_applied:
                # Also transition personality to match
                await self.personality_provider.transition_personality(personality_state, context)
            
            return {
                "mood": mood,
                "personality_state": personality_state,
                "theme_applied": theme_applied,
                "current_theme": await self.theme_manager.get_current_theme(),
                "current_personality": await self.personality_provider.get_current_personality()
            }
            
        except Exception as e:
            logger.error(f"Mood theme application failed: {e}")
            return {"error": str(e)}
    
    async def get_mood_recommendations(self, system_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get mood and theme recommendations based on system context."""
        try:
            recommendations = []
            
            system_load = system_context.get("system_load", 0.5)
            error_rate = system_context.get("error_rate", 0.0)
            active_users = system_context.get("active_users", 1)
            
            # Monitor emotional intelligence factors
            stress_level = await self.emotional_intelligence.monitor_team_stress(system_context)
            morale_level = await self.emotional_intelligence.monitor_team_morale(system_context)
            
            # High stress - calming mood
            if stress_level > 0.7:
                recommendations.append({
                    "mood": "calm",
                    "reason": f"High team stress detected ({stress_level:.1f})",
                    "confidence": 0.9
                })
            
            # Low morale - energetic/supportive mood
            elif morale_level < 0.4:
                recommendations.append({
                    "mood": "energetic",
                    "reason": f"Low team morale detected ({morale_level:.1f})",
                    "confidence": 0.85
                })
            
            # High morale and low stress - celebratory mood
            elif morale_level > 0.8 and stress_level < 0.3:
                recommendations.append({
                    "mood": "celebratory",
                    "reason": "High morale and low stress - time to celebrate!",
                    "confidence": 0.95
                })
            
            # High performance - celebratory mood
            elif system_load < 0.3 and error_rate < 0.01:
                recommendations.append({
                    "mood": "celebratory",
                    "reason": "System performing excellently",
                    "confidence": 0.9
                })
            
            # High load - focused mood
            elif system_load > 0.7:
                recommendations.append({
                    "mood": "focused",
                    "reason": "High system load requires attention",
                    "confidence": 0.8
                })
            
            # Errors present - professional mood
            elif error_rate > 0.05:
                recommendations.append({
                    "mood": "professional",
                    "reason": "Errors detected, maintaining professional focus",
                    "confidence": 0.85
                })
            
            # Multiple users - energetic mood
            elif active_users > 3:
                recommendations.append({
                    "mood": "energetic",
                    "reason": "High user activity, maintaining engagement",
                    "confidence": 0.7
                })
            
            # Default calm mood if no specific conditions
            else:
                recommendations.append({
                    "mood": "calm",
                    "reason": "Stable system conditions",
                    "confidence": 0.6
                })
            
            return sorted(recommendations, key=lambda x: x["confidence"], reverse=True)
            
        except Exception as e:
            logger.error(f"Mood recommendations failed: {e}")
            return [{"mood": "professional", "reason": "Error in analysis", "confidence": 0.5}]
    
    async def manage_personality_state_transitions(self, trigger_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage personality state transitions based on system conditions.
        
        This is the core personality state management system that handles:
        - Automatic transitions based on system conditions
        - Smooth transitions between personality states
        - State validation and rollback capabilities
        - Transition history tracking
        """
        try:
            current_personality = await self.personality_provider.get_current_personality()
            current_state = current_personality["state"]
            
            # Analyze trigger conditions to determine if transition is needed
            transition_analysis = await self._analyze_transition_triggers(trigger_conditions)
            
            if not transition_analysis["transition_needed"]:
                return {
                    "status": "no_transition_needed",
                    "current_state": current_state,
                    "analysis": transition_analysis,
                    "timestamp": datetime.now().isoformat()
                }
            
            target_state = transition_analysis["recommended_state"]
            transition_reason = transition_analysis["reason"]
            confidence = transition_analysis["confidence"]
            
            # Create context for transition
            context = EngagementContext(
                user_id=trigger_conditions.get("user_id", "system"),
                engagement_level=EngagementLevel.ACTIVE,
                system_load=trigger_conditions.get("system_load", 0.5)
            )
            
            # Execute personality state transition
            transition_result = await self.personality_provider.transition_personality(target_state, context)
            
            # Apply matching theme
            theme_result = await self.theme_manager.apply_theme(target_state, context)
            
            # Record transition in history
            transition_record = {
                "from_state": current_state,
                "to_state": target_state,
                "reason": transition_reason,
                "confidence": confidence,
                "trigger_conditions": trigger_conditions,
                "timestamp": datetime.now().isoformat(),
                "success": transition_result and theme_result
            }
            
            return {
                "status": "transition_completed" if transition_result else "transition_failed",
                "transition_record": transition_record,
                "new_personality": await self.personality_provider.get_current_personality(),
                "new_theme": await self.theme_manager.get_current_theme(),
                "analysis": transition_analysis
            }
            
        except Exception as e:
            logger.error(f"Personality state transition management failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_context_aware_adaptation_plan(self, user_id: str, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a context-aware adaptation plan for personality and theme changes.
        
        This method analyzes multiple context factors to create a comprehensive
        adaptation plan that considers user preferences, system state, and emotional intelligence.
        """
        try:
            # Get user context and preferences
            user_context = await self.context_analyzer.analyze_user_context(user_id)
            user_preferences = await self.preference_manager.get_user_preferences(user_id)
            personalized_recs = await self.preference_manager.get_personalized_recommendations(user_id, user_context)
            
            # Get system context analysis
            system_context = await self.context_analyzer.analyze_system_context()
            system_context.update(system_metrics)
            
            # Get emotional intelligence analysis
            stress_level = await self.emotional_intelligence.monitor_team_stress(system_context)
            morale_level = await self.emotional_intelligence.monitor_team_morale(system_context)
            
            # Create emotional context
            emotional_context = EmotionalContext(
                team_stress_level=stress_level,
                team_morale=morale_level,
                recent_achievements=self.emotional_intelligence.achievements[-3:],
                error_frequency=system_context.get("error_rate", 0.0) * 3600,
                workload_intensity=system_context.get("system_load", 0.5),
                collaboration_activity=system_context.get("active_users", 1) / 10.0
            )
            
            # Get adaptive response strategy
            response_strategy = await self.emotional_intelligence.get_adaptive_response_strategy(emotional_context)
            
            # Create comprehensive adaptation plan
            adaptation_plan = {
                "user_id": user_id,
                "analysis": {
                    "user_context": {
                        "engagement_level": user_context.engagement_level.value,
                        "session_duration": user_context.session_duration,
                        "interaction_count": user_context.interaction_count
                    },
                    "system_context": system_context,
                    "emotional_context": {
                        "stress_level": stress_level,
                        "morale_level": morale_level,
                        "emotional_balance": emotional_context.team_stress_level
                    },
                    "user_preferences": {
                        "preferred_personalities": user_preferences.preferred_personality_states,
                        "preferred_themes": user_preferences.preferred_themes,
                        "auto_adaptation": user_preferences.auto_adaptation_enabled,
                        "learning_enabled": user_preferences.learning_enabled
                    }
                },
                "recommendations": {
                    "personalized": personalized_recs,
                    "emotional_intelligence": response_strategy,
                    "system_based": await self.get_mood_recommendations(system_context)
                },
                "adaptation_strategy": {
                    "primary_personality": None,
                    "primary_theme": None,
                    "fallback_personality": "professional",
                    "fallback_theme": "professional",
                    "adaptation_confidence": 0.0,
                    "adaptation_reason": "",
                    "user_preference_weight": 0.4,
                    "emotional_intelligence_weight": 0.4,
                    "system_context_weight": 0.2
                },
                "execution_plan": {
                    "immediate_actions": [],
                    "gradual_transitions": [],
                    "monitoring_points": [],
                    "rollback_conditions": []
                }
            }
            
            # Determine primary adaptation strategy
            if user_preferences.auto_adaptation_enabled:
                # Weight different recommendation sources
                personality_scores = {}
                theme_scores = {}
                
                # User preferences (40% weight)
                for personality in personalized_recs["personality_recommendations"][:3]:
                    personality_scores[personality] = personality_scores.get(personality, 0) + 0.4
                
                for theme in personalized_recs["theme_recommendations"][:3]:
                    theme_scores[theme] = theme_scores.get(theme, 0) + 0.4
                
                # Emotional intelligence (40% weight)
                ei_personality = response_strategy["personality_recommendation"]
                ei_theme = response_strategy["theme_recommendation"]
                personality_scores[ei_personality] = personality_scores.get(ei_personality, 0) + 0.4
                theme_scores[ei_theme] = theme_scores.get(ei_theme, 0) + 0.4
                
                # System context (20% weight)
                system_recs = await self.get_mood_recommendations(system_context)
                if system_recs:
                    system_personality = system_recs[0]["mood"]
                    personality_scores[system_personality] = personality_scores.get(system_personality, 0) + 0.2
                    theme_scores[system_personality] = theme_scores.get(system_personality, 0) + 0.2
                
                # Select highest scoring options
                primary_personality = max(personality_scores.items(), key=lambda x: x[1])[0] if personality_scores else "professional"
                primary_theme = max(theme_scores.items(), key=lambda x: x[1])[0] if theme_scores else "professional"
                adaptation_confidence = max(personality_scores.values()) if personality_scores else 0.5
                
                adaptation_plan["adaptation_strategy"].update({
                    "primary_personality": primary_personality,
                    "primary_theme": primary_theme,
                    "adaptation_confidence": adaptation_confidence,
                    "adaptation_reason": f"Weighted combination of user preferences, emotional intelligence, and system context"
                })
                
                # Create execution plan
                current_personality = await self.personality_provider.get_current_personality()
                current_theme = await self.theme_manager.get_current_theme()
                
                if primary_personality != current_personality["state"]:
                    adaptation_plan["execution_plan"]["immediate_actions"].append({
                        "action": "transition_personality",
                        "from": current_personality["state"],
                        "to": primary_personality,
                        "priority": "high"
                    })
                
                if primary_theme != current_theme["theme_name"]:
                    adaptation_plan["execution_plan"]["immediate_actions"].append({
                        "action": "apply_theme",
                        "from": current_theme["theme_name"],
                        "to": primary_theme,
                        "priority": "medium"
                    })
                
                # Add monitoring points
                adaptation_plan["execution_plan"]["monitoring_points"] = [
                    "user_satisfaction_feedback",
                    "engagement_level_changes",
                    "system_performance_impact",
                    "emotional_context_changes"
                ]
                
                # Add rollback conditions
                adaptation_plan["execution_plan"]["rollback_conditions"] = [
                    "user_explicitly_requests_change",
                    "system_performance_degrades",
                    "stress_level_increases_significantly",
                    "adaptation_confidence_drops_below_threshold"
                ]
                
            else:
                # User has disabled auto-adaptation, use their explicit preferences
                adaptation_plan["adaptation_strategy"].update({
                    "primary_personality": user_preferences.preferred_personality_states[0] if user_preferences.preferred_personality_states else "professional",
                    "primary_theme": user_preferences.preferred_themes[0] if user_preferences.preferred_themes else "professional",
                    "adaptation_confidence": 1.0,
                    "adaptation_reason": "User explicit preferences (auto-adaptation disabled)"
                })
            
            return adaptation_plan
            
        except Exception as e:
            logger.error(f"Context-aware adaptation plan creation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def execute_adaptation_plan(self, adaptation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a context-aware adaptation plan."""
        try:
            execution_results = {
                "plan_id": adaptation_plan.get("user_id", "system"),
                "execution_timestamp": datetime.now().isoformat(),
                "actions_executed": [],
                "actions_failed": [],
                "final_state": {},
                "learning_data": {}
            }
            
            # Execute immediate actions
            for action in adaptation_plan["execution_plan"]["immediate_actions"]:
                try:
                    if action["action"] == "transition_personality":
                        context = EngagementContext(
                            user_id=adaptation_plan["user_id"],
                            engagement_level=EngagementLevel.ACTIVE
                        )
                        
                        success = await self.personality_provider.transition_personality(action["to"], context)
                        
                        if success:
                            execution_results["actions_executed"].append(action)
                        else:
                            execution_results["actions_failed"].append({**action, "error": "transition_failed"})
                    
                    elif action["action"] == "apply_theme":
                        context = EngagementContext(
                            user_id=adaptation_plan["user_id"],
                            engagement_level=EngagementLevel.ACTIVE
                        )
                        
                        success = await self.theme_manager.apply_theme(action["to"], context)
                        
                        if success:
                            execution_results["actions_executed"].append(action)
                        else:
                            execution_results["actions_failed"].append({**action, "error": "theme_application_failed"})
                
                except Exception as action_error:
                    execution_results["actions_failed"].append({**action, "error": str(action_error)})
            
            # Record final state
            execution_results["final_state"] = {
                "personality": await self.personality_provider.get_current_personality(),
                "theme": await self.theme_manager.get_current_theme()
            }
            
            # Create learning data for user preference learning
            if adaptation_plan.get("user_id") and adaptation_plan["user_id"] != "system":
                execution_results["learning_data"] = {
                    "personality_state": execution_results["final_state"]["personality"]["state"],
                    "theme": execution_results["final_state"]["theme"]["theme_name"],
                    "user_satisfaction": 0.8,  # Would be measured from actual feedback
                    "interaction_duration": 300,  # Would be measured from session
                    "engagement_level": "active",
                    "adaptation_confidence": adaptation_plan["adaptation_strategy"]["adaptation_confidence"]
                }
                
                # Record learning interaction
                await self.preference_manager.learn_from_interaction(
                    adaptation_plan["user_id"], 
                    execution_results["learning_data"]
                )
            
            return execution_results
            
        except Exception as e:
            logger.error(f"Adaptation plan execution failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_transition_triggers(self, trigger_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trigger conditions to determine if personality transition is needed."""
        try:
            analysis = {
                "transition_needed": False,
                "recommended_state": None,
                "reason": "",
                "confidence": 0.0,
                "trigger_analysis": {}
            }
            
            # Analyze system load triggers
            system_load = trigger_conditions.get("system_load", 0.5)
            if system_load > 0.8:
                analysis.update({
                    "transition_needed": True,
                    "recommended_state": "focused",
                    "reason": f"High system load ({system_load:.1f}) requires focused attention",
                    "confidence": 0.9
                })
                analysis["trigger_analysis"]["system_load"] = "high_load_trigger"
            
            # Analyze error rate triggers
            error_rate = trigger_conditions.get("error_rate", 0.0)
            if error_rate > 0.1:
                analysis.update({
                    "transition_needed": True,
                    "recommended_state": "professional",
                    "reason": f"High error rate ({error_rate:.2f}) requires professional focus",
                    "confidence": 0.85
                })
                analysis["trigger_analysis"]["error_rate"] = "high_error_trigger"
            
            # Analyze user activity triggers
            active_users = trigger_conditions.get("active_users", 1)
            if active_users > 5:
                analysis.update({
                    "transition_needed": True,
                    "recommended_state": "energetic",
                    "reason": f"High user activity ({active_users} users) suggests energetic engagement",
                    "confidence": 0.7
                })
                analysis["trigger_analysis"]["user_activity"] = "high_activity_trigger"
            
            # Analyze achievement triggers
            recent_achievements = trigger_conditions.get("recent_achievements", [])
            if len(recent_achievements) > 0:
                analysis.update({
                    "transition_needed": True,
                    "recommended_state": "celebratory",
                    "reason": f"Recent achievements ({len(recent_achievements)}) warrant celebration",
                    "confidence": 0.95
                })
                analysis["trigger_analysis"]["achievements"] = "achievement_trigger"
            
            # Analyze time-based triggers
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 17:  # Business hours
                if not analysis["transition_needed"]:
                    analysis.update({
                        "transition_needed": True,
                        "recommended_state": "professional",
                        "reason": "Business hours suggest professional personality",
                        "confidence": 0.6
                    })
                    analysis["trigger_analysis"]["time_based"] = "business_hours_trigger"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Transition trigger analysis failed: {e}")
            return {
                "transition_needed": False,
                "error": str(e)
            }
    
    async def celebrate_achievement(self, achievement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Celebrate team achievements with appropriate personality and theme changes."""
        try:
            # Recognize the achievement
            recognition_result = await self.emotional_intelligence.recognize_achievement(achievement_data)
            
            if "error" in recognition_result:
                return recognition_result
            
            achievement = recognition_result["achievement"]
            celebration = recognition_result["celebration"]
            
            # Create emotional context for celebration
            emotional_context = EmotionalContext(
                team_stress_level=0.2,  # Achievements reduce stress
                team_morale=min(0.8 + recognition_result["morale_impact"], 1.0),
                recent_achievements=[achievement]
            )
            
            # Get adaptive response strategy
            response_strategy = await self.emotional_intelligence.get_adaptive_response_strategy(emotional_context)
            
            # Apply celebratory personality and theme
            context = EngagementContext(
                user_id="system",
                engagement_level=EngagementLevel.IMMERSIVE
            )
            
            await self.personality_provider.transition_personality(
                response_strategy["personality_recommendation"], 
                context
            )
            
            await self.theme_manager.apply_theme(
                response_strategy["theme_recommendation"], 
                context
            )
            
            return {
                "achievement": achievement,
                "celebration": celebration,
                "response_strategy": response_strategy,
                "personality_applied": response_strategy["personality_recommendation"],
                "theme_applied": response_strategy["theme_recommendation"],
                "emotional_impact": {
                    "morale_boost": recognition_result["morale_impact"],
                    "stress_reduction": 0.1
                }
            }
            
        except Exception as e:
            logger.error(f"Achievement celebration failed: {e}")
            return {"error": str(e)}
    
    async def adapt_to_emotional_context(self, system_metrics: Dict[str, Any], activity_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt personality and theme based on emotional intelligence analysis."""
        try:
            # Monitor emotional state
            stress_level = await self.emotional_intelligence.monitor_team_stress(system_metrics)
            morale_level = await self.emotional_intelligence.monitor_team_morale(activity_metrics)
            
            # Create emotional context
            emotional_context = EmotionalContext(
                team_stress_level=stress_level,
                team_morale=morale_level,
                recent_achievements=self.emotional_intelligence.achievements[-3:],  # Last 3
                error_frequency=system_metrics.get("error_rate", 0.0) * 3600,  # errors per hour
                workload_intensity=system_metrics.get("system_load", 0.5),
                collaboration_activity=activity_metrics.get("active_users", 1) / 10.0  # normalized
            )
            
            # Store emotional context
            self.emotional_intelligence.emotional_history.append(emotional_context)
            
            # Get adaptive response strategy
            response_strategy = await self.emotional_intelligence.get_adaptive_response_strategy(emotional_context)
            
            # Apply recommended personality and theme
            context = EngagementContext(
                user_id="system",
                engagement_level=EngagementLevel.ACTIVE,
                system_load=system_metrics.get("system_load", 0.5)
            )
            
            personality_changed = False
            theme_changed = False
            
            # Apply personality if different from current
            current_personality = await self.personality_provider.get_current_personality()
            if response_strategy["personality_recommendation"] != current_personality["state"]:
                await self.personality_provider.transition_personality(
                    response_strategy["personality_recommendation"], 
                    context
                )
                personality_changed = True
            
            # Apply theme if different from current
            current_theme = await self.theme_manager.get_current_theme()
            if response_strategy["theme_recommendation"] != current_theme["theme_name"]:
                await self.theme_manager.apply_theme(
                    response_strategy["theme_recommendation"], 
                    context
                )
                theme_changed = True
            
            return {
                "emotional_context": {
                    "stress_level": stress_level,
                    "morale_level": morale_level,
                    "emotional_balance": emotional_context.team_stress_level
                },
                "response_strategy": response_strategy,
                "changes_applied": {
                    "personality_changed": personality_changed,
                    "theme_changed": theme_changed,
                    "new_personality": response_strategy["personality_recommendation"],
                    "new_theme": response_strategy["theme_recommendation"]
                },
                "emotional_analytics": await self.emotional_intelligence.get_emotional_analytics()
            }
            
        except Exception as e:
            logger.error(f"Emotional context adaptation failed: {e}")
            return {"error": str(e)}
    
    async def adapt_with_user_preferences(self, user_id: str, system_metrics: Dict[str, Any], 
                                        activity_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt personality and theme considering user preferences and learning."""
        try:
            # Get user context
            context = await self.context_analyzer.analyze_user_context(user_id)
            self.active_contexts[user_id] = context
            
            # Get personalized recommendations
            personalized_recs = await self.preference_manager.get_personalized_recommendations(user_id, context)
            
            # Get emotional intelligence recommendations
            emotional_adaptation = await self.adapt_to_emotional_context(system_metrics, activity_metrics)
            
            # Combine recommendations with user preferences
            final_personality = personalized_recs["personality_recommendations"][0]
            final_theme = personalized_recs["theme_recommendations"][0]
            
            # Override with emotional intelligence if critical conditions exist
            if "emotional_context" in emotional_adaptation:
                emotional_ctx = emotional_adaptation["emotional_context"]
                
                # High stress overrides user preferences for safety
                if emotional_ctx["stress_level"] > 0.8:
                    user_prefs = await self.preference_manager.get_user_preferences(user_id)
                    final_personality = user_prefs.stress_response_preference
                    final_theme = "calm"
                
                # Very low morale overrides for morale boost
                elif emotional_ctx["morale_level"] < 0.3:
                    user_prefs = await self.preference_manager.get_user_preferences(user_id)
                    final_personality = user_prefs.morale_boost_preference
                    final_theme = "energetic"
            
            # Apply the final personality and theme
            personality_changed = False
            theme_changed = False
            
            current_personality = await self.personality_provider.get_current_personality()
            if final_personality != current_personality["state"]:
                await self.personality_provider.transition_personality(final_personality, context)
                personality_changed = True
            
            current_theme = await self.theme_manager.get_current_theme()
            if final_theme != current_theme["theme_name"]:
                await self.theme_manager.apply_theme(final_theme, context)
                theme_changed = True
            
            # Record interaction for learning (simulate user satisfaction)
            interaction_data = {
                "personality_state": final_personality,
                "theme": final_theme,
                "user_satisfaction": 0.8,  # Would be measured from actual user feedback
                "interaction_duration": 300,  # Would be measured from actual session
                "engagement_level": context.engagement_level.value
            }
            
            await self.preference_manager.learn_from_interaction(user_id, interaction_data)
            
            return {
                "user_id": user_id,
                "personalized_recommendations": personalized_recs,
                "emotional_adaptation": emotional_adaptation.get("emotional_context", {}),
                "final_decisions": {
                    "personality": final_personality,
                    "theme": final_theme,
                    "personality_changed": personality_changed,
                    "theme_changed": theme_changed
                },
                "learning_status": "interaction_recorded"
            }
            
        except Exception as e:
            logger.error(f"User preference adaptation failed: {e}")
            return {"error": str(e)}
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences for personality customization."""
        try:
            success = await self.preference_manager.update_user_preferences(user_id, preferences)
            
            if success:
                # Apply new preferences immediately if auto-adaptation is enabled
                user_prefs = await self.preference_manager.get_user_preferences(user_id)
                
                if user_prefs.auto_adaptation_enabled and user_prefs.preferred_personality_states:
                    context = self.active_contexts.get(user_id) or EngagementContext(user_id=user_id)
                    
                    # Apply preferred personality
                    preferred_personality = user_prefs.preferred_personality_states[0]
                    await self.personality_provider.transition_personality(preferred_personality, context)
                    
                    # Apply preferred theme
                    if user_prefs.preferred_themes:
                        preferred_theme = user_prefs.preferred_themes[0]
                        await self.theme_manager.apply_theme(preferred_theme, context)
                
                return {
                    "status": "preferences_updated",
                    "user_id": user_id,
                    "updated_preferences": preferences,
                    "auto_applied": user_prefs.auto_adaptation_enabled
                }
            else:
                return {"status": "update_failed", "user_id": user_id}
                
        except Exception as e:
            logger.error(f"User preference update failed: {e}")
            return {"error": str(e)}
    
    async def get_user_personality_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive personality analytics for a specific user."""
        try:
            user_prefs = await self.preference_manager.get_user_preferences(user_id)
            learning_analytics = await self.preference_manager.get_learning_analytics(user_id)
            personalized_recs = await self.preference_manager.get_personalized_recommendations(
                user_id, 
                self.active_contexts.get(user_id, EngagementContext(user_id=user_id))
            )
            
            return {
                "user_id": user_id,
                "current_preferences": {
                    "preferred_personalities": user_prefs.preferred_personality_states,
                    "preferred_themes": user_prefs.preferred_themes,
                    "visual_intensity": user_prefs.visual_intensity_preference,
                    "animation_speed": user_prefs.animation_speed_preference,
                    "celebration_level": user_prefs.celebration_level_preference,
                    "auto_adaptation": user_prefs.auto_adaptation_enabled,
                    "learning_enabled": user_prefs.learning_enabled,
                    "last_updated": user_prefs.last_updated.isoformat()
                },
                "learning_analytics": learning_analytics,
                "personalized_recommendations": personalized_recs,
                "interaction_history_count": len(self.preference_manager.interaction_history.get(user_id, [])),
                "active_context": self.active_contexts.get(user_id) is not None
            }
            
        except Exception as e:
            logger.error(f"User personality analytics failed: {e}")
            return {"error": str(e)}
    
    async def create_personality_state_transition_plan(self, target_state: str, user_id: str) -> Dict[str, Any]:
        """Create a plan for transitioning to a target personality state."""
        try:
            current_personality = await self.personality_provider.get_current_personality()
            current_state = current_personality["state"]
            
            if current_state == target_state:
                return {
                    "status": "already_at_target",
                    "current_state": current_state,
                    "target_state": target_state
                }
            
            # Get user preferences to customize transition
            user_prefs = await self.preference_manager.get_user_preferences(user_id)
            context = self.active_contexts.get(user_id, EngagementContext(user_id=user_id))
            
            # Create transition plan
            transition_plan = {
                "from_state": current_state,
                "to_state": target_state,
                "transition_steps": [],
                "estimated_duration": 0,
                "theme_changes": [],
                "user_customizations": []
            }
            
            # Determine if intermediate states are needed
            state_compatibility = {
                "professional": ["analytical", "focused"],
                "energetic": ["celebratory", "friendly"],
                "calm": ["professional", "analytical"],
                "celebratory": ["energetic", "friendly"],
                "analytical": ["professional", "focused"],
                "friendly": ["energetic", "celebratory"],
                "focused": ["professional", "analytical"]
            }
            
            compatible_states = state_compatibility.get(current_state, [])
            
            if target_state not in compatible_states and target_state != current_state:
                # Need intermediate transition
                intermediate_state = None
                for state in user_prefs.preferred_personality_states:
                    if state in compatible_states and target_state in state_compatibility.get(state, []):
                        intermediate_state = state
                        break
                
                if not intermediate_state and compatible_states:
                    intermediate_state = compatible_states[0]
                
                if intermediate_state:
                    transition_plan["transition_steps"].extend([
                        {
                            "step": 1,
                            "action": "transition_personality",
                            "from_state": current_state,
                            "to_state": intermediate_state,
                            "duration_ms": 2000,
                            "reason": "intermediate_transition"
                        },
                        {
                            "step": 2,
                            "action": "transition_personality", 
                            "from_state": intermediate_state,
                            "to_state": target_state,
                            "duration_ms": 2000,
                            "reason": "final_transition"
                        }
                    ])
                    transition_plan["estimated_duration"] = 4000
                else:
                    # Direct transition
                    transition_plan["transition_steps"].append({
                        "step": 1,
                        "action": "transition_personality",
                        "from_state": current_state,
                        "to_state": target_state,
                        "duration_ms": 3000,
                        "reason": "direct_transition"
                    })
                    transition_plan["estimated_duration"] = 3000
            else:
                # Direct compatible transition
                transition_plan["transition_steps"].append({
                    "step": 1,
                    "action": "transition_personality",
                    "from_state": current_state,
                    "to_state": target_state,
                    "duration_ms": 1500,
                    "reason": "compatible_transition"
                })
                transition_plan["estimated_duration"] = 1500
            
            # Add theme transition
            if target_state in user_prefs.preferred_themes:
                target_theme = target_state
            else:
                target_theme = target_state  # Use personality state as theme
            
            transition_plan["theme_changes"].append({
                "action": "apply_theme",
                "theme": target_theme,
                "visual_intensity": user_prefs.visual_intensity_preference,
                "animation_speed": user_prefs.animation_speed_preference
            })
            
            # Add user customizations
            transition_plan["user_customizations"] = [
                f"Visual intensity: {user_prefs.visual_intensity_preference}",
                f"Animation speed: {user_prefs.animation_speed_preference}",
                f"Celebration level: {user_prefs.celebration_level_preference}"
            ]
            
            return transition_plan
            
        except Exception as e:
            logger.error(f"Transition plan creation failed: {e}")
            return {"error": str(e)}
    
    async def get_personality_analytics(self) -> Dict[str, Any]:
        """Get personality analytics and insights."""
        try:
            current_personality = await self.personality_provider.get_current_personality()
            current_theme = await self.theme_manager.get_current_theme()
            system_context = await self.context_analyzer.analyze_system_context()
            emotional_analytics = await self.emotional_intelligence.get_emotional_analytics()
            
            return {
                "current_personality": current_personality,
                "current_theme": current_theme,
                "transition_history": self.personality_provider.personality_history[-10:],  # Last 10
                "theme_history": self.theme_manager.theme_history[-10:],  # Last 10
                "active_contexts": len(self.active_contexts),
                "context_analysis": system_context,
                "emotional_intelligence": emotional_analytics,
                "mood_recommendations": await self.get_mood_recommendations(system_context),
                "personality_effectiveness": await self._calculate_personality_effectiveness(),
                "available_themes": await self.theme_manager.get_available_themes(),
                "recent_achievements": self.emotional_intelligence.achievements[-5:]  # Last 5
            }
            
        except Exception as e:
            logger.error(f"Failed to get personality analytics: {e}")
            return {"error": str(e)}
    
    async def _calculate_personality_effectiveness(self) -> Dict[str, float]:
        """Calculate personality effectiveness metrics."""
        # Placeholder effectiveness calculation
        return {
            "user_engagement_score": 0.8,
            "personality_stability": 0.9,
            "context_adaptation_rate": 0.7,
            "user_satisfaction_estimate": 0.85
        }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Personality Engine capabilities."""
        return [
            "adaptive_personality",
            "context_analysis", 
            "mood_management",
            "theme_management",
            "emotional_intelligence",
            "team_stress_monitoring",
            "team_morale_monitoring",
            "achievement_recognition",
            "adaptive_response_strategies",
            "user_preference_learning",
            "personalized_recommendations",
            "personality_state_transitions",
            "context_aware_adaptation",
            "engagement_prediction",
            "dynamic_theming",
            "personality_transitions",
            "celebration_management"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Personality Engine health status."""
        recent_emotional_context = (self.emotional_intelligence.emotional_history[-1] 
                                  if self.emotional_intelligence.emotional_history else None)
        
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "active_contexts": len(self.active_contexts),
            "current_personality": self.personality_provider.current_profile.current_state.value,
            "current_theme": self.theme_manager.current_theme_name,
            "transition_count": len(self.personality_provider.personality_history),
            "theme_changes": len(self.theme_manager.theme_history),
            "achievements_tracked": len(self.emotional_intelligence.achievements),
            "users_with_preferences": len(self.preference_manager.user_preferences),
            "total_user_interactions": sum(len(history) for history in self.preference_manager.interaction_history.values()),
            "emotional_state": {
                "team_stress": recent_emotional_context.team_stress_level if recent_emotional_context else 0.5,
                "team_morale": recent_emotional_context.team_morale if recent_emotional_context else 0.7
            }
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Personality Engine module information."""
        return {
            "module_id": self.module_id,
            "name": "Personality Engine",
            "version": "1.0.0",
            "description": "Adaptive dashboard behavior with mood management and emotional intelligence"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation to basic personality mode."""
        try:
            degradation_actions = []
            
            # Reset to professional personality
            default_context = EngagementContext(
                user_id="system",
                engagement_level=EngagementLevel.PASSIVE
            )
            
            asyncio.create_task(
                self.personality_provider.transition_personality(
                    PersonalityState.PROFESSIONAL.value, 
                    default_context
                )
            )
            degradation_actions.append("Reset to professional personality")
            
            # Clear active contexts to reduce processing load
            context_count = len(self.active_contexts)
            self.active_contexts.clear()
            degradation_actions.append(f"Cleared {context_count} active contexts")
            
            # Reduce personality responsiveness
            self.personality_provider.current_profile.responsiveness = 0.3
            degradation_actions.append("Reduced personality responsiveness")
            
            # Disable complex emotional intelligence features
            self.personality_provider.current_profile.energy_level = 0.5
            self.personality_provider.current_profile.visual_intensity = 0.3
            degradation_actions.append("Simplified personality parameters")
            
            return {
                "status": "degraded",
                "actions_taken": degradation_actions,
                "current_personality": PersonalityState.PROFESSIONAL.value,
                "functionality_level": "basic_professional_mode",
                "recovery_possible": True
            }
        except Exception as e:
            return {
                "status": "degradation_failed",
                "error": str(e),
                "functionality_level": "unknown",
                "recovery_possible": False
            }