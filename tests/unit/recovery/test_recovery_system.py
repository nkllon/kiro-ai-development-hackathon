"""
Unit tests for AutomatedRecoverySystem.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from src.beast_mode.observatory.recovery.failure_classifier import FailureType, FailureData
from src.beast_mode.observatory.recovery.recovery_strategies import RecoveryResult
from src.beast_mode.observatory.recovery.recovery_system import (
    AutomatedRecoverySystem,
    SystemMetrics
)


class TestAutomatedRecoverySystem:
    """Test cases for AutomatedRecoverySystem."""
    
    @pytest.fixture
    def recovery_system(self):
        """Create an AutomatedRecoverySystem instance."""
        return AutomatedRecoverySystem()
    
    @pytest.fixture
    def sample_failure_data(self):
        """Create sample failure data."""
        return {
            "error_code": 1033,
            "error_message": "Cloudflare bot protection triggered",
            "http_status": 403,
            "symptoms": ["connection refused", "timeout"]
        }
    
    @pytest.mark.asyncio
    async def test_start_system(self, recovery_system):
        """Test starting the recovery system."""
        await recovery_system.start()
        
        assert recovery_system.is_active == True
        assert recovery_system.start_time is not None
    
    @pytest.mark.asyncio
    async def test_stop_system(self, recovery_system):
        """Test stopping the recovery system."""
        await recovery_system.start()
        await recovery_system.stop()
        
        assert recovery_system.is_active == False
        assert recovery_system.metrics.system_uptime > 0
    
    @pytest.mark.asyncio
    async def test_detect_failure(self, recovery_system):
        """Test failure detection."""
        symptoms = ["connection refused", "timeout"]
        
        with patch.object(recovery_system.failure_classifier, 'detect_failure_from_symptoms', return_value=FailureType.CONNECTION_REFUSED):
            failure_type = await recovery_system.detect_failure(symptoms)
            
            assert failure_type == FailureType.CONNECTION_REFUSED
            assert recovery_system.metrics.total_failures_detected == 1
            assert recovery_system.metrics.last_failure_time is not None
    
    @pytest.mark.asyncio
    async def test_classify_failure(self, recovery_system, sample_failure_data):
        """Test failure classification."""
        with patch.object(recovery_system.failure_classifier, 'classify_failure', return_value=FailureType.BOT_PROTECTION_TRIGGERED):
            failure_type = await recovery_system.classify_failure(sample_failure_data)
            
            assert failure_type == FailureType.BOT_PROTECTION_TRIGGERED
    
    @pytest.mark.asyncio
    async def test_execute_recovery_success(self, recovery_system):
        """Test successful recovery execution."""
        await recovery_system.start()
        
        with patch.object(recovery_system.recovery_coordinator, 'coordinate_recovery', return_value=MagicMock(
            success=True,
            total_recovery_time=30.0,
            final_strategy="websocket_reconnection",
            session_id="test_session"
        )):
            result = await recovery_system.execute_recovery(FailureType.CONNECTION_REFUSED)
            
            assert result.success == True
            assert result.strategy_used == "websocket_reconnection"
            assert result.recovery_time == 30.0
            assert recovery_system.metrics.total_recoveries_attempted == 1
            assert recovery_system.metrics.total_recoveries_successful == 1
    
    @pytest.mark.asyncio
    async def test_execute_recovery_failure(self, recovery_system):
        """Test failed recovery execution."""
        await recovery_system.start()
        
        with patch.object(recovery_system.recovery_coordinator, 'coordinate_recovery', return_value=MagicMock(
            success=False,
            total_recovery_time=60.0,
            final_strategy=None,
            session_id="test_session"
        )):
            result = await recovery_system.execute_recovery(FailureType.BOT_PROTECTION_TRIGGERED)
            
            assert result.success == False
            assert result.error_message == "Recovery failed"
            assert recovery_system.metrics.total_recoveries_attempted == 1
            assert recovery_system.metrics.total_recoveries_successful == 0
    
    @pytest.mark.asyncio
    async def test_execute_recovery_system_inactive(self, recovery_system):
        """Test recovery execution when system is inactive."""
        result = await recovery_system.execute_recovery(FailureType.CONNECTION_REFUSED)
        
        assert result.success == False
        assert result.error_message == "Recovery system is not active"
        assert result.strategy_used == "none"
    
    @pytest.mark.asyncio
    async def test_execute_recovery_with_exception(self, recovery_system):
        """Test recovery execution with exception."""
        await recovery_system.start()
        
        with patch.object(recovery_system.recovery_coordinator, 'coordinate_recovery', side_effect=Exception("Test error")):
            result = await recovery_system.execute_recovery(FailureType.CONNECTION_REFUSED)
            
            assert result.success == False
            assert result.error_message == "Test error"
    
    @pytest.mark.asyncio
    async def test_validate_recovery(self, recovery_system):
        """Test recovery validation."""
        from src.beast_mode.observatory.recovery.recovery_strategies import RecoveryAttempt
        
        attempt = RecoveryAttempt(
            strategy_name="websocket_reconnection",
            failure_type=FailureType.CONNECTION_REFUSED,
            attempt_number=1,
            start_time=datetime.utcnow(),
            success=True
        )
        
        with patch.object(recovery_system.recovery_validator, 'verify_recovery_success', return_value=True):
            result = await recovery_system.validate_recovery(attempt)
            assert result == True
    
    @pytest.mark.asyncio
    async def test_handle_failure_with_symptoms(self, recovery_system):
        """Test handling failure with symptoms only."""
        await recovery_system.start()
        
        symptoms = ["connection refused"]
        
        with patch.object(recovery_system, 'detect_failure', return_value=FailureType.CONNECTION_REFUSED), \
             patch.object(recovery_system, 'execute_recovery', return_value=RecoveryResult(
                 success=True,
                 strategy_used="websocket_reconnection",
                 recovery_time=30.0
             )):
            
            result = await recovery_system.handle_failure(symptoms)
            
            assert result.success == True
            assert result.strategy_used == "websocket_reconnection"
    
    @pytest.mark.asyncio
    async def test_handle_failure_with_data(self, recovery_system, sample_failure_data):
        """Test handling failure with detailed data."""
        await recovery_system.start()
        
        symptoms = ["connection refused"]
        
        with patch.object(recovery_system, 'classify_failure', return_value=FailureType.BOT_PROTECTION_TRIGGERED), \
             patch.object(recovery_system, 'execute_recovery', return_value=RecoveryResult(
                 success=True,
                 strategy_used="bot_protection_clear",
                 recovery_time=300.0
             )):
            
            result = await recovery_system.handle_failure(symptoms, sample_failure_data)
            
            assert result.success == True
            assert result.strategy_used == "bot_protection_clear"
    
    @pytest.mark.asyncio
    async def test_handle_failure_with_exception(self, recovery_system):
        """Test handling failure with exception."""
        await recovery_system.start()
        
        symptoms = ["connection refused"]
        
        with patch.object(recovery_system, 'detect_failure', side_effect=Exception("Test error")):
            result = await recovery_system.handle_failure(symptoms)
            
            assert result.success == False
            assert result.error_message == "Test error"
    
    def test_get_system_status(self, recovery_system):
        """Test getting system status."""
        status = recovery_system.get_system_status()
        
        assert "is_active" in status
        assert "uptime_seconds" in status
        assert "metrics" in status
        assert "available_strategies" in status
        assert "configuration" in status
        
        metrics = status["metrics"]
        assert "total_failures_detected" in metrics
        assert "total_recoveries_attempted" in metrics
        assert "total_recoveries_successful" in metrics
        assert "success_rate" in metrics
        assert "average_recovery_time" in metrics
    
    @pytest.mark.asyncio
    async def test_get_recovery_statistics(self, recovery_system):
        """Test getting recovery statistics."""
        with patch.object(recovery_system.recovery_coordinator, 'get_recovery_statistics', return_value={
            "total_recoveries": 10,
            "successful_recoveries": 8,
            "strategy_success_rates": {}
        }):
            stats = await recovery_system.get_recovery_statistics()
            
            assert "system_metrics" in stats
            assert "coordinator_statistics" in stats
            assert "available_strategies" in stats
            
            system_metrics = stats["system_metrics"]
            assert "total_failures_detected" in system_metrics
            assert "total_recoveries_attempted" in system_metrics
            assert "success_rate" in system_metrics
    
    @pytest.mark.asyncio
    async def test_get_recovery_statistics_with_exception(self, recovery_system):
        """Test getting recovery statistics with exception."""
        with patch.object(recovery_system.recovery_coordinator, 'get_recovery_statistics', side_effect=Exception("Test error")):
            stats = await recovery_system.get_recovery_statistics()
            
            assert "system_metrics" in stats
            assert "error" in stats
            assert stats["error"] == "Test error"
    
    def test_calculate_success_rate_no_attempts(self, recovery_system):
        """Test success rate calculation with no attempts."""
        rate = recovery_system._calculate_success_rate()
        assert rate == 0.0
    
    def test_calculate_success_rate_with_attempts(self, recovery_system):
        """Test success rate calculation with attempts."""
        recovery_system.metrics.total_recoveries_attempted = 10
        recovery_system.metrics.total_recoveries_successful = 8
        
        rate = recovery_system._calculate_success_rate()
        assert rate == 0.8


class TestSystemMetrics:
    """Test cases for SystemMetrics."""
    
    def test_system_metrics_creation(self):
        """Test SystemMetrics creation."""
        metrics = SystemMetrics()
        
        assert metrics.total_failures_detected == 0
        assert metrics.total_recoveries_attempted == 0
        assert metrics.total_recoveries_successful == 0
        assert metrics.average_recovery_time == 0.0
        assert metrics.last_failure_time is None
        assert metrics.last_recovery_time is None
        assert metrics.system_uptime == 0.0
    
    def test_system_metrics_with_values(self):
        """Test SystemMetrics with values."""
        now = datetime.utcnow()
        
        metrics = SystemMetrics(
            total_failures_detected=5,
            total_recoveries_attempted=4,
            total_recoveries_successful=3,
            average_recovery_time=45.0,
            last_failure_time=now,
            last_recovery_time=now,
            system_uptime=3600.0
        )
        
        assert metrics.total_failures_detected == 5
        assert metrics.total_recoveries_attempted == 4
        assert metrics.total_recoveries_successful == 3
        assert metrics.average_recovery_time == 45.0
        assert metrics.last_failure_time == now
        assert metrics.last_recovery_time == now
        assert metrics.system_uptime == 3600.0