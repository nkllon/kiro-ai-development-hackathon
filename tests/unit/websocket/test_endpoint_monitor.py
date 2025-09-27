"""Unit tests for WebSocket endpoint monitor."""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import time

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.beast_mode.observatory.websocket.endpoint_monitor import (
    EndpointMonitor,
    MonitoringConfig,
    Alert
)
from src.beast_mode.observatory.websocket.health_validator import (
    HealthStatus,
    HealthCheckResult,
    QualityMetrics
)


class TestMonitoringConfig:
    """Test cases for MonitoringConfig."""
    
    def test_default_config(self):
        """Test default monitoring configuration."""
        config = MonitoringConfig()
        
        assert config.check_interval_seconds == 30.0
        assert config.health_check_timeout == 5.0
        assert config.max_consecutive_failures == 3
        assert config.alert_cooldown_seconds == 300.0
        assert config.enable_quality_metrics is True
        assert config.enable_failure_detection is True
        assert config.enable_alerts is True
    
    def test_custom_config(self):
        """Test custom monitoring configuration."""
        config = MonitoringConfig(
            check_interval_seconds=60.0,
            health_check_timeout=10.0,
            max_consecutive_failures=5,
            alert_cooldown_seconds=600.0,
            enable_quality_metrics=False,
            enable_failure_detection=False,
            enable_alerts=False
        )
        
        assert config.check_interval_seconds == 60.0
        assert config.health_check_timeout == 10.0
        assert config.max_consecutive_failures == 5
        assert config.alert_cooldown_seconds == 600.0
        assert config.enable_quality_metrics is False
        assert config.enable_failure_detection is False
        assert config.enable_alerts is False


class TestAlert:
    """Test cases for Alert dataclass."""
    
    def test_alert_creation(self):
        """Test Alert creation."""
        alert = Alert(
            endpoint='/ws/emoji-rain',
            alert_type='endpoint_unhealthy',
            severity='critical',
            message='Endpoint is unhealthy',
            metadata={'response_time_ms': 5000.0}
        )
        
        assert alert.endpoint == '/ws/emoji-rain'
        assert alert.alert_type == 'endpoint_unhealthy'
        assert alert.severity == 'critical'
        assert alert.message == 'Endpoint is unhealthy'
        assert alert.metadata['response_time_ms'] == 5000.0
        assert alert.resolved_at is None
        assert isinstance(alert.triggered_at, datetime)
    
    def test_alert_to_dict(self):
        """Test Alert to_dict method."""
        alert = Alert(
            endpoint='/ws/emoji-rain',
            alert_type='endpoint_unhealthy',
            severity='critical',
            message='Endpoint is unhealthy',
            metadata={'response_time_ms': 5000.0}
        )
        
        data = alert.to_dict()
        
        assert data["endpoint"] == '/ws/emoji-rain'
        assert data["alert_type"] == 'endpoint_unhealthy'
        assert data["severity"] == 'critical'
        assert data["message"] == 'Endpoint is unhealthy'
        assert data["metadata"]["response_time_ms"] == 5000.0
        assert data["resolved_at"] is None
        assert "triggered_at" in data


