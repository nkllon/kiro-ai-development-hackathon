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
    IMultiModalInterface,
    ICollaborationManager,
    IMobileAdapter,
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


class MultiModalInterface(IMultiModalInterface):
    """Implementation of multi-modal feedback system."""
    
    def __init__(self):
        self.supported_modalities = ["visual", "audio", "haptic"]
        self.audio_enabled = True
        self.haptic_enabled = False  # Depends on device support
        self.visual_enabled = True
        
    async def provide_audio_feedback(self, message: str, priority: str = "normal") -> bool:
        """Provide audio feedback to user."""
        try:
            if not self.audio_enabled:
                return False
            
            # In a real implementation, this would use Web Audio API or similar
            audio_config = {
                "message": message,
                "priority": priority,
                "voice": "system",
                "rate": 1.0 if priority == "normal" else 1.2,
                "volume": 0.7 if priority == "normal" else 0.9
            }
            
            logger.info(f"Audio feedback: {message} (priority: {priority})")
            
            # Placeholder for actual audio synthesis
            # In real implementation: await self._synthesize_speech(audio_config)
            
            return True
        except Exception as e:
            logger.error(f"Audio feedback failed: {e}")
            return False
    
    async def provide_haptic_feedback(self, pattern: str, intensity: float = 0.5) -> bool:
        """Provide haptic feedback for supported devices."""
        try:
            if not self.haptic_enabled:
                return False
            
            # Validate intensity
            intensity = max(0.0, min(1.0, intensity))
            
            haptic_patterns = {
                "click": {"duration": 50, "intensity": intensity},
                "success": {"duration": 100, "intensity": intensity * 0.8},
                "error": {"duration": 200, "intensity": intensity * 1.2},
                "notification": {"duration": 150, "intensity": intensity}
            }
            
            pattern_config = haptic_patterns.get(pattern, haptic_patterns["click"])
            
            logger.info(f"Haptic feedback: {pattern} (intensity: {intensity})")
            
            # Placeholder for actual haptic feedback
            # In real implementation: await self._trigger_haptic(pattern_config)
            
            return True
        except Exception as e:
            logger.error(f"Haptic feedback failed: {e}")
            return False
    
    async def provide_visual_feedback(self, feedback_type: str, config: Dict[str, Any]) -> bool:
        """Provide visual feedback with animations or highlights."""
        try:
            if not self.visual_enabled:
                return False
            
            visual_feedback_types = {
                "highlight": {
                    "animation": "pulse",
                    "color": config.get("color", "#007bff"),
                    "duration": config.get("duration", 500)
                },
                "success": {
                    "animation": "checkmark",
                    "color": "#28a745",
                    "duration": 1000
                },
                "error": {
                    "animation": "shake",
                    "color": "#dc3545",
                    "duration": 800
                },
                "focus": {
                    "animation": "outline",
                    "color": "#007bff",
                    "duration": 300
                }
            }
            
            feedback_config = visual_feedback_types.get(feedback_type, visual_feedback_types["highlight"])
            feedback_config.update(config)  # Override with provided config
            
            logger.info(f"Visual feedback: {feedback_type} with config {feedback_config}")
            
            # Placeholder for actual visual feedback
            # In real implementation: await self._trigger_visual_animation(feedback_config)
            
            return True
        except Exception as e:
            logger.error(f"Visual feedback failed: {e}")
            return False
    
    async def get_supported_modalities(self) -> List[str]:
        """Get list of supported feedback modalities."""
        supported = []
        if self.visual_enabled:
            supported.append("visual")
        if self.audio_enabled:
            supported.append("audio")
        if self.haptic_enabled:
            supported.append("haptic")
        return supported


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


