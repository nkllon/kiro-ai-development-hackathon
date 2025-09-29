"""
Unit tests for Recovery Strategies.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from src.beast_mode.observatory.recovery.failure_classifier import FailureType
from src.beast_mode.observatory.recovery.recovery_strategies import (
    WebSocketReconnectionStrategy,
    TunnelRestartStrategy,
    ConfigurationReloadStrategy,
    BotProtectionClearStrategy,
    FallbackActivationStrategy,
    RecoveryResult
)


class TestWebSocketReconnectionStrategy:
    """Test cases for WebSocketReconnectionStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a WebSocketReconnectionStrategy instance."""
        return WebSocketReconnectionStrategy()
    
    @pytest.mark.asyncio
    async def test_can_handle_connection_refused(self, strategy):
        """Test that strategy can handle connection refused."""
        assert await strategy.can_handle(FailureType.CONNECTION_REFUSED) == True
    
    @pytest.mark.asyncio
    async def test_can_handle_timeout(self, strategy):
        """Test that strategy can handle timeout."""
        assert await strategy.can_handle(FailureType.TIMEOUT) == True
    
    @pytest.mark.asyncio
    async def test_cannot_handle_bot_protection(self, strategy):
        """Test that strategy cannot handle bot protection."""
        assert await strategy.can_handle(FailureType.BOT_PROTECTION_TRIGGERED) == False
    
    @pytest.mark.asyncio
    async def test_cannot_handle_authentication_failed(self, strategy):
        """Test that strategy cannot handle authentication failed."""
        assert await strategy.can_handle(FailureType.AUTHENTICATION_FAILED) == False
    
    @pytest.mark.asyncio
    async def test_execute_successful_reconnection(self, strategy):
        """Test successful reconnection execution."""
        with patch.object(strategy, '_attempt_reconnection', return_value=True):
            result = await strategy.execute(FailureType.TIMEOUT, 1)
            
            assert result.success == True
            assert result.strategy_used == "websocket_reconnection"
            assert result.recovery_time > 0
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_execute_failed_reconnection(self, strategy):
        """Test failed reconnection execution."""
        with patch.object(strategy, '_attempt_reconnection', return_value=False):
            result = await strategy.execute(FailureType.CONNECTION_REFUSED, 1)
            
            assert result.success == False
            assert result.strategy_used == "websocket_reconnection"
            assert result.recovery_time > 0
            assert result.error_message == "Reconnection attempt failed"
    
    @pytest.mark.asyncio
    async def test_execute_with_exception(self, strategy):
        """Test execution with exception."""
        with patch.object(strategy, '_attempt_reconnection', side_effect=Exception("Test error")):
            result = await strategy.execute(FailureType.TIMEOUT, 1)
            
            assert result.success == False
            assert result.strategy_used == "websocket_reconnection"
            assert result.error_message == "Test error"
    
    def test_get_priority(self, strategy):
        """Test priority value."""
        assert strategy.get_priority() == 1


class TestTunnelRestartStrategy:
    """Test cases for TunnelRestartStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a TunnelRestartStrategy instance."""
        return TunnelRestartStrategy()
    
    @pytest.mark.asyncio
    async def test_can_handle_connection_refused(self, strategy):
        """Test that strategy can handle connection refused."""
        assert await strategy.can_handle(FailureType.CONNECTION_REFUSED) == True
    
    @pytest.mark.asyncio
    async def test_can_handle_upgrade_failed(self, strategy):
        """Test that strategy can handle upgrade failed."""
        assert await strategy.can_handle(FailureType.UPGRADE_FAILED) == True
    
    @pytest.mark.asyncio
    async def test_cannot_handle_rate_limited(self, strategy):
        """Test that strategy cannot handle rate limited."""
        assert await strategy.can_handle(FailureType.RATE_LIMITED) == False
    
    @pytest.mark.asyncio
    async def test_execute_successful_tunnel_restart(self, strategy):
        """Test successful tunnel restart execution."""
        with patch.object(strategy, '_stop_tunnel', return_value=None), \
             patch.object(strategy, '_start_tunnel', return_value=None), \
             patch.object(strategy, '_verify_tunnel_health', return_value=True):
            
            result = await strategy.execute(FailureType.CONNECTION_REFUSED, 1)
            
            assert result.success == True
            assert result.strategy_used == "tunnel_restart"
            assert result.recovery_time > 0
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_execute_failed_tunnel_restart(self, strategy):
        """Test failed tunnel restart execution."""
        with patch.object(strategy, '_stop_tunnel', return_value=None), \
             patch.object(strategy, '_start_tunnel', return_value=None), \
             patch.object(strategy, '_verify_tunnel_health', return_value=False):
            
            result = await strategy.execute(FailureType.CONNECTION_REFUSED, 1)
            
            assert result.success == False
            assert result.strategy_used == "tunnel_restart"
            assert result.error_message == "Tunnel restart failed - tunnel not healthy"
    
    @pytest.mark.asyncio
    async def test_execute_with_exception(self, strategy):
        """Test execution with exception."""
        with patch.object(strategy, '_stop_tunnel', side_effect=Exception("Test error")):
            result = await strategy.execute(FailureType.CONNECTION_REFUSED, 1)
            
            assert result.success == False
            assert result.strategy_used == "tunnel_restart"
            assert result.error_message == "Test error"
    
    def test_get_priority(self, strategy):
        """Test priority value."""
        assert strategy.get_priority() == 2


class TestConfigurationReloadStrategy:
    """Test cases for ConfigurationReloadStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a ConfigurationReloadStrategy instance."""
        return ConfigurationReloadStrategy()
    
    @pytest.mark.asyncio
    async def test_can_handle_authentication_failed(self, strategy):
        """Test that strategy can handle authentication failed."""
        assert await strategy.can_handle(FailureType.AUTHENTICATION_FAILED) == True
    
    @pytest.mark.asyncio
    async def test_can_handle_connection_refused(self, strategy):
        """Test that strategy can handle connection refused."""
        assert await strategy.can_handle(FailureType.CONNECTION_REFUSED) == True
    
    @pytest.mark.asyncio
    async def test_cannot_handle_timeout(self, strategy):
        """Test that strategy cannot handle timeout."""
        assert await strategy.can_handle(FailureType.TIMEOUT) == False
    
    @pytest.mark.asyncio
    async def test_execute_successful_config_reload(self, strategy):
        """Test successful configuration reload execution."""
        with patch.object(strategy, '_reload_configuration', return_value=None), \
             patch.object(strategy, '_restart_tunnel_with_config', return_value=None), \
             patch.object(strategy, '_verify_configuration', return_value=True):
            
            result = await strategy.execute(FailureType.AUTHENTICATION_FAILED, 1)
            
            assert result.success == True
            assert result.strategy_used == "configuration_reload"
            assert result.recovery_time > 0
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_execute_failed_config_reload(self, strategy):
        """Test failed configuration reload execution."""
        with patch.object(strategy, '_reload_configuration', return_value=None), \
             patch.object(strategy, '_restart_tunnel_with_config', return_value=None), \
             patch.object(strategy, '_verify_configuration', return_value=False):
            
            result = await strategy.execute(FailureType.AUTHENTICATION_FAILED, 1)
            
            assert result.success == False
            assert result.strategy_used == "configuration_reload"
            assert result.error_message == "Configuration reload failed"
    
    def test_get_priority(self, strategy):
        """Test priority value."""
        assert strategy.get_priority() == 3


class TestBotProtectionClearStrategy:
    """Test cases for BotProtectionClearStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a BotProtectionClearStrategy instance."""
        return BotProtectionClearStrategy()
    
    @pytest.mark.asyncio
    async def test_can_handle_bot_protection(self, strategy):
        """Test that strategy can handle bot protection."""
        assert await strategy.can_handle(FailureType.BOT_PROTECTION_TRIGGERED) == True
    
    @pytest.mark.asyncio
    async def test_cannot_handle_other_failures(self, strategy):
        """Test that strategy cannot handle other failures."""
        assert await strategy.can_handle(FailureType.CONNECTION_REFUSED) == False
        assert await strategy.can_handle(FailureType.TIMEOUT) == False
    
    @pytest.mark.asyncio
    async def test_execute_successful_bot_protection_clear(self, strategy):
        """Test successful bot protection clear execution."""
        with patch.object(strategy, '_clear_cached_blocks', return_value=None), \
             patch.object(strategy, '_test_protection_clear', return_value=True):
            
            result = await strategy.execute(FailureType.BOT_PROTECTION_TRIGGERED, 1)
            
            assert result.success == True
            assert result.strategy_used == "bot_protection_clear"
            assert result.recovery_time > 0
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_execute_failed_bot_protection_clear(self, strategy):
        """Test failed bot protection clear execution."""
        with patch.object(strategy, '_clear_cached_blocks', return_value=None), \
             patch.object(strategy, '_test_protection_clear', return_value=False):
            
            result = await strategy.execute(FailureType.BOT_PROTECTION_TRIGGERED, 1)
            
            assert result.success == False
            assert result.strategy_used == "bot_protection_clear"
            assert result.error_message == "Bot protection still active"
            assert result.fallback_activated == True
    
    @pytest.mark.asyncio
    async def test_execute_with_exception(self, strategy):
        """Test execution with exception."""
        with patch.object(strategy, '_clear_cached_blocks', side_effect=Exception("Test error")):
            result = await strategy.execute(FailureType.BOT_PROTECTION_TRIGGERED, 1)
            
            assert result.success == False
            assert result.strategy_used == "bot_protection_clear"
            assert result.error_message == "Test error"
            assert result.fallback_activated == True
    
    def test_get_priority(self, strategy):
        """Test priority value."""
        assert strategy.get_priority() == 4


class TestFallbackActivationStrategy:
    """Test cases for FallbackActivationStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create a FallbackActivationStrategy instance."""
        return FallbackActivationStrategy()
    
    @pytest.mark.asyncio
    async def test_can_handle_any_failure(self, strategy):
        """Test that strategy can handle any failure type."""
        for failure_type in FailureType:
            assert await strategy.can_handle(failure_type) == True
    
    @pytest.mark.asyncio
    async def test_execute_successful_fallback_activation(self, strategy):
        """Test successful fallback activation execution."""
        with patch.object(strategy, '_activate_http_polling', return_value=None), \
             patch.object(strategy, '_verify_fallback', return_value=True):
            
            result = await strategy.execute(FailureType.BOT_PROTECTION_TRIGGERED, 1)
            
            assert result.success == True
            assert result.strategy_used == "fallback_activation"
            assert result.recovery_time > 0
            assert result.fallback_activated == True
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_execute_failed_fallback_activation(self, strategy):
        """Test failed fallback activation execution."""
        with patch.object(strategy, '_activate_http_polling', return_value=None), \
             patch.object(strategy, '_verify_fallback', return_value=False):
            
            result = await strategy.execute(FailureType.BOT_PROTECTION_TRIGGERED, 1)
            
            assert result.success == False
            assert result.strategy_used == "fallback_activation"
            assert result.error_message == "Fallback activation failed"
    
    @pytest.mark.asyncio
    async def test_execute_with_exception(self, strategy):
        """Test execution with exception."""
        with patch.object(strategy, '_activate_http_polling', side_effect=Exception("Test error")):
            result = await strategy.execute(FailureType.BOT_PROTECTION_TRIGGERED, 1)
            
            assert result.success == False
            assert result.strategy_used == "fallback_activation"
            assert result.error_message == "Test error"
    
    def test_get_priority(self, strategy):
        """Test priority value."""
        assert strategy.get_priority() == 5


class TestRecoveryResult:
    """Test cases for RecoveryResult dataclass."""
    
    def test_recovery_result_creation(self):
        """Test RecoveryResult creation."""
        result = RecoveryResult(
            success=True,
            strategy_used="test_strategy",
            recovery_time=1.5,
            error_message=None,
            fallback_activated=False
        )
        
        assert result.success == True
        assert result.strategy_used == "test_strategy"
        assert result.recovery_time == 1.5
        assert result.error_message is None
        assert result.fallback_activated == False
    
    def test_recovery_result_with_fallback(self):
        """Test RecoveryResult with fallback activated."""
        result = RecoveryResult(
            success=True,
            strategy_used="fallback_strategy",
            recovery_time=2.0,
            fallback_activated=True
        )
        
        assert result.success == True
        assert result.fallback_activated == True