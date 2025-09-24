"""
Unit tests for Observatory data models.

Tests the core data structures and configuration models for the
Beast Mode Coordination Observatory.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.beast_mode.observatory.models import (
    CoordinationEvent,
    CoordinationEventType,
    CoordinationMetrics,
    LLMMetrics,
    CostMetrics,
    CostTrend,
    HealthScore,
    HealthTrend,
    Anomaly,
    AnomalyType,
    AnomalySeverity,
    Achievement,
    EmojiRainEffect,
    AnimationStyle,
    ObservatoryConfig,
    RedisConfig,
    MetricsConfig,
    CostTrackingConfig,
    ProviderConfig,
)


class TestCoordinationEvent:
    """Test CoordinationEvent model."""
    
    def test_coordination_event_creation(self):
        """Test creating a coordination event with defaults."""
        event = CoordinationEvent(
            event_type=CoordinationEventType.TASK_COMPLETED,
            source_component="task_queue"
        )
        
        assert event.event_id is not None
        assert event.timestamp is not None
        assert event.event_type == CoordinationEventType.TASK_COMPLETED
        assert event.source_component == "task_queue"
        assert event.event_data == {}
        assert event.correlation_id is None
        assert event.user_id is None
    
    def test_coordination_event_with_data(self):
        """Test creating a coordination event with custom data."""
        event_data = {"task_id": "test-123", "duration_ms": 1500}
        event = CoordinationEvent(
            event_type=CoordinationEventType.TASK_COMPLETED,
            source_component="task_queue",
            event_data=event_data,
            correlation_id="corr-456",
            user_id="user-789"
        )
        
        assert event.event_data == event_data
        assert event.correlation_id == "corr-456"
        assert event.user_id == "user-789"


class TestCoordinationMetrics:
    """Test CoordinationMetrics model."""
    
    def test_coordination_metrics_defaults(self):
        """Test coordination metrics with default values."""
        metrics = CoordinationMetrics()
        
        assert metrics.timestamp is not None
        assert metrics.task_queue_health == 1.0
        assert metrics.api_response_times == {}
        assert metrics.error_rates == {}
        assert metrics.throughput_metrics == {}
        assert metrics.coordination_efficiency == 1.0
        assert metrics.system_load is not None
    
    def test_coordination_metrics_with_data(self):
        """Test coordination metrics with custom data."""
        api_times = {"openai": 250.5, "anthropic": 180.2}
        error_rates = {"task_queue": 0.01, "websocket": 0.005}
        
        metrics = CoordinationMetrics(
            task_queue_health=0.95,
            api_response_times=api_times,
            error_rates=error_rates,
            coordination_efficiency=0.88
        )
        
        assert metrics.task_queue_health == 0.95
        assert metrics.api_response_times == api_times
        assert metrics.error_rates == error_rates
        assert metrics.coordination_efficiency == 0.88


class TestLLMMetrics:
    """Test LLMMetrics model."""
    
    def test_llm_metrics_creation(self):
        """Test creating LLM metrics."""
        metrics = LLMMetrics(
            provider="openai",
            model="gpt-4",
            tokens_used=1500,
            estimated_cost=Decimal("0.045"),
            response_time_ms=2500.0,
            operation_type="completion"
        )
        
        assert metrics.provider == "openai"
        assert metrics.model == "gpt-4"
        assert metrics.tokens_used == 1500
        assert metrics.estimated_cost == Decimal("0.045")
        assert metrics.response_time_ms == 2500.0
        assert metrics.operation_type == "completion"
        assert metrics.success is True
        assert metrics.error_type is None
    
    def test_llm_metrics_with_error(self):
        """Test LLM metrics with error information."""
        metrics = LLMMetrics(
            provider="anthropic",
            model="claude-3-opus",
            success=False,
            error_type="rate_limit_exceeded"
        )
        
        assert metrics.success is False
        assert metrics.error_type == "rate_limit_exceeded"


class TestCostMetrics:
    """Test CostMetrics model."""
    
    def test_cost_metrics_defaults(self):
        """Test cost metrics with defaults."""
        metrics = CostMetrics()
        
        assert metrics.timestamp is not None
        assert metrics.total_cost_today == Decimal('0.00')
        assert metrics.cost_by_provider == {}
        assert metrics.cost_by_model == {}
        assert metrics.projected_monthly_cost == Decimal('0.00')
        assert metrics.cost_trend == CostTrend.STABLE
        assert metrics.anomalies == []
    
    def test_cost_metrics_with_data(self):
        """Test cost metrics with actual data."""
        cost_by_provider = {
            "openai": Decimal("25.50"),
            "anthropic": Decimal("18.75")
        }
        
        metrics = CostMetrics(
            total_cost_today=Decimal("44.25"),
            cost_by_provider=cost_by_provider,
            projected_monthly_cost=Decimal("1327.50"),
            cost_trend=CostTrend.INCREASING
        )
        
        assert metrics.total_cost_today == Decimal("44.25")
        assert metrics.cost_by_provider == cost_by_provider
        assert metrics.projected_monthly_cost == Decimal("1327.50")
        assert metrics.cost_trend == CostTrend.INCREASING


class TestHealthScore:
    """Test HealthScore model."""
    
    def test_health_score_defaults(self):
        """Test health score with defaults."""
        health = HealthScore(overall_score=0.85)
        
        assert health.overall_score == 0.85
        assert health.component_scores == {}
        assert health.trend == HealthTrend.STABLE
        assert health.factors == []
        assert health.recommendations == []


class TestAnomaly:
    """Test Anomaly model."""
    
    def test_anomaly_creation(self):
        """Test creating an anomaly."""
        anomaly = Anomaly(
            anomaly_type=AnomalyType.COST_SPIKE,
            severity=AnomalySeverity.HIGH,
            affected_components=["openai_api", "cost_tracker"],
            description="Unusual cost increase detected",
            confidence_score=0.92,
            suggested_actions=["Check API usage", "Review recent deployments"]
        )
        
        assert anomaly.anomaly_id is not None
        assert anomaly.timestamp is not None
        assert anomaly.anomaly_type == AnomalyType.COST_SPIKE
        assert anomaly.severity == AnomalySeverity.HIGH
        assert anomaly.affected_components == ["openai_api", "cost_tracker"]
        assert anomaly.description == "Unusual cost increase detected"
        assert anomaly.confidence_score == 0.92
        assert len(anomaly.suggested_actions) == 2
        assert anomaly.auto_resolved is False


class TestAchievement:
    """Test Achievement model."""
    
    def test_achievement_creation(self):
        """Test creating an achievement."""
        achievement = Achievement(
            name="Cost Optimizer",
            description="Reduced LLM costs by 20% through efficient coordination",
            icon_emoji="💰",
            user_id="user-123"
        )
        
        assert achievement.achievement_id is not None
        assert achievement.unlocked_at is not None
        assert achievement.name == "Cost Optimizer"
        assert achievement.description == "Reduced LLM costs by 20% through efficient coordination"
        assert achievement.icon_emoji == "💰"
        assert achievement.user_id == "user-123"
        assert achievement.celebration_effect is not None


class TestEmojiRainEffect:
    """Test EmojiRainEffect model."""
    
    def test_emoji_rain_defaults(self):
        """Test emoji rain effect with defaults."""
        effect = EmojiRainEffect()
        
        assert effect.emojis == ["✨", "🎉", "🚀"]
        assert effect.intensity == 0.5
        assert effect.duration_seconds == 5.0
        assert effect.animation_style == AnimationStyle.GENTLE_FALL
        assert effect.trigger_event == ""
    
    def test_emoji_rain_custom(self):
        """Test emoji rain effect with custom values."""
        custom_emojis = ["🏆", "🎊", "🌟"]
        effect = EmojiRainEffect(
            emojis=custom_emojis,
            intensity=0.8,
            duration_seconds=3.0,
            animation_style=AnimationStyle.CELEBRATION_BURST,
            trigger_event="achievement_unlocked"
        )
        
        assert effect.emojis == custom_emojis
        assert effect.intensity == 0.8
        assert effect.duration_seconds == 3.0
        assert effect.animation_style == AnimationStyle.CELEBRATION_BURST
        assert effect.trigger_event == "achievement_unlocked"


class TestObservatoryConfig:
    """Test ObservatoryConfig model."""
    
    def test_config_defaults(self):
        """Test configuration with default values."""
        config = ObservatoryConfig()
        
        assert config.redis_config is not None
        assert config.websocket_config is not None
        assert config.metrics_config is not None
        assert config.analytics_config is not None
        assert config.anomaly_config is not None
        assert config.cost_config is not None
        assert config.gamification_config is not None
        assert config.web_interface_config is not None
    
    def test_config_validation_valid(self):
        """Test configuration validation with valid config."""
        config = ObservatoryConfig()
        assert config.validate() is True
    
    def test_config_validation_invalid_redis_port(self):
        """Test configuration validation with invalid Redis port."""
        config = ObservatoryConfig()
        config.redis_config.port = -1
        assert config.validate() is False
    
    def test_config_validation_invalid_websocket_port(self):
        """Test configuration validation with invalid WebSocket port."""
        config = ObservatoryConfig()
        config.websocket_config.port = 70000
        assert config.validate() is False
    
    def test_config_validation_invalid_metrics_interval(self):
        """Test configuration validation with invalid metrics interval."""
        config = ObservatoryConfig()
        config.metrics_config.collection_interval_seconds = 0
        assert config.validate() is False


class TestProviderConfig:
    """Test ProviderConfig model."""
    
    def test_provider_config_creation(self):
        """Test creating a provider configuration."""
        cost_per_1k = {
            "gpt-4": Decimal("0.03"),
            "gpt-3.5-turbo": Decimal("0.002")
        }
        
        provider = ProviderConfig(
            name="openai",
            api_key_env_var="OPENAI_API_KEY",
            cost_per_1k_tokens=cost_per_1k,
            rate_limit_rpm=60
        )
        
        assert provider.name == "openai"
        assert provider.api_key_env_var == "OPENAI_API_KEY"
        assert provider.cost_per_1k_tokens == cost_per_1k
        assert provider.rate_limit_rpm == 60