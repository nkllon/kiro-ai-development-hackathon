"""Unit tests for WebSocket health validator."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.beast_mode.observatory.websocket.health_validator import (
    WebSocketHealthValidator,
    HealthStatus,
    QualityMetrics,
    FailureIndicator,
    HealthCheckResult
)


class TestWebSocketHealthValidator:
    """Test cases for WebSocketHealthValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a WebSocketHealthValidator instance."""
        return WebSocketHealthValidator(timeout=1.0, max_retries=2)
    
    @pytest.fixture
    def mock_quality_metrics(self):
        """Create mock quality metrics."""
        return QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
    
    def test_initialization(self, validator):
        """Test validator initialization."""
        assert validator.timeout == 1.0
        assert validator.max_retries == 2
        assert len(validator.endpoints) == 4
        assert '/ws/emoji-rain' in validator.endpoints
        assert '/ws/observatory' in validator.endpoints
        assert '/ws/anomalies' in validator.endpoints
        assert '/ws/doctor-status' in validator.endpoints
    
    @pytest.mark.asyncio
    async def test_validate_endpoint_health_success(self, validator):
        """Test successful endpoint health validation."""
        with patch.object(validator, '_test_connection') as mock_test, \
             patch.object(validator, '_collect_quality_metrics') as mock_quality, \
             patch.object(validator, '_detect_endpoint_failures') as mock_failures:
            
            mock_test.return_value = {"success": True, "response": {"type": "pong"}}
            mock_quality.return_value = QualityMetrics(
                endpoint='/ws/test',
                response_time_ms=100.0,
                connection_time_ms=200.0,
                message_latency_ms=50.0,
                throughput_bytes_per_sec=1000.0,
                error_rate=0.01,
                uptime_percentage=99.0
            )
            mock_failures.return_value = []
            
            result = await validator.validate_endpoint_health('/ws/test')
            
            assert isinstance(result, HealthCheckResult)
            assert result.endpoint == '/ws/test'
            assert result.status == HealthStatus.HEALTHY
            assert result.response_time_ms > 0
            assert result.quality_metrics is not None
            assert len(result.failure_indicators) == 0
    
    @pytest.mark.asyncio
    async def test_validate_endpoint_health_failure(self, validator):
        """Test endpoint health validation with failure."""
        with patch.object(validator, '_test_connection') as mock_test:
            mock_test.side_effect = Exception("Connection failed")
            
            result = await validator.validate_endpoint_health('/ws/test')
            
            assert isinstance(result, HealthCheckResult)
            assert result.endpoint == '/ws/test'
            assert result.status == HealthStatus.UNHEALTHY
            assert result.error_message is not None
            assert "Connection failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_check_connection_quality(self, validator):
        """Test connection quality check."""
        with patch('websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_websocket.send = AsyncMock()
            mock_websocket.recv = AsyncMock(return_value='{"type": "pong"}')
            mock_websocket.close = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            metrics = await validator.check_connection_quality('/ws/test')
            
            assert isinstance(metrics, QualityMetrics)
            assert metrics.endpoint == '/ws/test'
            assert metrics.response_time_ms > 0
            assert metrics.connection_time_ms > 0
            assert metrics.message_latency_ms > 0
            assert metrics.throughput_bytes_per_sec >= 0
    
    @pytest.mark.asyncio
    async def test_detect_endpoint_failures(self, validator, mock_quality_metrics):
        """Test endpoint failure detection."""
        # Test with good metrics
        failures = await validator.detect_endpoint_failures('/ws/test', mock_quality_metrics)
        assert len(failures) == 0
        
        # Test with poor metrics
        poor_metrics = QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=2000.0,  # Exceeds threshold
            connection_time_ms=6000.0,  # Exceeds threshold
            message_latency_ms=200.0,  # Exceeds threshold
            throughput_bytes_per_sec=500.0,
            error_rate=0.1,  # Exceeds threshold
            uptime_percentage=80.0  # Below threshold
        )
        
        failures = await validator.detect_endpoint_failures('/ws/test', poor_metrics)
        assert len(failures) > 0
        
        # Check specific failure types
        failure_types = [f.failure_type for f in failures]
        assert 'slow_response' in failure_types
        assert 'slow_connection' in failure_types
        assert 'high_latency' in failure_types
        assert 'high_error_rate' in failure_types
        assert 'low_uptime' in failure_types
    
    @pytest.mark.asyncio
    async def test_validate_all_endpoints(self, validator):
        """Test validation of all endpoints."""
        with patch.object(validator, 'validate_endpoint_health') as mock_validate:
            mock_result = HealthCheckResult(
                endpoint='/ws/test',
                status=HealthStatus.HEALTHY,
                response_time_ms=100.0
            )
            mock_validate.return_value = mock_result
            
            results = await validator.validate_all_endpoints()
            
            assert len(results) == 4
            for endpoint in validator.endpoints:
                assert endpoint in results
                assert isinstance(results[endpoint], HealthCheckResult)
    
    def test_get_health_summary(self, validator):
        """Test health summary generation."""
        # Test with no history
        summary = validator.get_health_summary()
        assert summary['overall_status'] == HealthStatus.UNKNOWN.value
        assert summary['total_endpoints'] == 4
        assert summary['healthy_endpoints'] == 0
        assert summary['unhealthy_endpoints'] == 4
        
        # Add some mock history
        mock_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        validator._health_history['/ws/test'] = [mock_result]
        
        summary = validator.get_health_summary()
        assert summary['healthy_endpoints'] == 1
        assert summary['unhealthy_endpoints'] == 3
    
    def test_determine_health_status(self, validator):
        """Test health status determination."""
        good_metrics = QualityMetrics(
            endpoint='/ws/test',
            response_time_ms=100.0,
            connection_time_ms=200.0,
            message_latency_ms=50.0,
            throughput_bytes_per_sec=1000.0,
            error_rate=0.01,
            uptime_percentage=99.0
        )
        
        # Test healthy status
        status = validator._determine_health_status(good_metrics, [])
        assert status == HealthStatus.HEALTHY
        
        # Test degraded status
        medium_failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='slow_response',
            severity='medium',
            description='Slow response'
        )
        status = validator._determine_health_status(good_metrics, [medium_failure])
        assert status == HealthStatus.DEGRADED
        
        # Test unhealthy status
        critical_failure = FailureIndicator(
            endpoint='/ws/test',
            failure_type='critical_error',
            severity='critical',
            description='Critical error'
        )
        status = validator._determine_health_status(good_metrics, [critical_failure])
        assert status == HealthStatus.UNHEALTHY
    
    def test_calculate_error_rate(self, validator):
        """Test error rate calculation."""
        # Test with no history
        error_rate = validator._calculate_error_rate('/ws/test')
        assert error_rate == 0.0
        
        # Add mock history
        healthy_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        unhealthy_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.UNHEALTHY,
            response_time_ms=100.0
        )
        
        validator._health_history['/ws/test'] = [healthy_result, unhealthy_result, healthy_result]
        
        error_rate = validator._calculate_error_rate('/ws/test')
        assert error_rate == 1/3  # 1 out of 3 failures
    
    def test_calculate_uptime_percentage(self, validator):
        """Test uptime percentage calculation."""
        # Test with no history
        uptime = validator._calculate_uptime_percentage('/ws/test')
        assert uptime == 100.0
        
        # Add mock history
        healthy_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        unhealthy_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.UNHEALTHY,
            response_time_ms=100.0
        )
        
        validator._health_history['/ws/test'] = [healthy_result, unhealthy_result, healthy_result]
        
        uptime = validator._calculate_uptime_percentage('/ws/test')
        assert uptime == (2/3) * 100  # 2 out of 3 healthy
    
    def test_count_consecutive_failures(self, validator):
        """Test consecutive failure counting."""
        # Test with no history
        count = validator._count_consecutive_failures('/ws/test')
        assert count == 0
        
        # Add mock history
        healthy_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.HEALTHY,
            response_time_ms=100.0
        )
        unhealthy_result = HealthCheckResult(
            endpoint='/ws/test',
            status=HealthStatus.UNHEALTHY,
            response_time_ms=100.0
        )
        
        validator._health_history['/ws/test'] = [
            healthy_result,
            unhealthy_result,
            unhealthy_result,
            unhealthy_result
        ]
        
        count = validator._count_consecutive_failures('/ws/test')
        assert count == 3  # Last 3 are failures
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, validator):
        """Test successful connection test."""
        with patch('websockets.connect') as mock_connect:
            mock_websocket = AsyncMock()
            mock_websocket.send = AsyncMock()
            mock_websocket.recv = AsyncMock(return_value='{"type": "pong"}')
            mock_websocket.close = AsyncMock()
            mock_connect.return_value = mock_websocket
            
            result = await validator._test_connection('/ws/test')
            
            assert result['success'] is True
            assert 'response' in result
    
    @pytest.mark.asyncio
    async def test_test_connection_timeout(self, validator):
        """Test connection timeout."""
        with patch('websockets.connect') as mock_connect:
            mock_connect.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(Exception):  # Should raise ConnectionTimeoutError
                await validator._test_connection('/ws/test')
    
    @pytest.mark.asyncio
    async def test_test_connection_auth_failure(self, validator):
        """Test authentication failure."""
        from websockets.exceptions import InvalidStatusCode
        
        with patch('websockets.connect') as mock_connect:
            mock_connect.side_effect = InvalidStatusCode(401, "Unauthorized")
            
            with pytest.raises(Exception):  # Should raise AuthenticationError
                await validator._test_connection('/ws/test')
    
    @pytest.mark.asyncio
    async def test_check_endpoint_specific_issues(self, validator):
        """Test endpoint-specific issue detection."""
        # Test emoji rain endpoint
        failures = await validator._check_endpoint_specific_issues('/ws/emoji-rain')
        assert isinstance(failures, list)
        
        # Test observatory endpoint
        failures = await validator._check_endpoint_specific_issues('/ws/observatory')
        assert isinstance(failures, list)
        
        # Test anomalies endpoint
        failures = await validator._check_endpoint_specific_issues('/ws/anomalies')
        assert isinstance(failures, list)
        
        # Test doctor status endpoint
        failures = await validator._check_endpoint_specific_issues('/ws/doctor-status')
        assert isinstance(failures, list)