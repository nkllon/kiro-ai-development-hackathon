"""
Core Engagement System Interfaces
=================================

Defines the core interfaces that establish system boundaries and enable
modular, testable, and extensible engagement components.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import asyncio


class EngagementLevel(Enum):
    """Levels of user engagement."""
    PASSIVE = "passive"
    ACTIVE = "active"
    IMMERSIVE = "immersive"
    COLLABORATIVE = "collaborative"


class AttentionPriority(Enum):
    """Priority levels for attention management."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class EngagementContext:
    """Context information for engagement decisions."""
    user_id: Optional[str] = None
    session_duration: float = 0.0
    interaction_count: int = 0
    current_focus: Optional[str] = None
    engagement_level: EngagementLevel = EngagementLevel.PASSIVE
    system_load: float = 0.0
    data_freshness: float = 1.0


@dataclass
class AnimationFrame:
    """Single frame of animation data."""
    timestamp: float
    elements: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]


# Dashboard Engine Interfaces

class IDashboardRenderer(ABC):
    """Interface for dashboard visual rendering pipeline."""
    
    @abstractmethod
    async def render_component(self, component_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Render a dashboard component with given data."""
        pass
    
    @abstractmethod
    async def update_layout(self, layout_config: Dict[str, Any]) -> bool:
        """Update dashboard layout configuration."""
        pass
    
    @abstractmethod
    async def apply_theme(self, theme_config: Dict[str, Any]) -> bool:
        """Apply visual theme to dashboard."""
        pass


class IDataSubscriber(ABC):
    """Interface for real-time data subscription."""
    
    @abstractmethod
    async def subscribe_to_data_stream(self, stream_id: str, callback: Callable) -> bool:
        """Subscribe to a real-time data stream."""
        pass
    
    @abstractmethod
    async def unsubscribe_from_stream(self, stream_id: str) -> bool:
        """Unsubscribe from a data stream."""
        pass
    
    @abstractmethod
    async def get_latest_data(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest data from a stream."""
        pass


# Animation Engine Interfaces

class IAnimationController(ABC):
    """Interface for animation lifecycle management."""
    
    @abstractmethod
    async def start_animation(self, animation_id: str, config: Dict[str, Any]) -> bool:
        """Start an animation with given configuration."""
        pass
    
    @abstractmethod
    async def stop_animation(self, animation_id: str) -> bool:
        """Stop a running animation."""
        pass
    
    @abstractmethod
    async def update_animation(self, animation_id: str, frame_data: AnimationFrame) -> bool:
        """Update animation with new frame data."""
        pass


class IPerformanceMonitor(ABC):
    """Interface for performance monitoring and optimization."""
    
    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        pass
    
    @abstractmethod
    async def optimize_for_performance(self, target_fps: int) -> Dict[str, Any]:
        """Optimize system for target performance."""
        pass
    
    @abstractmethod
    async def detect_performance_issues(self) -> List[Dict[str, Any]]:
        """Detect current performance issues."""
        pass


# Personality Engine Interfaces

class IPersonalityProvider(ABC):
    """Interface for personality states and transitions."""
    
    @abstractmethod
    async def get_current_personality(self) -> Dict[str, Any]:
        """Get current personality state."""
        pass
    
    @abstractmethod
    async def transition_personality(self, new_state: str, context: EngagementContext) -> bool:
        """Transition to new personality state."""
        pass
    
    @abstractmethod
    async def get_personality_recommendations(self, context: EngagementContext) -> List[str]:
        """Get personality recommendations for given context."""
        pass


class IContextAnalyzer(ABC):
    """Interface for analyzing system and user context."""
    
    @abstractmethod
    async def analyze_user_context(self, user_id: str) -> EngagementContext:
        """Analyze current user context."""
        pass
    
    @abstractmethod
    async def analyze_system_context(self) -> Dict[str, Any]:
        """Analyze current system context."""
        pass
    
    @abstractmethod
    async def predict_engagement_needs(self, context: EngagementContext) -> List[str]:
        """Predict engagement needs based on context."""
        pass


class IThemeManager(ABC):
    """Interface for visual themes and moods based on system state."""
    
    @abstractmethod
    async def get_current_theme(self) -> Dict[str, Any]:
        """Get current visual theme configuration."""
        pass
    
    @abstractmethod
    async def apply_theme(self, theme_name: str, context: EngagementContext) -> bool:
        """Apply visual theme based on personality and context."""
        pass
    
    @abstractmethod
    async def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        pass
    
    @abstractmethod
    async def create_dynamic_theme(self, personality_state: str, system_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create dynamic theme based on personality and system state."""
        pass


# Attention Management Interfaces

class IAttentionPrioritizer(ABC):
    """Interface for ranking events by importance and urgency."""
    
    @abstractmethod
    async def prioritize_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize events by importance and urgency."""
        pass
    
    @abstractmethod
    async def calculate_attention_score(self, event: Dict[str, Any]) -> float:
        """Calculate attention score for an event."""
        pass
    
    @abstractmethod
    async def update_priority_rules(self, rules: Dict[str, Any]) -> bool:
        """Update priority calculation rules."""
        pass


class IFocusController(ABC):
    """Interface for managing user attention flow."""
    
    @abstractmethod
    async def set_focus(self, target: str, priority: AttentionPriority) -> bool:
        """Set user focus to specific target."""
        pass
    
    @abstractmethod
    async def clear_focus(self) -> bool:
        """Clear current focus."""
        pass
    
    @abstractmethod
    async def get_focus_history(self) -> List[Dict[str, Any]]:
        """Get history of focus changes."""
        pass


class IProgressiveDisclosure(ABC):
    """Interface for controlling information revelation."""
    
    @abstractmethod
    async def reveal_information(self, information_id: str, level: int) -> Dict[str, Any]:
        """Reveal information at specified detail level."""
        pass
    
    @abstractmethod
    async def hide_information(self, information_id: str) -> bool:
        """Hide previously revealed information."""
        pass
    
    @abstractmethod
    async def get_disclosure_level(self, information_id: str) -> int:
        """Get current disclosure level for information."""
        pass
    
    @abstractmethod
    async def set_disclosure_rules(self, rules: Dict[str, Any]) -> bool:
        """Set rules for progressive disclosure."""
        pass


# Interaction Engine Interfaces

class IInteractionHandler(ABC):
    """Interface for processing user interactions."""
    
    @abstractmethod
    async def handle_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a user interaction."""
        pass
    
    @abstractmethod
    async def register_interaction_handler(self, event_type: str, handler: Callable) -> bool:
        """Register handler for specific interaction type."""
        pass
    
    @abstractmethod
    async def get_interaction_analytics(self) -> Dict[str, Any]:
        """Get interaction analytics data."""
        pass


class IAccessibilityProvider(ABC):
    """Interface for accessibility support."""
    
    @abstractmethod
    async def enable_screen_reader_support(self) -> bool:
        """Enable screen reader support."""
        pass
    
    @abstractmethod
    async def enable_keyboard_navigation(self) -> bool:
        """Enable keyboard navigation."""
        pass
    
    @abstractmethod
    async def get_accessibility_status(self) -> Dict[str, bool]:
        """Get current accessibility feature status."""
        pass


class IMultiModalInterface(ABC):
    """Interface for audio, haptic, and visual feedback."""
    
    @abstractmethod
    async def provide_audio_feedback(self, message: str, priority: str = "normal") -> bool:
        """Provide audio feedback to user."""
        pass
    
    @abstractmethod
    async def provide_haptic_feedback(self, pattern: str, intensity: float = 0.5) -> bool:
        """Provide haptic feedback for supported devices."""
        pass
    
    @abstractmethod
    async def provide_visual_feedback(self, feedback_type: str, config: Dict[str, Any]) -> bool:
        """Provide visual feedback with animations or highlights."""
        pass
    
    @abstractmethod
    async def get_supported_modalities(self) -> List[str]:
        """Get list of supported feedback modalities."""
        pass


class ICollaborationManager(ABC):
    """Interface for multi-user interactions and shared experiences."""
    
    @abstractmethod
    async def create_shared_session(self, session_id: str, participants: List[str]) -> Dict[str, Any]:
        """Create a shared collaboration session."""
        pass
    
    @abstractmethod
    async def add_shared_cursor(self, user_id: str, position: Dict[str, float]) -> bool:
        """Add or update shared cursor position."""
        pass
    
    @abstractmethod
    async def create_annotation(self, annotation: Dict[str, Any]) -> str:
        """Create a shared annotation."""
        pass
    
    @abstractmethod
    async def add_contextual_comment(self, comment: Dict[str, Any]) -> str:
        """Add contextual comment tied to specific metrics."""
        pass
    
    @abstractmethod
    async def share_insight(self, insight: Dict[str, Any]) -> str:
        """Share knowledge insight with team."""
        pass
    
    @abstractmethod
    async def get_collaboration_state(self, session_id: str) -> Dict[str, Any]:
        """Get current collaboration state."""
        pass


class IMobileAdapter(ABC):
    """Interface for touch interface optimization and mobile adaptation."""
    
    @abstractmethod
    async def optimize_for_touch(self, interface_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize interface for touch interactions."""
        pass
    
    @abstractmethod
    async def enable_responsive_design(self, screen_size: Dict[str, int]) -> bool:
        """Enable responsive design for given screen size."""
        pass
    
    @abstractmethod
    async def configure_touch_gestures(self, gesture_config: Dict[str, Any]) -> bool:
        """Configure touch-specific interaction patterns."""
        pass
    
    @abstractmethod
    async def get_mobile_capabilities(self) -> Dict[str, Any]:
        """Get mobile device capabilities."""
        pass


# Data Storytelling Interfaces

class IPatternDetector(ABC):
    """Interface for identifying trends and anomalies in data."""
    
    @abstractmethod
    async def detect_trends(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect trends in data."""
        pass
    
    @abstractmethod
    async def detect_anomalies(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in data."""
        pass
    
    @abstractmethod
    async def find_correlations(self, datasets: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Find correlations between datasets."""
        pass


class INarrativeGenerator(ABC):
    """Interface for generating human-readable explanations."""
    
    @abstractmethod
    async def generate_narrative(self, data_insights: Dict[str, Any]) -> str:
        """Generate narrative from data insights."""
        pass
    
    @abstractmethod
    async def explain_trend(self, trend_data: Dict[str, Any]) -> str:
        """Explain a detected trend."""
        pass
    
    @abstractmethod
    async def explain_anomaly(self, anomaly_data: Dict[str, Any]) -> str:
        """Explain a detected anomaly."""
        pass


# Learning and Optimization Interfaces

class IUserBehaviorAnalyzer(ABC):
    """Interface for tracking engagement patterns."""
    
    @abstractmethod
    async def track_user_behavior(self, user_id: str, behavior_data: Dict[str, Any]) -> bool:
        """Track user behavior data."""
        pass
    
    @abstractmethod
    async def analyze_engagement_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user engagement patterns."""
        pass
    
    @abstractmethod
    async def predict_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Predict user preferences based on behavior."""
        pass


class IEngagementOptimizer(ABC):
    """Interface for strategy optimization based on analytics."""
    
    @abstractmethod
    async def optimize_engagement_strategy(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize engagement strategy based on analytics."""
        pass
    
    @abstractmethod
    async def run_ab_test(self, test_config: Dict[str, Any]) -> str:
        """Run A/B test for engagement strategies."""
        pass
    
    @abstractmethod
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations."""
        pass