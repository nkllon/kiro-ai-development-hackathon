"""
Comprehensive unit tests for the Observatory LLM Cost Tracker system.

Tests multi-provider cost tracking, anomaly detection, pricing calculations,
and real-time monitoring capabilities.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.beast_mode.observatory.llm_cost_tracker import (
    LLMCostTracker,
    LLMProvider,
    LLMPricing,
    LLMAPICall,
)
from src.beast_mode.observatory.models import (
    CostMetrics,
    CostTrend,
    CostAnomaly,
    ObservatoryConfig,
    RedisConfig,
    CostTrackingConfig
)


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.xadd = AsyncMock(return_value="stream-id")
    mock_redis.close = AsyncMock()
    return mock_redis


@pytest.fixture
def cost_config():
    """Sample cost tracking configuration."""
    return CostTrackingConfig(
        provider_configs={},
        cost_alert_thresholds={
            'daily_limit': Decimal('100.0'),
            'hourly_limit': Decimal('10.0'),
            'single_call_limit': Decimal('1.0')
        },
        projection_window_days=30,
        anomaly_detection_sensitivity=0.8
    )


@pytest.fixture
def observatory_config(cost_config):
    """Sample observatory configuration."""
    return ObservatoryConfig(
        redis_config=RedisConfig(
            host='localhost',
            port=6379,
            stream_name='test_metrics'
        ),
        cost_config=cost_config
    )


@pytest.fixture
async def cost_tracker(observatory_config, mock_redis):
    """Create and initialize an LLM cost tracker."""
    tracker = LLMCostTracker(observatory_config)

    with patch('redis.asyncio.Redis', return_value=mock_redis):
        await tracker.start_tracking()
        yield tracker
        await tracker.stop_tracking()


class TestLLMPricing:
    """Test LLM pricing model."""

    def test_llm_pricing_creation(self):
        """Test LLMPricing model creation."""
        pricing = LLMPricing(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            input_cost_per_1k_tokens=Decimal('0.03'),
            output_cost_per_1k_tokens=Decimal('0.06'),
            context_window=8192
        )

        assert pricing.provider == LLMProvider.OPENAI
        assert pricing.model == "gpt-4"
        assert pricing.input_cost_per_1k_tokens == Decimal('0.03')
        assert pricing.output_cost_per_1k_tokens == Decimal('0.06')
        assert pricing.context_window == 8192
        assert isinstance(pricing.last_updated, datetime)


class TestLLMAPICall:
    """Test LLM API call model."""

    def test_api_call_creation_with_defaults(self):
        """Test LLMAPICall creation with default values."""
        api_call = LLMAPICall(
            input_tokens=100,
            output_tokens=50
        )

        assert isinstance(api_call.call_id, str)
        assert isinstance(api_call.timestamp, datetime)
        assert api_call.provider == LLMProvider.OPENAI
        assert api_call.model == "gpt-3.5-turbo"
        assert api_call.input_tokens == 100
        assert api_call.output_tokens == 50
        assert api_call.total_tokens == 0  # Not calculated automatically
        assert api_call.estimated_cost == Decimal('0.00')
        assert api_call.success is True

    def test_api_call_creation_with_custom_values(self):
        """Test LLMAPICall creation with custom values."""
        custom_time = datetime.now()
        api_call = LLMAPICall(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-opus",
            input_tokens=200,
            output_tokens=100,
            total_tokens=300,
            estimated_cost=Decimal('4.50'),
            response_time_ms=1500.0,
            success=False,
            error_type="rate_limit",
            user_id="user123",
            correlation_id="req456"
        )

        assert api_call.provider == LLMProvider.ANTHROPIC
        assert api_call.model == "claude-3-opus"
        assert api_call.total_tokens == 300
        assert api_call.estimated_cost == Decimal('4.50')
        assert api_call.success is False
        assert api_call.error_type == "rate_limit"
        assert api_call.user_id == "user123"


class TestLLMCostTrackerInitialization:
    """Test LLMCostTracker initialization."""

    def test_cost_tracker_initialization(self, observatory_config):
        """Test proper initialization of LLMCostTracker."""
        tracker = LLMCostTracker(observatory_config)

        assert tracker.module_id == "llm_cost_tracker"
        assert tracker._config == observatory_config
        assert tracker._running is False
        assert tracker._api_calls == []
        assert tracker._daily_costs == {}
        assert tracker._provider_costs == {}
        assert tracker._model_costs == {}
        assert tracker._calls_tracked == 0
        assert tracker._anomalies_detected == 0
        assert len(tracker._pricing_db) > 0

    def test_pricing_database_initialization(self, observatory_config):
        """Test that pricing database is properly initialized."""
        tracker = LLMCostTracker(observatory_config)

        # Check OpenAI models
        assert "openai:gpt-4" in tracker._pricing_db
        assert "openai:gpt-3.5-turbo" in tracker._pricing_db

        gpt4_pricing = tracker._pricing_db["openai:gpt-4"]
        assert gpt4_pricing.provider == LLMProvider.OPENAI
        assert gpt4_pricing.model == "gpt-4"
        assert gpt4_pricing.input_cost_per_1k_tokens == Decimal('0.03')
        assert gpt4_pricing.output_cost_per_1k_tokens == Decimal('0.06')

        # Check Anthropic models
        assert "anthropic:claude-3-opus" in tracker._pricing_db
        assert "anthropic:claude-3-sonnet" in tracker._pricing_db

        # Check Google models
        assert "google:gemini-pro" in tracker._pricing_db

        # Verify total count
        assert len(tracker._pricing_db) >= 15  # Should have multiple providers

    def test_cost_thresholds_loading(self, observatory_config):
        """Test that cost thresholds are properly loaded."""
        tracker = LLMCostTracker(observatory_config)

        assert tracker._cost_thresholds == observatory_config.cost_config.cost_alert_thresholds
        assert 'daily_limit' in tracker._cost_thresholds
        assert 'hourly_limit' in tracker._cost_thresholds


class TestLLMCostTrackerLifecycle:
    """Test LLMCostTracker lifecycle management."""

    @pytest.mark.asyncio
    async def test_start_tracking_success(self, observatory_config, mock_redis):
        """Test successful start of cost tracking."""
        tracker = LLMCostTracker(observatory_config)

        with patch('redis.asyncio.Redis', return_value=mock_redis):
            result = await tracker.start_tracking()

            assert result is True
            assert tracker._running is True
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_tracking_already_running(self, cost_tracker):
        """Test starting tracker when already running."""
        # Already started in fixture
        result = await cost_tracker.start_tracking()

        assert result is True
        assert cost_tracker._running is True

    @pytest.mark.asyncio
    async def test_start_tracking_redis_failure(self, observatory_config):
        """Test handling of Redis connection failure."""
        tracker = LLMCostTracker(observatory_config)

        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Redis connection failed")

        with patch('redis.asyncio.Redis', return_value=mock_redis):
            result = await tracker.start_tracking()

            assert result is False
            assert tracker._running is False

    @pytest.mark.asyncio
    async def test_stop_tracking(self, cost_tracker):
        """Test graceful stopping of cost tracking."""
        assert cost_tracker._running is True

        await cost_tracker.stop_tracking()

        assert cost_tracker._running is False
        cost_tracker._redis_client.close.assert_called_once()


class TestCostCalculation:
    """Test cost calculation functionality."""

    def test_calculate_cost_openai_gpt4(self, cost_tracker):
        """Test cost calculation for OpenAI GPT-4."""
        cost = cost_tracker._calculate_cost(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500
        )

        # Expected: (1000/1000 * 0.03) + (500/1000 * 0.06) = 0.03 + 0.03 = 0.06
        expected = Decimal('0.0600')
        assert cost == expected

    def test_calculate_cost_anthropic_claude_opus(self, cost_tracker):
        """Test cost calculation for Anthropic Claude Opus."""
        cost = cost_tracker._calculate_cost(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-opus",
            input_tokens=2000,
            output_tokens=1000
        )

        # Expected: (2000/1000 * 0.015) + (1000/1000 * 0.075) = 0.03 + 0.075 = 0.105
        expected = Decimal('0.1050')
        assert cost == expected

    def test_calculate_cost_unknown_model(self, cost_tracker):
        """Test cost calculation for unknown model falls back to default."""
        cost = cost_tracker._calculate_cost(
            provider=LLMProvider.OPENAI,
            model="unknown-model",
            input_tokens=1000,
            output_tokens=500
        )

        # Should fall back to gpt-3.5-turbo pricing
        # Expected: (1000/1000 * 0.0015) + (500/1000 * 0.002) = 0.0015 + 0.001 = 0.0025
        expected = Decimal('0.0025')
        assert cost == expected

    def test_calculate_cost_zero_tokens(self, cost_tracker):
        """Test cost calculation with zero tokens."""
        cost = cost_tracker._calculate_cost(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            input_tokens=0,
            output_tokens=0
        )

        assert cost == Decimal('0.0000')

    def test_calculate_cost_precision_rounding(self, cost_tracker):
        """Test cost calculation rounding to 4 decimal places."""
        cost = cost_tracker._calculate_cost(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            input_tokens=333,  # Should result in precise decimal
            output_tokens=167
        )

        # Verify rounding to 4 decimal places
        assert len(str(cost).split('.')[-1]) <= 4


class TestAPICallTracking:
    """Test API call tracking functionality."""

    @pytest.mark.asyncio
    async def test_track_api_call_success(self, cost_tracker):
        """Test successful API call tracking."""
        api_call = await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
            response_time_ms=1200.0,
            user_id="user123",
            correlation_id="req456"
        )

        assert api_call.provider == LLMProvider.OPENAI
        assert api_call.model == "gpt-4"
        assert api_call.input_tokens == 1000
        assert api_call.output_tokens == 500
        assert api_call.total_tokens == 1500
        assert api_call.estimated_cost == Decimal('0.0600')
        assert api_call.response_time_ms == 1200.0
        assert api_call.success is True
        assert api_call.user_id == "user123"
        assert api_call.correlation_id == "req456"

        # Verify tracking stats updated
        assert cost_tracker._calls_tracked == 1
        assert len(cost_tracker._api_calls) == 1

    @pytest.mark.asyncio
    async def test_track_api_call_unknown_provider(self, cost_tracker):
        """Test tracking with unknown provider defaults to OpenAI."""
        api_call = await cost_tracker.track_api_call(
            provider="unknown_provider",
            model="some-model",
            input_tokens=100,
            output_tokens=50,
            response_time_ms=800.0
        )

        assert api_call.provider == LLMProvider.OPENAI  # Should default to OpenAI

    @pytest.mark.asyncio
    async def test_track_api_call_with_error(self, cost_tracker):
        """Test tracking API call with error."""
        api_call = await cost_tracker.track_api_call(
            provider="anthropic",
            model="claude-3-sonnet",
            input_tokens=500,
            output_tokens=0,  # No output due to error
            response_time_ms=100.0,
            success=False,
            error_type="rate_limit"
        )

        assert api_call.success is False
        assert api_call.error_type == "rate_limit"
        assert api_call.estimated_cost > Decimal('0.0000')  # Still calculated

    @pytest.mark.asyncio
    async def test_track_multiple_api_calls(self, cost_tracker):
        """Test tracking multiple API calls and aggregation."""
        # Track several calls
        for i in range(5):
            await cost_tracker.track_api_call(
                provider="openai",
                model="gpt-3.5-turbo",
                input_tokens=100 + i * 10,
                output_tokens=50 + i * 5,
                response_time_ms=800.0 + i * 100
            )

        assert cost_tracker._calls_tracked == 5
        assert len(cost_tracker._api_calls) == 5

        # Check cost aggregations
        today = datetime.now().strftime('%Y-%m-%d')
        assert today in cost_tracker._daily_costs
        assert cost_tracker._daily_costs[today] > Decimal('0.0000')

        assert LLMProvider.OPENAI in cost_tracker._provider_costs
        assert "openai:gpt-3.5-turbo" in cost_tracker._model_costs


class TestCostAggregation:
    """Test cost aggregation functionality."""

    @pytest.mark.asyncio
    async def test_cost_aggregation_by_date(self, cost_tracker):
        """Test cost aggregation by date."""
        # Create calls for today and yesterday
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        # Mock timestamp for yesterday's call
        api_call_yesterday = LLMAPICall(
            timestamp=yesterday,
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
            estimated_cost=Decimal('0.0600')
        )

        await cost_tracker._update_cost_aggregations(api_call_yesterday)

        # Today's call
        await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-4",
            input_tokens=500,
            output_tokens=250,
            response_time_ms=1000.0
        )

        # Check daily costs
        today_key = today.strftime('%Y-%m-%d')
        yesterday_key = yesterday.strftime('%Y-%m-%d')

        assert today_key in cost_tracker._daily_costs
        assert yesterday_key in cost_tracker._daily_costs
        assert cost_tracker._daily_costs[yesterday_key] == Decimal('0.0600')

    @pytest.mark.asyncio
    async def test_cost_aggregation_by_provider(self, cost_tracker):
        """Test cost aggregation by provider."""
        # OpenAI call
        await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
            response_time_ms=1000.0
        )

        # Anthropic call
        await cost_tracker.track_api_call(
            provider="anthropic",
            model="claude-3-sonnet",
            input_tokens=1000,
            output_tokens=500,
            response_time_ms=1200.0
        )

        # Check provider costs
        assert LLMProvider.OPENAI in cost_tracker._provider_costs
        assert LLMProvider.ANTHROPIC in cost_tracker._provider_costs
        assert cost_tracker._provider_costs[LLMProvider.OPENAI] == Decimal('0.0600')
        assert cost_tracker._provider_costs[LLMProvider.ANTHROPIC] == Decimal('0.0405')

    @pytest.mark.asyncio
    async def test_cost_aggregation_by_model(self, cost_tracker):
        """Test cost aggregation by model."""
        # GPT-4 calls
        await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-4",
            input_tokens=500,
            output_tokens=250,
            response_time_ms=1000.0
        )
        await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-4",
            input_tokens=300,
            output_tokens=150,
            response_time_ms=800.0
        )

        # GPT-3.5 call
        await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-3.5-turbo",
            input_tokens=1000,
            output_tokens=500,
            response_time_ms=600.0
        )

        # Check model costs
        assert "openai:gpt-4" in cost_tracker._model_costs
        assert "openai:gpt-3.5-turbo" in cost_tracker._model_costs

        # GPT-4 should have combined cost from both calls
        gpt4_cost = cost_tracker._model_costs["openai:gpt-4"]
        assert gpt4_cost == Decimal('0.0390')  # (500+300)/1000*0.03 + (250+150)/1000*0.06


class TestAnomalyDetection:
    """Test cost anomaly detection."""

    @pytest.mark.asyncio
    async def test_high_cost_single_call_anomaly(self, cost_tracker):
        """Test detection of high-cost single call anomaly."""
        # Track a very expensive call
        api_call = await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-4",
            input_tokens=50000,  # Very high token count
            output_tokens=25000,
            response_time_ms=30000.0
        )

        # Should detect anomaly (cost > $1.00)
        assert api_call.estimated_cost > Decimal('1.00')
        assert cost_tracker._anomalies_detected == 1

    @pytest.mark.asyncio
    async def test_daily_cost_threshold_alert(self, cost_tracker):
        """Test daily cost threshold alert."""
        # Make many expensive calls to exceed daily threshold
        for i in range(10):
            await cost_tracker.track_api_call(
                provider="openai",
                model="gpt-4",
                input_tokens=10000,
                output_tokens=5000,
                response_time_ms=2000.0
            )

        # Check that daily cost exceeds threshold
        today = datetime.now().strftime('%Y-%m-%d')
        daily_cost = cost_tracker._daily_costs[today]
        assert daily_cost > Decimal('1.00')  # Should exceed some thresholds

    @pytest.mark.asyncio
    async def test_no_anomaly_normal_calls(self, cost_tracker):
        """Test that normal calls don't trigger anomalies."""
        # Make normal, inexpensive calls
        for i in range(5):
            await cost_tracker.track_api_call(
                provider="openai",
                model="gpt-3.5-turbo",
                input_tokens=100,
                output_tokens=50,
                response_time_ms=500.0
            )

        # Should not detect anomalies
        assert cost_tracker._anomalies_detected == 0


