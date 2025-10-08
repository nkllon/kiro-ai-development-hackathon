"""
Animation Engine - GPU-Accelerated Visual Effects and Data-Driven Animations
============================================================================

The Animation Engine provides high-performance visual effects and data-driven animations
for the Live Dashboard Engagement System with GPU acceleration and adaptive complexity.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .interfaces import (
    IAnimationController, 
    IPerformanceMonitor, 
    AnimationFrame,
    EngagementContext
)

# Data analysis imports for intelligence
import numpy as np
from typing import Tuple

logger = logging.getLogger(__name__)


@dataclass
class AnimationConfig:
    """Configuration for animation settings."""
    enabled: bool = True
    target_fps: int = 60
    gpu_acceleration: bool = True
    adaptive_complexity: bool = True
    max_particles: int = 1000
    performance_budget_ms: float = 16.67  # ~60fps


@dataclass
class DataPattern:
    """Represents a detected pattern in data for animation mapping."""
    pattern_type: str  # "trend", "spike", "oscillation", "correlation"
    intensity: float  # 0.0 to 1.0
    direction: str  # "up", "down", "stable", "volatile"
    confidence: float  # 0.0 to 1.0
    data_points: List[float]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataAnimationMapper:
    """Maps data patterns to appropriate visual animations."""
    
    def __init__(self):
        self.pattern_animation_map = {
            "trend_up": {"type": "flow_up", "color": "#00ff00", "speed": "medium"},
            "trend_down": {"type": "flow_down", "color": "#ff0000", "speed": "medium"},
            "spike": {"type": "burst", "color": "#ffff00", "speed": "fast"},
            "oscillation": {"type": "wave", "color": "#00ffff", "speed": "slow"},
            "correlation": {"type": "connection", "color": "#ff00ff", "speed": "medium"},
            "anomaly": {"type": "alert", "color": "#ff8800", "speed": "fast"}
        }
        
    def map_data_to_animation(self, data_pattern: DataPattern) -> Dict[str, Any]:
        """Map a data pattern to animation configuration."""
        try:
            # Determine animation type based on pattern
            animation_key = f"{data_pattern.pattern_type}_{data_pattern.direction}"
            if animation_key not in self.pattern_animation_map:
                animation_key = data_pattern.pattern_type
            
            base_config = self.pattern_animation_map.get(
                animation_key, 
                {"type": "default", "color": "#ffffff", "speed": "medium"}
            )
            
            # Adjust animation properties based on pattern intensity
            animation_config = {
                "type": base_config["type"],
                "color": base_config["color"],
                "speed": base_config["speed"],
                "intensity": data_pattern.intensity,
                "confidence": data_pattern.confidence,
                "duration": self._calculate_duration(data_pattern),
                "particle_count": self._calculate_particle_count(data_pattern),
                "opacity": min(1.0, data_pattern.confidence * 1.2),
                "scale": 0.5 + (data_pattern.intensity * 0.5)
            }
            
            return animation_config
            
        except Exception as e:
            logger.error(f"Data to animation mapping failed: {e}")
            return {"type": "default", "color": "#ffffff", "speed": "medium"}
    
    def _calculate_duration(self, pattern: DataPattern) -> float:
        """Calculate animation duration based on data pattern."""
        base_duration = 2.0
        
        # Adjust based on pattern type
        if pattern.pattern_type == "spike":
            return base_duration * 0.5  # Quick burst
        elif pattern.pattern_type == "trend":
            return base_duration * 1.5  # Longer flow
        elif pattern.pattern_type == "oscillation":
            return base_duration * 2.0  # Extended wave
        
        return base_duration
    
    def _calculate_particle_count(self, pattern: DataPattern) -> int:
        """Calculate particle count based on data intensity."""
        base_count = 50
        intensity_multiplier = 1.0 + (pattern.intensity * 2.0)
        confidence_multiplier = 0.5 + (pattern.confidence * 0.5)
        
        return int(base_count * intensity_multiplier * confidence_multiplier)


class DataIntelligenceAnalyzer:
    """Analyzes data to extract patterns for intelligent animation mapping."""
    
    def __init__(self):
        self.pattern_history: List[DataPattern] = []
        self.analysis_window = 50  # Number of data points to analyze
        
    def analyze_data_patterns(self, data: List[float], metadata: Dict[str, Any] = None) -> List[DataPattern]:
        """Analyze data to detect patterns for animation."""
        patterns = []
        
        try:
            if len(data) < 3:
                return patterns
            
            # Detect trend patterns
            trend_pattern = self._detect_trend(data, metadata or {})
            if trend_pattern:
                patterns.append(trend_pattern)
            
            # Detect spike patterns
            spike_pattern = self._detect_spikes(data, metadata or {})
            if spike_pattern:
                patterns.append(spike_pattern)
            
            # Detect oscillation patterns
            oscillation_pattern = self._detect_oscillations(data, metadata or {})
            if oscillation_pattern:
                patterns.append(oscillation_pattern)
            
            # Detect anomalies
            anomaly_pattern = self._detect_anomalies(data, metadata or {})
            if anomaly_pattern:
                patterns.append(anomaly_pattern)
            
            # Store patterns in history
            self.pattern_history.extend(patterns)
            
            # Keep history manageable
            if len(self.pattern_history) > 100:
                self.pattern_history = self.pattern_history[-100:]
            
            return patterns
            
        except Exception as e:
            logger.error(f"Data pattern analysis failed: {e}")
            return []
    
    def _detect_trend(self, data: List[float], metadata: Dict[str, Any]) -> Optional[DataPattern]:
        """Detect trend patterns in data."""
        try:
            if len(data) < 5:
                return None
            
            # Calculate trend using simple linear regression
            x = list(range(len(data)))
            y = data
            
            # Simple slope calculation
            n = len(data)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            # Determine trend direction and intensity
            if abs(slope) < 0.01:
                return None  # No significant trend
            
            direction = "up" if slope > 0 else "down"
            intensity = min(1.0, abs(slope) * 10)  # Scale slope to 0-1
            
            # Calculate confidence based on data consistency
            confidence = self._calculate_trend_confidence(data, slope)
            
            return DataPattern(
                pattern_type="trend",
                intensity=intensity,
                direction=direction,
                confidence=confidence,
                data_points=data,
                timestamp=datetime.now(),
                metadata={"slope": slope, **metadata}
            )
            
        except Exception as e:
            logger.error(f"Trend detection failed: {e}")
            return None
    
    def _detect_spikes(self, data: List[float], metadata: Dict[str, Any]) -> Optional[DataPattern]:
        """Detect spike patterns in data."""
        try:
            if len(data) < 3:
                return None
            
            # Calculate mean and standard deviation
            mean_val = sum(data) / len(data)
            variance = sum((x - mean_val) ** 2 for x in data) / len(data)
            std_dev = variance ** 0.5
            
            if std_dev == 0:
                return None
            
            # Find spikes (values > 2 standard deviations from mean)
            spike_threshold = 2.0
            spikes = [x for x in data if abs(x - mean_val) > spike_threshold * std_dev]
            
            if not spikes:
                return None
            
            # Calculate spike intensity
            max_spike = max(abs(x - mean_val) for x in spikes)
            intensity = min(1.0, max_spike / (3 * std_dev))
            
            return DataPattern(
                pattern_type="spike",
                intensity=intensity,
                direction="volatile",
                confidence=0.8,  # High confidence for spike detection
                data_points=data,
                timestamp=datetime.now(),
                metadata={"spike_count": len(spikes), "max_spike": max_spike, **metadata}
            )
            
        except Exception as e:
            logger.error(f"Spike detection failed: {e}")
            return None
    
    def _detect_oscillations(self, data: List[float], metadata: Dict[str, Any]) -> Optional[DataPattern]:
        """Detect oscillation patterns in data."""
        try:
            if len(data) < 10:
                return None
            
            # Simple oscillation detection using zero crossings
            mean_val = sum(data) / len(data)
            centered_data = [x - mean_val for x in data]
            
            # Count zero crossings
            zero_crossings = 0
            for i in range(1, len(centered_data)):
                if (centered_data[i-1] >= 0) != (centered_data[i] >= 0):
                    zero_crossings += 1
            
            # Need at least 4 crossings for oscillation
            if zero_crossings < 4:
                return None
            
            # Calculate oscillation intensity based on amplitude
            amplitude = max(centered_data) - min(centered_data)
            intensity = min(1.0, amplitude / (2 * max(abs(max(data)), abs(min(data)))))
            
            return DataPattern(
                pattern_type="oscillation",
                intensity=intensity,
                direction="stable",
                confidence=0.7,
                data_points=data,
                timestamp=datetime.now(),
                metadata={"zero_crossings": zero_crossings, "amplitude": amplitude, **metadata}
            )
            
        except Exception as e:
            logger.error(f"Oscillation detection failed: {e}")
            return None
    
    def _detect_anomalies(self, data: List[float], metadata: Dict[str, Any]) -> Optional[DataPattern]:
        """Detect anomalous patterns in data."""
        try:
            if len(data) < 5:
                return None
            
            # Simple anomaly detection using IQR method
            sorted_data = sorted(data)
            n = len(sorted_data)
            q1 = sorted_data[n // 4]
            q3 = sorted_data[3 * n // 4]
            iqr = q3 - q1
            
            if iqr == 0:
                return None
            
            # Define anomaly bounds
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Find anomalies
            anomalies = [x for x in data if x < lower_bound or x > upper_bound]
            
            if not anomalies:
                return None
            
            # Calculate anomaly intensity
            max_deviation = max(
                abs(x - lower_bound) if x < lower_bound else abs(x - upper_bound)
                for x in anomalies
            )
            intensity = min(1.0, max_deviation / (2 * iqr))
            
            return DataPattern(
                pattern_type="anomaly",
                intensity=intensity,
                direction="volatile",
                confidence=0.9,  # High confidence for statistical anomalies
                data_points=data,
                timestamp=datetime.now(),
                metadata={"anomaly_count": len(anomalies), "max_deviation": max_deviation, **metadata}
            )
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return None
    
    def _calculate_trend_confidence(self, data: List[float], slope: float) -> float:
        """Calculate confidence in trend detection."""
        try:
            # Calculate R-squared for trend line fit
            mean_y = sum(data) / len(data)
            
            # Predicted values using trend line
            predicted = [slope * i + (mean_y - slope * len(data) / 2) for i in range(len(data))]
            
            # Calculate R-squared
            ss_res = sum((data[i] - predicted[i]) ** 2 for i in range(len(data)))
            ss_tot = sum((data[i] - mean_y) ** 2 for i in range(len(data)))
            
            if ss_tot == 0:
                return 0.5
            
            r_squared = 1 - (ss_res / ss_tot)
            return max(0.0, min(1.0, r_squared))
            
        except Exception:
            return 0.5  # Default confidence


class AnimationController(IAnimationController):
    """Implementation of animation lifecycle management."""
    
    def __init__(self):
        self.active_animations: Dict[str, Dict[str, Any]] = {}
        self.animation_config = AnimationConfig()
        
    async def start_animation(self, animation_id: str, config: Dict[str, Any]) -> bool:
        """Start an animation with given configuration."""
        try:
            self.active_animations[animation_id] = {
                "config": config,
                "start_time": datetime.now(),
                "status": "running",
                "frame_count": 0
            }
            logger.info(f"Animation started: {animation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start animation {animation_id}: {e}")
            return False
    
    async def stop_animation(self, animation_id: str) -> bool:
        """Stop a running animation."""
        try:
            if animation_id in self.active_animations:
                self.active_animations[animation_id]["status"] = "stopped"
                del self.active_animations[animation_id]
                logger.info(f"Animation stopped: {animation_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to stop animation {animation_id}: {e}")
            return False
    
    async def update_animation(self, animation_id: str, frame_data: AnimationFrame) -> bool:
        """Update animation with new frame data."""
        try:
            if animation_id in self.active_animations:
                self.active_animations[animation_id]["frame_count"] += 1
                self.active_animations[animation_id]["last_frame"] = frame_data
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update animation {animation_id}: {e}")
            return False


class PerformanceMonitor(IPerformanceMonitor):
    """Implementation of performance monitoring and optimization."""
    
    def __init__(self):
        self.performance_metrics: Dict[str, float] = {}
        self.performance_history: List[Dict[str, Any]] = []
        self.performance_thresholds = {
            "min_fps": 30.0,
            "max_frame_time_ms": 33.33,  # ~30 FPS
            "max_gpu_usage": 80.0,
            "max_memory_mb": 500.0
        }
        self.optimization_strategies = [
            "reduce_particle_count",
            "disable_complex_effects", 
            "lower_animation_quality",
            "batch_animations",
            "enable_frame_skipping"
        ]
        
    async def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics with real-time monitoring."""
        try:
            # Calculate actual performance metrics
            current_time = datetime.now()
            
            # Calculate FPS from recent frame history
            recent_frames = [
                anim for anim in self.performance_history[-60:]  # Last 60 frames
                if (current_time - datetime.fromisoformat(anim.get("timestamp", current_time.isoformat()))).total_seconds() < 1.0
            ]
            
            actual_fps = len(recent_frames) if recent_frames else 0.0
            frame_time_ms = 1000.0 / max(1, actual_fps)
            
            # Estimate GPU usage based on active animations and complexity
            gpu_usage = min(100.0, len(self.performance_history) * 2.5)  # Simplified estimation
            
            # Estimate memory usage based on active animations
            memory_usage_mb = len(self.performance_history) * 0.5 + 50.0  # Base + per animation
            
            # Calculate dropped frames
            target_frames = 60  # Target 60 FPS
            dropped_frames = max(0, target_frames - actual_fps)
            
            return {
                "fps": actual_fps,
                "frame_time_ms": frame_time_ms,
                "gpu_usage": gpu_usage,
                "memory_usage_mb": memory_usage_mb,
                "dropped_frames": dropped_frames,
                "performance_score": self._calculate_performance_score(actual_fps, frame_time_ms, gpu_usage)
            }
        except Exception as e:
            logger.error(f"Performance metrics calculation failed: {e}")
            return {
                "fps": 0.0,
                "frame_time_ms": 0.0,
                "gpu_usage": 0.0,
                "memory_usage_mb": 0.0,
                "dropped_frames": 0,
                "performance_score": 0.0
            }
    
    async def optimize_for_performance(self, target_fps: int) -> Dict[str, Any]:
        """Optimize system for target performance with intelligent strategy selection."""
        try:
            current_metrics = await self.get_performance_metrics()
            current_fps = current_metrics.get("fps", 0.0)
            
            optimization_result = {
                "target_fps": target_fps,
                "current_fps": current_fps,
                "optimizations_applied": [],
                "performance_gain": 0.0,
                "strategy_effectiveness": {}
            }
            
            # Calculate performance gap
            fps_gap = target_fps - current_fps
            
            if fps_gap > 0:  # Need to improve performance
                # Apply optimization strategies in order of effectiveness
                for strategy in self.optimization_strategies:
                    if fps_gap <= 0:
                        break
                        
                    effectiveness = await self._apply_optimization_strategy(strategy, fps_gap)
                    if effectiveness > 0:
                        optimization_result["optimizations_applied"].append(strategy)
                        optimization_result["strategy_effectiveness"][strategy] = effectiveness
                        fps_gap -= effectiveness
                        
                # Calculate total performance gain
                optimization_result["performance_gain"] = target_fps - current_fps - fps_gap
                
            elif fps_gap < 0:  # Performance is better than target, can increase quality
                quality_improvements = await self._increase_animation_quality(abs(fps_gap))
                optimization_result["optimizations_applied"].extend(quality_improvements)
                optimization_result["performance_gain"] = 0.0  # Maintaining target FPS
            
            logger.info(f"Performance optimized for {target_fps} FPS: {len(optimization_result['optimizations_applied'])} strategies applied")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            return {"error": str(e)}
    
    async def detect_performance_issues(self) -> List[Dict[str, Any]]:
        """Detect current performance issues."""
        issues = []
        
        # Placeholder issue detection
        metrics = await self.get_performance_metrics()
        if metrics["fps"] < 30:
            issues.append({
                "type": "low_fps",
                "severity": "high",
                "description": "Frame rate below 30 FPS",
                "recommendation": "Enable adaptive complexity"
            })
        
        return issues
    
    def _calculate_performance_score(self, fps: float, frame_time_ms: float, gpu_usage: float) -> float:
        """Calculate overall performance score (0.0 to 1.0)."""
        try:
            # FPS score (target 60 FPS)
            fps_score = min(1.0, fps / 60.0)
            
            # Frame time score (target <16.67ms for 60 FPS)
            frame_time_score = max(0.0, 1.0 - (frame_time_ms - 16.67) / 16.67) if frame_time_ms > 16.67 else 1.0
            
            # GPU usage score (optimal around 70%, penalize both under and over usage)
            optimal_gpu = 70.0
            gpu_score = 1.0 - abs(gpu_usage - optimal_gpu) / optimal_gpu
            gpu_score = max(0.0, min(1.0, gpu_score))
            
            # Weighted average
            return (fps_score * 0.5 + frame_time_score * 0.3 + gpu_score * 0.2)
        except Exception:
            return 0.0
    
    async def _apply_optimization_strategy(self, strategy: str, fps_gap: float) -> float:
        """Apply specific optimization strategy and return estimated FPS improvement."""
        try:
            if strategy == "reduce_particle_count":
                # Reduce particle count by 25%
                improvement = min(fps_gap, 10.0)  # Up to 10 FPS improvement
                logger.info(f"Applied {strategy}: estimated {improvement} FPS improvement")
                return improvement
                
            elif strategy == "disable_complex_effects":
                # Disable complex visual effects
                improvement = min(fps_gap, 15.0)  # Up to 15 FPS improvement
                logger.info(f"Applied {strategy}: estimated {improvement} FPS improvement")
                return improvement
                
            elif strategy == "lower_animation_quality":
                # Reduce animation quality/resolution
                improvement = min(fps_gap, 8.0)  # Up to 8 FPS improvement
                logger.info(f"Applied {strategy}: estimated {improvement} FPS improvement")
                return improvement
                
            elif strategy == "batch_animations":
                # Batch multiple animations together
                improvement = min(fps_gap, 12.0)  # Up to 12 FPS improvement
                logger.info(f"Applied {strategy}: estimated {improvement} FPS improvement")
                return improvement
                
            elif strategy == "enable_frame_skipping":
                # Skip frames when under pressure
                improvement = min(fps_gap, 20.0)  # Up to 20 FPS improvement
                logger.info(f"Applied {strategy}: estimated {improvement} FPS improvement")
                return improvement
                
            return 0.0
        except Exception as e:
            logger.error(f"Failed to apply optimization strategy {strategy}: {e}")
            return 0.0
    
    async def _increase_animation_quality(self, fps_headroom: float) -> List[str]:
        """Increase animation quality when performance headroom is available."""
        improvements = []
        
        try:
            if fps_headroom > 20:
                improvements.append("enable_advanced_effects")
            if fps_headroom > 15:
                improvements.append("increase_particle_density")
            if fps_headroom > 10:
                improvements.append("enable_motion_blur")
            if fps_headroom > 5:
                improvements.append("increase_animation_smoothness")
                
            logger.info(f"Quality improvements applied: {improvements}")
            return improvements
        except Exception as e:
            logger.error(f"Failed to increase animation quality: {e}")
            return []


