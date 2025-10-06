"""
Data Storyteller Engine - Intelligent Data Discovery and Narrative Generation
============================================================================

The Data Storyteller Engine automatically discovers interesting patterns, anomalies,
and correlations in live data streams, then generates human-readable narratives
and visual highlights to make data insights engaging and actionable.
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.interfaces import EngagementLevel, EngagementContext

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of data patterns that can be detected."""
    TREND_INCREASING = "trend_increasing"
    TREND_DECREASING = "trend_decreasing"
    ANOMALY_SPIKE = "anomaly_spike"
    ANOMALY_DROP = "anomaly_drop"
    CORRELATION_POSITIVE = "correlation_positive"
    CORRELATION_NEGATIVE = "correlation_negative"
    CYCLICAL_PATTERN = "cyclical_pattern"
    THRESHOLD_BREACH = "threshold_breach"
    STABILITY_PERIOD = "stability_period"
    VOLATILITY_INCREASE = "volatility_increase"


class InterestLevel(Enum):
    """How interesting a discovered pattern is."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DataPoint:
    """Represents a single data point with metadata."""
    timestamp: datetime
    value: float
    metric_name: str
    source: str
    quality_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectedPattern:
    """Represents a discovered data pattern."""
    pattern_id: str
    pattern_type: PatternType
    interest_level: InterestLevel
    confidence: float
    start_time: datetime
    end_time: datetime
    affected_metrics: List[str]
    description: str
    narrative: str
    visual_suggestion: Dict[str, Any]
    data_points: List[DataPoint] = field(default_factory=list)
    correlation_data: Optional[Dict[str, Any]] = None
    prediction: Optional[Dict[str, Any]] = None


@dataclass
class MetricCorrelation:
    """Represents correlation between two metrics."""
    metric_a: str
    metric_b: str
    correlation_coefficient: float
    confidence: float
    time_window: timedelta
    lag_seconds: int = 0


class IPatternDetector:
    """Interface for pattern detection algorithms."""
    
    async def detect_patterns(self, data_points: List[DataPoint]) -> List[DetectedPattern]:
        """Detect patterns in the provided data points."""
        raise NotImplementedError
    
    def get_pattern_types(self) -> List[PatternType]:
        """Get the types of patterns this detector can find."""
        raise NotImplementedError


class INarrativeGenerator:
    """Interface for generating human-readable narratives."""
    
    async def generate_narrative(self, pattern: DetectedPattern) -> str:
        """Generate a human-readable narrative for the pattern."""
        raise NotImplementedError
    
    async def generate_summary(self, patterns: List[DetectedPattern]) -> str:
        """Generate a summary narrative for multiple patterns."""
        raise NotImplementedError


class ICorrelationAnalyzer:
    """Interface for analyzing correlations between metrics."""
    
    async def analyze_correlations(self, metrics_data: Dict[str, List[DataPoint]]) -> List[MetricCorrelation]:
        """Analyze correlations between different metrics."""
        raise NotImplementedError
    
    async def find_leading_indicators(self, target_metric: str, candidate_metrics: List[str], 
                                    data: Dict[str, List[DataPoint]]) -> List[MetricCorrelation]:
        """Find metrics that lead changes in the target metric."""
        raise NotImplementedError


class TrendPatternDetector(IPatternDetector):
    """Detects trend patterns in time series data."""
    
    def __init__(self, min_trend_length: int = 5, trend_threshold: float = 0.1):
        self.min_trend_length = min_trend_length
        self.trend_threshold = trend_threshold
    
    async def detect_patterns(self, data_points: List[DataPoint]) -> List[DetectedPattern]:
        """Detect trend patterns in data."""
        if len(data_points) < self.min_trend_length:
            return []
        
        patterns = []
        
        # Sort by timestamp
        sorted_points = sorted(data_points, key=lambda p: p.timestamp)
        values = [p.value for p in sorted_points]
        
        # Calculate moving averages and trends
        window_size = min(self.min_trend_length, len(values))
        trends = []
        
        for i in range(window_size, len(values)):
            recent_values = values[i-window_size:i]
            trend_slope = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
            trends.append(trend_slope)
        
        # Detect significant trends
        for i, trend_slope in enumerate(trends):
            if abs(trend_slope) > self.trend_threshold:
                start_idx = i
                end_idx = i + window_size
                
                pattern_type = PatternType.TREND_INCREASING if trend_slope > 0 else PatternType.TREND_DECREASING
                interest_level = self._calculate_trend_interest(trend_slope, values[start_idx:end_idx])
                
                pattern = DetectedPattern(
                    pattern_id=f"trend_{sorted_points[0].metric_name}_{start_idx}",
                    pattern_type=pattern_type,
                    interest_level=interest_level,
                    confidence=min(abs(trend_slope) / self.trend_threshold, 1.0),
                    start_time=sorted_points[start_idx].timestamp,
                    end_time=sorted_points[end_idx-1].timestamp,
                    affected_metrics=[sorted_points[0].metric_name],
                    description=f"{'Increasing' if trend_slope > 0 else 'Decreasing'} trend detected",
                    narrative="",  # Will be filled by narrative generator
                    visual_suggestion={
                        "animation_type": "trend_highlight",
                        "color": "#2ecc71" if trend_slope > 0 else "#e74c3c",
                        "intensity": min(abs(trend_slope) * 10, 1.0)
                    },
                    data_points=sorted_points[start_idx:end_idx]
                )
                patterns.append(pattern)
        
        return patterns
    
    def get_pattern_types(self) -> List[PatternType]:
        return [PatternType.TREND_INCREASING, PatternType.TREND_DECREASING]
    
    def _calculate_trend_interest(self, slope: float, values: List[float]) -> InterestLevel:
        """Calculate how interesting a trend is based on slope and magnitude."""
        magnitude = max(values) - min(values)
        relative_change = magnitude / (np.mean(values) + 1e-6)
        
        if abs(slope) > 1.0 or relative_change > 0.5:
            return InterestLevel.CRITICAL
        elif abs(slope) > 0.5 or relative_change > 0.2:
            return InterestLevel.HIGH
        elif abs(slope) > 0.2 or relative_change > 0.1:
            return InterestLevel.MEDIUM
        else:
            return InterestLevel.LOW


class AnomalyPatternDetector(IPatternDetector):
    """Detects anomalies and outliers in data."""
    
    def __init__(self, z_threshold: float = 2.5, window_size: int = 20):
        self.z_threshold = z_threshold
        self.window_size = window_size
    
    async def detect_patterns(self, data_points: List[DataPoint]) -> List[DetectedPattern]:
        """Detect anomaly patterns in data."""
        if len(data_points) < self.window_size:
            return []
        
        patterns = []
        sorted_points = sorted(data_points, key=lambda p: p.timestamp)
        values = [p.value for p in sorted_points]
        
        # Calculate rolling statistics
        for i in range(self.window_size, len(values)):
            window_values = values[i-self.window_size:i]
            mean_val = np.mean(window_values)
            std_val = np.std(window_values)
            
            if std_val > 0:
                z_score = abs(values[i] - mean_val) / std_val
                
                if z_score > self.z_threshold:
                    pattern_type = PatternType.ANOMALY_SPIKE if values[i] > mean_val else PatternType.ANOMALY_DROP
                    interest_level = self._calculate_anomaly_interest(z_score)
                    
                    pattern = DetectedPattern(
                        pattern_id=f"anomaly_{sorted_points[0].metric_name}_{i}",
                        pattern_type=pattern_type,
                        interest_level=interest_level,
                        confidence=min(z_score / self.z_threshold, 1.0),
                        start_time=sorted_points[i].timestamp,
                        end_time=sorted_points[i].timestamp,
                        affected_metrics=[sorted_points[0].metric_name],
                        description=f"{'Spike' if values[i] > mean_val else 'Drop'} anomaly detected",
                        narrative="",  # Will be filled by narrative generator
                        visual_suggestion={
                            "animation_type": "anomaly_pulse",
                            "color": "#f39c12" if pattern_type == PatternType.ANOMALY_SPIKE else "#e67e22",
                            "intensity": min(z_score / 5.0, 1.0),
                            "pulse_rate": "fast"
                        },
                        data_points=[sorted_points[i]]
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def get_pattern_types(self) -> List[PatternType]:
        return [PatternType.ANOMALY_SPIKE, PatternType.ANOMALY_DROP]
    
    def _calculate_anomaly_interest(self, z_score: float) -> InterestLevel:
        """Calculate how interesting an anomaly is based on its z-score."""
        if z_score > 4.0:
            return InterestLevel.CRITICAL
        elif z_score > 3.0:
            return InterestLevel.HIGH
        elif z_score > 2.5:
            return InterestLevel.MEDIUM
        else:
            return InterestLevel.LOW


class CorrelationAnalyzer(ICorrelationAnalyzer):
    """Analyzes correlations between different metrics."""
    
    def __init__(self, min_correlation: float = 0.7, min_data_points: int = 10):
        self.min_correlation = min_correlation
        self.min_data_points = min_data_points
    
    async def analyze_correlations(self, metrics_data: Dict[str, List[DataPoint]]) -> List[MetricCorrelation]:
        """Analyze correlations between different metrics."""
        correlations = []
        metric_names = list(metrics_data.keys())
        
        for i, metric_a in enumerate(metric_names):
            for metric_b in metric_names[i+1:]:
                correlation = await self._calculate_correlation(
                    metrics_data[metric_a], 
                    metrics_data[metric_b]
                )
                if correlation and abs(correlation.correlation_coefficient) >= self.min_correlation:
                    correlations.append(correlation)
        
        return correlations
    
    async def find_leading_indicators(self, target_metric: str, candidate_metrics: List[str], 
                                    data: Dict[str, List[DataPoint]]) -> List[MetricCorrelation]:
        """Find metrics that lead changes in the target metric."""
        leading_indicators = []
        
        if target_metric not in data:
            return leading_indicators
        
        target_data = data[target_metric]
        
        for candidate in candidate_metrics:
            if candidate not in data or candidate == target_metric:
                continue
            
            # Test different lag periods
            for lag_minutes in [1, 5, 15, 30, 60]:
                correlation = await self._calculate_lagged_correlation(
                    data[candidate], target_data, lag_minutes
                )
                
                if correlation and abs(correlation.correlation_coefficient) >= self.min_correlation:
                    leading_indicators.append(correlation)
                    break  # Use the first significant lag found
        
        return leading_indicators
    
    async def _calculate_correlation(self, data_a: List[DataPoint], data_b: List[DataPoint]) -> Optional[MetricCorrelation]:
        """Calculate correlation between two data series."""
        if len(data_a) < self.min_data_points or len(data_b) < self.min_data_points:
            return None
        
        # Align data points by timestamp
        aligned_a, aligned_b = self._align_data_points(data_a, data_b)
        
        if len(aligned_a) < self.min_data_points:
            return None
        
        values_a = [p.value for p in aligned_a]
        values_b = [p.value for p in aligned_b]
        
        correlation_coeff = np.corrcoef(values_a, values_b)[0, 1]
        
        if np.isnan(correlation_coeff):
            return None
        
        # Calculate confidence based on data quality and sample size
        avg_quality = (np.mean([p.quality_score for p in aligned_a]) + 
                      np.mean([p.quality_score for p in aligned_b])) / 2
        sample_confidence = min(len(aligned_a) / 50.0, 1.0)  # More samples = higher confidence
        confidence = avg_quality * sample_confidence
        
        return MetricCorrelation(
            metric_a=data_a[0].metric_name,
            metric_b=data_b[0].metric_name,
            correlation_coefficient=correlation_coeff,
            confidence=confidence,
            time_window=aligned_a[-1].timestamp - aligned_a[0].timestamp,
            lag_seconds=0
        )
    
    async def _calculate_lagged_correlation(self, leading_data: List[DataPoint], 
                                         target_data: List[DataPoint], 
                                         lag_minutes: int) -> Optional[MetricCorrelation]:
        """Calculate correlation with a time lag."""
        lag_delta = timedelta(minutes=lag_minutes)
        
        # Shift the leading data forward by the lag amount
        shifted_leading = []
        for point in leading_data:
            shifted_point = DataPoint(
                timestamp=point.timestamp + lag_delta,
                value=point.value,
                metric_name=point.metric_name,
                source=point.source,
                quality_score=point.quality_score,
                metadata=point.metadata
            )
            shifted_leading.append(shifted_point)
        
        correlation = await self._calculate_correlation(shifted_leading, target_data)
        if correlation:
            correlation.lag_seconds = lag_minutes * 60
        
        return correlation
    
    def _align_data_points(self, data_a: List[DataPoint], data_b: List[DataPoint]) -> Tuple[List[DataPoint], List[DataPoint]]:
        """Align two data series by timestamp."""
        # Sort both series
        sorted_a = sorted(data_a, key=lambda p: p.timestamp)
        sorted_b = sorted(data_b, key=lambda p: p.timestamp)
        
        aligned_a = []
        aligned_b = []
        
        i, j = 0, 0
        tolerance = timedelta(seconds=30)  # Allow 30-second tolerance for alignment
        
        while i < len(sorted_a) and j < len(sorted_b):
            time_diff = abs(sorted_a[i].timestamp - sorted_b[j].timestamp)
            
            if time_diff <= tolerance:
                aligned_a.append(sorted_a[i])
                aligned_b.append(sorted_b[j])
                i += 1
                j += 1
            elif sorted_a[i].timestamp < sorted_b[j].timestamp:
                i += 1
            else:
                j += 1
        
        return aligned_a, aligned_b


class NarrativeGenerator(INarrativeGenerator):
    """Generates human-readable narratives using the 'bebopping along → something happened → response → outcome' story pattern."""
    
    def __init__(self):
        # Story-driven narrative templates following the dramatic arc
        self.narrative_templates = {
            PatternType.TREND_INCREASING: [
                "🎵 {metric} was cruising along normally, then started climbing steadily. The system responded by scaling resources. Result: {change:.1%} improvement over {duration} - the hero moment we needed! 🚀",
                "📈 Everything was bebopping along fine with {metric}, then we noticed it trending upward. The team leaned in, optimizations kicked in, and boom - {change:.1%} gains in {duration}. Victory! 🎯",
                "⬆️ {metric} was just doing its thing, then something shifted and it started rising. Our monitoring caught it, alerts fired, and the system auto-scaled. {change:.1%} improvement - crisis averted! 💪"
            ],
            PatternType.TREND_DECREASING: [
                "🎵 {metric} was humming along nicely, then started sliding downward. The team jumped in with optimizations, but it's still down {change:.1%} over {duration}. The plot thickens... 🎭",
                "📉 We were bebopping along with stable {metric}, then it began declining. Emergency protocols engaged, but we're still seeing a {change:.1%} drop in {duration}. Drama building! ⚡",
                "🔻 {metric} was steady as she goes, then took a downturn. All hands on deck, countermeasures deployed, yet down {change:.1%} over {duration}. The struggle continues! 🛠️"
            ],
            PatternType.ANOMALY_SPIKE: [
                "🎵 {metric} was just cruising along at normal levels, then WHAM! Massive spike hit - {magnitude:.1f}x higher than usual! Alerts screaming, team scrambling. Did we save the day? Stay tuned... ⚡",
                "🔥 Everything was bebopping along smoothly with {metric}, then it exploded to {magnitude:.1f}x normal levels! Circuit breakers triggered, emergency response activated. The hero's journey begins! 🚨",
                "📊 {metric} was doing its normal thing, then suddenly spiked {magnitude:.1f}x higher! Auto-scaling kicked in, monitoring went crazy, and now we're in full response mode. Epic battle underway! ⚔️"
            ],
            PatternType.ANOMALY_DROP: [
                "🎵 {metric} was bebopping along fine, then suddenly crashed to {magnitude:.1f}x below normal! Red alerts everywhere, team mobilizing. Can our heroes recover? The tension builds... 😰",
                "⚠️ We were cruising with stable {metric}, then it plummeted {magnitude:.1f}x lower than expected! Emergency protocols firing, all systems responding. Will this be our comeback story? 🎬",
                "🔻 {metric} was steady as a rock, then took a dramatic dive to {magnitude:.1f}x normal levels! Incident response activated, troubleshooting in progress. The plot thickens! 🕵️"
            ],
            PatternType.CORRELATION_POSITIVE: [
                "🎵 {metric_a} and {metric_b} were doing their own thing, then we noticed they started dancing together! {correlation:.0%} correlation discovered. The system learned, adapted, and now we're optimizing both. Teamwork makes the dream work! 🤝",
                "🔗 We were bebopping along monitoring {metric_a} and {metric_b} separately, then realized they're best friends - {correlation:.0%} correlation! Our AI caught it, tuned the algorithms, and now we're predicting both. Victory through insight! 🧠",
                "📈 {metric_a} and {metric_b} seemed independent, then the pattern emerged - they move together {correlation:.0%} of the time! Machine learning kicked in, models updated, optimization achieved. The hero was the data all along! 📊"
            ],
            PatternType.CORRELATION_NEGATIVE: [
                "🎵 {metric_a} and {metric_b} were bebopping along independently, then we discovered they're frenemies - {correlation:.0%} inverse correlation! Load balancer adjusted, resources rebalanced. Tension resolved! ⚖️",
                "🔄 Everything seemed normal with {metric_a} and {metric_b}, then the inverse relationship revealed itself - {correlation:.0%} negative correlation! Smart routing engaged, conflicts minimized. Drama turned to harmony! 🎭",
                "🔀 We were monitoring {metric_a} and {metric_b} separately, then noticed when one goes up, the other goes down {correlation:.0%} of the time! Auto-balancing activated, equilibrium restored. The system found its balance! ⚖️"
            ]
        }
    
    async def generate_narrative(self, pattern: DetectedPattern) -> str:
        """Generate a human-readable narrative for the pattern."""
        templates = self.narrative_templates.get(pattern.pattern_type, ["Pattern detected in {metric}."])
        template = np.random.choice(templates)
        
        # Prepare template variables
        variables = {
            "metric": pattern.affected_metrics[0] if pattern.affected_metrics else "metric",
            "confidence": pattern.confidence,
            "duration": self._format_duration(pattern.end_time - pattern.start_time)
        }
        
        # Add pattern-specific variables
        if pattern.pattern_type in [PatternType.TREND_INCREASING, PatternType.TREND_DECREASING]:
            if pattern.data_points:
                start_val = pattern.data_points[0].value
                end_val = pattern.data_points[-1].value
                change = (end_val - start_val) / (start_val + 1e-6)
                variables["change"] = abs(change)
        
        elif pattern.pattern_type in [PatternType.ANOMALY_SPIKE, PatternType.ANOMALY_DROP]:
            if pattern.data_points:
                # Calculate magnitude relative to recent average
                recent_values = [p.value for p in pattern.data_points[-10:] if p != pattern.data_points[-1]]
                if recent_values:
                    avg_recent = np.mean(recent_values)
                    magnitude = pattern.data_points[-1].value / (avg_recent + 1e-6)
                    variables["magnitude"] = magnitude
                else:
                    variables["magnitude"] = 2.0  # Default magnitude
        
        elif pattern.correlation_data:
            variables.update(pattern.correlation_data)
        
        try:
            narrative = template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing template variable {e} for pattern {pattern.pattern_id}")
            narrative = f"Interesting pattern detected in {variables.get('metric', 'data')}"
        
        return narrative
    
    async def generate_summary(self, patterns: List[DetectedPattern]) -> str:
        """Generate a summary narrative following the dramatic story arc."""
        if not patterns:
            return "🎵 Everything was bebopping along smoothly - all systems in harmony, no drama to report. Sometimes the best story is no story! ✨"
        
        # Group patterns by interest level for dramatic effect
        critical_patterns = [p for p in patterns if p.interest_level == InterestLevel.CRITICAL]
        high_patterns = [p for p in patterns if p.interest_level == InterestLevel.HIGH]
        medium_patterns = [p for p in patterns if p.interest_level == InterestLevel.MEDIUM]
        
        # Create dramatic story arc
        story_parts = []
        
        # The setup - we were bebopping along
        story_parts.append("🎵 We were bebopping along with our systems")
        
        # Then this happened - the inciting incident
        if critical_patterns:
            story_parts.append(f"then BOOM! {len(critical_patterns)} critical situation{'s' if len(critical_patterns) > 1 else ''} erupted! 🚨")
            
            # The response
            story_parts.append("Emergency protocols activated, all hands on deck")
            
            # The outcome (building drama)
            story_parts.append("The battle is ON - will our heroes save the day? 🦸‍♂️")
            
        elif high_patterns:
            story_parts.append(f"then {len(high_patterns)} significant event{'s' if len(high_patterns) > 1 else ''} caught our attention! ⚠️")
            
            # The response  
            story_parts.append("Monitoring systems engaged, team investigating")
            
            # The outcome
            story_parts.append("Plot thickening - stay tuned for the resolution! 🎬")
            
        elif medium_patterns:
            story_parts.append(f"then we noticed {len(medium_patterns)} interesting development{'s' if len(medium_patterns) > 1 else ''} 📈")
            
            # The response
            story_parts.append("Systems adapting, optimizations in progress")
            
            # The outcome
            story_parts.append("Steady progress - the quiet hero's journey continues! 🌟")
        
        # Add additional drama if we have mixed patterns
        total_patterns = len(patterns)
        if total_patterns > 5:
            story_parts.append(f"With {total_patterns} total patterns unfolding, this is turning into quite the epic! 📚")
        
        return " ".join(story_parts)
    
    async def generate_story_arc(self, patterns: List[DetectedPattern]) -> str:
        """Generate a connected story arc from multiple related patterns."""
        if not patterns:
            return ""
        
        # Sort patterns by timestamp to create chronological story
        sorted_patterns = sorted(patterns, key=lambda p: p.start_time)
        
        # Identify story themes
        metrics_involved = set()
        for pattern in sorted_patterns:
            metrics_involved.update(pattern.affected_metrics)
        
        # Create the story arc
        story = []
        
        # Opening - the normal state
        story.append(f"🎵 Our {', '.join(list(metrics_involved)[:3])} were bebopping along in their usual rhythm")
        
        # The inciting incident - first significant pattern
        first_pattern = sorted_patterns[0]
        if first_pattern.interest_level in [InterestLevel.CRITICAL, InterestLevel.HIGH]:
            story.append(f"when suddenly {first_pattern.affected_metrics[0]} {self._get_action_verb(first_pattern.pattern_type)}!")
        
        # Rising action - subsequent patterns
        if len(sorted_patterns) > 1:
            story.append("This triggered a cascade:")
            for pattern in sorted_patterns[1:3]:  # Show up to 2 more patterns
                action = self._get_action_verb(pattern.pattern_type)
                story.append(f"• {pattern.affected_metrics[0]} {action}")
        
        # The response - what we did
        story.append("🦸‍♂️ Our monitoring heroes sprang into action:")
        story.append("• Alerts fired across all channels")
        story.append("• Auto-scaling kicked in where needed") 
        story.append("• The team mobilized for rapid response")
        
        # The outcome - did it work?
        critical_count = len([p for p in sorted_patterns if p.interest_level == InterestLevel.CRITICAL])
        if critical_count > 0:
            story.append(f"⚔️ The battle continues with {critical_count} critical situation{'s' if critical_count > 1 else ''} still unfolding...")
            story.append("Will our heroes save the day? The drama builds! 🎭")
        else:
            story.append("✅ Crisis averted! Systems stabilized, metrics normalized.")
            story.append("Once again, our heroes saved the day! 🎉")
        
        return " ".join(story)
    
    def _get_action_verb(self, pattern_type: PatternType) -> str:
        """Get dramatic action verb for pattern type."""
        action_verbs = {
            PatternType.TREND_INCREASING: "started climbing rapidly",
            PatternType.TREND_DECREASING: "began sliding downward", 
            PatternType.ANOMALY_SPIKE: "exploded through the roof",
            PatternType.ANOMALY_DROP: "crashed through the floor",
            PatternType.CORRELATION_POSITIVE: "synchronized with its partner",
            PatternType.CORRELATION_NEGATIVE: "turned against its counterpart"
        }
        return action_verbs.get(pattern_type, "changed dramatically")
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format a duration in a human-readable way."""
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} seconds"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            days = total_seconds // 86400
            return f"{days} day{'s' if days > 1 else ''}"


