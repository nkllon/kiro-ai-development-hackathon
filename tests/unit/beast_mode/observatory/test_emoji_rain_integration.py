"""
Unit tests for Emoji Rain Integration System
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from src.beast_mode.observatory.emoji_rain_integration import (
    EmojiRainIntegration,
    EmojiRainPattern,
    CelebrationTrigger
)


class TestEmojiRainIntegration:
    """Test suite for EmojiRainIntegration functionality."""

    @pytest.fixture
    def mock_websocket_manager(self):
        """Create mock websocket manager."""
        manager = Mock()
        manager.broadcast_message = AsyncMock()
        manager.send_to_participant = AsyncMock()
        return manager

    @pytest.fixture
    def mock_frontend_integration(self):
        """Create mock frontend integration."""
        integration = Mock()
        integration.trigger_rain_effect = AsyncMock()
        integration.show_notification = AsyncMock()
        return integration

    @pytest.fixture
    def emoji_rain_integration(self, mock_websocket_manager, mock_frontend_integration):
        """Create EmojiRainIntegration instance for testing."""
        integration = EmojiRainIntegration(
            websocket_manager=mock_websocket_manager,
            frontend_integration=mock_frontend_integration
        )
        # Manually start processor if needed in tests
        if integration._processor_task is None:
            try:
                integration._processor_task = asyncio.create_task(integration._process_celebration_queue())
            except RuntimeError:
                pass  # Event loop not running
        return integration

    def test_initialization(self, emoji_rain_integration):
        """Test EmojiRainIntegration initialization."""
        assert emoji_rain_integration.instance_id.startswith("emoji_rain_")
        assert len(emoji_rain_integration.rain_patterns) > 0
        assert emoji_rain_integration.celebration_queue is not None
        assert len(emoji_rain_integration.active_celebrations) == 0

        # Check that default patterns are registered
        expected_patterns = [
            "common_achievement",
            "uncommon_achievement",
            "rare_achievement",
            "epic_achievement",
            "legendary_achievement",
            "daily_milestone",
            "weekly_milestone",
            "streak_celebration",
            "perfect_coordination",
            "innovation_burst"
        ]

        for pattern_id in expected_patterns:
            assert pattern_id in emoji_rain_integration.rain_patterns

    def test_register_pattern(self, emoji_rain_integration):
        """Test emoji rain pattern registration."""
        test_pattern = EmojiRainPattern(
            pattern_id="test_pattern",
            name="Test Pattern",
            emoji_sequence=["🧪", "⚗️", "🔬"],
            duration_ms=2000,
            intensity=0.8,
            drop_rate=25
        )

        initial_count = len(emoji_rain_integration.rain_patterns)
        emoji_rain_integration.register_pattern(test_pattern)

        assert len(emoji_rain_integration.rain_patterns) == initial_count + 1
        assert "test_pattern" in emoji_rain_integration.rain_patterns
        assert emoji_rain_integration.rain_patterns["test_pattern"] == test_pattern

    def test_register_celebration_trigger(self, emoji_rain_integration):
        """Test celebration trigger registration."""
        test_trigger = CelebrationTrigger(
            trigger_id="test_trigger",
            celebration_type="custom",
            conditions={"score_threshold": 0.9},
            emoji_patterns=["🎉", "🎊"],
            custom_effects={"sparkle": True}
        )

        initial_count = len(emoji_rain_integration.celebration_triggers)
        emoji_rain_integration.register_celebration_trigger(test_trigger)

        assert len(emoji_rain_integration.celebration_triggers) == initial_count + 1
        assert "test_trigger" in emoji_rain_integration.celebration_triggers

    @pytest.mark.asyncio
    async def test_trigger_celebration_rain_basic(self, emoji_rain_integration):
        """Test basic celebration rain triggering."""
        result = await emoji_rain_integration.trigger_celebration_rain(
            emoji_patterns=["🌟", "⭐"],
            duration_ms=3000,
            intensity=0.8,
            message="Test celebration",
            celebration_type="test"
        )

        assert result is True
        assert emoji_rain_integration.celebration_queue.qsize() == 1

        # Get the queued celebration
        celebration_data = await emoji_rain_integration.celebration_queue.get()
        assert celebration_data["type"] == "test"
        assert celebration_data["emoji_patterns"] == ["🌟", "⭐"]
        assert celebration_data["duration_ms"] == 3000
        assert celebration_data["intensity"] == 0.8
        assert celebration_data["message"] == "Test celebration"

    @pytest.mark.asyncio
    async def test_trigger_achievement_celebration_common(self, emoji_rain_integration):
        """Test achievement celebration for common rarity."""
        result = await emoji_rain_integration.trigger_achievement_celebration(
            achievement_name="First Steps",
            achievement_rarity="common",
            celebration_level="normal",
            unlock_message="Great start!"
        )

        assert result is True
        assert emoji_rain_integration.celebration_queue.qsize() == 1

        celebration_data = await emoji_rain_integration.celebration_queue.get()
        assert celebration_data["type"] == "achievement"
        assert celebration_data["achievement_name"] == "First Steps"
        assert celebration_data["achievement_rarity"] == "common"
        assert celebration_data["celebration_level"] == "normal"
        assert celebration_data["message"] == "Great start!"

    @pytest.mark.asyncio
    async def test_trigger_achievement_celebration_legendary(self, emoji_rain_integration):
        """Test achievement celebration for legendary rarity."""
        result = await emoji_rain_integration.trigger_achievement_celebration(
            achievement_name="Ultimate Master",
            achievement_rarity="legendary",
            celebration_level="spectacular",
            unlock_message="LEGENDARY ACHIEVEMENT!"
        )

        assert result is True

        celebration_data = await emoji_rain_integration.celebration_queue.get()
        pattern = celebration_data["pattern"]

        # Legendary achievements should have spectacular effects
        assert len(pattern.emoji_sequence) > 5  # More emojis for legendary
        assert pattern.duration_ms >= 5000  # Longer duration
        assert pattern.intensity >= 1.0  # High intensity
        assert pattern.sparkle_effect is True
        assert pattern.bounce_effect is True

    @pytest.mark.asyncio
    async def test_trigger_milestone_celebration(self, emoji_rain_integration):
        """Test milestone celebration triggering."""
        result = await emoji_rain_integration.trigger_milestone_celebration(
            milestone_name="Weekly Goal",
            milestone_type="weekly",
            threshold_reached=0.85,
            custom_message="Weekly milestone achieved!"
        )

        assert result is True

        celebration_data = await emoji_rain_integration.celebration_queue.get()
        assert celebration_data["type"] == "milestone"
        assert celebration_data["milestone_name"] == "Weekly Goal"
        assert celebration_data["milestone_type"] == "weekly"
        assert celebration_data["threshold_reached"] == 0.85
        assert celebration_data["message"] == "Weekly milestone achieved!"

    @pytest.mark.asyncio
    async def test_celebration_execution_achievement(self, emoji_rain_integration, mock_websocket_manager, mock_frontend_integration):
        """Test achievement celebration execution."""
        # Queue a celebration
        await emoji_rain_integration.trigger_achievement_celebration(
            achievement_name="Test Achievement",
            achievement_rarity="rare",
            celebration_level="enhanced"
        )

        # Get the queued celebration and execute it manually
        celebration_data = await emoji_rain_integration.celebration_queue.get()
        await emoji_rain_integration._execute_celebration(celebration_data)

        # Verify websocket message was sent
        mock_websocket_manager.broadcast_message.assert_called_once()
        call_args = mock_websocket_manager.broadcast_message.call_args[0][0]
        message_data = json.loads(call_args)

        assert message_data["type"] == "achievement_celebration"
        assert message_data["achievement_name"] == "Test Achievement"
        assert message_data["achievement_rarity"] == "rare"

        # Verify frontend integration was called
        mock_frontend_integration.trigger_rain_effect.assert_called_once()

    @pytest.mark.asyncio
    async def test_celebration_execution_milestone(self, emoji_rain_integration, mock_websocket_manager):
        """Test milestone celebration execution."""
        # Queue a milestone celebration
        await emoji_rain_integration.trigger_milestone_celebration(
            milestone_name="Daily Goal",
            milestone_type="daily",
            threshold_reached=0.8
        )

        # Execute the celebration
        celebration_data = await emoji_rain_integration.celebration_queue.get()
        await emoji_rain_integration._execute_celebration(celebration_data)

        # Verify websocket message was sent
        mock_websocket_manager.broadcast_message.assert_called_once()
        call_args = mock_websocket_manager.broadcast_message.call_args[0][0]
        message_data = json.loads(call_args)

        assert message_data["type"] == "milestone_celebration"
        assert message_data["milestone_name"] == "Daily Goal"
        assert message_data["milestone_type"] == "daily"

    @pytest.mark.asyncio
    async def test_celebration_execution_generic(self, emoji_rain_integration, mock_websocket_manager):
        """Test generic celebration execution."""
        # Queue a generic celebration
        await emoji_rain_integration.trigger_celebration_rain(
            emoji_patterns=["🎉", "🎊"],
            duration_ms=2500,
            intensity=0.9,
            message="Generic celebration",
            celebration_type="generic"
        )

        # Execute the celebration
        celebration_data = await emoji_rain_integration.celebration_queue.get()
        await emoji_rain_integration._execute_celebration(celebration_data)

        # Verify websocket message was sent
        mock_websocket_manager.broadcast_message.assert_called_once()
        call_args = mock_websocket_manager.broadcast_message.call_args[0][0]
        message_data = json.loads(call_args)

        assert message_data["type"] == "generic_celebration"
        assert message_data["emoji_patterns"] == ["🎉", "🎊"]
        assert message_data["duration_ms"] == 2500
        assert message_data["intensity"] == 0.9

    def test_duration_for_celebration_levels(self, emoji_rain_integration):
        """Test duration calculation for different celebration levels."""
        assert emoji_rain_integration._get_duration_for_level("subtle") == 1500
        assert emoji_rain_integration._get_duration_for_level("normal") == 2500
        assert emoji_rain_integration._get_duration_for_level("enhanced") == 3500
        assert emoji_rain_integration._get_duration_for_level("spectacular") == 5000
        assert emoji_rain_integration._get_duration_for_level("unknown") == 2500  # Default

    def test_intensity_for_celebration_levels(self, emoji_rain_integration):
        """Test intensity calculation for different celebration levels."""
        assert emoji_rain_integration._get_intensity_for_level("subtle") == 0.5
        assert emoji_rain_integration._get_intensity_for_level("normal") == 0.7
        assert emoji_rain_integration._get_intensity_for_level("enhanced") == 0.9
        assert emoji_rain_integration._get_intensity_for_level("spectacular") == 1.2
        assert emoji_rain_integration._get_intensity_for_level("unknown") == 0.7  # Default

    def test_pattern_enhancement_for_levels(self, emoji_rain_integration):
        """Test pattern enhancement based on celebration levels."""
        base_pattern = EmojiRainPattern(
            pattern_id="test_pattern",
            name="Test Pattern",
            emoji_sequence=["⭐"],
            duration_ms=2000,
            intensity=0.6,
            drop_rate=20,
            sparkle_effect=False,
            bounce_effect=False
        )

        # Test subtle enhancement
        subtle_pattern = emoji_rain_integration._enhance_pattern_for_level(base_pattern, "subtle")
        assert subtle_pattern.intensity == 0.6  # Base intensity is higher
        assert subtle_pattern.sparkle_effect is False
        assert subtle_pattern.bounce_effect is False

        # Test spectacular enhancement
        spectacular_pattern = emoji_rain_integration._enhance_pattern_for_level(base_pattern, "spectacular")
        assert spectacular_pattern.intensity >= 1.0  # Should be enhanced
        assert spectacular_pattern.duration_ms >= 5000
        assert spectacular_pattern.sparkle_effect is True
        assert spectacular_pattern.bounce_effect is True
        assert spectacular_pattern.drop_rate > base_pattern.drop_rate

    @pytest.mark.asyncio
    async def test_active_celebration_tracking(self, emoji_rain_integration):
        """Test tracking of active celebrations."""
        # Queue and execute a celebration
        await emoji_rain_integration.trigger_celebration_rain(
            emoji_patterns=["🌟"],
            duration_ms=1000,  # Short duration for test
            celebration_type="test"
        )

        celebration_data = await emoji_rain_integration.celebration_queue.get()
        await emoji_rain_integration._execute_celebration(celebration_data)

        # Should be added to active celebrations
        assert len(emoji_rain_integration.active_celebrations) == 1
        active_celebration = emoji_rain_integration.active_celebrations[0]
        assert active_celebration["status"] == "executing"
        assert "execution_start" in active_celebration

    @pytest.mark.asyncio
    async def test_cleanup_active_celebrations(self, emoji_rain_integration):
        """Test cleanup of completed celebrations."""
        # Create a mock active celebration that should be cleaned up
        past_time = datetime.now() - timedelta(seconds=10)
        test_celebration = {
            "celebration_id": "test_123",
            "status": "executing",
            "execution_start": past_time,
            "duration_ms": 1000  # 1 second duration, already passed
        }

        emoji_rain_integration.active_celebrations.append(test_celebration)
        assert len(emoji_rain_integration.active_celebrations) == 1

        # Run cleanup
        await emoji_rain_integration._cleanup_active_celebrations()

        # Should be removed since it's past the duration
        assert len(emoji_rain_integration.active_celebrations) == 0

    def test_celebration_stats(self, emoji_rain_integration):
        """Test celebration statistics collection."""
        # Simulate some activity
        emoji_rain_integration._celebrations_triggered = 25
        emoji_rain_integration._total_emojis_sent = 1000

        stats = emoji_rain_integration.get_celebration_stats()

        assert "instance_id" in stats
        assert stats["celebrations_triggered"] == 25
        assert stats["total_emojis_sent"] == 1000
        assert stats["patterns_registered"] > 0
        assert "uptime_hours" in stats
        assert "celebrations_per_hour" in stats
        assert stats["websocket_integration"] is True
        assert stats["frontend_integration"] is True

    @pytest.mark.asyncio
    async def test_error_handling_in_execution(self, emoji_rain_integration, mock_websocket_manager):
        """Test error handling during celebration execution."""
        # Make websocket manager raise an error
        mock_websocket_manager.broadcast_message.side_effect = Exception("Websocket error")

        # Queue and execute a celebration
        await emoji_rain_integration.trigger_celebration_rain(
            emoji_patterns=["🌟"],
            celebration_type="error_test"
        )

        celebration_data = await emoji_rain_integration.celebration_queue.get()

        # Should not raise exception, should handle gracefully
        await emoji_rain_integration._execute_celebration(celebration_data)

        # Celebration should still be marked as executed (even if websocket failed)
        assert celebration_data["status"] in ["executing", "failed"]

    def test_default_pattern_properties(self, emoji_rain_integration):
        """Test properties of default patterns."""
        # Check common achievement pattern
        common_pattern = emoji_rain_integration.rain_patterns["common_achievement"]
        assert common_pattern.duration_ms == 2000
        assert common_pattern.intensity == 0.5
        assert "⭐" in common_pattern.emoji_sequence

        # Check legendary achievement pattern
        legendary_pattern = emoji_rain_integration.rain_patterns["legendary_achievement"]
        assert legendary_pattern.duration_ms == 6000
        assert legendary_pattern.intensity == 1.5
        assert len(legendary_pattern.emoji_sequence) > 5
        assert legendary_pattern.sparkle_effect is True
        assert legendary_pattern.bounce_effect is True
        assert "👑" in legendary_pattern.emoji_sequence

        # Check innovation pattern
        innovation_pattern = emoji_rain_integration.rain_patterns["innovation_burst"]
        assert "💡" in innovation_pattern.emoji_sequence
        assert "🚀" in innovation_pattern.emoji_sequence

    @pytest.mark.asyncio
    async def test_custom_pattern_celebration(self, emoji_rain_integration):
        """Test celebration with custom emoji patterns."""
        custom_emojis = ["🧪", "⚗️", "🔬", "🧬", "⚛️"]

        result = await emoji_rain_integration.trigger_achievement_celebration(
            achievement_name="Science Master",
            achievement_rarity="epic",
            celebration_level="spectacular",
            custom_patterns=custom_emojis
        )

        assert result is True

        celebration_data = await emoji_rain_integration.celebration_queue.get()
        pattern = celebration_data["pattern"]

        # Should use custom emojis
        assert pattern.emoji_sequence == custom_emojis
        assert pattern.name.startswith("Custom Science Master")

    @pytest.mark.asyncio
    async def test_queue_overflow_handling(self, emoji_rain_integration):
        """Test handling of queue overflow scenarios."""
        # Queue many celebrations rapidly
        for i in range(20):
            await emoji_rain_integration.trigger_celebration_rain(
                emoji_patterns=["🌟"],
                celebration_type=f"test_{i}"
            )

        # Should handle all celebrations without error
        assert emoji_rain_integration.celebration_queue.qsize() == 20

        # Process a few celebrations
        for i in range(5):
            celebration_data = await emoji_rain_integration.celebration_queue.get()
            await emoji_rain_integration._execute_celebration(celebration_data)

        assert emoji_rain_integration.celebration_queue.qsize() == 15
        assert len(emoji_rain_integration.active_celebrations) == 5

    @pytest.mark.asyncio
    async def test_shutdown(self, emoji_rain_integration):
        """Test graceful shutdown."""
        # Queue some celebrations
        await emoji_rain_integration.trigger_celebration_rain(emoji_patterns=["🌟"])
        await emoji_rain_integration.trigger_celebration_rain(emoji_patterns=["⭐"])

        # Add some active celebrations
        emoji_rain_integration.active_celebrations.append({"test": "celebration"})

        assert emoji_rain_integration.celebration_queue.qsize() == 2
        assert len(emoji_rain_integration.active_celebrations) == 1

        # Shutdown
        await emoji_rain_integration.shutdown()

        # Should clear everything
        assert emoji_rain_integration.celebration_queue.qsize() == 0
        assert len(emoji_rain_integration.active_celebrations) == 0