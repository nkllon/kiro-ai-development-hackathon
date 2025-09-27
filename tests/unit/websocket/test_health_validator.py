"""Unit tests for WebSocket health validator."""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import time

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.beast_mode.observatory.websocket.health_validator import (
    WebSocketHealthValidator,
    HealthStatus,
    QualityMetrics,
    FailureIndicator,
    HealthCheckResult
)
from src.beast_mode.observatory.websocket.exceptions import (
    ConnectionFailedError,
    ConnectionTimeoutError,
    AuthenticationError,
    RateLimitError,
    ProtocolError
)


class TestWebSocketHealthValidator:
    """Test cases for WebSocketHealthValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a WebSocketHealthValidator instance for testing."""
        return WebSocketHealthValidator(timeout=1.0, max_retries=2)
    
    def test_initialization(self, validator):
        """Test validator initialization."""
        assert validator.endpoints == [
            '/ws/emoji-rain',
            '/ws/observatory',
            '/ws/anomalies',
            '/ws/doctor-status'
        ]
        assert validator.timeout == 1.0
        assert validator.max_retries == 2
        assert validator._health_history == {}
        assert validator._quality_thresholds['response_time_ms'] == 1000.0
    
    @pytest.mark.asyncio
    async def test_validate_endpoint_health_success(self, validator):
        """Test successful endpoint health validation."""
        endpoint = '/ws/emoji-rain'
        
        with patch('websockets.connect') as mock_connect:
            # Mock successful connection
            mock_websocket = AsyncMock()
            mock_websocket.send = AsyncMock()
            mock_websocket.recv = AsyncMock(return_value='{"type": "pong"}')
            mock_websocket.close = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            result = await validator.validate_endpoint_health(endpoint)
            
            assert result.endpoint == endpoint
            assert result.status == HealthStatus.HEALTHY
            assert result.response_time_ms > 0
            assert result.error_message is None
            assert result.quality_metrics is not None
            assert endpoint in validator._health_history
    
    @pytest.mark.asyncio
    async def test_validate_endpoint_health_connection_timeout(self, validator):
        """Test endpoint health validation with connection timeout."""
        endpoint = '/ws/emoji-rain'
        
        with patch('websockets.connect') as mock_connect:
            mock_connect.side_effect = asyncio.TimeoutError()
            
            result = await validator.validate_endpoint_health(endpoint)
            
            assert result.endpoint == endpoint
            assert result.status == HealthStatus.UNHEALTHY
            assert result.error_message is not None
            assert "timeout" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_validate_endpoint_health_authentication_error(self, validator):
        """Test endpoint health validation with authentication error."""
        endpoint = '/ws/emoji-rain'
        
        with patch('websockets.connect') as mock_connect:
            from websockets.exceptions import InvalidStatusCode
            mock_connect.side_effect = InvalidStatusCode(401, "Unauthorized")
            
            result = await validator.validate_endpoint_health(endpoint)
            
            assert result.endpoint == endpoint
            assert result.status == HealthStatus.UNHEALTHY
            assert result.error_message is not None
            assert "authentication" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_validate_endpoint_health_rate_limit_error(self, validator):
        """Test endpoint health validation with rate limit error."""
        endpoint = '/ws/emoji-rain'
        
        with patch('websockets.connect') as mock_connect:
            from websockets.exceptions import InvalidStatusCode
            mock_connect.side_effect = InvalidStatusCode(429, "Too Many Requests")
            
            result = await validator.validate_endpoint_health(endpoint)
            
            assert result.endpoint == endpoint
            assert result.status == HealthStatus.UNHEALTHY
            assert result.error_message is not None
            assert "rate limit" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_check_connection_quality_success(self, validator):
        """Test successful connection quality check."""
        endpoint = '/ws/emoji-rain'
        
        with patch('websockets.connect') as mock_connect:
            # Mock successful connection with timing
            mock_websocket = AsyncMock()
            mock_websocket.send = AsyncMock()
            mock_websocket.recv = AsyncMock(return_value='{"type": "pong"}')
            mock_websocket.close = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            metrics = await validator.check_connection_quality(endpoint)
            
            assert metrics.endpoint == endpoint
            assert metrics.response_time_ms > 0
            assert metrics.connection_time_ms > 0
            assert metrics.message_latency_ms > 0
            assert metrics.throughput_bytes_per_sec >= 0
            assert metrics.error_rate >= 0
            assert metrics.uptime_percentage >= 0
    
    @pytest.mark.asyncio
    async def test_check_connection_quality_failure(self, validator):
        """Test connection quality check with failure."""
        endpoint = '/ws/emoji-rain'
        
        with patch('websockets.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            metrics = await validator.check_connection_quality(endpoint)
            
            assert metrics.endpoint == endpoint
            assert metrics.response_time_ms == float('inf')
            assert metrics.connection_time_ms == float('inf')
            assert metrics.message_latency_ms == float('inf')
            assert metrics.throughput_bytes_per_sec == 0.0
            assert metrics.error_rate == 1.0
            assert metrics.uptime_percentage == 0.0
    
    @pytest.mark.asyncio
    async def test_detect_endpoint_failures_no_failures(self, validator):
        """Test failure detection with no failures."""
        endpoint = '/ws/emoji-rain'
        
        # Create good quality metrics
        quality_metrics = QualityMetrics(
            endpoint=endpoint,
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        failures = await validator.detect_endpoint_failures(endpoint, quality_metrics)
        
        assert len(failures) == 0
    
    @pytest.mark.asyncio
    async def test_detect_endpoint_failures_slow_response(self, validator):
        """Test failure detection with slow response time."""
        endpoint = '/ws/emoji-rain'
        
        # Create quality metrics with slow response
        quality_metrics = QualityMetrics(
            endpoint=endpoint,
            response_time_ms=2000.0,  # Exceeds threshold
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        failures = await validator.detect_endpoint_failures(endpoint, quality_metrics)
        
        assert len(failures) > 0
        slow_response_failures = [f for f in failures if f.failure_type == "slow_response"]
        assert len(slow_response_failures) > 0
        assert slow_response_failures[0].severity == "medium"
    
    @pytest.mark.asyncio
    async def test_detect_endpoint_failures_high_error_rate(self, validator):
        """Test failure detection with high error rate."""
        endpoint = '/ws/emoji-rain'
        
        # Create quality metrics with high error rate
        quality_metrics = QualityMetrics(
            endpoint=endpoint,
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.1,  # Exceeds threshold
            uptime_percentage=99.0
        )
        
        failures = await validator.detect_endpoint_failures(endpoint, quality_metrics)
        
        assert len(failures) > 0
        error_rate_failures = [f for f in failures if f.failure_type == "high_error_rate"]
        assert len(error_rate_failures) > 0
        assert error_rate_failures[0].severity == "high"
    
    @pytest.mark.asyncio
    async def test_detect_endpoint_failures_low_uptime(self, validator):
        """Test failure detection with low uptime."""
        endpoint = '/ws/emoji-rain'
        
        # Create quality metrics with low uptime
        quality_metrics = QualityMetrics(
            endpoint=endpoint,
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=90.0  # Below threshold
        )
        
        failures = await validator.detect_endpoint_failures(endpoint, quality_metrics)
        
        assert len(failures) > 0
        uptime_failures = [f for f in failures if f.failure_type == "low_uptime"]
        assert len(uptime_failures) > 0
        assert uptime_failures[0].severity == "critical"
    
    @pytest.mark.asyncio
    async def test_detect_endpoint_failures_consecutive_failures(self, validator):
        """Test failure detection with consecutive failures."""
        endpoint = '/ws/emoji-rain'
        
        # Add consecutive failures to history
        for _ in range(3):
            validator._health_history[endpoint] = validator._health_history.get(endpoint, [])
            validator._health_history[endpoint].append(
                HealthCheckResult(
                    endpoint=endpoint,
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=1000.0
                )
            )
        
        failures = await validator.detect_endpoint_failures(endpoint)
        
        assert len(failures) > 0
        consecutive_failures = [f for f in failures if f.failure_type == "consecutive_failures"]
        assert len(consecutive_failures) > 0
        assert consecutive_failures[0].severity == "critical"
    
    @pytest.mark.asyncio
    async def test_validate_all_endpoints(self, validator):
        """Test validation of all endpoints."""
        with patch.object(validator, 'validate_endpoint_health') as mock_validate:
            # Mock successful results for all endpoints
            mock_results = []
            for endpoint in validator.endpoints:
                mock_result = HealthCheckResult(
                    endpoint=endpoint,
                    status=HealthStatus.HEALTHY,
                    response_time_ms=100.0
                )
                mock_results.append(mock_result)
            
            mock_validate.side_effect = mock_results
            
            results = await validator.validate_all_endpoints()
            
            assert len(results) == len(validator.endpoints)
            for endpoint in validator.endpoints:
                assert endpoint in results
                assert results[endpoint].status == HealthStatus.HEALTHY
    
    def test_get_health_summary_no_history(self, validator):
        """Test health summary with no history."""
        summary = validator.get_health_summary()
        
        assert summary["overall_status"] == HealthStatus.UNKNOWN.value
        assert summary["total_endpoints"] == len(validator.endpoints)
        assert summary["healthy_endpoints"] == 0
        assert summary["unhealthy_endpoints"] == len(validator.endpoints)
    
    def test_get_health_summary_with_history(self, validator):
        """Test health summary with history."""
        endpoint = '/ws/emoji-rain'
        
        # Add healthy result to history
        validator._health_history[endpoint] = [
            HealthCheckResult(
                endpoint=endpoint,
                status=HealthStatus.HEALTHY,
                response_time_ms=100.0
            )
        ]
        
        summary = validator.get_health_summary()
        
        assert summary["overall_status"] == HealthStatus.UNHEALTHY.value  # Other endpoints unknown
        assert summary["total_endpoints"] == len(validator.endpoints)
        assert summary["healthy_endpoints"] == 1
        assert summary["unhealthy_endpoints"] == len(validator.endpoints) - 1
    
    def test_determine_health_status_healthy(self, validator):
        """Test health status determination for healthy endpoint."""
        quality_metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        status = validator._determine_health_status(quality_metrics, [])
        
        assert status == HealthStatus.HEALTHY
    
    def test_determine_health_status_degraded(self, validator):
        """Test health status determination for degraded endpoint."""
        quality_metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        # Add high severity failure
        failure = FailureIndicator(
            endpoint='/ws/emoji-rain',
            failure_type="test_failure",
            severity="high",
            description="Test failure"
        )
        
        status = validator._determine_health_status(quality_metrics, [failure])
        
        assert status == HealthStatus.DEGRADED
    
    def test_determine_health_status_unhealthy(self, validator):
        """Test health status determination for unhealthy endpoint."""
        quality_metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        # Add critical failure
        failure = FailureIndicator(
            endpoint='/ws/emoji-rain',
            failure_type="test_failure",
            severity="critical",
            description="Test failure"
        )
        
        status = validator._determine_health_status(quality_metrics, [failure])
        
        assert status == HealthStatus.UNHEALTHY
    
    def test_calculate_error_rate(self, validator):
        """Test error rate calculation."""
        endpoint = '/ws/emoji-rain'
        
        # Add mixed results to history
        validator._health_history[endpoint] = [
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.HEALTHY, response_time_ms=100.0),
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.UNHEALTHY, response_time_ms=100.0),
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.HEALTHY, response_time_ms=100.0),
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.UNHEALTHY, response_time_ms=100.0),
        ]
        
        error_rate = validator._calculate_error_rate(endpoint)
        
        assert error_rate == 0.5  # 2 out of 4 failures
    
    def test_calculate_uptime_percentage(self, validator):
        """Test uptime percentage calculation."""
        endpoint = '/ws/emoji-rain'
        
        # Add mixed results to history
        validator._health_history[endpoint] = [
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.HEALTHY, response_time_ms=100.0),
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.HEALTHY, response_time_ms=100.0),
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.UNHEALTHY, response_time_ms=100.0),
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.HEALTHY, response_time_ms=100.0),
        ]
        
        uptime = validator._calculate_uptime_percentage(endpoint)
        
        assert uptime == 75.0  # 3 out of 4 healthy
    
    def test_count_consecutive_failures(self, validator):
        """Test consecutive failure counting."""
        endpoint = '/ws/emoji-rain'
        
        # Add results with consecutive failures at the end
        validator._health_history[endpoint] = [
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.HEALTHY, response_time_ms=100.0),
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.UNHEALTHY, response_time_ms=100.0),
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.UNHEALTHY, response_time_ms=100.0),
            HealthCheckResult(endpoint=endpoint, status=HealthStatus.UNHEALTHY, response_time_ms=100.0),
        ]
        
        consecutive = validator._count_consecutive_failures(endpoint)
        
        assert consecutive == 3
    
    @pytest.mark.asyncio
    async def test_check_endpoint_specific_issues(self, validator):
        """Test endpoint-specific issue checking."""
        endpoint = '/ws/emoji-rain'
        
        failures = await validator._check_endpoint_specific_issues(endpoint)
        
        # Should return empty list for now (no specific issues detected)
        assert isinstance(failures, list)
    
    def test_log_action(self, validator, capsys):
        """Test JSON logging functionality."""
        validator._log_action("test_action", {"test": "data"})
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.out.strip())
        
        assert log_data["task"] == "2.3"
        assert log_data["action"] == "health_validator_test_action"
        assert log_data["status"] == "in_progress"
        assert log_data["details"]["test"] == "data"
        assert "timestamp" in log_data


