"""
Unit tests for CloudflareAPIClient

Tests the low-level Cloudflare API client functionality including
authentication, error handling, retries, and API operations.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from src.beast_mode.observatory.cloudflare.api_client import (
    CloudflareAPIClient,
    CloudflareConfig,
    CloudflareAPIError
)


class TestCloudflareConfig:
    """Test CloudflareConfig dataclass"""
    
    def test_config_creation(self):
        """Test basic config creation"""
        config = CloudflareConfig(
            api_token="test_token",
            zone_id="test_zone"
        )
        
        assert config.api_token == "test_token"
        assert config.zone_id == "test_zone"
        assert config.base_url == "https://api.cloudflare.com/client/v4"
        assert config.timeout == 30
        assert config.max_retries == 3
    
    def test_config_custom_values(self):
        """Test config with custom values"""
        config = CloudflareConfig(
            api_token="custom_token",
            zone_id="custom_zone",
            base_url="https://custom.api.com",
            timeout=60,
            max_retries=5
        )
        
        assert config.api_token == "custom_token"
        assert config.zone_id == "custom_zone"
        assert config.base_url == "https://custom.api.com"
        assert config.timeout == 60
        assert config.max_retries == 5


class TestCloudflareAPIError:
    """Test CloudflareAPIError exception"""
    
    def test_basic_error(self):
        """Test basic error creation"""
        error = CloudflareAPIError("Test error")
        
        assert str(error) == "Test error"
        assert error.status_code is None
        assert error.response_data is None
    
    def test_error_with_status_code(self):
        """Test error with status code"""
        error = CloudflareAPIError("Test error", status_code=404)
        
        assert str(error) == "Test error"
        assert error.status_code == 404
        assert error.response_data is None
    
    def test_error_with_response_data(self):
        """Test error with response data"""
        response_data = {"error": "API error"}
        error = CloudflareAPIError("Test error", status_code=400, response_data=response_data)
        
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.response_data == response_data


class TestCloudflareAPIClient:
    """Test CloudflareAPIClient functionality"""
    
    @pytest.fixture
    def config(self):
        """Create test config"""
        return CloudflareConfig(
            api_token="test_token",
            zone_id="test_zone"
        )
    
    @pytest.fixture
    def client(self, config):
        """Create test client"""
        return CloudflareAPIClient(config)
    
    def test_client_initialization(self, client, config):
        """Test client initialization"""
        assert client.config == config
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager"""
        with patch.object(client, '_create_session', new_callable=AsyncMock) as mock_create:
            with patch.object(client, '_close_session', new_callable=AsyncMock) as mock_close:
                async with client:
                    mock_create.assert_called_once()
                
                mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_session(self, client):
        """Test session creation"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await client._create_session()
            
            assert client.session == mock_session
            mock_session_class.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_session(self, client):
        """Test session closing"""
        mock_session = AsyncMock()
        client.session = mock_session
        
        await client._close_session()
        
        mock_session.close.assert_called_once()
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, client):
        """Test successful API request"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"success": True, "result": "test"})
        
        mock_session = AsyncMock()
        mock_session.request.return_value.__aenter__.return_value = mock_response
        client.session = mock_session
        
        result = await client._make_request("GET", "/test")
        
        assert result == {"success": True, "result": "test"}
        mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_api_error(self, client):
        """Test API error handling"""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value={
            "success": False,
            "errors": [{"code": 1001, "message": "API error"}]
        })
        
        mock_session = AsyncMock()
        mock_session.request.return_value.__aenter__.return_value = mock_response
        client.session = mock_session
        
        with pytest.raises(CloudflareAPIError) as exc_info:
            await client._make_request("GET", "/test")
        
        assert exc_info.value.status_code == 400
        assert "API error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_make_request_network_error(self, client):
        """Test network error handling"""
        mock_session = AsyncMock()
        mock_session.request.side_effect = Exception("Network error")
        client.session = mock_session
        
        with pytest.raises(CloudflareAPIError) as exc_info:
            await client._make_request("GET", "/test")
        
        assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_zone_info(self, client):
        """Test get zone info API call"""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True, "result": {"id": "test_zone"}}
            
            result = await client.get_zone_info()
            
            assert result == {"success": True, "result": {"id": "test_zone"}}
            mock_request.assert_called_once_with("GET", "/zones/test_zone")
    
    @pytest.mark.asyncio
    async def test_list_firewall_rules(self, client):
        """Test list firewall rules API call"""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True, "result": [{"id": "rule1"}]}
            
            result = await client.list_firewall_rules()
            
            assert result == [{"id": "rule1"}]
            mock_request.assert_called_once_with("GET", "/zones/test_zone/firewall/rules")
    
    @pytest.mark.asyncio
    async def test_create_firewall_rule(self, client):
        """Test create firewall rule API call"""
        rule_data = {"action": "allow", "expression": "true"}
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True, "result": [{"id": "new_rule"}]}
            
            result = await client.create_firewall_rule(rule_data)
            
            assert result == {"id": "new_rule"}
            mock_request.assert_called_once_with(
                "POST", 
                "/zones/test_zone/firewall/rules",
                {"rules": [rule_data]}
            )
    
    @pytest.mark.asyncio
    async def test_update_firewall_rule(self, client):
        """Test update firewall rule API call"""
        rule_data = {"action": "block", "expression": "false"}
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True, "result": {"id": "updated_rule"}}
            
            result = await client.update_firewall_rule("rule_id", rule_data)
            
            assert result == {"id": "updated_rule"}
            mock_request.assert_called_once_with(
                "PUT",
                "/zones/test_zone/firewall/rules/rule_id",
                rule_data
            )
    
    @pytest.mark.asyncio
    async def test_delete_firewall_rule(self, client):
        """Test delete firewall rule API call"""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True}
            
            result = await client.delete_firewall_rule("rule_id")
            
            assert result is True
            mock_request.assert_called_once_with(
                "DELETE",
                "/zones/test_zone/firewall/rules/rule_id"
            )
    
    @pytest.mark.asyncio
    async def test_list_rate_limit_rules(self, client):
        """Test list rate limit rules API call"""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True, "result": [{"id": "rate1"}]}
            
            result = await client.list_rate_limit_rules()
            
            assert result == [{"id": "rate1"}]
            mock_request.assert_called_once_with("GET", "/zones/test_zone/rate_limits")
    
    @pytest.mark.asyncio
    async def test_create_rate_limit_rule(self, client):
        """Test create rate limit rule API call"""
        rule_data = {"rate": 100, "period": 60}
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True, "result": {"id": "new_rate"}}
            
            result = await client.create_rate_limit_rule(rule_data)
            
            assert result == {"id": "new_rate"}
            mock_request.assert_called_once_with(
                "POST",
                "/zones/test_zone/rate_limits",
                rule_data
            )
    
    @pytest.mark.asyncio
    async def test_get_bot_management_config(self, client):
        """Test get bot management config API call"""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True, "result": {"enable_js": True}}
            
            result = await client.get_bot_management_config()
            
            assert result == {"enable_js": True}
            mock_request.assert_called_once_with("GET", "/zones/test_zone/bot_management")
    
    @pytest.mark.asyncio
    async def test_update_bot_management_config(self, client):
        """Test update bot management config API call"""
        config_data = {"enable_js": True, "enable_cookie": False}
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True, "result": {"updated": True}}
            
            result = await client.update_bot_management_config(config_data)
            
            assert result == {"updated": True}
            mock_request.assert_called_once_with(
                "PUT",
                "/zones/test_zone/bot_management",
                config_data
            )
    
    @pytest.mark.asyncio
    async def test_get_security_events(self, client):
        """Test get security events API call"""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"success": True, "result": [{"id": "event1"}]}
            
            result = await client.get_security_events(limit=50)
            
            assert result == [{"id": "event1"}]
            mock_request.assert_called_once_with("GET", "/zones/test_zone/security/events")
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, client):
        """Test successful connection test"""
        with patch.object(client, 'get_zone_info', new_callable=AsyncMock) as mock_get_zone:
            mock_get_zone.return_value = {"success": True}
            
            result = await client.test_connection()
            
            assert result is True
            mock_get_zone.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, client):
        """Test failed connection test"""
        with patch.object(client, 'get_zone_info', new_callable=AsyncMock) as mock_get_zone:
            mock_get_zone.side_effect = CloudflareAPIError("Connection failed")
            
            result = await client.test_connection()
            
            assert result is False
            mock_get_zone.assert_called_once()
    
    def test_log_action(self, client):
        """Test logging functionality"""
        with patch('builtins.print') as mock_print:
            client._log_action("test_action", "in_progress", {"test": "data"})
            
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            log_data = json.loads(call_args)
            
            assert log_data["task"] == "5.1"
            assert log_data["action"] == "test_action"
            assert log_data["status"] == "in_progress"
            assert log_data["details"] == {"test": "data"}
            assert "timestamp" in log_data