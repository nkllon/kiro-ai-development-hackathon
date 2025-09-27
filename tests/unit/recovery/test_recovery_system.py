"""
Unit tests for AutomatedRecoverySystem
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

from src.beast_mode.observatory.recovery.recovery_system import AutomatedRecoverySystem, RecoveryMetrics
from src.beast_mode.observatory.recovery.failure_classifier import FailureType, FailureContext
from src.beast_mode.observatory.recovery.recovery_strategies import RecoveryResult, RecoveryStrategyType


class TestAutomatedRecoverySystem:
    """Test cases for AutomatedRecoverySystem"""
    
    @pytest.fixture
    def recovery_system(self):
        """Create recovery system instance for testing"""
        return AutomatedRecoverySystem(
            auto_recovery_enabled=True,
            max_consecutive_failures=3,
            recovery_cooldown=10.0
        )
    
    @pytest.fixture
    def disabled_recovery_system(self):
        """Create disabled recovery system for testing"""
        return AutomatedRecoverySystem(auto_recovery_enabled=False)
    
    @pytest.mark.asyncio
    async def test_detect_failure(self, recovery_system):
        """Test failure detection from symptoms"""
        symptoms = ["connection refused", "timeout error"]
        
        failure_type = await recovery_system.detect_failure(symptoms)
        
        assert failure_type in [FailureType.CONNECTION_REFUSED, FailureType.TIMEOUT]
    
    @pytest.mark.asyncio
    async def test_classify_failure(self, recovery_system):
        """Test failure classification from detailed data"""
        failure_data = {
            "error_message": "Connection refused",
            "error_code": 1033,
            "http_status": 403,
            "retry_count": 2
        }
        
        failure_type = await recovery_system.classify_failure(failure_data)
        
        assert failure_type == FailureType.BOT_PROTECTION_TRIGGERED
    
    @pytest.mark.asyncio
    async def test_execute_recovery_success(self, recovery_system):
        """Test successful recovery execution"""
        with patch.object(recovery_system.strategy_manager, 'execute_recovery') as mock_recovery:
            mock_recovery.return_value = RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategyType.WEBSOCKET_RECONNECTION,
                attempts_made=1,
                total_duration=2.0
            )
            
            result = await recovery_system.execute_recovery(FailureType.CONNECTION_REFUSED)
            
            assert result.success is True
            assert result.strategy_used == RecoveryStrategyType.WEBSOCKET_RECONNECTION
            assert recovery_system.metrics.successful_recoveries == 1
            assert recovery_system.metrics.consecutive_failures == 0
    
    @pytest.mark.asyncio
    async def test_execute_recovery_failure(self, recovery_system):
        """Test failed recovery execution"""
        with patch.object(recovery_system.strategy_manager, 'execute_recovery') as mock_recovery:
            mock_recovery.return_value = RecoveryResult(
                success=False,
                strategy_used=None,
                attempts_made=3,
                total_duration=10.0,
                error_message="All strategies failed"
            )
            
            result = await recovery_system.execute_recovery(FailureType.UNKNOWN)
            
            assert result.success is False
            assert recovery_system.metrics.failed_recoveries == 1
            assert recovery_system.metrics.consecutive_failures == 1
    
    @pytest.mark.asyncio
    async def test_execute_recovery_disabled(self, disabled_recovery_system):
        """Test recovery execution when disabled"""
        result = await disabled_recovery_system.execute_recovery(FailureType.CONNECTION_REFUSED)
        
        assert result.success is False
        assert "disabled" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_execute_recovery_cooldown(self, recovery_system):
        """Test recovery cooldown mechanism"""
        # Set last recovery attempt to recent time
        recovery_system.last_recovery_attempt = datetime.utcnow() - timedelta(seconds=5)
        
        result = await recovery_system.execute_recovery(FailureType.CONNECTION_REFUSED)
        
        assert result.success is False
        assert "cooldown" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_validate_recovery(self, recovery_system):
        """Test recovery validation"""
        mock_attempt = Mock()
        mock_attempt.strategy_type = RecoveryStrategyType.WEBSOCKET_RECONNECTION
        mock_attempt.failure_type = FailureType.CONNECTION_REFUSED
        mock_attempt.attempt_number = 1
        mock_attempt.start_time = datetime.utcnow()
        mock_attempt.end_time = datetime.utcnow()
        mock_attempt.success = True
        
        with patch.object(recovery_system.recovery_validator, 'validate_recovery') as mock_validate:
            mock_validate.return_value = Mock(overall_success=True)
            
            result = await recovery_system.validate_recovery(mock_attempt)
            
            assert result is True
            mock_validate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_full_recovery_cycle(self, recovery_system):
        """Test full recovery cycle"""
        symptoms = ["connection refused"]
        context = {"retry_count": 1}
        
        with patch.object(recovery_system.coordinator, 'initiate_recovery') as mock_coordinator:
            mock_session = Mock()
            mock_session.session_id = "test_session"
            mock_session.success = True
            mock_session.failure_type = FailureType.CONNECTION_REFUSED
            mock_session.start_time = datetime.utcnow()
            mock_session.end_time = datetime.utcnow()
            mock_coordinator.return_value = mock_session
            
            session = await recovery_system.full_recovery_cycle(symptoms, context)
            
            assert session.success is True
            assert recovery_system.metrics.successful_recoveries == 1
    
    def test_add_recovery_callback(self, recovery_system):
        """Test adding recovery callbacks"""
        callback = Mock()
        
        recovery_system.add_recovery_callback(callback)
        
        assert len(recovery_system.recovery_callbacks) == 1
        assert callback in recovery_system.recovery_callbacks
    
    @pytest.mark.asyncio
    async def test_trigger_recovery_callbacks(self, recovery_system):
        """Test triggering recovery callbacks"""
        callback = Mock()
        recovery_system.add_recovery_callback(callback)
        
        result = RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategyType.WEBSOCKET_RECONNECTION,
            attempts_made=1,
            total_duration=2.0
        )
        
        await recovery_system._trigger_recovery_callbacks(result)
        
        callback.assert_called_once_with(result)
    
    def test_get_system_status(self, recovery_system):
        """Test getting system status"""
        # Set some metrics
        recovery_system.metrics.total_recoveries = 10
        recovery_system.metrics.successful_recoveries = 8
        recovery_system.metrics.failed_recoveries = 2
        
        with patch.object(recovery_system.coordinator, 'get_recovery_statistics') as mock_stats:
            mock_stats.return_value = {"total_sessions": 10, "success_rate": 0.8}
            
            status = recovery_system.get_system_status()
            
            assert status["system_enabled"] is True
            assert status["metrics"]["total_recoveries"] == 10
            assert status["metrics"]["success_rate"] == 0.8
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, recovery_system):
        """Test health check when system is healthy"""
        with patch.object(recovery_system.coordinator, 'health_check') as mock_health:
            mock_health.return_value = {"overall_health": "healthy"}
            
            health = await recovery_system.health_check()
            
            assert health["overall_health"] == "healthy"
            assert health["escalation_needed"] is False
    
    @pytest.mark.asyncio
    async def test_health_check_escalation_needed(self, recovery_system):
        """Test health check when escalation is needed"""
        recovery_system.metrics.consecutive_failures = 5  # Exceeds max of 3
        
        with patch.object(recovery_system.coordinator, 'health_check') as mock_health:
            mock_health.return_value = {"overall_health": "healthy"}
            
            health = await recovery_system.health_check()
            
            assert health["overall_health"] == "critical"
            assert health["escalation_needed"] is True
    
    def test_enable_auto_recovery(self, recovery_system):
        """Test enabling auto recovery"""
        recovery_system.auto_recovery_enabled = False
        
        recovery_system.enable_auto_recovery()
        
        assert recovery_system.auto_recovery_enabled is True
    
    def test_disable_auto_recovery(self, recovery_system):
        """Test disabling auto recovery"""
        recovery_system.disable_auto_recovery()
        
        assert recovery_system.auto_recovery_enabled is False
    
    def test_reset_metrics(self, recovery_system):
        """Test resetting metrics"""
        recovery_system.metrics.total_recoveries = 10
        recovery_system.metrics.successful_recoveries = 8
        
        recovery_system.reset_metrics()
        
        assert recovery_system.metrics.total_recoveries == 0
        assert recovery_system.metrics.successful_recoveries == 0


class TestRecoveryMetrics:
    """Test cases for RecoveryMetrics"""
    
    def test_recovery_metrics_initialization(self):
        """Test recovery metrics initialization"""
        metrics = RecoveryMetrics()
        
        assert metrics.total_recoveries == 0
        assert metrics.successful_recoveries == 0
        assert metrics.failed_recoveries == 0
        assert metrics.average_recovery_time == 0.0
        assert metrics.last_recovery_time is None
        assert metrics.consecutive_failures == 0
        assert metrics.recovery_rate_24h == 0.0