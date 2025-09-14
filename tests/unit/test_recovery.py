"""
Unit tests for the recovery system.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.beast_mode.monitoring.recovery import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    RecoveryManager, RecoveryAction, RecoveryActionType, RecoveryResult, RecoveryAttempt
)


class TestRecoveryManager(ReflectiveModule):
    """Test cases for RecoveryManager."""
    
    @pytest.fixture
    def recovery_manager(self):
        """Create a recovery manager instance for testing."""
        return RecoveryManager("redis://localhost:6379")
        
    @pytest.mark.asyncio
    async def test_register_recovery_action(self, recovery_manager):
        """Test registering a recovery action."""
        action_function = AsyncMock(return_value={"result": RecoveryResult.SUCCESS})
        
        await recovery_manager.register_recovery_action(
            name="test_action",
            action_type=RecoveryActionType.RESTART_SERVICE,
            description="Test recovery action",
            action_function=action_function,
            max_attempts=3,
            retry_delay_seconds=10
        )
        
        assert "test_action" in recovery_manager.recovery_actions
        action = recovery_manager.recovery_actions["test_action"]
        assert action.name == "test_action"
        assert action.action_type == RecoveryActionType.RESTART_SERVICE
        assert action.max_attempts == 3
        assert action.retry_delay_seconds == 10
        
    def test_add_recovery_callback(self, recovery_manager):
        """Test adding recovery callbacks."""
        callback = MagicMock()
        
        recovery_manager.add_recovery_callback(callback)
        assert callback in recovery_manager.recovery_callbacks
        
    @pytest.mark.asyncio
    async def test_start_stop_recovery_system(self, recovery_manager):
        """Test starting and stopping recovery system."""
        assert not recovery_manager.recovery_active
        
        await recovery_manager.start_recovery_system()
        assert recovery_manager.recovery_active
        assert recovery_manager.recovery_task is not None
        
        await recovery_manager.stop_recovery_system()
        assert not recovery_manager.recovery_active
        
    @pytest.mark.asyncio
    async def test_trigger_recovery_success(self, recovery_manager):
        """Test successful recovery action trigger."""
        action_function = AsyncMock(return_value={
            "result": RecoveryResult.SUCCESS,
            "message": "Recovery completed successfully"
        })
        
        await recovery_manager.register_recovery_action(
            name="test_action",
            action_type=RecoveryActionType.RECONNECT,
            description="Test action",
            action_function=action_function,
            timeout_seconds=5
        )
        
        result = await recovery_manager.trigger_recovery("test_action")
        
        assert result == RecoveryResult.SUCCESS
        action_function.assert_called_once()
        
        # Check recovery history
        assert len(recovery_manager.recovery_attempts) == 1
        attempt = recovery_manager.recovery_attempts[0]
        assert attempt.action_name == "test_action"
        assert attempt.result == RecoveryResult.SUCCESS
        assert attempt.completed_at is not None
        
    @pytest.mark.asyncio
    async def test_trigger_recovery_failure_with_retry(self, recovery_manager):
        """Test recovery action failure with retry."""
        action_function = AsyncMock(return_value={
            "result": RecoveryResult.FAILED,
            "message": "Recovery failed"
        })
        
        await recovery_manager.register_recovery_action(
            name="failing_action",
            action_type=RecoveryActionType.RESTART_SERVICE,
            description="Failing action",
            action_function=action_function,
            max_attempts=3,
            retry_delay_seconds=0.1,  # Short delay for testing
            timeout_seconds=5
        )
        
        result = await recovery_manager.trigger_recovery("failing_action")
        
        assert result == RecoveryResult.FAILED
        assert action_function.call_count == 3  # Should retry 3 times
        
        # Check recovery history - should have 3 attempts
        assert len(recovery_manager.recovery_attempts) == 3
        for attempt in recovery_manager.recovery_attempts:
            assert attempt.action_name == "failing_action"
            assert attempt.result == RecoveryResult.FAILED
            
    @pytest.mark.asyncio
    async def test_trigger_recovery_timeout(self, recovery_manager):
        """Test recovery action timeout."""
        async def slow_action(context):
            await asyncio.sleep(10)  # Longer than timeout
            return {"result": RecoveryResult.SUCCESS}
            
        await recovery_manager.register_recovery_action(
            name="slow_action",
            action_type=RecoveryActionType.CUSTOM,
            description="Slow action",
            action_function=slow_action,
            timeout_seconds=1,  # Short timeout
            max_attempts=1
        )
        
        result = await recovery_manager.trigger_recovery("slow_action")
        
        assert result == RecoveryResult.FAILED
        
        # Check that attempt was recorded with timeout error
        assert len(recovery_manager.recovery_attempts) == 1
        attempt = recovery_manager.recovery_attempts[0]
        assert attempt.result == RecoveryResult.FAILED
        assert "timeout" in attempt.message.lower()
        
    @pytest.mark.asyncio
    async def test_trigger_recovery_exception(self, recovery_manager):
        """Test recovery action exception handling."""
        async def failing_action(context):
            raise ValueError("Test exception")
            
        await recovery_manager.register_recovery_action(
            name="exception_action",
            action_type=RecoveryActionType.CUSTOM,
            description="Exception action",
            action_function=failing_action,
            max_attempts=1
        )
        
        result = await recovery_manager.trigger_recovery("exception_action")
        
        assert result == RecoveryResult.FAILED
        
        # Check that exception was recorded
        assert len(recovery_manager.recovery_attempts) == 1
        attempt = recovery_manager.recovery_attempts[0]
        assert attempt.result == RecoveryResult.FAILED
        assert "Test exception" in attempt.message
        assert attempt.error == "Test exception"
        
    @pytest.mark.asyncio
    async def test_trigger_recovery_nonexistent_action(self, recovery_manager):
        """Test triggering non-existent recovery action."""
        result = await recovery_manager.trigger_recovery("nonexistent_action")
        assert result == RecoveryResult.FAILED
        
    @pytest.mark.asyncio
    async def test_trigger_recovery_already_running(self, recovery_manager):
        """Test triggering recovery action that's already running."""
        # Create a slow action
        async def slow_action(context):
            await asyncio.sleep(1)
            return {"result": RecoveryResult.SUCCESS}
            
        await recovery_manager.register_recovery_action(
            name="slow_action",
            action_type=RecoveryActionType.CUSTOM,
            description="Slow action",
            action_function=slow_action
        )
        
        # Start first recovery
        task1 = asyncio.create_task(recovery_manager.trigger_recovery("slow_action"))
        
        # Try to start second recovery while first is running
        await asyncio.sleep(0.1)  # Let first one start
        result2 = await recovery_manager.trigger_recovery("slow_action")
        
        # Second should return IN_PROGRESS
        assert result2 == RecoveryResult.IN_PROGRESS
        
        # Wait for first to complete
        result1 = await task1
        assert result1 == RecoveryResult.SUCCESS
        
    @pytest.mark.asyncio
    async def test_report_failure(self, recovery_manager):
        """Test reporting component failures."""
        await recovery_manager.report_failure(
            component="redis",
            failure_type="connection_failed",
            details={"error": "Connection refused"}
        )
        
        # Check failure tracking
        failure_key = "redis_connection_failed"
        assert recovery_manager.failure_counts[failure_key] == 1
        assert failure_key in recovery_manager.last_failure_time
        
        # Report more failures
        for _ in range(3):
            await recovery_manager.report_failure("redis", "connection_failed")
            
        assert recovery_manager.failure_counts[failure_key] == 4
        
    def test_get_recovery_history(self, recovery_manager):
        """Test getting recovery history."""
        # Add recovery attempts with different timestamps
        old_attempt = RecoveryAttempt(
            action_name="old_action",
            attempt_number=1,
            started_at=datetime.now() - timedelta(hours=25),  # Older than 24h
            result=RecoveryResult.SUCCESS
        )
        recent_attempt = RecoveryAttempt(
            action_name="recent_action",
            attempt_number=1,
            started_at=datetime.now() - timedelta(hours=1),  # Within 24h
            result=RecoveryResult.FAILED
        )
        
        recovery_manager.recovery_attempts.extend([old_attempt, recent_attempt])
        
        # Get 24-hour history
        history = recovery_manager.get_recovery_history(24)
        assert len(history) == 1
        assert history[0].action_name == "recent_action"
        
        # Get 48-hour history
        history = recovery_manager.get_recovery_history(48)
        assert len(history) == 2
        
    def test_get_active_recoveries(self, recovery_manager):
        """Test getting active recoveries."""
        # Initially empty
        active = recovery_manager.get_active_recoveries()
        assert len(active) == 0
        
        # Add active recovery
        attempt = RecoveryAttempt(
            action_name="active_action",
            attempt_number=1,
            started_at=datetime.now()
        )
        recovery_manager.active_recoveries["active_action"] = attempt
        
        active = recovery_manager.get_active_recoveries()
        assert len(active) == 1
        assert active[0].action_name == "active_action"
        
    def test_get_recovery_summary(self, recovery_manager):
        """Test getting recovery summary."""
        # Add some recovery actions
        recovery_manager.recovery_actions["action1"] = RecoveryAction(
            name="action1", action_type=RecoveryActionType.RECONNECT,
            description="Test", action_function=lambda: None
        )
        
        # Add active recovery
        recovery_manager.active_recoveries["active"] = RecoveryAttempt(
            action_name="active", attempt_number=1, started_at=datetime.now()
        )
        
        # Add recovery history
        recovery_manager.recovery_attempts.extend([
            RecoveryAttempt(
                action_name="success", attempt_number=1,
                started_at=datetime.now() - timedelta(hours=1),
                result=RecoveryResult.SUCCESS
            ),
            RecoveryAttempt(
                action_name="failed", attempt_number=1,
                started_at=datetime.now() - timedelta(hours=2),
                result=RecoveryResult.FAILED
            )
        ])
        
        summary = recovery_manager.get_recovery_summary()
        
        assert summary["registered_actions"] == 1
        assert summary["active_recoveries"] == 1
        assert summary["recent_attempts_24h"] == 2
        assert summary["success_rate_24h"] == 50.0  # 1 success out of 2
        assert summary["failed_attempts_24h"] == 1
        assert "last_updated" in summary
        
    @pytest.mark.asyncio
    async def test_check_stuck_recoveries(self, recovery_manager):
        """Test checking for stuck recoveries."""
        # Add a recovery action with short timeout
        await recovery_manager.register_recovery_action(
            name="test_action",
            action_type=RecoveryActionType.CUSTOM,
            description="Test",
            action_function=lambda x: None,
            timeout_seconds=1
        )
        
        # Add a stuck recovery (started long ago)
        stuck_attempt = RecoveryAttempt(
            action_name="test_action",
            attempt_number=1,
            started_at=datetime.now() - timedelta(seconds=10)  # Much longer than timeout
        )
        recovery_manager.active_recoveries["test_action"] = stuck_attempt
        
        await recovery_manager._check_stuck_recoveries()
        
        # Should have been removed from active and marked as failed
        assert "test_action" not in recovery_manager.active_recoveries
        assert len(recovery_manager.recovery_attempts) == 1
        
        failed_attempt = recovery_manager.recovery_attempts[0]
        assert failed_attempt.result == RecoveryResult.FAILED
        assert "stuck" in failed_attempt.message.lower()
        
    @pytest.mark.asyncio
    async def test_notify_recovery_callbacks(self, recovery_manager):
        """Test recovery callback notification."""
        # Add sync and async callbacks
        sync_callback = MagicMock()
        async_callback = AsyncMock()
        
        recovery_manager.add_recovery_callback(sync_callback)
        recovery_manager.add_recovery_callback(async_callback)
        
        attempt = RecoveryAttempt(
            action_name="test",
            attempt_number=1,
            started_at=datetime.now(),
            result=RecoveryResult.SUCCESS
        )
        
        await recovery_manager._notify_recovery_callbacks(attempt)
        
        # Both callbacks should have been called
        sync_callback.assert_called_once_with(attempt)
        async_callback.assert_called_once_with(attempt)
        
    @pytest.mark.asyncio
    @patch('redis.asyncio.from_url')
    async def test_redis_reconnect_action(self, mock_redis, recovery_manager):
        """Test Redis reconnect recovery action."""
        # Mock successful Redis connection
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock()
        mock_client.close = AsyncMock()
        mock_redis.return_value = mock_client
        
        result = await recovery_manager._redis_reconnect_action({})
        
        assert result["result"] == RecoveryResult.SUCCESS
        assert "successful" in result["message"].lower()
        mock_client.ping.assert_called_once()
        mock_client.close.assert_called_once()
        
        # Test failure
        mock_client.ping.side_effect = Exception("Connection failed")
        
        result = await recovery_manager._redis_reconnect_action({})
        
        assert result["result"] == RecoveryResult.FAILED
        assert "Connection failed" in result["message"]
        
    @pytest.mark.asyncio
    @patch('redis.asyncio.from_url')
    async def test_redis_clear_cache_action(self, mock_redis, recovery_manager):
        """Test Redis cache clear recovery action."""
        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.keys = AsyncMock(return_value=["key1", "key2"])
        mock_client.delete = AsyncMock()
        mock_client.close = AsyncMock()
        mock_redis.return_value = mock_client
        
        result = await recovery_manager._redis_clear_cache_action({})
        
        assert result["result"] == RecoveryResult.SUCCESS
        assert "cleared" in result["message"].lower()
        mock_client.keys.assert_called()
        mock_client.delete.assert_called_with("key1", "key2")
        
    @pytest.mark.asyncio
    async def test_reset_counters_action(self, recovery_manager):
        """Test reset counters recovery action."""
        # Add some failure counts
        recovery_manager.failure_counts["test"] = 5
        recovery_manager.last_failure_time["test"] = datetime.now()
        
        result = await recovery_manager._reset_counters_action({})
        
        assert result["result"] == RecoveryResult.SUCCESS
        assert "reset" in result["message"].lower()
        assert len(recovery_manager.failure_counts) == 0
        assert len(recovery_manager.last_failure_time) == 0
        
    @pytest.mark.asyncio
    async def test_enable_degraded_mode_action(self, recovery_manager):
        """Test enable degraded mode recovery action."""
        result = await recovery_manager._enable_degraded_mode_action({})
        
        assert result["result"] == RecoveryResult.SUCCESS
        assert "degraded mode" in result["message"].lower()

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert result["details"]["mode"] == "degraded"