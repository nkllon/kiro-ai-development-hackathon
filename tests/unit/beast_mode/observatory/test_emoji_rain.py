"""
Unit tests for the Emoji Rain Engine.

Tests the delightful emoji rain system that transforms coordination events
into beautiful, cascading visual celebrations.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.beast_mode.observatory.emoji_rain import (
    EmojiRainEngine,
    EmojiParticle,
    ActiveRainEffect,
    EmojiIntensity,
    EmojiRainWebSocketHandler,
)
from src.beast_mode.observatory.models import (
    CoordinationEvent,
    CoordinationEventType,
    EmojiRainEffect,
    AnimationStyle,
    Achievement,
)


class TestEmojiRainEngine:
    """Test EmojiRainEngine functionality."""
    
    @pytest.fixture
    def emoji_engine(self):
        """Create an EmojiRainEngine for testing."""
        return EmojiRainEngine()
    
    def test_emoji_engine_initialization(self, emoji_engine):
        """Test emoji rain engine initialization."""
        assert emoji_engine._active_effects == {}
        assert emoji_engine._running is False
        assert emoji_engine._frame_rate == 60
        assert emoji_engine._canvas_width == 1920
        assert emoji_engine._canvas_height == 1080
        assert len(emoji_engine._event_mappings) > 0
    
    def test_event_mappings_complete(self, emoji_engine):
        """Test that all coordination event types have emoji mappings."""
        expected_events = [
            CoordinationEventType.TASK_COMPLETED,
            CoordinationEventType.API_CALL_SUCCESS,
            CoordinationEventType.COST_THRESHOLD_REACHED,
            CoordinationEventType.ANOMALY_DETECTED,
            CoordinationEventType.ACHIEVEMENT_UNLOCKED,
            CoordinationEventType.COORDINATION_MILESTONE,
            CoordinationEventType.SYSTEM_HEALTH_CHANGE,
        ]
        
        for event_type in expected_events:
            assert event_type in emoji_engine._event_mappings
            mapping = emoji_engine._event_mappings[event_type]
            assert "emojis" in mapping
            assert "intensity" in mapping
            assert "duration" in mapping
            assert "animation_style" in mapping
            assert len(mapping["emojis"]) > 0
    
    @pytest.mark.asyncio
    async def test_start_stop_animation_loop(self, emoji_engine):
        """Test starting and stopping the animation loop."""
        # Start animation loop
        await emoji_engine.start_animation_loop()
        assert emoji_engine._running is True
        assert emoji_engine._animation_task is not None
        
        # Stop animation loop
        await emoji_engine.stop_animation_loop()
        assert emoji_engine._running is False
        assert len(emoji_engine._active_effects) == 0
    
    @pytest.mark.asyncio
    async def test_trigger_event_rain(self, emoji_engine):
        """Test triggering emoji rain from coordination events."""
        event = CoordinationEvent(
            event_type=CoordinationEventType.TASK_COMPLETED,
            source_component="test_component",
            event_data={"task_id": "test-123"}
        )
        
        effect_id = await emoji_engine.trigger_event_rain(event)
        
        assert effect_id != ""
        assert effect_id in emoji_engine._active_effects
        
        active_effect = emoji_engine._active_effects[effect_id]
        assert active_effect.trigger_event == "TASK_COMPLETED"
        assert len(active_effect.particles) > 0
    
    @pytest.mark.asyncio
    async def test_create_rain_effect(self, emoji_engine):
        """Test creating custom rain effects."""
        effect_config = EmojiRainEffect(
            emojis=["🎉", "✨", "🚀"],
            intensity=0.8,
            duration_seconds=5.0,
            animation_style=AnimationStyle.CELEBRATION_BURST,
            trigger_event="test_event"
        )
        
        effect_id = await emoji_engine.create_rain_effect(effect_config)
        
        assert effect_id in emoji_engine._active_effects
        active_effect = emoji_engine._active_effects[effect_id]
        assert active_effect.effect_config == effect_config
        assert len(active_effect.particles) > 0
    
    @pytest.mark.asyncio
    async def test_create_achievement_celebration(self, emoji_engine):
        """Test creating special achievement celebrations."""
        achievement = Achievement(
            name="Test Achievement",
            description="Test achievement description",
            icon_emoji="🏆",
            user_id="test-user"
        )
        
        effect_id = await emoji_engine.create_achievement_celebration(achievement)
        
        assert effect_id in emoji_engine._active_effects
        active_effect = emoji_engine._active_effects[effect_id]
        assert active_effect.effect_config.intensity == 1.0  # Maximum intensity
        assert active_effect.effect_config.duration_seconds == 8.0  # Longer duration
        assert "🏆" in active_effect.effect_config.emojis
    
    def test_create_particle(self, emoji_engine):
        """Test particle creation with different animation styles."""
        # Test gentle fall particles
        gentle_config = EmojiRainEffect(
            emojis=["✨"],
            intensity=0.5,
            duration_seconds=3.0,
            animation_style=AnimationStyle.GENTLE_FALL
        )
        
        particle = emoji_engine._create_particle(gentle_config)
        assert particle.emoji == "✨"
        assert 0.0 <= particle.x <= 1.0
        assert particle.y <= 0.0  # Starts above screen
        assert particle.velocity_y > 0  # Falls downward
        
        # Test celebration burst particles
        burst_config = EmojiRainEffect(
            emojis=["🎉"],
            intensity=1.0,
            duration_seconds=5.0,
            animation_style=AnimationStyle.CELEBRATION_BURST
        )
        
        particle = emoji_engine._create_particle(burst_config)
        assert particle.emoji == "🎉"
        assert 0.3 <= particle.x <= 0.7  # Starts near center
        assert 0.3 <= particle.y <= 0.7  # Starts near center
    
    def test_update_particle_physics(self, emoji_engine):
        """Test particle physics simulation."""
        particle = EmojiParticle(
            emoji="🚀",
            x=0.5,
            y=0.5,
            velocity_x=1.0,
            velocity_y=-1.0,
            rotation=0.0,
            rotation_speed=90.0,  # 90 degrees per second
            lifetime=5.0
        )
        
        initial_x = particle.x
        initial_y = particle.y
        initial_rotation = particle.rotation
        
        # Simulate one frame (1/60 second)
        emoji_engine._update_particle_physics(particle, 1/60)
        
        # Check that particle moved
        assert particle.x != initial_x
        assert particle.y != initial_y
        assert particle.rotation != initial_rotation
        
        # Check that gravity was applied (velocity_y should increase)
        assert particle.velocity_y > -1.0
    
    def test_register_animation_callback(self, emoji_engine):
        """Test registering animation callbacks."""
        callback = Mock()
        callback.__name__ = "test_callback"  # Add __name__ attribute for logging
        
        emoji_engine.register_animation_callback(callback)
        assert callback in emoji_engine._animation_callbacks
        
        emoji_engine.unregister_animation_callback(callback)
        assert callback not in emoji_engine._animation_callbacks
    
    def test_get_active_effects(self, emoji_engine):
        """Test getting active effects information."""
        # Initially no effects
        effects = emoji_engine.get_active_effects()
        assert effects == {}
        
        # Add a test effect
        effect_config = EmojiRainEffect(
            emojis=["🎯"],
            intensity=0.5,
            duration_seconds=3.0,
            animation_style=AnimationStyle.GENTLE_FALL,
            trigger_event="test"
        )
        
        # Manually add effect for testing
        from src.beast_mode.observatory.emoji_rain import ActiveRainEffect
        test_effect = ActiveRainEffect(
            effect_id="test-effect",
            effect_config=effect_config,
            particles=[],
            start_time=datetime.now(),
            duration=3.0,
            trigger_event="test"
        )
        emoji_engine._active_effects["test-effect"] = test_effect
        
        effects = emoji_engine.get_active_effects()
        assert "test-effect" in effects
        assert effects["test-effect"]["trigger_event"] == "test"
        assert effects["test-effect"]["duration"] == 3.0
    
    def test_set_canvas_size(self, emoji_engine):
        """Test setting canvas dimensions."""
        emoji_engine.set_canvas_size(1280, 720)
        assert emoji_engine._canvas_width == 1280
        assert emoji_engine._canvas_height == 720
    
    def test_get_performance_stats(self, emoji_engine):
        """Test getting performance statistics."""
        stats = emoji_engine.get_performance_stats()
        
        assert "active_effects" in stats
        assert "total_particles" in stats
        assert "target_fps" in stats
        assert "canvas_size" in stats
        assert "animation_running" in stats
        assert "registered_callbacks" in stats
        
        assert stats["active_effects"] == 0
        assert stats["total_particles"] == 0
        assert stats["target_fps"] == 60
        assert stats["animation_running"] is False


class TestEmojiParticle:
    """Test EmojiParticle model."""
    
    def test_particle_creation(self):
        """Test creating emoji particles."""
        particle = EmojiParticle(
            emoji="🌟",
            x=0.5,
            y=0.3,
            velocity_x=1.0,
            velocity_y=2.0
        )
        
        assert particle.emoji == "🌟"
        assert particle.x == 0.5
        assert particle.y == 0.3
        assert particle.velocity_x == 1.0
        assert particle.velocity_y == 2.0
        assert particle.rotation == 0.0
        assert particle.scale == 1.0
        assert particle.opacity == 1.0
        assert particle.lifetime == 5.0
        assert particle.age == 0.0
        assert particle.particle_id is not None


class TestActiveRainEffect:
    """Test ActiveRainEffect model."""
    
    def test_active_effect_creation(self):
        """Test creating active rain effects."""
        effect_config = EmojiRainEffect(
            emojis=["🎊"],
            intensity=0.7,
            duration_seconds=4.0,
            animation_style=AnimationStyle.CELEBRATION_BURST
        )
        
        particles = [
            EmojiParticle(emoji="🎊", x=0.5, y=0.5, velocity_x=0, velocity_y=1)
        ]
        
        active_effect = ActiveRainEffect(
            effect_id="test-effect",
            effect_config=effect_config,
            particles=particles,
            start_time=datetime.now(),
            duration=4.0,
            trigger_event="test_event"
        )
        
        assert active_effect.effect_id == "test-effect"
        assert active_effect.effect_config == effect_config
        assert len(active_effect.particles) == 1
        assert active_effect.duration == 4.0
        assert active_effect.trigger_event == "test_event"
        assert active_effect.is_active is True


class TestEmojiRainWebSocketHandler:
    """Test WebSocket handler for emoji rain."""
    
    @pytest.fixture
    def emoji_engine(self):
        """Create an emoji engine for testing."""
        return EmojiRainEngine()
    
    @pytest.fixture
    def ws_handler(self, emoji_engine):
        """Create a WebSocket handler for testing."""
        return EmojiRainWebSocketHandler(emoji_engine)
    
    @pytest.mark.asyncio
    async def test_add_remove_client(self, ws_handler):
        """Test adding and removing WebSocket clients."""
        mock_websocket = Mock()
        
        # Add client
        await ws_handler.add_client(mock_websocket)
        assert mock_websocket in ws_handler.connected_clients
        assert len(ws_handler.connected_clients) == 1
        
        # Remove client
        await ws_handler.remove_client(mock_websocket)
        assert mock_websocket not in ws_handler.connected_clients
        assert len(ws_handler.connected_clients) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_frame_update(self, ws_handler):
        """Test broadcasting frame updates to clients."""
        # Add mock clients
        mock_client1 = AsyncMock()
        mock_client2 = AsyncMock()
        
        await ws_handler.add_client(mock_client1)
        await ws_handler.add_client(mock_client2)
        
        # Broadcast frame update
        frame_data = {
            "timestamp": datetime.now().isoformat(),
            "active_effects": 1,
            "total_particles": 5,
            "effects": []
        }
        
        await ws_handler._broadcast_frame_update(frame_data)
        
        # Check that both clients received the message
        mock_client1.send.assert_called_once()
        mock_client2.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_broadcast_with_failed_client(self, ws_handler):
        """Test broadcasting when a client connection fails."""
        # Add mock clients - one working, one failing
        working_client = AsyncMock()
        failing_client = AsyncMock()
        failing_client.send.side_effect = Exception("Connection failed")
        
        await ws_handler.add_client(working_client)
        await ws_handler.add_client(failing_client)
        
        assert len(ws_handler.connected_clients) == 2
        
        # Broadcast frame update
        frame_data = {"test": "data"}
        await ws_handler._broadcast_frame_update(frame_data)
        
        # Working client should still be connected, failing client should be removed
        assert working_client in ws_handler.connected_clients
        assert failing_client not in ws_handler.connected_clients
        assert len(ws_handler.connected_clients) == 1


class TestEmojiIntensity:
    """Test EmojiIntensity enum."""
    
    def test_intensity_values(self):
        """Test emoji intensity enum values."""
        assert EmojiIntensity.GENTLE.value == 0.2
        assert EmojiIntensity.MODERATE.value == 0.5
        assert EmojiIntensity.INTENSE.value == 0.8
        assert EmojiIntensity.CELEBRATION.value == 1.0