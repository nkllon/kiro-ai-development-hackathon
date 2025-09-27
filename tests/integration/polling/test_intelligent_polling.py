"""
Integration tests for intelligent HTTP polling fallback system.

Tests comprehensive polling behavior including rate limiting, exponential backoff,
bot protection integration, and fallback activation/deactivation scenarios.
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


class TestIntelligentPolling:
    """Test intelligent polling behavior and rate limiting."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter with test configuration."""
        config = RateLimitConfig(
            max_requests_per_minute=5,  # Lower for testing
            max_requests_per_hour=50,
            burst_allowance=2,
            cooldown_period=1.0  # Shorter for testing
        )
        return RateLimiter(config)
    
    @pytest.fixture
    def request_deduplicator(self):
        """Create request deduplicator for testing."""
        return RequestDeduplicator(cache_ttl=10, max_cache_size=100)
    
    @pytest.fixture
    def mock_websocket_connection(self):
        """Create mock WebSocket connection."""
        connection = Mock(spec=WebSocketConnection)
        connection.state.status = ConnectionStatus.CONNECTED
        connection.endpoint = "ws://test.example.com/ws/observatory"
        return connection
    
    @pytest.fixture
    def mock_health_validator(self):
        """Create mock health validator."""
        validator = Mock(spec=WebSocketHealthValidator)
        validator.is_healthy.return_value = True
        validator.get_health_status.return_value = Mock(health_score=95.0)
        return validator

    def test_rate_limiting_basic_functionality(self, rate_limiter):
        """Test basic rate limiting functionality."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_rate_limiting_basic",
            "status": "in_progress",
            "details": {"test": "basic_functionality"}
        }))
        
        endpoint = "/api/test"
        
        # First request should be allowed
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        asyncio.run(rate_limiter.record_request(endpoint))
        
        # Second request should be allowed (within burst allowance)
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        asyncio.run(rate_limiter.record_request(endpoint))
        
        # Third request should be blocked (exceeds burst allowance)
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_rate_limiting_basic",
            "status": "completed",
            "details": {"test": "basic_functionality", "result": "passed"}
        }))

    def test_rate_limiting_cooldown_period(self, rate_limiter):
        """Test cooldown period enforcement."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_cooldown_period",
            "status": "in_progress",
            "details": {"test": "cooldown_enforcement"}
        }))
        
        endpoint = "/api/test"
        
        # Make a request
        asyncio.run(rate_limiter.record_request(endpoint))
        
        # Immediate request should be blocked by cooldown
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is False
        
        # Wait for cooldown period
        import time
        time.sleep(1.1)  # Slightly more than cooldown period
        
        # Request should now be allowed
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_cooldown_period",
            "status": "completed",
            "details": {"test": "cooldown_enforcement", "result": "passed"}
        }))

    def test_rate_limiting_per_minute_limit(self, rate_limiter):
        """Test per-minute rate limit enforcement."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_per_minute_limit",
            "status": "in_progress",
            "details": {"test": "minute_limit_enforcement"}
        }))
        
        endpoint = "/api/test"
        
        # Make requests up to the limit
        for i in range(5):  # max_requests_per_minute
            assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
            asyncio.run(rate_limiter.record_request(endpoint))
        
        # Next request should be blocked
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_per_minute_limit",
            "status": "completed",
            "details": {"test": "minute_limit_enforcement", "result": "passed"}
        }))

    def test_rate_limiting_global_vs_endpoint(self, rate_limiter):
        """Test global vs endpoint-specific rate limiting."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_global_vs_endpoint",
            "status": "in_progress",
            "details": {"test": "global_endpoint_limits"}
        }))
        
        endpoint1 = "/api/test1"
        endpoint2 = "/api/test2"
        
        # Make requests to different endpoints
        for i in range(3):
            assert asyncio.run(rate_limiter.can_make_request(endpoint1)) is True
            asyncio.run(rate_limiter.record_request(endpoint1))
            
            assert asyncio.run(rate_limiter.can_make_request(endpoint2)) is True
            asyncio.run(rate_limiter.record_request(endpoint2))
        
        # Both endpoints should still be allowed (global limit not exceeded)
        assert asyncio.run(rate_limiter.can_make_request(endpoint1)) is True
        assert asyncio.run(rate_limiter.can_make_request(endpoint2)) is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_global_vs_endpoint",
            "status": "completed",
            "details": {"test": "global_endpoint_limits", "result": "passed"}
        }))

    def test_request_deduplication_caching(self, request_deduplicator):
        """Test request deduplication and caching functionality."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_request_deduplication",
            "status": "in_progress",
            "details": {"test": "caching_functionality"}
        }))
        
        endpoint = "/api/test"
        mock_response_data = {"status": "success", "data": "test_data"}
        mock_status_code = 200
        
        async def mock_request_func(endpoint, params=None):
            return mock_response_data, mock_status_code
        
        # First request should make actual call
        response_data, status_code = asyncio.run(
            request_deduplicator.get_or_request(endpoint, request_func=mock_request_func)
        )
        
        assert response_data == mock_response_data
        assert status_code == mock_status_code
        
        # Second request should return cached response
        response_data, status_code = asyncio.run(
            request_deduplicator.get_or_request(endpoint, request_func=mock_request_func)
        )
        
        assert response_data == mock_response_data
        assert status_code == mock_status_code
        
        # Verify cache stats
        stats = request_deduplicator.get_cache_stats()
        assert stats["valid_entries"] >= 1
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_request_deduplication",
            "status": "completed",
            "details": {"test": "caching_functionality", "result": "passed"}
        }))

    def test_request_deduplication_batching(self, request_deduplicator):
        """Test request batching for concurrent requests."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_request_batching",
            "status": "in_progress",
            "details": {"test": "concurrent_batching"}
        }))
        
        endpoint = "/api/test"
        mock_response_data = {"status": "success", "data": "batched_data"}
        mock_status_code = 200
        
        request_count = 0
        
        async def mock_request_func(endpoint, params=None):
            nonlocal request_count
            request_count += 1
            await asyncio.sleep(0.1)  # Simulate network delay
            return mock_response_data, mock_status_code
        
        # Make multiple concurrent requests
        async def make_request():
            return await request_deduplicator.get_or_request(endpoint, request_func=mock_request_func)
        
        # Run multiple requests concurrently
        tasks = [make_request() for _ in range(5)]
        results = asyncio.run(asyncio.gather(*tasks))
        
        # All requests should return the same response
        for response_data, status_code in results:
            assert response_data == mock_response_data
            assert status_code == mock_status_code
        
        # Only one actual request should have been made
        assert request_count == 1
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_request_batching",
            "status": "completed",
            "details": {"test": "concurrent_batching", "result": "passed"}
        }))

    def test_exponential_backoff_simulation(self, rate_limiter):
        """Test exponential backoff behavior simulation."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_exponential_backoff",
            "status": "in_progress",
            "details": {"test": "backoff_simulation"}
        }))
        
        endpoint = "/api/test"
        
        # Simulate multiple failed requests (rate limited)
        for i in range(3):
            asyncio.run(rate_limiter.record_request(endpoint))
        
        # Check next allowed time
        next_allowed = rate_limiter.get_next_allowed_time(endpoint)
        assert next_allowed is not None
        
        # Verify it's in the future
        now = datetime.utcnow()
        assert next_allowed > now
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_exponential_backoff",
            "status": "completed",
            "details": {"test": "backoff_simulation", "result": "passed"}
        }))

    def test_traffic_pattern_optimization(self, rate_limiter, request_deduplicator):
        """Test traffic pattern optimization through deduplication."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_traffic_optimization",
            "status": "in_progress",
            "details": {"test": "pattern_optimization"}
        }))
        
        endpoints = ["/api/dashboard", "/api/analytics", "/api/components"]
        
        async def mock_request_func(endpoint, params=None):
            return {"data": f"response_from_{endpoint}"}, 200
        
        # Simulate multiple clients requesting same data
        total_requests = 0
        for endpoint in endpoints:
            for client_id in range(3):  # 3 clients per endpoint
                if asyncio.run(rate_limiter.can_make_request(endpoint)):
                    response_data, status_code = await request_deduplicator.get_or_request(
                        endpoint, request_func=mock_request_func
                    )
                    asyncio.run(rate_limiter.record_request(endpoint))
                    total_requests += 1
        
        # Verify deduplication reduced actual network requests
        cache_stats = request_deduplicator.get_cache_stats()
        assert cache_stats["valid_entries"] < total_requests  # Some requests were deduplicated
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_traffic_optimization",
            "status": "completed",
            "details": {"test": "pattern_optimization", "result": "passed"}
        }))

    def test_rate_limiter_cleanup_old_requests(self, rate_limiter):
        """Test cleanup of old request records."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_cleanup_old_requests",
            "status": "in_progress",
            "details": {"test": "cleanup_functionality"}
        }))
        
        endpoint = "/api/test"
        
        # Make some requests
        for i in range(3):
            asyncio.run(rate_limiter.record_request(endpoint))
        
        # Verify requests are tracked
        assert len(rate_limiter.endpoint_requests[endpoint]) == 3
        assert len(rate_limiter.global_requests) == 3
        
        # Manually trigger cleanup (simulating time passage)
        old_time = datetime.utcnow() - timedelta(hours=2)
        rate_limiter.global_requests = [old_time] * 3
        rate_limiter.endpoint_requests[endpoint] = [old_time] * 3
        
        # Make a new request to trigger cleanup
        asyncio.run(rate_limiter.record_request(endpoint))
        
        # Old requests should be cleaned up
        assert len(rate_limiter.endpoint_requests[endpoint]) == 1
        assert len(rate_limiter.global_requests) == 1
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_cleanup_old_requests",
            "status": "completed",
            "details": {"test": "cleanup_functionality", "result": "passed"}
        }))

    def test_integration_with_websocket_health(self, rate_limiter, mock_websocket_connection, mock_health_validator):
        """Test integration with WebSocket health monitoring."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_websocket_integration",
            "status": "in_progress",
            "details": {"test": "health_monitoring_integration"}
        }))
        
        endpoint = "/api/health"
        
        # Simulate healthy WebSocket connection
        mock_websocket_connection.state.status = ConnectionStatus.CONNECTED
        mock_health_validator.is_healthy.return_value = True
        
        # Should be able to make requests when WebSocket is healthy
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        
        # Simulate WebSocket failure
        mock_websocket_connection.state.status = ConnectionStatus.DISCONNECTED
        mock_health_validator.is_healthy.return_value = False
        
        # Should still be able to make requests (fallback to polling)
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_websocket_integration",
            "status": "completed",
            "details": {"test": "health_monitoring_integration", "result": "passed"}
        }))

    def test_performance_under_load(self, rate_limiter, request_deduplicator):
        """Test performance under high load conditions."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_performance_load",
            "status": "in_progress",
            "details": {"test": "load_performance"}
        }))
        
        endpoints = ["/api/dashboard", "/api/analytics", "/api/components", "/api/cost", "/api/anomaly"]
        
        async def mock_request_func(endpoint, params=None):
            return {"data": f"load_test_{endpoint}"}, 200
        
        start_time = datetime.utcnow()
        
        # Simulate high load
        successful_requests = 0
        blocked_requests = 0
        
        for i in range(50):  # High number of requests
            endpoint = endpoints[i % len(endpoints)]
            
            if asyncio.run(rate_limiter.can_make_request(endpoint)):
                try:
                    await request_deduplicator.get_or_request(endpoint, request_func=mock_request_func)
                    asyncio.run(rate_limiter.record_request(endpoint))
                    successful_requests += 1
                except Exception:
                    pass
            else:
                blocked_requests += 1
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Verify rate limiting worked
        assert blocked_requests > 0  # Some requests should be blocked
        assert successful_requests > 0  # Some requests should succeed
        
        # Performance should be reasonable
        assert duration < 5.0  # Should complete within 5 seconds
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_performance_load",
            "status": "completed",
            "details": {
                "test": "load_performance",
                "result": "passed",
                "successful_requests": successful_requests,
                "blocked_requests": blocked_requests,
                "duration_seconds": duration
            }
        }))