class TestEndpointMonitor:
    """Test cases for EndpointMonitor."""
    
    @pytest.fixture
    def monitor(self):
        """Create an EndpointMonitor instance for testing."""
        config = MonitoringConfig(
            check_interval_seconds=1.0,  # Short interval for testing
            health_check_timeout=1.0,
            max_consecutive_failures=2,
            alert_cooldown_seconds=60.0
        )
        return EndpointMonitor(config)
    
    def test_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.config.check_interval_seconds == 1.0
        assert monitor.config.health_check_timeout == 1.0
        assert monitor.config.max_consecutive_failures == 2
        assert monitor.config.alert_cooldown_seconds == 60.0
        assert monitor.health_validator is not None
        assert monitor._monitoring_active is False
        assert monitor._monitoring_task is None
        assert monitor._last_health_checks == {}
        assert monitor._active_alerts == {}
        assert monitor._alert_history == []
        assert monitor._quality_metrics_history == {}
        assert monitor._failure_history == {}
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, monitor):
        """Test starting monitoring."""
        with patch.object(monitor, '_monitoring_loop') as mock_loop:
            mock_loop.return_value = AsyncMock()
            
            await monitor.start_monitoring()
            
            assert monitor._monitoring_active is True
            assert monitor._monitoring_task is not None
    
    @pytest.mark.asyncio
    async def test_start_monitoring_already_active(self, monitor):
        """Test starting monitoring when already active."""
        monitor._monitoring_active = True
        
        await monitor.start_monitoring()
        
        # Should not create new task
        assert monitor._monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, monitor):
        """Test stopping monitoring."""
        monitor._monitoring_active = True
        monitor._monitoring_task = AsyncMock()
        
        await monitor.stop_monitoring()
        
        assert monitor._monitoring_active is False
        monitor._monitoring_task.cancel.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_not_active(self, monitor):
        """Test stopping monitoring when not active."""
        await monitor.stop_monitoring()
        
        # Should not raise exception
        assert monitor._monitoring_active is False
    
    @pytest.mark.asyncio
    async def test_get_endpoint_status(self, monitor):
        """Test getting endpoint status."""
        endpoint = '/ws/emoji-rain'
        result = HealthCheckResult(
            endpoint=endpoint,
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        
        monitor._last_health_checks[endpoint] = result
        
        status = await monitor.get_endpoint_status(endpoint)
        
        assert status == result
    
    @pytest.mark.asyncio
    async def test_get_endpoint_status_not_found(self, monitor):
        """Test getting endpoint status when not found."""
        endpoint = '/ws/nonexistent'
        
        status = await monitor.get_endpoint_status(endpoint)
        
        assert status is None
    
    @pytest.mark.asyncio
    async def test_get_all_endpoint_statuses(self, monitor):
        """Test getting all endpoint statuses."""
        endpoint1 = '/ws/emoji-rain'
        endpoint2 = '/ws/observatory'
        
        result1 = HealthCheckResult(
            endpoint=endpoint1,
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        result2 = HealthCheckResult(
            endpoint=endpoint2,
            status=HealthStatus.DEGRADED,
            response_time_ms=200.0
        )
        
        monitor._last_health_checks[endpoint1] = result1
        monitor._last_health_checks[endpoint2] = result2
        
        statuses = await monitor.get_all_endpoint_statuses()
        
        assert len(statuses) == 2
        assert statuses[endpoint1] == result1
        assert statuses[endpoint2] == result2
    
    @pytest.mark.asyncio
    async def test_get_active_alerts(self, monitor):
        """Test getting active alerts."""
        alert = Alert(
            endpoint='/ws/emoji-rain',
            alert_type='endpoint_unhealthy',
            severity='critical',
            message='Endpoint is unhealthy'
        )
        
        monitor._active_alerts['/ws/emoji-rain:endpoint_unhealthy'] = alert
        
        alerts = await monitor.get_active_alerts()
        
        assert len(alerts) == 1
        assert alerts[0] == alert
    
    @pytest.mark.asyncio
    async def test_get_alert_history(self, monitor):
        """Test getting alert history."""
        alert1 = Alert(
            endpoint='/ws/emoji-rain',
            alert_type='endpoint_unhealthy',
            severity='critical',
            message='Endpoint is unhealthy'
        )
        alert2 = Alert(
            endpoint='/ws/observatory',
            alert_type='endpoint_degraded',
            severity='medium',
            message='Endpoint is degraded'
        )
        
        monitor._alert_history = [alert1, alert2]
        
        history = await monitor.get_alert_history(limit=1)
        
        assert len(history) == 1
        assert history[0] == alert2  # Last alert
    
    @pytest.mark.asyncio
    async def test_get_quality_metrics_history(self, monitor):
        """Test getting quality metrics history."""
        endpoint = '/ws/emoji-rain'
        metrics = QualityMetrics(
            endpoint=endpoint,
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        monitor._quality_metrics_history[endpoint] = [metrics]
        
        history = await monitor.get_quality_metrics_history(endpoint, limit=1)
        
        assert len(history) == 1
        assert history[0] == metrics
    
    @pytest.mark.asyncio
    async def test_get_quality_metrics_history_not_found(self, monitor):
        """Test getting quality metrics history for unknown endpoint."""
        endpoint = '/ws/nonexistent'
        
        history = await monitor.get_quality_metrics_history(endpoint)
        
        assert len(history) == 0
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, monitor):
        """Test resolving an alert."""
        alert = Alert(
            endpoint='/ws/emoji-rain',
            alert_type='endpoint_unhealthy',
            severity='critical',
            message='Endpoint is unhealthy'
        )
        
        alert_key = '/ws/emoji-rain:endpoint_unhealthy'
        monitor._active_alerts[alert_key] = alert
        
        result = await monitor.resolve_alert('/ws/emoji-rain', 'endpoint_unhealthy')
        
        assert result is True
        assert alert_key not in monitor._active_alerts
        assert alert.resolved_at is not None
        assert len(monitor._alert_history) == 1
    
    @pytest.mark.asyncio
    async def test_resolve_alert_not_found(self, monitor):
        """Test resolving a non-existent alert."""
        result = await monitor.resolve_alert('/ws/emoji-rain', 'nonexistent_alert')
        
        assert result is False
    
    def test_add_health_callback(self, monitor):
        """Test adding health callback."""
        callback = MagicMock()
        
        monitor.add_health_callback(callback)
        
        assert callback in monitor._health_callbacks
    
    def test_remove_health_callback(self, monitor):
        """Test removing health callback."""
        callback = MagicMock()
        monitor.add_health_callback(callback)
        
        monitor.remove_health_callback(callback)
        
        assert callback not in monitor._health_callbacks
    
    def test_add_alert_callback(self, monitor):
        """Test adding alert callback."""
        callback = MagicMock()
        
        monitor.add_alert_callback(callback)
        
        assert callback in monitor._alert_callbacks
    
    def test_remove_alert_callback(self, monitor):
        """Test removing alert callback."""
        callback = MagicMock()
        monitor.add_alert_callback(callback)
        
        monitor.remove_alert_callback(callback)
        
        assert callback not in monitor._alert_callbacks
    
    def test_add_quality_callback(self, monitor):
        """Test adding quality callback."""
        callback = MagicMock()
        
        monitor.add_quality_callback(callback)
        
        assert callback in monitor._quality_callbacks
    
    def test_remove_quality_callback(self, monitor):
        """Test removing quality callback."""
        callback = MagicMock()
        monitor.add_quality_callback(callback)
        
        monitor.remove_quality_callback(callback)
        
        assert callback not in monitor._quality_callbacks
    
    @pytest.mark.asyncio
    async def test_perform_health_checks(self, monitor):
        """Test performing health checks."""
        with patch.object(monitor.health_validator, 'validate_all_endpoints') as mock_validate:
            # Mock health check results
            mock_results = {}
            for endpoint in monitor.health_validator.endpoints:
                mock_results[endpoint] = HealthCheckResult(
                    endpoint=endpoint,
                    status=HealthStatus.HEALTHY,
                    response_time_ms=100.0
                )
            
            mock_validate.return_value = mock_results
            
            await monitor._perform_health_checks()
            
            assert len(monitor._last_health_checks) == len(monitor.health_validator.endpoints)
            for endpoint in monitor.health_validator.endpoints:
                assert endpoint in monitor._last_health_checks
                assert monitor._last_health_checks[endpoint].status == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_store_quality_metrics(self, monitor):
        """Test storing quality metrics."""
        endpoint = '/ws/emoji-rain'
        metrics = QualityMetrics(
            endpoint=endpoint,
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        await monitor._store_quality_metrics(endpoint, metrics)
        
        assert endpoint in monitor._quality_metrics_history
        assert len(monitor._quality_metrics_history[endpoint]) == 1
        assert monitor._quality_metrics_history[endpoint][0] == metrics
    
    @pytest.mark.asyncio
    async def test_store_failures(self, monitor):
        """Test storing failures."""
        from src.beast_mode.observatory.websocket.health_validator import FailureIndicator
        
        endpoint = '/ws/emoji-rain'
        failure = FailureIndicator(
            endpoint=endpoint,
            failure_type='slow_response',
            severity='medium',
            description='Response time exceeds threshold'
        )
        
        await monitor._store_failures(endpoint, [failure])
        
        assert endpoint in monitor._failure_history
        assert len(monitor._failure_history[endpoint]) == 1
        assert monitor._failure_history[endpoint][0] == failure
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_alerts_unhealthy(self, monitor):
        """Test checking and triggering alerts for unhealthy endpoint."""
        result = HealthCheckResult(
            endpoint='/ws/emoji-rain',
            status=HealthStatus.UNHEALTHY,
            response_time_ms=5000.0,
            error_message='Connection failed'
        )
        
        await monitor._check_and_trigger_alerts('/ws/emoji-rain', result)
        
        # Should trigger unhealthy alert
        alert_key = '/ws/emoji-rain:endpoint_unhealthy'
        assert alert_key in monitor._active_alerts
        alert = monitor._active_alerts[alert_key]
        assert alert.severity == 'critical'
        assert 'unhealthy' in alert.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_alerts_degraded(self, monitor):
        """Test checking and triggering alerts for degraded endpoint."""
        result = HealthCheckResult(
            endpoint='/ws/emoji-rain',
            status=HealthStatus.DEGRADED,
            response_time_ms=100.0
        )
        
        await monitor._check_and_trigger_alerts('/ws/emoji-rain', result)
        
        # Should trigger degraded alert
        alert_key = '/ws/emoji-rain:endpoint_degraded'
        assert alert_key in monitor._active_alerts
        alert = monitor._active_alerts[alert_key]
        assert alert.severity == 'medium'
        assert 'degraded' in alert.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_alerts_high_response_time(self, monitor):
        """Test checking and triggering alerts for high response time."""
        result = HealthCheckResult(
            endpoint='/ws/emoji-rain',
            status=HealthStatus.HEALTHY,
            response_time_ms=3000.0  # Exceeds 2000ms threshold
        )
        
        await monitor._check_and_trigger_alerts('/ws/emoji-rain', result)
        
        # Should trigger high response time alert
        alert_key = '/ws/emoji-rain:high_response_time'
        assert alert_key in monitor._active_alerts
        alert = monitor._active_alerts[alert_key]
        assert alert.severity == 'medium'
        assert 'response time' in alert.message.lower()
    
    @pytest.mark.asyncio
    async def test_trigger_alert_if_needed_new_alert(self, monitor):
        """Test triggering a new alert."""
        await monitor._trigger_alert_if_needed(
            endpoint='/ws/emoji-rain',
            alert_type='test_alert',
            severity='medium',
            message='Test alert message',
            metadata={'test': 'data'}
        )
        
        alert_key = '/ws/emoji-rain:test_alert'
        assert alert_key in monitor._active_alerts
        alert = monitor._active_alerts[alert_key]
        assert alert.endpoint == '/ws/emoji-rain'
        assert alert.alert_type == 'test_alert'
        assert alert.severity == 'medium'
        assert alert.message == 'Test alert message'
        assert alert.metadata['test'] == 'data'
    
    @pytest.mark.asyncio
    async def test_trigger_alert_if_needed_existing_alert(self, monitor):
        """Test not triggering alert if already exists."""
        # Create existing alert
        existing_alert = Alert(
            endpoint='/ws/emoji-rain',
            alert_type='test_alert',
            severity='medium',
            message='Existing alert'
        )
        alert_key = '/ws/emoji-rain:test_alert'
        monitor._active_alerts[alert_key] = existing_alert
        
        await monitor._trigger_alert_if_needed(
            endpoint='/ws/emoji-rain',
            alert_type='test_alert',
            severity='medium',
            message='New alert message',
            metadata={}
        )
        
        # Should not create new alert
        assert len(monitor._active_alerts) == 1
        assert monitor._active_alerts[alert_key] == existing_alert
    
    @pytest.mark.asyncio
    async def test_notify_health_callbacks(self, monitor):
        """Test notifying health callbacks."""
        callback = MagicMock()
        monitor.add_health_callback(callback)
        
        result = HealthCheckResult(
            endpoint='/ws/emoji-rain',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        
        await monitor._notify_health_callbacks('/ws/emoji-rain', result)
        
        callback.assert_called_once_with('/ws/emoji-rain', result)
    
    @pytest.mark.asyncio
    async def test_notify_alert_callbacks(self, monitor):
        """Test notifying alert callbacks."""
        callback = MagicMock()
        monitor.add_alert_callback(callback)
        
        alert = Alert(
            endpoint='/ws/emoji-rain',
            alert_type='test_alert',
            severity='medium',
            message='Test alert'
        )
        
        await monitor._notify_alert_callbacks(alert)
        
        callback.assert_called_once_with(alert)
    
    @pytest.mark.asyncio
    async def test_notify_quality_callbacks(self, monitor):
        """Test notifying quality callbacks."""
        callback = MagicMock()
        monitor.add_quality_callback(callback)
        
        metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        await monitor._notify_quality_callbacks('/ws/emoji-rain', metrics)
        
        callback.assert_called_once_with('/ws/emoji-rain', metrics)
    
    def test_get_monitoring_stats(self, monitor):
        """Test getting monitoring statistics."""
        # Add some test data
        monitor._last_health_checks['/ws/emoji-rain'] = HealthCheckResult(
            endpoint='/ws/emoji-rain',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        
        alert = Alert(
            endpoint='/ws/emoji-rain',
            alert_type='test_alert',
            severity='medium',
            message='Test alert'
        )
        monitor._active_alerts['/ws/emoji-rain:test_alert'] = alert
        
        metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        monitor._quality_metrics_history['/ws/emoji-rain'] = [metrics]
        
        stats = monitor.get_monitoring_stats()
        
        assert stats["monitoring_active"] is False
        assert stats["total_endpoints"] == len(monitor.health_validator.endpoints)
        assert "health_stats" in stats
        assert "alert_stats" in stats
        assert stats["alert_stats"]["active_alerts"] == 1
        assert stats["quality_metrics_collected"] == 1
        assert stats["callback_counts"]["health_callbacks"] == 0
    
    def test_log_action(self, monitor, capsys):
        """Test JSON logging functionality."""
        monitor._log_action("test_action", {"test": "data"})
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.out.strip())
        
        assert log_data["task"] == "2.3"
        assert log_data["action"] == "endpoint_monitor_test_action"
        assert log_data["status"] == "in_progress"
        assert log_data["details"]["test"] == "data"
        assert "timestamp" in log_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])