class TestCostMetrics:
    """Test cost metrics generation."""

    @pytest.mark.asyncio
    async def test_get_cost_metrics_empty(self, cost_tracker):
        """Test cost metrics with no tracked calls."""
        metrics = cost_tracker.get_cost_metrics()

        assert isinstance(metrics, CostMetrics)
        assert metrics.total_cost_today == Decimal('0.00')
        assert metrics.cost_by_provider == {}
        assert metrics.cost_by_model == {}
        assert metrics.projected_monthly_cost == Decimal('0.00')
        assert metrics.cost_trend == CostTrend.STABLE

    @pytest.mark.asyncio
    async def test_get_cost_metrics_with_data(self, cost_tracker):
        """Test cost metrics with tracked calls."""
        # Track some calls
        await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
            response_time_ms=1200.0
        )
        await cost_tracker.track_api_call(
            provider="anthropic",
            model="claude-3-sonnet",
            input_tokens=800,
            output_tokens=400,
            response_time_ms=1000.0
        )

        metrics = cost_tracker.get_cost_metrics()

        assert metrics.total_cost_today > Decimal('0.00')
        assert 'openai' in metrics.cost_by_provider
        assert 'anthropic' in metrics.cost_by_provider
        assert 'openai:gpt-4' in metrics.cost_by_model
        assert 'anthropic:claude-3-sonnet' in metrics.cost_by_model
        assert metrics.projected_monthly_cost > Decimal('0.00')

    @pytest.mark.asyncio
    async def test_cost_trend_calculation(self, cost_tracker):
        """Test cost trend calculation with historical data."""
        # Add some historical daily costs
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')

        cost_tracker._daily_costs[yesterday] = Decimal('10.00')
        cost_tracker._daily_costs[today] = Decimal('15.00')

        metrics = cost_tracker.get_cost_metrics()

        # Cost increased from 10 to 15 (50% increase > 20% threshold)
        assert metrics.cost_trend == CostTrend.INCREASING


