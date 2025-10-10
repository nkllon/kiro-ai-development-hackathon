"""
Emoji Rain Integration for Achievement Celebrations

This module provides integration between the Achievement Tracker and the Emoji Rain
system to create spectacular celebration effects when achievements are unlocked.
"""

import asyncio
import json
import logging
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

from .achievement_models import CelebrationLevel, AchievementRarity


@dataclass
class EmojiRainPattern:
    """Configuration for emoji rain celebration patterns."""
    pattern_id: str
    name: str
    emoji_sequence: List[str]
    duration_ms: int = 3000
    intensity: float = 1.0
    drop_rate: int = 20  # emojis per second
    fade_effect: bool = True
    bounce_effect: bool = False
    sparkle_effect: bool = False
    message_overlay: Optional[str] = None


@dataclass
class CelebrationTrigger:
    """Trigger configuration for celebrations."""
    trigger_id: str
    celebration_type: str  # "achievement", "milestone", "streak", "custom"
    conditions: Dict[str, Any] = field(default_factory=dict)
    emoji_patterns: List[str] = field(default_factory=list)
    custom_effects: Dict[str, Any] = field(default_factory=dict)


class EmojiRainIntegration:
    """
    Integration system for triggering emoji rain celebrations based on achievements.

    Provides sophisticated celebration effects that scale with achievement rarity
    and importance, creating an engaging gamification experience.
    """

    def __init__(self, websocket_manager=None, frontend_integration=None):
        self.websocket_manager = websocket_manager
        self.frontend_integration = frontend_integration
        self.instance_id = f"emoji_rain_{uuid.uuid4().hex[:8]}"
        self._logger = logging.getLogger(f"{__name__}.EmojiRainIntegration")

        # Rain patterns registry
        self.rain_patterns: Dict[str, EmojiRainPattern] = {}
        self.celebration_triggers: Dict[str, CelebrationTrigger] = {}

        # Active celebrations tracking
        self.active_celebrations: List[Dict[str, Any]] = []
        self.celebration_queue: asyncio.Queue = asyncio.Queue()

        # Performance tracking
        self._celebrations_triggered = 0
        self._total_emojis_sent = 0
        self._celebration_start_time = datetime.now()

        # Initialize default patterns
        self._initialize_default_patterns()

        # Start celebration processor (only if event loop is running)
        try:
            self._processor_task = asyncio.create_task(self._process_celebration_queue())
        except RuntimeError:
            # No event loop running (likely in tests)
            self._processor_task = None

        self._logger.info(
            f"EmojiRainIntegration initialized",
            extra={
                "instance_id": self.instance_id,
                "default_patterns": len(self.rain_patterns),
                "websocket_available": self.websocket_manager is not None
            }
        )

    def _initialize_default_patterns(self):
        """Initialize default emoji rain patterns for different celebration types."""

        # Achievement rarity patterns
        self.register_pattern(EmojiRainPattern(
            pattern_id="common_achievement",
            name="Common Achievement",
            emoji_sequence=["⭐", "🌟"],
            duration_ms=2000,
            intensity=0.5,
            drop_rate=15,
            message_overlay="Nice work! ⭐"
        ))

        self.register_pattern(EmojiRainPattern(
            pattern_id="uncommon_achievement",
            name="Uncommon Achievement",
            emoji_sequence=["⭐", "🌟", "✨"],
            duration_ms=2500,
            intensity=0.7,
            drop_rate=20,
            sparkle_effect=True,
            message_overlay="Great achievement! ✨"
        ))

        self.register_pattern(EmojiRainPattern(
            pattern_id="rare_achievement",
            name="Rare Achievement",
            emoji_sequence=["🏆", "🌟", "✨", "💫"],
            duration_ms=3500,
            intensity=0.9,
            drop_rate=25,
            sparkle_effect=True,
            bounce_effect=True,
            message_overlay="Rare achievement unlocked! 🏆"
        ))

        self.register_pattern(EmojiRainPattern(
            pattern_id="epic_achievement",
            name="Epic Achievement",
            emoji_sequence=["🏆", "🎉", "🌟", "✨", "💫", "🎊"],
            duration_ms=4500,
            intensity=1.2,
            drop_rate=35,
            sparkle_effect=True,
            bounce_effect=True,
            message_overlay="EPIC ACHIEVEMENT! 🎉🏆"
        ))

        self.register_pattern(EmojiRainPattern(
            pattern_id="legendary_achievement",
            name="Legendary Achievement",
            emoji_sequence=["👑", "🏆", "🎉", "🌟", "✨", "💫", "🎊", "🚀", "💎"],
            duration_ms=6000,
            intensity=1.5,
            drop_rate=50,
            sparkle_effect=True,
            bounce_effect=True,
            fade_effect=True,
            message_overlay="🌟 LEGENDARY ACHIEVEMENT! 👑"
        ))

        # Milestone patterns
        self.register_pattern(EmojiRainPattern(
            pattern_id="daily_milestone",
            name="Daily Milestone",
            emoji_sequence=["🎯", "⭐", "🔥"],
            duration_ms=2000,
            intensity=0.6,
            drop_rate=18,
            message_overlay="Daily goal achieved! 🎯"
        ))

        self.register_pattern(EmojiRainPattern(
            pattern_id="weekly_milestone",
            name="Weekly Milestone",
            emoji_sequence=["🏆", "🎯", "⭐", "🔥"],
            duration_ms=3000,
            intensity=0.8,
            drop_rate=25,
            sparkle_effect=True,
            message_overlay="Weekly milestone reached! 🏆"
        ))

        self.register_pattern(EmojiRainPattern(
            pattern_id="streak_celebration",
            name="Streak Celebration",
            emoji_sequence=["🔥", "⚡", "🌟", "💥"],
            duration_ms=2500,
            intensity=0.9,
            drop_rate=30,
            bounce_effect=True,
            message_overlay="Streak maintained! 🔥"
        ))

        # Special coordination patterns
        self.register_pattern(EmojiRainPattern(
            pattern_id="perfect_coordination",
            name="Perfect Coordination",
            emoji_sequence=["🎪", "🎭", "🎨", "🎵", "🌈", "✨"],
            duration_ms=4000,
            intensity=1.1,
            drop_rate=40,
            sparkle_effect=True,
            bounce_effect=True,
            message_overlay="Perfect coordination! 🎪"
        ))

        self.register_pattern(EmojiRainPattern(
            pattern_id="innovation_burst",
            name="Innovation Burst",
            emoji_sequence=["💡", "🚀", "⚡", "🌟", "💫", "🔬"],
            duration_ms=3500,
            intensity=1.0,
            drop_rate=32,
            sparkle_effect=True,
            message_overlay="Innovation achieved! 💡🚀"
        ))

    def register_pattern(self, pattern: EmojiRainPattern):
        """Register a new emoji rain pattern."""
        self.rain_patterns[pattern.pattern_id] = pattern
        self._logger.debug(f"Registered emoji rain pattern: {pattern.name}")

    def register_celebration_trigger(self, trigger: CelebrationTrigger):
        """Register a celebration trigger configuration."""
        self.celebration_triggers[trigger.trigger_id] = trigger
        self._logger.debug(f"Registered celebration trigger: {trigger.celebration_type}")

    async def trigger_celebration_rain(self,
                                     emoji_patterns: Optional[List[str]] = None,
                                     duration_ms: int = 3000,
                                     intensity: float = 1.0,
                                     message: Optional[str] = None,
                                     celebration_type: str = "achievement",
                                     custom_effects: Optional[Dict[str, Any]] = None) -> bool:
        """
        Trigger emoji rain celebration with specified parameters.

        Args:
            emoji_patterns: List of emoji to use in rain
            duration_ms: Duration of celebration
            intensity: Intensity multiplier for effects
            message: Optional message to display
            celebration_type: Type of celebration
            custom_effects: Additional custom effects

        Returns:
            True if celebration was queued successfully
        """
        try:
            celebration_data = {
                "celebration_id": str(uuid.uuid4()),
                "type": celebration_type,
                "emoji_patterns": emoji_patterns or ["🌟"],
                "duration_ms": duration_ms,
                "intensity": intensity,
                "message": message,
                "custom_effects": custom_effects or {},
                "triggered_at": datetime.now(),
                "status": "queued"
            }

            await self.celebration_queue.put(celebration_data)

            self._logger.info(
                f"Queued celebration rain",
                extra={
                    "celebration_id": celebration_data["celebration_id"],
                    "type": celebration_type,
                    "duration_ms": duration_ms,
                    "emoji_count": len(emoji_patterns) if emoji_patterns else 1
                }
            )

            return True

        except Exception as e:
            self._logger.error(f"Error triggering celebration rain: {e}")
            return False

    async def trigger_achievement_celebration(self,
                                            achievement_name: str,
                                            achievement_rarity: str,
                                            celebration_level: str,
                                            unlock_message: Optional[str] = None,
                                            custom_patterns: Optional[List[str]] = None) -> bool:
        """
        Trigger achievement-specific celebration with appropriate effects.

        Args:
            achievement_name: Name of the unlocked achievement
            achievement_rarity: Rarity level (common, uncommon, rare, epic, legendary)
            celebration_level: Celebration intensity (subtle, normal, enhanced, spectacular)
            unlock_message: Custom unlock message
            custom_patterns: Custom emoji patterns to use

        Returns:
            True if celebration was triggered successfully
        """
        try:
            # Select appropriate pattern based on rarity
            pattern_id = f"{achievement_rarity}_achievement"
            pattern = self.rain_patterns.get(pattern_id)

            if custom_patterns:
                # Create temporary pattern for custom celebration
                pattern = EmojiRainPattern(
                    pattern_id=f"custom_{uuid.uuid4().hex[:8]}",
                    name=f"Custom {achievement_name}",
                    emoji_sequence=custom_patterns,
                    duration_ms=self._get_duration_for_level(celebration_level),
                    intensity=self._get_intensity_for_level(celebration_level)
                )
            elif not pattern:
                # Use default pattern if no custom patterns and no matching rarity pattern
                pattern = self.rain_patterns.get("common_achievement")

            if pattern:
                # Enhance pattern based on celebration level
                enhanced_pattern = self._enhance_pattern_for_level(pattern, celebration_level)

                celebration_data = {
                    "celebration_id": str(uuid.uuid4()),
                    "type": "achievement",
                    "achievement_name": achievement_name,
                    "achievement_rarity": achievement_rarity,
                    "celebration_level": celebration_level,
                    "pattern": enhanced_pattern,
                    "message": unlock_message or f"{achievement_name} unlocked!",
                    "triggered_at": datetime.now(),
                    "status": "queued"
                }

                await self.celebration_queue.put(celebration_data)

                self._logger.info(
                    f"Queued achievement celebration",
                    extra={
                        "achievement_name": achievement_name,
                        "rarity": achievement_rarity,
                        "celebration_level": celebration_level
                    }
                )

                return True

            else:
                # Fallback to basic celebration
                return await self.trigger_celebration_rain(
                    emoji_patterns=custom_patterns or ["🌟", "⭐"],
                    duration_ms=3000,
                    intensity=0.8,
                    message=unlock_message or f"{achievement_name} unlocked!",
                    celebration_type="achievement"
                )

        except Exception as e:
            self._logger.error(f"Error triggering achievement celebration: {e}")
            return False

    async def trigger_milestone_celebration(self,
                                          milestone_name: str,
                                          milestone_type: str,
                                          threshold_reached: float,
                                          custom_message: Optional[str] = None) -> bool:
        """
        Trigger milestone-specific celebration.

        Args:
            milestone_name: Name of the milestone
            milestone_type: Type of milestone (daily, weekly, etc.)
            threshold_reached: The threshold value that was reached
            custom_message: Custom celebration message

        Returns:
            True if celebration was triggered successfully
        """
        try:
            # Select pattern based on milestone type
            pattern_mapping = {
                "daily": "daily_milestone",
                "weekly": "weekly_milestone",
                "streak": "streak_celebration",
                "coordination": "perfect_coordination"
            }

            pattern_id = pattern_mapping.get(milestone_type, "daily_milestone")
            pattern = self.rain_patterns.get(pattern_id)

            if pattern:
                celebration_data = {
                    "celebration_id": str(uuid.uuid4()),
                    "type": "milestone",
                    "milestone_name": milestone_name,
                    "milestone_type": milestone_type,
                    "threshold_reached": threshold_reached,
                    "pattern": pattern,
                    "message": custom_message or f"{milestone_name} milestone reached!",
                    "triggered_at": datetime.now(),
                    "status": "queued"
                }

                await self.celebration_queue.put(celebration_data)

                self._logger.info(
                    f"Queued milestone celebration",
                    extra={
                        "milestone_name": milestone_name,
                        "milestone_type": milestone_type,
                        "threshold": threshold_reached
                    }
                )

                return True

            return False

        except Exception as e:
            self._logger.error(f"Error triggering milestone celebration: {e}")
            return False

    async def _process_celebration_queue(self):
        """Background processor for celebration queue."""
        self._logger.info("Started celebration queue processor")

        while True:
            try:
                # Get next celebration from queue
                celebration_data = await asyncio.wait_for(
                    self.celebration_queue.get(), timeout=1.0
                )

                await self._execute_celebration(celebration_data)

            except asyncio.TimeoutError:
                # Check for cleanup of active celebrations
                await self._cleanup_active_celebrations()

            except Exception as e:
                self._logger.error(f"Error in celebration processor: {e}")

    async def _execute_celebration(self, celebration_data: Dict[str, Any]):
        """Execute a queued celebration."""
        try:
            celebration_data["status"] = "executing"
            celebration_data["execution_start"] = datetime.now()

            # Add to active celebrations
            self.active_celebrations.append(celebration_data)

            # Execute based on celebration type
            celebration_type = celebration_data.get("type", "generic")

            if celebration_type == "achievement":
                await self._execute_achievement_celebration(celebration_data)
            elif celebration_type == "milestone":
                await self._execute_milestone_celebration(celebration_data)
            else:
                await self._execute_generic_celebration(celebration_data)

            # Update metrics
            self._celebrations_triggered += 1

            self._logger.debug(
                f"Executed celebration",
                extra={
                    "celebration_id": celebration_data["celebration_id"],
                    "type": celebration_type
                }
            )

        except Exception as e:
            self._logger.error(f"Error executing celebration: {e}")
            celebration_data["status"] = "failed"
            celebration_data["error"] = str(e)

    async def _execute_achievement_celebration(self, celebration_data: Dict[str, Any]):
        """Execute achievement-specific celebration effects."""
        pattern = celebration_data.get("pattern")
        if not pattern:
            return

        # Send to websocket clients
        if self.websocket_manager:
            websocket_message = {
                "type": "achievement_celebration",
                "celebration_id": celebration_data["celebration_id"],
                "achievement_name": celebration_data.get("achievement_name"),
                "achievement_rarity": celebration_data.get("achievement_rarity"),
                "emoji_patterns": pattern.emoji_sequence,
                "duration_ms": pattern.duration_ms,
                "intensity": pattern.intensity,
                "effects": {
                    "sparkle": pattern.sparkle_effect,
                    "bounce": pattern.bounce_effect,
                    "fade": pattern.fade_effect
                },
                "message": celebration_data.get("message"),
                "timestamp": datetime.now().isoformat()
            }

            await self._send_to_websockets(websocket_message)

        # Send to frontend integration
        if self.frontend_integration:
            await self.frontend_integration.trigger_rain_effect(
                emojis=pattern.emoji_sequence,
                duration=pattern.duration_ms,
                intensity=pattern.intensity,
                message=celebration_data.get("message")
            )

        # Track emoji count
        estimated_emoji_count = (pattern.drop_rate * pattern.duration_ms) // 1000
        self._total_emojis_sent += estimated_emoji_count

    async def _execute_milestone_celebration(self, celebration_data: Dict[str, Any]):
        """Execute milestone-specific celebration effects."""
        pattern = celebration_data.get("pattern")
        if not pattern:
            return

        # Similar to achievement but with milestone-specific messaging
        if self.websocket_manager:
            websocket_message = {
                "type": "milestone_celebration",
                "celebration_id": celebration_data["celebration_id"],
                "milestone_name": celebration_data.get("milestone_name"),
                "milestone_type": celebration_data.get("milestone_type"),
                "threshold_reached": celebration_data.get("threshold_reached"),
                "emoji_patterns": pattern.emoji_sequence,
                "duration_ms": pattern.duration_ms,
                "intensity": pattern.intensity,
                "effects": {
                    "sparkle": pattern.sparkle_effect,
                    "bounce": pattern.bounce_effect,
                    "fade": pattern.fade_effect
                },
                "message": celebration_data.get("message"),
                "timestamp": datetime.now().isoformat()
            }

            await self._send_to_websockets(websocket_message)

        if self.frontend_integration:
            await self.frontend_integration.trigger_rain_effect(
                emojis=pattern.emoji_sequence,
                duration=pattern.duration_ms,
                intensity=pattern.intensity,
                message=celebration_data.get("message")
            )

    async def _execute_generic_celebration(self, celebration_data: Dict[str, Any]):
        """Execute generic celebration effects."""
        emoji_patterns = celebration_data.get("emoji_patterns", ["🌟"])
        duration_ms = celebration_data.get("duration_ms", 3000)
        intensity = celebration_data.get("intensity", 1.0)

        if self.websocket_manager:
            websocket_message = {
                "type": "generic_celebration",
                "celebration_id": celebration_data["celebration_id"],
                "emoji_patterns": emoji_patterns,
                "duration_ms": duration_ms,
                "intensity": intensity,
                "message": celebration_data.get("message"),
                "timestamp": datetime.now().isoformat()
            }

            await self._send_to_websockets(websocket_message)

        if self.frontend_integration:
            await self.frontend_integration.trigger_rain_effect(
                emojis=emoji_patterns,
                duration=duration_ms,
                intensity=intensity,
                message=celebration_data.get("message")
            )

    async def _send_to_websockets(self, message: Dict[str, Any]):
        """Send celebration message to all websocket clients."""
        try:
            message_json = json.dumps(message)
            await self.websocket_manager.broadcast_message(message_json)

        except Exception as e:
            self._logger.error(f"Error sending websocket message: {e}")

    async def _cleanup_active_celebrations(self):
        """Clean up completed celebrations."""
        current_time = datetime.now()
        completed_celebrations = []

        for celebration in self.active_celebrations:
            execution_start = celebration.get("execution_start")
            if not execution_start:
                continue

            # Get duration from pattern or fallback
            pattern = celebration.get("pattern")
            duration_ms = getattr(pattern, 'duration_ms', None) if pattern else None
            if not duration_ms:
                duration_ms = celebration.get("duration_ms", 3000)

            # Check if celebration is complete
            elapsed_ms = (current_time - execution_start).total_seconds() * 1000
            if elapsed_ms >= duration_ms:
                celebration["status"] = "completed"
                celebration["completed_at"] = current_time
                completed_celebrations.append(celebration)

        # Remove completed celebrations
        for celebration in completed_celebrations:
            if celebration in self.active_celebrations:
                self.active_celebrations.remove(celebration)

    def _get_duration_for_level(self, celebration_level: str) -> int:
        """Get duration based on celebration level."""
        durations = {
            "subtle": 1500,
            "normal": 2500,
            "enhanced": 3500,
            "spectacular": 5000
        }
        return durations.get(celebration_level, 2500)

    def _get_intensity_for_level(self, celebration_level: str) -> float:
        """Get intensity based on celebration level."""
        intensities = {
            "subtle": 0.5,
            "normal": 0.7,
            "enhanced": 0.9,
            "spectacular": 1.2
        }
        return intensities.get(celebration_level, 0.7)

    def _enhance_pattern_for_level(self, base_pattern: EmojiRainPattern, celebration_level: str) -> EmojiRainPattern:
        """Enhance a base pattern for the specified celebration level."""
        enhanced = EmojiRainPattern(
            pattern_id=f"{base_pattern.pattern_id}_{celebration_level}",
            name=f"{base_pattern.name} ({celebration_level.title()})",
            emoji_sequence=base_pattern.emoji_sequence.copy(),
            duration_ms=max(base_pattern.duration_ms, self._get_duration_for_level(celebration_level)),
            intensity=max(base_pattern.intensity, self._get_intensity_for_level(celebration_level)),
            drop_rate=base_pattern.drop_rate,
            fade_effect=base_pattern.fade_effect,
            bounce_effect=base_pattern.bounce_effect or (celebration_level in ["enhanced", "spectacular"]),
            sparkle_effect=base_pattern.sparkle_effect or (celebration_level in ["enhanced", "spectacular"]),
            message_overlay=base_pattern.message_overlay
        )

        # Enhance effects for higher celebration levels
        if celebration_level == "spectacular":
            enhanced.drop_rate = int(enhanced.drop_rate * 1.5)
            enhanced.sparkle_effect = True
            enhanced.bounce_effect = True

        return enhanced

    def get_celebration_stats(self) -> Dict[str, Any]:
        """Get statistics about celebration activity."""
        uptime_hours = (datetime.now() - self._celebration_start_time).total_seconds() / 3600

        return {
            "instance_id": self.instance_id,
            "celebrations_triggered": self._celebrations_triggered,
            "total_emojis_sent": self._total_emojis_sent,
            "active_celebrations": len(self.active_celebrations),
            "patterns_registered": len(self.rain_patterns),
            "uptime_hours": uptime_hours,
            "celebrations_per_hour": self._celebrations_triggered / uptime_hours if uptime_hours > 0 else 0,
            "queue_size": self.celebration_queue.qsize(),
            "websocket_integration": self.websocket_manager is not None,
            "frontend_integration": self.frontend_integration is not None
        }

    async def shutdown(self):
        """Gracefully shutdown the emoji rain integration."""
        self._logger.info("Shutting down emoji rain integration")

        # Cancel processor task
        if hasattr(self, '_processor_task') and self._processor_task is not None and not self._processor_task.cancelled():
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

        # Clear active celebrations
        self.active_celebrations.clear()

        # Clear queue
        while not self.celebration_queue.empty():
            try:
                self.celebration_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        self._logger.info("Emoji rain integration shutdown complete")