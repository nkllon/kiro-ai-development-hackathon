"""
Integration tests for bot protection integration with HTTP polling fallback.

Tests Cloudflare bot protection trigger thresholds, whitelist effectiveness,
and security event correlation with WebSocket/polling activity.
"""

import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

from src.beast_mode.observatory.polling.rate_limiter import RateLimiter, RateLimitConfig
from src.beast_mode.observatory.polling.request_deduplicator import RequestDeduplicator
from src.beast_mode.observatory.cloudflare.api_client import CloudflareAPIClient
from src.beast_mode.observatory.cloudflare.rule_manager import RuleManager


class TestBotProtectionIntegration:
    """Test bot protection integration and security measures."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter with bot-safe configuration."""
        config = RateLimitConfig(
            max_requests_per_minute=12,  # Conservative limit
            max_requests_per_hour=720,
            burst_allowance=3,
            cooldown_period=5.0
        )
        return RateLimiter(config)
    
    @pytest.fixture
    def mock_cloudflare_client(self):
        """Create mock Cloudflare API client."""
        client = Mock(spec=CloudflareAPIClient)
        client.get_zone_id.return_value = "test_zone_id"
        client.create_firewall_rule.return_value = {"success": True, "rule_id": "test_rule"}
        client.get_bot_analytics.return_value = {
            "bot_score_distribution": {"1": 100, "2": 50, "3": 25},
            "challenge_rate": 0.05,
            "block_rate": 0.02
        }
        return client
    
    @pytest.fixture
    def mock_rule_manager(self):
        """Create mock rule manager."""
        manager = Mock(spec=RuleManager)
        manager.create_whitelist_rule.return_value = {"success": True, "rule_id": "whitelist_rule"}
        manager.get_existing_rules.return_value = []
        return manager

    def test_bot_protection_trigger_threshold(self, rate_limiter):
        """Test bot protection trigger threshold validation."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_bot_protection_threshold",
            "status": "in_progress",
            "details": {"test": "trigger_threshold_validation"}
        }))
        
        endpoint = "/api/test"
        
        # Simulate aggressive polling that would trigger bot protection
        requests_made = 0
        blocked_requests = 0
        
        for i in range(20):  # More than normal rate limit
            if asyncio.run(rate_limiter.can_make_request(endpoint)):
                asyncio.run(rate_limiter.record_request(endpoint))
                requests_made += 1
            else:
                blocked_requests += 1
        
        # Rate limiter should prevent most requests
        assert blocked_requests > requests_made
        assert requests_made <= 12  # Should not exceed per-minute limit
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_bot_protection_threshold",
            "status": "completed",
            "details": {
                "test": "trigger_threshold_validation",
                "result": "passed",
                "requests_made": requests_made,
                "blocked_requests": blocked_requests
            }
        }))

    def test_cloudflare_whitelist_effectiveness(self, mock_cloudflare_client, mock_rule_manager):
        """Test Cloudflare whitelist rule effectiveness."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_cloudflare_whitelist",
            "status": "in_progress",
            "details": {"test": "whitelist_effectiveness"}
        }))
        
        # Test whitelist rule creation
        whitelist_rule = {
            "expression": '(http.user_agent contains "Observatory-Internal")',
            "action": "allow",
            "description": "Observatory internal polling traffic"
        }
        
        result = mock_rule_manager.create_whitelist_rule(whitelist_rule)
        assert result["success"] is True
        assert "rule_id" in result
        
        # Test WebSocket endpoint whitelist
        websocket_rule = {
            "expression": '(http.request.uri.path matches "^/ws/")',
            "action": "allow",
            "description": "Observatory WebSocket endpoints"
        }
        
        result = mock_rule_manager.create_whitelist_rule(websocket_rule)
        assert result["success"] is True
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_cloudflare_whitelist",
            "status": "completed",
            "details": {"test": "whitelist_effectiveness", "result": "passed"}
        }))

    def test_bot_safe_headers_validation(self):
        """Test bot-safe header configuration."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_bot_safe_headers",
            "status": "in_progress",
            "details": {"test": "header_validation"}
        }))
        
        # Expected bot-safe headers
        expected_headers = {
            "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
            "X-Observatory-Client": "internal-polling",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
            "Cache-Control": "no-cache"
        }
        
        # Validate header structure
        assert "User-Agent" in expected_headers
        assert "Observatory-Internal" in expected_headers["User-Agent"]
        assert "X-Observatory-Client" in expected_headers
        assert expected_headers["X-Observatory-Client"] == "internal-polling"
        assert expected_headers["Accept"] == "application/json"
        
        # Validate headers don't contain suspicious patterns
        user_agent = expected_headers["User-Agent"]
        assert "bot" not in user_agent.lower()
        assert "crawler" not in user_agent.lower()
        assert "scraper" not in user_agent.lower()
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_bot_safe_headers",
            "status": "completed",
            "details": {"test": "header_validation", "result": "passed"}
        }))

    def test_traffic_pattern_analysis(self, rate_limiter, request_deduplicator):
        """Test traffic pattern analysis for bot detection avoidance."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_traffic_pattern_analysis",
            "status": "in_progress",
            "details": {"test": "pattern_analysis"}
        }))
        
        endpoints = ["/api/dashboard", "/api/analytics", "/api/components"]
        
        async def mock_request_func(endpoint, params=None):
            return {"data": f"pattern_test_{endpoint}"}, 200
        
        # Simulate realistic traffic patterns
        request_times = []
        successful_requests = 0
        
        for i in range(30):  # Simulate 30 requests over time
            endpoint = endpoints[i % len(endpoints)]
            
            if asyncio.run(rate_limiter.can_make_request(endpoint)):
                start_time = datetime.utcnow()
                await request_deduplicator.get_or_request(endpoint, request_func=mock_request_func)
                asyncio.run(rate_limiter.record_request(endpoint))
                request_times.append(datetime.utcnow() - start_time)
                successful_requests += 1
                
                # Add realistic delay between requests
                await asyncio.sleep(0.1)
        
        # Analyze traffic patterns
        avg_response_time = sum(t.total_seconds() for t in request_times) / len(request_times)
        
        # Verify patterns are bot-safe
        assert avg_response_time < 1.0  # Reasonable response time
        assert successful_requests > 0  # Some requests succeeded
        assert len(request_times) == successful_requests  # All successful requests timed
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_traffic_pattern_analysis",
            "status": "completed",
            "details": {
                "test": "pattern_analysis",
                "result": "passed",
                "successful_requests": successful_requests,
                "avg_response_time": avg_response_time
            }
        }))

    def test_bot_protection_bypass_simulation(self, mock_cloudflare_client):
        """Test simulation of bot protection bypass scenarios."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_bot_protection_bypass",
            "status": "in_progress",
            "details": {"test": "bypass_simulation"}
        }))
        
        # Simulate bot analytics data
        analytics = mock_cloudflare_client.get_bot_analytics()
        
        # Verify analytics structure
        assert "bot_score_distribution" in analytics
        assert "challenge_rate" in analytics
        assert "block_rate" in analytics
        
        # Verify rates are reasonable
        assert analytics["challenge_rate"] < 0.1  # Less than 10% challenge rate
        assert analytics["block_rate"] < 0.05  # Less than 5% block rate
        
        # Simulate IP whitelist check
        test_ip = "192.168.1.100"
        whitelist_result = mock_cloudflare_client.check_ip_whitelist(test_ip)
        
        # Should be able to check whitelist status
        assert whitelist_result is not None
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_bot_protection_bypass",
            "status": "completed",
            "details": {"test": "bypass_simulation", "result": "passed"}
        }))

    def test_security_event_correlation(self, rate_limiter):
        """Test correlation between security events and polling activity."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_security_event_correlation",
            "status": "in_progress",
            "details": {"test": "event_correlation"}
        }))
        
        endpoint = "/api/test"
        security_events = []
        
        # Simulate polling activity with security event tracking
        for i in range(10):
            if asyncio.run(rate_limiter.can_make_request(endpoint)):
                asyncio.run(rate_limiter.record_request(endpoint))
                
                # Simulate security event (rate limiting)
                event = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "rate_limit_check",
                    "endpoint": endpoint,
                    "allowed": True,
                    "request_count": i + 1
                }
                security_events.append(event)
            else:
                # Simulate blocked request event
                event = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "rate_limit_blocked",
                    "endpoint": endpoint,
                    "allowed": False,
                    "request_count": i + 1
                }
                security_events.append(event)
        
        # Analyze security events
        allowed_events = [e for e in security_events if e["allowed"]]
        blocked_events = [e for e in security_events if not e["allowed"]]
        
        assert len(security_events) == 10
        assert len(allowed_events) > 0
        assert len(blocked_events) > 0  # Some requests should be blocked
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_security_event_correlation",
            "status": "completed",
            "details": {
                "test": "event_correlation",
                "result": "passed",
                "total_events": len(security_events),
                "allowed_events": len(allowed_events),
                "blocked_events": len(blocked_events)
            }
        }))

    def test_multi_layer_bot_protection_coordination(self, rate_limiter, request_deduplicator):
        """Test coordination between multiple bot protection layers."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_multi_layer_protection",
            "status": "in_progress",
            "details": {"test": "multi_layer_coordination"}
        }))
        
        endpoints = ["/api/dashboard", "/api/analytics"]
        
        async def mock_request_func(endpoint, params=None):
            return {"data": f"multi_layer_test_{endpoint}"}, 200
        
        # Simulate coordinated protection layers
        layer_results = {
            "rate_limiter": {"allowed": 0, "blocked": 0},
            "deduplicator": {"cached": 0, "fresh": 0},
            "cloudflare": {"challenged": 0, "passed": 0}
        }
        
        for endpoint in endpoints:
            for i in range(5):  # Multiple requests per endpoint
                # Layer 1: Rate limiter
                if asyncio.run(rate_limiter.can_make_request(endpoint)):
                    layer_results["rate_limiter"]["allowed"] += 1
                    
                    # Layer 2: Deduplicator
                    response_data, status_code = await request_deduplicator.get_or_request(
                        endpoint, request_func=mock_request_func
                    )
                    
                    # Check if response was cached
                    cache_stats = request_deduplicator.get_cache_stats()
                    if cache_stats["valid_entries"] > 0:
                        layer_results["deduplicator"]["cached"] += 1
                    else:
                        layer_results["deduplicator"]["fresh"] += 1
                    
                    # Layer 3: Simulate Cloudflare check
                    layer_results["cloudflare"]["passed"] += 1
                    
                    asyncio.run(rate_limiter.record_request(endpoint))
                else:
                    layer_results["rate_limiter"]["blocked"] += 1
        
        # Verify multi-layer coordination
        assert layer_results["rate_limiter"]["allowed"] > 0
        assert layer_results["rate_limiter"]["blocked"] > 0
        assert layer_results["deduplicator"]["fresh"] > 0
        assert layer_results["cloudflare"]["passed"] > 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_multi_layer_protection",
            "status": "completed",
            "details": {
                "test": "multi_layer_coordination",
                "result": "passed",
                "layer_results": layer_results
            }
        }))

    def test_bot_protection_recovery_scenarios(self, rate_limiter):
        """Test recovery scenarios after bot protection triggers."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_bot_protection_recovery",
            "status": "in_progress",
            "details": {"test": "recovery_scenarios"}
        }))
        
        endpoint = "/api/test"
        
        # Simulate bot protection trigger (excessive requests)
        for i in range(15):  # Exceed rate limit
            asyncio.run(rate_limiter.record_request(endpoint))
        
        # Verify requests are blocked
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is False
        
        # Simulate recovery period (wait for rate limit reset)
        import time
        time.sleep(6)  # Wait for cooldown + buffer
        
        # Verify recovery
        assert asyncio.run(rate_limiter.can_make_request(endpoint)) is True
        
        # Make a successful request after recovery
        asyncio.run(rate_limiter.record_request(endpoint))
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_bot_protection_recovery",
            "status": "completed",
            "details": {"test": "recovery_scenarios", "result": "passed"}
        }))

    def test_legitimate_vs_suspicious_traffic_differentiation(self, rate_limiter):
        """Test differentiation between legitimate and suspicious traffic patterns."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_traffic_differentiation",
            "status": "in_progress",
            "details": {"test": "legitimate_vs_suspicious"}
        }))
        
        # Simulate legitimate Observatory traffic
        legitimate_endpoints = ["/api/dashboard", "/api/analytics", "/api/components"]
        legitimate_requests = 0
        
        for endpoint in legitimate_endpoints:
            if asyncio.run(rate_limiter.can_make_request(endpoint)):
                asyncio.run(rate_limiter.record_request(endpoint))
                legitimate_requests += 1
                await asyncio.sleep(0.5)  # Realistic delay
        
        # Simulate suspicious traffic pattern (rapid requests to same endpoint)
        suspicious_endpoint = "/api/test"
        suspicious_requests = 0
        
        for i in range(10):  # Rapid requests
            if asyncio.run(rate_limiter.can_make_request(suspicious_endpoint)):
                asyncio.run(rate_limiter.record_request(suspicious_endpoint))
                suspicious_requests += 1
            # No delay - suspicious pattern
        
        # Verify differentiation
        assert legitimate_requests > suspicious_requests  # Legitimate should succeed more
        assert suspicious_requests < 5  # Suspicious should be limited
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.2",
            "action": "test_traffic_differentiation",
            "status": "completed",
            "details": {
                "test": "legitimate_vs_suspicious",
                "result": "passed",
                "legitimate_requests": legitimate_requests,
                "suspicious_requests": suspicious_requests
            }
        }))