class TestTrackingStatistics:
    """Test tracking statistics and performance metrics."""

    @pytest.mark.asyncio
    async def test_get_tracking_stats_initial(self, cost_tracker):
        """Test tracking statistics when just started."""
        stats = cost_tracker.get_tracking_stats()

        assert stats["uptime_seconds"] > 0
        assert stats["calls_tracked"] == 0
        assert stats["anomalies_detected"] == 0
        assert stats["tracking_rate_per_second"] == 0
        assert len(stats["supported_providers"]) > 0
        assert stats["pricing_models"] > 0
        assert stats["daily_costs_tracked"] == 0
        assert stats["total_cost_today"] == 0.0

    @pytest.mark.asyncio
    async def test_get_tracking_stats_with_data(self, cost_tracker):
        """Test tracking statistics with tracked calls."""
        # Track multiple calls
        for i in range(3):
            await cost_tracker.track_api_call(
                provider="openai",
                model="gpt-3.5-turbo",
                input_tokens=100,
                output_tokens=50,
                response_time_ms=500.0
            )

        stats = cost_tracker.get_tracking_stats()

        assert stats["calls_tracked"] == 3
        assert stats["tracking_rate_per_second"] > 0
        assert stats["daily_costs_tracked"] == 1  # Today
        assert stats["total_cost_today"] > 0
        assert "openai" in stats["provider_costs"]


