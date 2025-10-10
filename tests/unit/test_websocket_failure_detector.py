"""Unit tests for WebSocket failure detector."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.beast_mode.observatory.websocket.failure_detector import (
    FailureDetector,
    FailureSeverity,
    FailureType,
    FailureRule
)
from src.beast_mode.observatory.websocket.health_validator import (
    QualityMetrics,
    FailureIndicator,
    HealthStatus
)


class TestFailureDetector:
    """Test cases for FailureDetector."""
    
    @pytest.fixture
    def detector(self):
        """Create FailureDetector instance."""
        return FailureDetector()
    
    @pytest.fixture
    def good_quality_metrics(self):
        """Create good quality metrics."""
        return QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
    
    @pytest.fixture
    def poor_quality_metrics(self):
        """Create poor quality metrics."""
        return QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=2000.0,  # Exceeds threshold
            connection_time_ms=6000.0,  # Exceeds threshold
            message_latency_ms=200.0,  # Exceeds threshold
            throughput_bytes_per_sec=500.0,
            error_rate=0.1,  # Exceeds threshold
            uptime_percentage=80.0  # Below threshold
        )
    
    def test_initialization(self, detector):
        """Test detector initialization."""
        assert len(detector._failure_rules) > 0  # Should have default rules
        assert len(detector._failure_history) == 0
        assert len(detector._last_failure_times) == 0
        assert len(detector._failure_callbacks) == 0
    
    def test_add_failure_rule(self, detector):
        """Test adding custom failure rule."""
        rule = FailureRule(
            name='custom_rule',
            failure_type=FailureType.SLOW_RESPONSE,
            severity=FailureSeverity.MEDIUM,
            condition='response_time_ms > 500',
            threshold=500.0
        )
        
        detector.add_failure_rule(rule)
        
        assert 'custom_rule' in detector._failure_rules
        assert detector._failure_rules['custom_rule'] == rule
    
    def test_remove_failure_rule(self, detector):
        """Test removing failure rule."""
        # Add a rule first
        rule = FailureRule(
            name='test_rule',
            failure_type=FailureType.SLOW_RESPONSE,
            severity=FailureSeverity.MEDIUM,
            condition='response_time_ms > 500',
            threshold=500.0
        )
        detector.add_failure_rule(rule)
        
        # Remove it
        result = detector.remove_failure_rule('test_rule')
        assert result is True
        assert 'test_rule' not in detector._failure_rules
        
        # Try to remove non-existent rule
        result = detector.remove_failure_rule('nonexistent')
        assert result is False
    
    def test_enable_disable_rule(self, detector):
        """Test enabling and disabling rules."""
        # Add a rule
        rule = FailureRule(
            name='test_rule',
            failure_type=FailureType.SLOW_RESPONSE,
            severity=FailureSeverity.MEDIUM,
            condition='response_time_ms > 500',
            threshold=500.0,
            enabled=True
        )
        detector.add_failure_rule(rule)
        
        # Disable it
        result = detector.disable_rule('test_rule')
        assert result is True
        assert detector._failure_rules['test_rule'].enabled is False
        
        # Enable it
        result = detector.enable_rule('test_rule')
        assert result is True
        assert detector._failure_rules['test_rule'].enabled is True
        
        # Try with non-existent rule
        result = detector.enable_rule('nonexistent')
        assert result is False
    
    @pytest.mark.asyncio
    async def test_detect_failures_good_metrics(self, detector, good_quality_metrics):
        """Test failure detection with good metrics."""
        failures = await detector.detect_failures(
            '/ws/test',
            quality_metrics=good_quality_metrics,
            health_status=HealthStatus.HEALTHY
        )
        
        # Should not detect any failures with good metrics
        assert len(failures) == 0
    
    @pytest.mark.asyncio
    async def test_detect_failures_poor_metrics(self, detector, poor_quality_metrics):
        """Test failure detection with poor metrics."""
        failures = await detector.detect_failures(
            '/ws/test',
            quality_metrics=poor_quality_metrics,
            health_status=HealthStatus.DEGRADED
        )
        
        # Should detect multiple failures
        assert len(failures) > 0
        
        # Check specific failure types
        failure_types = [f.failure_type for f in failures]
        assert 'slow_response' in failure_types
        assert 'slow_connection' in failure_types
        assert 'high_latency' in failure_types
        assert 'high_error_rate' in failure_types
        assert 'low_uptime' in failure_types
    
    @pytest.mark.asyncio
    async def test_detect_failures_unhealthy_status(self, detector, good_quality_metrics):
        """Test failure detection with unhealthy status."""
        failures = await detector.detect_failures(
            '/ws/test',
            quality_metrics=good_quality_metrics,
            health_status=HealthStatus.UNHEALTHY
        )
        
        # Should detect failures even with good metrics if status is unhealthy
        assert len(failures) > 0
    
    @pytest.mark.asyncio
    async def test_detect_failures_with_additional_data(self, detector, good_quality_metrics):
        """Test failure detection with additional data."""
        additional_data = {
            'active_connections': 1000,  # Too many
            'emoji_engine_running': False,
            'observatory_health_score': 0.5
        }
        
        failures = await detector.detect_failures(
            '/ws/test',
            quality_metrics=good_quality_metrics,
            health_status=HealthStatus.HEALTHY,
            additional_data=additional_data
        )
        
        # Should detect endpoint-specific failures
        assert len(failures) > 0
    
    @pytest.mark.asyncio
    async def test_get_failure_history(self, detector):
        """Test getting failure history."""
        # Add some failures
        failure1 = FailureIndicator(
            endpoint='/ws/test',
            failure_type='slow_response',
            severity='medium',
            description='Slow response'
        )
        failure2 = FailureIndicator(
            endpoint='/ws/test',
            failure_type='high_error_rate',
            severity='high',
            description='High error rate'
        )
        
        detector._failure_history['/ws/test'] = [failure1, failure2]
        
        # Get history
        history = await detector.get_failure_history('/ws/test')
        assert len(history) == 2
        assert history[0] == failure1
        assert history[1] == failure2
        
        # Get limited history
        history = await detector.get_failure_history('/ws/test', limit=1)
        assert len(history) == 1
        assert history[0] == failure2  # Most recent
        
        # Get history for non-existent endpoint
        history = await detector.get_failure_history('/ws/nonexistent')
        assert len(history) == 0
    
    @pytest.mark.asyncio
    async def test_get_failure_summary(self, detector):
        """Test getting failure summary."""
        # Add some failures over time
        now = datetime.utcnow()
        recent_failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='slow_response',
            severity='medium',
            description='Slow response',
            detected_at=now
        )
        old_failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='high_error_rate',
            severity='high',
            description='High error rate',
            detected_at=now - timedelta(hours=25)  # Outside 24-hour window
        )
        
        detector._failure_history['/ws/test'] = [old_failure, recent_failure]
        
        summary = await detector.get_failure_summary('/ws/test', period_hours=24)
        
        assert summary['endpoint'] == '/ws/test'
        assert summary['period_hours'] == 24
        assert summary['total_failures'] == 1  # Only recent failure
        assert 'slow_response' in summary['failures_by_type']
        assert summary['failures_by_type']['slow_response'] == 1
        assert 'medium' in summary['failures_by_severity']
        assert summary['failures_by_severity']['medium'] == 1
        assert summary['most_common_failure'] == 'slow_response'
        assert summary['failure_trend'] in ['stable', 'increasing', 'decreasing']
    
    def test_add_remove_failure_callbacks(self, detector):
        """Test adding and removing failure callbacks."""
        def callback(failure):
            pass
        
        # Add callback
        detector.add_failure_callback(callback)
        assert len(detector._failure_callbacks) == 1
        
        # Remove callback
        detector.remove_failure_callback(callback)
        assert len(detector._failure_callbacks) == 0
    
    def test_get_detection_stats(self, detector):
        """Test getting detection statistics."""
        # Add some failures
        failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='slow_response',
            severity='medium',
            description='Slow response'
        )
        detector._failure_history['/ws/test'] = [failure]
        
        stats = detector.get_detection_stats()
        
        assert 'total_failures_detected' in stats
        assert 'endpoints_monitored' in stats
        assert 'active_rules' in stats
        assert 'total_rules' in stats
        assert 'failures_by_severity' in stats
        assert 'failures_by_type' in stats
        assert 'callback_count' in stats
        
        assert stats['total_failures_detected'] == 1
        assert stats['endpoints_monitored'] == 1
        assert stats['total_failures_detected'] == 1
        assert stats['failures_by_severity']['medium'] == 1
        assert stats['failures_by_type']['slow_response'] == 1
    
    @pytest.mark.asyncio
    async def test_apply_failure_rule(self, detector, poor_quality_metrics):
        """Test applying specific failure rules."""
        # Test slow response rule
        rule = detector._failure_rules['slow_response_time']
        result = await detector._apply_failure_rule(
            rule, '/ws/test', poor_quality_metrics, HealthStatus.HEALTHY, {}
        )
        assert result is True  # Should trigger with poor metrics
        
        # Test with good metrics
        good_metrics = QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        result = await detector._apply_failure_rule(
            rule, '/ws/test', good_metrics, HealthStatus.HEALTHY, {}
        )
        assert result is False  # Should not trigger with good metrics
    
    @pytest.mark.asyncio
    async def test_detect_endpoint_specific_failures(self, detector, good_quality_metrics):
        """Test endpoint-specific failure detection."""
        # Test emoji rain endpoint
        failures = await detector._detect_endpoint_specific_failures(
            '/ws/emoji-rain', good_quality_metrics, HealthStatus.HEALTHY, {}
        )
        assert isinstance(failures, list)
        
        # Test with additional data that should trigger failures
        additional_data = {
            'active_effects_count': 150,  # Too many
            'connected_clients': 1500,  # Too many
            'emoji_engine_running': False
        }
        
        failures = await detector._detect_endpoint_specific_failures(
            '/ws/emoji-rain', good_quality_metrics, HealthStatus.HEALTHY, additional_data
        )
        assert len(failures) > 0
        
        # Test observatory endpoint
        additional_data = {
            'observatory_health_score': 0.5,  # Low health score
            'metrics_collection_rate': 0.5  # Low collection rate
        }
        
        failures = await detector._detect_endpoint_specific_failures(
            '/ws/observatory', good_quality_metrics, HealthStatus.HEALTHY, additional_data
        )
        assert len(failures) > 0
        
        # Test anomalies endpoint
        additional_data = {
            'anomaly_detector_running': False,
            'active_anomalies_count': 100  # Too many
        }
        
        failures = await detector._detect_endpoint_specific_failures(
            '/ws/anomalies', good_quality_metrics, HealthStatus.HEALTHY, additional_data
        )
        assert len(failures) > 0
        
        # Test doctor status endpoint
        additional_data = {
            'ai_consultation_available': False,
            'doctor_available': False
        }
        
        failures = await detector._detect_endpoint_specific_failures(
            '/ws/doctor-status', good_quality_metrics, HealthStatus.HEALTHY, additional_data
        )
        assert len(failures) > 0
    
    def test_is_in_cooldown(self, detector):
        """Test cooldown mechanism."""
        endpoint = '/ws/test'
        rule_name = 'test_rule'
        
        # Not in cooldown initially
        assert detector._is_in_cooldown(endpoint, rule_name, 60.0) is False
        
        # Set last failure time
        detector._last_failure_times[endpoint] = {rule_name: datetime.utcnow()}
        
        # Should be in cooldown
        assert detector._is_in_cooldown(endpoint, rule_name, 60.0) is True
        
        # Should not be in cooldown after time passes
        detector._last_failure_times[endpoint][rule_name] = datetime.utcnow() - timedelta(seconds=70)
        assert detector._is_in_cooldown(endpoint, rule_name, 60.0) is False
    
    @pytest.mark.asyncio
    async def test_store_failure(self, detector):
        """Test storing failure in history."""
        failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='slow_response',
            severity='medium',
            description='Slow response'
        )
        
        await detector._store_failure('/ws/test', failure)
        
        assert '/ws/test' in detector._failure_history
        assert len(detector._failure_history['/ws/test']) == 1
        assert detector._failure_history['/ws/test'][0] == failure
    
    @pytest.mark.asyncio
    async def test_notify_failure_callbacks(self, detector):
        """Test failure callback notifications."""
        callback_called = False
        received_failure = None
        
        def callback(failure):
            nonlocal callback_called, received_failure
            callback_called = True
            received_failure = failure
        
        detector.add_failure_callback(callback)
        
        failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='slow_response',
            severity='medium',
            description='Slow response'
        )
        
        await detector._notify_failure_callbacks(failure)
        
        assert callback_called is True
        assert received_failure == failure
    
    @pytest.mark.asyncio
    async def test_callback_exception_handling(self, detector):
        """Test callback exception handling."""
        def bad_callback(failure):
            raise Exception("Callback error")
        
        detector.add_failure_callback(bad_callback)
        
        failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='slow_response',
            severity='medium',
            description='Slow response'
        )
        
        # Should not raise exception
        await detector._notify_failure_callbacks(failure)
    
    @pytest.mark.asyncio
    async def test_evaluate_custom_condition(self, detector, poor_quality_metrics):
        """Test custom condition evaluation."""
        # Test response time condition
        result = await detector._evaluate_custom_condition(
            'response_time_ms > 1000',
            '/ws/test',
            poor_quality_metrics,
            HealthStatus.HEALTHY,
            {}
        )
        assert result is True  # 2000 > 1000
        
        # Test error rate condition
        result = await detector._evaluate_custom_condition(
            'error_rate > 0.05',
            '/ws/test',
            poor_quality_metrics,
            HealthStatus.HEALTHY,
            {}
        )
        assert result is True  # 0.1 > 0.05
        
        # Test uptime condition
        result = await detector._evaluate_custom_condition(
            'uptime_percentage < 90',
            '/ws/test',
            poor_quality_metrics,
            HealthStatus.HEALTHY,
            {}
        )
        assert result is True  # 80 < 90


class TestFailureRule:
    """Test cases for FailureRule."""
    
    def test_to_dict(self):
        """Test FailureRule to_dict method."""
        rule = FailureRule(
            name='test_rule',
            failure_type=FailureType.SLOW_RESPONSE,
            severity=FailureSeverity.MEDIUM,
            condition='response_time_ms > 1000',
            threshold=1000.0,
            cooldown_seconds=300.0,
            enabled=True
        )
        
        rule_dict = rule.to_dict()
        
        assert rule_dict['name'] == 'test_rule'
        assert rule_dict['failure_type'] == 'slow_response'
        assert rule_dict['severity'] == 'medium'
        assert rule_dict['condition'] == 'response_time_ms > 1000'
        assert rule_dict['threshold'] == 1000.0
        assert rule_dict['cooldown_seconds'] == 300.0
        assert rule_dict['enabled'] is True


class TestFailureSeverity:
    """Test cases for FailureSeverity enum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert FailureSeverity.LOW.value == 'low'
        assert FailureSeverity.MEDIUM.value == 'medium'
        assert FailureSeverity.HIGH.value == 'high'
        assert FailureSeverity.CRITICAL.value == 'critical'


class TestFailureType:
    """Test cases for FailureType enum."""
    
    def test_enum_values(self):
        """Test enum values."""
        assert FailureType.CONNECTION_TIMEOUT.value == 'connection_timeout'
        assert FailureType.AUTHENTICATION_FAILURE.value == 'authentication_failure'
        assert FailureType.RATE_LIMIT_EXCEEDED.value == 'rate_limit_exceeded'
        assert FailureType.PROTOCOL_ERROR.value == 'protocol_error'
        assert FailureType.SLOW_RESPONSE.value == 'slow_response'
        assert FailureType.HIGH_LATENCY.value == 'high_latency'
        assert FailureType.HIGH_ERROR_RATE.value == 'high_error_rate'
        assert FailureType.LOW_UPTIME.value == 'low_uptime'
        assert FailureType.CONSECUTIVE_FAILURES.value == 'consecutive_failures'
        assert FailureType.ENDPOINT_SPECIFIC.value == 'endpoint_specific'
        assert FailureType.QUALITY_DEGRADATION.value == 'quality_degradation'
        assert FailureType.RESOURCE_EXHAUSTION.value == 'resource_exhaustion'