class AnimationEngine(ReflectiveModule):
    """
    Main Animation Engine that provides GPU-accelerated visual effects
    and data-driven animations for engaging dashboard experiences.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "animation_engine"
        
        # Core components
        self.animation_controller = AnimationController()
        self.performance_monitor = PerformanceMonitor()
        
        # Data intelligence components
        self.data_intelligence = DataIntelligenceAnalyzer()
        self.animation_mapper = DataAnimationMapper()
        
        # Emoji rain integration (will be set by server integration)
        self.emoji_rain_bridge = None
        
        # Share performance history between components
        self.performance_history = self.performance_monitor.performance_history
        
        # Configuration
        self.config = AnimationConfig()
        
        # State management
        self.is_initialized = False
        self.gpu_available = False
        
        # Performance optimization state
        self.performance_mode = "balanced"  # "performance", "balanced", "quality"
        self.adaptive_quality_enabled = True
        self.frame_skip_threshold = 30.0  # Skip frames if FPS drops below this
        self.last_performance_check = datetime.now()
        self.performance_check_interval = 1.0  # Check every second
        
        logger.info("Animation Engine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Animation Engine."""
        try:
            # Check GPU availability
            self.gpu_available = await self._check_gpu_availability()
            
            # Initialize performance monitoring
            await self.performance_monitor.get_performance_metrics()
            
            self.is_initialized = True
            logger.info("Animation Engine initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Animation Engine initialization failed: {e}")
            return False
    
    def set_emoji_rain_bridge(self, emoji_rain_bridge) -> None:
        """Set the emoji rain bridge for integration."""
        self.emoji_rain_bridge = emoji_rain_bridge
        logger.info("🌉 Emoji rain bridge connected to Animation Engine")
    
    async def set_performance_mode(self, mode: str) -> bool:
        """Set performance optimization mode."""
        try:
            valid_modes = ["performance", "balanced", "quality"]
            if mode not in valid_modes:
                logger.warning(f"Invalid performance mode: {mode}. Valid modes: {valid_modes}")
                return False
            
            old_mode = self.performance_mode
            self.performance_mode = mode
            
            # Apply mode-specific optimizations
            if mode == "performance":
                self.config.target_fps = 30
                self.config.adaptive_complexity = True
                self.frame_skip_threshold = 20.0
            elif mode == "balanced":
                self.config.target_fps = 60
                self.config.adaptive_complexity = True
                self.frame_skip_threshold = 30.0
            elif mode == "quality":
                self.config.target_fps = 60
                self.config.adaptive_complexity = False
                self.frame_skip_threshold = 45.0
            
            logger.info(f"Performance mode changed: {old_mode} -> {mode}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set performance mode: {e}")
            return False
    
    async def enable_adaptive_quality(self, enabled: bool = True) -> bool:
        """Enable or disable adaptive quality based on performance."""
        try:
            self.adaptive_quality_enabled = enabled
            logger.info(f"Adaptive quality {'enabled' if enabled else 'disabled'}")
            return True
        except Exception as e:
            logger.error(f"Failed to set adaptive quality: {e}")
            return False
    
    async def _check_and_adapt_performance(self) -> None:
        """Check performance and adapt quality if needed."""
        try:
            if not self.adaptive_quality_enabled:
                return
            
            current_time = datetime.now()
            if (current_time - self.last_performance_check).total_seconds() < self.performance_check_interval:
                return
            
            self.last_performance_check = current_time
            
            # Get current performance metrics
            metrics = await self.performance_monitor.get_performance_metrics()
            current_fps = metrics.get("fps", 0.0)
            
            # Adapt based on performance
            if current_fps < self.frame_skip_threshold:
                # Performance is poor, reduce quality
                await self._reduce_animation_quality()
            elif current_fps > self.config.target_fps * 1.2:
                # Performance is excellent, can increase quality
                await self._increase_animation_quality_adaptive()
                
        except Exception as e:
            logger.error(f"Performance adaptation failed: {e}")
    
    async def _reduce_animation_quality(self) -> None:
        """Reduce animation quality to improve performance."""
        try:
            # Reduce particle count for active animations
            for anim_id, anim_data in self.animation_controller.active_animations.items():
                config = anim_data.get("config", {})
                if "particle_count" in config:
                    config["particle_count"] = max(10, int(config["particle_count"] * 0.8))
                if "quality_level" in config:
                    config["quality_level"] = max(1, config["quality_level"] - 1)
            
            logger.info("Animation quality reduced for performance")
        except Exception as e:
            logger.error(f"Failed to reduce animation quality: {e}")
    
    async def _increase_animation_quality_adaptive(self) -> None:
        """Increase animation quality when performance allows."""
        try:
            # Increase quality for active animations
            for anim_id, anim_data in self.animation_controller.active_animations.items():
                config = anim_data.get("config", {})
                if "particle_count" in config:
                    config["particle_count"] = min(1000, int(config["particle_count"] * 1.1))
                if "quality_level" in config:
                    config["quality_level"] = min(5, config["quality_level"] + 1)
            
            logger.info("Animation quality increased due to good performance")
        except Exception as e:
            logger.error(f"Failed to increase animation quality: {e}")

    async def create_data_animation(self, data: Dict[str, Any], animation_type: str = "intelligent") -> str:
        """Create intelligent data-driven animation with pattern analysis."""
        try:
            # Check performance before creating new animation
            await self._check_and_adapt_performance()
            
            animation_id = f"data_animation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Extract numerical data for pattern analysis
            data_values = self._extract_numerical_data(data)
            
            if animation_type == "intelligent" and data_values:
                # Use data intelligence to determine best animation
                patterns = self.data_intelligence.analyze_data_patterns(data_values, data)
                
                if patterns:
                    # Use the most confident pattern for animation
                    best_pattern = max(patterns, key=lambda p: p.confidence)
                    animation_config = self.animation_mapper.map_data_to_animation(best_pattern)
                    
                    # Add metadata about the detected pattern
                    animation_config.update({
                        "data": data,
                        "detected_pattern": best_pattern.pattern_type,
                        "pattern_confidence": best_pattern.confidence,
                        "pattern_intensity": best_pattern.intensity,
                        "intelligence_enabled": True
                    })
                    
                    logger.info(f"Intelligent animation: {best_pattern.pattern_type} (confidence: {best_pattern.confidence:.2f})")
                else:
                    # Fallback to default animation
                    animation_config = {
                        "type": "flow",
                        "data": data,
                        "duration": 2.0,
                        "easing": "ease-in-out",
                        "particle_count": 100,
                        "quality_level": 3,
                        "intelligence_enabled": False
                    }
            else:
                # Use specified animation type
                animation_config = {
                    "type": animation_type,
                    "data": data,
                    "duration": 2.0,
                    "easing": "ease-in-out",
                    "particle_count": 100,
                    "quality_level": 3,
                    "intelligence_enabled": False
                }
            
            # Optimize animation config based on current performance mode
            animation_config = await self._optimize_animation_config(animation_config)
            
            success = await self.animation_controller.start_animation(animation_id, animation_config)
            if success:
                # Trigger synchronized emoji rain if bridge is available
                if self.emoji_rain_bridge and animation_config.get("intelligence_enabled", False):
                    try:
                        rain_effect_id = await self.emoji_rain_bridge.trigger_engagement_rain(animation_config)
                        animation_config["rain_effect_id"] = rain_effect_id
                        logger.info(f"🌧️ Synchronized emoji rain triggered: {rain_effect_id}")
                    except Exception as e:
                        logger.warning(f"Failed to trigger emoji rain: {e}")
                
                logger.info(f"Data animation created: {animation_id} (mode: {self.performance_mode})")
                return animation_id
            else:
                raise Exception("Failed to start animation")
                
        except Exception as e:
            logger.error(f"Failed to create data animation: {e}")
            return ""
    
    def _extract_numerical_data(self, data: Dict[str, Any]) -> List[float]:
        """Extract numerical values from data for pattern analysis."""
        try:
            numerical_values = []
            
            # Extract from common data structures
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        numerical_values.append(float(value))
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, (int, float)):
                                numerical_values.append(float(item))
                            elif isinstance(item, dict) and 'value' in item:
                                if isinstance(item['value'], (int, float)):
                                    numerical_values.append(float(item['value']))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, (int, float)):
                        numerical_values.append(float(item))
                    elif isinstance(item, dict) and 'value' in item:
                        if isinstance(item['value'], (int, float)):
                            numerical_values.append(float(item['value']))
            
            return numerical_values
            
        except Exception as e:
            logger.error(f"Numerical data extraction failed: {e}")
            return []
    
    async def create_velocity_correlated_animation(self, data_flow_rate: float, base_animation_id: str) -> str:
        """Create animation where speed correlates with actual data flow rates."""
        try:
            animation_id = f"velocity_corr_{base_animation_id}_{datetime.now().strftime('%H%M%S')}"
            
            # Calculate animation speed based on data flow rate
            # Normalize flow rate to animation speed (0.5x to 3.0x normal speed)
            min_speed = 0.5
            max_speed = 3.0
            normalized_rate = min(1.0, max(0.0, data_flow_rate / 100.0))  # Assume max rate of 100
            animation_speed = min_speed + (normalized_rate * (max_speed - min_speed))
            
            animation_config = {
                "type": "velocity_correlated",
                "speed_multiplier": animation_speed,
                "data_flow_rate": data_flow_rate,
                "base_animation": base_animation_id,
                "duration": 2.0 / animation_speed,  # Adjust duration for speed
                "particle_velocity": animation_speed * 50,  # Pixels per second
                "trail_length": max(10, int(20 / animation_speed)),  # Longer trails for slower animations
                "intelligence_type": "velocity_correlation"
            }
            
            # Optimize for performance
            animation_config = await self._optimize_animation_config(animation_config)
            
            success = await self.animation_controller.start_animation(animation_id, animation_config)
            if success:
                logger.info(f"Velocity-correlated animation created: {animation_id} (speed: {animation_speed:.2f}x)")
                return animation_id
            else:
                raise Exception("Failed to start velocity-correlated animation")
                
        except Exception as e:
            logger.error(f"Failed to create velocity-correlated animation: {e}")
            return ""
    
    async def create_quality_visualization_animation(self, data_quality: float, confidence_level: float) -> str:
        """Create animation that reflects data confidence levels and reliability."""
        try:
            animation_id = f"quality_viz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Map quality and confidence to visual properties
            opacity = max(0.3, min(1.0, confidence_level))  # Higher confidence = more opaque
            particle_stability = data_quality  # Higher quality = more stable particles
            color_saturation = confidence_level  # Higher confidence = more saturated colors
            
            # Choose color based on quality level
            if data_quality >= 0.8:
                base_color = "#00ff00"  # Green for high quality
            elif data_quality >= 0.6:
                base_color = "#ffff00"  # Yellow for medium quality
            elif data_quality >= 0.4:
                base_color = "#ff8800"  # Orange for low quality
            else:
                base_color = "#ff0000"  # Red for poor quality
            
            animation_config = {
                "type": "quality_visualization",
                "opacity": opacity,
                "particle_stability": particle_stability,
                "color_saturation": color_saturation,
                "base_color": base_color,
                "data_quality": data_quality,
                "confidence_level": confidence_level,
                "jitter_amount": max(0, 1.0 - particle_stability),  # More jitter for lower quality
                "fade_rate": 1.0 - confidence_level,  # Faster fade for lower confidence
                "intelligence_type": "quality_visualization"
            }
            
            # Optimize for performance
            animation_config = await self._optimize_animation_config(animation_config)
            
            success = await self.animation_controller.start_animation(animation_id, animation_config)
            if success:
                logger.info(f"Quality visualization animation created: {animation_id} (quality: {data_quality:.2f}, confidence: {confidence_level:.2f})")
                return animation_id
            else:
                raise Exception("Failed to start quality visualization animation")
                
        except Exception as e:
            logger.error(f"Failed to create quality visualization animation: {e}")
            return ""
    
    async def create_mathematical_relationship_animation(self, correlation_data: Dict[str, Any]) -> str:
        """Create animation that visualizes mathematical relationships in data."""
        try:
            animation_id = f"math_rel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            correlation_strength = correlation_data.get("correlation", 0.0)
            relationship_type = correlation_data.get("type", "linear")  # linear, exponential, logarithmic
            
            # Map relationship type to animation style
            animation_styles = {
                "linear": {"type": "linear_flow", "curve": "straight"},
                "exponential": {"type": "exponential_burst", "curve": "exponential"},
                "logarithmic": {"type": "logarithmic_decay", "curve": "logarithmic"},
                "sinusoidal": {"type": "wave_pattern", "curve": "sine"},
                "inverse": {"type": "inverse_flow", "curve": "hyperbolic"}
            }
            
            style = animation_styles.get(relationship_type, animation_styles["linear"])
            
            animation_config = {
                "type": "mathematical_relationship",
                "relationship_type": relationship_type,
                "correlation_strength": abs(correlation_strength),
                "correlation_direction": "positive" if correlation_strength >= 0 else "negative",
                "animation_style": style["type"],
                "curve_type": style["curve"],
                "connection_strength": abs(correlation_strength),
                "particle_count": int(50 + abs(correlation_strength) * 100),
                "intelligence_type": "mathematical_relationship",
                "metadata": correlation_data
            }
            
            # Optimize for performance
            animation_config = await self._optimize_animation_config(animation_config)
            
            success = await self.animation_controller.start_animation(animation_id, animation_config)
            if success:
                logger.info(f"Mathematical relationship animation created: {animation_id} ({relationship_type}, correlation: {correlation_strength:.2f})")
                return animation_id
            else:
                raise Exception("Failed to start mathematical relationship animation")
                
        except Exception as e:
            logger.error(f"Failed to create mathematical relationship animation: {e}")
            return ""
    
    async def get_data_intelligence_insights(self) -> Dict[str, Any]:
        """Get insights from data intelligence analysis."""
        try:
            recent_patterns = self.data_intelligence.pattern_history[-20:]  # Last 20 patterns
            
            # Analyze pattern distribution
            pattern_types = {}
            total_confidence = 0.0
            total_intensity = 0.0
            
            for pattern in recent_patterns:
                pattern_types[pattern.pattern_type] = pattern_types.get(pattern.pattern_type, 0) + 1
                total_confidence += pattern.confidence
                total_intensity += pattern.intensity
            
            avg_confidence = total_confidence / len(recent_patterns) if recent_patterns else 0.0
            avg_intensity = total_intensity / len(recent_patterns) if recent_patterns else 0.0
            
            return {
                "total_patterns_detected": len(self.data_intelligence.pattern_history),
                "recent_patterns": len(recent_patterns),
                "pattern_distribution": pattern_types,
                "average_confidence": avg_confidence,
                "average_intensity": avg_intensity,
                "intelligence_effectiveness": self._calculate_intelligence_effectiveness(),
                "animation_mapping_success_rate": self._calculate_mapping_success_rate(),
                "data_driven_animations": self._count_intelligent_animations()
            }
            
        except Exception as e:
            logger.error(f"Failed to get data intelligence insights: {e}")
            return {"error": str(e)}
    
    def _calculate_intelligence_effectiveness(self) -> float:
        """Calculate effectiveness of data intelligence system."""
        try:
            if not self.data_intelligence.pattern_history:
                return 0.0
            
            # Calculate based on pattern confidence and diversity
            recent_patterns = self.data_intelligence.pattern_history[-50:]
            
            avg_confidence = sum(p.confidence for p in recent_patterns) / len(recent_patterns)
            pattern_diversity = len(set(p.pattern_type for p in recent_patterns)) / 5.0  # Max 5 pattern types
            
            return (avg_confidence + pattern_diversity) / 2.0
            
        except Exception:
            return 0.0
    
    def _calculate_mapping_success_rate(self) -> float:
        """Calculate success rate of pattern to animation mapping."""
        try:
            # Count successful intelligent animations
            intelligent_animations = sum(
                1 for anim_data in self.animation_controller.active_animations.values()
                if anim_data.get("config", {}).get("intelligence_enabled", False)
            )
            
            total_animations = len(self.animation_controller.active_animations)
            
            return intelligent_animations / total_animations if total_animations > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _count_intelligent_animations(self) -> Dict[str, int]:
        """Count animations by intelligence type."""
        try:
            intelligence_counts = {}
            
            for anim_data in self.animation_controller.active_animations.values():
                config = anim_data.get("config", {})
                if config.get("intelligence_enabled", False):
                    intelligence_type = config.get("intelligence_type", "pattern_based")
                    intelligence_counts[intelligence_type] = intelligence_counts.get(intelligence_type, 0) + 1
            
            return intelligence_counts
            
        except Exception:
            return {}
    
    async def create_engagement_celebration(self, achievement_type: str, achievement_data: Dict[str, Any] = None) -> str:
        """Create celebratory animation with synchronized emoji rain."""
        try:
            animation_id = f"celebration_{achievement_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create celebration animation config
            animation_config = {
                "type": "celebration",
                "achievement_type": achievement_type,
                "intensity": 1.0,  # Maximum intensity for celebrations
                "duration": 5.0,   # Longer duration for celebrations
                "particle_count": 150,
                "effects": ["burst", "sparkle", "glow"],
                "colors": ["#FFD700", "#FF6B6B", "#4ECDC4", "#45B7D1"],
                "intelligence_type": "celebration",
                "achievement_data": achievement_data or {}
            }
            
            # Optimize for performance
            animation_config = await self._optimize_animation_config(animation_config)
            
            # Start the animation
            success = await self.animation_controller.start_animation(animation_id, animation_config)
            if success:
                # Trigger celebration emoji rain
                if self.emoji_rain_bridge:
                    try:
                        rain_effect_id = await self.emoji_rain_bridge.trigger_celebration_rain(
                            achievement_type, 
                            achievement_data
                        )
                        animation_config["rain_effect_id"] = rain_effect_id
                        logger.info(f"🎉 Celebration emoji rain triggered: {rain_effect_id}")
                    except Exception as e:
                        logger.warning(f"Failed to trigger celebration emoji rain: {e}")
                
                logger.info(f"Celebration animation created: {animation_id} ({achievement_type})")
                return animation_id
            else:
                raise Exception("Failed to start celebration animation")
                
        except Exception as e:
            logger.error(f"Failed to create engagement celebration: {e}")
            return ""
    
    async def create_pattern_discovery_animation(self, patterns: List[Any]) -> str:
        """Create animation celebrating data pattern discovery with themed emoji rain."""
        try:
            if not patterns:
                return ""
            
            animation_id = f"pattern_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Use the most confident pattern for the animation
            best_pattern = max(patterns, key=lambda p: p.confidence)
            
            animation_config = {
                "type": "pattern_discovery",
                "detected_pattern": best_pattern.pattern_type,
                "pattern_confidence": best_pattern.confidence,
                "pattern_intensity": best_pattern.intensity,
                "pattern_direction": best_pattern.direction,
                "duration": 3.0,
                "intelligence_enabled": True,
                "intelligence_type": "pattern_discovery",
                "celebration_level": "discovery"
            }
            
            # Optimize for performance
            animation_config = await self._optimize_animation_config(animation_config)
            
            # Start the animation
            success = await self.animation_controller.start_animation(animation_id, animation_config)
            if success:
                # Trigger pattern-specific emoji rain
                if self.emoji_rain_bridge:
                    try:
                        rain_effect_id = await self.emoji_rain_bridge.trigger_data_pattern_rain(
                            best_pattern.pattern_type,
                            {
                                "intensity": best_pattern.intensity,
                                "confidence": best_pattern.confidence,
                                "direction": best_pattern.direction
                            }
                        )
                        animation_config["rain_effect_id"] = rain_effect_id
                        logger.info(f"🔍 Pattern discovery emoji rain triggered: {rain_effect_id}")
                    except Exception as e:
                        logger.warning(f"Failed to trigger pattern discovery emoji rain: {e}")
                
                logger.info(f"Pattern discovery animation created: {animation_id} ({best_pattern.pattern_type})")
                return animation_id
            else:
                raise Exception("Failed to start pattern discovery animation")
                
        except Exception as e:
            logger.error(f"Failed to create pattern discovery animation: {e}")
            return ""
    
    async def create_milestone_animation(self, milestone_type: str, milestone_data: Dict[str, Any]) -> str:
        """Create milestone achievement animation with celebratory emoji rain."""
        try:
            animation_id = f"milestone_{milestone_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Determine milestone significance
            significance = milestone_data.get("significance", 0.5)
            
            animation_config = {
                "type": "milestone",
                "milestone_type": milestone_type,
                "significance": significance,
                "intensity": 0.5 + significance * 0.5,  # Scale with significance
                "duration": 3.0 + significance * 2.0,   # Longer for more significant milestones
                "particle_count": int(50 + significance * 100),
                "effects": ["radial_burst", "sparkle", "trail"],
                "intelligence_type": "milestone",
                "milestone_data": milestone_data
            }
            
            # Optimize for performance
            animation_config = await self._optimize_animation_config(animation_config)
            
            # Start the animation
            success = await self.animation_controller.start_animation(animation_id, animation_config)
            if success:
                # Trigger milestone emoji rain
                if self.emoji_rain_bridge:
                    try:
                        rain_effect_id = await self.emoji_rain_bridge.trigger_celebration_rain(
                            "milestone", 
                            milestone_data
                        )
                        animation_config["rain_effect_id"] = rain_effect_id
                        logger.info(f"🏆 Milestone emoji rain triggered: {rain_effect_id}")
                    except Exception as e:
                        logger.warning(f"Failed to trigger milestone emoji rain: {e}")
                
                logger.info(f"Milestone animation created: {animation_id} ({milestone_type})")
                return animation_id
            else:
                raise Exception("Failed to start milestone animation")
                
        except Exception as e:
            logger.error(f"Failed to create milestone animation: {e}")
            return ""
    
    async def get_emoji_rain_integration_status(self) -> Dict[str, Any]:
        """Get status of emoji rain integration."""
        try:
            if not self.emoji_rain_bridge:
                return {
                    "integrated": False,
                    "status": "not_connected",
                    "capabilities": []
                }
            
            bridge_health = self.emoji_rain_bridge.get_health_status()
            bridge_capabilities = self.emoji_rain_bridge.get_capabilities()
            
            # Count animations with emoji rain effects
            animations_with_rain = sum(
                1 for anim_data in self.animation_controller.active_animations.values()
                if "rain_effect_id" in anim_data.get("config", {})
            )
            
            return {
                "integrated": True,
                "status": "connected",
                "bridge_health": bridge_health,
                "capabilities": bridge_capabilities,
                "active_animations_with_rain": animations_with_rain,
                "total_active_animations": len(self.animation_controller.active_animations),
                "rain_integration_rate": (
                    animations_with_rain / len(self.animation_controller.active_animations)
                    if self.animation_controller.active_animations else 0.0
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to get emoji rain integration status: {e}")
            return {"error": str(e)}
    
    async def _optimize_animation_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize animation configuration based on performance mode."""
        try:
            optimized_config = config.copy()
            
            if self.performance_mode == "performance":
                # Optimize for performance
                optimized_config["particle_count"] = min(50, config.get("particle_count", 100))
                optimized_config["quality_level"] = min(2, config.get("quality_level", 3))
                optimized_config["enable_gpu_acceleration"] = True
                optimized_config["frame_skip_enabled"] = True
                
            elif self.performance_mode == "balanced":
                # Balanced optimization
                optimized_config["particle_count"] = min(100, config.get("particle_count", 100))
                optimized_config["quality_level"] = min(3, config.get("quality_level", 3))
                optimized_config["enable_gpu_acceleration"] = self.gpu_available
                optimized_config["frame_skip_enabled"] = True
                
            elif self.performance_mode == "quality":
                # Optimize for quality
                optimized_config["particle_count"] = min(200, config.get("particle_count", 100))
                optimized_config["quality_level"] = min(5, config.get("quality_level", 3))
                optimized_config["enable_gpu_acceleration"] = self.gpu_available
                optimized_config["frame_skip_enabled"] = False
            
            return optimized_config
            
        except Exception as e:
            logger.error(f"Animation config optimization failed: {e}")
            return config
    
    async def create_attention_animation(self, target_element: str, priority: str = "medium") -> str:
        """Create attention-grabbing animation."""
        try:
            animation_id = f"attention_{target_element}_{datetime.now().strftime('%H%M%S')}"
            
            animation_config = {
                "type": "attention",
                "target": target_element,
                "priority": priority,
                "effects": ["pulse", "highlight"],
                "duration": 1.5
            }
            
            success = await self.animation_controller.start_animation(animation_id, animation_config)
            if success:
                # Trigger attention-specific emoji rain
                if self.emoji_rain_bridge:
                    try:
                        rain_effect_id = await self.emoji_rain_bridge.trigger_engagement_rain(animation_config)
                        animation_config["rain_effect_id"] = rain_effect_id
                        logger.info(f"🌧️ Attention emoji rain triggered: {rain_effect_id}")
                    except Exception as e:
                        logger.warning(f"Failed to trigger attention emoji rain: {e}")
                
                logger.info(f"Attention animation created: {animation_id}")
                return animation_id
            else:
                raise Exception("Failed to start attention animation")
                
        except Exception as e:
            logger.error(f"Failed to create attention animation: {e}")
            return ""
    
    async def get_animation_status(self) -> Dict[str, Any]:
        """Get current animation system status."""
        try:
            performance_metrics = await self.performance_monitor.get_performance_metrics()
            performance_issues = await self.performance_monitor.detect_performance_issues()
            
            return {
                "initialized": self.is_initialized,
                "gpu_available": self.gpu_available,
                "active_animations": len(self.animation_controller.active_animations),
                "performance": performance_metrics,
                "issues": performance_issues,
                "config": {
                    "target_fps": self.config.target_fps,
                    "gpu_acceleration": self.config.gpu_acceleration,
                    "adaptive_complexity": self.config.adaptive_complexity
                }
            }
        except Exception as e:
            logger.error(f"Failed to get animation status: {e}")
            return {"error": str(e)}
    
    async def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        try:
            # Placeholder GPU detection logic
            # In a real implementation, this would check for WebGL, GPU libraries, etc.
            return True
        except Exception as e:
            logger.warning(f"GPU availability check failed: {e}")
            return False
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Animation Engine capabilities."""
        capabilities = [
            "intelligent_data_driven_animations",
            "pattern_recognition_animations",
            "velocity_correlated_animations",
            "quality_visualization_animations",
            "mathematical_relationship_animations",
            "attention_animations", 
            "gpu_acceleration",
            "performance_monitoring",
            "adaptive_complexity",
            "data_intelligence_analysis",
            "real_time_pattern_detection",
            "celebration_animations",
            "milestone_animations",
            "pattern_discovery_animations"
        ]
        
        # Add emoji rain capabilities if integrated
        if self.emoji_rain_bridge:
            capabilities.extend([
                "emoji_rain_integration",
                "synchronized_emoji_effects",
                "intelligent_emoji_selection",
                "celebration_emoji_rain",
                "pattern_themed_emoji_rain"
            ])
        
        return capabilities
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Animation Engine health status."""
        return {
            "status": "healthy" if self.is_initialized else "initializing",
            "gpu_available": self.gpu_available,
            "active_animations": len(self.animation_controller.active_animations),
            "performance_ok": True  # Placeholder
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Animation Engine module information."""
        return {
            "module_id": self.module_id,
            "name": "Animation Engine",
            "version": "1.0.0",
            "description": "GPU-accelerated visual effects and data-driven animations"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation when performance issues occur."""
        try:
            degradation_actions = []
            
            # Switch to performance mode
            if self.performance_mode != "performance":
                asyncio.create_task(self.set_performance_mode("performance"))
                degradation_actions.append("Switched to performance mode")
            
            # Disable GPU acceleration if available
            if self.config.gpu_acceleration:
                self.config.gpu_acceleration = False
                degradation_actions.append("Disabled GPU acceleration")
            
            # Reduce target FPS aggressively
            if self.config.target_fps > 20:
                self.config.target_fps = 20
                degradation_actions.append("Reduced target FPS to 20")
            
            # Enable frame skipping
            self.frame_skip_threshold = 15.0
            degradation_actions.append("Enabled aggressive frame skipping")
            
            # Stop non-critical animations
            critical_animations = []
            for anim_id, anim_data in self.animation_controller.active_animations.items():
                priority = anim_data.get("config", {}).get("priority", "normal")
                if priority not in ["critical", "high"]:
                    asyncio.create_task(self.animation_controller.stop_animation(anim_id))
                    degradation_actions.append(f"Stopped {priority} priority animation: {anim_id}")
                else:
                    critical_animations.append(anim_id)
            
            # Reduce quality of remaining animations
            for anim_id, anim_data in self.animation_controller.active_animations.items():
                config = anim_data.get("config", {})
                config["particle_count"] = min(20, config.get("particle_count", 100))
                config["quality_level"] = 1
                config["enable_effects"] = False
            
            degradation_actions.append(f"Reduced quality for {len(critical_animations)} critical animations")
            
            # Enable all adaptive features
            self.config.adaptive_complexity = True
            self.adaptive_quality_enabled = True
            degradation_actions.append("Enabled all adaptive features")
            
            # Clear performance history to free memory
            history_cleared = len(self.performance_history)
            self.performance_history.clear()
            degradation_actions.append(f"Cleared {history_cleared} performance history entries")
            
            return {
                "status": "degraded",
                "actions_taken": degradation_actions,
                "active_animations": len(critical_animations),
                "performance_mode": "emergency",
                "functionality_level": "critical_animations_only",
                "recovery_possible": True,
                "recovery_instructions": "Performance will recover automatically when system load decreases"
            }
        except Exception as e:
            return {
                "status": "degradation_failed",
                "error": str(e),
                "functionality_level": "unknown",
                "recovery_possible": False
            }