class DataStorytellerEngine(ReflectiveModule):
    """
    Main Data Storyteller Engine that discovers interesting patterns in data
    and generates engaging narratives and visual suggestions.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "data_storyteller_engine"
        
        # Pattern detectors
        self.pattern_detectors: List[IPatternDetector] = [
            TrendPatternDetector(),
            AnomalyPatternDetector()
        ]
        
        # Analysis components
        self.correlation_analyzer = CorrelationAnalyzer()
        self.narrative_generator = NarrativeGenerator()
        
        # Data storage
        self.metrics_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.detected_patterns: List[DetectedPattern] = []
        self.pattern_history: deque = deque(maxlen=500)
        
        # Configuration
        self.analysis_interval = 30  # seconds
        self.max_patterns_per_analysis = 20
        
        logger.info("Data Storyteller Engine initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Data Storyteller Engine."""
        try:
            # Start background analysis task
            asyncio.create_task(self._background_analysis_loop())
            
            logger.info("Data Storyteller Engine initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Data Storyteller Engine initialization failed: {e}")
            return False
    
    async def add_data_point(self, data_point: DataPoint) -> None:
        """Add a new data point for analysis."""
        self.metrics_data[data_point.metric_name].append(data_point)
        
        # Trigger immediate analysis for critical metrics
        if data_point.metric_name in ["error_rate", "response_time", "cpu_usage"]:
            await self._analyze_metric_immediately(data_point.metric_name)
    
    async def add_data_points(self, data_points: List[DataPoint]) -> None:
        """Add multiple data points for analysis."""
        for point in data_points:
            self.metrics_data[point.metric_name].append(point)
    
    async def discover_patterns(self, metric_names: Optional[List[str]] = None) -> List[DetectedPattern]:
        """Discover interesting patterns in the specified metrics."""
        if metric_names is None:
            metric_names = list(self.metrics_data.keys())
        
        all_patterns = []
        
        for metric_name in metric_names:
            if metric_name not in self.metrics_data:
                continue
            
            data_points = list(self.metrics_data[metric_name])
            if len(data_points) < 5:  # Need minimum data for analysis
                continue
            
            # Run all pattern detectors
            for detector in self.pattern_detectors:
                try:
                    patterns = await detector.detect_patterns(data_points)
                    for pattern in patterns:
                        # Generate narrative
                        pattern.narrative = await self.narrative_generator.generate_narrative(pattern)
                        all_patterns.append(pattern)
                        
                except Exception as e:
                    logger.error(f"Error in pattern detector {detector.__class__.__name__}: {e}")
        
        # Sort by interest level and confidence
        all_patterns.sort(key=lambda p: (p.interest_level.value, p.confidence), reverse=True)
        
        # Limit number of patterns
        selected_patterns = all_patterns[:self.max_patterns_per_analysis]
        
        # Store patterns
        self.detected_patterns = selected_patterns
        self.pattern_history.extend(selected_patterns)
        
        return selected_patterns
    
    async def analyze_correlations(self, metric_names: Optional[List[str]] = None) -> List[MetricCorrelation]:
        """Analyze correlations between metrics."""
        if metric_names is None:
            metric_names = list(self.metrics_data.keys())
        
        # Prepare data for correlation analysis
        metrics_data = {}
        for metric_name in metric_names:
            if metric_name in self.metrics_data and len(self.metrics_data[metric_name]) >= 10:
                metrics_data[metric_name] = list(self.metrics_data[metric_name])
        
        if len(metrics_data) < 2:
            return []
        
        try:
            correlations = await self.correlation_analyzer.analyze_correlations(metrics_data)
            
            # Generate correlation patterns
            for correlation in correlations:
                if abs(correlation.correlation_coefficient) >= 0.7:
                    pattern_type = (PatternType.CORRELATION_POSITIVE if correlation.correlation_coefficient > 0 
                                  else PatternType.CORRELATION_NEGATIVE)
                    
                    interest_level = InterestLevel.HIGH if abs(correlation.correlation_coefficient) > 0.8 else InterestLevel.MEDIUM
                    
                    pattern = DetectedPattern(
                        pattern_id=f"correlation_{correlation.metric_a}_{correlation.metric_b}",
                        pattern_type=pattern_type,
                        interest_level=interest_level,
                        confidence=correlation.confidence,
                        start_time=datetime.now() - correlation.time_window,
                        end_time=datetime.now(),
                        affected_metrics=[correlation.metric_a, correlation.metric_b],
                        description=f"Correlation between {correlation.metric_a} and {correlation.metric_b}",
                        narrative="",
                        visual_suggestion={
                            "animation_type": "correlation_link",
                            "color": "#3498db" if correlation.correlation_coefficient > 0 else "#e74c3c",
                            "intensity": abs(correlation.correlation_coefficient)
                        },
                        correlation_data={
                            "metric_a": correlation.metric_a,
                            "metric_b": correlation.metric_b,
                            "correlation": correlation.correlation_coefficient
                        }
                    )
                    
                    pattern.narrative = await self.narrative_generator.generate_narrative(pattern)
                    self.detected_patterns.append(pattern)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
            return []
    
    async def get_current_insights(self) -> Dict[str, Any]:
        """Get current data insights and narratives with dramatic story arcs."""
        summary_narrative = await self.narrative_generator.generate_summary(self.detected_patterns)
        
        # Generate story arc for high-interest patterns
        high_interest_patterns = [p for p in self.detected_patterns 
                                if p.interest_level in [InterestLevel.CRITICAL, InterestLevel.HIGH]]
        story_arc = await self.narrative_generator.generate_story_arc(high_interest_patterns) if high_interest_patterns else ""
        
        return {
            "summary": summary_narrative,
            "story_arc": story_arc,
            "patterns": [
                {
                    "id": p.pattern_id,
                    "type": p.pattern_type.value,
                    "interest_level": p.interest_level.value,
                    "confidence": p.confidence,
                    "narrative": p.narrative,
                    "affected_metrics": p.affected_metrics,
                    "visual_suggestion": p.visual_suggestion,
                    "timestamp": p.end_time.isoformat()
                }
                for p in self.detected_patterns
            ],
            "metrics_analyzed": len(self.metrics_data),
            "total_data_points": sum(len(data) for data in self.metrics_data.values()),
            "analysis_timestamp": datetime.now().isoformat(),
            "drama_level": self._calculate_drama_level()
        }
    
    def _calculate_drama_level(self) -> str:
        """Calculate the current drama level of the system."""
        critical_count = len([p for p in self.detected_patterns if p.interest_level == InterestLevel.CRITICAL])
        high_count = len([p for p in self.detected_patterns if p.interest_level == InterestLevel.HIGH])
        
        if critical_count >= 3:
            return "EPIC_BATTLE"  # Multiple critical issues = epic battle
        elif critical_count >= 1:
            return "CRISIS_MODE"  # At least one critical = crisis
        elif high_count >= 3:
            return "RISING_ACTION"  # Multiple high interest = building tension
        elif high_count >= 1:
            return "PLOT_THICKENS"  # Some high interest = plot development
        else:
            return "PEACEFUL_TIMES"  # All quiet = peaceful
    
    async def _background_analysis_loop(self) -> None:
        """Background task that continuously analyzes data for patterns."""
        while True:
            try:
                await asyncio.sleep(self.analysis_interval)
                
                if self.metrics_data:
                    patterns = await self.discover_patterns()
                    correlations = await self.analyze_correlations()
                    
                    logger.debug(f"Background analysis complete: {len(patterns)} patterns, {len(correlations)} correlations")
                
            except Exception as e:
                logger.error(f"Error in background analysis loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _analyze_metric_immediately(self, metric_name: str) -> None:
        """Perform immediate analysis on a specific metric."""
        try:
            patterns = await self.discover_patterns([metric_name])
            if patterns:
                logger.info(f"Immediate analysis found {len(patterns)} patterns in {metric_name}")
        except Exception as e:
            logger.error(f"Error in immediate analysis for {metric_name}: {e}")
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List[str]:
        """Get Data Storyteller Engine capabilities."""
        return [
            "pattern_detection",
            "anomaly_detection", 
            "correlation_analysis",
            "narrative_generation",
            "trend_analysis",
            "real_time_insights"
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Data Storyteller Engine health status."""
        return {
            "status": "healthy",
            "metrics_tracked": len(self.metrics_data),
            "active_patterns": len(self.detected_patterns),
            "pattern_detectors": len(self.pattern_detectors),
            "total_data_points": sum(len(data) for data in self.metrics_data.values())
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Data Storyteller Engine module information."""
        return {
            "module_id": self.module_id,
            "name": "Data Storyteller Engine",
            "version": "1.0.0",
            "description": "Intelligent data pattern discovery and narrative generation"
        }
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation when errors occur."""
        try:
            logger.warning(f"Data Storyteller entering degradation mode due to: {error}")
            
            # Reduce analysis frequency
            self.analysis_interval = min(self.analysis_interval * 2, 300)  # Max 5 minutes
            
            # Reduce pattern detection complexity
            self.max_patterns_per_analysis = max(self.max_patterns_per_analysis // 2, 5)
            
            # Clear problematic data if needed
            if "memory" in str(error).lower():
                # Clear old data to free memory
                for metric_data in self.metrics_data.values():
                    if len(metric_data) > 100:
                        # Keep only recent 100 points
                        while len(metric_data) > 100:
                            metric_data.popleft()
            
            logger.info(f"Degradation applied: interval={self.analysis_interval}s, max_patterns={self.max_patterns_per_analysis}")
            return True
            
        except Exception as degradation_error:
            logger.error(f"Failed to apply graceful degradation: {degradation_error}")
            return False