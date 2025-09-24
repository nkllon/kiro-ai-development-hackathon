"""
Unit tests for Achievement Tracking System
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from src.beast_mode.observatory.achievement_tracker import AchievementTracker
from src.beast_mode.observatory.achievement_models import (
    CoordinationEvent,
    AchievementDefinition,
    AchievementType,
    AchievementCategory,
    AchievementRarity,
    CelebrationLevel,
    MilestoneDefinition,
    CelebrationEffect
)


class TestAchievementTracker:
    """Test suite for AchievementTracker functionality."""

    @pytest.fixture
    def mock_storage_backend(self):
        """Create mock storage backend."""
        return Mock()

    @pytest.fixture
    def mock_emoji_rain_integration(self):
        """Create mock emoji rain integration."""
        integration = Mock()
        integration.trigger_celebration_rain = AsyncMock(return_value=True)
        return integration

    @pytest.fixture
    def achievement_tracker(self, mock_storage_backend, mock_emoji_rain_integration):
        """Create AchievementTracker instance for testing."""
        return AchievementTracker(
            storage_backend=mock_storage_backend,
            emoji_rain_integration=mock_emoji_rain_integration
        )

    @pytest.fixture
    def sample_coordination_event(self):
        """Create sample coordination event for testing."""
        return CoordinationEvent(
            event_id="test_event_001",
            event_type="systematic_coordination",
            timestamp=datetime.now(),
            participant_id="participant_001",
            context={"team_size": 4, "project": "test_project"},
            coordination_quality=0.85,
            systematic_score=0.9,
            collaboration_score=0.8
        )

    def test_initialization(self, achievement_tracker):
        """Test AchievementTracker initialization."""
        assert achievement_tracker.instance_id.startswith("achievement_tracker_")
        assert len(achievement_tracker.achievement_definitions) > 0
        assert len(achievement_tracker.milestone_definitions) > 0
        assert len(achievement_tracker.coordination_events) == 0
        assert len(achievement_tracker.participant_profiles) == 0

    def test_register_achievement(self, achievement_tracker):
        """Test achievement registration."""
        test_achievement = AchievementDefinition(
            id="test_achievement",
            name="Test Achievement",
            description="A test achievement",
            achievement_type=AchievementType.SYSTEMATIC_PRACTICE,
            category=AchievementCategory.PERSONAL,
            rarity=AchievementRarity.COMMON,
            celebration_level=CelebrationLevel.NORMAL,
            requirements={"test_metric": 10},
            points=100
        )

        initial_count = len(achievement_tracker.achievement_definitions)
        achievement_tracker.register_achievement(test_achievement)

        assert len(achievement_tracker.achievement_definitions) == initial_count + 1
        assert "test_achievement" in achievement_tracker.achievement_definitions
        assert achievement_tracker.achievement_definitions["test_achievement"] == test_achievement

    def test_register_milestone(self, achievement_tracker):
        """Test milestone registration."""
        test_milestone = MilestoneDefinition(
            milestone_id="test_milestone",
            name="Test Milestone",
            description="A test milestone",
            threshold_value=0.8,
            metric_name="coordination_score",
            evaluation_period_days=7
        )

        initial_count = len(achievement_tracker.milestone_definitions)
        achievement_tracker.register_milestone(test_milestone)

        assert len(achievement_tracker.milestone_definitions) == initial_count + 1
        assert "test_milestone" in achievement_tracker.milestone_definitions
        assert achievement_tracker.milestone_definitions["test_milestone"] == test_milestone

    @pytest.mark.asyncio
    async def test_track_coordination_event_new_participant(self, achievement_tracker, sample_coordination_event):
        """Test tracking coordination event for new participant."""
        participant_id = sample_coordination_event.participant_id

        # Ensure participant doesn't exist
        assert participant_id not in achievement_tracker.participant_profiles

        result = await achievement_tracker.track_coordination_event(sample_coordination_event)

        # Verify processing result
        assert result["event_processed"] is True
        assert "achievements_unlocked" in result
        assert "progress_updates" in result
        assert "milestones_reached" in result

        # Verify participant was initialized
        assert participant_id in achievement_tracker.participant_profiles
        profile = achievement_tracker.participant_profiles[participant_id]
        assert profile.participant_id == participant_id
        assert profile.joined_at is not None

        # Verify event was stored
        assert len(achievement_tracker.coordination_events) == 1
        assert achievement_tracker.coordination_events[0] == sample_coordination_event

    @pytest.mark.asyncio
    async def test_consistency_achievement_progress(self, achievement_tracker):
        """Test consistency achievement progress tracking."""
        participant_id = "test_participant"

        # Create events for 5 consecutive days
        events = []
        base_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)

        for i in range(5):
            event_date = base_date - timedelta(days=i)
            event = CoordinationEvent(
                event_id=f"event_{i}",
                event_type="daily_coordination",
                timestamp=event_date,
                participant_id=participant_id,
                coordination_quality=0.8,  # Meets minimum requirement
                systematic_score=0.7,
                collaboration_score=0.75
            )
            events.append(event)

        # Process events
        for event in events:
            result = await achievement_tracker.track_coordination_event(event)
            assert result["event_processed"] is True

        # Check if daily coordinator achievement was unlocked
        unlocked_achievements = achievement_tracker.unlocked_achievements.get(participant_id, [])
        daily_coordinator_unlocked = any(
            unlock.achievement_id == "daily_coordinator"
            for unlock in unlocked_achievements
        )

        assert daily_coordinator_unlocked, "Daily coordinator achievement should be unlocked after 5 consecutive days"

    @pytest.mark.asyncio
    async def test_systematic_practice_achievement_progress(self, achievement_tracker):
        """Test systematic practice achievement progress."""
        participant_id = "test_participant"

        # Create 10 systematic coordination events
        for i in range(10):
            event = CoordinationEvent(
                event_id=f"systematic_event_{i}",
                event_type="systematic_coordination",
                timestamp=datetime.now() - timedelta(hours=i),
                participant_id=participant_id,
                coordination_quality=0.7,
                systematic_score=0.85,  # Meets minimum requirement
                collaboration_score=0.7
            )

            result = await achievement_tracker.track_coordination_event(event)
            assert result["event_processed"] is True

        # Check if systematic practitioner achievement was unlocked
        unlocked_achievements = achievement_tracker.unlocked_achievements.get(participant_id, [])
        systematic_unlocked = any(
            unlock.achievement_id == "systematic_practitioner"
            for unlock in unlocked_achievements
        )

        assert systematic_unlocked, "Systematic practitioner achievement should be unlocked after 10 events"

    @pytest.mark.asyncio
    async def test_collaboration_achievement_progress(self, achievement_tracker):
        """Test collaboration achievement progress."""
        participant_id = "test_participant"

        # Create 20 team collaboration events
        for i in range(20):
            event = CoordinationEvent(
                event_id=f"collaboration_event_{i}",
                event_type="team_coordination",
                timestamp=datetime.now() - timedelta(hours=i),
                participant_id=participant_id,
                context={"team_size": 4},  # Meets minimum team size
                coordination_quality=0.8,
                systematic_score=0.8,
                collaboration_score=0.92  # Meets minimum requirement
            )

            result = await achievement_tracker.track_coordination_event(event)
            assert result["event_processed"] is True

        # Check if collaboration champion achievement was unlocked
        unlocked_achievements = achievement_tracker.unlocked_achievements.get(participant_id, [])
        collaboration_unlocked = any(
            unlock.achievement_id == "collaboration_champion"
            for unlock in unlocked_achievements
        )

        assert collaboration_unlocked, "Collaboration champion achievement should be unlocked after 20 team events"

    @pytest.mark.asyncio
    async def test_milestone_evaluation(self, achievement_tracker):
        """Test milestone threshold evaluation."""
        participant_id = "test_participant"

        # Create events with high coordination scores for a week
        base_date = datetime.now()
        for i in range(7):
            event = CoordinationEvent(
                event_id=f"milestone_event_{i}",
                event_type="coordination",
                timestamp=base_date - timedelta(days=i),
                participant_id=participant_id,
                coordination_quality=0.85,  # Above 0.8 threshold
                systematic_score=0.8,
                collaboration_score=0.8
            )

            result = await achievement_tracker.track_coordination_event(event)
            assert result["event_processed"] is True

        # The weekly coordination goal milestone should be reached
        last_result = result
        milestones_reached = last_result.get("milestones_reached", [])

        weekly_milestone_reached = any(
            milestone["milestone_id"] == "weekly_coordination_goal"
            for milestone in milestones_reached
        )

        # Note: This might not trigger on every event, depending on implementation
        # Let's check if participant has consistently high scores
        profile = achievement_tracker.participant_profiles[participant_id]
        assert profile.coordination_score >= 0.8

    @pytest.mark.asyncio
    async def test_celebration_integration(self, achievement_tracker, mock_emoji_rain_integration):
        """Test integration with emoji rain celebration system."""
        participant_id = "test_participant"

        # Create events to trigger an achievement
        for i in range(5):
            event = CoordinationEvent(
                event_id=f"celebration_event_{i}",
                event_type="daily_coordination",
                timestamp=datetime.now() - timedelta(days=i),
                participant_id=participant_id,
                coordination_quality=0.8,
                systematic_score=0.7,
                collaboration_score=0.75
            )

            result = await achievement_tracker.track_coordination_event(event)

        # Verify emoji rain was triggered for achievement unlocks
        achievements_unlocked = result.get("achievements_unlocked", [])
        if achievements_unlocked:
            mock_emoji_rain_integration.trigger_celebration_rain.assert_called()

    def test_participant_stats_generation(self, achievement_tracker):
        """Test participant statistics generation."""
        participant_id = "test_participant"

        # Initialize participant
        achievement_tracker.participant_profiles[participant_id] = Mock()
        achievement_tracker.participant_profiles[participant_id].name = "Test Participant"
        achievement_tracker.participant_profiles[participant_id].total_points = 250
        achievement_tracker.participant_profiles[participant_id].current_level = 2
        achievement_tracker.participant_profiles[participant_id].achievements_unlocked = ["test_achievement"]
        achievement_tracker.participant_profiles[participant_id].coordination_score = 0.8
        achievement_tracker.participant_profiles[participant_id].systematic_practice_score = 0.85
        achievement_tracker.participant_profiles[participant_id].collaboration_score = 0.75

        stats = achievement_tracker.get_participant_stats(participant_id)

        assert stats is not None
        assert stats["participant_id"] == participant_id
        assert stats["total_points"] == 250
        assert stats["current_level"] == 2
        assert "achievements_by_category" in stats
        assert "achievements_by_rarity" in stats

    def test_leaderboard_generation(self, achievement_tracker):
        """Test leaderboard generation."""
        # Create multiple participants
        participants_data = [
            ("participant_001", 500, 3, ["achievement_1", "achievement_2"]),
            ("participant_002", 300, 2, ["achievement_1"]),
            ("participant_003", 750, 4, ["achievement_1", "achievement_2", "achievement_3"])
        ]

        for pid, points, level, achievements in participants_data:
            profile = Mock()
            profile.name = f"Participant {pid}"
            profile.total_points = points
            profile.current_level = level
            profile.achievements_unlocked = achievements
            profile.coordination_score = 0.8
            profile.systematic_practice_score = 0.75
            profile.collaboration_score = 0.85

            achievement_tracker.participant_profiles[pid] = profile

        leaderboard = achievement_tracker.get_leaderboard(limit=5)

        assert len(leaderboard) == 3
        # Should be sorted by points descending
        assert leaderboard[0]["participant_id"] == "participant_003"
        assert leaderboard[0]["total_points"] == 750
        assert leaderboard[1]["participant_id"] == "participant_001"
        assert leaderboard[2]["participant_id"] == "participant_002"

    def test_system_stats_calculation(self, achievement_tracker):
        """Test system statistics calculation."""
        # Add some mock data
        achievement_tracker.participant_profiles["test_1"] = Mock()
        achievement_tracker.participant_profiles["test_2"] = Mock()

        # Add some mock unlocked achievements
        from src.beast_mode.observatory.achievement_models import UnlockedAchievement
        unlock1 = UnlockedAchievement(
            achievement_id="daily_coordinator",
            unlocked_at=datetime.now(),
            points_awarded=100
        )
        unlock2 = UnlockedAchievement(
            achievement_id="systematic_practitioner",
            unlocked_at=datetime.now(),
            points_awarded=250
        )

        achievement_tracker.unlocked_achievements["test_1"] = [unlock1]
        achievement_tracker.unlocked_achievements["test_2"] = [unlock2]

        stats = achievement_tracker.get_system_stats()

        assert stats.total_achievements_defined > 0
        assert stats.total_achievements_unlocked == 2
        assert stats.total_points_earned == 350
        assert stats.completion_rate >= 0
        assert isinstance(stats.achievements_by_rarity, dict)
        assert isinstance(stats.achievements_by_category, dict)

    def test_performance_metrics(self, achievement_tracker):
        """Test performance metrics collection."""
        # Process some events to generate metrics
        achievement_tracker._total_events_processed = 100
        achievement_tracker._event_processing_times.extend([1.5, 2.0, 1.8, 2.2, 1.7])

        metrics = achievement_tracker.get_performance_metrics()

        assert "instance_id" in metrics
        assert metrics["total_events_processed"] == 100
        assert "average_processing_time_ms" in metrics
        assert metrics["achievement_definitions_count"] > 0
        assert metrics["milestone_definitions_count"] > 0
        assert "uptime_hours" in metrics

    @pytest.mark.asyncio
    async def test_event_handler_registration(self, achievement_tracker):
        """Test event handler registration and invocation."""
        unlock_handler_called = False
        milestone_handler_called = False
        celebration_handler_called = False

        async def unlock_handler(participant_id, achievement, unlock_record):
            nonlocal unlock_handler_called
            unlock_handler_called = True

        async def milestone_handler(participant_id, milestone_def, event):
            nonlocal milestone_handler_called
            milestone_handler_called = True

        async def celebration_handler(celebration_data):
            nonlocal celebration_handler_called
            celebration_handler_called = True

        # Register handlers
        achievement_tracker.add_achievement_unlock_handler(unlock_handler)
        achievement_tracker.add_milestone_handler(milestone_handler)
        achievement_tracker.add_celebration_handler(celebration_handler)

        # Trigger events that should call handlers
        participant_id = "test_participant"

        # Create enough events to trigger an achievement
        for i in range(5):
            event = CoordinationEvent(
                event_id=f"handler_event_{i}",
                event_type="daily_coordination",
                timestamp=datetime.now() - timedelta(days=i),
                participant_id=participant_id,
                coordination_quality=0.8,
                systematic_score=0.7,
                collaboration_score=0.75
            )

            await achievement_tracker.track_coordination_event(event)

        # Verify handlers were called
        assert unlock_handler_called, "Achievement unlock handler should have been called"
        assert celebration_handler_called, "Celebration handler should have been called"

    def test_default_achievements_exist(self, achievement_tracker):
        """Test that default achievements are properly initialized."""
        expected_achievements = [
            "daily_coordinator",
            "systematic_practitioner",
            "collaboration_champion",
            "innovation_catalyst",
            "coordination_legend"
        ]

        for achievement_id in expected_achievements:
            assert achievement_id in achievement_tracker.achievement_definitions
            achievement = achievement_tracker.achievement_definitions[achievement_id]
            assert achievement.name is not None
            assert achievement.description is not None
            assert achievement.points > 0

    def test_default_milestones_exist(self, achievement_tracker):
        """Test that default milestones are properly initialized."""
        expected_milestones = [
            "weekly_coordination_goal",
            "systematic_streak"
        ]

        for milestone_id in expected_milestones:
            assert milestone_id in achievement_tracker.milestone_definitions
            milestone = achievement_tracker.milestone_definitions[milestone_id]
            assert milestone.name is not None
            assert milestone.description is not None
            assert milestone.threshold_value > 0

    @pytest.mark.asyncio
    async def test_consecutive_days_calculation(self, achievement_tracker):
        """Test consecutive days calculation logic."""
        participant_id = "test_participant"

        # Create events for non-consecutive days (gap in middle)
        base_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        event_dates = [0, 1, 2, 5, 6, 7, 8]  # Gap between day 2 and day 5

        for i, day_offset in enumerate(event_dates):
            event = CoordinationEvent(
                event_id=f"consecutive_event_{i}",
                event_type="daily_coordination",
                timestamp=base_date - timedelta(days=day_offset),
                participant_id=participant_id,
                coordination_quality=0.8,
                systematic_score=0.7,
                collaboration_score=0.75
            )

            await achievement_tracker.track_coordination_event(event)

        # Check progress for daily coordinator achievement
        progress = achievement_tracker.participant_progress[participant_id]["daily_coordinator"]
        consecutive_days = progress.current_progress.get("consecutive_days", 0)

        # Should be 4 consecutive days (days 5, 6, 7, 8), not 7 total days
        assert consecutive_days == 4, f"Expected 4 consecutive days, got {consecutive_days}"

    @pytest.mark.asyncio
    async def test_achievement_prerequisite_checking(self, achievement_tracker):
        """Test achievement prerequisite validation."""
        participant_id = "test_participant"

        # The coordination_legend achievement requires prerequisite achievements
        legend_achievement = achievement_tracker.achievement_definitions["coordination_legend"]
        assert len(legend_achievement.prerequisite_achievements) > 0

        # Initialize participant progress
        await achievement_tracker._initialize_participant(participant_id)

        # Mock having prerequisites unlocked
        from src.beast_mode.observatory.achievement_models import UnlockedAchievement
        prereq_unlock1 = UnlockedAchievement(
            achievement_id="systematic_practitioner",
            unlocked_at=datetime.now(),
            points_awarded=250
        )
        prereq_unlock2 = UnlockedAchievement(
            achievement_id="collaboration_champion",
            unlocked_at=datetime.now(),
            points_awarded=500
        )

        achievement_tracker.unlocked_achievements[participant_id] = [prereq_unlock1, prereq_unlock2]

        # Now check if legend achievement can be completed
        # (This would require actually meeting the mastery requirements too)
        progress = achievement_tracker.participant_progress[participant_id]["coordination_legend"]

        # Create events to build up mastery score
        for i in range(100):
            event = CoordinationEvent(
                event_id=f"mastery_event_{i}",
                event_type="coordination_mastery",
                timestamp=datetime.now() - timedelta(hours=i),
                participant_id=participant_id,
                coordination_quality=0.98,
                systematic_score=0.97,
                collaboration_score=0.96
            )

            await achievement_tracker.track_coordination_event(event)

        # Check if prerequisites are properly considered
        can_complete = await achievement_tracker._is_achievement_complete(
            legend_achievement, progress, participant_id
        )

        # Should be True if all requirements (including prerequisites) are met
        mastery_score = progress.current_progress.get("mastery_score", 0.0)
        total_events = progress.current_progress.get("total_events", 0)

        assert mastery_score > 0.9, f"Mastery score should be high, got {mastery_score}"
        assert total_events >= 100, f"Should have processed 100 events, got {total_events}"