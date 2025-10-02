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
            
            # Predict engagement needs
            engagement_needs = await self.context_analyzer.predict_engagement_needs(context)
            
            return {
                "user_id": user_id,
                "context": {
                    "engagement_level": context.engagement_level.value,
                    "session_duration": context.session_duration,
                    "system_load": context.system_load
                },
                "personality": await self.personality_provider.get_current_personality(),
                "recommendations": recommendations,
                "engagement_needs": engagement_needs
            }
            
        except Exception as e:
            logger.error(f"Context adaptation failed: {e}")
            return {"error": str(e)}
    
    async def get_personality_analytics(self) -> Dict[str, Any]:
        """Get personality analytics and insights."""
        try:
            current_personality = await self.personality_provider.get_current_personality()
            
            return {
                "current_personality": current_personality,
                "transition_history": self.personality_provider.personality_history[-10:],  # Last 10
                "active_contexts": len(self.active_contexts),
                "context_analysis": await self.context_analyzer.analyze_system_context(),
                "personality_effectiveness": await self._calculate_personality_effectiveness()
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
            "emotional_intelligence",
            "engagement_prediction"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Personality Engine health status."""
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "active_contexts": len(self.active_contexts),
            "current_personality": self.personality_provider.current_profile.current_state.value,
            "transition_count": len(self.personality_provider.personality_history)
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