class TestRedisStreaming:
    """Test Redis streaming functionality."""

    @pytest.mark.asyncio
    async def test_stream_api_call_to_redis(self, cost_tracker):
        """Test streaming API call to Redis."""
        api_call = LLMAPICall(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-opus",
            input_tokens=1000,
            output_tokens=500,
            estimated_cost=Decimal('1.8750'),
            response_time_ms=1500.0,
            success=True,
            user_id="user123"
        )

        await cost_tracker._stream_api_call_to_redis(api_call)

        # Verify Redis stream was called
        cost_tracker._redis_client.xadd.assert_called_once()
        call_args = cost_tracker._redis_client.xadd.call_args

        stream_name = call_args[0][0]
        stream_data = call_args[0][1]

        assert stream_name.endswith(":llm_costs")
        assert stream_data["provider"] == "anthropic"
        assert stream_data["model"] == "claude-3-opus"
        assert stream_data["input_tokens"] == "1000"
        assert stream_data["estimated_cost"] == "1.8750"
        assert stream_data["user_id"] == "user123"

    @pytest.mark.asyncio
    async def test_stream_api_call_redis_failure(self, cost_tracker):
        """Test handling Redis streaming failure."""
        # Make Redis throw an exception
        cost_tracker._redis_client.xadd.side_effect = Exception("Redis error")

        api_call = LLMAPICall()

        # Should not raise exception
        await cost_tracker._stream_api_call_to_redis(api_call)

    @pytest.mark.asyncio
    async def test_stream_api_call_no_redis(self, observatory_config):
        """Test streaming when Redis is not connected."""
        tracker = LLMCostTracker(observatory_config)
        # Don't start tracking (no Redis connection)

        api_call = LLMAPICall()

        # Should not raise exception
        await tracker._stream_api_call_to_redis(api_call)


