"""
Unit tests for IntelligentPoller.
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from src.beast_mode.observatory.polling.intelligent_poller import IntelligentPoller, PollingResult
from src.beast_mode.observatory.polling.rate_limiter import RateLimitConfig
from src.beast_mode.observatory.polling.polling_strategy import PollingConfig


class TestIntelligentPoller:
    """Test cases for IntelligentPoller."""
    
    @pytest.fixture
    def poller(self):
        """Create an IntelligentPoller instance for testing."""
        rate_config = RateLimitConfig(max_requests_per_minute=10, max_requests_per_hour=100)
        polling_config = PollingConfig(base_interval=1.0, max_interval=5.0)
        return IntelligentPoller(rate_config, polling_config, cache_ttl=10)
    
    @pytest.mark.asyncio
    async def test_start_polling(self, poller):
        """Test starting polling for an endpoint."""
        endpoint = "test-endpoint"
        
        await poller.start_polling(endpoint)
        
        assert endpoint in poller.active_endpoints
        assert endpoint in poller.polling_tasks
        assert endpoint in poller.endpoint_last_poll
    
    @pytest.mark.asyncio
    async def test_stop_polling(self, poller):
        """Test stopping polling for an endpoint."""
        endpoint = "test-endpoint"
        
        # Start polling first
        await poller.start_polling(endpoint)
        
        # Stop polling
        await poller.stop_polling(endpoint)
        
        assert endpoint not in poller.active_endpoints
        assert endpoint not in poller.polling_tasks
    
    @pytest.mark.asyncio
    async def test_poll_endpoint_success(self, poller):
        """Test successful endpoint polling."""
        endpoint = "test-endpoint"
        
        # Mock the HTTP request
        with patch.object(poller, '_make_http_request') as mock_request:
            mock_request.return_value = ({"data": "test"}, 200)
            
            result = await poller.poll_endpoint(endpoint)
            
            assert isinstance(result, PollingResult)
            assert result.success is True
            assert result.response_data == {"data": "test"}
            assert result.status_code == 200
            assert result.endpoint == endpoint
    
    @pytest.mark.asyncio
    async def test_poll_endpoint_rate_limited(self, poller):
        """Test endpoint polling when rate limited."""
        endpoint = "test-endpoint"
        
        # Mock rate limiter to deny request
        with patch.object(poller.rate_limiter, 'can_make_request') as mock_can_request:
            mock_can_request.return_value = False
            
            with patch.object(poller.rate_limiter, 'get_next_allowed_time') as mock_next_time:
                mock_next_time.return_value = datetime.utcnow()
                
                result = await poller.poll_endpoint(endpoint)
                
                assert isinstance(result, PollingResult)
                assert result.success is False
                assert "Rate limited" in result.error_message
    
    @pytest.mark.asyncio
    async def test_poll_endpoint_error(self, poller):
        """Test endpoint polling with error."""
        endpoint = "test-endpoint"
        
        # Mock the HTTP request to raise an exception
        with patch.object(poller, '_make_http_request') as mock_request:
            mock_request.side_effect = Exception("Network error")
            
            result = await poller.poll_endpoint(endpoint)
            
            assert isinstance(result, PollingResult)
            assert result.success is False
            assert "Network error" in result.error_message
    
    @pytest.mark.asyncio
    async def test_make_http_request(self, poller):
        """Test HTTP request making."""
        endpoint = "http://test.com/api"
        
        # Mock aiohttp session and response
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.status = 200
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            poller.session = mock_session
            
            response_data, status_code = await poller._make_http_request(endpoint)
            
            assert response_data == {"data": "test"}
            assert status_code == 200
    
    @pytest.mark.asyncio
    async def test_make_http_request_non_json(self, poller):
        """Test HTTP request with non-JSON response."""
        endpoint = "http://test.com/api"
        
        # Mock aiohttp session and response
        mock_response = AsyncMock()
        mock_response.json.side_effect = aiohttp.ContentTypeError(
            request_info=MagicMock(),
            history=MagicMock()
        )
        mock_response.text.return_value = "plain text"
        mock_response.status = 200
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            poller.session = mock_session
            
            response_data, status_code = await poller._make_http_request(endpoint)
            
            assert response_data == "plain text"
            assert status_code == 200
    
    @pytest.mark.asyncio
    async def test_poll_endpoint_loop(self, poller):
        """Test the polling loop."""
        endpoint = "test-endpoint"
        
        # Start polling
        await poller.start_polling(endpoint)
        
        # Mock poll_endpoint to avoid actual requests
        with patch.object(poller, 'poll_endpoint') as mock_poll:
            mock_poll.return_value = PollingResult(endpoint=endpoint, success=True)
            
            # Let the loop run briefly
            await asyncio.sleep(0.1)
            
            # Stop polling
            await poller.stop_polling(endpoint)
            
            # Verify poll_endpoint was called
            assert mock_poll.called
    
    @pytest.mark.asyncio
    async def test_response_callback(self, poller):
        """Test response callback functionality."""
        endpoint = "test-endpoint"
        callback_called = False
        callback_result = None
        
        def response_callback(result):
            nonlocal callback_called, callback_result
            callback_called = True
            callback_result = result
        
        poller.on_response = response_callback
        
        # Mock successful request
        with patch.object(poller, '_make_http_request') as mock_request:
            mock_request.return_value = ({"data": "test"}, 200)
            
            await poller.poll_endpoint(endpoint)
            
            assert callback_called is True
            assert callback_result.success is True
    
    @pytest.mark.asyncio
    async def test_error_callback(self, poller):
        """Test error callback functionality."""
        endpoint = "test-endpoint"
        callback_called = False
        callback_result = None
        
        def error_callback(result):
            nonlocal callback_called, callback_result
            callback_called = True
            callback_result = result
        
        poller.on_error = error_callback
        
        # Mock failed request
        with patch.object(poller, '_make_http_request') as mock_request:
            mock_request.side_effect = Exception("Network error")
            
            await poller.poll_endpoint(endpoint)
            
            assert callback_called is True
            assert callback_result.success is False
    
    @pytest.mark.asyncio
    async def test_get_status(self, poller):
        """Test getting poller status."""
        endpoint = "test-endpoint"
        
        # Start polling
        await poller.start_polling(endpoint)
        
        status = await poller.get_status()
        
        assert "active_endpoints" in status
        assert "endpoint_count" in status
        assert "polling_strategy_stats" in status
        assert "cache_stats" in status
        assert "rate_limiter_config" in status
        assert endpoint in status["active_endpoints"]
        assert status["endpoint_count"] == 1
    
    @pytest.mark.asyncio
    async def test_shutdown(self, poller):
        """Test poller shutdown."""
        endpoint = "test-endpoint"
        
        # Start polling
        await poller.start_polling(endpoint)
        
        # Shutdown
        await poller.shutdown()
        
        assert len(poller.active_endpoints) == 0
        assert len(poller.polling_tasks) == 0
        assert poller.session is None
    
    @pytest.mark.asyncio
    async def test_duplicate_start_polling(self, poller):
        """Test starting polling for already active endpoint."""
        endpoint = "test-endpoint"
        
        # Start polling first time
        await poller.start_polling(endpoint)
        initial_task_count = len(poller.polling_tasks)
        
        # Try to start polling again
        await poller.start_polling(endpoint)
        
        # Should not create duplicate tasks
        assert len(poller.polling_tasks) == initial_task_count
    
    @pytest.mark.asyncio
    async def test_stop_inactive_endpoint(self, poller):
        """Test stopping polling for inactive endpoint."""
        endpoint = "test-endpoint"
        
        # Try to stop polling for endpoint that's not being polled
        await poller.stop_polling(endpoint)
        
        # Should not raise an error
        assert endpoint not in poller.active_endpoints