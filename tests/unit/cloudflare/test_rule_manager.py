"""
Unit tests for RuleManager.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.beast_mode.observatory.cloudflare.rule_manager import RuleManager
from src.beast_mode.observatory.cloudflare.api_client import CloudflareAPIError


class TestRuleManager:
    """Test cases for RuleManager."""
    
    @pytest.fixture
    def rule_manager(self):
        """Create a RuleManager instance for testing."""
        mock_api_client = AsyncMock()
        return RuleManager(mock_api_client)
        
    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        return AsyncMock()
        
    @pytest.mark.asyncio
    async def test_create_whitelist_rule_success(self, rule_manager):
        """Test successful whitelist rule creation."""
        # Mock API client response
        rule_manager.api_client.create_firewall_rule.return_value = {
            "result": {"id": "rule_123", "description": "Test rule"}
        }
        
        # Test the method
        result = await rule_manager.create_whitelist_rule(
            zone_id="zone_123",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test Observatory rule",
            action="allow"
        )
        
        # Verify results
        assert result["result"]["id"] == "rule_123"
        
        # Verify API call
        rule_manager.api_client.create_firewall_rule.assert_called_once()
        call_args = rule_manager.api_client.create_firewall_rule.call_args
        
        assert call_args[0][0] == "zone_123"  # zone_id
        rule_data = call_args[0][1]  # rule_data
        
        assert rule_data["filter"]["expression"] == '(http.user_agent contains "Observatory-Internal")'
        assert rule_data["action"] == "allow"
        assert rule_data["description"] == "Test Observatory rule"
        assert rule_data["paused"] is False
        
    @pytest.mark.asyncio
    async def test_create_whitelist_rule_api_error(self, rule_manager):
        """Test whitelist rule creation with API error."""
        # Mock API client error
        rule_manager.api_client.create_firewall_rule.side_effect = CloudflareAPIError("API Error")
        
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError):
            await rule_manager.create_whitelist_rule(
                zone_id="zone_123",
                expression='(http.user_agent contains "Observatory-Internal")',
                description="Test Observatory rule"
            )
            
    @pytest.mark.asyncio
    async def test_create_rate_limit_exception_success(self, rule_manager):
        """Test successful rate limit exception creation."""
        # Mock API client response
        rule_manager.api_client.create_rate_limit_rule.return_value = {
            "result": {"id": "rate_limit_123"}
        }
        
        # Test the method
        result = await rule_manager.create_rate_limit_exception(
            zone_id="zone_123",
            match_expression='http.request.uri.path matches "^/ws/"',
            description="Observatory WebSocket rate limit exception",
            rate_limit=1000,
            period=60
        )
        
        # Verify results
        assert result["result"]["id"] == "rate_limit_123"
        
        # Verify API call
        rule_manager.api_client.create_rate_limit_rule.assert_called_once()
        call_args = rule_manager.api_client.create_rate_limit_rule.call_args
        
        assert call_args[0][0] == "zone_123"  # zone_id
        rule_data = call_args[0][1]  # rule_data
        
        assert rule_data["match"]["request"]["url"] == 'http.request.uri.path matches "^/ws/"'
        assert rule_data["rate"] == 1000
        assert rule_data["period"] == 60
        assert rule_data["description"] == "Observatory WebSocket rate limit exception"
        assert rule_data["disabled"] is False
        
    @pytest.mark.asyncio
    async def test_create_rate_limit_exception_api_error(self, rule_manager):
        """Test rate limit exception creation with API error."""
        # Mock API client error
        rule_manager.api_client.create_rate_limit_rule.side_effect = CloudflareAPIError("API Error")
        
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError):
            await rule_manager.create_rate_limit_exception(
                zone_id="zone_123",
                match_expression='http.request.uri.path matches "^/ws/"',
                description="Test rate limit exception"
            )
            
    @pytest.mark.asyncio
    async def test_update_rule_description_firewall_success(self, rule_manager):
        """Test successful firewall rule description update."""
        # Mock existing rule data
        existing_rule = {
            "id": "rule_123",
            "filter": {"expression": "test"},
            "action": "allow",
            "description": "Old description",
            "paused": False
        }
        
        rule_manager.api_client.list_firewall_rules.return_value = {
            "result": [existing_rule]
        }
        
        rule_manager.api_client.update_firewall_rule.return_value = {
            "result": {"id": "rule_123"}
        }
        
        # Test the method
        result = await rule_manager.update_rule_description(
            zone_id="zone_123",
            rule_id="rule_123",
            new_description="New description",
            rule_type="firewall"
        )
        
        # Verify results
        assert result["result"]["id"] == "rule_123"
        
        # Verify API calls
        rule_manager.api_client.list_firewall_rules.assert_called_once()
        rule_manager.api_client.update_firewall_rule.assert_called_once()
        
        # Verify update data
        update_call_args = rule_manager.api_client.update_firewall_rule.call_args
        update_data = update_call_args[0][2]  # rule_data
        
        assert update_data["description"] == "New description"
        assert update_data["filter"] == existing_rule["filter"]
        assert update_data["action"] == existing_rule["action"]
        
    @pytest.mark.asyncio
    async def test_update_rule_description_firewall_not_found(self, rule_manager):
        """Test firewall rule description update when rule not found."""
        # Mock empty rules list
        rule_manager.api_client.list_firewall_rules.return_value = {"result": []}
        
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError, match="Firewall rule rule_123 not found"):
            await rule_manager.update_rule_description(
                zone_id="zone_123",
                rule_id="rule_123",
                new_description="New description",
                rule_type="firewall"
            )
            
    @pytest.mark.asyncio
    async def test_update_rule_description_rate_limit_not_implemented(self, rule_manager):
        """Test rate limit rule description update (not implemented)."""
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError, match="Rate limit rule updates not fully implemented"):
            await rule_manager.update_rule_description(
                zone_id="zone_123",
                rule_id="rate_limit_123",
                new_description="New description",
                rule_type="rate_limit"
            )
            
    @pytest.mark.asyncio
    async def test_update_rule_description_unknown_type(self, rule_manager):
        """Test rule description update with unknown rule type."""
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError, match="Unknown rule type: unknown"):
            await rule_manager.update_rule_description(
                zone_id="zone_123",
                rule_id="rule_123",
                new_description="New description",
                rule_type="unknown"
            )
            
    @pytest.mark.asyncio
    async def test_delete_rule_firewall_success(self, rule_manager):
        """Test successful firewall rule deletion."""
        # Mock API client response
        rule_manager.api_client.delete_firewall_rule.return_value = {
            "result": {"id": "rule_123"}
        }
        
        # Test the method
        result = await rule_manager.delete_rule(
            zone_id="zone_123",
            rule_id="rule_123",
            rule_type="firewall"
        )
        
        # Verify results
        assert result["result"]["id"] == "rule_123"
        
        # Verify API call
        rule_manager.api_client.delete_firewall_rule.assert_called_once_with("zone_123", "rule_123")
        
    @pytest.mark.asyncio
    async def test_delete_rule_unknown_type(self, rule_manager):
        """Test rule deletion with unknown rule type."""
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError, match="Rule deletion not implemented for type: unknown"):
            await rule_manager.delete_rule(
                zone_id="zone_123",
                rule_id="rule_123",
                rule_type="unknown"
            )
            
    @pytest.mark.asyncio
    async def test_delete_rule_api_error(self, rule_manager):
        """Test rule deletion with API error."""
        # Mock API client error
        rule_manager.api_client.delete_firewall_rule.side_effect = CloudflareAPIError("API Error")
        
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError):
            await rule_manager.delete_rule(
                zone_id="zone_123",
                rule_id="rule_123",
                rule_type="firewall"
            )
            
    @pytest.mark.asyncio
    async def test_list_observatory_rules_success(self, rule_manager):
        """Test successful Observatory rules listing."""
        # Mock API client response
        mock_rules = [
            {
                "id": "rule_1",
                "description": "Observatory internal polling traffic",
                "action": "allow",
                "filter": {"expression": "test"},
                "paused": False
            },
            {
                "id": "rule_2", 
                "description": "Regular firewall rule",
                "action": "block",
                "filter": {"expression": "test2"},
                "paused": False
            },
            {
                "id": "rule_3",
                "description": "Observatory WebSocket endpoints",
                "action": "allow",
                "filter": {"expression": "test3"},
                "paused": False
            }
        ]
        
        rule_manager.api_client.list_firewall_rules.return_value = {"result": mock_rules}
        
        # Test the method
        result = await rule_manager.list_observatory_rules("zone_123")
        
        # Verify results - should only include Observatory rules
        assert len(result) == 2
        assert result[0]["id"] == "rule_1"
        assert result[1]["id"] == "rule_3"
        
        # Verify all returned rules have Observatory in description
        for rule in result:
            assert "observatory" in rule["description"].lower()
            assert "type" in rule
            assert rule["type"] == "firewall"
            
    @pytest.mark.asyncio
    async def test_list_observatory_rules_api_error(self, rule_manager):
        """Test Observatory rules listing with API error."""
        # Mock API client error
        rule_manager.api_client.list_firewall_rules.side_effect = CloudflareAPIError("API Error")
        
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError):
            await rule_manager.list_observatory_rules("zone_123")
            
    def test_validate_rule_syntax_valid(self, rule_manager):
        """Test rule syntax validation with valid expression."""
        valid_expressions = [
            '(http.user_agent contains "Observatory-Internal")',
            '(http.request.uri.path matches "^/ws/")',
            '(http.request.headers["x-observatory-client"][0] eq "internal-polling")',
            '(ip.src eq 192.168.1.1)',
            '(cf.threat_score gt 10)'
        ]
        
        for expression in valid_expressions:
            assert rule_manager.validate_rule_syntax(expression) is True
            
    def test_validate_rule_syntax_invalid(self, rule_manager):
        """Test rule syntax validation with invalid expressions."""
        invalid_expressions = [
            "",  # Empty
            None,  # None
            "invalid expression",  # No parentheses
            "(unbalanced parentheses",  # Unbalanced
            "(no http field)",  # No required fields
            "()",  # Empty parentheses
        ]
        
        for expression in invalid_expressions:
            assert rule_manager.validate_rule_syntax(expression) is False
            
    def test_validate_rule_syntax_exception(self, rule_manager):
        """Test rule syntax validation with exception."""
        # Mock an exception in validation
        with patch.object(rule_manager, 'validate_rule_syntax', side_effect=Exception("Test error")):
            # The method should catch the exception and return False
            result = rule_manager.validate_rule_syntax("test")
            assert result is False