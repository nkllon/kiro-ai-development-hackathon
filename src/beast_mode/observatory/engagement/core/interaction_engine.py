"""
Interaction Engine - Multi-Modal Engagement and Accessibility Support
=====================================================================

The Interaction Engine provides multi-modal user interaction processing,
accessibility support, and collaborative engagement features.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .interfaces import (
    IInteractionHandler, 
    IAccessibilityProvider,
    EngagementContext
)

logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """Types of user interactions."""
    CLICK = "click"
    HOVER = "hover"
    KEYBOARD = "keyboard"
    TOUCH = "touch"
    VOICE = "voice"
    GESTURE = "gesture"
    SCROLL = "scroll"
    FOCUS = "focus"


@dataclass
class InteractionEvent:
    """User interaction event."""
    event_id: str
    interaction_type: InteractionType
    target_element: str
    timestamp: datetime
    user_id: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False


@dataclass
class AccessibilitySettings:
    """User accessibility preferences."""
    screen_reader_enabled: bool = False
    keyboard_navigation_enabled: bool = True
    high_contrast_mode: bool = False
    reduced_motion: bool = False
    font_size_multiplier: float = 1.0
    audio_descriptions: bool = False


class InteractionHandler(IInteractionHandler):
    """Implementation of user interaction processing."""
    
    def __init__(self):
        self.interaction_handlers: Dict[str, Callable] = {}
        self.interaction_history: List[InteractionEvent] = []
        self.analytics_data: Dict[str, Any] = {
            "total_interactions": 0,
            "interactions_by_type": {},
            "popular_elements": {},
            "user_patterns": {}
        }
        
    async def handle_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a user interaction."""
        try:
            # Create interaction event
            interaction_event = InteractionEvent(
                event_id=interaction.get("id", f"interaction_{datetime.now().strftime('%H%M%S')}"),
                interaction_type=InteractionType(interaction.get("type", "click")),
                target_element=interaction.get("target", "unknown"),
                timestamp=datetime.now(),
                user_id=interaction.get("user_id"),
                coordinates=interaction.get("coordinates"),
                metadata=interaction.get("metadata", {})
            )
            
            # Add to history
            self.interaction_history.append(interaction_event)
            
            # Update analytics
            await self._update_analytics(interaction_event)
            
            # Process interaction
            result = await self._process_interaction(interaction_event)
            
            # Mark as processed
            interaction_event.processed = True
            
            logger.info(f"Interaction processed: {interaction_event.interaction_type.value} on {interaction_event.target_element}")
            
            return {
                "event_id": interaction_event.event_id,
                "processed": True,
                "result": result,
                "timestamp": interaction_event.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Interaction handling failed: {e}")
            return {"error": str(e), "processed": False}
    
    async def register_interaction_handler(self, event_type: str, handler: Callable) -> bool:
        """Register handler for specific interaction type."""
        try:
            self.interaction_handlers[event_type] = handler
            logger.info(f"Interaction handler registered for: {event_type}")
            return True
        except Exception as e:
            logger.error(f"Handler registration failed: {e}")
            return False
    
    async def get_interaction_analytics(self) -> Dict[str, Any]:
        """Get interaction analytics data."""
        try:
            # Calculate recent interaction patterns
            recent_interactions = self.interaction_history[-100:]  # Last 100
            
            # Update analytics with recent data
            for interaction in recent_interactions:
                interaction_type = interaction.interaction_type.value
                self.analytics_data["interactions_by_type"][interaction_type] = (
                    self.analytics_data["interactions_by_type"].get(interaction_type, 0) + 1
                )
                
                self.analytics_data["popular_elements"][interaction.target_element] = (
                    self.analytics_data["popular_elements"].get(interaction.target_element, 0) + 1
                )
            
            return {
                "total_interactions": len(self.interaction_history),
                "interactions_by_type": self.analytics_data["interactions_by_type"],
                "popular_elements": dict(sorted(
                    self.analytics_data["popular_elements"].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10]),  # Top 10
                "recent_interaction_rate": len(recent_interactions),
                "average_interactions_per_session": self._calculate_session_average(),
                "interaction_effectiveness": await self._calculate_interaction_effectiveness()
            }
            
        except Exception as e:
            logger.error(f"Interaction analytics failed: {e}")
            return {"error": str(e)}
    
    async def _process_interaction(self, interaction: InteractionEvent) -> Dict[str, Any]:
        """Process individual interaction event."""
        try:
            # Check for registered handler
            handler = self.interaction_handlers.get(interaction.interaction_type.value)
            if handler:
                return await handler(interaction)
            
            # Default processing based on interaction type
            if interaction.interaction_type == InteractionType.CLICK:
                return await self._handle_click_interaction(interaction)
            elif interaction.interaction_type == InteractionType.HOVER:
                return await self._handle_hover_interaction(interaction)
            elif interaction.interaction_type == InteractionType.KEYBOARD:
                return await self._handle_keyboard_interaction(interaction)
            else:
                return {"action": "logged", "details": "No specific handler"}
                
        except Exception as e:
            logger.error(f"Interaction processing failed: {e}")
            return {"error": str(e)}
    
    async def _handle_click_interaction(self, interaction: InteractionEvent) -> Dict[str, Any]:
        """Handle click interactions."""
        return {
            "action": "click_processed",
            "target": interaction.target_element,
            "engagement_boost": 0.1
        }
    
    async def _handle_hover_interaction(self, interaction: InteractionEvent) -> Dict[str, Any]:
        """Handle hover interactions."""
        return {
            "action": "hover_processed",
            "target": interaction.target_element,
            "show_tooltip": True
        }
    
    async def _handle_keyboard_interaction(self, interaction: InteractionEvent) -> Dict[str, Any]:
        """Handle keyboard interactions."""
        return {
            "action": "keyboard_processed",
            "accessibility_friendly": True,
            "navigation_support": True
        }
    
    async def _update_analytics(self, interaction: InteractionEvent) -> None:
        """Update interaction analytics."""
        self.analytics_data["total_interactions"] += 1
        
        # Update user patterns if user_id available
        if interaction.user_id:
            if interaction.user_id not in self.analytics_data["user_patterns"]:
                self.analytics_data["user_patterns"][interaction.user_id] = {
                    "total_interactions": 0,
                    "preferred_interaction_types": {},
                    "session_start": datetime.now()
                }
            
            user_pattern = self.analytics_data["user_patterns"][interaction.user_id]
            user_pattern["total_interactions"] += 1
            
            interaction_type = interaction.interaction_type.value
            user_pattern["preferred_interaction_types"][interaction_type] = (
                user_pattern["preferred_interaction_types"].get(interaction_type, 0) + 1
            )
    
    def _calculate_session_average(self) -> float:
        """Calculate average interactions per session."""
        if not self.analytics_data["user_patterns"]:
            return 0.0
        
        total_interactions = sum(
            pattern["total_interactions"] 
            for pattern in self.analytics_data["user_patterns"].values()
        )
        total_sessions = len(self.analytics_data["user_patterns"])
        
        return total_interactions / total_sessions if total_sessions > 0 else 0.0
    
    async def _calculate_interaction_effectiveness(self) -> float:
        """Calculate interaction effectiveness score."""
        # Simple effectiveness based on interaction diversity and frequency
        if not self.analytics_data["interactions_by_type"]:
            return 0.0
        
        # More diverse interactions = higher effectiveness
        interaction_diversity = len(self.analytics_data["interactions_by_type"])
        max_diversity = len(InteractionType)
        
        diversity_score = interaction_diversity / max_diversity
        
        # Balanced interaction types = higher effectiveness
        interaction_counts = list(self.analytics_data["interactions_by_type"].values())
        if interaction_counts:
            balance_score = 1.0 - (max(interaction_counts) - min(interaction_counts)) / sum(interaction_counts)
        else:
            balance_score = 0.0
        
        return (diversity_score + balance_score) / 2


class AccessibilityProvider(IAccessibilityProvider):
    """Implementation of accessibility support features."""
    
    def __init__(self):
        self.accessibility_settings = AccessibilitySettings()
        self.screen_reader_active = False
        self.keyboard_navigation_active = True
        
    async def enable_screen_reader_support(self) -> bool:
        """Enable screen reader support."""
        try:
            self.accessibility_settings.screen_reader_enabled = True
            self.screen_reader_active = True
            
            # Configure screen reader optimizations
            await self._configure_screen_reader()
            
            logger.info("Screen reader support enabled")
            return True
        except Exception as e:
            logger.error(f"Screen reader enablement failed: {e}")
            return False
    
    async def enable_keyboard_navigation(self) -> bool:
        """Enable keyboard navigation."""
        try:
            self.accessibility_settings.keyboard_navigation_enabled = True
            self.keyboard_navigation_active = True
            
            # Configure keyboard navigation
            await self._configure_keyboard_navigation()
            
            logger.info("Keyboard navigation enabled")
            return True
        except Exception as e:
            logger.error(f"Keyboard navigation enablement failed: {e}")
            return False
    
    async def get_accessibility_status(self) -> Dict[str, bool]:
        """Get current accessibility feature status."""
        return {
            "screen_reader_enabled": self.accessibility_settings.screen_reader_enabled,
            "keyboard_navigation_enabled": self.accessibility_settings.keyboard_navigation_enabled,
            "high_contrast_mode": self.accessibility_settings.high_contrast_mode,
            "reduced_motion": self.accessibility_settings.reduced_motion,
            "audio_descriptions": self.accessibility_settings.audio_descriptions
        }
    
    async def _configure_screen_reader(self) -> None:
        """Configure screen reader optimizations."""
        # Placeholder for screen reader configuration
        # In a real implementation, this would:
        # - Add ARIA labels to all interactive elements
        # - Configure focus management
        # - Set up screen reader announcements
        pass
    
    async def _configure_keyboard_navigation(self) -> None:
        """Configure keyboard navigation."""
        # Placeholder for keyboard navigation configuration
        # In a real implementation, this would:
        # - Set up tab order
        # - Configure keyboard shortcuts
        # - Enable focus indicators
        pass


class InteractionEngine(ReflectiveModule):
    """
    Main Interaction Engine that provides multi-modal user interaction processing,
    accessibility support, and collaborative engagement features.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "interaction_engine"
        
        # Core components
        self.interaction_handler = InteractionHandler()
        self.accessibility_provider = AccessibilityProvider()
        
        # State management
        self.is_initialized = False
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Interaction Engine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Interaction Engine."""
        try:
            # Register default interaction handlers
            await self._register_default_handlers()
            
            # Enable basic accessibility features
            await self.accessibility_provider.enable_keyboard_navigation()
            
            self.is_initialized = True
            logger.info("Interaction Engine initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Interaction Engine initialization failed: {e}")
            return False
    
    async def process_user_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user interaction event."""
        try:
            # Handle the interaction
            result = await self.interaction_handler.handle_interaction(interaction)
            
            # Update session tracking
            user_id = interaction.get("user_id", "anonymous")
            await self._update_session_tracking(user_id, interaction)
            
            return result
            
        except Exception as e:
            logger.error(f"User interaction processing failed: {e}")
            return {"error": str(e)}
    
    async def configure_accessibility(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure accessibility settings."""
        try:
            results = {}
            
            if settings.get("screen_reader", False):
                results["screen_reader"] = await self.accessibility_provider.enable_screen_reader_support()
            
            if settings.get("keyboard_navigation", True):
                results["keyboard_navigation"] = await self.accessibility_provider.enable_keyboard_navigation()
            
            # Update accessibility settings
            if "high_contrast" in settings:
                self.accessibility_provider.accessibility_settings.high_contrast_mode = settings["high_contrast"]
                results["high_contrast"] = True
            
            if "reduced_motion" in settings:
                self.accessibility_provider.accessibility_settings.reduced_motion = settings["reduced_motion"]
                results["reduced_motion"] = True
            
            logger.info(f"Accessibility configured: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Accessibility configuration failed: {e}")
            return {"error": str(e)}
    
    async def get_interaction_insights(self) -> Dict[str, Any]:
        """Get interaction insights and analytics."""
        try:
            analytics = await self.interaction_handler.get_interaction_analytics()
            accessibility_status = await self.accessibility_provider.get_accessibility_status()
            
            return {
                "interaction_analytics": analytics,
                "accessibility_status": accessibility_status,
                "active_sessions": len(self.active_sessions),
                "session_insights": await self._get_session_insights(),
                "engagement_metrics": await self._calculate_engagement_metrics()
            }
            
        except Exception as e:
            logger.error(f"Failed to get interaction insights: {e}")
            return {"error": str(e)}
    
    async def _register_default_handlers(self) -> None:
        """Register default interaction handlers."""
        try:
            # Register engagement-specific handlers
            await self.interaction_handler.register_interaction_handler(
                "engagement_click", 
                self._handle_engagement_click
            )
            
            await self.interaction_handler.register_interaction_handler(
                "data_exploration", 
                self._handle_data_exploration
            )
            
        except Exception as e:
            logger.error(f"Default handler registration failed: {e}")
    
    async def _handle_engagement_click(self, interaction: InteractionEvent) -> Dict[str, Any]:
        """Handle engagement-specific click interactions."""
        return {
            "action": "engagement_boost",
            "target": interaction.target_element,
            "engagement_increase": 0.2,
            "animation_triggered": True
        }
    
    async def _handle_data_exploration(self, interaction: InteractionEvent) -> Dict[str, Any]:
        """Handle data exploration interactions."""
        return {
            "action": "data_drill_down",
            "target": interaction.target_element,
            "context_layers_revealed": 2,
            "progressive_disclosure": True
        }
    
    async def _update_session_tracking(self, user_id: str, interaction: Dict[str, Any]) -> None:
        """Update session tracking for user."""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = {
                "session_start": datetime.now(),
                "interaction_count": 0,
                "last_interaction": None
            }
        
        session = self.active_sessions[user_id]
        session["interaction_count"] += 1
        session["last_interaction"] = datetime.now()
    
    async def _get_session_insights(self) -> Dict[str, Any]:
        """Get insights from active sessions."""
        if not self.active_sessions:
            return {"total_sessions": 0}
        
        total_interactions = sum(s["interaction_count"] for s in self.active_sessions.values())
        avg_interactions = total_interactions / len(self.active_sessions)
        
        return {
            "total_sessions": len(self.active_sessions),
            "average_interactions_per_session": avg_interactions,
            "total_interactions": total_interactions
        }
    
    async def _calculate_engagement_metrics(self) -> Dict[str, Any]:
        """Calculate engagement metrics from interactions."""
        analytics = await self.interaction_handler.get_interaction_analytics()
        
        return {
            "interaction_diversity": len(analytics.get("interactions_by_type", {})),
            "engagement_score": analytics.get("interaction_effectiveness", 0.0),
            "popular_elements_count": len(analytics.get("popular_elements", {})),
            "user_engagement_level": "high" if analytics.get("total_interactions", 0) > 50 else "medium"
        }
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Interaction Engine capabilities."""
        return [
            "multi_modal_interaction",
            "accessibility_support",
            "interaction_analytics",
            "session_tracking",
            "engagement_optimization"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Interaction Engine health status."""
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "active_sessions": len(self.active_sessions),
            "total_interactions": len(self.interaction_handler.interaction_history),
            "accessibility_enabled": self.accessibility_provider.accessibility_settings.screen_reader_enabled,
            "keyboard_navigation": self.accessibility_provider.accessibility_settings.keyboard_navigation_enabled
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Interaction Engine module information."""
        return {
            "module_id": self.module_id,
            "name": "Interaction Engine",
            "version": "1.0.0",
            "description": "Multi-modal user interaction processing with accessibility support"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation to basic interaction handling."""
        try:
            degradation_actions = []
            
            # Clear non-essential interaction handlers
            essential_handlers = ["click", "hover", "keyboard"]
            handlers_to_remove = [
                event_type for event_type in self.interaction_handler.interaction_handlers.keys()
                if event_type not in essential_handlers
            ]
            
            for event_type in handlers_to_remove:
                del self.interaction_handler.interaction_handlers[event_type]
            
            if handlers_to_remove:
                degradation_actions.append(f"Removed {len(handlers_to_remove)} non-essential handlers")
            
            # Clear old interaction history to save memory
            if len(self.interaction_handler.interaction_history) > 50:
                kept_interactions = self.interaction_handler.interaction_history[-50:]
                cleared_count = len(self.interaction_handler.interaction_history) - 50
                self.interaction_handler.interaction_history = kept_interactions
                degradation_actions.append(f"Cleared {cleared_count} old interaction records")
            
            # Clear inactive user sessions
            active_sessions = {}
            current_time = datetime.now()
            for user_id, session in self.active_sessions.items():
                if (current_time - session["last_activity"]).total_seconds() < 3600:  # Keep sessions active within 1 hour
                    active_sessions[user_id] = session
            
            cleared_sessions = len(self.active_sessions) - len(active_sessions)
            self.active_sessions = active_sessions
            if cleared_sessions > 0:
                degradation_actions.append(f"Cleared {cleared_sessions} inactive sessions")
            
            # Disable advanced accessibility features, keep basic ones
            self.accessibility_provider.accessibility_features = {
                "screen_reader": False,
                "keyboard_navigation": True,  # Keep this essential feature
                "high_contrast": False,
                "reduced_motion": True,  # Keep this for performance
                "focus_indicators": True   # Keep this essential feature
            }
            degradation_actions.append("Disabled advanced accessibility features")
            
            return {
                "status": "degraded",
                "actions_taken": degradation_actions,
                "active_sessions": len(self.active_sessions),
                "active_handlers": len(self.interaction_handler.interaction_handlers),
                "functionality_level": "basic_interaction_only",
                "recovery_possible": True
            }
        except Exception as e:
            return {
                "status": "degradation_failed",
                "error": str(e),
                "functionality_level": "unknown",
                "recovery_possible": False
            }