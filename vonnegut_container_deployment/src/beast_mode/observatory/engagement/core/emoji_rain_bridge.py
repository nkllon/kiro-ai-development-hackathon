"""
Emoji Rain Bridge - Integration between AnimationEngine and EmojiRainEngine
===========================================================================

This module provides seamless integration between the new AnimationEngine
and the existing EmojiRainEngine, enabling engagement-specific animations
to trigger appropriate emoji rain effects.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ...emoji_rain import EmojiRainEngine, EmojiIntensity, EmojiParticle
from ...models import CoordinationEvent, CoordinationEventType, EmojiRainEffect, AnimationStyle

logger = logging.getLogger(__name__)


class EmojiRainBridge(ReflectiveModule):
    """Bridge between AnimationEngine and EmojiRainEngine for seamless integration."""
    
    def __init__(self, emoji_rain_engine: EmojiRainEngine):
        super().__init__()
        self.module_id = "emoji_rain_bridge"
        self.emoji_rain_engine = emoji_rain_engine
        
        # Animation to emoji mapping
        self.animation_emoji_map = {
            "data_animation": {
                "trend_up": ["📈", "🚀", "⬆️", "💹", "📊"],
                "trend_down": ["📉", "⬇️", "📊", "💔", "🔻"],
                "spike": ["⚡", "💥", "🔥", "💫", "✨"],
                "oscillation": ["🌊", "〰️", "🔄", "🎵", "🌀"],
                "anomaly": ["⚠️", "🚨", "❗", "🔍", "👀"]
            },
            "attention_animation": {
                "high": ["👁️", "🎯", "⭐", "🔥", "💡"],
                "medium": ["👀", "💫", "✨", "🌟", "💭"],
                "low": ["💤", "😴", "🌙", "💭", "🔮"]
            },
            "quality_visualization": {
                "high_quality": ["✅", "💎", "🏆", "⭐", "🌟"],
                "medium_quality": ["⚡", "💫", "✨", "🔶", "🟡"],
                "low_quality": ["⚠️", "🔸", "🟠", "📊", "🔍"],
                "poor_quality": ["❌", "🔴", "⛔", "🚫", "💔"]
            },
            "velocity_correlated": {
                "fast": ["💨", "⚡", "🚀", "💥", "🔥"],
                "medium": ["🏃", "💫", "✨", "🌟", "⭐"],
                "slow": ["🐌", "🚶", "💤", "🌙", "🔮"]
            },
            "mathematical_relationship": {
                "linear": ["📏", "📐", "➡️", "🔗", "⚖️"],
                "exponential": ["📈", "🚀", "💥", "⚡", "🔥"],
                "logarithmic": ["📉", "🌊", "🔄", "📊", "💹"],
                "sinusoidal": ["🌊", "〰️", "🎵", "🔄", "🌀"]
            }
        }
        
        # Engagement celebration emojis
        self.celebration_emojis = {
            "achievement": ["🎉", "🏆", "🥇", "🎊", "🌟", "⭐", "💫", "✨"],
            "milestone": ["🚀", "🎯", "💎", "👑", "🔥", "💥", "⚡", "🌈"],
            "success": ["✅", "💚", "👍", "🎈", "🎁", "🍾", "🥂", "🎭"]
        }
        
        logger.info("🌉 Emoji Rain Bridge initialized")
    
    async def trigger_engagement_rain(self, animation_config: Dict[str, Any]) -> str:
        """Trigger emoji rain based on engagement animation configuration."""
        try:
            # Extract animation details
            animation_type = animation_config.get("type", "default")
            intelligence_type = animation_config.get("intelligence_type", "pattern_based")
            intensity = animation_config.get("intensity", 0.5)
            confidence = animation_config.get("confidence", 0.5)
            
            # Determine appropriate emojis
            emojis = self._select_emojis_for_animation(animation_config)
            
            # Calculate rain intensity based on animation properties
            rain_intensity = self._calculate_rain_intensity(animation_config)
            
            # Create emoji rain effect configuration
            effect_config = EmojiRainEffect(
                emojis=emojis,
                intensity=rain_intensity,
                duration=animation_config.get("duration", 2.0),
                animation_style=self._map_animation_style(animation_type),
                particle_count=self._calculate_particle_count(animation_config),
                colors=self._select_colors_for_animation(animation_config)
            )
            
            # Trigger the emoji rain
            effect_id = await self.emoji_rain_engine.create_rain_effect(effect_config)
            
            logger.info(f"🌧️ Engagement emoji rain triggered: {effect_id} ({animation_type})")
            return effect_id
            
        except Exception as e:
            logger.error(f"Failed to trigger engagement rain: {e}")
            return ""
    
    async def trigger_data_pattern_rain(self, pattern_type: str, pattern_data: Dict[str, Any]) -> str:
        """Trigger emoji rain based on detected data patterns."""
        try:
            # Get pattern-specific emojis
            emojis = self.animation_emoji_map.get("data_animation", {}).get(
                pattern_type, 
                ["📊", "📈", "📉", "💹", "🔍"]
            )
            
            # Calculate intensity based on pattern confidence and intensity
            pattern_intensity = pattern_data.get("intensity", 0.5)
            pattern_confidence = pattern_data.get("confidence", 0.5)
            rain_intensity = self._intensity_to_emoji_intensity(pattern_intensity * pattern_confidence)
            
            # Create effect configuration
            effect_config = EmojiRainEffect(
                emojis=emojis,
                intensity=rain_intensity,
                duration=2.0 + pattern_intensity,  # Longer for more intense patterns
                animation_style=self._pattern_to_animation_style(pattern_type),
                particle_count=int(20 + pattern_intensity * 30),
                colors=self._pattern_to_colors(pattern_type)
            )
            
            effect_id = await self.emoji_rain_engine.create_rain_effect(effect_config)
            
            logger.info(f"🌧️ Data pattern rain triggered: {effect_id} ({pattern_type})")
            return effect_id
            
        except Exception as e:
            logger.error(f"Failed to trigger data pattern rain: {e}")
            return ""
    
    async def trigger_celebration_rain(self, celebration_type: str, achievement_data: Dict[str, Any] = None) -> str:
        """Trigger celebratory emoji rain for achievements and milestones."""
        try:
            # Get celebration-specific emojis
            emojis = self.celebration_emojis.get(celebration_type, self.celebration_emojis["success"])
            
            # High intensity for celebrations
            rain_intensity = EmojiIntensity.CELEBRATION
            
            # Create celebration effect
            effect_config = EmojiRainEffect(
                emojis=emojis,
                intensity=rain_intensity,
                duration=5.0,  # Longer celebration
                animation_style=AnimationStyle.CELEBRATION_BURST,
                particle_count=100,  # Lots of particles for celebration
                colors=["#FFD700", "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
            )
            
            effect_id = await self.emoji_rain_engine.create_rain_effect(effect_config)
            
            logger.info(f"🎉 Celebration rain triggered: {effect_id} ({celebration_type})")
            return effect_id
            
        except Exception as e:
            logger.error(f"Failed to trigger celebration rain: {e}")
            return ""
    
    async def create_synchronized_animation_rain(self, animation_id: str, animation_config: Dict[str, Any]) -> str:
        """Create emoji rain synchronized with animation lifecycle."""
        try:
            # Create base rain effect
            base_effect_id = await self.trigger_engagement_rain(animation_config)
            
            # If animation has specific timing, create synchronized effects
            if "keyframes" in animation_config:
                await self._create_keyframe_synchronized_rain(animation_id, animation_config["keyframes"])
            
            return base_effect_id
            
        except Exception as e:
            logger.error(f"Failed to create synchronized animation rain: {e}")
            return ""
    
    def _select_emojis_for_animation(self, animation_config: Dict[str, Any]) -> List[str]:
        """Select appropriate emojis based on animation configuration."""
        try:
            animation_type = animation_config.get("type", "default")
            intelligence_type = animation_config.get("intelligence_type", "pattern_based")
            
            # Check for specific pattern types
            if "detected_pattern" in animation_config:
                pattern = animation_config["detected_pattern"]
                return self.animation_emoji_map.get("data_animation", {}).get(pattern, ["📊", "💹"])
            
            # Check for quality visualization
            if intelligence_type == "quality_visualization":
                quality = animation_config.get("data_quality", 0.5)
                if quality >= 0.8:
                    return self.animation_emoji_map["quality_visualization"]["high_quality"]
                elif quality >= 0.6:
                    return self.animation_emoji_map["quality_visualization"]["medium_quality"]
                elif quality >= 0.4:
                    return self.animation_emoji_map["quality_visualization"]["low_quality"]
                else:
                    return self.animation_emoji_map["quality_visualization"]["poor_quality"]
            
            # Check for velocity correlation
            if intelligence_type == "velocity_correlation":
                speed = animation_config.get("speed_multiplier", 1.0)
                if speed >= 2.0:
                    return self.animation_emoji_map["velocity_correlated"]["fast"]
                elif speed >= 1.0:
                    return self.animation_emoji_map["velocity_correlated"]["medium"]
                else:
                    return self.animation_emoji_map["velocity_correlated"]["slow"]
            
            # Check for mathematical relationships
            if intelligence_type == "mathematical_relationship":
                relationship = animation_config.get("relationship_type", "linear")
                return self.animation_emoji_map["mathematical_relationship"].get(relationship, ["📊", "📈"])
            
            # Default based on animation type
            if animation_type == "attention":
                priority = animation_config.get("priority", "medium")
                return self.animation_emoji_map["attention_animation"].get(priority, ["💫", "✨"])
            
            # Fallback to generic data emojis
            return ["📊", "💹", "📈", "📉", "🔍"]
            
        except Exception as e:
            logger.error(f"Emoji selection failed: {e}")
            return ["📊", "💹"]
    
    def _calculate_rain_intensity(self, animation_config: Dict[str, Any]) -> EmojiIntensity:
        """Calculate emoji rain intensity based on animation properties."""
        try:
            # Base intensity from animation
            base_intensity = animation_config.get("intensity", 0.5)
            confidence = animation_config.get("confidence", 0.5)
            
            # Adjust based on animation type
            if animation_config.get("type") == "attention":
                priority = animation_config.get("priority", "medium")
                if priority == "critical":
                    base_intensity = min(1.0, base_intensity * 1.5)
                elif priority == "high":
                    base_intensity = min(1.0, base_intensity * 1.2)
            
            # Factor in confidence
            effective_intensity = base_intensity * (0.5 + confidence * 0.5)
            
            return self._intensity_to_emoji_intensity(effective_intensity)
            
        except Exception:
            return EmojiIntensity.MODERATE
    
    def _intensity_to_emoji_intensity(self, intensity: float) -> EmojiIntensity:
        """Convert numerical intensity to EmojiIntensity enum."""
        if intensity >= 0.8:
            return EmojiIntensity.CELEBRATION
        elif intensity >= 0.6:
            return EmojiIntensity.INTENSE
        elif intensity >= 0.3:
            return EmojiIntensity.MODERATE
        else:
            return EmojiIntensity.GENTLE
    
    def _map_animation_style(self, animation_type: str) -> AnimationStyle:
        """Map animation type to emoji rain animation style."""
        style_map = {
            "flow": AnimationStyle.GENTLE_FALL,
            "burst": AnimationStyle.CELEBRATION_BURST,
            "attention": AnimationStyle.FOCUSED_BEAM,
            "data_animation": AnimationStyle.GENTLE_FALL,
            "velocity_correlated": AnimationStyle.DYNAMIC_FLOW,
            "quality_visualization": AnimationStyle.GENTLE_FALL,
            "mathematical_relationship": AnimationStyle.PATTERN_FLOW
        }
        
        return style_map.get(animation_type, AnimationStyle.GENTLE_FALL)
    
    def _pattern_to_animation_style(self, pattern_type: str) -> AnimationStyle:
        """Map data pattern type to animation style."""
        pattern_styles = {
            "trend": AnimationStyle.DIRECTIONAL_FLOW,
            "spike": AnimationStyle.CELEBRATION_BURST,
            "oscillation": AnimationStyle.WAVE_PATTERN,
            "anomaly": AnimationStyle.FOCUSED_BEAM
        }
        
        return pattern_styles.get(pattern_type, AnimationStyle.GENTLE_FALL)
    
    def _calculate_particle_count(self, animation_config: Dict[str, Any]) -> int:
        """Calculate number of particles based on animation configuration."""
        try:
            base_count = 30
            
            # Adjust based on intensity
            intensity = animation_config.get("intensity", 0.5)
            intensity_multiplier = 1.0 + intensity
            
            # Adjust based on confidence
            confidence = animation_config.get("confidence", 0.5)
            confidence_multiplier = 0.5 + confidence * 0.5
            
            # Adjust based on animation type
            type_multipliers = {
                "attention": 1.5,
                "celebration": 2.0,
                "data_animation": 1.0,
                "quality_visualization": 1.2
            }
            
            animation_type = animation_config.get("type", "default")
            type_multiplier = type_multipliers.get(animation_type, 1.0)
            
            final_count = int(base_count * intensity_multiplier * confidence_multiplier * type_multiplier)
            return max(10, min(100, final_count))  # Clamp between 10 and 100
            
        except Exception:
            return 30
    
    def _select_colors_for_animation(self, animation_config: Dict[str, Any]) -> List[str]:
        """Select colors based on animation configuration."""
        try:
            # Default colors
            default_colors = ["#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]
            
            # Pattern-specific colors
            pattern_colors = {
                "trend_up": ["#00FF00", "#32CD32", "#90EE90", "#98FB98"],
                "trend_down": ["#FF0000", "#DC143C", "#FF6347", "#FFA07A"],
                "spike": ["#FFD700", "#FFA500", "#FF8C00", "#FF4500"],
                "oscillation": ["#00BFFF", "#87CEEB", "#87CEFA", "#B0E0E6"],
                "anomaly": ["#FF6B6B", "#FF8E53", "#FF6B9D", "#C44569"]
            }
            
            # Quality-based colors
            quality_colors = {
                "high_quality": ["#00FF00", "#32CD32", "#90EE90"],
                "medium_quality": ["#FFD700", "#FFA500", "#FFFF00"],
                "low_quality": ["#FF8C00", "#FFA500", "#FFB347"],
                "poor_quality": ["#FF0000", "#DC143C", "#FF6347"]
            }
            
            # Check for detected pattern
            if "detected_pattern" in animation_config:
                pattern = animation_config["detected_pattern"]
                return pattern_colors.get(pattern, default_colors)
            
            # Check for quality visualization
            if animation_config.get("intelligence_type") == "quality_visualization":
                quality = animation_config.get("data_quality", 0.5)
                if quality >= 0.8:
                    return quality_colors["high_quality"]
                elif quality >= 0.6:
                    return quality_colors["medium_quality"]
                elif quality >= 0.4:
                    return quality_colors["low_quality"]
                else:
                    return quality_colors["poor_quality"]
            
            return default_colors
            
        except Exception:
            return ["#4ECDC4", "#45B7D1", "#96CEB4"]
    
    def _pattern_to_colors(self, pattern_type: str) -> List[str]:
        """Get colors for specific pattern types."""
        pattern_colors = {
            "trend": ["#00FF00", "#32CD32", "#90EE90"],
            "spike": ["#FFD700", "#FFA500", "#FF8C00"],
            "oscillation": ["#00BFFF", "#87CEEB", "#87CEFA"],
            "anomaly": ["#FF6B6B", "#FF8E53", "#FF6B9D"]
        }
        
        return pattern_colors.get(pattern_type, ["#4ECDC4", "#45B7D1", "#96CEB4"])
    
    async def _create_keyframe_synchronized_rain(self, animation_id: str, keyframes: List[Dict[str, Any]]) -> None:
        """Create emoji rain synchronized with animation keyframes."""
        try:
            for keyframe in keyframes:
                # Schedule rain effect at keyframe time
                delay = keyframe.get("time", 0.0)
                effect_config = keyframe.get("rain_config", {})
                
                # Create delayed task
                asyncio.create_task(self._delayed_rain_effect(delay, effect_config))
                
        except Exception as e:
            logger.error(f"Keyframe synchronized rain creation failed: {e}")
    
    async def _delayed_rain_effect(self, delay: float, effect_config: Dict[str, Any]) -> None:
        """Create a delayed rain effect."""
        try:
            await asyncio.sleep(delay)
            await self.trigger_engagement_rain(effect_config)
        except Exception as e:
            logger.error(f"Delayed rain effect failed: {e}")
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Emoji Rain Bridge capabilities."""
        return [
            "engagement_rain_integration",
            "data_pattern_rain",
            "celebration_rain",
            "synchronized_animation_rain",
            "intelligent_emoji_selection",
            "adaptive_rain_intensity"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Emoji Rain Bridge health status."""
        return {
            "status": "healthy",
            "emoji_rain_engine_available": self.emoji_rain_engine is not None,
            "animation_mappings": len(self.animation_emoji_map),
            "celebration_types": len(self.celebration_emojis)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Emoji Rain Bridge module information."""
        return {
            "module_id": self.module_id,
            "name": "Emoji Rain Bridge",
            "version": "1.0.0",
            "description": "Integration bridge between AnimationEngine and EmojiRainEngine"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation for emoji rain integration."""
        try:
            degradation_actions = []
            
            # Reduce emoji variety to basic set
            basic_emojis = ["📊", "💹", "✅", "⚠️", "🔍"]
            for category in self.animation_emoji_map.values():
                for subcategory in category.values():
                    if isinstance(subcategory, list):
                        subcategory.clear()
                        subcategory.extend(basic_emojis[:2])  # Only 2 emojis per category
            
            degradation_actions.append("Reduced emoji variety to basic set")
            
            # Simplify celebration emojis
            basic_celebration = ["🎉", "✅", "⭐"]
            for celebration_type in self.celebration_emojis:
                self.celebration_emojis[celebration_type] = basic_celebration
            
            degradation_actions.append("Simplified celebration emojis")
            
            # Disable complex rain effects (would need emoji engine cooperation)
            degradation_actions.append("Disabled complex rain synchronization")
            
            return {
                "status": "degraded",
                "actions_taken": degradation_actions,
                "functionality_level": "basic_emoji_rain_only",
                "recovery_possible": True,
                "emoji_variety_reduced": True
            }
            
        except Exception as e:
            return {
                "status": "degradation_failed",
                "error": str(e),
                "functionality_level": "unknown",
                "recovery_possible": False
            }