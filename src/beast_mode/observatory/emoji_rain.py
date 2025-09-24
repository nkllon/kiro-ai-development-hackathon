"""
Emoji Rain Engine - The delightful visual celebration system for the Observatory.

This module transforms coordination events into beautiful, cascading emoji effects
that make systematic coordination feel rewarding and engaging.
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any
from uuid import uuid4

from .models import (
    CoordinationEvent,
    CoordinationEventType,
    EmojiRainEffect,
    AnimationStyle,
    Achievement,
    CelebrationEffect,
)


logger = logging.getLogger(__name__)


class EmojiIntensity(Enum):
    """Intensity levels for emoji rain effects."""
    GENTLE = 0.2
    MODERATE = 0.5
    INTENSE = 0.8
    CELEBRATION = 1.0


@dataclass
class EmojiParticle:
    """Individual emoji particle in the rain effect."""
    emoji: str
    x: float  # Horizontal position (0.0 to 1.0)
    y: float  # Vertical position (0.0 to 1.0)
    velocity_x: float  # Horizontal velocity
    velocity_y: float  # Vertical velocity
    rotation: float = 0.0
    rotation_speed: float = 0.0
    scale: float = 1.0
    opacity: float = 1.0
    lifetime: float = 5.0  # Seconds
    age: float = 0.0
    particle_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class ActiveRainEffect:
    """Currently active emoji rain effect."""
    effect_id: str
    effect_config: EmojiRainEffect
    particles: List[EmojiParticle]
    start_time: datetime
    duration: float
    trigger_event: str
    is_active: bool = True


class EmojiRainEngine:
    """
    Manages delightful emoji rain visualization for coordination events.
    
    The Matrix had it wrong - it's not green and black, it's raining emojis!
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}
        self._active_effects: Dict[str, ActiveRainEffect] = {}
        self._event_mappings = self._initialize_event_mappings()
        self._animation_callbacks: List[Callable] = []
        self._running = False
        self._animation_task: Optional[asyncio.Task] = None
        self._frame_rate = 60  # Target 60 FPS
        self._canvas_width = 1920  # Default canvas dimensions
        self._canvas_height = 1080
        
        logger.info("🌧️ Emoji Rain Engine initialized - Ready to make it rain!")
    
    def _initialize_event_mappings(self) -> Dict[CoordinationEventType, Dict[str, Any]]:
        """Initialize the mapping from coordination events to emoji effects."""
        return {
            CoordinationEventType.TASK_COMPLETED: {
                "emojis": ["✅", "🎉", "🚀", "⭐", "💫"],
                "intensity": EmojiIntensity.MODERATE,
                "duration": 3.0,
                "animation_style": AnimationStyle.GENTLE_FALL,
                "colors": ["#00FF00", "#FFD700", "#FF6B6B"]
            },
            CoordinationEventType.API_CALL_SUCCESS: {
                "emojis": ["⚡", "🔥", "💨", "🎯", "✨"],
                "intensity": EmojiIntensity.GENTLE,
                "duration": 2.0,
                "animation_style": AnimationStyle.GENTLE_FALL,
                "colors": ["#4ECDC4", "#45B7D1", "#96CEB4"]
            },
            CoordinationEventType.COST_THRESHOLD_REACHED: {
                "emojis": ["💰", "📉", "🎯", "💎", "🏆"],
                "intensity": EmojiIntensity.MODERATE,
                "duration": 4.0,
                "animation_style": AnimationStyle.CELEBRATION_BURST,
                "colors": ["#FFD700", "#FFA500", "#FF6B6B"]
            },
            CoordinationEventType.ANOMALY_DETECTED: {
                "emojis": ["⚠️", "🔍", "📊", "🔧", "🛠️"],
                "intensity": EmojiIntensity.GENTLE,
                "duration": 2.5,
                "animation_style": AnimationStyle.ALERT_PULSE,
                "colors": ["#FF6B6B", "#FFA500", "#FFD700"]
            },
            CoordinationEventType.ACHIEVEMENT_UNLOCKED: {
                "emojis": ["🏆", "🎊", "🌟", "🎉", "👑", "💎", "🚀"],
                "intensity": EmojiIntensity.CELEBRATION,
                "duration": 6.0,
                "animation_style": AnimationStyle.CELEBRATION_BURST,
                "colors": ["#FFD700", "#FF6B6B", "#4ECDC4", "#9B59B6"]
            },
            CoordinationEventType.COORDINATION_MILESTONE: {
                "emojis": ["🤝", "⚙️", "🔄", "🎯", "📈", "✨"],
                "intensity": EmojiIntensity.INTENSE,
                "duration": 5.0,
                "animation_style": AnimationStyle.CELEBRATION_BURST,
                "colors": ["#2ECC71", "#3498DB", "#E74C3C"]
            },
            CoordinationEventType.SYSTEM_HEALTH_CHANGE: {
                "emojis": ["💚", "📊", "⚡", "🔋", "💪"],
                "intensity": EmojiIntensity.MODERATE,
                "duration": 3.0,
                "animation_style": AnimationStyle.GENTLE_FALL,
                "colors": ["#2ECC71", "#27AE60", "#16A085"]
            }
        }
    
    async def start_animation_loop(self) -> None:
        """Start the main animation loop for emoji rain effects."""
        if self._running:
            logger.warning("Emoji rain animation loop already running")
            return
        
        self._running = True
        self._animation_task = asyncio.create_task(self._animation_loop())
        logger.info("🎬 Emoji rain animation loop started at 60 FPS")
    
    async def stop_animation_loop(self) -> None:
        """Stop the animation loop gracefully."""
        self._running = False
        if self._animation_task and not self._animation_task.done():
            self._animation_task.cancel()
            try:
                await self._animation_task
            except asyncio.CancelledError:
                pass
        
        self._active_effects.clear()
        logger.info("🛑 Emoji rain animation loop stopped")
    
    async def _animation_loop(self) -> None:
        """Main animation loop that updates all active emoji effects."""
        frame_duration = 1.0 / self._frame_rate
        
        while self._running:
            frame_start = time.time()
            
            try:
                # Update all active effects
                await self._update_active_effects(frame_duration)
                
                # Notify animation callbacks
                await self._notify_animation_callbacks()
                
                # Calculate sleep time to maintain frame rate
                frame_time = time.time() - frame_start
                sleep_time = max(0, frame_duration - frame_time)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
            except asyncio.CancelledError:
                logger.info("Animation loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in animation loop: {e}")
                await asyncio.sleep(0.1)  # Brief pause on error
    
    async def _update_active_effects(self, delta_time: float) -> None:
        """Update all active emoji rain effects."""
        effects_to_remove = []
        
        for effect_id, effect in self._active_effects.items():
            # Check if effect has expired
            elapsed = (datetime.now() - effect.start_time).total_seconds()
            if elapsed >= effect.duration:
                effects_to_remove.append(effect_id)
                continue
            
            # Update particles
            particles_to_remove = []
            for i, particle in enumerate(effect.particles):
                # Update particle physics
                self._update_particle_physics(particle, delta_time)
                
                # Update particle age and lifetime
                particle.age += delta_time
                if particle.age >= particle.lifetime:
                    particles_to_remove.append(i)
            
            # Remove expired particles
            for i in reversed(particles_to_remove):
                effect.particles.pop(i)
            
            # Add new particles if needed (for continuous effects)
            if effect.effect_config.animation_style == AnimationStyle.CELEBRATION_BURST:
                await self._maybe_add_burst_particles(effect, delta_time)
        
        # Remove expired effects
        for effect_id in effects_to_remove:
            logger.debug(f"🌧️ Emoji rain effect {effect_id} completed")
            del self._active_effects[effect_id]
    
    def _update_particle_physics(self, particle: EmojiParticle, delta_time: float) -> None:
        """Update particle physics simulation."""
        # Apply gravity
        gravity = 0.5
        particle.velocity_y += gravity * delta_time
        
        # Apply air resistance
        air_resistance = 0.98
        particle.velocity_x *= air_resistance
        particle.velocity_y *= air_resistance
        
        # Update position
        particle.x += particle.velocity_x * delta_time
        particle.y += particle.velocity_y * delta_time
        
        # Update rotation
        particle.rotation += particle.rotation_speed * delta_time
        
        # Update opacity based on age
        age_ratio = particle.age / particle.lifetime
        if age_ratio > 0.7:  # Start fading in last 30% of lifetime
            fade_ratio = (age_ratio - 0.7) / 0.3
            particle.opacity = 1.0 - fade_ratio
        
        # Wrap around screen edges
        if particle.x < -0.1:
            particle.x = 1.1
        elif particle.x > 1.1:
            particle.x = -0.1
    
    async def _maybe_add_burst_particles(self, effect: ActiveRainEffect, delta_time: float) -> None:
        """Add new particles for burst-style effects."""
        # Add particles at a rate based on intensity
        intensity = effect.effect_config.intensity
        particles_per_second = intensity * 20  # Up to 20 particles per second at max intensity
        
        if random.random() < particles_per_second * delta_time:
            new_particle = self._create_particle(effect.effect_config)
            effect.particles.append(new_particle)
    
    async def _notify_animation_callbacks(self) -> None:
        """Notify all registered animation callbacks with current frame data."""
        if not self._animation_callbacks:
            logger.debug("No animation callbacks registered")
            return
        
        frame_data = {
            "timestamp": datetime.now().isoformat(),
            "active_effects": len(self._active_effects),
            "total_particles": sum(len(effect.particles) for effect in self._active_effects.values()),
            "effects": [
                {
                    "effect_id": effect_id,
                    "trigger_event": effect.trigger_event,
                    "particle_count": len(effect.particles),
                    "particles": [
                        {
                            "emoji": p.emoji,
                            "x": p.x,
                            "y": p.y,
                            "rotation": p.rotation,
                            "scale": p.scale,
                            "opacity": p.opacity
                        }
                        for p in effect.particles
                    ]
                }
                for effect_id, effect in self._active_effects.items()
            ]
        }
        
        logger.debug(f"Notifying {len(self._animation_callbacks)} callbacks with {frame_data['total_particles']} particles")
        
        # Notify all callbacks
        for callback in self._animation_callbacks:
            try:
                logger.debug(f"Calling callback: {callback.__name__} (async: {asyncio.iscoroutinefunction(callback)})")
                if asyncio.iscoroutinefunction(callback):
                    await callback(frame_data)
                else:
                    callback(frame_data)
                logger.debug(f"Successfully called callback: {callback.__name__}")
            except Exception as e:
                logger.error(f"Error in animation callback {callback.__name__}: {e}")
    
    def register_animation_callback(self, callback: Callable) -> None:
        """Register a callback to receive animation frame updates."""
        self._animation_callbacks.append(callback)
        logger.debug(f"Registered animation callback: {callback.__name__}")
    
    def unregister_animation_callback(self, callback: Callable) -> None:
        """Unregister an animation callback."""
        if callback in self._animation_callbacks:
            self._animation_callbacks.remove(callback)
            logger.debug(f"Unregistered animation callback: {callback.__name__}")
    
    async def trigger_event_rain(self, event: CoordinationEvent) -> str:
        """
        Trigger emoji rain based on a coordination event.

        Args:
            event: The coordination event that triggered the rain

        Returns:
            Effect ID for the created rain effect
        """
        # Get event mapping
        event_mapping = self._event_mappings.get(event.event_type)
        if not event_mapping:
            logger.debug(f"No emoji mapping for event type: {event.event_type}")
            return ""

        # Create emoji rain effect
        effect_config = EmojiRainEffect(
            emojis=event_mapping["emojis"],
            intensity=event_mapping["intensity"].value,
            duration_seconds=event_mapping["duration"],
            animation_style=event_mapping["animation_style"],
            trigger_event=event.event_type.name
        )

        effect_id = await self.create_rain_effect(effect_config)

        logger.info(f"🌧️ Triggered {event.event_type.name} emoji rain: {effect_config.emojis[:3]}... (ID: {effect_id})")
        return effect_id

    
    async def create_rain_effect(self, effect_config: EmojiRainEffect) -> str:
        """
        Create a new emoji rain effect.
        
        Args:
            effect_config: Configuration for the rain effect
            
        Returns:
            Effect ID for the created effect
        """
        effect_id = str(uuid4())
        
        # Create initial particles
        particles = []
        initial_particle_count = int(effect_config.intensity * 30)  # Up to 30 initial particles
        
        for _ in range(initial_particle_count):
            particle = self._create_particle(effect_config)
            particles.append(particle)
        
        # Create active effect
        active_effect = ActiveRainEffect(
            effect_id=effect_id,
            effect_config=effect_config,
            particles=particles,
            start_time=datetime.now(),
            duration=effect_config.duration_seconds,
            trigger_event=effect_config.trigger_event
        )
        
        self._active_effects[effect_id] = active_effect
        
        logger.debug(f"Created emoji rain effect {effect_id} with {len(particles)} particles")
        return effect_id
    
    def _create_particle(self, effect_config: EmojiRainEffect) -> EmojiParticle:
        """Create a new emoji particle based on effect configuration."""
        emoji = random.choice(effect_config.emojis)
        
        # Position based on animation style
        if effect_config.animation_style == AnimationStyle.CELEBRATION_BURST:
            # Start from center and burst outward
            x = 0.5 + random.uniform(-0.2, 0.2)
            y = 0.5 + random.uniform(-0.2, 0.2)
            velocity_x = random.uniform(-2.0, 2.0)
            velocity_y = random.uniform(-3.0, -1.0)
        else:
            # Start from top and fall down
            x = random.uniform(0.0, 1.0)
            y = random.uniform(-0.1, 0.0)
            velocity_x = random.uniform(-0.5, 0.5)
            velocity_y = random.uniform(0.5, 1.5)
        
        return EmojiParticle(
            emoji=emoji,
            x=x,
            y=y,
            velocity_x=velocity_x,
            velocity_y=velocity_y,
            rotation=random.uniform(0, 360),
            rotation_speed=random.uniform(-180, 180),  # degrees per second
            scale=random.uniform(0.8, 1.2),
            opacity=1.0,
            lifetime=random.uniform(3.0, 8.0)
        )
    
    async def create_achievement_celebration(self, achievement: Achievement) -> str:
        """
        Create a special celebration effect for achievements.
        
        Args:
            achievement: The achievement that was unlocked
            
        Returns:
            Effect ID for the celebration
        """
        # Create extra special effect for achievements
        celebration_emojis = ["🏆", "🎊", "🌟", "🎉", "👑", "💎", "🚀", "✨", "🎯"]
        
        effect_config = EmojiRainEffect(
            emojis=celebration_emojis,
            intensity=1.0,  # Maximum intensity
            duration_seconds=8.0,  # Longer duration
            animation_style=AnimationStyle.CELEBRATION_BURST,
            trigger_event=f"achievement_{achievement.achievement_id}"
        )
        
        effect_id = await self.create_rain_effect(effect_config)
        
        logger.info(f"🏆 Created achievement celebration for '{achievement.name}': {effect_id}")
        return effect_id
    
    def get_active_effects(self) -> Dict[str, Dict[str, Any]]:
        """Get information about currently active effects."""
        return {
            effect_id: {
                "trigger_event": effect.trigger_event,
                "duration": effect.duration,
                "elapsed": (datetime.now() - effect.start_time).total_seconds(),
                "particle_count": len(effect.particles),
                "emojis": effect.effect_config.emojis,
                "intensity": effect.effect_config.intensity
            }
            for effect_id, effect in self._active_effects.items()
        }
    
    def set_canvas_size(self, width: int, height: int) -> None:
        """Set the canvas dimensions for particle positioning."""
        self._canvas_width = width
        self._canvas_height = height
        logger.debug(f"Canvas size set to {width}x{height}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the emoji rain engine."""
        total_particles = sum(len(effect.particles) for effect in self._active_effects.values())
        
        return {
            "active_effects": len(self._active_effects),
            "total_particles": total_particles,
            "target_fps": self._frame_rate,
            "canvas_size": f"{self._canvas_width}x{self._canvas_height}",
            "animation_running": self._running,
            "registered_callbacks": len(self._animation_callbacks)
        }


class EmojiRainWebSocketHandler:
    """Handles WebSocket communication for real-time emoji rain updates."""
    
    def __init__(self, emoji_engine: EmojiRainEngine):
        self.emoji_engine = emoji_engine
        self.connected_clients: List[Any] = []  # WebSocket connections
        
        # Register for animation updates
        self.emoji_engine.register_animation_callback(self._broadcast_frame_update)
    
    async def add_client(self, websocket) -> None:
        """Add a new WebSocket client."""
        logger.debug(f"🔌 Adding client: {type(websocket)} - {websocket}")
        self.connected_clients.append(websocket)
        logger.info(f"🔌 New emoji rain client connected (total: {len(self.connected_clients)})")
    
    async def remove_client(self, websocket) -> None:
        """Remove a WebSocket client."""
        if websocket in self.connected_clients:
            self.connected_clients.remove(websocket)
            logger.info(f"🔌 Emoji rain client disconnected (total: {len(self.connected_clients)})")
    
    async def _broadcast_frame_update(self, frame_data: Dict[str, Any]) -> None:
        """Broadcast frame updates to all connected clients."""
        logger.debug(f"🔄 _broadcast_frame_update called with {len(self.connected_clients)} clients")
        
        if not self.connected_clients:
            logger.debug("No WebSocket clients connected for emoji rain updates")
            return
        
        message = {
            "type": "emoji_rain_frame",
            "data": frame_data
        }
        
        logger.debug(f"📡 Broadcasting frame with {frame_data.get('total_particles', 0)} particles to {len(self.connected_clients)} clients")
        
        # Send to all connected clients
        disconnected_clients = []
        for i, client in enumerate(self.connected_clients):
            try:
                logger.debug(f"🔄 Sending to client {i}: {type(client)}")
                await client.send_text(json.dumps(message))  # Use send_text instead of send
                logger.debug(f"✅ Sent frame to client {i}")
            except Exception as e:
                logger.warning(f"❌ Failed to send to client {i}: {e}")
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.remove_client(client)