"""
Unit tests for Recovery Strategies
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from src.beast_mode.observatory.recovery.recovery_strategies import (
    WebSocketReconnectionStrategy,
    TunnelRestartStrategy,
    ConfigurationReloadStrategy,
    BotProtectionClearStrategy,
    FallbackActivationStrategy,
    RecoveryStrategyManager,
    RecoveryStrategyType,
    RecoveryAttempt,
    RecoveryResult
)
from src.beast_mode.observatory.recovery.failure_classifier import FailureType


class TestWebSocketReconnectionStrategy:
    """Test cases for WebSocketReconnectionStrategy"""
    
    @pytest.fixture
    def strategy(self):
        """Create WebSocket reconnection strategy instance"""
        return WebSocketReconnectionStrategy()
    
    def test_can_handle_connection_refused(self, strategy):
        """Test handling connection refused failures"""
        assert strategy.can_handle(FailureType.CONNECTION_REFUSED) is True
    
    def test_can_handle_timeout(self, strategy):
        """Test handling timeout failures"""
        assert strategy.can_handle(FailureType.TIMEOUT) is True
    
    def test_can_handle_network_error(self, strategy):
        """Test handling network errors"""
        assert strategy.can_handle(FailureType.NETWORK_ERROR) is True
    
    def test_can_handle_upgrade_failed(self, strategy):
        """Test handling upgrade failures"""
        assert strategy.can_handle(FailureType.UPGRADE_FAILED) is True
    
    def test_cannot_handle_bot_protection(self, strategy):
        """Test not handling bot protection failures"""
        assert strategy.can_handle(FailureType.BOT_PROTECTION_TRIGGERED) is False
    
    @pytest.mark.asyncio
    async def test_execute_success(self, strategy):
        """Test successful execution"""
        with patch('asyncio.sleep') as mock_sleep:
            result = await strategy.execute(FailureType.CONNECTION_REFUSED, {})
            
            assert isinstance(result, RecoveryAttempt)
            assert result.strategy_type == RecoveryStrategyType.WEBSOCKET_RECONNECTION
            assert result.failure_type == FailureType.CONNECTION_REFUSED
            assert result.attempt_number == 1
            assert result.start_time is not None
            assert result.end_time is not None
            assert result.success is True  # Should succeed on first attempt in mock
    
    @pytest.mark.asyncio
    async def test_execute_multiple_attempts(self, strategy):
        """Test multiple execution attempts"""
        # First attempt
        result1 = await strategy.execute(FailureType.CONNECTION_REFUSED, {})
        assert result1.attempt_number == 1
        
        # Second attempt
        result2 = await strategy.execute(FailureType.CONNECTION_REFUSED, {})
        assert result2.attempt_number == 2
    
    def test_get_backoff_delay(self, strategy):
        """Test exponential backoff delay calculation"""
        assert strategy.get_backoff_delay(0) == 2.0  # base_delay
        assert strategy.get_backoff_delay(1) == 4.0  # base_delay * 2^1
        assert strategy.get_backoff_delay(2) == 8.0  # base_delay * 2^2
        assert strategy.get_backoff_delay(3) == 16.0  # base_delay * 2^3


class TestTunnelRestartStrategy:
    """Test cases for TunnelRestartStrategy"""
    
    @pytest.fixture
    def strategy(self):
        """Create tunnel restart strategy instance"""
        return TunnelRestartStrategy()
    
    def test_can_handle_connection_refused(self, strategy):
        """Test handling connection refused failures"""
        assert strategy.can_handle(FailureType.CONNECTION_REFUSED) is True
    
    def test_can_handle_configuration_error(self, strategy):
        """Test handling configuration errors"""
        assert strategy.can_handle(FailureType.CONFIGURATION_ERROR) is True
    
    def test_can_handle_timeout(self, strategy):
        """Test handling timeout failures"""
        assert strategy.can_handle(FailureType.TIMEOUT) is True
    
    def test_cannot_handle_bot_protection(self, strategy):
        """Test not handling bot protection failures"""
        assert strategy.can_handle(FailureType.BOT_PROTECTION_TRIGGERED) is False
    
    @pytest.mark.asyncio
    async def test_execute_success(self, strategy):
        """Test successful execution"""
        with patch('asyncio.sleep') as mock_sleep:
            result = await strategy.execute(FailureType.CONNECTION_REFUSED, {})
            
            assert isinstance(result, RecoveryAttempt)
            assert result.strategy_type == RecoveryStrategyType.TUNNEL_RESTART
            assert result.success is True
            assert result.recovery_data is not None
            assert "tunnel_pid" in result.recovery_data
            assert "restart_duration" in result.recovery_data


class TestConfigurationReloadStrategy:
    """Test cases for ConfigurationReloadStrategy"""
    
    @pytest.fixture
    def strategy(self):
        """Create configuration reload strategy instance"""
        return ConfigurationReloadStrategy()
    
    def test_can_handle_configuration_error(self, strategy):
        """Test handling configuration errors"""
        assert strategy.can_handle(FailureType.CONFIGURATION_ERROR) is True
    
    def test_can_handle_authentication_failed(self, strategy):
        """Test handling authentication failures"""
        assert strategy.can_handle(FailureType.AUTHENTICATION_FAILED) is True
    
    def test_cannot_handle_network_error(self, strategy):
        """Test not handling network errors"""
        assert strategy.can_handle(FailureType.NETWORK_ERROR) is False
    
    @pytest.mark.asyncio
    async def test_execute_success(self, strategy):
        """Test successful execution"""
        with patch('asyncio.sleep') as mock_sleep:
            result = await strategy.execute(FailureType.CONFIGURATION_ERROR, {})
            
            assert isinstance(result, RecoveryAttempt)
            assert result.strategy_type == RecoveryStrategyType.CONFIGURATION_RELOAD
            assert result.success is True
            assert result.recovery_data is not None
            assert "config_file" in result.recovery_data
            assert "validation_passed" in result.recovery_data


class TestBotProtectionClearStrategy:
    """Test cases for BotProtectionClearStrategy"""
    
    @pytest.fixture
    def strategy(self):
        """Create bot protection clear strategy instance"""
        return BotProtectionClearStrategy()
    
    def test_can_handle_bot_protection(self, strategy):
        """Test handling bot protection failures"""
        assert strategy.can_handle(FailureType.BOT_PROTECTION_TRIGGERED) is True
    
    def test_cannot_handle_other_failures(self, strategy):
        """Test not handling other failure types"""
        assert strategy.can_handle(FailureType.CONNECTION_REFUSED) is False
        assert strategy.can_handle(FailureType.TIMEOUT) is False
    
    @pytest.mark.asyncio
    async def test_execute_success(self, strategy):
        """Test successful execution"""
        with patch('asyncio.sleep') as mock_sleep:
            result = await strategy.execute(FailureType.BOT_PROTECTION_TRIGGERED, {})
            
            assert isinstance(result, RecoveryAttempt)
            assert result.strategy_type == RecoveryStrategyType.BOT_PROTECTION_CLEAR
            assert result.success is True
            assert result.recovery_data is not None
            assert "wait_duration" in result.recovery_data
            assert "protection_expired" in result.recovery_data


class TestFallbackActivationStrategy:
    """Test cases for FallbackActivationStrategy"""
    
    @pytest.fixture
    def strategy(self):
        """Create fallback activation strategy instance"""
        return FallbackActivationStrategy()
    
    def test_can_handle_any_failure(self, strategy):
        """Test handling any failure type"""
        for failure_type in FailureType:
            assert strategy.can_handle(failure_type) is True
    
    @pytest.mark.asyncio
    async def test_execute_success(self, strategy):
        """Test successful execution"""
        with patch('asyncio.sleep') as mock_sleep:
            result = await strategy.execute(FailureType.UNKNOWN, {})
            
            assert isinstance(result, RecoveryAttempt)
            assert result.strategy_type == RecoveryStrategyType.FALLBACK_ACTIVATION
            assert result.success is True
            assert result.recovery_data is not None
            assert "fallback_mode" in result.recovery_data
            assert result.recovery_data["fallback_mode"] == "http_polling"


class TestRecoveryStrategyManager:
    """Test cases for RecoveryStrategyManager"""
    
    @pytest.fixture
    def manager(self):
        """Create recovery strategy manager instance"""
        return RecoveryStrategyManager()
    
    def test_strategies_initialization(self, manager):
        """Test that all strategies are initialized"""
        assert len(manager.strategies) == 5
        
        strategy_types = {strategy.strategy_type for strategy in manager.strategies}
        expected_types = {
            RecoveryStrategyType.WEBSOCKET_RECONNECTION,
            RecoveryStrategyType.TUNNEL_RESTART,
            RecoveryStrategyType.CONFIGURATION_RELOAD,
            RecoveryStrategyType.BOT_PROTECTION_CLEAR,
            RecoveryStrategyType.FALLBACK_ACTIVATION
        }
        assert strategy_types == expected_types
    
    def test_get_applicable_strategies_connection_refused(self, manager):
        """Test getting applicable strategies for connection refused"""
        strategies = manager.get_applicable_strategies(FailureType.CONNECTION_REFUSED)
        
        strategy_types = {strategy.strategy_type for strategy in strategies}
        expected_types = {
            RecoveryStrategyType.WEBSOCKET_RECONNECTION,
            RecoveryStrategyType.TUNNEL_RESTART
        }
        assert strategy_types == expected_types
    
    def test_get_applicable_strategies_bot_protection(self, manager):
        """Test getting applicable strategies for bot protection"""
        strategies = manager.get_applicable_strategies(FailureType.BOT_PROTECTION_TRIGGERED)
        
        strategy_types = {strategy.strategy_type for strategy in strategies}
        expected_types = {
            RecoveryStrategyType.BOT_PROTECTION_CLEAR,
            RecoveryStrategyType.FALLBACK_ACTIVATION
        }
        assert strategy_types == expected_types
    
    def test_get_applicable_strategies_unknown(self, manager):
        """Test getting applicable strategies for unknown failure"""
        strategies = manager.get_applicable_strategies(FailureType.UNKNOWN)
        
        # Only fallback activation should handle unknown failures
        assert len(strategies) == 1
        assert strategies[0].strategy_type == RecoveryStrategyType.FALLBACK_ACTIVATION
    
    @pytest.mark.asyncio
    async def test_execute_recovery_success(self, manager):
        """Test successful recovery execution"""
        with patch.object(manager.strategies[0], 'execute') as mock_execute:
            mock_execute.return_value = RecoveryAttempt(
                strategy_type=RecoveryStrategyType.WEBSOCKET_RECONNECTION,
                failure_type=FailureType.CONNECTION_REFUSED,
                attempt_number=1,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                success=True
            )
            
            result = await manager.execute_recovery(FailureType.CONNECTION_REFUSED, {})
            
            assert isinstance(result, RecoveryResult)
            assert result.success is True
            assert result.strategy_used == RecoveryStrategyType.WEBSOCKET_RECONNECTION
            assert result.attempts_made == 1
    
    @pytest.mark.asyncio
    async def test_execute_recovery_all_strategies_fail(self, manager):
        """Test recovery when all strategies fail"""
        # Mock all strategies to fail
        for strategy in manager.strategies:
            with patch.object(strategy, 'execute') as mock_execute:
                mock_execute.return_value = RecoveryAttempt(
                    strategy_type=strategy.strategy_type,
                    failure_type=FailureType.CONNECTION_REFUSED,
                    attempt_number=1,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow(),
                    success=False,
                    error_message="Strategy failed"
                )
        
        result = await manager.execute_recovery(FailureType.CONNECTION_REFUSED, {})
        
        assert isinstance(result, RecoveryResult)
        assert result.success is False
        assert result.error_message == "All recovery strategies failed"
        assert result.attempts_made == len(manager.strategies)


class TestRecoveryAttempt:
    """Test cases for RecoveryAttempt dataclass"""
    
    def test_recovery_attempt_creation(self):
        """Test creating recovery attempt"""
        attempt = RecoveryAttempt(
            strategy_type=RecoveryStrategyType.WEBSOCKET_RECONNECTION,
            failure_type=FailureType.CONNECTION_REFUSED,
            attempt_number=1,
            start_time=datetime.utcnow()
        )
        
        assert attempt.strategy_type == RecoveryStrategyType.WEBSOCKET_RECONNECTION
        assert attempt.failure_type == FailureType.CONNECTION_REFUSED
        assert attempt.attempt_number == 1
        assert attempt.start_time is not None
        assert attempt.end_time is None
        assert attempt.success is False
        assert attempt.error_message is None
        assert attempt.recovery_data is None


class TestRecoveryResult:
    """Test cases for RecoveryResult dataclass"""
    
    def test_recovery_result_creation(self):
        """Test creating recovery result"""
        result = RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategyType.WEBSOCKET_RECONNECTION,
            attempts_made=1,
            total_duration=2.5
        )
        
        assert result.success is True
        assert result.strategy_used == RecoveryStrategyType.WEBSOCKET_RECONNECTION
        assert result.attempts_made == 1
        assert result.total_duration == 2.5
        assert result.error_message is None
        assert result.recovery_data is None
    
    def test_recovery_result_with_error(self):
        """Test creating recovery result with error"""
        result = RecoveryResult(
            success=False,
            strategy_used=None,
            attempts_made=3,
            total_duration=10.0,
            error_message="All strategies failed"
        )
        
        assert result.success is False
        assert result.strategy_used is None
        assert result.attempts_made == 3
        assert result.total_duration == 10.0
        assert result.error_message == "All strategies failed"