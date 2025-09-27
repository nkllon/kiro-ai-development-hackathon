"""
Unit tests for CloudflareAPIClient.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from src.beast_mode.observatory.cloudflare.api_client import CloudflareAPIClient, CloudflareAPIError


class TestCloudflareAPIClient:
    """Test cases for CloudflareAPIClient."""
    
    @pytest.fixture
    def client(self):
        """Create a CloudflareAPIClient instance for testing."""
        return CloudflareAPIClient("test_token", timeout=10)
        
    @pytest.fixture
    def mock_response(self):
        """Mock HTTP response."""
        response = AsyncMock()
        response.ok = True
        response.status = 200
        response.json.return_value = {"result": {"id": "test_id"}, "success": True}
        return response
        
    @pytest.mark.asyncio
    async def test_init(self, client):
        """Test client initialization."""
        assert client.api_token == "test_token"
        assert client.timeout == 10
        assert client.session is None
        
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            async with client as ctx_client:
                assert ctx_client is client
                assert client.session is mock_session
                
            # Session should be closed on exit
            mock_session.close.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_make_request_success(self, client, mock_response):
        """Test successful API request."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.request.return_value.__aenter__.return_value = mock_response
            mock_session_class.return_value = mock_session
            
            async with client:
                result = await client._make_request("GET", "test/endpoint")
                
            assert result == {"result": {"id": "test_id"}, "success": True}
            mock_session.request.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_retry(self, client):
        """Test API request with rate limit retry."""
        # First response: rate limited
        rate_limit_response = AsyncMock()
        rate_limit_response.status = 429
        rate_limit_response.headers = {"Retry-After": "1"}
        rate_limit_response.json.return_value = {"errors": [{"message": "Rate limited"}]}
        
        # Second response: success
        success_response = AsyncMock()
        success_response.ok = True
        success_response.status = 200
        success_response.json.return_value = {"result": {"id": "test_id"}, "success": True}
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.request.return_value.__aenter__.side_effect = [
                rate_limit_response,
                success_response
            ]
            mock_session_class.return_value = mock_session
            
            with patch('asyncio.sleep') as mock_sleep:
                async with client:
                    result = await client._make_request("GET", "test/endpoint")
                    
                assert result == {"result": {"id": "test_id"}, "success": True}
                mock_sleep.assert_called_once_with(1)  # Retry-After value
                
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_max_retries(self, client):
        """Test API request with rate limit exceeding max retries."""
        # All responses: rate limited
        rate_limit_response = AsyncMock()
        rate_limit_response.status = 429
        rate_limit_response.headers = {"Retry-After": "1"}
        rate_limit_response.json.return_value = {"errors": [{"message": "Rate limited"}]}
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.request.return_value.__aenter__.return_value = rate_limit_response
            mock_session_class.return_value = mock_session
            
            with patch('asyncio.sleep'):
                async with client:
                    with pytest.raises(CloudflareAPIError, match="Rate limit exceeded"):
                        await client._make_request("GET", "test/endpoint")
                        
    @pytest.mark.asyncio
    async def test_make_request_api_error(self, client):
        """Test API request with API error."""
        error_response = AsyncMock()
        error_response.ok = False
        error_response.status = 400
        error_response.json.return_value = {
            "errors": [{"message": "Bad request"}],
            "success": False
        }
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.request.return_value.__aenter__.return_value = error_response
            mock_session_class.return_value = mock_session
            
            async with client:
                with pytest.raises(CloudflareAPIError, match="Bad request"):
                    await client._make_request("GET", "test/endpoint")
                    
    @pytest.mark.asyncio
    async def test_make_request_client_error_retry(self, client):
        """Test API request with client error retry."""
        # First response: client error
        client_error_response = AsyncMock()
        client_error_response.ok = False
        client_error_response.status = 500
        client_error_response.json.side_effect = aiohttp.ClientError("Connection error")
        
        # Second response: success
        success_response = AsyncMock()
        success_response.ok = True
        success_response.status = 200
        success_response.json.return_value = {"result": {"id": "test_id"}, "success": True}
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.request.return_value.__aenter__.side_effect = [
                client_error_response,
                success_response
            ]
            mock_session_class.return_value = mock_session
            
            with patch('asyncio.sleep') as mock_sleep:
                async with client:
                    result = await client._make_request("GET", "test/endpoint")
                    
                assert result == {"result": {"id": "test_id"}, "success": True}
                mock_sleep.assert_called_once()
                
    @pytest.mark.asyncio
    async def test_get_zone_info(self, client, mock_response):
        """Test get zone info."""
        with patch.object(client, '_make_request', return_value={"result": {"id": "zone_123"}}):
            result = await client.get_zone_info("zone_123")
            
            assert result == {"result": {"id": "zone_123"}}
            client._make_request.assert_called_once_with("GET", "zones/zone_123")
            
    @pytest.mark.asyncio
    async def test_list_firewall_rules(self, client):
        """Test list firewall rules."""
        with patch.object(client, '_make_request', return_value={"result": []}):
            result = await client.list_firewall_rules("zone_123", page=1, per_page=50)
            
            assert result == {"result": []}
            client._make_request.assert_called_once_with(
                "GET", "zones/zone_123/firewall/rules", params={"page": 1, "per_page": 50}
            )
            
    @pytest.mark.asyncio
    async def test_create_firewall_rule(self, client):
        """Test create firewall rule."""
        rule_data = {"filter": {"expression": "test"}, "action": "allow"}
        
        with patch.object(client, '_make_request', return_value={"result": {"id": "rule_123"}}):
            result = await client.create_firewall_rule("zone_123", rule_data)
            
            assert result == {"result": {"id": "rule_123"}}
            client._make_request.assert_called_once_with(
                "POST", "zones/zone_123/firewall/rules", data=rule_data
            )
            
    @pytest.mark.asyncio
    async def test_update_firewall_rule(self, client):
        """Test update firewall rule."""
        rule_data = {"filter": {"expression": "updated"}, "action": "block"}
        
        with patch.object(client, '_make_request', return_value={"result": {"id": "rule_123"}}):
            result = await client.update_firewall_rule("zone_123", "rule_123", rule_data)
            
            assert result == {"result": {"id": "rule_123"}}
            client._make_request.assert_called_once_with(
                "PUT", "zones/zone_123/firewall/rules/rule_123", data=rule_data
            )
            
    @pytest.mark.asyncio
    async def test_delete_firewall_rule(self, client):
        """Test delete firewall rule."""
        with patch.object(client, '_make_request', return_value={"result": {"id": "rule_123"}}):
            result = await client.delete_firewall_rule("zone_123", "rule_123")
            
            assert result == {"result": {"id": "rule_123"}}
            client._make_request.assert_called_once_with(
                "DELETE", "zones/zone_123/firewall/rules/rule_123"
            )
            
    @pytest.mark.asyncio
    async def test_list_rate_limit_rules(self, client):
        """Test list rate limit rules."""
        with patch.object(client, '_make_request', return_value={"result": []}):
            result = await client.list_rate_limit_rules("zone_123", page=1, per_page=50)
            
            assert result == {"result": []}
            client._make_request.assert_called_once_with(
                "GET", "zones/zone_123/rate_limits", params={"page": 1, "per_page": 50}
            )
            
    @pytest.mark.asyncio
    async def test_create_rate_limit_rule(self, client):
        """Test create rate limit rule."""
        rule_data = {"match": {"request": {"url": "test"}}, "rate": 100}
        
        with patch.object(client, '_make_request', return_value={"result": {"id": "rate_123"}}):
            result = await client.create_rate_limit_rule("zone_123", rule_data)
            
            assert result == {"result": {"id": "rate_123"}}
            client._make_request.assert_called_once_with(
                "POST", "zones/zone_123/rate_limits", data=rule_data
            )
            
    @pytest.mark.asyncio
    async def test_get_bot_management_config(self, client):
        """Test get bot management config."""
        with patch.object(client, '_make_request', return_value={"result": {"enable_js": True}}):
            result = await client.get_bot_management_config("zone_123")
            
            assert result == {"result": {"enable_js": True}}
            client._make_request.assert_called_once_with("GET", "zones/zone_123/bot_management")
            
    @pytest.mark.asyncio
    async def test_update_bot_management_config(self, client):
        """Test update bot management config."""
        config_data = {"enable_js": True, "fight_mode": False}
        
        with patch.object(client, '_make_request', return_value={"result": {"enable_js": True}}):
            result = await client.update_bot_management_config("zone_123", config_data)
            
            assert result == {"result": {"enable_js": True}}
            client._make_request.assert_called_once_with(
                "PUT", "zones/zone_123/bot_management", data=config_data
            )
            
    @pytest.mark.asyncio
    async def test_get_security_events(self, client):
        """Test get security events."""
        from datetime import datetime
        
        start_time = datetime(2023, 1, 1, 0, 0, 0)
        end_time = datetime(2023, 1, 2, 0, 0, 0)
        
        with patch.object(client, '_make_request', return_value={"result": []}):
            result = await client.get_security_events("zone_123", start_time, end_time)
            
            assert result == {"result": []}
            client._make_request.assert_called_once_with(
                "GET", "zones/zone_123/security/events",
                params={"since": start_time.isoformat(), "until": end_time.isoformat()}
            )
            
    @pytest.mark.asyncio
    async def test_get_security_events_no_times(self, client):
        """Test get security events without time parameters."""
        with patch.object(client, '_make_request', return_value={"result": []}):
            result = await client.get_security_events("zone_123")
            
            assert result == {"result": []}
            client._make_request.assert_called_once_with(
                "GET", "zones/zone_123/security/events", params={}
            )
            
    def test_cloudflare_api_error(self):
        """Test CloudflareAPIError exception."""
        error = CloudflareAPIError("Test error", status_code=400, response_data={"error": "test"})
        
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.response_data == {"error": "test"}
        
    def test_cloudflare_api_error_minimal(self):
        """Test CloudflareAPIError exception with minimal parameters."""
        error = CloudflareAPIError("Test error")
        
        assert str(error) == "Test error"
        assert error.status_code is None
        assert error.response_data is None