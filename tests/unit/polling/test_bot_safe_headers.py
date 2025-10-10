"""
Unit tests for BotSafeHeaders.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.beast_mode.observatory.polling.bot_safe_headers import BotSafeHeaders


class TestBotSafeHeaders:
    """Test cases for BotSafeHeaders."""
    
    @pytest.fixture
    def bot_safe_headers(self):
        """Create a BotSafeHeaders instance for testing."""
        return BotSafeHeaders()
    
    def test_get_headers_basic(self, bot_safe_headers):
        """Test getting basic bot-safe headers."""
        headers = bot_safe_headers.get_headers()
        
        # Check that all required headers are present
        assert "User-Agent" in headers
        assert "X-Observatory-Client" in headers
        assert "X-Requested-With" in headers
        assert "Accept" in headers
        assert "Cache-Control" in headers
        assert "X-Polling-Reason" in headers
        
        # Check specific values
        assert headers["User-Agent"] == "Observatory-Internal/1.0 (WebSocket-Fallback)"
        assert headers["X-Observatory-Client"] == "internal-polling"
        assert headers["Accept"] == "application/json"
    
    def test_get_headers_with_endpoint(self, bot_safe_headers):
        """Test getting headers with endpoint context."""
        endpoint = "http://test.com/api"
        headers = bot_safe_headers.get_headers(endpoint)
        
        assert "X-Target-Endpoint" in headers
        assert headers["X-Target-Endpoint"] == endpoint
        assert "X-Request-Timestamp" in headers
    
    def test_get_headers_with_additional(self, bot_safe_headers):
        """Test getting headers with additional headers."""
        additional_headers = {"Custom-Header": "custom-value"}
        headers = bot_safe_headers.get_headers(additional_headers=additional_headers)
        
        assert "Custom-Header" in headers
        assert headers["Custom-Header"] == "custom-value"
        
        # Original headers should still be present
        assert "User-Agent" in headers
        assert "X-Observatory-Client" in headers
    
    def test_get_retry_headers(self, bot_safe_headers):
        """Test getting retry headers."""
        endpoint = "http://test.com/api"
        retry_count = 3
        
        headers = bot_safe_headers.get_retry_headers(retry_count, endpoint)
        
        # Should include all basic headers
        assert "User-Agent" in headers
        assert "X-Observatory-Client" in headers
        
        # Should include retry-specific headers
        assert "X-Retry-Count" in headers
        assert "X-Retry-Reason" in headers
        assert headers["X-Retry-Count"] == "3"
        assert headers["X-Retry-Reason"] == "websocket-fallback-retry"
        
        # Should include endpoint context
        assert "X-Target-Endpoint" in headers
        assert headers["X-Target-Endpoint"] == endpoint
    
    def test_get_retry_headers_no_endpoint(self, bot_safe_headers):
        """Test getting retry headers without endpoint."""
        retry_count = 2
        
        headers = bot_safe_headers.get_retry_headers(retry_count)
        
        assert "X-Retry-Count" in headers
        assert "X-Retry-Reason" in headers
        assert headers["X-Retry-Count"] == "2"
        
        # Should not include endpoint-specific header
        assert "X-Target-Endpoint" not in headers
    
    def test_timestamp_format(self, bot_safe_headers):
        """Test that timestamps are in ISO format."""
        headers = bot_safe_headers.get_headers()
        
        timestamp_str = headers["X-Request-Timestamp"]
        
        # Should be able to parse as ISO format
        timestamp = datetime.fromisoformat(timestamp_str)
        assert isinstance(timestamp, datetime)
    
    def test_headers_immutability(self, bot_safe_headers):
        """Test that modifying returned headers doesn't affect base headers."""
        headers1 = bot_safe_headers.get_headers()
        headers2 = bot_safe_headers.get_headers()
        
        # Modify first headers
        headers1["Custom-Header"] = "modified"
        
        # Second headers should be unchanged
        assert "Custom-Header" not in headers2
    
    def test_bot_safe_headers_constants(self, bot_safe_headers):
        """Test that bot-safe header constants are properly defined."""
        constants = BotSafeHeaders.BOT_SAFE_HEADERS
        
        assert isinstance(constants, dict)
        assert len(constants) > 0
        
        # Check that all expected headers are present
        expected_headers = [
            "User-Agent",
            "X-Observatory-Client", 
            "X-Requested-With",
            "Accept",
            "Cache-Control",
            "X-Polling-Reason"
        ]
        
        for header in expected_headers:
            assert header in constants
    
    def test_header_values_are_strings(self, bot_safe_headers):
        """Test that all header values are strings."""
        headers = bot_safe_headers.get_headers()
        
        for key, value in headers.items():
            assert isinstance(value, str), f"Header {key} value is not a string: {type(value)}"
    
    def test_retry_count_is_string(self, bot_safe_headers):
        """Test that retry count is converted to string."""
        headers = bot_safe_headers.get_retry_headers(5)
        
        assert isinstance(headers["X-Retry-Count"], str)
        assert headers["X-Retry-Count"] == "5"