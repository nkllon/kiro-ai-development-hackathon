"""
Unit tests for TrafficAnalyzer.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.beast_mode.observatory.cloudflare.traffic_analyzer import (
    TrafficAnalyzer, TrafficPattern
)
from src.beast_mode.observatory.cloudflare.api_client import CloudflareAPIError


class TestTrafficPattern:
    """Test cases for TrafficPattern."""
    
    def test_traffic_pattern_init(self):
        """Test TrafficPattern initialization."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=0.9,
            metadata={"source": "test"}
        )
        
        assert pattern.pattern_type == "user_agent"
        assert pattern.expression == '(http.user_agent contains "Observatory-Internal")'
        assert pattern.description == "Test pattern"
        assert pattern.confidence == 0.9
        assert pattern.metadata == {"source": "test"}
        
    def test_traffic_pattern_to_dict(self):
        """Test TrafficPattern to_dict method."""
        pattern = TrafficPattern(
            pattern_type="websocket",
            expression='(http.request.uri.path matches "^/ws/")',
            description="WebSocket pattern",
            confidence=0.95
        )
        
        result = pattern.to_dict()
        
        assert result["pattern_type"] == "websocket"
        assert result["expression"] == '(http.request.uri.path matches "^/ws/")'
        assert result["description"] == "WebSocket pattern"
        assert result["confidence"] == 0.95
        assert "metadata" in result