class TestQualityMetrics:
    """Test cases for QualityMetrics dataclass."""
    
    def test_quality_metrics_creation(self):
        """Test QualityMetrics creation."""
        metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        assert metrics.endpoint == '/ws/emoji-rain'
        assert metrics.response_time_ms == 100.0
        assert metrics.connection_time_ms == 200.0
        assert metrics.message_latency_ms == 50.0
        assert metrics.throughput_bytes_per_sec == 1000.0
        assert metrics.error_rate == 0.01
        assert metrics.uptime_percentage == 99.0
        assert isinstance(metrics.last_check, datetime)
    
    def test_quality_metrics_to_dict(self):
        """Test QualityMetrics to_dict method."""
        metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        data = metrics.to_dict()
        
        assert data["endpoint"] == '/ws/emoji-rain'
        assert data["response_time_ms"] == 100.0
        assert data["connection_time_ms"] == 200.0
        assert data["message_latency_ms"] == 50.0
        assert data["throughput_bytes_per_sec"] == 1000.0
        assert data["error_rate"] == 0.01
        assert data["uptime_percentage"] == 99.0
        assert "last_check" in data


class TestFailureIndicator:
    """Test cases for FailureIndicator dataclass."""
    
    def test_failure_indicator_creation(self):
        """Test FailureIndicator creation."""
        failure = FailureIndicator(
            endpoint='/ws/emoji-rain',
            failure_type='slow_response',
            severity='medium',
            description='Response time exceeds threshold',
            metadata={'response_time_ms': 2000.0}
        )
        
        assert failure.endpoint == '/ws/emoji-rain'
        assert failure.failure_type == 'slow_response'
        assert failure.severity == 'medium'
        assert failure.description == 'Response time exceeds threshold'
        assert failure.metadata['response_time_ms'] == 2000.0
        assert isinstance(failure.detected_at, datetime)
    
    def test_failure_indicator_to_dict(self):
        """Test FailureIndicator to_dict method."""
        failure = FailureIndicator(
            endpoint='/ws/emoji-rain',
            failure_type='slow_response',
            severity='medium',
            description='Response time exceeds threshold',
            metadata={'response_time_ms': 2000.0}
        )
        
        data = failure.to_dict()
        
        assert data["endpoint"] == '/ws/emoji-rain'
        assert data["failure_type"] == 'slow_response'
        assert data["severity"] == 'medium'
        assert data["description"] == 'Response time exceeds threshold'
        assert data["metadata"]["response_time_ms"] == 2000.0
        assert "detected_at" in data


