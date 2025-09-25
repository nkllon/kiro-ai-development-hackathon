"""
Unit tests for Discord Bot models

Tests the data models used in Discord bot integration.
"""

import pytest
from datetime import datetime
from dataclasses import asdict

from src.beast_mode.observatory.discord_bot.models import (
    BotConfig, BotStatus, NotificationLevel, DiscordChannel,
    CommandContext, CommandResult, ServiceHealth, BotHealthStatus,
    NotificationMessage, PluginConfig, AuditLogEntry
)


class TestBotConfig:
    """Test BotConfig model"""
    
    def test_bot_config_creation(self):
        """Test creating BotConfig with minimal parameters"""
        config = BotConfig(token="test_token")
        
        assert config.token == "test_token"
        assert config.command_prefix == "!bmo"
        assert config.ai_enabled is True
        assert config.observatory_integration is True
    
    def test_bot_config_full_parameters(self):
        """Test creating BotConfig with all parameters"""
        config = BotConfig(
            token="test_token",
            status_channel_id="123456789",
            alerts_channel_id="987654321",
            general_channel_id="555666777",
            command_prefix="!test",
            ai_enabled=False,
            observatory_integration=False,
            health_monitoring=False,
            audit_logging=False,
            rate_limiting=False
        )
        
        assert config.token == "test_token"
        assert config.status_channel_id == "123456789"
        assert config.command_prefix == "!test"
        assert config.ai_enabled is False
        assert config.observatory_integration is False


class TestCommandContext:
    """Test CommandContext model"""
    
    def test_command_context_creation(self):
        """Test creating CommandContext"""
        context = CommandContext(
            channel_id="123",
            user_id="456",
            guild_id="789",
            message_id="101112",
            command="help",
            args=["status"],
            raw_message="!bmo help status"
        )
        
        assert context.channel_id == "123"
        assert context.user_id == "456"
        assert context.command == "help"
        assert context.args == ["status"]
        assert isinstance(context.timestamp, datetime)
    
    def test_command_context_optional_fields(self):
        """Test CommandContext with optional fields"""
        context = CommandContext(
            channel_id="123",
            user_id="456",
            guild_id=None,  # DM context
            message_id="101112",
            command="ping",
            args=[],
            raw_message="!bmo ping",
            observatory_context={"test": "data"},
            correlation_id="test-123"
        )
        
        assert context.guild_id is None
        assert context.observatory_context == {"test": "data"}
        assert context.correlation_id == "test-123"


class TestCommandResult:
    """Test CommandResult model"""
    
    def test_successful_command_result(self):
        """Test successful command result"""
        result = CommandResult(
            success=True,
            message="Command executed successfully",
            execution_time_ms=150.5
        )
        
        assert result.success is True
        assert result.message == "Command executed successfully"
        assert result.execution_time_ms == 150.5
        assert result.error_code is None
        assert result.fallback_used is False
    
    def test_failed_command_result(self):
        """Test failed command result"""
        result = CommandResult(
            success=False,
            message="Command failed",
            error_code="VALIDATION_ERROR",
            error_details="Invalid parameter",
            fallback_used=True
        )
        
        assert result.success is False
        assert result.error_code == "VALIDATION_ERROR"
        assert result.error_details == "Invalid parameter"
        assert result.fallback_used is True


class TestNotificationMessage:
    """Test NotificationMessage model"""
    
    def test_notification_message_creation(self):
        """Test creating notification message"""
        notification = NotificationMessage(
            title="Test Alert",
            message="This is a test notification",
            level=NotificationLevel.WARNING,
            components=["test_component"],
            metadata={"severity": "medium"}
        )
        
        assert notification.title == "Test Alert"
        assert notification.level == NotificationLevel.WARNING
        assert notification.components == ["test_component"]
        assert notification.metadata == {"severity": "medium"}
        assert notification.embed is True
        assert isinstance(notification.timestamp, datetime)


class TestBotHealthStatus:
    """Test BotHealthStatus model"""
    
    def test_bot_health_status_creation(self):
        """Test creating bot health status"""
        health = BotHealthStatus(
            status=BotStatus.ONLINE,
            uptime_seconds=3600.0,
            total_commands=100,
            successful_commands=95,
            failed_commands=5,
            avg_response_time_ms=250.0,
            memory_usage_mb=128.5
        )
        
        assert health.status == BotStatus.ONLINE
        assert health.uptime_seconds == 3600.0
        assert health.total_commands == 100
        assert health.successful_commands == 95
        assert health.failed_commands == 5
        assert health.avg_response_time_ms == 250.0
        assert health.memory_usage_mb == 128.5
        assert isinstance(health.last_updated, datetime)


class TestEnums:
    """Test enum values"""
    
    def test_notification_level_values(self):
        """Test NotificationLevel enum values"""
        assert NotificationLevel.DEBUG == "debug"
        assert NotificationLevel.INFO == "info"
        assert NotificationLevel.WARNING == "warning"
        assert NotificationLevel.ERROR == "error"
        assert NotificationLevel.CRITICAL == "critical"
    
    def test_bot_status_values(self):
        """Test BotStatus enum values"""
        assert BotStatus.STARTING == "starting"
        assert BotStatus.ONLINE == "online"
        assert BotStatus.DEGRADED == "degraded"
        assert BotStatus.OFFLINE == "offline"
        assert BotStatus.ERROR == "error"
    
    def test_service_health_values(self):
        """Test ServiceHealth enum values"""
        assert ServiceHealth.HEALTHY == "healthy"
        assert ServiceHealth.DEGRADED == "degraded"
        assert ServiceHealth.UNHEALTHY == "unhealthy"
        assert ServiceHealth.UNKNOWN == "unknown"


class TestAuditLogEntry:
    """Test AuditLogEntry model"""
    
    def test_audit_log_entry_creation(self):
        """Test creating audit log entry"""
        entry = AuditLogEntry(
            timestamp=datetime.utcnow(),
            user_id="123456",
            action="command_execution",
            resource="help_command",
            details={"command": "help", "args": []},
            success=True,
            correlation_id="test-correlation-123"
        )
        
        assert entry.user_id == "123456"
        assert entry.action == "command_execution"
        assert entry.resource == "help_command"
        assert entry.success is True
        assert entry.details == {"command": "help", "args": []}
        assert entry.correlation_id == "test-correlation-123"


class TestDataclassConversion:
    """Test dataclass conversion methods"""
    
    def test_bot_config_to_dict(self):
        """Test converting BotConfig to dictionary"""
        config = BotConfig(
            token="test_token",
            command_prefix="!test"
        )
        
        config_dict = asdict(config)
        
        assert isinstance(config_dict, dict)
        assert config_dict["token"] == "test_token"
        assert config_dict["command_prefix"] == "!test"
        assert "service_registry_config" in config_dict
        assert "plugin_config" in config_dict
    
    def test_command_result_serialization(self):
        """Test CommandResult can be serialized"""
        result = CommandResult(
            success=True,
            message="Test message",
            execution_time_ms=100.0
        )
        
        result_dict = asdict(result)
        
        assert result_dict["success"] is True
        assert result_dict["message"] == "Test message"
        assert result_dict["execution_time_ms"] == 100.0