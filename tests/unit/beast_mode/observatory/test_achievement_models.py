"""
Comprehensive unit tests for the Observatory Achievement Models system.

Tests achievement definitions, progress tracking, celebration effects,
and gamification data models for systematic coordination.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
import uuid

from src.beast_mode.observatory.achievement_models import (
    AchievementType,
    AchievementCategory,
    AchievementRarity,
    CelebrationLevel,
    AchievementDefinition,
    AchievementProgress,
    UnlockedAchievement,
    CoordinationEvent,
    AchievementStats,
    CelebrationEffect,
    MilestoneDefinition,
    ParticipantProfile
)


class TestAchievementEnums:
    """Test achievement enumeration types."""

    def test_achievement_type_enum(self):
        """Test AchievementType enum values."""
        assert AchievementType.COORDINATION_MASTERY
        assert AchievementType.SYSTEMATIC_PRACTICE
        assert AchievementType.COLLABORATION
        assert AchievementType.INNOVATION
        assert AchievementType.CONSISTENCY
        assert AchievementType.MILESTONE
        assert AchievementType.LEADERSHIP
        assert AchievementType.EFFICIENCY

        # Verify all enum values are unique
        values = [item.value for item in AchievementType]
        assert len(values) == len(set(values))

    def test_achievement_category_enum(self):
        """Test AchievementCategory enum values."""
        assert AchievementCategory.DAILY
        assert AchievementCategory.WEEKLY
        assert AchievementCategory.PROJECT
        assert AchievementCategory.SYSTEM
        assert AchievementCategory.PERSONAL
        assert AchievementCategory.TEAM

        # Verify all enum values are unique
        values = [item.value for item in AchievementCategory]
        assert len(values) == len(set(values))

    def test_achievement_rarity_enum(self):
        """Test AchievementRarity enum values."""
        assert AchievementRarity.COMMON.value == "common"
        assert AchievementRarity.UNCOMMON.value == "uncommon"
        assert AchievementRarity.RARE.value == "rare"
        assert AchievementRarity.EPIC.value == "epic"
        assert AchievementRarity.LEGENDARY.value == "legendary"

    def test_celebration_level_enum(self):
        """Test CelebrationLevel enum values."""
        assert CelebrationLevel.SUBTLE.value == "subtle"
        assert CelebrationLevel.NORMAL.value == "normal"
        assert CelebrationLevel.ENHANCED.value == "enhanced"
        assert CelebrationLevel.SPECTACULAR.value == "spectacular"


class TestAchievementDefinition:
    """Test AchievementDefinition data class."""

    def test_achievement_definition_creation_minimal(self):
        """Test creating AchievementDefinition with minimal required fields."""
        achievement = AchievementDefinition(
            id="test_achievement_1",
            name="First Test Achievement",
            description="A basic achievement for testing",
            achievement_type=AchievementType.COORDINATION_MASTERY,
            category=AchievementCategory.DAILY,
            rarity=AchievementRarity.COMMON,
            celebration_level=CelebrationLevel.NORMAL
        )

        assert achievement.id == "test_achievement_1"
        assert achievement.name == "First Test Achievement"
        assert achievement.description == "A basic achievement for testing"
        assert achievement.achievement_type == AchievementType.COORDINATION_MASTERY
        assert achievement.category == AchievementCategory.DAILY
        assert achievement.rarity == AchievementRarity.COMMON
        assert achievement.celebration_level == CelebrationLevel.NORMAL

        # Check default values
        assert achievement.requirements == {}
        assert achievement.rewards == {}
        assert achievement.icon is None
        assert achievement.unlock_message is None
        assert achievement.points == 0
        assert achievement.prerequisite_achievements == []
        assert achievement.is_repeatable is False
        assert achievement.cooldown_hours is None

    def test_achievement_definition_creation_complete(self):
        """Test creating AchievementDefinition with all fields."""
        requirements = {
            "coordination_events": 10,
            "quality_threshold": 0.8,
            "consecutive_days": 7
        }
        rewards = {
            "points": 100,
            "badge": "coordination_master",
            "title": "Coordination Champion"
        }
        prerequisites = ["basic_coordination", "team_player"]

        achievement = AchievementDefinition(
            id="master_coordinator",
            name="Master Coordinator",
            description="Demonstrate exceptional coordination skills over a week",
            achievement_type=AchievementType.COORDINATION_MASTERY,
            category=AchievementCategory.WEEKLY,
            rarity=AchievementRarity.EPIC,
            celebration_level=CelebrationLevel.SPECTACULAR,
            requirements=requirements,
            rewards=rewards,
            icon="🎯",
            unlock_message="Congratulations! You've mastered coordination!",
            points=100,
            prerequisite_achievements=prerequisites,
            is_repeatable=True,
            cooldown_hours=168  # One week
        )

        assert achievement.requirements == requirements
        assert achievement.rewards == rewards
        assert achievement.icon == "🎯"
        assert achievement.unlock_message == "Congratulations! You've mastered coordination!"
        assert achievement.points == 100
        assert achievement.prerequisite_achievements == prerequisites
        assert achievement.is_repeatable is True
        assert achievement.cooldown_hours == 168

    def test_achievement_definition_with_complex_requirements(self):
        """Test achievement definition with complex requirements structure."""
        complex_requirements = {
            "coordination_metrics": {
                "min_score": 0.85,
                "consistency_threshold": 0.9
            },
            "time_constraints": {
                "evaluation_period_days": 14,
                "minimum_activity_days": 10
            },
            "collaboration": {
                "min_team_interactions": 5,
                "cross_functional_work": True
            }
        }

        achievement = AchievementDefinition(
            id="systematic_excellence",
            name="Systematic Excellence",
            description="Achieve consistent high-quality coordination",
            achievement_type=AchievementType.SYSTEMATIC_PRACTICE,
            category=AchievementCategory.SYSTEM,
            rarity=AchievementRarity.RARE,
            celebration_level=CelebrationLevel.ENHANCED,
            requirements=complex_requirements
        )

        assert achievement.requirements["coordination_metrics"]["min_score"] == 0.85
        assert achievement.requirements["time_constraints"]["evaluation_period_days"] == 14
        assert achievement.requirements["collaboration"]["cross_functional_work"] is True


class TestAchievementProgress:
    """Test AchievementProgress data class."""

    def test_achievement_progress_creation_empty(self):
        """Test creating empty AchievementProgress."""
        progress = AchievementProgress(achievement_id="test_achievement")

        assert progress.achievement_id == "test_achievement"
        assert progress.current_progress == {}
        assert progress.progress_percentage == 0.0
        assert progress.first_progress_at is None
        assert progress.last_updated_at is None
        assert progress.is_completed is False
        assert progress.completion_times == []

    def test_achievement_progress_with_data(self):
        """Test AchievementProgress with progress data."""
        current_time = datetime.now()
        first_progress = current_time - timedelta(days=3)

        current_progress = {
            "coordination_events": 7,
            "quality_score": 0.85,
            "consecutive_days": 3
        }
        completion_times = [current_time - timedelta(hours=1)]

        progress = AchievementProgress(
            achievement_id="weekly_coordinator",
            current_progress=current_progress,
            progress_percentage=70.0,
            first_progress_at=first_progress,
            last_updated_at=current_time,
            is_completed=True,
            completion_times=completion_times
        )

        assert progress.current_progress["coordination_events"] == 7
        assert progress.progress_percentage == 70.0
        assert progress.first_progress_at == first_progress
        assert progress.last_updated_at == current_time
        assert progress.is_completed is True
        assert len(progress.completion_times) == 1

    def test_achievement_progress_percentage_validation(self):
        """Test achievement progress percentage edge cases."""
        # Test with 100% completion
        progress = AchievementProgress(
            achievement_id="completed_achievement",
            progress_percentage=100.0,
            is_completed=True
        )
        assert progress.progress_percentage == 100.0
        assert progress.is_completed is True

        # Test with over 100% (edge case)
        progress_over = AchievementProgress(
            achievement_id="over_achievement",
            progress_percentage=150.0
        )
        assert progress_over.progress_percentage == 150.0

    def test_achievement_progress_completion_tracking(self):
        """Test tracking multiple completions for repeatable achievements."""
        completion_times = [
            datetime.now() - timedelta(days=7),
            datetime.now() - timedelta(days=14),
            datetime.now() - timedelta(days=21)
        ]

        progress = AchievementProgress(
            achievement_id="repeatable_achievement",
            is_completed=True,
            completion_times=completion_times
        )

        assert len(progress.completion_times) == 3
        # Completions should be in order
        for i in range(len(completion_times) - 1):
            assert completion_times[i] > completion_times[i + 1]


class TestUnlockedAchievement:
    """Test UnlockedAchievement data class."""

    def test_unlocked_achievement_creation_minimal(self):
        """Test creating UnlockedAchievement with minimal data."""
        unlock_time = datetime.now()
        unlocked = UnlockedAchievement(
            achievement_id="first_achievement",
            unlocked_at=unlock_time
        )

        assert unlocked.achievement_id == "first_achievement"
        assert unlocked.unlocked_at == unlock_time
        assert unlocked.unlock_context == {}
        assert unlocked.celebration_triggered is False
        assert unlocked.points_awarded == 0
        assert unlocked.unlock_session_id is None

    def test_unlocked_achievement_creation_complete(self):
        """Test creating UnlockedAchievement with complete data."""
        unlock_time = datetime.now()
        unlock_context = {
            "trigger_event": "coordination_milestone_reached",
            "coordination_score": 0.92,
            "team_members": ["alice", "bob", "charlie"],
            "project_phase": "implementation"
        }
        session_id = str(uuid.uuid4())

        unlocked = UnlockedAchievement(
            achievement_id="collaboration_master",
            unlocked_at=unlock_time,
            unlock_context=unlock_context,
            celebration_triggered=True,
            points_awarded=150,
            unlock_session_id=session_id
        )

        assert unlocked.unlock_context["trigger_event"] == "coordination_milestone_reached"
        assert unlocked.unlock_context["coordination_score"] == 0.92
        assert unlocked.unlock_context["team_members"] == ["alice", "bob", "charlie"]
        assert unlocked.celebration_triggered is True
        assert unlocked.points_awarded == 150
        assert unlocked.unlock_session_id == session_id

    def test_unlocked_achievement_context_validation(self):
        """Test various unlock contexts are properly stored."""
        contexts = [
            {"simple": "value"},
            {"nested": {"deep": {"value": 123}}},
            {"list": [1, 2, 3, {"nested": "item"}]},
            {"mixed": {"string": "text", "number": 42, "boolean": True}}
        ]

        for i, context in enumerate(contexts):
            unlocked = UnlockedAchievement(
                achievement_id=f"test_achievement_{i}",
                unlocked_at=datetime.now(),
                unlock_context=context
            )
            assert unlocked.unlock_context == context


class TestCoordinationEvent:
    """Test CoordinationEvent data class."""

    def test_coordination_event_creation_minimal(self):
        """Test creating CoordinationEvent with minimal fields."""
        event_time = datetime.now()
        event = CoordinationEvent(
            event_id="event_001",
            event_type="task_completion",
            timestamp=event_time
        )

        assert event.event_id == "event_001"
        assert event.event_type == "task_completion"
        assert event.timestamp == event_time
        assert event.participant_id is None
        assert event.context == {}
        assert event.coordination_quality is None
        assert event.systematic_score is None
        assert event.collaboration_score is None

    def test_coordination_event_creation_complete(self):
        """Test creating CoordinationEvent with all fields."""
        event_time = datetime.now()
        context = {
            "task_id": "TASK-123",
            "project": "coordination_system",
            "duration_minutes": 45,
            "tools_used": ["planning", "review", "collaboration"]
        }

        event = CoordinationEvent(
            event_id="event_comprehensive",
            event_type="systematic_coordination",
            timestamp=event_time,
            participant_id="user_alice",
            context=context,
            coordination_quality=0.92,
            systematic_score=0.88,
            collaboration_score=0.95
        )

        assert event.participant_id == "user_alice"
        assert event.context["task_id"] == "TASK-123"
        assert event.context["duration_minutes"] == 45
        assert event.coordination_quality == 0.92
        assert event.systematic_score == 0.88
        assert event.collaboration_score == 0.95

    def test_coordination_event_score_ranges(self):
        """Test coordination event with various score ranges."""
        # Test with perfect scores
        event_perfect = CoordinationEvent(
            event_id="perfect_event",
            event_type="excellence",
            timestamp=datetime.now(),
            coordination_quality=1.0,
            systematic_score=1.0,
            collaboration_score=1.0
        )

        assert event_perfect.coordination_quality == 1.0
        assert event_perfect.systematic_score == 1.0
        assert event_perfect.collaboration_score == 1.0

        # Test with minimum scores
        event_minimum = CoordinationEvent(
            event_id="minimum_event",
            event_type="basic",
            timestamp=datetime.now(),
            coordination_quality=0.0,
            systematic_score=0.0,
            collaboration_score=0.0
        )

        assert event_minimum.coordination_quality == 0.0
        assert event_minimum.systematic_score == 0.0
        assert event_minimum.collaboration_score == 0.0


class TestAchievementStats:
    """Test AchievementStats data class."""

    def test_achievement_stats_creation_empty(self):
        """Test creating empty AchievementStats."""
        stats = AchievementStats()

        assert stats.total_achievements_defined == 0
        assert stats.total_achievements_unlocked == 0
        assert stats.total_points_earned == 0
        assert stats.completion_rate == 0.0
        assert stats.current_streak_days == 0
        assert stats.longest_streak_days == 0
        assert stats.last_achievement_unlocked is None
        assert stats.last_unlock_timestamp is None
        assert stats.achievements_by_rarity == {}
        assert stats.achievements_by_category == {}

    def test_achievement_stats_with_data(self):
        """Test AchievementStats with complete data."""
        last_unlock = datetime.now() - timedelta(hours=2)
        rarity_breakdown = {
            "common": 5,
            "uncommon": 3,
            "rare": 2,
            "epic": 1,
            "legendary": 0
        }
        category_breakdown = {
            "daily": 4,
            "weekly": 3,
            "project": 2,
            "system": 1,
            "personal": 1
        }

        stats = AchievementStats(
            total_achievements_defined=25,
            total_achievements_unlocked=11,
            total_points_earned=1250,
            completion_rate=44.0,
            current_streak_days=12,
            longest_streak_days=18,
            last_achievement_unlocked="coordination_master",
            last_unlock_timestamp=last_unlock,
            achievements_by_rarity=rarity_breakdown,
            achievements_by_category=category_breakdown
        )

        assert stats.total_achievements_defined == 25
        assert stats.total_achievements_unlocked == 11
        assert stats.completion_rate == 44.0
        assert stats.current_streak_days == 12
        assert stats.last_achievement_unlocked == "coordination_master"
        assert stats.achievements_by_rarity["rare"] == 2
        assert stats.achievements_by_category["daily"] == 4

    def test_achievement_stats_completion_rate_calculation(self):
        """Test completion rate calculations."""
        # Test 100% completion
        stats_complete = AchievementStats(
            total_achievements_defined=10,
            total_achievements_unlocked=10,
            completion_rate=100.0
        )
        assert stats_complete.completion_rate == 100.0

        # Test partial completion
        stats_partial = AchievementStats(
            total_achievements_defined=20,
            total_achievements_unlocked=7,
            completion_rate=35.0
        )
        assert stats_partial.completion_rate == 35.0


class TestCelebrationEffect:
    """Test CelebrationEffect data class."""

    def test_celebration_effect_creation_minimal(self):
        """Test creating CelebrationEffect with minimal data."""
        effect = CelebrationEffect(
            effect_id="basic_celebration",
            effect_type="emoji_rain"
        )

        assert effect.effect_id == "basic_celebration"
        assert effect.effect_type == "emoji_rain"
        assert effect.duration_ms == 3000
        assert effect.intensity == 1.0
        assert effect.emoji_patterns == []
        assert effect.sound_effects == []
        assert effect.visual_effects == {}
        assert effect.custom_message is None

    def test_celebration_effect_creation_complete(self):
        """Test creating CelebrationEffect with all customizations."""
        emoji_patterns = ["🎉", "⭐", "🏆", "✨"]
        sound_effects = ["fanfare.mp3", "applause.wav"]
        visual_effects = {
            "particle_count": 100,
            "colors": ["gold", "silver", "bronze"],
            "animation_type": "burst",
            "fade_duration": 2000
        }

        effect = CelebrationEffect(
            effect_id="epic_milestone_celebration",
            effect_type="spectacular_display",
            duration_ms=5000,
            intensity=1.5,
            emoji_patterns=emoji_patterns,
            sound_effects=sound_effects,
            visual_effects=visual_effects,
            custom_message="Outstanding coordination achievement!"
        )

        assert effect.duration_ms == 5000
        assert effect.intensity == 1.5
        assert effect.emoji_patterns == emoji_patterns
        assert effect.sound_effects == sound_effects
        assert effect.visual_effects["particle_count"] == 100
        assert effect.visual_effects["animation_type"] == "burst"
        assert effect.custom_message == "Outstanding coordination achievement!"

    def test_celebration_effect_intensity_variations(self):
        """Test celebration effects with different intensity levels."""
        intensities = [0.1, 0.5, 1.0, 1.5, 2.0, 3.0]

        for intensity in intensities:
            effect = CelebrationEffect(
                effect_id=f"intensity_{intensity}",
                effect_type="test_effect",
                intensity=intensity
            )
            assert effect.intensity == intensity


class TestMilestoneDefinition:
    """Test MilestoneDefinition data class."""

    def test_milestone_definition_creation_minimal(self):
        """Test creating MilestoneDefinition with minimal data."""
        milestone = MilestoneDefinition(
            milestone_id="first_milestone",
            name="First Milestone",
            description="Complete your first coordination task",
            threshold_value=1.0,
            metric_name="completed_tasks"
        )

        assert milestone.milestone_id == "first_milestone"
        assert milestone.name == "First Milestone"
        assert milestone.description == "Complete your first coordination task"
        assert milestone.threshold_value == 1.0
        assert milestone.metric_name == "completed_tasks"
        assert milestone.evaluation_period_days == 7
        assert milestone.is_cumulative is True
        assert milestone.celebration_effect is None

    def test_milestone_definition_creation_complete(self):
        """Test creating MilestoneDefinition with celebration effect."""
        celebration = CelebrationEffect(
            effect_id="milestone_celebration",
            effect_type="achievement_unlock",
            emoji_patterns=["🎯", "🎉"],
            custom_message="Milestone reached!"
        )

        milestone = MilestoneDefinition(
            milestone_id="coordination_excellence",
            name="Coordination Excellence",
            description="Maintain high coordination quality for 2 weeks",
            threshold_value=0.9,
            metric_name="average_coordination_score",
            evaluation_period_days=14,
            is_cumulative=False,
            celebration_effect=celebration
        )

        assert milestone.evaluation_period_days == 14
        assert milestone.is_cumulative is False
        assert milestone.celebration_effect == celebration
        assert milestone.celebration_effect.effect_id == "milestone_celebration"

    def test_milestone_definition_threshold_values(self):
        """Test milestones with various threshold values."""
        threshold_tests = [
            (0.0, "zero_threshold"),
            (0.5, "half_threshold"),
            (1.0, "unity_threshold"),
            (10.0, "ten_threshold"),
            (100.0, "hundred_threshold")
        ]

        for threshold, test_id in threshold_tests:
            milestone = MilestoneDefinition(
                milestone_id=test_id,
                name=f"Milestone {threshold}",
                description=f"Test threshold {threshold}",
                threshold_value=threshold,
                metric_name="test_metric"
            )
            assert milestone.threshold_value == threshold


class TestParticipantProfile:
    """Test ParticipantProfile data class."""

    def test_participant_profile_creation_minimal(self):
        """Test creating ParticipantProfile with minimal data."""
        profile = ParticipantProfile(participant_id="user_001")

        assert profile.participant_id == "user_001"
        assert profile.name is None
        assert profile.total_points == 0
        assert profile.achievements_unlocked == []
        assert profile.current_level == 1
        assert profile.coordination_score == 0.0
        assert profile.systematic_practice_score == 0.0
        assert profile.collaboration_score == 0.0
        assert profile.joined_at is None
        assert profile.last_active_at is None
        assert profile.preferences == {}

    def test_participant_profile_creation_complete(self):
        """Test creating ParticipantProfile with complete data."""
        join_time = datetime.now() - timedelta(days=30)
        active_time = datetime.now() - timedelta(minutes=10)
        achievements = ["first_task", "collaboration_start", "systematic_approach"]
        preferences = {
            "notification_frequency": "daily",
            "celebration_style": "enhanced",
            "theme": "dark",
            "dashboard_widgets": ["achievements", "progress", "leaderboard"]
        }

        profile = ParticipantProfile(
            participant_id="alice_coordinator",
            name="Alice Smith",
            total_points=1850,
            achievements_unlocked=achievements,
            current_level=8,
            coordination_score=0.87,
            systematic_practice_score=0.92,
            collaboration_score=0.79,
            joined_at=join_time,
            last_active_at=active_time,
            preferences=preferences
        )

        assert profile.name == "Alice Smith"
        assert profile.total_points == 1850
        assert len(profile.achievements_unlocked) == 3
        assert "collaboration_start" in profile.achievements_unlocked
        assert profile.current_level == 8
        assert profile.coordination_score == 0.87
        assert profile.systematic_practice_score == 0.92
        assert profile.joined_at == join_time
        assert profile.preferences["notification_frequency"] == "daily"
        assert profile.preferences["theme"] == "dark"

    def test_participant_profile_score_validation(self):
        """Test participant profile with various score ranges."""
        # Test with perfect scores
        profile_perfect = ParticipantProfile(
            participant_id="perfect_participant",
            coordination_score=1.0,
            systematic_practice_score=1.0,
            collaboration_score=1.0
        )

        assert profile_perfect.coordination_score == 1.0
        assert profile_perfect.systematic_practice_score == 1.0
        assert profile_perfect.collaboration_score == 1.0

        # Test with varying scores
        profile_varied = ParticipantProfile(
            participant_id="varied_participant",
            coordination_score=0.75,
            systematic_practice_score=0.88,
            collaboration_score=0.62
        )

        assert profile_varied.coordination_score == 0.75
        assert profile_varied.systematic_practice_score == 0.88
        assert profile_varied.collaboration_score == 0.62

    def test_participant_profile_achievement_tracking(self):
        """Test participant profile achievement list management."""
        initial_achievements = ["starter", "first_week"]

        profile = ParticipantProfile(
            participant_id="achievement_tracker",
            achievements_unlocked=initial_achievements
        )

        assert len(profile.achievements_unlocked) == 2
        assert "starter" in profile.achievements_unlocked
        assert "first_week" in profile.achievements_unlocked

        # Test with large achievement list
        many_achievements = [f"achievement_{i}" for i in range(50)]
        profile_many = ParticipantProfile(
            participant_id="prolific_achiever",
            achievements_unlocked=many_achievements,
            total_points=10000,
            current_level=25
        )

        assert len(profile_many.achievements_unlocked) == 50
        assert profile_many.total_points == 10000
        assert profile_many.current_level == 25


class TestAchievementModelIntegration:
    """Test integration between different achievement model components."""

    def test_achievement_and_progress_integration(self):
        """Test that AchievementDefinition and AchievementProgress work together."""
        # Define an achievement
        achievement = AchievementDefinition(
            id="integration_test",
            name="Integration Test Achievement",
            description="Test achievement for integration",
            achievement_type=AchievementType.SYSTEMATIC_PRACTICE,
            category=AchievementCategory.WEEKLY,
            rarity=AchievementRarity.UNCOMMON,
            celebration_level=CelebrationLevel.ENHANCED,
            requirements={"coordination_events": 10, "quality_threshold": 0.8},
            points=150
        )

        # Track progress for the achievement
        progress = AchievementProgress(
            achievement_id=achievement.id,
            current_progress={"coordination_events": 7, "current_quality": 0.85},
            progress_percentage=70.0,
            first_progress_at=datetime.now() - timedelta(days=2),
            last_updated_at=datetime.now()
        )

        assert progress.achievement_id == achievement.id
        assert progress.current_progress["coordination_events"] < achievement.requirements["coordination_events"]
        assert progress.current_progress["current_quality"] > achievement.requirements["quality_threshold"]

    def test_milestone_and_celebration_integration(self):
        """Test integration between MilestoneDefinition and CelebrationEffect."""
        # Create celebration effect
        celebration = CelebrationEffect(
            effect_id="milestone_celebration",
            effect_type="milestone_reached",
            duration_ms=4000,
            intensity=1.2,
            emoji_patterns=["🎯", "⭐", "🏆"],
            custom_message="Fantastic milestone achievement!"
        )

        # Create milestone with celebration
        milestone = MilestoneDefinition(
            milestone_id="quality_milestone",
            name="Quality Excellence Milestone",
            description="Achieve consistent high-quality coordination",
            threshold_value=0.9,
            metric_name="average_coordination_quality",
            evaluation_period_days=14,
            celebration_effect=celebration
        )

        assert milestone.celebration_effect.effect_id == celebration.effect_id
        assert milestone.celebration_effect.custom_message == celebration.custom_message
        assert milestone.threshold_value == 0.9

    def test_participant_profile_and_unlocked_achievement_integration(self):
        """Test integration between ParticipantProfile and UnlockedAchievement."""
        # Create participant profile
        profile = ParticipantProfile(
            participant_id="integration_participant",
            name="Integration Tester",
            total_points=500,
            achievements_unlocked=["basic_start", "first_milestone"],
            current_level=5
        )

        # Create new unlocked achievement
        new_unlock = UnlockedAchievement(
            achievement_id="collaboration_excellence",
            unlocked_at=datetime.now(),
            points_awarded=200,
            unlock_context={"trigger": "team_coordination_milestone"}
        )

        # Simulate adding the achievement to profile
        updated_achievements = profile.achievements_unlocked + [new_unlock.achievement_id]
        updated_points = profile.total_points + new_unlock.points_awarded

        assert len(updated_achievements) == 3
        assert "collaboration_excellence" in updated_achievements
        assert updated_points == 700

    def test_coordination_event_to_achievement_progression(self):
        """Test how CoordinationEvent contributes to achievement progression."""
        # Define achievement requirements
        achievement = AchievementDefinition(
            id="systematic_coordinator",
            name="Systematic Coordinator",
            description="Demonstrate systematic coordination practices",
            achievement_type=AchievementType.SYSTEMATIC_PRACTICE,
            category=AchievementCategory.PERSONAL,
            rarity=AchievementRarity.RARE,
            celebration_level=CelebrationLevel.ENHANCED,
            requirements={
                "min_events": 5,
                "min_systematic_score": 0.8,
                "min_coordination_quality": 0.85
            }
        )

        # Create coordination events
        events = [
            CoordinationEvent(
                event_id=f"event_{i}",
                event_type="systematic_coordination",
                timestamp=datetime.now() - timedelta(hours=i),
                participant_id="systematic_user",
                coordination_quality=0.87 + (i * 0.01),
                systematic_score=0.82 + (i * 0.015),
                collaboration_score=0.80
            )
            for i in range(5)
        ]

        # Calculate if events meet achievement requirements
        event_count = len(events)
        avg_systematic = sum(e.systematic_score for e in events) / len(events)
        avg_coordination = sum(e.coordination_quality for e in events) / len(events)

        meets_count = event_count >= achievement.requirements["min_events"]
        meets_systematic = avg_systematic >= achievement.requirements["min_systematic_score"]
        meets_coordination = avg_coordination >= achievement.requirements["min_coordination_quality"]

        assert meets_count is True
        assert meets_systematic is True
        assert meets_coordination is True

        # All requirements met - achievement should be unlockable
        achievement_ready = meets_count and meets_systematic and meets_coordination
        assert achievement_ready is True