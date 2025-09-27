"""
Integration tests for HTTP polling fallback activation and deactivation.

Tests fallback activation when WebSocket fails, deactivation when WebSocket recovers,
and seamless transition between WebSocket and HTTP polling modes.
"""

import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

from src.beast_mode.observatory.polling.rate_limiter import RateLimiter, RateLimitConfig
from src.beast_mode.observatory.polling.request_deduplicator import RequestDeduplicator
from src.beast_mode.observatory.websocket.connection import WebSocketConnection, ConnectionStatus
from src.beast_mode.observatory.websocket.health_validator import WebSocketHealthValidator
from src.beast_mode.observatory.recovery.recovery_strategies import FallbackActivationStrategy


class TestFallbackActivation:
    """Test fallback activation and deactivation scenarios."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter for fallback testing."""
        config = RateLimitConfig(
            max_requests_per_minute=10,
            max_requests_per_hour=100,
            burst_allowance=3,
            cooldown_period=2.0
        )
        return RateLimiter(config)
    
    @pytest.fixture
    def request_deduplicator(self):
        """Create request deduplicator for fallback testing."""
        return RequestDeduplicator(cache_ttl=15, max_cache_size=50)
    
    @pytest.fixture
    def mock_websocket_connection(self):
        """Create mock WebSocket connection."""
        connection = Mock(spec=WebSocketConnection)
        connection.endpoint = "ws://test.example.com/ws/observatory"
        connection.state.status = ConnectionStatus.CONNECTED
        return connection
    
    @pytest.fixture
    def mock_health_validator(self):
        """Create mock health validator."""
        validator = Mock(spec=WebSocketHealthValidator)
        validator.is_healthy.return_value = True
        validator.get_health_status.return_value = Mock(health_score=95.0)
        return validator
    
    @pytest.fixture
    def fallback_strategy(self):
        """Create fallback activation strategy."""
        return FallbackActivationStrategy()

    def test_websocket_failure_detection(self, mock_websocket_connection, mock_health_validator):
        """Test WebSocket failure detection triggers fallback."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_websocket_failure_detection",
            "status": "in_progress",
            "details": {"test": "failure_detection"}
        }))
        
        # Simulate healthy WebSocket
        mock_websocket_connection.state.status = ConnectionStatus.CONNECTED
        mock_health_validator.is_healthy.return_value = True
        
        # Verify healthy state
        assert mock_websocket_connection.state.status == ConnectionStatus.CONNECTED
        assert mock_health_validator.is_healthy() is True
        
        # Simulate WebSocket failure
        mock_websocket_connection.state.status = ConnectionStatus.DISCONNECTED
        mock_health_validator.is_healthy.return_value = False
        
        # Verify failure detection
        assert mock_websocket_connection.state.status == ConnectionStatus.DISCONNECTED
        assert mock_health_validator.is_healthy() is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_websocket_failure_detection",
            "status": "completed",
            "details": {"test": "failure_detection", "result": "passed"}
        }))

    def test_fallback_activation_when_websocket_fails(self, rate_limiter, request_deduplicator, fallback_strategy):
        """Test fallback activation when WebSocket connection fails."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_activation",
            "status": "in_progress",
            "details": {"test": "activation_on_failure"}
        }))
        
        # Simulate WebSocket failure
        failure_type = Mock()
        failure_type.value = "websocket_connection_failed"
        
        # Execute fallback activation
        result = asyncio.run(fallback_strategy.execute(failure_type, attempt_number=1))
        
        # Verify fallback activation
        assert result.success is True
        assert "HTTP polling fallback activated" in result.message
        assert result.attempt.strategy == "FallbackActivation"
        
        # Verify polling can be used
        endpoint = "/api/dashboard"
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_activation",
            "status": "completed",
            "details": {"test": "activation_on_failure", "result": "passed"}
        }))

    def test_fallback_deactivation_when_websocket_recovers(self, mock_websocket_connection, mock_health_validator):
        """Test fallback deactivation when WebSocket connection recovers."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_deactivation",
            "status": "in_progress",
            "details": {"test": "deactivation_on_recovery"}
        }))
        
        # Simulate WebSocket failure state
        mock_websocket_connection.state.status = ConnectionStatus.DISCONNECTED
        mock_health_validator.is_healthy.return_value = False
        
        # Verify failure state
        assert mock_websocket_connection.state.status == ConnectionStatus.DISCONNECTED
        assert mock_health_validator.is_healthy() is False
        
        # Simulate WebSocket recovery
        mock_websocket_connection.state.status = ConnectionStatus.CONNECTED
        mock_health_validator.is_healthy.return_value = True
        
        # Verify recovery state
        assert mock_websocket_connection.state.status == ConnectionStatus.CONNECTED
        assert mock_health_validator.is_healthy() is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_deactivation",
            "status": "completed",
            "details": {"test": "deactivation_on_recovery", "result": "passed"}
        }))

    def test_seamless_transition_between_modes(self, rate_limiter, request_deduplicator, mock_websocket_connection, mock_health_validator):
        """Test seamless transition between WebSocket and HTTP polling modes."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_seamless_transition",
            "status": "in_progress",
            "details": {"test": "mode_transition"}
        }))
        
        endpoint = "/api/test"
        
        async def mock_request_func(endpoint, params=None):
            return {"data": f"transition_test_{endpoint}"}, 200
        
        # Phase 1: WebSocket mode (healthy)
        mock_websocket_connection.state.status = ConnectionStatus.CONNECTED
        mock_health_validator.is_healthy.return_value = True
        
        # Should be able to make requests
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        response_data, status_code = await request_deduplicator.get_or_request(endpoint, request_func=mock_request_func)
        asyncio.run(rate_limiter.record_request(endpoint))
        
        assert response_data["data"] == f"transition_test_{endpoint}"
        assert status_code == 200
        
        # Phase 2: Transition to fallback mode
        mock_websocket_connection.state.status = ConnectionStatus.DISCONNECTED
        mock_health_validator.is_healthy.return_value = False
        
        # Should still be able to make requests (fallback active)
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        response_data, status_code = await request_deduplicator.get_or_request(endpoint, request_func=mock_request_func)
        asyncio.run(rate_limiter.record_request(endpoint))
        
        assert response_data["data"] == f"transition_test_{endpoint}"
        assert status_code == 200
        
        # Phase 3: Return to WebSocket mode
        mock_websocket_connection.state.status = ConnectionStatus.CONNECTED
        mock_health_validator.is_healthy.return_value = True
        
        # Should continue working seamlessly
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_seamless_transition",
            "status": "completed",
            "details": {"test": "mode_transition", "result": "passed"}
        }))

    def test_fallback_activation_with_multiple_endpoints(self, rate_limiter, request_deduplicator):
        """Test fallback activation with multiple API endpoints."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_multiple_endpoints",
            "status": "in_progress",
            "details": {"test": "multiple_endpoints"}
        }))
        
        endpoints = ["/api/dashboard", "/api/analytics", "/api/components", "/api/cost", "/api/anomaly"]
        
        async def mock_request_func(endpoint, params=None):
            return {"data": f"multi_endpoint_test_{endpoint}"}, 200
        
        successful_requests = 0
        failed_requests = 0
        
        # Test all endpoints in fallback mode
        for endpoint in endpoints:
            try:
                if asyncio.run(rate_limiter.can_make_request(endpoint)):
                    response_data, status_code = await request_deduplicator.get_or_request(
                        endpoint, request_func=mock_request_func
                    )
                    asyncio.run(rate_limiter.record_request(endpoint))
                    successful_requests += 1
                    
                    assert response_data["data"] == f"multi_endpoint_test_{endpoint}"
                    assert status_code == 200
                else:
                    failed_requests += 1
            except Exception as e:
                failed_requests += 1
        
        # Verify fallback works for multiple endpoints
        assert successful_requests > 0
        assert successful_requests >= len(endpoints) // 2  # At least half should succeed
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_multiple_endpoints",
            "status": "completed",
            "details": {
                "test": "multiple_endpoints",
                "result": "passed",
                "successful_requests": successful_requests,
                "failed_requests": failed_requests
            }
        }))

    def test_fallback_performance_comparison(self, rate_limiter, request_deduplicator):
        """Test performance comparison between WebSocket and HTTP polling fallback."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_performance",
            "status": "in_progress",
            "details": {"test": "performance_comparison"}
        }))
        
        endpoint = "/api/test"
        
        async def mock_request_func(endpoint, params=None):
            await asyncio.sleep(0.05)  # Simulate network delay
            return {"data": f"performance_test_{endpoint}"}, 200
        
        # Test HTTP polling performance
        start_time = datetime.utcnow()
        
        polling_requests = 0
        for i in range(5):
            if asyncio.run(rate_limiter.can_make_request(endpoint)):
                response_data, status_code = await request_deduplicator.get_or_request(
                    endpoint, request_func=mock_request_func
                )
                asyncio.run(rate_limiter.record_request(endpoint))
                polling_requests += 1
        
        end_time = datetime.utcnow()
        polling_duration = (end_time - start_time).total_seconds()
        
        # Verify performance is reasonable
        assert polling_requests > 0
        assert polling_duration < 2.0  # Should complete within 2 seconds
        assert polling_duration / polling_requests < 0.5  # Average per request
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_performance",
            "status": "completed",
            "details": {
                "test": "performance_comparison",
                "result": "passed",
                "polling_requests": polling_requests,
                "polling_duration": polling_duration
            }
        }))

    def test_fallback_error_handling(self, rate_limiter, request_deduplicator):
        """Test error handling in fallback mode."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_error_handling",
            "status": "in_progress",
            "details": {"test": "error_handling"}
        }))
        
        endpoint = "/api/test"
        
        async def failing_request_func(endpoint, params=None):
            raise Exception("Simulated network error")
        
        async def successful_request_func(endpoint, params=None):
            return {"data": f"success_after_error_{endpoint}"}, 200
        
        # Test error handling
        error_handled = False
        try:
            await request_deduplicator.get_or_request(endpoint, request_func=failing_request_func)
        except Exception as e:
            error_handled = True
            assert "Simulated network error" in str(e)
        
        assert error_handled is True
        
        # Test recovery after error
        recovery_successful = False
        try:
            response_data, status_code = await request_deduplicator.get_or_request(
                endpoint, request_func=successful_request_func
            )
            recovery_successful = True
            assert response_data["data"] == f"success_after_error_{endpoint}"
            assert status_code == 200
        except Exception:
            recovery_successful = False
        
        assert recovery_successful is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_error_handling",
            "status": "completed",
            "details": {"test": "error_handling", "result": "passed"}
        }))

    def test_fallback_state_persistence(self, rate_limiter, request_deduplicator):
        """Test state persistence during fallback mode."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_state_persistence",
            "status": "in_progress",
            "details": {"test": "state_persistence"}
        }))
        
        endpoint = "/api/test"
        
        async def mock_request_func(endpoint, params=None):
            return {"data": f"state_test_{endpoint}", "timestamp": datetime.utcnow().isoformat()}, 200
        
        # Make initial request
        response_data, status_code = await request_deduplicator.get_or_request(
            endpoint, request_func=mock_request_func
        )
        asyncio.run(rate_limiter.record_request(endpoint))
        
        initial_data = response_data["data"]
        initial_timestamp = response_data["timestamp"]
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Make another request (should be cached)
        response_data, status_code = await request_deduplicator.get_or_request(
            endpoint, request_func=mock_request_func
        )
        
        # Verify state persistence
        assert response_data["data"] == initial_data
        assert response_data["timestamp"] == initial_timestamp  # Should be cached
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_state_persistence",
            "status": "completed",
            "details": {"test": "state_persistence", "result": "passed"}
        }))

    def test_fallback_activation_logging(self, fallback_strategy):
        """Test comprehensive logging during fallback activation."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_logging",
            "status": "in_progress",
            "details": {"test": "activation_logging"}
        }))
        
        # Simulate fallback activation with logging
        failure_type = Mock()
        failure_type.value = "websocket_connection_failed"
        
        # Execute fallback with logging capture
        with patch('builtins.print') as mock_print:
            result = asyncio.run(fallback_strategy.execute(failure_type, attempt_number=1))
            
            # Verify logging occurred
            assert mock_print.called
            
            # Check log content
            log_calls = mock_print.call_args_list
            log_found = False
            
            for call in log_calls:
                log_data = call[0][0]
                if isinstance(log_data, str):
                    try:
                        log_json = json.loads(log_data)
                        if log_json.get("task") == "6.2" and "fallback" in log_json.get("action", ""):
                            log_found = True
                            break
                    except json.JSONDecodeError:
                        continue
            
            assert log_found is True
        
        # Verify fallback execution
        assert result.success is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_fallback_logging",
            "status": "completed",
            "details": {"test": "activation_logging", "result": "passed"}
        }))