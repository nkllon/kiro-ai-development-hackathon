"""
Unit tests for CloudflareWhitelistManager

Tests the main orchestrator for Observatory Cloudflare integration
including whitelist operations, security validation, and monitoring.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from src.beast_mode.observatory.cloudflare.whitelist_manager import (
    CloudflareWhitelistManager,
    WhitelistOperationResult
)
from src.beast_mode.observatory.cloudflare.api_client import CloudflareAPIError
from src.beast_mode.observatory.cloudflare.security_validator import SecurityValidationReport, ValidationResult


class TestWhitelistOperationResult:
    """Test WhitelistOperationResult dataclass"""
    
    def test_result_creation(self):
        """Test basic result creation"""
        result = WhitelistOperationResult(
            success=True,
            rules_created=5,
            rules_updated=2,
            rules_deleted=1,
            errors=[],
            warnings=["Test warning"]
        )
        
        assert result.success is True
        assert result.rules_created == 5
        assert result.rules_updated == 2
        assert result.rules_deleted == 1
        assert result.errors == []
        assert result.warnings == ["Test warning"]
        assert result.security_validation is None
    
    def test_result_with_validation(self):
        """Test result with security validation"""
        validation_report = SecurityValidationReport(
            overall_status=ValidationResult.PASS,
            checks_performed=5,
            checks_passed=5,
            checks_failed=0,
            checks_warning=0,
            security_score=100.0,
            checks=[],
            summary="All checks passed",
            timestamp=datetime.utcnow()
        )
        
        result = WhitelistOperationResult(
            success=True,
            rules_created=3,
            rules_updated=0,
            rules_deleted=0,
            errors=[],
            warnings=[],
            security_validation=validation_report
        )
        
        assert result.security_validation == validation_report


class TestCloudflareWhitelistManager:
    """Test CloudflareWhitelistManager functionality"""
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_rule_manager(self):
        """Create mock rule manager"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_traffic_analyzer(self):
        """Create mock traffic analyzer"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_security_validator(self):
        """Create mock security validator"""
        return AsyncMock()
    
    @pytest.fixture
    def whitelist_manager(self, mock_api_client, mock_rule_manager, 
                         mock_traffic_analyzer, mock_security_validator):
        """Create whitelist manager with mocks"""
        with patch('src.beast_mode.observatory.cloudflare.whitelist_manager.CloudflareAPIClient') as mock_client_class, \
             patch('src.beast_mode.observatory.cloudflare.whitelist_manager.RuleManager') as mock_rule_class, \
             patch('src.beast_mode.observatory.cloudflare.whitelist_manager.TrafficAnalyzer') as mock_traffic_class, \
             patch('src.beast_mode.observatory.cloudflare.whitelist_manager.SecurityValidator') as mock_security_class:
            
            mock_client_class.return_value = mock_api_client
            mock_rule_class.return_value = mock_rule_manager
            mock_traffic_class.return_value = mock_traffic_analyzer
            mock_security_class.return_value = mock_security_validator
            
            manager = CloudflareWhitelistManager("test_token", "test_zone")
            return manager
    
    def test_whitelist_manager_initialization(self, whitelist_manager):
        """Test whitelist manager initialization"""
        assert whitelist_manager.config.api_token == "test_token"
        assert whitelist_manager.config.zone_id == "test_zone"
        assert whitelist_manager.api_client is not None
        assert whitelist_manager.rule_manager is not None
        assert whitelist_manager.traffic_analyzer is not None
        assert whitelist_manager.security_validator is not None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, whitelist_manager, mock_api_client):
        """Test async context manager"""
        async with whitelist_manager:
            mock_api_client.__aenter__.assert_called_once()
        
        mock_api_client.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_whitelist_observatory_patterns_success(self, whitelist_manager, 
                                                       mock_api_client, mock_rule_manager):
        """Test successful Observatory pattern whitelisting"""
        mock_api_client.test_connection.return_value = True
        mock_rule_manager.create_observatory_whitelist_rules.return_value = [
            {"id": "rule1"}, {"id": "rule2"}, {"id": "rule3"}
        ]
        
        result = await whitelist_manager.whitelist_observatory_patterns()
        
        assert result == ["rule1", "rule2", "rule3"]
        mock_api_client.test_connection.assert_called_once()
        mock_rule_manager.create_observatory_whitelist_rules.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_whitelist_observatory_patterns_connection_failure(self, whitelist_manager, 
                                                                 mock_api_client):
        """Test Observatory pattern whitelisting with connection failure"""
        mock_api_client.test_connection.return_value = False
        
        with pytest.raises(CloudflareAPIError) as exc_info:
            await whitelist_manager.whitelist_observatory_patterns()
        
        assert "Failed to connect" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_whitelist_observatory_patterns_api_error(self, whitelist_manager, 
                                                          mock_api_client, mock_rule_manager):
        """Test Observatory pattern whitelisting with API error"""
        mock_api_client.test_connection.return_value = True
        mock_rule_manager.create_observatory_whitelist_rules.side_effect = CloudflareAPIError("API Error")
        
        with pytest.raises(CloudflareAPIError):
            await whitelist_manager.whitelist_observatory_patterns()
    
    @pytest.mark.asyncio
    async def test_create_rate_limit_exception_success(self, whitelist_manager, mock_rule_manager):
        """Test successful rate limit exception creation"""
        mock_rule_manager.create_observatory_rate_limit_exceptions.return_value = [
            {"id": "rate1"}, {"id": "rate2"}
        ]
        
        result = await whitelist_manager.create_rate_limit_exception()
        
        assert result == "rate1"  # Returns first rule ID
        mock_rule_manager.create_observatory_rate_limit_exceptions.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_rate_limit_exception_no_rules(self, whitelist_manager, mock_rule_manager):
        """Test rate limit exception creation with no rules created"""
        mock_rule_manager.create_observatory_rate_limit_exceptions.return_value = []
        
        result = await whitelist_manager.create_rate_limit_exception()
        
        assert result == "no_rules_created"
    
    @pytest.mark.asyncio
    async def test_create_rate_limit_exception_api_error(self, whitelist_manager, mock_rule_manager):
        """Test rate limit exception creation with API error"""
        mock_rule_manager.create_observatory_rate_limit_exceptions.side_effect = CloudflareAPIError("API Error")
        
        with pytest.raises(CloudflareAPIError):
            await whitelist_manager.create_rate_limit_exception()
    
    @pytest.mark.asyncio
    async def test_validate_security_rules_success(self, whitelist_manager, mock_security_validator):
        """Test successful security validation"""
        validation_report = SecurityValidationReport(
            overall_status=ValidationResult.PASS,
            checks_performed=5,
            checks_passed=5,
            checks_failed=0,
            checks_warning=0,
            security_score=100.0,
            checks=[],
            summary="All checks passed",
            timestamp=datetime.utcnow()
        )
        
        mock_security_validator.validate_observatory_integration.return_value = validation_report
        
        result = await whitelist_manager.validate_security_rules()
        
        assert result is True
        mock_security_validator.validate_observatory_integration.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_security_rules_warning(self, whitelist_manager, mock_security_validator):
        """Test security validation with warnings"""
        validation_report = SecurityValidationReport(
            overall_status=ValidationResult.WARNING,
            checks_performed=5,
            checks_passed=4,
            checks_failed=0,
            checks_warning=1,
            security_score=80.0,
            checks=[],
            summary="Validation passed with warnings",
            timestamp=datetime.utcnow()
        )
        
        mock_security_validator.validate_observatory_integration.return_value = validation_report
        
        result = await whitelist_manager.validate_security_rules()
        
        assert result is True  # Warnings still count as pass
    
    @pytest.mark.asyncio
    async def test_validate_security_rules_failure(self, whitelist_manager, mock_security_validator):
        """Test failed security validation"""
        validation_report = SecurityValidationReport(
            overall_status=ValidationResult.FAIL,
            checks_performed=5,
            checks_passed=3,
            checks_failed=2,
            checks_warning=0,
            security_score=60.0,
            checks=[],
            summary="Validation failed",
            timestamp=datetime.utcnow()
        )
        
        mock_security_validator.validate_observatory_integration.return_value = validation_report
        
        result = await whitelist_manager.validate_security_rules()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_security_rules_exception(self, whitelist_manager, mock_security_validator):
        """Test security validation with exception"""
        mock_security_validator.validate_observatory_integration.side_effect = Exception("Validation error")
        
        with pytest.raises(CloudflareAPIError) as exc_info:
            await whitelist_manager.validate_security_rules()
        
        assert "Security validation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_bot_protection_events(self, whitelist_manager, mock_api_client):
        """Test getting bot protection events"""
        mock_events = [
            {"id": "event1", "action": "block"},
            {"id": "event2", "action": "challenge"},
            {"id": "event3", "action": "allow"}
        ]
        
        mock_api_client.get_security_events.return_value = mock_events
        
        result = await whitelist_manager.get_bot_protection_events()
        
        assert len(result) == 2  # Only blocked/challenged events
        assert result[0]["id"] == "event1"
        assert result[1]["id"] == "event2"
        mock_api_client.get_security_events.assert_called_once_with(limit=100)
    
    @pytest.mark.asyncio
    async def test_get_bot_protection_events_api_error(self, whitelist_manager, mock_api_client):
        """Test getting bot protection events with API error"""
        mock_api_client.get_security_events.side_effect = CloudflareAPIError("API Error")
        
        with pytest.raises(CloudflareAPIError):
            await whitelist_manager.get_bot_protection_events()
    
    @pytest.mark.asyncio
    async def test_setup_observatory_integration_success(self, whitelist_manager, 
                                                       mock_api_client, mock_rule_manager, 
                                                       mock_security_validator):
        """Test successful Observatory integration setup"""
        # Mock successful operations
        mock_api_client.test_connection.return_value = True
        mock_rule_manager.create_observatory_whitelist_rules.return_value = [{"id": "rule1"}]
        mock_rule_manager.create_observatory_rate_limit_exceptions.return_value = [{"id": "rate1"}]
        
        validation_report = SecurityValidationReport(
            overall_status=ValidationResult.PASS,
            checks_performed=5,
            checks_passed=5,
            checks_failed=0,
            checks_warning=0,
            security_score=100.0,
            checks=[],
            summary="All checks passed",
            timestamp=datetime.utcnow()
        )
        
        mock_security_validator.validate_observatory_integration.return_value = validation_report
        
        result = await whitelist_manager.setup_observatory_integration()
        
        assert result.success is True
        assert result.rules_created == 2  # 1 firewall + 1 rate limit
        assert result.rules_updated == 0
        assert result.rules_deleted == 0
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.security_validation == validation_report
    
    @pytest.mark.asyncio
    async def test_setup_observatory_integration_with_errors(self, whitelist_manager, 
                                                           mock_api_client, mock_rule_manager, 
                                                           mock_security_validator):
        """Test Observatory integration setup with errors"""
        # Mock failed operations
        mock_api_client.test_connection.return_value = True
        mock_rule_manager.create_observatory_whitelist_rules.side_effect = CloudflareAPIError("Rule creation failed")
        mock_rule_manager.create_observatory_rate_limit_exceptions.side_effect = CloudflareAPIError("Rate limit failed")
        
        validation_report = SecurityValidationReport(
            overall_status=ValidationResult.FAIL,
            checks_performed=5,
            checks_passed=3,
            checks_failed=2,
            checks_warning=0,
            security_score=60.0,
            checks=[],
            summary="Validation failed",
            timestamp=datetime.utcnow()
        )
        
        mock_security_validator.validate_observatory_integration.return_value = validation_report
        
        result = await whitelist_manager.setup_observatory_integration()
        
        assert result.success is False
        assert result.rules_created == 0
        assert len(result.errors) == 2
        assert "Rule creation failed" in result.errors[0]
        assert "Rate limit failed" in result.errors[1]
        assert len(result.warnings) == 1
        assert "immediate review required" in result.warnings[0]
    
    @pytest.mark.asyncio
    async def test_monitor_observatory_traffic(self, whitelist_manager, 
                                             mock_traffic_analyzer, mock_security_validator):
        """Test Observatory traffic monitoring"""
        traffic_summary = {
            "total_requests_24h": 1000,
            "observatory_requests_24h": 200,
            "blocked_requests_24h": 10
        }
        
        effectiveness = {
            "whitelist_success_rate": 95.0,
            "false_positive_rate": 5.0
        }
        
        security_status = {
            "security_score": 90.0,
            "overall_status": "pass"
        }
        
        mock_traffic_analyzer.get_observatory_traffic_summary.return_value = traffic_summary
        mock_traffic_analyzer.monitor_whitelist_effectiveness.return_value = effectiveness
        mock_security_validator.get_security_status.return_value = security_status
        
        result = await whitelist_manager.monitor_observatory_traffic()
        
        assert result["traffic_summary"] == traffic_summary
        assert result["whitelist_effectiveness"] == effectiveness
        assert result["security_status"] == security_status
        assert "monitoring_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_monitor_observatory_traffic_error(self, whitelist_manager, mock_traffic_analyzer):
        """Test Observatory traffic monitoring with error"""
        mock_traffic_analyzer.get_observatory_traffic_summary.side_effect = Exception("Monitoring error")
        
        with pytest.raises(CloudflareAPIError) as exc_info:
            await whitelist_manager.monitor_observatory_traffic()
        
        assert "Traffic monitoring failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_cleanup_observatory_rules(self, whitelist_manager, mock_rule_manager):
        """Test cleanup of Observatory rules"""
        cleanup_stats = {
            "firewall_rules_deleted": 3,
            "rate_limit_rules_deleted": 2,
            "errors": 0
        }
        
        mock_rule_manager.cleanup_observatory_rules.return_value = cleanup_stats
        
        result = await whitelist_manager.cleanup_observatory_rules()
        
        assert result == cleanup_stats
        mock_rule_manager.cleanup_observatory_rules.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_integration_status(self, whitelist_manager, mock_rule_manager, 
                                        mock_traffic_analyzer, mock_security_validator):
        """Test getting integration status"""
        firewall_rules = [{"id": "rule1"}, {"id": "rule2"}]
        rate_limit_rules = [{"id": "rate1"}]
        
        traffic_monitoring = {
            "traffic_summary": {"total_requests_24h": 1000},
            "whitelist_effectiveness": {"success_rate": 95.0}
        }
        
        security_status = {
            "security_score": 90.0,
            "overall_status": "pass"
        }
        
        mock_rule_manager.get_existing_observatory_rules.return_value = (firewall_rules, rate_limit_rules)
        mock_traffic_analyzer.monitor_observatory_traffic.return_value = traffic_monitoring
        mock_security_validator.get_security_status.return_value = security_status
        
        result = await whitelist_manager.get_integration_status()
        
        assert result["integration_active"] is True
        assert result["firewall_rules_count"] == 2
        assert result["rate_limit_rules_count"] == 1
        assert result["traffic_monitoring"] == traffic_monitoring
        assert result["security_status"] == security_status
        assert "last_updated" in result
    
    @pytest.mark.asyncio
    async def test_test_observatory_traffic_flow(self, whitelist_manager, mock_traffic_analyzer):
        """Test Observatory traffic flow testing"""
        from src.beast_mode.observatory.cloudflare.traffic_analyzer import TrafficAnalysis, TrafficPattern
        
        mock_analysis = TrafficAnalysis(
            total_requests=100,
            observatory_requests=20,
            blocked_requests=2,
            pattern_breakdown={
                TrafficPattern.INTERNAL_POLLING: 10,
                TrafficPattern.WEBSOCKET_CONNECTION: 10
            },
            suspicious_activity=[{"type": "test_suspicious"}],
            recommendations=["Test recommendation"]
        )
        
        mock_traffic_analyzer.analyze_recent_traffic.return_value = mock_analysis
        
        result = await whitelist_manager.test_observatory_traffic_flow()
        
        assert result["observatory_traffic_detected"] is True
        assert result["observatory_requests"] == 20
        assert result["blocked_requests"] == 2
        assert result["success_rate"] == 90.0  # (20-2)/20 * 100
        assert result["pattern_breakdown"]["internal_polling"] == 10
        assert result["pattern_breakdown"]["websocket_connection"] == 10
        assert result["suspicious_activity"] == 1
        assert "test_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_test_observatory_traffic_flow_no_traffic(self, whitelist_manager, mock_traffic_analyzer):
        """Test traffic flow testing with no Observatory traffic"""
        from src.beast_mode.observatory.cloudflare.traffic_analyzer import TrafficAnalysis, TrafficPattern
        
        mock_analysis = TrafficAnalysis(
            total_requests=100,
            observatory_requests=0,
            blocked_requests=0,
            pattern_breakdown={TrafficPattern.UNKNOWN: 100},
            suspicious_activity=[],
            recommendations=[]
        )
        
        mock_traffic_analyzer.analyze_recent_traffic.return_value = mock_analysis
        
        result = await whitelist_manager.test_observatory_traffic_flow()
        
        assert result["observatory_traffic_detected"] is False
        assert result["observatory_requests"] == 0
        assert result["success_rate"] == 100.0  # No traffic to test
        assert result["suspicious_activity"] == 0
    
    def test_log_action(self, whitelist_manager):
        """Test logging functionality"""
        with patch('builtins.print') as mock_print:
            whitelist_manager._log_action("test_action", "completed", {"test": "data"})
            
            mock_print.assert_called_once()
            # Verify JSON format
            call_args = mock_print.call_args[0][0]
            import json
            log_data = json.loads(call_args)
            
            assert log_data["task"] == "5.1"
            assert log_data["action"] == "test_action"
            assert log_data["status"] == "completed"
            assert log_data["details"] == {"test": "data"}