class TestTrafficAnalyzer:
    """Test cases for TrafficAnalyzer."""
    
    @pytest.fixture
    def traffic_analyzer(self):
        """Create a TrafficAnalyzer instance for testing."""
        mock_api_client = AsyncMock()
        return TrafficAnalyzer(mock_api_client)
        
    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        return AsyncMock()
        
    def test_observatory_patterns_configured(self, traffic_analyzer):
        """Test that Observatory patterns are properly configured."""
        patterns = traffic_analyzer.OBSERVATORY_PATTERNS
        
        assert len(patterns) == 5
        
        # Check pattern types
        pattern_types = [p.pattern_type for p in patterns]
        assert "user_agent" in pattern_types
        assert "websocket" in pattern_types
        assert "custom_header" in pattern_types
        assert "health_check" in pattern_types
        assert "api_endpoint" in pattern_types
        
        # Check expressions contain Observatory-specific elements
        expressions = [p.expression for p in patterns]
        assert any("Observatory-Internal" in expr for expr in expressions)
        assert any("/ws/" in expr for expr in expressions)
        assert any("x-observatory-client" in expr for expr in expressions)
        assert any("/health" in expr for expr in expressions)
        assert any("/api/observatory/" in expr for expr in expressions)
        
    @pytest.mark.asyncio
    async def test_analyze_recent_traffic_success(self, traffic_analyzer):
        """Test successful traffic analysis."""
        # Mock API client response
        mock_events = [
            {
                "action": "block",
                "user_agent": "Observatory-Internal/1.0",
                "uri": "/ws/status",
                "request_headers": {"x-observatory-client": "internal-polling"}
            },
            {
                "action": "allow",
                "user_agent": "Mozilla/5.0",
                "uri": "/",
                "request_headers": {}
            },
            {
                "action": "challenge",
                "user_agent": "Observatory-Internal/1.0",
                "uri": "/health",
                "request_headers": {}
            }
        ]
        
        traffic_analyzer.api_client.get_security_events.return_value = {"result": mock_events}
        
        # Test the method
        result = await traffic_analyzer.analyze_recent_traffic("zone_123", hours_back=24)
        
        # Verify results
        assert "patterns" in result
        assert "summary" in result
        assert result["summary"]["total_events"] == 3
        assert result["summary"]["observatory_requests"] == 2  # Two Observatory requests
        assert result["summary"]["blocked_observatory_requests"] == 1  # One blocked
        
        # Should have patterns for blocked Observatory requests
        assert len(result["patterns"]) >= 1
        
    @pytest.mark.asyncio
    async def test_analyze_recent_traffic_no_events(self, traffic_analyzer):
        """Test traffic analysis with no events."""
        # Mock empty API response
        traffic_analyzer.api_client.get_security_events.return_value = {"result": []}
        
        # Test the method
        result = await traffic_analyzer.analyze_recent_traffic("zone_123")
        
        # Verify results
        assert result["patterns"] == []
        assert result["summary"]["total_events"] == 0
        
    @pytest.mark.asyncio
    async def test_analyze_recent_traffic_large_sample(self, traffic_analyzer):
        """Test traffic analysis with large event sample."""
        # Create large event list
        large_events = [
            {"action": "block", "user_agent": f"bot_{i}", "uri": f"/test{i}"}
            for i in range(1500)  # More than default sample_size
        ]
        
        traffic_analyzer.api_client.get_security_events.return_value = {"result": large_events}
        
        # Test the method
        result = await traffic_analyzer.analyze_recent_traffic("zone_123", sample_size=1000)
        
        # Verify results - should be limited to sample_size
        assert result["summary"]["total_events"] == 1000
        
    @pytest.mark.asyncio
    async def test_analyze_recent_traffic_api_error(self, traffic_analyzer):
        """Test traffic analysis with API error."""
        # Mock API client error
        traffic_analyzer.api_client.get_security_events.side_effect = CloudflareAPIError("API Error")
        
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError):
            await traffic_analyzer.analyze_recent_traffic("zone_123")
            
    def test_is_observatory_request_user_agent(self, traffic_analyzer):
        """Test Observatory request detection by user agent."""
        event = {
            "user_agent": "Observatory-Internal/1.0",
            "uri": "/test",
            "request_headers": {}
        }
        
        assert traffic_analyzer._is_observatory_request(event) is True
        
    def test_is_observatory_request_uri_path(self, traffic_analyzer):
        """Test Observatory request detection by URI path."""
        event = {
            "user_agent": "Mozilla/5.0",
            "uri": "/ws/status",
            "request_headers": {}
        }
        
        assert traffic_analyzer._is_observatory_request(event) is True
        
        event["uri"] = "/health"
        assert traffic_analyzer._is_observatory_request(event) is True
        
        event["uri"] = "/api/observatory/status"
        assert traffic_analyzer._is_observatory_request(event) is True
        
    def test_is_observatory_request_headers(self, traffic_analyzer):
        """Test Observatory request detection by headers."""
        event = {
            "user_agent": "Mozilla/5.0",
            "uri": "/test",
            "request_headers": {"x-observatory-client": "internal-polling"}
        }
        
        assert traffic_analyzer._is_observatory_request(event) is True
        
    def test_is_observatory_request_not_observatory(self, traffic_analyzer):
        """Test Observatory request detection with non-Observatory request."""
        event = {
            "user_agent": "Mozilla/5.0",
            "uri": "/regular-page",
            "request_headers": {}
        }
        
        assert traffic_analyzer._is_observatory_request(event) is False
        
    def test_find_matching_pattern_user_agent(self, traffic_analyzer):
        """Test pattern matching for user agent."""
        event = {
            "user_agent": "Observatory-Internal/1.0",
            "uri": "/test",
            "request_headers": {}
        }
        
        pattern = traffic_analyzer._find_matching_pattern(event)
        
        assert pattern is not None
        assert pattern.pattern_type == "user_agent"
        
    def test_find_matching_pattern_websocket(self, traffic_analyzer):
        """Test pattern matching for WebSocket."""
        event = {
            "user_agent": "Mozilla/5.0",
            "uri": "/ws/status",
            "request_headers": {}
        }
        
        pattern = traffic_analyzer._find_matching_pattern(event)
        
        assert pattern is not None
        assert pattern.pattern_type == "websocket"
        
    def test_find_matching_pattern_custom_header(self, traffic_analyzer):
        """Test pattern matching for custom header."""
        event = {
            "user_agent": "Mozilla/5.0",
            "uri": "/test",
            "request_headers": {"x-observatory-client": "internal-polling"}
        }
        
        pattern = traffic_analyzer._find_matching_pattern(event)
        
        assert pattern is not None
        assert pattern.pattern_type == "custom_header"
        
    def test_find_matching_pattern_no_match(self, traffic_analyzer):
        """Test pattern matching with no match."""
        event = {
            "user_agent": "Mozilla/5.0",
            "uri": "/regular-page",
            "request_headers": {}
        }
        
        pattern = traffic_analyzer._find_matching_pattern(event)
        
        assert pattern is None
        
    def test_calculate_pattern_match_score_user_agent(self, traffic_analyzer):
        """Test pattern match score calculation for user agent."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        event = {
            "user_agent": "Observatory-Internal/1.0",
            "uri": "/test",
            "request_headers": {}
        }
        
        score = traffic_analyzer._calculate_pattern_match_score(event, pattern)
        
        assert score > 0.5  # Should be a good match
        
    def test_calculate_pattern_match_score_websocket(self, traffic_analyzer):
        """Test pattern match score calculation for WebSocket."""
        pattern = TrafficPattern(
            pattern_type="websocket",
            expression='(http.request.uri.path matches "^/ws/")',
            description="WebSocket pattern",
            confidence=0.9
        )
        
        event = {
            "user_agent": "Mozilla/5.0",
            "uri": "/ws/status",
            "request_headers": {}
        }
        
        score = traffic_analyzer._calculate_pattern_match_score(event, pattern)
        
        assert score > 0.5  # Should be a good match
        
    def test_calculate_pattern_match_score_no_match(self, traffic_analyzer):
        """Test pattern match score calculation with no match."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        event = {
            "user_agent": "Mozilla/5.0",
            "uri": "/test",
            "request_headers": {}
        }
        
        score = traffic_analyzer._calculate_pattern_match_score(event, pattern)
        
        assert score == 0.0  # Should be no match
        
    def test_get_recommended_whitelist_rules(self, traffic_analyzer):
        """Test getting recommended whitelist rules."""
        rules = traffic_analyzer.get_recommended_whitelist_rules()
        
        assert len(rules) == 5
        assert all(isinstance(rule, TrafficPattern) for rule in rules)
        
        # Check that all patterns are Observatory-specific
        for rule in rules:
            assert "observatory" in rule.description.lower() or "/ws/" in rule.expression or "/health" in rule.expression
            
    def test_create_custom_pattern(self, traffic_analyzer):
        """Test creating custom traffic pattern."""
        pattern = traffic_analyzer.create_custom_pattern(
            pattern_type="custom",
            expression='(http.request.uri.path matches "^/custom/")',
            description="Custom Observatory pattern",
            confidence=0.8
        )
        
        assert pattern.pattern_type == "custom"
        assert pattern.expression == '(http.request.uri.path matches "^/custom/")'
        assert pattern.description == "Custom Observatory pattern"
        assert pattern.confidence == 0.8
        assert pattern.metadata["source"] == "custom"
        assert "created_at" in pattern.metadata
        
    @pytest.mark.asyncio
    async def test_validate_pattern_effectiveness_success(self, traffic_analyzer):
        """Test pattern effectiveness validation."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        # Mock events
        mock_events = [
            {
                "user_agent": "Observatory-Internal/1.0",
                "uri": "/test",
                "request_headers": {}
            },
            {
                "user_agent": "Mozilla/5.0",
                "uri": "/test",
                "request_headers": {}
            }
        ]
        
        traffic_analyzer.api_client.get_security_events.return_value = {"result": mock_events}
        
        # Test the method
        result = await traffic_analyzer.validate_pattern_effectiveness("zone_123", pattern, 1)
        
        # Verify results
        assert "pattern" in result
        assert "total_matches" in result
        assert "false_positives" in result
        assert "precision" in result
        assert "test_duration_hours" in result
        
        assert result["test_duration_hours"] == 1
        assert result["total_matches"] >= 1  # At least one Observatory request
        
    @pytest.mark.asyncio
    async def test_validate_pattern_effectiveness_api_error(self, traffic_analyzer):
        """Test pattern effectiveness validation with API error."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        # Mock API client error
        traffic_analyzer.api_client.get_security_events.side_effect = CloudflareAPIError("API Error")
        
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError):
            await traffic_analyzer.validate_pattern_effectiveness("zone_123", pattern, 1)