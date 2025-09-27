"""
Unit tests for the RateLimiter class.

Tests individual rate limiting functionality, configuration validation,
and edge cases for HTTP polling fallback system.
"""

import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.beast_mode.observatory.polling.rate_limiter import RateLimiter, RateLimitConfig


class TestRateLimiter:
    """Test RateLimiter class functionality."""
    
    @pytest.fixture
    def default_config(self):
        """Create default rate limit configuration."""
        return RateLimitConfig()
    
    @pytest.fixture
    def custom_config(self):
        """Create custom rate limit configuration for testing."""
        return RateLimitConfig(
            max_requests_per_minute=5,
            max_requests_per_hour=50,
            burst_allowance=2,
            cooldown_period=1.0
        )
    
    @pytest.fixture
    def rate_limiter_default(self, default_config):
        """Create rate limiter with default configuration."""
        return RateLimiter(default_config)
    
    @pytest.fixture
    def rate_limiter_custom(self, custom_config):
        """Create rate limiter with custom configuration."""
        return RateLimiter(custom_config)

    def test_rate_limiter_initialization(self, rate_limiter_default):
        """Test rate limiter initialization."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_rate_limiter_init",
            "status": "in_progress",
            "details": {"test": "initialization"}
        }))
        
        # Verify initialization
        assert rate_limiter_default.config is not None
        assert rate_limiter_default.config.max_requests_per_minute == 12
        assert rate_limiter_default.config.max_requests_per_hour == 720
        assert rate_limiter_default.config.burst_allowance == 3
        assert rate_limiter_default.config.cooldown_period == 5.0
        
        # Verify internal state
        assert isinstance(rate_limiter_default.endpoint_requests, dict)
        assert isinstance(rate_limiter_default.global_requests, list)
        assert isinstance(rate_limiter_default.endpoint_cooldowns, dict)
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_rate_limiter_init",
            "status": "completed",
            "details": {"test": "initialization", "result": "passed"}
        }))

    def test_rate_limiter_custom_config(self, rate_limiter_custom):
        """Test rate limiter with custom configuration."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_custom_config",
            "status": "in_progress",
            "details": {"test": "custom_configuration"}
        }))
        
        # Verify custom configuration
        assert rate_limiter_custom.config.max_requests_per_minute == 5
        assert rate_limiter_custom.config.max_requests_per_hour == 50
        assert rate_limiter_custom.config.burst_allowance == 2
        assert rate_limiter_custom.config.cooldown_period == 1.0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_custom_config",
            "status": "completed",
            "details": {"test": "custom_configuration", "result": "passed"}
        }))

    def test_can_make_request_new_endpoint(self, rate_limiter_custom):
        """Test can_make_request for new endpoint."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_new_endpoint_request",
            "status": "in_progress",
            "details": {"test": "new_endpoint"}
        }))
        
        endpoint = "/api/new_endpoint"
        
        # New endpoint should be allowed
        result = asyncio.run(rate_limiter_custom.can_make_request(endpoint))
        assert result is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_new_endpoint_request",
            "status": "completed",
            "details": {"test": "new_endpoint", "result": "passed"}
        }))

    def test_record_request_functionality(self, rate_limiter_custom):
        """Test record_request functionality."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_record_request",
            "status": "in_progress",
            "details": {"test": "record_functionality"}
        }))
        
        endpoint = "/api/test"
        
        # Record a request
        asyncio.run(rate_limiter_custom.record_request(endpoint))
        
        # Verify request was recorded
        assert endpoint in rate_limiter_custom.endpoint_requests
        assert len(rate_limiter_custom.endpoint_requests[endpoint]) == 1
        assert len(rate_limiter_custom.global_requests) == 1
        assert endpoint in rate_limiter_custom.endpoint_cooldowns
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_record_request",
            "status": "completed",
            "details": {"test": "record_functionality", "result": "passed"}
        }))

    def test_burst_allowance_enforcement(self, rate_limiter_custom):
        """Test burst allowance enforcement."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_burst_allowance",
            "status": "in_progress",
            "details": {"test": "burst_enforcement"}
        }))
        
        endpoint = "/api/test"
        
        # Make requests up to burst allowance
        for i in range(2):  # burst_allowance = 2
            assert asyncio.run(rate_limiter_custom.can_make_request(endpoint)) is True
            asyncio.run(rate_limiter_custom.record_request(endpoint))
        
        # Next request should be blocked (exceeds burst allowance)
        assert asyncio.run(rate_limiter_custom.can_make_request(endpoint)) is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_burst_allowance",
            "status": "completed",
            "details": {"test": "burst_enforcement", "result": "passed"}
        }))

    def test_cooldown_period_enforcement(self, rate_limiter_custom):
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
        asyncio.run(rate_limiter_custom.record_request(endpoint))
        
        # Immediate request should be blocked by cooldown
        assert asyncio.run(rate_limiter_custom.can_make_request(endpoint)) is False
        
        # Wait for cooldown period
        import time
        time.sleep(1.1)  # Slightly more than cooldown_period
        
        # Request should now be allowed
        assert asyncio.run(rate_limiter_custom.can_make_request(endpoint)) is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_cooldown_period",
            "status": "completed",
            "details": {"test": "cooldown_enforcement", "result": "passed"}
        }))

    def test_per_minute_limit_enforcement(self, rate_limiter_custom):
        """Test per-minute limit enforcement."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_per_minute_limit",
            "status": "in_progress",
            "details": {"test": "minute_limit_enforcement"}
        }))
        
        endpoint = "/api/test"
        
        # Make requests up to the per-minute limit
        for i in range(5):  # max_requests_per_minute = 5
            assert asyncio.run(rate_limiter_custom.can_make_request(endpoint)) is True
            asyncio.run(rate_limiter_custom.record_request(endpoint))
        
        # Next request should be blocked
        assert asyncio.run(rate_limiter_custom.can_make_request(endpoint)) is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_per_minute_limit",
            "status": "completed",
            "details": {"test": "minute_limit_enforcement", "result": "passed"}
        }))

    def test_per_hour_limit_enforcement(self, rate_limiter_custom):
        """Test per-hour limit enforcement."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_per_hour_limit",
            "status": "in_progress",
            "details": {"test": "hour_limit_enforcement"}
        }))
        
        endpoint = "/api/test"
        
        # Make requests up to the per-hour limit
        for i in range(50):  # max_requests_per_hour = 50
            assert asyncio.run(rate_limiter_custom.can_make_request(endpoint)) is True
            asyncio.run(rate_limiter_custom.record_request(endpoint))
        
        # Next request should be blocked
        assert asyncio.run(rate_limiter_custom.can_make_request(endpoint)) is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_per_hour_limit",
            "status": "completed",
            "details": {"test": "hour_limit_enforcement", "result": "passed"}
        }))

    def test_get_next_allowed_time(self, rate_limiter_custom):
        """Test get_next_allowed_time functionality."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_next_allowed_time",
            "status": "in_progress",
            "details": {"test": "next_allowed_time"}
        }))
        
        endpoint = "/api/test"
        
        # Make a request to trigger cooldown
        asyncio.run(rate_limiter_custom.record_request(endpoint))
        
        # Get next allowed time
        next_allowed = rate_limiter_custom.get_next_allowed_time(endpoint)
        
        # Verify next allowed time is in the future
        assert next_allowed is not None
        assert next_allowed > datetime.utcnow()
        
        # Verify it's within cooldown period
        time_diff = (next_allowed - datetime.utcnow()).total_seconds()
        assert time_diff <= rate_limiter_custom.config.cooldown_period
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_next_allowed_time",
            "status": "completed",
            "details": {"test": "next_allowed_time", "result": "passed"}
        }))

    def test_multiple_endpoints_isolation(self, rate_limiter_custom):
        """Test that different endpoints are isolated."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_endpoint_isolation",
            "status": "in_progress",
            "details": {"test": "endpoint_isolation"}
        }))
        
        endpoint1 = "/api/test1"
        endpoint2 = "/api/test2"
        
        # Make requests to first endpoint
        for i in range(3):
            asyncio.run(rate_limiter_custom.record_request(endpoint1))
        
        # First endpoint should be blocked
        assert asyncio.run(rate_limiter_custom.can_make_request(endpoint1)) is False
        
        # Second endpoint should still be allowed
        assert asyncio.run(rate_limiter_custom.can_make_request(endpoint2)) is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_endpoint_isolation",
            "status": "completed",
            "details": {"test": "endpoint_isolation", "result": "passed"}
        }))

    def test_global_limit_affects_all_endpoints(self, rate_limiter_custom):
        """Test that global limit affects all endpoints."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_global_limit",
            "status": "in_progress",
            "details": {"test": "global_limit_effect"}
        }))
        
        endpoints = ["/api/test1", "/api/test2", "/api/test3"]
        
        # Make requests to exhaust global limit
        for endpoint in endpoints:
            for i in range(20):  # Total will exceed global limit
                if asyncio.run(rate_limiter_custom.can_make_request(endpoint)):
                    asyncio.run(rate_limiter_custom.record_request(endpoint))
        
        # All endpoints should eventually be blocked due to global limit
        for endpoint in endpoints:
            assert asyncio.run(rate_limiter_custom.can_make_request(endpoint)) is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_global_limit",
            "status": "completed",
            "details": {"test": "global_limit_effect", "result": "passed"}
        }))

    def test_cleanup_old_requests(self, rate_limiter_custom):
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
            asyncio.run(rate_limiter_custom.record_request(endpoint))
        
        # Verify requests are tracked
        assert len(rate_limiter_custom.endpoint_requests[endpoint]) == 3
        assert len(rate_limiter_custom.global_requests) == 3
        
        # Manually set old timestamps
        old_time = datetime.utcnow() - timedelta(hours=2)
        rate_limiter_custom.global_requests = [old_time] * 3
        rate_limiter_custom.endpoint_requests[endpoint] = [old_time] * 3
        
        # Make a new request to trigger cleanup
        asyncio.run(rate_limiter_custom.record_request(endpoint))
        
        # Old requests should be cleaned up
        assert len(rate_limiter_custom.endpoint_requests[endpoint]) == 1
        assert len(rate_limiter_custom.global_requests) == 1
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_cleanup_old_requests",
            "status": "completed",
            "details": {"test": "cleanup_functionality", "result": "passed"}
        }))

    def test_edge_case_empty_endpoint(self, rate_limiter_custom):
        """Test edge case with empty endpoint string."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_empty_endpoint",
            "status": "in_progress",
            "details": {"test": "empty_endpoint_edge_case"}
        }))
        
        empty_endpoint = ""
        
        # Should handle empty endpoint gracefully
        result = asyncio.run(rate_limiter_custom.can_make_request(empty_endpoint))
        assert result is True
        
        # Should be able to record request for empty endpoint
        asyncio.run(rate_limiter_custom.record_request(empty_endpoint))
        
        # Verify it was recorded
        assert empty_endpoint in rate_limiter_custom.endpoint_requests
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_empty_endpoint",
            "status": "completed",
            "details": {"test": "empty_endpoint_edge_case", "result": "passed"}
        }))

    def test_edge_case_none_endpoint(self, rate_limiter_custom):
        """Test edge case with None endpoint."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_none_endpoint",
            "status": "in_progress",
            "details": {"test": "none_endpoint_edge_case"}
        }))
        
        none_endpoint = None
        
        # Should handle None endpoint gracefully
        result = asyncio.run(rate_limiter_custom.can_make_request(none_endpoint))
        assert result is True
        
        # Should be able to record request for None endpoint
        asyncio.run(rate_limiter_custom.record_request(none_endpoint))
        
        # Verify it was recorded
        assert none_endpoint in rate_limiter_custom.endpoint_requests
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_none_endpoint",
            "status": "completed",
            "details": {"test": "none_endpoint_edge_case", "result": "passed"}
        }))

    def test_logging_functionality(self, rate_limiter_custom):
        """Test logging functionality."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_logging_functionality",
            "status": "in_progress",
            "details": {"test": "logging_functionality"}
        }))
        
        endpoint = "/api/test"
        
        # Test logging with print capture
        with patch('builtins.print') as mock_print:
            asyncio.run(rate_limiter_custom.can_make_request(endpoint))
            asyncio.run(rate_limiter_custom.record_request(endpoint))
            
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
                        if log_json.get("task") == "6.2" and "RateLimiter" in log_json.get("component", ""):
                            log_found = True
                            break
                    except json.JSONDecodeError:
                        continue
            
            assert log_found is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_logging_functionality",
            "status": "completed",
            "details": {"test": "logging_functionality", "result": "passed"}
        }))

    def test_concurrent_request_handling(self, rate_limiter_custom):
        """Test handling of concurrent requests."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_concurrent_requests",
            "status": "in_progress",
            "details": {"test": "concurrent_handling"}
        }))
        
        endpoint = "/api/test"
        
        async def make_request():
            if asyncio.run(rate_limiter_custom.can_make_request(endpoint)):
                asyncio.run(rate_limiter_custom.record_request(endpoint))
                return True
            return False
        
        # Make concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = asyncio.run(asyncio.gather(*tasks))
        
        # Some requests should succeed, some should be blocked
        successful_requests = sum(results)
        assert successful_requests > 0
        assert successful_requests <= rate_limiter_custom.config.burst_allowance
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_concurrent_requests",
            "status": "completed",
            "details": {
                "test": "concurrent_handling",
                "result": "passed",
                "successful_requests": successful_requests
            }
        }))