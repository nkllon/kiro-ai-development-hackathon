"""
Core data models for the Beast Mode Coordination Observatory.

These models define the structure for coordination events, metrics, and configuration
that enable real-time monitoring with cultural reinforcement.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class CoordinationEventType(Enum):
    """Types of coordination events that can occur in the system."""
    TASK_COMPLETED = auto()
    TASK_FAILED = auto()
    QUEUE_HEALTH_CHANGE = auto()
    API_CALL_SUCCESS = auto()
    API_CALL_FAILURE = auto()
    COST_THRESHOLD_REACHED = auto()
    ANOMALY_DETECTED = auto()
    ACHIEVEMENT_UNLOCKED = auto()
    COORDINATION_MILESTONE = auto()
    SYSTEM_HEALTH_CHANGE = auto()


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    COST_SPIKE = auto()
    PERFORMANCE_DEGRADATION = auto()
    ERROR_RATE_INCREASE = auto()
    COORDINATION_BREAKDOWN = auto()
    RESOURCE_EXHAUSTION = auto()
    PATTERN_DEVIATION = auto()


class AnomalySeverity(Enum):
    """Severity levels for detected anomalies."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class HealthTrend(Enum):
    """Trend direction for health scores."""
    IMPROVING = auto()
    STABLE = auto()
    DECLINING = auto()
    CRITICAL = auto()


class CostTrend(Enum):
    """Trend direction for cost metrics."""
    DECREASING = auto()
    STABLE = auto()
    INCREASING = auto()
    SPIKING = auto()


class AnimationStyle(Enum):
    """Animation styles for emoji rain effects."""
    GENTLE_FALL = auto()
    CELEBRATION_BURST = auto()
    ACHIEVEMENT_SHOWER = auto()
    ALERT_PULSE = auto()


@dataclass
class SystemLoadMetrics:
    """System load and resource utilization metrics."""
    cpu_usage_percent: float
    memory_usage_percent: float
    redis_memory_usage_mb: float
    active_connections: int
    queue_depth: int


@dataclass
class CoordinationEvent:
    """Represents a coordination event in the system."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: CoordinationEventType = CoordinationEventType.TASK_COMPLETED
    source_component: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class CoordinationMetrics:
    """Comprehensive coordination health metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    task_queue_health: float = 1.0  # 0.0 to 1.0
    api_response_times: Dict[str, float] = field(default_factory=dict)
    error_rates: Dict[str, float] = field(default_factory=dict)
    throughput_metrics: Dict[str, int] = field(default_factory=dict)
    coordination_efficiency: float = 1.0
    system_load: SystemLoadMetrics = field(default_factory=lambda: SystemLoadMetrics(0, 0, 0, 0, 0))


@dataclass
class LLMMetrics:
    """LLM API usage and cost metrics."""
    provider: str
    model: str
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: int = 0
    estimated_cost: Decimal = field(default_factory=lambda: Decimal('0.00'))
    response_time_ms: float = 0.0
    operation_type: str = "completion"  # completion, embedding, etc.
    success: bool = True
    error_type: Optional[str] = None


@dataclass
class CostAnomaly:
    """Detected cost anomaly."""
    anomaly_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    provider: str = ""
    cost_increase_percent: float = 0.0
    description: str = ""
    confidence_score: float = 0.0


@dataclass
class CostMetrics:
    """Real-time cost tracking across providers."""
    timestamp: datetime = field(default_factory=datetime.now)
    total_cost_today: Decimal = field(default_factory=lambda: Decimal('0.00'))
    cost_by_provider: Dict[str, Decimal] = field(default_factory=dict)
    cost_by_model: Dict[str, Decimal] = field(default_factory=dict)
    projected_monthly_cost: Decimal = field(default_factory=lambda: Decimal('0.00'))
    cost_trend: CostTrend = CostTrend.STABLE
    anomalies: List[CostAnomaly] = field(default_factory=list)


@dataclass
class HealthFactor:
    """Factor contributing to overall health score."""
    name: str
    score: float  # 0.0 to 1.0
    weight: float  # Importance weight
    description: str


@dataclass
class HealthScore:
    """Overall system coordination health score."""
    overall_score: float  # 0.0 to 1.0
    component_scores: Dict[str, float] = field(default_factory=dict)
    trend: HealthTrend = HealthTrend.STABLE
    factors: List[HealthFactor] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Anomaly:
    """Detected anomaly in system behavior."""
    anomaly_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    anomaly_type: AnomalyType = AnomalyType.PATTERN_DEVIATION
    severity: AnomalySeverity = AnomalySeverity.LOW
    affected_components: List[str] = field(default_factory=list)
    description: str = ""
    confidence_score: float = 0.0
    suggested_actions: List[str] = field(default_factory=list)
    auto_resolved: bool = False


