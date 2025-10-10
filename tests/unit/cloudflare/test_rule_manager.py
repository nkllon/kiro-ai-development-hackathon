"""
Unit tests for RuleManager

Tests the rule management functionality including Observatory
whitelist rule creation, rate limiting exceptions, and rule operations.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from src.beast_mode.observatory.cloudflare.rule_manager import (
    RuleManager,
    ObservatoryRule,
    RuleType,
    RuleAction
)
from src.beast_mode.observatory.cloudflare.api_client import CloudflareAPIClient, CloudflareAPIError


class TestObservatoryRule:
    """Test ObservatoryRule dataclass"""
    
    def test_rule_creation(self):
        """Test basic rule creation"""
        rule = ObservatoryRule(
            name="test_rule",
            expression="true",
            action=RuleAction.ALLOW,
            description="Test rule",
            priority=1
        )
        
        assert rule.name == "test_rule"
        assert rule.expression == "true"
        assert rule.action == RuleAction.ALLOW
        assert rule.description == "Test rule"
        assert rule.priority == 1
        assert rule.enabled is True
        assert rule.rule_type == RuleType.FIREWALL
    
    def test_rule_with_custom_values(self):
        """Test rule with custom values"""
        rule = ObservatoryRule(
            name="custom_rule",
            expression="false",
            action=RuleAction.BLOCK,
            description="Custom rule",
            priority=5,
            enabled=False,
            rule_type=RuleType.RATE_LIMIT
        )
        
        assert rule.name == "custom_rule"
        assert rule.expression == "false"
        assert rule.action == RuleAction.BLOCK
        assert rule.description == "Custom rule"
        assert rule.priority == 5
        assert rule.enabled is False
        assert rule.rule_type == RuleType.RATE_LIMIT


class TestRuleManager:
    """Test RuleManager functionality"""
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client"""
        return AsyncMock(spec=CloudflareAPIClient)
    
    @pytest.fixture
    def rule_manager(self, mock_api_client):
        """Create rule manager with mock client"""
        return RuleManager(mock_api_client)
    
    def test_rule_manager_initialization(self, rule_manager):
        """Test rule manager initialization"""
        assert rule_manager.api_client is not None
        assert len(rule_manager.OBSERVATORY_WHITELIST_RULES) == 5
    
    def test_observatory_whitelist_rules(self, rule_manager):
        """Test Observatory whitelist rules are properly defined"""
        rules = rule_manager.OBSERVATORY_WHITELIST_RULES
        
        # Check that all rules are ObservatoryRule instances
        for rule in rules:
            assert isinstance(rule, ObservatoryRule)
            assert rule.action == RuleAction.ALLOW
            assert rule.enabled is True
            assert rule.rule_type == RuleType.FIREWALL
        
        # Check specific rules exist
        rule_names = [rule.name for rule in rules]
        assert "observatory-internal-polling" in rule_names
        assert "observatory-websocket-endpoints" in rule_names
        assert "observatory-polling-fallback" in rule_names
        assert "observatory-health-checks" in rule_names
        assert "observatory-metrics-endpoints" in rule_names
    
    @pytest.mark.asyncio
    async def test_create_observatory_whitelist_rules(self, rule_manager, mock_api_client):
        """Test creation of Observatory whitelist rules"""
        # Mock API responses
        mock_responses = [
            {"id": f"rule_{i}", "success": True}
            for i in range(len(rule_manager.OBSERVATORY_WHITELIST_RULES))
        ]
        mock_api_client.create_firewall_rule.side_effect = mock_responses
        
        result = await rule_manager.create_observatory_whitelist_rules()
        
        assert len(result) == len(rule_manager.OBSERVATORY_WHITELIST_RULES)
        assert mock_api_client.create_firewall_rule.call_count == len(rule_manager.OBSERVATORY_WHITELIST_RULES)
        
        # Check that each rule was created with correct data
        for i, call in enumerate(mock_api_client.create_firewall_rule.call_args_list):
            rule_data = call[0][0]
            assert "action" in rule_data
            assert "expression" in rule_data
            assert "description" in rule_data
            assert "priority" in rule_data
    
    @pytest.mark.asyncio
    async def test_create_observatory_whitelist_rules_api_error(self, rule_manager, mock_api_client):
        """Test API error handling in rule creation"""
        mock_api_client.create_firewall_rule.side_effect = CloudflareAPIError("API Error")
        
        with pytest.raises(CloudflareAPIError):
            await rule_manager.create_observatory_whitelist_rules()
    
    @pytest.mark.asyncio
    async def test_create_rate_limit_exception(self, rule_manager, mock_api_client):
        """Test rate limit exception creation"""
        mock_api_client.create_rate_limit_rule.return_value = {"id": "rate_rule_1"}
        
        result = await rule_manager.create_rate_limit_exception(
            pattern="/test/*",
            description="Test rate limit",
            rate_limit=1000
        )
        
        assert result["id"] == "rate_rule_1"
        mock_api_client.create_rate_limit_rule.assert_called_once()
        
        # Check rule data structure
        call_args = mock_api_client.create_rate_limit_rule.call_args[0][0]
        assert call_args["match"]["request"]["url"] == "/test/*"
        assert call_args["rate"] == 1000
        assert call_args["period"] == 60
        assert call_args["description"] == "Test rate limit"
    
    @pytest.mark.asyncio
    async def test_create_observatory_rate_limit_exceptions(self, rule_manager, mock_api_client):
        """Test creation of Observatory rate limit exceptions"""
        mock_responses = [
            {"id": f"rate_rule_{i}"}
            for i in range(4)  # 4 exceptions defined
        ]
        mock_api_client.create_rate_limit_rule.side_effect = mock_responses
        
        result = await rule_manager.create_observatory_rate_limit_exceptions()
        
        assert len(result) == 4
        assert mock_api_client.create_rate_limit_rule.call_count == 4
    
    @pytest.mark.asyncio
    async def test_get_existing_observatory_rules(self, rule_manager, mock_api_client):
        """Test getting existing Observatory rules"""
        # Mock firewall rules
        firewall_rules = [
            {"id": "rule1", "description": "Observatory internal polling"},
            {"id": "rule2", "description": "Regular firewall rule"},
            {"id": "rule3", "description": "Observatory WebSocket"}
        ]
        
        # Mock rate limit rules
        rate_limit_rules = [
            {"id": "rate1", "description": "Observatory rate limit"},
            {"id": "rate2", "description": "Regular rate limit"}
        ]
        
        mock_api_client.list_firewall_rules.return_value = firewall_rules
        mock_api_client.list_rate_limit_rules.return_value = rate_limit_rules
        
        observatory_firewall, observatory_rate_limit = await rule_manager.get_existing_observatory_rules()
        
        assert len(observatory_firewall) == 2  # 2 Observatory-related
        assert len(observatory_rate_limit) == 1  # 1 Observatory-related
        
        # Check that Observatory rules are filtered correctly
        observatory_firewall_ids = [rule["id"] for rule in observatory_firewall]
        assert "rule1" in observatory_firewall_ids
        assert "rule3" in observatory_firewall_ids
        assert "rule2" not in observatory_firewall_ids
    
    @pytest.mark.asyncio
    async def test_update_rule_priority(self, rule_manager, mock_api_client):
        """Test updating rule priority"""
        # Mock existing rule
        existing_rule = {
            "id": "rule1",
            "action": "allow",
            "expression": "true",
            "description": "Test rule",
            "priority": 10,
            "paused": False
        }
        
        mock_api_client.list_firewall_rules.return_value = [existing_rule]
        mock_api_client.update_firewall_rule.return_value = {"id": "rule1", "priority": 5}
        
        result = await rule_manager.update_rule_priority("rule1", 5)
        
        assert result["id"] == "rule1"
        assert result["priority"] == 5
        
        # Check update call
        update_call_args = mock_api_client.update_firewall_rule.call_args[0]
        assert update_call_args[0] == "rule1"
        assert update_call_args[1]["priority"] == 5
    
    @pytest.mark.asyncio
    async def test_update_rule_priority_not_found(self, rule_manager, mock_api_client):
        """Test updating priority of non-existent rule"""
        mock_api_client.list_firewall_rules.return_value = []
        
        with pytest.raises(CloudflareAPIError) as exc_info:
            await rule_manager.update_rule_priority("nonexistent", 5)
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_disable_rule(self, rule_manager, mock_api_client):
        """Test disabling a rule"""
        existing_rule = {
            "id": "rule1",
            "action": "allow",
            "expression": "true",
            "description": "Test rule",
            "priority": 10,
            "paused": False
        }
        
        mock_api_client.list_firewall_rules.return_value = [existing_rule]
        mock_api_client.update_firewall_rule.return_value = {"id": "rule1", "paused": True}
        
        result = await rule_manager.disable_rule("rule1")
        
        assert result["id"] == "rule1"
        assert result["paused"] is True
        
        # Check update call
        update_call_args = mock_api_client.update_firewall_rule.call_args[0]
        assert update_call_args[0] == "rule1"
        assert update_call_args[1]["paused"] is True
    
    @pytest.mark.asyncio
    async def test_cleanup_observatory_rules(self, rule_manager, mock_api_client):
        """Test cleanup of Observatory rules"""
        # Mock existing rules
        observatory_firewall = [
            {"id": "rule1", "description": "Observatory rule 1"},
            {"id": "rule2", "description": "Observatory rule 2"}
        ]
        
        observatory_rate_limit = [
            {"id": "rate1", "description": "Observatory rate limit"}
        ]
        
        mock_api_client.list_firewall_rules.return_value = observatory_firewall
        mock_api_client.list_rate_limit_rules.return_value = observatory_rate_limit
        mock_api_client.delete_firewall_rule.return_value = True
        
        result = await rule_manager.cleanup_observatory_rules()
        
        assert result["firewall_rules_deleted"] == 2
        assert result["rate_limit_rules_deleted"] == 0  # Not implemented yet
        assert result["errors"] == 0
        
        # Check that delete was called for each firewall rule
        assert mock_api_client.delete_firewall_rule.call_count == 2
    
    @pytest.mark.asyncio
    async def test_cleanup_observatory_rules_with_errors(self, rule_manager, mock_api_client):
        """Test cleanup with some errors"""
        observatory_firewall = [
            {"id": "rule1", "description": "Observatory rule 1"},
            {"id": "rule2", "description": "Observatory rule 2"}
        ]
        
        mock_api_client.list_firewall_rules.return_value = observatory_firewall
        mock_api_client.delete_firewall_rule.side_effect = [
            True,  # First deletion succeeds
            CloudflareAPIError("Delete failed")  # Second deletion fails
        ]
        
        result = await rule_manager.cleanup_observatory_rules()
        
        assert result["firewall_rules_deleted"] == 1
        assert result["errors"] == 1
    
    def test_build_firewall_rule_data(self, rule_manager):
        """Test building firewall rule data"""
        rule = ObservatoryRule(
            name="test_rule",
            expression="true",
            action=RuleAction.ALLOW,
            description="Test rule",
            priority=5,
            enabled=True
        )
        
        rule_data = rule_manager._build_firewall_rule_data(rule)
        
        assert rule_data["action"] == "allow"
        assert rule_data["expression"] == "true"
        assert rule_data["description"] == "Test rule"
        assert rule_data["priority"] == 5
        assert rule_data["paused"] is False  # enabled=True means paused=False
    
    def test_build_firewall_rule_data_disabled(self, rule_manager):
        """Test building firewall rule data for disabled rule"""
        rule = ObservatoryRule(
            name="test_rule",
            expression="true",
            action=RuleAction.ALLOW,
            description="Test rule",
            priority=5,
            enabled=False
        )
        
        rule_data = rule_manager._build_firewall_rule_data(rule)
        
        assert rule_data["paused"] is True  # enabled=False means paused=True
    
    def test_log_action(self, rule_manager):
        """Test logging functionality"""
        with patch('builtins.print') as mock_print:
            rule_manager._log_action("test_action", "completed", {"test": "data"})
            
            mock_print.assert_called_once()
            # Verify JSON format
            call_args = mock_print.call_args[0][0]
            import json
            log_data = json.loads(call_args)
            
            assert log_data["task"] == "5.1"
            assert log_data["action"] == "test_action"
            assert log_data["status"] == "completed"
            assert log_data["details"] == {"test": "data"}