class CollaborationManager(ICollaborationManager):
    """Implementation of multi-user collaboration features."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.shared_cursors: Dict[str, Dict[str, float]] = {}
        self.annotations: Dict[str, Dict[str, Any]] = {}
        self.comments: Dict[str, Dict[str, Any]] = {}
        self.insights: Dict[str, Dict[str, Any]] = {}
        
    async def create_shared_session(self, session_id: str, participants: List[str]) -> Dict[str, Any]:
        """Create a shared collaboration session."""
        try:
            session = {
                "session_id": session_id,
                "participants": participants,
                "created_at": datetime.now(),
                "active_cursors": {},
                "annotations": [],
                "comments": [],
                "insights": [],
                "status": "active"
            }
            
            self.active_sessions[session_id] = session
            
            logger.info(f"Shared session created: {session_id} with {len(participants)} participants")
            
            return {
                "session_id": session_id,
                "status": "created",
                "participants": participants,
                "created_at": session["created_at"].isoformat()
            }
        except Exception as e:
            logger.error(f"Shared session creation failed: {e}")
            return {"error": str(e)}
    
    async def add_shared_cursor(self, user_id: str, position: Dict[str, float]) -> bool:
        """Add or update shared cursor position."""
        try:
            cursor_data = {
                "user_id": user_id,
                "x": position.get("x", 0.0),
                "y": position.get("y", 0.0),
                "timestamp": datetime.now(),
                "active": True
            }
            
            self.shared_cursors[user_id] = cursor_data
            
            # Update all active sessions with this user
            for session in self.active_sessions.values():
                if user_id in session["participants"]:
                    session["active_cursors"][user_id] = cursor_data
            
            logger.debug(f"Shared cursor updated for user {user_id}: {position}")
            return True
        except Exception as e:
            logger.error(f"Shared cursor update failed: {e}")
            return False
    
    async def create_annotation(self, annotation: Dict[str, Any]) -> str:
        """Create a shared annotation."""
        try:
            annotation_id = f"annotation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.annotations)}"
            
            annotation_data = {
                "id": annotation_id,
                "user_id": annotation.get("user_id", "anonymous"),
                "content": annotation.get("content", ""),
                "position": annotation.get("position", {"x": 0, "y": 0}),
                "target_element": annotation.get("target_element", ""),
                "created_at": datetime.now(),
                "type": annotation.get("type", "note"),
                "visibility": annotation.get("visibility", "public")
            }
            
            self.annotations[annotation_id] = annotation_data
            
            # Add to relevant sessions
            user_id = annotation_data["user_id"]
            for session in self.active_sessions.values():
                if user_id in session["participants"]:
                    session["annotations"].append(annotation_data)
            
            logger.info(f"Annotation created: {annotation_id} by {user_id}")
            return annotation_id
        except Exception as e:
            logger.error(f"Annotation creation failed: {e}")
            return ""
    
    async def add_contextual_comment(self, comment: Dict[str, Any]) -> str:
        """Add contextual comment tied to specific metrics."""
        try:
            comment_id = f"comment_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.comments)}"
            
            comment_data = {
                "id": comment_id,
                "user_id": comment.get("user_id", "anonymous"),
                "content": comment.get("content", ""),
                "metric_id": comment.get("metric_id", ""),
                "timeframe": comment.get("timeframe", ""),
                "context": comment.get("context", {}),
                "created_at": datetime.now(),
                "replies": [],
                "tags": comment.get("tags", [])
            }
            
            self.comments[comment_id] = comment_data
            
            # Add to relevant sessions
            user_id = comment_data["user_id"]
            for session in self.active_sessions.values():
                if user_id in session["participants"]:
                    session["comments"].append(comment_data)
            
            logger.info(f"Contextual comment added: {comment_id} for metric {comment_data['metric_id']}")
            return comment_id
        except Exception as e:
            logger.error(f"Contextual comment creation failed: {e}")
            return ""
    
    async def share_insight(self, insight: Dict[str, Any]) -> str:
        """Share knowledge insight with team."""
        try:
            insight_id = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.insights)}"
            
            insight_data = {
                "id": insight_id,
                "user_id": insight.get("user_id", "anonymous"),
                "title": insight.get("title", ""),
                "description": insight.get("description", ""),
                "data_source": insight.get("data_source", ""),
                "discovery_method": insight.get("discovery_method", "manual"),
                "impact_level": insight.get("impact_level", "medium"),
                "actionable_items": insight.get("actionable_items", []),
                "created_at": datetime.now(),
                "shared_with": insight.get("shared_with", []),
                "category": insight.get("category", "general")
            }
            
            self.insights[insight_id] = insight_data
            
            # Add to relevant sessions
            user_id = insight_data["user_id"]
            for session in self.active_sessions.values():
                if user_id in session["participants"]:
                    session["insights"].append(insight_data)
            
            logger.info(f"Knowledge insight shared: {insight_id} by {user_id}")
            return insight_id
        except Exception as e:
            logger.error(f"Insight sharing failed: {e}")
            return ""
    
    async def get_collaboration_state(self, session_id: str) -> Dict[str, Any]:
        """Get current collaboration state."""
        try:
            if session_id not in self.active_sessions:
                return {"error": "Session not found"}
            
            session = self.active_sessions[session_id]
            
            return {
                "session_id": session_id,
                "participants": session["participants"],
                "active_cursors": len(session["active_cursors"]),
                "annotations_count": len(session["annotations"]),
                "comments_count": len(session["comments"]),
                "insights_count": len(session["insights"]),
                "created_at": session["created_at"].isoformat(),
                "status": session["status"],
                "recent_activity": await self._get_recent_activity(session_id)
            }
        except Exception as e:
            logger.error(f"Collaboration state retrieval failed: {e}")
            return {"error": str(e)}
    
    async def _get_recent_activity(self, session_id: str) -> List[Dict[str, Any]]:
        """Get recent activity for a session."""
        try:
            session = self.active_sessions.get(session_id, {})
            activities = []
            
            # Recent annotations
            for annotation in session.get("annotations", [])[-5:]:  # Last 5
                activities.append({
                    "type": "annotation",
                    "user_id": annotation["user_id"],
                    "timestamp": annotation["created_at"].isoformat(),
                    "content": annotation["content"][:50] + "..." if len(annotation["content"]) > 50 else annotation["content"]
                })
            
            # Recent comments
            for comment in session.get("comments", [])[-5:]:  # Last 5
                activities.append({
                    "type": "comment",
                    "user_id": comment["user_id"],
                    "timestamp": comment["created_at"].isoformat(),
                    "content": comment["content"][:50] + "..." if len(comment["content"]) > 50 else comment["content"]
                })
            
            # Recent insights
            for insight in session.get("insights", [])[-3:]:  # Last 3
                activities.append({
                    "type": "insight",
                    "user_id": insight["user_id"],
                    "timestamp": insight["created_at"].isoformat(),
                    "title": insight["title"]
                })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return activities[:10]  # Return top 10 most recent
        except Exception as e:
            logger.error(f"Recent activity retrieval failed: {e}")
            return []


class MobileAdapter(IMobileAdapter):
    """Implementation of mobile touch interface optimization."""
    
    def __init__(self):
        self.touch_enabled = False
        self.responsive_design_active = False
        self.current_screen_size = {"width": 1920, "height": 1080}
        self.touch_gestures = {}
        
    async def optimize_for_touch(self, interface_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize interface for touch interactions."""
        try:
            optimizations = {
                "button_size_increase": 1.5,  # Increase button sizes by 50%
                "touch_target_minimum": 44,   # Minimum 44px touch targets
                "spacing_increase": 1.3,      # Increase spacing by 30%
                "gesture_support": True,
                "scroll_optimization": True
            }
            
            # Apply interface-specific optimizations
            if interface_config.get("component_type") == "dashboard":
                optimizations.update({
                    "chart_touch_zoom": True,
                    "swipe_navigation": True,
                    "pinch_to_zoom": True
                })
            elif interface_config.get("component_type") == "form":
                optimizations.update({
                    "input_field_enlargement": True,
                    "virtual_keyboard_support": True,
                    "touch_friendly_dropdowns": True
                })
            
            self.touch_enabled = True
            
            logger.info(f"Touch optimization applied: {optimizations}")
            return optimizations
        except Exception as e:
            logger.error(f"Touch optimization failed: {e}")
            return {"error": str(e)}
    
    async def enable_responsive_design(self, screen_size: Dict[str, int]) -> bool:
        """Enable responsive design for given screen size."""
        try:
            self.current_screen_size = screen_size
            width = screen_size.get("width", 1920)
            height = screen_size.get("height", 1080)
            
            # Determine device category
            if width <= 480:
                device_category = "mobile_small"
            elif width <= 768:
                device_category = "mobile_large"
            elif width <= 1024:
                device_category = "tablet"
            else:
                device_category = "desktop"
            
            # Apply responsive design rules
            responsive_config = {
                "device_category": device_category,
                "layout_columns": self._get_layout_columns(device_category),
                "font_scale": self._get_font_scale(device_category),
                "component_spacing": self._get_component_spacing(device_category),
                "navigation_style": self._get_navigation_style(device_category)
            }
            
            self.responsive_design_active = True
            
            logger.info(f"Responsive design enabled for {device_category}: {width}x{height}")
            return True
        except Exception as e:
            logger.error(f"Responsive design enablement failed: {e}")
            return False
    
    async def configure_touch_gestures(self, gesture_config: Dict[str, Any]) -> bool:
        """Configure touch-specific interaction patterns."""
        try:
            default_gestures = {
                "tap": {"enabled": True, "action": "click"},
                "double_tap": {"enabled": True, "action": "zoom"},
                "long_press": {"enabled": True, "action": "context_menu"},
                "swipe_left": {"enabled": True, "action": "navigate_back"},
                "swipe_right": {"enabled": True, "action": "navigate_forward"},
                "pinch": {"enabled": True, "action": "zoom"},
                "two_finger_scroll": {"enabled": True, "action": "scroll"}
            }
            
            # Update with provided configuration
            self.touch_gestures = {**default_gestures, **gesture_config}
            
            logger.info(f"Touch gestures configured: {len(self.touch_gestures)} gestures")
            return True
        except Exception as e:
            logger.error(f"Touch gesture configuration failed: {e}")
            return False
    
    async def get_mobile_capabilities(self) -> Dict[str, Any]:
        """Get mobile device capabilities."""
        return {
            "touch_enabled": self.touch_enabled,
            "responsive_design_active": self.responsive_design_active,
            "current_screen_size": self.current_screen_size,
            "supported_gestures": list(self.touch_gestures.keys()),
            "device_category": self._get_device_category(),
            "orientation_support": True,
            "haptic_feedback_available": False,  # Would be detected from device
            "camera_available": False,  # Would be detected from device
            "geolocation_available": False  # Would be detected from device
        }
    
    def _get_layout_columns(self, device_category: str) -> int:
        """Get number of layout columns for device category."""
        column_map = {
            "mobile_small": 1,
            "mobile_large": 1,
            "tablet": 2,
            "desktop": 3
        }
        return column_map.get(device_category, 3)
    
    def _get_font_scale(self, device_category: str) -> float:
        """Get font scale factor for device category."""
        scale_map = {
            "mobile_small": 0.9,
            "mobile_large": 1.0,
            "tablet": 1.1,
            "desktop": 1.0
        }
        return scale_map.get(device_category, 1.0)
    
    def _get_component_spacing(self, device_category: str) -> str:
        """Get component spacing for device category."""
        spacing_map = {
            "mobile_small": "compact",
            "mobile_large": "normal",
            "tablet": "comfortable",
            "desktop": "normal"
        }
        return spacing_map.get(device_category, "normal")
    
    def _get_navigation_style(self, device_category: str) -> str:
        """Get navigation style for device category."""
        nav_map = {
            "mobile_small": "bottom_tabs",
            "mobile_large": "bottom_tabs",
            "tablet": "side_drawer",
            "desktop": "top_navigation"
        }
        return nav_map.get(device_category, "top_navigation")
    
    def _get_device_category(self) -> str:
        """Get current device category."""
        width = self.current_screen_size.get("width", 1920)
        if width <= 480:
            return "mobile_small"
        elif width <= 768:
            return "mobile_large"
        elif width <= 1024:
            return "tablet"
        else:
            return "desktop"


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
        self.multimodal_interface = MultiModalInterface()
        self.collaboration_manager = CollaborationManager()
        self.mobile_adapter = MobileAdapter()
        
        # State management
        self.is_initialized = False
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Interaction Engine initialized with all components")
    
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
    
    async def provide_multimodal_feedback(self, feedback_config: Dict[str, Any]) -> Dict[str, Any]:
        """Provide multi-modal feedback (audio, haptic, visual)."""
        try:
            results = {}
            
            if feedback_config.get("audio"):
                audio_config = feedback_config["audio"]
                results["audio"] = await self.multimodal_interface.provide_audio_feedback(
                    audio_config.get("message", ""),
                    audio_config.get("priority", "normal")
                )
            
            if feedback_config.get("haptic"):
                haptic_config = feedback_config["haptic"]
                results["haptic"] = await self.multimodal_interface.provide_haptic_feedback(
                    haptic_config.get("pattern", "click"),
                    haptic_config.get("intensity", 0.5)
                )
            
            if feedback_config.get("visual"):
                visual_config = feedback_config["visual"]
                results["visual"] = await self.multimodal_interface.provide_visual_feedback(
                    visual_config.get("type", "highlight"),
                    visual_config.get("config", {})
                )
            
            return results
        except Exception as e:
            logger.error(f"Multi-modal feedback failed: {e}")
            return {"error": str(e)}
    
    async def create_collaboration_session(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new collaboration session."""
        try:
            session_id = session_config.get("session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            participants = session_config.get("participants", [])
            
            result = await self.collaboration_manager.create_shared_session(session_id, participants)
            
            # Also track in our active sessions
            if "error" not in result:
                self.active_sessions[session_id] = {
                    "type": "collaboration",
                    "created_at": datetime.now(),
                    "participants": participants
                }
            
            return result
        except Exception as e:
            logger.error(f"Collaboration session creation failed: {e}")
            return {"error": str(e)}
    
    async def add_collaboration_annotation(self, annotation_config: Dict[str, Any]) -> str:
        """Add a collaboration annotation."""
        try:
            return await self.collaboration_manager.create_annotation(annotation_config)
        except Exception as e:
            logger.error(f"Collaboration annotation failed: {e}")
            return ""
    
    async def add_contextual_comment(self, comment_config: Dict[str, Any]) -> str:
        """Add a contextual comment tied to specific metrics."""
        try:
            return await self.collaboration_manager.add_contextual_comment(comment_config)
        except Exception as e:
            logger.error(f"Contextual comment failed: {e}")
            return ""
    
    async def share_knowledge_insight(self, insight_config: Dict[str, Any]) -> str:
        """Share a knowledge insight with the team."""
        try:
            return await self.collaboration_manager.share_insight(insight_config)
        except Exception as e:
            logger.error(f"Knowledge insight sharing failed: {e}")
            return ""
    
    async def optimize_for_mobile(self, mobile_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize interface for mobile devices."""
        try:
            results = {}
            
            # Enable responsive design if screen size provided
            if "screen_size" in mobile_config:
                results["responsive_design"] = await self.mobile_adapter.enable_responsive_design(
                    mobile_config["screen_size"]
                )
            
            # Optimize for touch if requested
            if mobile_config.get("enable_touch", False):
                results["touch_optimization"] = await self.mobile_adapter.optimize_for_touch(
                    mobile_config.get("interface_config", {})
                )
            
            # Configure touch gestures if provided
            if "gestures" in mobile_config:
                results["gesture_configuration"] = await self.mobile_adapter.configure_touch_gestures(
                    mobile_config["gestures"]
                )
            
            return results
        except Exception as e:
            logger.error(f"Mobile optimization failed: {e}")
            return {"error": str(e)}
    
    async def get_interaction_insights(self) -> Dict[str, Any]:
        """Get interaction insights and analytics."""
        try:
            analytics = await self.interaction_handler.get_interaction_analytics()
            accessibility_status = await self.accessibility_provider.get_accessibility_status()
            multimodal_capabilities = await self.multimodal_interface.get_supported_modalities()
            mobile_capabilities = await self.mobile_adapter.get_mobile_capabilities()
            
            return {
                "interaction_analytics": analytics,
                "accessibility_status": accessibility_status,
                "multimodal_capabilities": multimodal_capabilities,
                "mobile_capabilities": mobile_capabilities,
                "active_sessions": len(self.active_sessions),
                "collaboration_sessions": len(self.collaboration_manager.active_sessions),
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
            "engagement_optimization",
            "audio_feedback",
            "haptic_feedback", 
            "visual_feedback",
            "collaborative_annotations",
            "contextual_comments",
            "knowledge_sharing",
            "shared_cursors",
            "mobile_optimization",
            "touch_interface_support",
            "responsive_design",
            "gesture_recognition"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Interaction Engine health status."""
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "active_sessions": len(self.active_sessions),
            "collaboration_sessions": len(self.collaboration_manager.active_sessions),
            "total_interactions": len(self.interaction_handler.interaction_history),
            "accessibility_enabled": self.accessibility_provider.accessibility_settings.screen_reader_enabled,
            "keyboard_navigation": self.accessibility_provider.accessibility_settings.keyboard_navigation_enabled,
            "multimodal_capabilities": len(self.multimodal_interface.supported_modalities),
            "mobile_optimization": self.mobile_adapter.touch_enabled,
            "responsive_design": self.mobile_adapter.responsive_design_active,
            "components": {
                "interaction_handler": "active",
                "accessibility_provider": "active", 
                "multimodal_interface": "active",
                "collaboration_manager": "active",
                "mobile_adapter": "active"
            }
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
            self.accessibility_provider.accessibility_settings.screen_reader_enabled = False
            self.accessibility_provider.accessibility_settings.high_contrast_mode = False
            self.accessibility_provider.accessibility_settings.audio_descriptions = False
            # Keep keyboard navigation and reduced motion for essential functionality
            degradation_actions.append("Disabled advanced accessibility features")
            
            # Disable resource-intensive multimodal features
            self.multimodal_interface.audio_enabled = False
            self.multimodal_interface.haptic_enabled = False
            # Keep visual feedback as it's essential
            degradation_actions.append("Disabled audio and haptic feedback")
            
            # Simplify collaboration features
            if len(self.collaboration_manager.active_sessions) > 5:
                # Keep only the 5 most recent sessions
                sessions_to_keep = dict(list(self.collaboration_manager.active_sessions.items())[-5:])
                removed_sessions = len(self.collaboration_manager.active_sessions) - 5
                self.collaboration_manager.active_sessions = sessions_to_keep
                degradation_actions.append(f"Reduced collaboration sessions from {removed_sessions + 5} to 5")
            
            # Disable advanced mobile features
            self.mobile_adapter.touch_gestures = {
                "tap": {"enabled": True, "action": "click"},  # Keep basic tap
                "scroll": {"enabled": True, "action": "scroll"}  # Keep basic scroll
            }
            degradation_actions.append("Simplified mobile touch gestures to basic tap and scroll")
            
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