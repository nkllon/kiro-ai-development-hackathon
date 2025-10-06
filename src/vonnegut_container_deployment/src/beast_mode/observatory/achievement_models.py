"""
Achievement Tracking Models for Beast Mode Observatory

This module defines the data models and enumerations for tracking coordination
achievements, milestones, and gamification elements in the Observatory system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Set
import uuid


class AchievementType(Enum):
    """Types of achievements that can be unlocked."""
    COORDINATION_MASTERY = auto()     # Excellence in coordination patterns
    SYSTEMATIC_PRACTICE = auto()     # Consistent systematic approaches
    COLLABORATION = auto()           # Effective team coordination
    INNOVATION = auto()              # Creative problem-solving approaches
    CONSISTENCY = auto()             # Regular and reliable coordination
    MILESTONE = auto()               # Significant project milestones
    LEADERSHIP = auto()              # Coordination leadership behaviors
    EFFICIENCY = auto()              # Process optimization achievements


class AchievementCategory(Enum):
    """Categories for organizing achievements."""
    DAILY = auto()                   # Daily coordination practices
    WEEKLY = auto()                  # Weekly coordination goals
    PROJECT = auto()                 # Project-specific achievements
    SYSTEM = auto()                  # System-wide coordination patterns
    PERSONAL = auto()                # Individual coordination growth
    TEAM = auto()                    # Team coordination achievements


class AchievementRarity(Enum):
    """Rarity levels for achievements."""
    COMMON = "common"               # Easy to achieve, frequent
    UNCOMMON = "uncommon"           # Moderate difficulty
    RARE = "rare"                   # Challenging achievements
    EPIC = "epic"                   # Very difficult achievements
    LEGENDARY = "legendary"         # Extremely rare achievements


class CelebrationLevel(Enum):
    """Levels of celebration for different achievements."""
    SUBTLE = "subtle"               # Minor visual feedback
    NORMAL = "normal"               # Standard celebration
    ENHANCED = "enhanced"           # More prominent celebration
    SPECTACULAR = "spectacular"     # Major celebration with effects


@dataclass
class AchievementDefinition:
    """Definition of an achievement that can be unlocked."""
    id: str
    name: str
    description: str
    achievement_type: AchievementType
    category: AchievementCategory
    rarity: AchievementRarity
    celebration_level: CelebrationLevel
    requirements: Dict[str, Any] = field(default_factory=dict)
    rewards: Dict[str, Any] = field(default_factory=dict)
    icon: Optional[str] = None
    unlock_message: Optional[str] = None
    points: int = 0
    prerequisite_achievements: List[str] = field(default_factory=list)
    is_repeatable: bool = False
    cooldown_hours: Optional[int] = None


@dataclass
class AchievementProgress:
    """Progress tracking for a specific achievement."""
    achievement_id: str
    current_progress: Dict[str, Any] = field(default_factory=dict)
    progress_percentage: float = 0.0
    first_progress_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    is_completed: bool = False
    completion_times: List[datetime] = field(default_factory=list)


@dataclass
class UnlockedAchievement:
    """Record of an unlocked achievement."""
    achievement_id: str
    unlocked_at: datetime
    unlock_context: Dict[str, Any] = field(default_factory=dict)
    celebration_triggered: bool = False
    points_awarded: int = 0
    unlock_session_id: Optional[str] = None


@dataclass
class CoordinationEvent:
    """Event that contributes to achievement progress."""
    event_id: str
    event_type: str
    timestamp: datetime
    participant_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    coordination_quality: Optional[float] = None  # 0.0 - 1.0
    systematic_score: Optional[float] = None      # 0.0 - 1.0
    collaboration_score: Optional[float] = None   # 0.0 - 1.0


@dataclass
class AchievementStats:
    """Statistics for achievement tracking."""
    total_achievements_defined: int = 0
    total_achievements_unlocked: int = 0
    total_points_earned: int = 0
    completion_rate: float = 0.0
    current_streak_days: int = 0
    longest_streak_days: int = 0
    last_achievement_unlocked: Optional[str] = None
    last_unlock_timestamp: Optional[datetime] = None
    achievements_by_rarity: Dict[str, int] = field(default_factory=dict)
    achievements_by_category: Dict[str, int] = field(default_factory=dict)


@dataclass
class CelebrationEffect:
    """Definition of celebration effects for achievements."""
    effect_id: str
    effect_type: str
    duration_ms: int = 3000
    intensity: float = 1.0
    emoji_patterns: List[str] = field(default_factory=list)
    sound_effects: List[str] = field(default_factory=list)
    visual_effects: Dict[str, Any] = field(default_factory=dict)
    custom_message: Optional[str] = None


@dataclass
class MilestoneDefinition:
    """Definition of coordination milestones."""
    milestone_id: str
    name: str
    description: str
    threshold_value: float
    metric_name: str
    evaluation_period_days: int = 7
    is_cumulative: bool = True
    celebration_effect: Optional[CelebrationEffect] = None


@dataclass
class ParticipantProfile:
    """Profile tracking for achievement participants."""
    participant_id: str
    name: Optional[str] = None
    total_points: int = 0
    achievements_unlocked: List[str] = field(default_factory=list)
    current_level: int = 1
    coordination_score: float = 0.0
    systematic_practice_score: float = 0.0
    collaboration_score: float = 0.0
    joined_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    preferences: Dict[str, Any] = field(default_factory=dict)