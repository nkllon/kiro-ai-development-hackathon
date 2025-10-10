"""
Unit tests for IntelligentPoller
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock

from src.beast_mode.observatory.polling.intelligent_poller import IntelligentPoller, PollingResult
from src.beast_mode.observatory.polling.rate_limiter import RateLimitConfig
from src.beast_mode.observatory.polling.polling_strategy import PollingConfig


class TestIntelligentPoller:
    """Test cases for IntelligentPoller"""
    
    @pytest.fixture
    def poller(self):
        """Create an IntelligentPoller instance for testing"""
        rate_config = RateLimitConfig(
            max_requests_per_minute=10,
            max_concurrent_requests=5
        )
        polling_config = PollingConfig(
            base_interval=5.0,
            max_interval=60.0
        )
        return IntelligentPoller(rate_config, polling_config)
    
    @pytest.fixture
    async def poller_with_session(self, poller):
        """Create a poller with HTTP session"""
        await poller.start()
        yield poller
        await poller.stop()
    
    @pytest.mark.asyncio
    async def test_start_stop(self, poller):
        """Test poller start and stop"""
        # Start poller
        await poller.start()
        assert poller.session is not None
        
        # Stop poller
        await poller.stop()
        assert poller.session is None
        assert len(poller.polling_tasks) == 0
        assert len(poller.active_endpoints) == 0
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test poller as context manager"""
        async with IntelligentPoller() as poller:
            assert poller.session is not None
            assert isinstance(poller.session, aiohttp.ClientSession)
        
        # Session should be closed after context exit
        assert poller.session is None
    
    @pytest.mark.asyncio
    async def test_start_polling(self, poller_with_session):
        """Test starting polling for an endpoint"""
        endpoint = "https://api.example.com/data"
        callback_called = False
        
        async def test_callback(ep, result):
            nonlocal callback_called
            callback_called = True
            assert ep == endpoint
            assert isinstance(result, PollingResult)
        
        # Start polling
        await poller_with_session.start_polling(endpoint, test_callback)
        
        assert endpoint in poller_with_session.active_endpoints
        assert endpoint in poller_with_session.polling_tasks
        assert test_callback in poller_with_session.endpoint_callbacks[endpoint]
        
        # Stop polling
        await poller_with_session.stop_polling(endpoint)
        assert endpoint not in poller_with_session.active_endpoints
    
    @pytest.mark.asyncio
    async def test_stop_polling(self, poller_with_session):
        """Test stopping polling for an endpoint"""
        endpoint = "https://api.example.com/data"
        
        # Start polling
        await poller_with_session.start_polling(endpoint)
        assert endpoint in poller_with_session.active_endpoints
        
        # Stop polling
        await poller_with_session.stop_polling(endpoint)
        assert endpoint not in poller_with_session.active_endpoints
        assert endpoint not in poller_with_session.polling_tasks
    
    @pytest.mark.asyncio
    async def test_poll_endpoint_success(self, poller_with_session):
        """Test successful endpoint polling"""
        endpoint = "https://httpbin.org/json"
        
        # Mock successful HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.headers = {"Content-Type": "application/json"}
        
        with patch.object(poller_with_session.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await poller_with_session.poll_endpoint(endpoint)
            
            assert result.success is True
            assert result.data == {"test": "data"}
            assert result.status_code == 200
            assert result.error is None
    
    @pytest.mark.asyncio
    async def test_poll_endpoint_failure(self, poller_with_session):
        """Test failed endpoint polling"""
        endpoint = "https://httpbin.org/status/500"
        
        # Mock failed HTTP response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_response.headers = {}
        
        with patch.object(poller_with_session.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await poller_with_session.poll_endpoint(endpoint)
            
            assert result.success is False
            assert result.status_code == 500
            assert result.data == "Internal Server Error"
    
    @pytest.mark.asyncio
    async def test_poll_endpoint_rate_limited(self, poller_with_session):
        """Test rate limited endpoint polling"""
        endpoint = "https://api.example.com/data"
        
        # Mock rate limiter to deny request
        with patch.object(poller_with_session.rate_limiter, 'can_make_request') as mock_can_request:
            mock_can_request.return_value = (False, "rate_limit_exceeded")
            
            result = await poller_with_session.poll_endpoint(endpoint)
            
            assert result.success is False
            assert "rate limit" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_poll_endpoint_suspended(self, poller_with_session):
        """Test polling suspended endpoint"""
        endpoint = "https://api.example.com/data"
        
        # Mock polling strategy to suspend endpoint
        with patch.object(poller_with_session.polling_strategy, 'should_poll_endpoint') as mock_should_poll:
            mock_should_poll.return_value = False
            
            result = await poller_with_session.poll_endpoint(endpoint)
            
            assert result.success is False
            assert "suspended" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_bot_protection_detection(self, poller_with_session):
        """Test bot protection detection"""
        endpoint = "https://api.example.com/data"
        
        # Mock response with bot protection indicators
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_response.text.return_value = "Access denied - bot detected"
        mock_response.headers = {"X-Bot-Detection": "true"}
        
        with patch.object(poller_with_session.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await poller_with_session.poll_endpoint(endpoint)
            
            assert result.success is False
            assert result.status_code == 403
            
            # Check that bot protection was detected
            assert poller_with_session.stats["bot_protection_events"] == 1
            assert len(poller_with_session.bot_protection_events) == 1
    
    @pytest.mark.asyncio
    async def test_request_deduplication(self, poller_with_session):
        """Test request deduplication"""
        endpoint = "https://api.example.com/data"
        params = {"param1": "value1"}
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.headers = {}
        
        with patch.object(poller_with_session.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Make two identical requests
            result1 = await poller_with_session.poll_endpoint(endpoint, params)
            result2 = await poller_with_session.poll_endpoint(endpoint, params)
            
            # Both should succeed
            assert result1.success is True
            assert result2.success is True
            
            # Check deduplication stats
            assert poller_with_session.stats["deduplicated_requests"] > 0
    
    @pytest.mark.asyncio
    async def test_polling_loop(self, poller_with_session):
        """Test polling loop functionality"""
        endpoint = "https://api.example.com/data"
        callback_calls = []
        
        async def test_callback(ep, result):
            callback_calls.append((ep, result))
            # Stop polling after first callback
            await poller_with_session.stop_polling(endpoint)
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.headers = {}
        
        with patch.object(poller_with_session.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Start polling
            await poller_with_session.start_polling(endpoint, test_callback)
            
            # Wait for callback to be called
            await asyncio.sleep(0.1)
            
            # Check callback was called
            assert len(callback_calls) > 0
            assert callback_calls[0][0] == endpoint
            assert callback_calls[0][1].success is True
    
    def test_get_stats(self, poller):
        """Test statistics retrieval"""
        stats = poller.get_stats()
        
        assert "poller_stats" in stats
        assert "rate_limiter_stats" in stats
        assert "deduplicator_stats" in stats
        assert "polling_strategy_stats" in stats
        assert "active_endpoints" in stats
        assert "bot_protection_events" in stats
        
        # Check initial stats
        assert stats["poller_stats"]["total_polls"] == 0
        assert stats["active_endpoints"] == []
        assert stats["bot_protection_events"] == 0
    
    def test_get_endpoint_stats(self, poller):
        """Test endpoint-specific statistics"""
        endpoint = "https://api.example.com/data"
        stats = poller.get_endpoint_stats(endpoint)
        
        assert stats["endpoint"] == endpoint
        assert stats["is_active"] is False
        assert "polling_strategy" in stats
        assert "rate_limiter" in stats
    
    def test_is_bot_protection_error(self, poller):
        """Test bot protection error detection"""
        # Test various bot protection indicators
        test_cases = [
            (403, "Access denied", True),
            (429, "Too many requests", True),
            (503, "Service unavailable", True),
            (200, "Success", False),
            (404, "Not found", False),
            (500, "Bot detected", True),
            (200, "CAPTCHA required", True),
        ]
        
        for status_code, error, expected in test_cases:
            result = PollingResult(
                success=False,
                status_code=status_code,
                error=error
            )
            assert poller._is_bot_protection_error(result) == expected