class TestHealthCheckResult:
    """Test cases for HealthCheckResult dataclass."""
    
    def test_health_check_result_creation(self):
        """Test HealthCheckResult creation."""
        quality_metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        failure = FailureIndicator(
            endpoint='/ws/emoji-rain',
            failure_type='test_failure',
            severity='low',
            description='Test failure'
        )
        
        result = HealthCheckResult(
            endpoint='/ws/emoji-rain',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0,
            quality_metrics=quality_metrics,
            failure_indicators=[failure]
        )
        
        assert result.endpoint == '/ws/emoji-rain'
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time_ms == 100.0
        assert result.quality_metrics == quality_metrics
        assert len(result.failure_indicators) == 1
        assert isinstance(result.checked_at, datetime)
    
    def test_health_check_result_to_dict(self):
        """Test HealthCheckResult to_dict method."""
        quality_metrics = QualityMetrics(
            endpoint='/ws/emoji-rain',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        result = HealthCheckResult(
            endpoint='/ws/emoji-rain',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0,
            quality_metrics=quality_metrics
        )
        
        data = result.to_dict()
        
        assert data["endpoint"] == '/ws/emoji-rain'
        assert data["status"] == HealthStatus.HEALTHY.value
        assert data["response_time_ms"] == 100.0
        assert data["quality_metrics"] is not None
        assert data["quality_metrics"]["endpoint"] == '/ws/emoji-rain'
        assert "checked_at" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])