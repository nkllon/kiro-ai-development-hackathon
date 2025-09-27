"""
Unit tests for CloudflareWhitelistManager.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.beast_mode.observatory.cloudflare.whitelist_manager import CloudflareWhitelistManager
from src.beast_mode.observatory.cloudflare.api_client import CloudflareAPIError


class TestCloudflareWhitelistManager:
    """Test cases for CloudflareWhitelistManager."""
    
    @pytest.fixture
    def manager(self):
        """Create a CloudflareWhitelistManager instance for testing."""
        return CloudflareWhitelistManager("test_token", "test_zone_id")
        
    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        return AsyncMock()
        
    @pytest.fixture
    def mock_rule_manager(self):
        """Mock rule manager."""
        return AsyncMock()
        
    @pytest.fixture
    def mock_traffic_analyzer(self):
        """Mock traffic analyzer."""
        return AsyncMock()
        
    @pytest.fixture
    def mock_security_validator(self):
        """Mock security validator."""
        return AsyncMock()
        
    @pytest.mark.asyncio
    async def test_whitelist_observatory_patterns_success(self, manager):
        """Test successful whitelist pattern creation."""
        # Mock dependencies
        manager.traffic_analyzer.get_recommended_whitelist_rules.return_value = [
            MagicMock(expression='(http.user_agent contains "Observatory-Internal")', 
                     description="Test pattern", pattern_type="user_agent")
        ]
        
        manager.security_validator.validate_rule_set.return_value = {
            "overall_score": 0.9,
            "individual_results": []
        }
        
        manager.rule_manager.create_whitelist_rule.return_value = {
            "result": {"id": "rule_123"}
        }
        
        # Test the method
        result = await manager.whitelist_observatory_patterns()
        
        # Verify results
        assert len(result) == 1
        assert result[0] == "rule_123"
        
        # Verify method calls
        manager.traffic_analyzer.get_recommended_whitelist_rules.assert_called_once()
        manager.security_validator.validate_rule_set.assert_called_once()
        manager.rule_manager.create_whitelist_rule.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_whitelist_observatory_patterns_security_validation_fails(self, manager):
        """Test whitelist pattern creation when security validation fails."""
        # Mock dependencies
        manager.traffic_analyzer.get_recommended_whitelist_rules.return_value = [
            MagicMock(expression='(http.user_agent contains "Observatory-Internal")', 
                     description="Test pattern", pattern_type="user_agent")
        ]
        
        manager.security_validator.validate_rule_set.return_value = {
            "overall_score": 0.5,  # Low score
            "individual_results": []
        }
        
        # Test the method - should raise ValueError
        with pytest.raises(ValueError, match="Security validation failed"):
            await manager.whitelist_observatory_patterns()
            
    @pytest.mark.asyncio
    async def test_create_rate_limit_exception_success(self, manager):
        """Test successful rate limit exception creation."""
        # Mock dependencies
        manager.rule_manager.create_rate_limit_exception.return_value = {
            "result": {"id": "rate_limit_123"}
        }
        
        # Test the method
        result = await manager.create_rate_limit_exception()
        
        # Verify results
        assert result == "rate_limit_123"
        
        # Verify method calls
        manager.rule_manager.create_rate_limit_exception.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_create_rate_limit_exception_failure(self, manager):
        """Test rate limit exception creation failure."""
        # Mock dependencies
        manager.rule_manager.create_rate_limit_exception.side_effect = CloudflareAPIError("API Error")
        
        # Test the method - should raise CloudflareAPIError
        with pytest.raises(CloudflareAPIError):
            await manager.create_rate_limit_exception()
            
    @pytest.mark.asyncio
    async def test_validate_security_rules_success(self, manager):
        """Test successful security rules validation."""
        # Mock dependencies
        manager.security_validator.audit_security_rules.return_value = {
            "total_rules": 10,
            "allow_rules": 5,
            "block_rules": 3,
            "challenge_rules": 2
        }
        
        manager.api_client.get_bot_management_config.return_value = {
            "result": {"enable_js": True}
        }
        
        manager.rule_manager.list_observatory_rules.return_value = [
            {"id": "rule_1", "type": "firewall"}
        ]
        
        # Test the method
        result = await manager.validate_security_rules()
        
        # Verify results
        assert result is True
        
        # Verify method calls
        manager.security_validator.audit_security_rules.assert_called_once()
        manager.api_client.get_bot_management_config.assert_called_once()
        manager.rule_manager.list_observatory_rules.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_validate_security_rules_failure(self, manager):
        """Test security rules validation failure."""
        # Mock dependencies
        manager.security_validator.audit_security_rules.return_value = {
            "total_rules": 0  # No rules
        }
        
        manager.api_client.get_bot_management_config.return_value = {
            "result": {"enable_js": False}  # Bot protection disabled
        }
        
        manager.rule_manager.list_observatory_rules.return_value = []  # No Observatory rules
        
        # Test the method
        result = await manager.validate_security_rules()
        
        # Verify results
        assert result is False
        
    @pytest.mark.asyncio
    async def test_get_bot_protection_events_success(self, manager):
        """Test successful bot protection events retrieval."""
        # Mock dependencies
        mock_events = [
            {"action": "block", "user_agent": "bot", "uri": "/test"},
            {"action": "challenge", "user_agent": "suspicious", "uri": "/admin"},
            {"action": "allow", "user_agent": "normal", "uri": "/"}
        ]
        
        manager.api_client.get_security_events.return_value = {
            "result": mock_events
        }
        
        # Test the method
        result = await manager.get_bot_protection_events()
        
        # Verify results - should only include blocked/challenged events
        assert len(result) == 2
        assert all(event["action"] in ["block", "challenge"] for event in result)
        
        # Verify method calls
        manager.api_client.get_security_events.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_analyze_traffic_patterns_success(self, manager):
        """Test successful traffic pattern analysis."""
        # Mock dependencies
        manager.traffic_analyzer.analyze_recent_traffic.return_value = {
            "patterns": [
                {"pattern_type": "user_agent", "confidence": 0.9}
            ],
            "summary": {
                "total_events": 100,
                "observatory_requests": 20,
                "blocked_observatory_requests": 5,
                "block_rate": 0.25
            }
        }
        
        # Test the method
        result = await manager.analyze_traffic_patterns(hours_back=12)
        
        # Verify results
        assert "patterns" in result
        assert "summary" in result
        assert result["summary"]["block_rate"] == 0.25
        
        # Verify method calls
        manager.traffic_analyzer.analyze_recent_traffic.assert_called_once_with(
            "test_zone_id", 12
        )
        
    @pytest.mark.asyncio
    async def test_deploy_observatory_whitelist_success(self, manager):
        """Test successful Observatory whitelist deployment."""
        # Mock all dependencies
        manager.analyze_traffic_patterns.return_value = {"patterns": []}
        manager.whitelist_observatory_patterns.return_value = ["rule_1", "rule_2"]
        manager.create_rate_limit_exception.return_value = "rate_limit_1"
        manager.validate_security_rules.return_value = True
        manager.get_bot_protection_events.return_value = [{"action": "block"}]
        
        # Test the method
        result = await manager.deploy_observatory_whitelist()
        
        # Verify results
        assert len(result["whitelist_rules"]) == 2
        assert len(result["rate_limit_exceptions"]) == 1
        assert result["validation_results"]["security_valid"] is True
        assert result["validation_results"]["recent_bot_events"] == 1
        assert len(result["errors"]) == 0
        
        # Verify method calls
        manager.analyze_traffic_patterns.assert_called_once()
        manager.whitelist_observatory_patterns.assert_called_once()
        manager.create_rate_limit_exception.assert_called_once()
        manager.validate_security_rules.assert_called_once()
        manager.get_bot_protection_events.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_deploy_observatory_whitelist_partial_failure(self, manager):
        """Test Observatory whitelist deployment with partial failures."""
        # Mock dependencies with some failures
        manager.analyze_traffic_patterns.return_value = {"patterns": []}
        manager.whitelist_observatory_patterns.side_effect = Exception("Whitelist failed")
        manager.create_rate_limit_exception.return_value = "rate_limit_1"
        manager.validate_security_rules.return_value = True
        manager.get_bot_protection_events.side_effect = Exception("Events failed")
        
        # Test the method
        result = await manager.deploy_observatory_whitelist()
        
        # Verify results
        assert len(result["whitelist_rules"]) == 0
        assert len(result["rate_limit_exceptions"]) == 1
        assert result["validation_results"]["security_valid"] is True
        assert len(result["errors"]) == 2  # Two failures
        
    @pytest.mark.asyncio
    async def test_cleanup_observatory_rules_success(self, manager):
        """Test successful Observatory rules cleanup."""
        # Mock dependencies
        manager.rule_manager.list_observatory_rules.return_value = [
            {"id": "rule_1", "type": "firewall"},
            {"id": "rule_2", "type": "firewall"}
        ]
        
        manager.rule_manager.delete_rule.return_value = {"result": {"id": "deleted"}}
        
        # Test the method
        result = await manager.cleanup_observatory_rules()
        
        # Verify results
        assert len(result["deleted_rules"]) == 2
        assert len(result["errors"]) == 0
        
        # Verify method calls
        manager.rule_manager.list_observatory_rules.assert_called_once()
        assert manager.rule_manager.delete_rule.call_count == 2
        
    @pytest.mark.asyncio
    async def test_cleanup_observatory_rules_partial_failure(self, manager):
        """Test Observatory rules cleanup with partial failures."""
        # Mock dependencies
        manager.rule_manager.list_observatory_rules.return_value = [
            {"id": "rule_1", "type": "firewall"},
            {"id": "rule_2", "type": "firewall"}
        ]
        
        # First deletion succeeds, second fails
        manager.rule_manager.delete_rule.side_effect = [
            {"result": {"id": "deleted"}},
            Exception("Delete failed")
        ]
        
        # Test the method
        result = await manager.cleanup_observatory_rules()
        
        # Verify results
        assert len(result["deleted_rules"]) == 1
        assert len(result["errors"]) == 1
        
    def test_log_action_format(self, manager):
        """Test that log_action produces correct JSON format."""
        with patch('builtins.print') as mock_print:
            manager._log_action("test_action", "completed", {"key": "value"})
            
            # Verify print was called
            mock_print.assert_called_once()
            
            # Verify JSON format
            call_args = mock_print.call_args[0][0]
            log_data = json.loads(call_args)
            
            assert log_data["task"] == "5.1"
            assert log_data["action"] == "test_action"
            assert log_data["status"] == "completed"
            assert log_data["details"]["key"] == "value"
            assert "timestamp" in log_data
            
    def test_observatory_rules_configuration(self, manager):
        """Test that Observatory rules are properly configured."""
        assert len(manager.observatory_rules) == 5
        
        # Check that all rules have required fields
        for rule in manager.observatory_rules:
            assert "expression" in rule
            assert "action" in rule
            assert "description" in rule
            assert rule["action"] == "allow"
            
        # Check specific rules
        expressions = [rule["expression"] for rule in manager.observatory_rules]
        assert any("Observatory-Internal" in expr for expr in expressions)
        assert any("/ws/" in expr for expr in expressions)
        assert any("x-observatory-client" in expr for expr in expressions)
        assert any("/health" in expr for expr in expressions)
        assert any("/api/observatory/" in expr for expr in expressions)