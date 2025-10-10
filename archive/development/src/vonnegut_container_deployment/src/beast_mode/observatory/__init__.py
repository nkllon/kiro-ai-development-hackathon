"""
Beast Mode Coordination Observatory

A real-time monitoring and visualization system that transforms systematic coordination
from necessary overhead into an engaging, rewarding experience.
"""

from .models import (
    CoordinationEvent,
    CoordinationEventType,
    CoordinationMetrics,
    LLMMetrics,
    CostMetrics,
    HealthScore,
    Anomaly,
    Achievement,
    EmojiRainEffect,
    ObservatoryConfig,
)

from .core import ObservatoryCoreEngine
from .config import load_observatory_config
from .redis_streams import ObservatoryRedisStreams
from .emoji_rain import EmojiRainEngine, EmojiRainWebSocketHandler

# Achievement Tracking System
from .achievement_models import (
    AchievementType,
    AchievementCategory,
    AchievementRarity,
    CelebrationLevel,
    AchievementDefinition,
    AchievementProgress,
    UnlockedAchievement,
    CoordinationEvent as AchievementCoordinationEvent,
)
from .achievement_tracker import AchievementTracker
from .emoji_rain_integration import EmojiRainIntegration, EmojiRainPattern, CelebrationTrigger
from .achievement_display import AchievementDisplay

# Optional web interface and server (requires FastAPI)
try:
    from .web_interface import ObservatoryWebInterface
    from .server import ObservatoryServer, create_server
    WEB_INTERFACE_AVAILABLE = True
except ImportError:
    ObservatoryWebInterface = None
    ObservatoryServer = None
    create_server = None
    WEB_INTERFACE_AVAILABLE = False

__all__ = [
    "CoordinationEvent",
    "CoordinationEventType",
    "CoordinationMetrics",
    "LLMMetrics",
    "CostMetrics",
    "HealthScore",
    "Anomaly",
    "Achievement",
    "EmojiRainEffect",
    "ObservatoryConfig",
    "ObservatoryCoreEngine",
    "load_observatory_config",
    "ObservatoryRedisStreams",
    "EmojiRainEngine",
    "EmojiRainWebSocketHandler",
    # Achievement Tracking System
    "AchievementType",
    "AchievementCategory",
    "AchievementRarity",
    "CelebrationLevel",
    "AchievementDefinition",
    "AchievementProgress",
    "UnlockedAchievement",
    "AchievementCoordinationEvent",
    "AchievementTracker",
    "EmojiRainIntegration",
    "EmojiRainPattern",
    "CelebrationTrigger",
    "AchievementDisplay",
    "ObservatoryWebInterface",
    "ObservatoryServer",
    "create_server",
    "WEB_INTERFACE_AVAILABLE",
]