class TestReflectiveModuleInterface:
    """Test ReflectiveModule interface implementation."""

    def test_get_capabilities(self, cost_tracker):
        """Test getting module capabilities."""
        capabilities = cost_tracker.get_capabilities()

        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        assert ModuleCapability.MONITORING in capabilities
        assert ModuleCapability.DATA_PROCESSING in capabilities
        assert ModuleCapability.COST_TRACKING in capabilities

    def test_get_module_info(self, cost_tracker):
        """Test getting module information."""
        module_info = cost_tracker.get_module_info()

        assert module_info["module_id"] == "llm_cost_tracker"
        assert module_info["name"] == "LLM Cost Tracker"
        assert module_info["version"] == "1.0.0"
        assert "supported_providers" in module_info["config"]
        assert "pricing_models" in module_info["config"]

    @pytest.mark.asyncio
    async def test_graceful_degradation_redis_error(self, cost_tracker):
        """Test graceful degradation for Redis errors."""
        redis_error = Exception("Redis connection lost")

        result = await cost_tracker.graceful_degradation(redis_error)
        assert result is True

    @pytest.mark.asyncio
    async def test_graceful_degradation_other_error(self, cost_tracker):
        """Test graceful degradation for other errors."""
        other_error = Exception("Some other error")

        result = await cost_tracker.graceful_degradation(other_error)
        assert result is False

    def test_get_health_status_healthy(self, cost_tracker):
        """Test health status when running and healthy."""
        health = cost_tracker.get_health_status()

        from src.rm_ddd.core.unified_reflective_module import ModuleStatus
        assert health.module_id == "llm_cost_tracker"
        assert health.status == ModuleStatus.HEALTHY
        assert health.health_score == 1.0
        assert len(health.issues) == 0

    def test_get_health_status_not_running(self, observatory_config):
        """Test health status when not running."""
        tracker = LLMCostTracker(observatory_config)
        # Don't start tracking

        health = tracker.get_health_status()

        from src.rm_ddd.core.unified_reflective_module import ModuleStatus
        assert health.status == ModuleStatus.ERROR
        assert health.health_score == 0.0
        assert "not running" in health.issues[0]

    @pytest.mark.asyncio
    async def test_get_metrics(self, cost_tracker):
        """Test getting current metrics."""
        # Track a call first
        await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-3.5-turbo",
            input_tokens=100,
            output_tokens=50,
            response_time_ms=500.0
        )

        metrics = await cost_tracker.get_metrics()

        assert "tracking_stats" in metrics
        assert "cost_metrics" in metrics
        assert "running" in metrics
        assert metrics["running"] is True
        assert metrics["tracking_stats"]["calls_tracked"] == 1


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_track_api_call_calculation_error(self, cost_tracker, monkeypatch):
        """Test handling of cost calculation errors."""
        # Mock _calculate_cost to raise exception
        def mock_calculate_cost(*args, **kwargs):
            raise Exception("Calculation error")

        monkeypatch.setattr(cost_tracker, '_calculate_cost', mock_calculate_cost)

        api_call = await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            response_time_ms=500.0
        )

        # Should return error call record
        assert api_call.success is False
        assert "error" in api_call.error_type.lower()

    @pytest.mark.asyncio
    async def test_extreme_token_counts(self, cost_tracker):
        """Test handling of extreme token counts."""
        # Very large token count
        api_call = await cost_tracker.track_api_call(
            provider="openai",
            model="gpt-4",
            input_tokens=1000000,
            output_tokens=500000,
            response_time_ms=60000.0
        )

        assert api_call.success is True
        assert api_call.estimated_cost > Decimal('100.00')  # Should be very expensive
        assert cost_tracker._anomalies_detected > 0  # Should trigger anomaly

    def test_invalid_provider_enum(self, cost_tracker):
        """Test cost calculation with invalid provider enum."""
        # This should be handled by the enum validation in track_api_call
        cost = cost_tracker._calculate_cost(
            provider=None,  # Invalid
            model="some-model",
            input_tokens=100,
            output_tokens=50
        )

        # Should handle gracefully and return 0 cost
        assert cost == Decimal('0.00')

    @pytest.mark.asyncio
    async def test_concurrent_api_call_tracking(self, cost_tracker):
        """Test concurrent API call tracking."""
        # Create concurrent tracking tasks
        tasks = []
        for i in range(10):
            task = cost_tracker.track_api_call(
                provider="openai",
                model="gpt-3.5-turbo",
                input_tokens=100 + i,
                output_tokens=50 + i,
                response_time_ms=500.0,
                correlation_id=f"concurrent-{i}"
            )
            tasks.append(task)

        # Wait for all to complete
        api_calls = await asyncio.gather(*tasks)

        assert len(api_calls) == 10
        assert cost_tracker._calls_tracked == 10

        # All should be successful and have different correlation IDs
        for i, api_call in enumerate(api_calls):
            assert api_call.success is True
            assert api_call.correlation_id == f"concurrent-{i}"