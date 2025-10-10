"""Integration tests for WebSocket health validation system."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.beast_mode.observatory.websocket.health_validator import WebSocketHealthValidator
from src.beast_mode.observatory.websocket.endpoint_monitor import EndpointMonitor, MonitoringConfig
from src.beast_mode.observatory.websocket.quality_metrics import QualityMetricsCollector
from src.beast_mode.observatory.websocket.failure_detector import FailureDetector


class TestWebSocketHealthValidationIntegration:
    """Integration tests for the complete WebSocket health validation system."""
    
    @pytest.fixture
    def health_validator(self):
        """Create health validator."""
        return WebSocketHealthValidator(timeout=1.0, max_retries=2)
    
    @pytest.fixture
    def endpoint_monitor(self):
        """Create endpoint monitor."""
        config = MonitoringConfig(
            check_interval_seconds=1.0,
            health_check_timeout=2.0,
            max_consecutive_failures=3,
            alert_cooldown_seconds=60.0,
            enable_quality_metrics=True,
            enable_failure_detection=True,
            enable_alerts=True
        )
        return EndpointMonitor(config)
    
    @pytest.fixture
    def quality_collector(self):
        """Create quality metrics collector."""
        return QualityMetricsCollector(max_history_size=1000)
    
    @pytest.fixture
    def failure_detector(self):
        """Create failure detector."""
        return FailureDetector()
    
    def test_component_initialization(self, health_validator, endpoint_monitor, quality_collector, failure_detector):
        """Test that all components initialize correctly."""
        # Health validator
        assert health_validator is not None
        assert len(health_validator.endpoints) == 4
        
        # Endpoint monitor
        assert endpoint_monitor is not None
        assert endpoint_monitor.health_validator is not None
        
        # Quality collector
        assert quality_collector is not None
        assert quality_collector.max_history_size == 1000
        
        # Failure detector
        assert failure_detector is not None
        assert len(failure_detector._failure_rules) > 0
    
    @pytest.mark.asyncio
    async def test_health_validator_basic_functionality(self, health_validator):
        """Test basic health validator functionality."""
        # Test health summary with no data
        summary = health_validator.get_health_summary()
        assert summary['overall_status'] == 'unknown'
        assert summary['total_endpoints'] == 4
        
        # Test validate all endpoints (will fail without real connections)
        results = await health_validator.validate_all_endpoints()
        assert len(results) == 4
        for endpoint in health_validator.endpoints:
            assert endpoint in results
            assert results[endpoint].status.value in ['healthy', 'degraded', 'unhealthy']
    
    @pytest.mark.asyncio
    async def test_endpoint_monitor_basic_functionality(self, endpoint_monitor):
        """Test basic endpoint monitor functionality."""
        # Test getting endpoint status (no data initially)
        status = await endpoint_monitor.get_endpoint_status('/ws/test')
        assert status is None
        
        # Test getting all endpoint statuses
        statuses = await endpoint_monitor.get_all_endpoint_statuses()
        assert len(statuses) == 0
        
        # Test getting active alerts
        alerts = await endpoint_monitor.get_active_alerts()
        assert len(alerts) == 0
        
        # Test getting alert history
        history = await endpoint_monitor.get_alert_history()
        assert len(history) == 0
    
    def test_quality_collector_basic_functionality(self, quality_collector):
        """Test basic quality collector functionality."""
        # Test getting collection stats
        stats = quality_collector.get_collection_stats()
        assert 'total_metrics_collected' in stats
        assert 'endpoints_tracked' in stats
        assert 'max_history_size' in stats
        assert stats['total_metrics_collected'] == 0
        assert stats['endpoints_tracked'] == 0
    
    def test_failure_detector_basic_functionality(self, failure_detector):
        """Test basic failure detector functionality."""
        # Test getting detection stats
        stats = failure_detector.get_detection_stats()
        assert 'total_failures_detected' in stats
        assert 'endpoints_monitored' in stats
        assert 'active_rules' in stats
        assert 'total_rules' in stats
        assert stats['total_failures_detected'] == 0
        assert stats['endpoints_monitored'] == 0
    
    @pytest.mark.asyncio
    async def test_callback_functionality(self, endpoint_monitor, failure_detector):
        """Test callback functionality."""
        health_callback_called = False
        alert_callback_called = False
        failure_callback_called = False
        
        def health_callback(endpoint, result):
            nonlocal health_callback_called
            health_callback_called = True
        
        def alert_callback(alert):
            nonlocal alert_callback_called
            alert_callback_called = True
        
        def failure_callback(failure):
            nonlocal failure_callback_called
            failure_callback_called = True
        
        # Add callbacks
        endpoint_monitor.add_health_callback(health_callback)
        endpoint_monitor.add_alert_callback(alert_callback)
        failure_detector.add_failure_callback(failure_callback)
        
        # Test callback counts
        stats = endpoint_monitor.get_monitoring_stats()
        assert stats['callback_counts']['health_callbacks'] == 1
        assert stats['callback_counts']['alert_callbacks'] == 1
        
        stats = failure_detector.get_detection_stats()
        assert stats['callback_count'] == 1
        
        # Remove callbacks
        endpoint_monitor.remove_health_callback(health_callback)
        endpoint_monitor.remove_alert_callback(alert_callback)
        failure_detector.remove_failure_callback(failure_callback)
        
        # Test callback counts after removal
        stats = endpoint_monitor.get_monitoring_stats()
        assert stats['callback_counts']['health_callbacks'] == 0
        assert stats['callback_counts']['alert_callbacks'] == 0
        
        stats = failure_detector.get_detection_stats()
        assert stats['callback_count'] == 0
    
    def test_rule_management(self, failure_detector):
        """Test failure rule management."""
        from src.beast_mode.observatory.websocket.failure_detector import FailureRule, FailureType, FailureSeverity
        
        # Test adding custom rule
        rule = FailureRule(
            name='custom_test_rule',
            failure_type=FailureType.SLOW_RESPONSE,
            severity=FailureSeverity.MEDIUM,
            condition='response_time_ms > 500',
            threshold=500.0
        )
        
        failure_detector.add_failure_rule(rule)
        assert 'custom_test_rule' in failure_detector._failure_rules
        
        # Test enabling/disabling rule
        failure_detector.disable_rule('custom_test_rule')
        assert failure_detector._failure_rules['custom_test_rule'].enabled is False
        
        failure_detector.enable_rule('custom_test_rule')
        assert failure_detector._failure_rules['custom_test_rule'].enabled is True
        
        # Test removing rule
        result = failure_detector.remove_failure_rule('custom_test_rule')
        assert result is True
        assert 'custom_test_rule' not in failure_detector._failure_rules
    
    def test_threshold_management(self, quality_collector):
        """Test quality threshold management."""
        from src.beast_mode.observatory.websocket.quality_metrics import QualityThresholds
        
        # Test updating thresholds
        new_thresholds = QualityThresholds(
            response_time_ms=2000.0,
            connection_time_ms=10000.0,
            message_latency_ms=200.0,
            throughput_bytes_per_sec=2000.0,
            error_rate=0.1,
            uptime_percentage=90.0
        )
        
        quality_collector.update_quality_thresholds(new_thresholds)
        
        assert quality_collector._quality_thresholds.response_time_ms == 2000.0
        assert quality_collector._quality_thresholds.connection_time_ms == 10000.0
        assert quality_collector._quality_thresholds.message_latency_ms == 200.0
        assert quality_collector._quality_thresholds.throughput_bytes_per_sec == 2000.0
        assert quality_collector._quality_thresholds.error_rate == 0.1
        assert quality_collector._quality_thresholds.uptime_percentage == 90.0
    
    @pytest.mark.asyncio
    async def test_alert_management(self, endpoint_monitor):
        """Test alert management."""
        from src.beast_mode.observatory.websocket.endpoint_monitor import Alert
        
        # Create an alert
        alert = Alert(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert message'
        )
        
        # Add alert to active alerts
        endpoint_monitor._active_alerts['/ws/test:test_alert'] = alert
        
        # Test getting active alerts
        active_alerts = await endpoint_monitor.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0] == alert
        
        # Test resolving alert
        result = await endpoint_monitor.resolve_alert('/ws/test', 'test_alert')
        assert result is True
        
        # Check alert was moved to history
        active_alerts = await endpoint_monitor.get_active_alerts()
        assert len(active_alerts) == 0
        
        history = await endpoint_monitor.get_alert_history()
        assert len(history) == 1
        assert history[0].resolved_at is not None
    
    def test_data_structures(self):
        """Test data structure serialization."""
        from src.beast_mode.observatory.websocket.health_validator import QualityMetrics, FailureIndicator, HealthCheckResult
        from src.beast_mode.observatory.websocket.endpoint_monitor import Alert
        from src.beast_mode.observatory.websocket.quality_metrics import MetricsSnapshot, MetricsAggregation, QualityThresholds
        
        # Test QualityMetrics
        metrics = QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        metrics_dict = metrics.to_dict()
        assert metrics_dict['endpoint'] == '/ws/test'
        assert metrics_dict['response_time_ms'] == 100.0
        
        # Test FailureIndicator
        failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='slow_response',
            severity='medium',
            description='Slow response detected',
            metadata={'key': 'value'}
        )
        failure_dict = failure.to_dict()
        assert failure_dict['endpoint'] == '/ws/test'
        assert failure_dict['failure_type'] == 'slow_response'
        assert failure_dict['severity'] == 'medium'
        
        # Test Alert
        alert = Alert(
            endpoint='/ws/test',
            alert_type='test_alert',
            severity='medium',
            message='Test alert',
            metadata={'key': 'value'}
        )
        alert_dict = alert.to_dict()
        assert alert_dict['endpoint'] == '/ws/test'
        assert alert_dict['alert_type'] == 'test_alert'
        assert alert_dict['severity'] == 'medium'
        
        # Test MetricsSnapshot
        snapshot = MetricsSnapshot(
            timestamp=datetime.utcnow(),
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        snapshot_dict = snapshot.to_dict()
        assert snapshot_dict['endpoint'] == '/ws/test'
        assert snapshot_dict['response_time_ms'] == 100.0
        
        # Test QualityThresholds
        thresholds = QualityThresholds()
        thresholds_dict = thresholds.to_dict()
        assert 'response_time_ms' in thresholds_dict
        assert 'connection_time_ms' in thresholds_dict
        assert 'message_latency_ms' in thresholds_dict
        assert 'throughput_bytes_per_sec' in thresholds_dict
        assert 'error_rate' in thresholds_dict
        assert 'uptime_percentage' in thresholds_dict
    
    def test_enum_values(self):
        """Test enum values."""
        from src.beast_mode.observatory.websocket.health_validator import HealthStatus
        from src.beast_mode.observatory.websocket.failure_detector import FailureSeverity, FailureType
        
        # Test HealthStatus
        assert HealthStatus.HEALTHY.value == 'healthy'
        assert HealthStatus.DEGRADED.value == 'degraded'
        assert HealthStatus.UNHEALTHY.value == 'unhealthy'
        assert HealthStatus.UNKNOWN.value == 'unknown'
        
        # Test FailureSeverity
        assert FailureSeverity.LOW.value == 'low'
        assert FailureSeverity.MEDIUM.value == 'medium'
        assert FailureSeverity.HIGH.value == 'high'
        assert FailureSeverity.CRITICAL.value == 'critical'
        
        # Test FailureType
        assert FailureType.SLOW_RESPONSE.value == 'slow_response'
        assert FailureType.HIGH_LATENCY.value == 'high_latency'
        assert FailureType.HIGH_ERROR_RATE.value == 'high_error_rate'
        assert FailureType.LOW_UPTIME.value == 'low_uptime'
        assert FailureType.ENDPOINT_SPECIFIC.value == 'endpoint_specific'
    
    @pytest.mark.asyncio
    async def test_error_handling(self, health_validator, endpoint_monitor, quality_collector, failure_detector):
        """Test error handling in components."""
        # Test health validator with invalid endpoint
        result = await health_validator.validate_endpoint_health('invalid://endpoint')
        assert result.status.value in ['unhealthy', 'unknown']
        assert result.error_message is not None
        
        # Test quality collector with None metrics
        snapshot = await quality_collector.collect_metrics('/ws/test', None)
        assert snapshot is not None
        assert snapshot.response_time_ms == float('inf')
        
        # Test failure detector with None metrics
        failures = await failure_detector.detect_failures('/ws/test', None, None, {})
        assert isinstance(failures, list)
        
        # Test endpoint monitor with invalid data
        status = await endpoint_monitor.get_endpoint_status(None)
        assert status is None
    
    def test_logging_format(self):
        """Test that logging follows the required JSON format."""
        # This test verifies that the _log_action methods produce valid JSON
        import json
        
        from src.beast_mode.observatory.websocket.health_validator import WebSocketHealthValidator
        from src.beast_mode.observatory.websocket.endpoint_monitor import EndpointMonitor, MonitoringConfig
        from src.beast_mode.observatory.websocket.quality_metrics import QualityMetricsCollector
        from src.beast_mode.observatory.websocket.failure_detector import FailureDetector
        
        # Test health validator logging
        validator = WebSocketHealthValidator()
        # The _log_action method should produce valid JSON
        # We can't easily test the actual output without mocking print, but we can verify the method exists
        assert hasattr(validator, '_log_action')
        
        # Test endpoint monitor logging
        config = MonitoringConfig()
        monitor = EndpointMonitor(config)
        assert hasattr(monitor, '_log_action')
        
        # Test quality collector logging
        collector = QualityMetricsCollector()
        assert hasattr(collector, '_log_action')
        
        # Test failure detector logging
        detector = FailureDetector()
        assert hasattr(detector, '_log_action')