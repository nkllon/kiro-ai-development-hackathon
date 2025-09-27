"""Unit tests for WebSocket endpoint monitor."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

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


class TestEndpointMonitor:
    """Test cases for EndpointMonitor."""
    
    @pytest.fixture
    def config(self):
        """Create monitoring configuration."""
        return MonitoringConfig(
            check_interval_seconds=1.0,
            health_check_timeout=2.0,
            max_consecutive_failures=3,
            alert_cooldown_seconds=60.0,
            enable_quality_metrics=True,
            enable_failure_detection=True,
            enable_alerts=True
        )
    
    @pytest.fixture
    def monitor(self, config):
        """Create EndpointMonitor instance."""
        return EndpointMonitor(config)
    
    @pytest.fixture
    def mock_health_result(self):
        """Create mock health check result."""
        return HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0,
            quality_metrics=QualityMetrics(
                endpoint='/ws/test',
                response_time_ms=100.0,
                connection_time_ms=200.0,
                message_latency_ms=50.0,
                throughput_bytes_per_sec=1000.0,
                error_rate=0.01,
                uptime_percentage=99.0
            )
        )
    
    def test_initialization(self, monitor, config):
        """Test monitor initialization."""
        assert monitor.config == config
        assert monitor.health_validator is not None
        assert monitor._monitoring_active is False
        assert monitor._monitoring_task is None
        assert len(monitor._last_health_checks) == 0
        assert len(monitor._active_alerts) == 0
        assert len(monitor._alert_history) == 0
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, monitor):
        """Test starting monitoring."""
        with patch.object(monitor, '_monitoring_loop') as mock_loop:
            mock_loop.return_value = AsyncMock()
            
            await monitor.start_monitoring()
            
            assert monitor._monitoring_active is True
            assert monitor._monitoring_task is not None
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, monitor):
        """Test stopping monitoring."""
        # Start monitoring first
        monitor._monitoring_active = True
        monitor._monitoring_task = asyncio.create_task(asyncio.sleep(1))
        
        await monitor.stop_monitoring()
        
        assert monitor._monitoring_active is False
        assert monitor._monitoring_task.cancelled()
    
    @pytest.mark.asyncio
    async def test_get_endpoint_status(self, monitor, mock_health_result):
        """Test getting endpoint status."""
        monitor._last_health_checks['/ws/test'] = mock_health_result
        
        status = await monitor.get_endpoint_status('/ws/test')
        assert status == mock_health_result
        
        # Test non-existent endpoint
        status = await monitor.get_endpoint_status('/ws/nonexistent')
        assert status is None
    
    @pytest.mark.asyncio
    async def test_get_all_endpoint_statuses(self, monitor, mock_health_result):
        """Test getting all endpoint statuses."""
        monitor._last_health_checks['/ws/test'] = mock_health_result
        
        statuses = await monitor.get_all_endpoint_statuses()
        assert len(statuses) == 1
        assert '/ws/test' in statuses
        assert statuses['/ws/test'] == mock_health_result
    
    @pytest.mark.asyncio
    async def test_get_active_alerts(self, monitor):
        """Test getting active alerts."""
        alert = Alert(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert message'
        )
        monitor._active_alerts['/ws/test:test_alert'] = alert
        
        alerts = await monitor.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0] == alert
    
    @pytest.mark.asyncio
    async def test_get_alert_history(self, monitor):
        """Test getting alert history."""
        alert = Alert(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert message'
        )
        monitor._alert_history.append(alert)
        
        history = await monitor.get_alert_history(limit=10)
        assert len(history) == 1
        assert history[0] == alert
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, monitor):
        """Test resolving an alert."""
        alert = Alert(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert message'
        )
        monitor._active_alerts['/ws/test:test_alert'] = alert
        
        # Resolve alert
        result = await monitor.resolve_alert('/ws/test', 'test_alert')
        assert result is True
        assert '/ws/test:test_alert' not in monitor._active_alerts
        assert len(monitor._alert_history) == 1
        assert monitor._alert_history[0].resolved_at is not None
        
        # Try to resolve non-existent alert
        result = await monitor.resolve_alert('/ws/test', 'nonexistent')
        assert result is False
    
    def test_add_remove_callbacks(self, monitor):
        """Test adding and removing callbacks."""
        def health_callback(endpoint, result):
            pass
        
        def alert_callback(alert):
            pass
        
        def quality_callback(endpoint, metrics):
            pass
        
        # Add callbacks
        monitor.add_health_callback(health_callback)
        monitor.add_alert_callback(alert_callback)
        monitor.add_quality_callback(quality_callback)
        
        assert len(monitor._health_callbacks) == 1
        assert len(monitor._alert_callbacks) == 1
        assert len(monitor._quality_callbacks) == 1
        
        # Remove callbacks
        monitor.remove_health_callback(health_callback)
        monitor.remove_alert_callback(alert_callback)
        monitor.remove_quality_callback(quality_callback)
        
        assert len(monitor._health_callbacks) == 0
        assert len(monitor._alert_callbacks) == 0
        assert len(monitor._quality_callbacks) == 0
    
    @pytest.mark.asyncio
    async def test_perform_health_checks(self, monitor, mock_health_result):
        """Test performing health checks."""
        with patch.object(monitor.health_validator, 'validate_all_endpoints') as mock_validate:
            mock_validate.return_value = {'/ws/test': mock_health_result}
            
            await monitor._perform_health_checks()
            
            assert '/ws/test' in monitor._last_health_checks
            assert monitor._last_health_checks['/ws/test'] == mock_health_result
    
    @pytest.mark.asyncio
    async def test_store_quality_metrics(self, monitor):
        """Test storing quality metrics."""
        metrics = QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        await monitor._store_quality_metrics('/ws/test', metrics)
        
        assert '/ws/test' in monitor._quality_metrics_history
        assert len(monitor._quality_metrics_history['/ws/test']) == 1
        assert monitor._quality_metrics_history['/ws/test'][0] == metrics
    
    @pytest.mark.asyncio
    async def test_store_failures(self, monitor):
        """Test storing failures."""
        from src.beast_mode.observatory.websocket.health_validator import FailureIndicator
        
        failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='slow_response',
            severity='medium',
            description='Slow response detected'
        )
        
        await monitor._store_failures('/ws/test', [failure])
        
        assert '/ws/test' in monitor._failure_history
        assert len(monitor._failure_history['/ws/test']) == 1
        assert monitor._failure_history['/ws/test'][0] == failure
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_alerts_healthy(self, monitor, mock_health_result):
        """Test alert checking with healthy status."""
        await monitor._check_and_trigger_alerts('/ws/test', mock_health_result)
        
        # Should not trigger any alerts for healthy status
        assert len(monitor._active_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_alerts_unhealthy(self, monitor):
        """Test alert checking with unhealthy status."""
        unhealthy_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.UNHEALTHY,
            response_time_ms=100.0,
            error_message='Connection failed'
        )
        
        await monitor._check_and_trigger_alerts('/ws/test', unhealthy_result)
        
        # Should trigger an alert for unhealthy status
        assert len(monitor._active_alerts) > 0
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_alerts_degraded(self, monitor):
        """Test alert checking with degraded status."""
        degraded_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.DEGRADED,
            response_time_ms=100.0
        )
        
        await monitor._check_and_trigger_alerts('/ws/test', degraded_result)
        
        # Should trigger an alert for degraded status
        assert len(monitor._active_alerts) > 0
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_alerts_high_response_time(self, monitor):
        """Test alert checking with high response time."""
        high_response_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.HEALTHY,
            response_time_ms=3000.0  # High response time
        )
        
        await monitor._check_and_trigger_alerts('/ws/test', high_response_result)
        
        # Should trigger an alert for high response time
        assert len(monitor._active_alerts) > 0
    
    @pytest.mark.asyncio
    async def test_trigger_alert_if_needed(self, monitor):
        """Test triggering alert if needed."""
        await monitor._trigger_alert_if_needed(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert',
            metadata={}
        )
        
        assert '/ws/test:test_alert' in monitor._active_alerts
        alert = monitor._active_alerts['/ws/test:test_alert']
        assert alert.endpoint == '/ws/test'
        assert alert.alert_type == 'test_alert'
        assert alert.severity == 'medium'
        assert alert.message == 'Test alert'
    
    @pytest.mark.asyncio
    async def test_trigger_alert_cooldown(self, monitor):
        """Test alert cooldown mechanism."""
        # Trigger first alert
        await monitor._trigger_alert_if_needed(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert',
            metadata={}
        )
        
        assert len(monitor._active_alerts) == 1
        
        # Try to trigger same alert again (should be in cooldown)
        await monitor._trigger_alert_if_needed(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert',
            metadata={}
        )
        
        # Should still only have one alert
        assert len(monitor._active_alerts) == 1
    
    @pytest.mark.asyncio
    async def test_notify_callbacks(self, monitor, mock_health_result):
        """Test callback notifications."""
        health_callback_called = False
        alert_callback_called = False
        quality_callback_called = False
        
        def health_callback(endpoint, result):
            nonlocal health_callback_called
            health_callback_called = True
        
        def alert_callback(alert):
            nonlocal alert_callback_called
            alert_callback_called = True
        
        def quality_callback(endpoint, metrics):
            nonlocal quality_callback_called
            quality_callback_called = True
        
        monitor.add_health_callback(health_callback)
        monitor.add_alert_callback(alert_callback)
        monitor.add_quality_callback(quality_callback)
        
        # Test health callback
        await monitor._notify_health_callbacks('/ws/test', mock_health_result)
        assert health_callback_called
        
        # Test alert callback
        alert = Alert(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert'
        )
        await monitor._notify_alert_callbacks(alert)
        assert alert_callback_called
        
        # Test quality callback
        metrics = QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        await monitor._notify_quality_callbacks('/ws/test', metrics)
        assert quality_callback_called
    
    def test_get_monitoring_stats(self, monitor):
        """Test getting monitoring statistics."""
        stats = monitor.get_monitoring_stats()
        
        assert 'monitoring_active' in stats
        assert 'total_endpoints' in stats
        assert 'health_stats' in stats
        assert 'alert_stats' in stats
        assert 'quality_metrics_collected' in stats
        assert 'failures_detected' in stats
        assert 'callback_counts' in stats
        
        assert stats['monitoring_active'] is False
        assert stats['total_endpoints'] == 4
        assert stats['health_stats']['healthy'] == 0
        assert stats['health_stats']['unhealthy'] == 4
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_cancellation(self, monitor):
        """Test monitoring loop cancellation."""
        monitor._monitoring_active = True
        
        # Create a task that will be cancelled
        task = asyncio.create_task(monitor._monitoring_loop())
        
        # Cancel the task
        task.cancel()
        
        # Should not raise an exception
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        assert task.cancelled()
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_exception(self, monitor):
        """Test monitoring loop exception handling."""
        monitor._monitoring_active = True
        
        with patch.object(monitor, '_perform_health_checks') as mock_checks:
            mock_checks.side_effect = Exception("Test exception")
            
            with pytest.raises(Exception):
                await monitor._monitoring_loop()
    
    def test_alert_to_dict(self):
        """Test Alert to_dict method."""
        alert = Alert(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert message',
            metadata={'key': 'value'}
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict['endpoint'] == '/ws/test'
        assert alert_dict['alert_type'] == 'test_alert'
        assert alert_dict['severity'] == 'medium'
        assert alert_dict['message'] == 'Test alert message'
        assert alert_dict['metadata']['key'] == 'value'
        assert 'triggered_at' in alert_dict
        assert alert_dict['resolved_at'] is None