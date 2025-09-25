"""
Unit tests for Observatory Context Provider

Tests monitoring data extraction, formatting, and brownfield safety.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.beast_mode.observatory.ai_consultation.observatory_context_provider import (
    ObservatoryContextProvider,
    MetricData,
    AlertData,
    SystemStatus,
    DataSensitivity,
    MetricType,
    observatory_context_provider,
    get_observatory_context,
    initialize_context_provider,
    cleanup_context_provider
)
from src.beast_mode.observatory.ai_consultation.models import ObservatoryContext
from src.beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag
from src.beast_mode.observatory.ai_consultation.exceptions import ContextUnavailableError
from src.beast_mode.observatory.ai_consultation.health_checker import ComponentHealth


class TestObservatoryContextProvider:
    """Test ObservatoryContextProvider class"""
    
    @pytest.fixture
    async def context_provider(self):
        """Create test context provider instance"""
        provider = ObservatoryContextProvider(
            cache_ttl=60,
            max_metrics=10,
            max_alerts=5,
            max_context_tokens=1000,
            observatory_timeout=5
        )
        
        # Enable feature flags
        await feature_flags.set_flag(FeatureFlag.OBSERVATORY_CONTEXT.value, True)
        await feature_flags.set_flag(FeatureFlag.METRICS_ACCESS.value, True)
        await feature_flags.set_flag(FeatureFlag.ALERTS_ACCESS.value, True)
        
        yield provider
        
        # Cleanup
        await provider.cleanup()
    
    @pytest.mark.asyncio
    async def test_initialization(self, context_provider):
        """Test context provider initialization"""
        await context_provider.initialize()
        
        # Should have detected endpoints
        assert len(context_provider._observatory_endpoints) > 0
        assert 'metrics' in context_provider._observatory_endpoints
        assert 'alerts' in context_provider._observatory_endpoints
        assert 'status' in context_provider._observatory_endpoints
    
    @pytest.mark.asyncio
    async def test_get_current_metrics(self, context_provider):
        """Test getting current metrics"""
        await context_provider.initialize()
        
        # Get metrics
        metrics = await context_provider.get_current_metrics()
        
        assert isinstance(metrics, list)
        assert len(metrics) > 0
        
        # Check metric structure
        for metric in metrics:
            assert isinstance(metric, MetricData)
            assert metric.name
            assert metric.value is not None
            assert isinstance(metric.metric_type, MetricType)
            assert isinstance(metric.timestamp, datetime)
            assert isinstance(metric.labels, dict)
            assert isinstance(metric.sensitivity, DataSensitivity)
    
    @pytest.mark.asyncio
    async def test_get_current_alerts(self, context_provider):
        """Test getting current alerts"""
        await context_provider.initialize()
        
        # Get alerts
        alerts = await context_provider.get_current_alerts()
        
        assert isinstance(alerts, list)
        assert len(alerts) > 0
        
        # Check alert structure
        for alert in alerts:
            assert isinstance(alert, AlertData)
            assert alert.name
            assert alert.status in ["firing", "resolved", "pending"]
            assert alert.severity in ["critical", "warning", "info"]
            assert alert.message
            assert isinstance(alert.timestamp, datetime)
            assert isinstance(alert.labels, dict)
            assert isinstance(alert.sensitivity, DataSensitivity)
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, context_provider):
        """Test getting system status"""
        await context_provider.initialize()
        
        # Get system status
        status = await context_provider.get_system_status()
        
        assert isinstance(status, SystemStatus)
        assert status.overall_health in ["healthy", "degraded", "unhealthy"]
        assert status.active_alerts >= 0
        assert status.critical_alerts >= 0
        assert status.warning_alerts >= 0
        assert status.services_up >= 0
        assert status.services_total > 0
        assert isinstance(status.last_updated, datetime)
    
    @pytest.mark.asyncio
    async def test_caching_mechanism(self, context_provider):
        """Test caching mechanism for performance"""
        await context_provider.initialize()
        
        # First call should miss cache
        metrics1 = await context_provider.get_current_metrics()
        assert context_provider._stats['cache_misses'] >= 1
        
        # Second call should hit cache
        metrics2 = await context_provider.get_current_metrics()
        assert context_provider._stats['cache_hits'] >= 1
        
        # Results should be the same
        assert len(metrics1) == len(metrics2)
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, context_provider):
        """Test cache expiration"""
        # Set very short cache TTL
        context_provider.cache_ttl = 1  # 1 second
        await context_provider.initialize()
        
        # Get metrics
        await context_provider.get_current_metrics()
        
        # Wait for cache to expire
        await asyncio.sleep(1.1)
        
        # Next call should miss cache
        cache_misses_before = context_provider._stats['cache_misses']
        await context_provider.get_current_metrics()
        assert context_provider._stats['cache_misses'] > cache_misses_before
    
    @pytest.mark.asyncio
    async def test_metric_filtering_by_names(self, context_provider):
        """Test filtering metrics by names"""
        await context_provider.initialize()
        
        # Get specific metrics
        specific_metrics = await context_provider.get_current_metrics(
            metric_names=["cpu_usage_percent", "memory_usage_bytes"]
        )
        
        # Should only return requested metrics
        metric_names = [m.name for m in specific_metrics]
        assert "cpu_usage_percent" in metric_names
        assert "memory_usage_bytes" in metric_names
        
        # Should not contain other metrics
        assert len([m for m in specific_metrics if m.name not in ["cpu_usage_percent", "memory_usage_bytes"]]) == 0
    
    @pytest.mark.asyncio
    async def test_alert_filtering_by_severity(self, context_provider):
        """Test filtering alerts by severity"""
        await context_provider.initialize()
        
        # Get only critical alerts
        critical_alerts = await context_provider.get_current_alerts(
            severity_filter=["critical"]
        )
        
        # Should only return critical alerts
        for alert in critical_alerts:
            assert alert.severity == "critical"
    
    @pytest.mark.asyncio
    async def test_data_sensitivity_filtering(self, context_provider):
        """Test data filtering by sensitivity level"""
        await context_provider.initialize()
        
        # Get metrics
        metrics = await context_provider.get_current_metrics()
        
        # Filter by public sensitivity
        public_metrics = context_provider._filter_by_sensitivity(metrics, DataSensitivity.PUBLIC)
        
        # Should only contain public metrics
        for metric in public_metrics:
            assert metric.sensitivity in [DataSensitivity.PUBLIC]
        
        # Filter by internal sensitivity
        internal_metrics = context_provider._filter_by_sensitivity(metrics, DataSensitivity.INTERNAL)
        
        # Should contain public and internal metrics
        for metric in internal_metrics:
            assert metric.sensitivity in [DataSensitivity.PUBLIC, DataSensitivity.INTERNAL]
    
    @pytest.mark.asyncio
    async def test_data_sanitization(self, context_provider):
        """Test data sanitization for sensitive information"""
        # Create metric with sensitive data
        sensitive_metric = MetricData(
            name="api_key_usage",
            value=100,
            metric_type=MetricType.COUNTER,
            timestamp=datetime.utcnow(),
            labels={"password": "secret123", "api_key": "abc123"},
            description="API key usage with password authentication"
        )
        
        # Sanitize the metric
        sanitized = context_provider._sanitize_data(sensitive_metric)
        
        # Sensitive information should be redacted
        assert "[REDACTED]" in sanitized.name
        assert "[REDACTED]" in sanitized.description
        assert "[REDACTED]" in sanitized.labels["password"]
        assert "[REDACTED]" in sanitized.labels["api_key"]
    
    @pytest.mark.asyncio
    async def test_get_observatory_context_complete(self, context_provider):
        """Test getting complete Observatory context"""
        await context_provider.initialize()
        
        # Get complete context
        context = await context_provider.get_observatory_context(
            user_id="test_user",
            include_metrics=True,
            include_alerts=True,
            include_status=True,
            sensitivity_level=DataSensitivity.INTERNAL
        )
        
        assert isinstance(context, ObservatoryContext)
        assert context.timestamp
        assert context.system_status
        assert context.active_alerts >= 0
        assert context.critical_alerts >= 0
        assert isinstance(context.metrics_summary, dict)
        assert isinstance(context.alerts_summary, dict)
        assert context.formatted_context
        assert len(context.formatted_context) > 0
    
    @pytest.mark.asyncio
    async def test_llm_formatting(self, context_provider):
        """Test LLM-optimized formatting"""
        await context_provider.initialize()
        
        # Get metrics and alerts
        metrics = await context_provider.get_current_metrics()
        alerts = await context_provider.get_current_alerts()
        status = await context_provider.get_system_status()
        
        # Format for LLM
        formatted = await context_provider._format_for_llm(
            metrics, alerts, status, DataSensitivity.INTERNAL
        )
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
        
        # Should contain key information
        if status.overall_health != "healthy":
            assert status.overall_health.upper() in formatted
        
        # Should contain critical alerts if any
        critical_alerts = [a for a in alerts if a.severity == "critical" and a.status == "firing"]
        if critical_alerts:
            assert "CRITICAL ALERTS" in formatted
    
    @pytest.mark.asyncio
    async def test_token_optimization(self, context_provider):
        """Test token optimization for LLM context"""
        # Set very low token limit
        context_provider.max_context_tokens = 100
        await context_provider.initialize()
        
        # Get context
        context = await context_provider.get_observatory_context("test_user")
        
        # Formatted context should be truncated if too long
        if len(context.formatted_context) > 400:  # Rough token estimation
            assert "[truncated]" in context.formatted_context
    
    @pytest.mark.asyncio
    async def test_feature_flag_integration(self, context_provider):
        """Test feature flag integration"""
        await context_provider.initialize()
        
        # Disable Observatory context
        await feature_flags.set_flag(FeatureFlag.OBSERVATORY_CONTEXT.value, False)
        
        # Should raise exception
        with pytest.raises(ContextUnavailableError):
            await context_provider.get_observatory_context("test_user")
        
        # Re-enable and disable metrics access
        await feature_flags.set_flag(FeatureFlag.OBSERVATORY_CONTEXT.value, True)
        await feature_flags.set_flag(FeatureFlag.METRICS_ACCESS.value, False)
        
        # Should get context without metrics
        context = await context_provider.get_observatory_context("test_user")
        assert context.metrics_summary["count"] == 0
    
    @pytest.mark.asyncio
    async def test_observatory_unavailable(self, context_provider):
        """Test behavior when Observatory is unavailable"""
        # Force Observatory unavailable
        context_provider._observatory_available = False
        await context_provider.initialize()
        
        # Should return empty results gracefully
        metrics = await context_provider.get_current_metrics()
        alerts = await context_provider.get_current_alerts()
        
        assert metrics == []
        assert alerts == []
        
        # System status should indicate degraded state
        status = await context_provider.get_system_status()
        assert status.overall_health == "degraded"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, context_provider):
        """Test circuit breaker integration"""
        await context_provider.initialize()
        
        # Mock circuit breaker failure
        with patch('src.beast_mode.observatory.ai_consultation.observatory_context_provider.with_circuit_breaker') as mock_cb:
            mock_cb.side_effect = Exception("Circuit breaker open")
            
            # Should handle circuit breaker gracefully
            metrics = await context_provider.get_current_metrics()
            assert metrics == []  # Should return empty on failure
    
    @pytest.mark.asyncio
    async def test_metrics_summary_generation(self, context_provider):
        """Test metrics summary generation"""
        # Create test metrics
        test_metrics = [
            MetricData(
                name="cpu_usage",
                value=75.0,
                metric_type=MetricType.GAUGE,
                timestamp=datetime.utcnow(),
                labels={},
                unit="percent"
            ),
            MetricData(
                name="memory_usage",
                value=2048,
                metric_type=MetricType.GAUGE,
                timestamp=datetime.utcnow(),
                labels={},
                unit="MB"
            ),
            MetricData(
                name="requests_total",
                value=1000,
                metric_type=MetricType.COUNTER,
                timestamp=datetime.utcnow(),
                labels={},
                unit="requests"
            )
        ]
        
        # Generate summary
        summary = context_provider._summarize_metrics(test_metrics)
        
        assert summary["count"] == 3
        assert "gauge" in summary["types"]
        assert "counter" in summary["types"]
        assert "latest_timestamp" in summary
        assert "by_type" in summary
        assert len(summary["by_type"]["gauge"]) == 2
        assert len(summary["by_type"]["counter"]) == 1
    
    @pytest.mark.asyncio
    async def test_alerts_summary_generation(self, context_provider):
        """Test alerts summary generation"""
        # Create test alerts
        test_alerts = [
            AlertData(
                name="HighCPU",
                status="firing",
                severity="critical",
                message="CPU high",
                timestamp=datetime.utcnow(),
                labels={}
            ),
            AlertData(
                name="HighMemory",
                status="firing",
                severity="warning",
                message="Memory high",
                timestamp=datetime.utcnow(),
                labels={}
            ),
            AlertData(
                name="DiskSpace",
                status="resolved",
                severity="warning",
                message="Disk space low",
                timestamp=datetime.utcnow(),
                labels={}
            )
        ]
        
        # Generate summary
        summary = context_provider._summarize_alerts(test_alerts)
        
        assert summary["count"] == 3
        assert summary["firing"] == 2
        assert summary["critical"] == 1
        assert summary["warning"] == 2
        assert "latest_timestamp" in summary
    
    @pytest.mark.asyncio
    async def test_cache_clearing(self, context_provider):
        """Test cache clearing functionality"""
        await context_provider.initialize()
        
        # Populate cache
        await context_provider.get_current_metrics()
        await context_provider.get_current_alerts()
        
        # Verify cache has data
        assert len(context_provider._cache_timestamps) > 0
        
        # Clear cache
        await context_provider.clear_cache()
        
        # Verify cache is empty
        assert len(context_provider._cache_timestamps) == 0
        assert len(context_provider._metrics_cache) == 0
        assert len(context_provider._alerts_cache) == 0
        assert context_provider._system_status_cache is None
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, context_provider):
        """Test statistics tracking"""
        await context_provider.initialize()
        
        # Perform some operations
        await context_provider.get_current_metrics()
        await context_provider.get_current_alerts()
        await context_provider.get_observatory_context("test_user")
        
        # Check stats
        stats = await context_provider.get_stats()
        
        assert stats['context_requests'] > 0
        assert stats['observatory_calls'] >= 0
        assert 'observatory_available' in stats
        assert 'cache_size' in stats
        assert 'endpoints_configured' in stats
    
    @pytest.mark.asyncio
    async def test_health_check(self, context_provider):
        """Test health check functionality"""
        await context_provider.initialize()
        
        health = await context_provider.health_check()
        
        assert isinstance(health, ComponentHealth)
        assert health.component == "observatory_context_provider"
        assert health.status in ["healthy", "degraded", "unhealthy"]
        assert "observatory_available" in health.metadata
        assert "cache_hit_rate" in health.metadata
        assert "observatory_calls" in health.metadata
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, context_provider):
        """Test concurrent context operations"""
        await context_provider.initialize()
        
        # Run multiple operations concurrently
        tasks = [
            context_provider.get_current_metrics(),
            context_provider.get_current_alerts(),
            context_provider.get_system_status(),
            context_provider.get_observatory_context("user1"),
            context_provider.get_observatory_context("user2")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without exceptions
        for result in results:
            assert not isinstance(result, Exception)


class TestGlobalContextProvider:
    """Test global context provider functions"""
    
    @pytest.mark.asyncio
    async def test_global_functions(self):
        """Test global context provider functions"""
        with patch('src.beast_mode.observatory.ai_consultation.observatory_context_provider.observatory_context_provider') as mock_provider:
            mock_context = ObservatoryContext(
                timestamp=datetime.utcnow(),
                system_status="healthy",
                active_alerts=0,
                critical_alerts=0,
                metrics_summary={"count": 5},
                alerts_summary={"count": 2},
                formatted_context="Test context"
            )
            
            mock_provider.get_observatory_context = AsyncMock(return_value=mock_context)
            mock_provider.initialize = AsyncMock()
            mock_provider.cleanup = AsyncMock()
            
            # Test get_observatory_context
            context = await get_observatory_context("test_user")
            assert context.system_status == "healthy"
            mock_provider.get_observatory_context.assert_called_once()
            
            # Test initialize_context_provider
            await initialize_context_provider()
            mock_provider.initialize.assert_called_once()
            
            # Test cleanup_context_provider
            await cleanup_context_provider()
            mock_provider.cleanup.assert_called_once()


class TestDataStructures:
    """Test data structure classes"""
    
    def test_metric_data_creation(self):
        """Test MetricData creation"""
        metric = MetricData(
            name="test_metric",
            value=42.0,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.utcnow(),
            labels={"instance": "test"},
            unit="percent",
            description="Test metric",
            sensitivity=DataSensitivity.INTERNAL
        )
        
        assert metric.name == "test_metric"
        assert metric.value == 42.0
        assert metric.metric_type == MetricType.GAUGE
        assert metric.unit == "percent"
        assert metric.sensitivity == DataSensitivity.INTERNAL
    
    def test_alert_data_creation(self):
        """Test AlertData creation"""
        alert = AlertData(
            name="test_alert",
            status="firing",
            severity="critical",
            message="Test alert message",
            timestamp=datetime.utcnow(),
            labels={"service": "test"},
            duration=timedelta(minutes=5),
            sensitivity=DataSensitivity.INTERNAL
        )
        
        assert alert.name == "test_alert"
        assert alert.status == "firing"
        assert alert.severity == "critical"
        assert alert.message == "Test alert message"
        assert alert.duration == timedelta(minutes=5)
    
    def test_system_status_creation(self):
        """Test SystemStatus creation"""
        status = SystemStatus(
            overall_health="healthy",
            active_alerts=2,
            critical_alerts=0,
            warning_alerts=2,
            services_up=5,
            services_total=5,
            last_updated=datetime.utcnow()
        )
        
        assert status.overall_health == "healthy"
        assert status.active_alerts == 2
        assert status.services_up == 5
        assert status.services_total == 5


if __name__ == "__main__":
    pytest.main([__file__])