@dataclass
class CelebrationEffect:
    """Configuration for celebration visual effects."""
    effect_type: str = "burst"
    duration_seconds: float = 3.0
    intensity: float = 1.0
    colors: List[str] = field(default_factory=lambda: ["#FFD700", "#FF6B6B", "#4ECDC4"])


@dataclass
class Achievement:
    """Coordination achievement for gamification."""
    achievement_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    icon_emoji: str = "🏆"
    unlocked_at: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    celebration_effect: CelebrationEffect = field(default_factory=CelebrationEffect)


@dataclass
class EmojiRainEffect:
    """Configuration for emoji rain visualization."""
    emojis: List[str] = field(default_factory=lambda: ["✨", "🎉", "🚀"])
    intensity: float = 0.5  # 0.0 to 1.0
    duration_seconds: float = 5.0
    animation_style: AnimationStyle = AnimationStyle.GENTLE_FALL
    trigger_event: str = ""


# Configuration Models

@dataclass
class RedisConfig:
    """Redis connection configuration."""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    ssl: bool = False
    connection_pool_size: int = 10
    stream_name: str = "observatory_metrics"


@dataclass
class WebSocketConfig:
    """WebSocket server configuration."""
    host: str = "0.0.0.0"
    port: int = 8888
    max_connections: int = 100
    heartbeat_interval: int = 30


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""
    collection_interval_seconds: int = 5
    retention_days: int = 30
    high_frequency_metrics: List[str] = field(default_factory=list)
    component_discovery_enabled: bool = True
    performance_impact_limit: float = 0.01  # Max 1% performance impact


@dataclass
class AnalyticsConfig:
    """Configuration for real-time analytics."""
    window_size_seconds: int = 60
    trend_analysis_window_minutes: int = 15
    health_calculation_interval: int = 10
    enable_ml_analytics: bool = False


@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider."""
    name: str
    api_key_env_var: str
    cost_per_1k_tokens: Dict[str, Decimal]  # model -> cost
    rate_limit_rpm: int = 60


@dataclass
class CostTrackingConfig:
    """Configuration for LLM cost tracking."""
    provider_configs: Dict[str, ProviderConfig] = field(default_factory=dict)
    cost_alert_thresholds: Dict[str, Decimal] = field(default_factory=dict)
    projection_window_days: int = 30
    anomaly_detection_sensitivity: float = 0.8


@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection."""
    enable_ml: bool = False
    enable_ml_detection: bool = False  # Legacy name, keep for compatibility
    baseline_window_days: int = 7
    sensitivity_threshold: float = 0.8
    auto_resolution_timeout_minutes: int = 30
    detection_interval_seconds: int = 10

    def __post_init__(self):
        # Support both naming conventions
        if self.enable_ml_detection:
            self.enable_ml = self.enable_ml_detection


@dataclass
class GamificationConfig:
    """Configuration for gamification features."""
    achievements_enabled: bool = True
    team_metrics_enabled: bool = True
    celebration_effects_enabled: bool = True
    emoji_rain_enabled: bool = True
    leaderboard_enabled: bool = False  # Privacy-conscious default


@dataclass
class WebInterfaceConfig:
    """Configuration for the web interface."""
    title: str = "Beast Mode Coordination Observatory"
    theme: str = "dark"
    refresh_rate_ms: int = 1000
    chart_animation_duration_ms: int = 750
    enable_demo_mode: bool = False


@dataclass
class ObservatoryConfig:
    """Main configuration for the Observatory system."""
    redis_config: RedisConfig = field(default_factory=RedisConfig)
    websocket_config: WebSocketConfig = field(default_factory=WebSocketConfig)
    metrics_config: MetricsConfig = field(default_factory=MetricsConfig)
    analytics_config: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    anomaly_config: AnomalyConfig = field(default_factory=AnomalyConfig)
    cost_config: CostTrackingConfig = field(default_factory=CostTrackingConfig)
    gamification_config: GamificationConfig = field(default_factory=GamificationConfig)
    web_interface_config: WebInterfaceConfig = field(default_factory=WebInterfaceConfig)

    def validate(self) -> bool:
        """Validate configuration parameters."""
        # Basic validation - can be expanded
        if self.redis_config.port <= 0 or self.redis_config.port > 65535:
            return False
        if self.websocket_config.port <= 0 or self.websocket_config.port > 65535:
            return False
        if self.metrics_config.collection_interval_seconds <= 0:
            return False
        return True