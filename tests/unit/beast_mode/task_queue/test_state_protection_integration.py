"""
Unit tests for state protection integration with TaskQueueManager
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.beast_mode.task_queue.task_queue_manager import TaskQueueManager
from src.beast_mode.task_queue.state_protection import (
    StatePersistenceStrategy,
    EnhancedStateIntegrityMonitor,
    ConversationStateLockManager,
    PersistenceLayer,
    IntegrityStatus,
)
from src.beast_mode.task_queue.models import (
    TaskQueueConfig,
    QueueConfig,
    PersistenceConfig,
    CoordinationConfig,
    SecuritySettings,
    ConversationContext,
    ConversationState,
)


class TestStateProtectionIntegration:
    """Test integration of state protection components with TaskQueueManager."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client."""
        client = Mock()
        client.ping = AsyncMock(return_value=True)
        client.get = AsyncMock()
        client.set = AsyncMock(return_value=True)
        client.setex = AsyncMock(return_value=True)
        client.delete = AsyncMock(return_value=True)
        client.keys = AsyncMock(return_value=[])
        client.sadd = AsyncMock(return_value=True)
        client.smembers = AsyncMock(return_value=set())
        return client

    @pytest.fixture
    def task_queue_config(self):
        """Create test TaskQueueConfig."""
        return TaskQueueConfig(
            queue_config=QueueConfig(
                task_queue_name="test_task_queue",
                max_task_size=1024 * 1024,
                max_queue_length=1000
            ),
            persistence_config=PersistenceConfig(
                hot_storage_ttl=3600,
                warm_storage_ttl=86400,
                checkpoint_interval=300
            ),
            coordination_config=CoordinationConfig(
                lock_timeout=30,
                consensus_timeout=10
            ),
            security_settings=SecuritySettings(
                dangerous_patterns=["rm -rf", "eval("],
                max_content_length=10000
            ),
            max_consecutive_failures=5
        )

    @pytest.fixture
    def conversation_context(self):
        """Create test conversation context."""
        return ConversationContext(
            conversation_id="test_conversation_123",
            current_state=ConversationState.IDLE,
            created_at=datetime.now(),
            turns=[]
        )

    @pytest.fixture
    async def task_queue_manager(self, task_queue_config, mock_redis_client):
        """Create TaskQueueManager with mocked dependencies."""
        # Mock async functions that get called during initialization
        with patch.object(StatePersistenceStrategy, '__init__', return_value=None), \
             patch.object(EnhancedStateIntegrityMonitor, '__init__', return_value=None), \
             patch.object(ConversationStateLockManager, '__init__', return_value=None), \
             patch.object(EnhancedStateIntegrityMonitor, 'start_continuous_monitoring', new_callable=AsyncMock):

            manager = TaskQueueManager(task_queue_config, mock_redis_client)

            # Mock the state protection components
            manager.state_persistence_strategy = Mock(spec=StatePersistenceStrategy)
            manager.integrity_monitor = Mock(spec=EnhancedStateIntegrityMonitor)
            manager.state_lock_manager = Mock(spec=ConversationStateLockManager)

            return manager

    @pytest.mark.asyncio
    async def test_state_protection_initialization(self, task_queue_config, mock_redis_client):
        """Test that state protection components are properly initialized."""
        with patch.object(StatePersistenceStrategy, '__init__', return_value=None) as mock_persistence_init, \
             patch.object(EnhancedStateIntegrityMonitor, '__init__', return_value=None) as mock_monitor_init, \
             patch.object(ConversationStateLockManager, '__init__', return_value=None) as mock_lock_init, \
             patch.object(EnhancedStateIntegrityMonitor, 'start_continuous_monitoring', new_callable=AsyncMock):

            manager = TaskQueueManager(task_queue_config, mock_redis_client)

            # Verify initialization calls were made
            mock_persistence_init.assert_called_once()
            mock_monitor_init.assert_called_once()
            mock_lock_init.assert_called_once()

            # Verify components are available
            assert hasattr(manager, 'state_persistence_strategy')
            assert hasattr(manager, 'integrity_monitor')
            assert hasattr(manager, 'state_lock_manager')

    @pytest.mark.asyncio
    async def test_secure_state_operation_with_locking(self, task_queue_manager, conversation_context):
        """Test secure state operation with distributed locking."""
        # Mock the lock manager context manager
        mock_lock = Mock()
        mock_lock.lock_id = "test_lock_123"

        # Create an async context manager mock
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_lock)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)

        task_queue_manager.state_lock_manager.acquire_conversation_lock = Mock(
            return_value=async_context_manager
        )

        # Mock operation function
        mock_operation = AsyncMock(return_value="operation_result")

        # Execute secure operation
        result = await task_queue_manager.secure_state_operation(
            conversation_context.conversation_id,
            mock_operation,
            "test_arg"
        )

        # Verify results
        assert result == "operation_result"
        mock_operation.assert_called_once_with("test_arg")
        task_queue_manager.state_lock_manager.acquire_conversation_lock.assert_called_once_with(
            conversation_context.conversation_id, "write", timeout=30
        )

    @pytest.mark.asyncio
    async def test_secure_state_operation_fallback_without_lock_manager(self, task_queue_manager):
        """Test secure state operation fallback when lock manager unavailable."""
        # Remove lock manager
        task_queue_manager.state_lock_manager = None

        # Mock operation function
        mock_operation = AsyncMock(return_value="fallback_result")

        # Execute operation
        result = await task_queue_manager.secure_state_operation(
            "test_conversation",
            mock_operation,
            "test_arg"
        )

        # Verify fallback behavior
        assert result == "fallback_result"
        mock_operation.assert_called_once_with("test_arg")

    @pytest.mark.asyncio
    async def test_persist_state_with_protection(self, task_queue_manager, conversation_context):
        """Test state persistence with full protection."""
        # Mock persistence strategy results
        mock_persistence_results = {
            PersistenceLayer.HOT: Mock(
                success=True,
                state_hash="hash123",
                timestamp=datetime.now(),
                integrity_verified=True,
                error_message=None
            ),
            PersistenceLayer.WARM: Mock(
                success=True,
                state_hash="hash123",
                timestamp=datetime.now(),
                integrity_verified=True,
                error_message=None
            )
        }

        task_queue_manager.state_persistence_strategy.persist_state_secure = AsyncMock(
            return_value=mock_persistence_results
        )

        # Mock integrity check
        mock_integrity_report = Mock()
        mock_integrity_report.overall_status = IntegrityStatus.VALID
        mock_integrity_report.corruption_detected = False
        mock_integrity_report.recovery_recommended = False

        task_queue_manager.integrity_monitor.check_conversation_integrity = AsyncMock(
            return_value=mock_integrity_report
        )

        # Execute protected persistence
        result = await task_queue_manager.persist_state_with_protection(conversation_context)

        # Verify results
        assert result["success"] is True
        assert result["success_rate"] == 1.0
        assert len(result["successful_layers"]) == 2
        assert result["integrity_report"]["overall_status"] == "valid"

        # Verify method calls
        task_queue_manager.state_persistence_strategy.persist_state_secure.assert_called_once()
        task_queue_manager.integrity_monitor.check_conversation_integrity.assert_called_once_with(
            conversation_context.conversation_id
        )

    @pytest.mark.asyncio
    async def test_persist_state_with_partial_failure(self, task_queue_manager, conversation_context):
        """Test state persistence with partial layer failures."""
        # Mock persistence strategy with mixed results
        mock_persistence_results = {
            PersistenceLayer.HOT: Mock(
                success=True,
                state_hash="hash123",
                timestamp=datetime.now(),
                integrity_verified=True,
                error_message=None
            ),
            PersistenceLayer.WARM: Mock(
                success=False,
                state_hash="hash123",
                timestamp=datetime.now(),
                integrity_verified=False,
                error_message="Connection failed"
            ),
            PersistenceLayer.COLD: Mock(
                success=True,
                state_hash="hash123",
                timestamp=datetime.now(),
                integrity_verified=True,
                error_message=None
            )
        }

        task_queue_manager.state_persistence_strategy.persist_state_secure = AsyncMock(
            return_value=mock_persistence_results
        )

        # Mock integrity check
        mock_integrity_report = Mock()
        mock_integrity_report.overall_status = IntegrityStatus.VALID
        mock_integrity_report.corruption_detected = False
        mock_integrity_report.recovery_recommended = False

        task_queue_manager.integrity_monitor.check_conversation_integrity = AsyncMock(
            return_value=mock_integrity_report
        )

        # Execute protected persistence
        result = await task_queue_manager.persist_state_with_protection(conversation_context)

        # Verify results reflect partial success
        assert result["success"] is True  # >50% success rate
        assert result["success_rate"] == 2/3  # 2 out of 3 layers successful
        assert len(result["successful_layers"]) == 2
        assert "hot" in result["successful_layers"]
        assert "cold" in result["successful_layers"]
        assert "warm" not in result["successful_layers"]

    @pytest.mark.asyncio
    async def test_check_system_state_integrity(self, task_queue_manager):
        """Test comprehensive system integrity check."""
        # Mock integrity monitor results
        mock_integrity_results = {
            "check_timestamp": datetime.now().isoformat(),
            "total_conversations": 5,
            "healthy_conversations": 4,
            "corrupted_conversations": 1,
            "corruption_rate": 0.2
        }

        task_queue_manager.integrity_monitor.perform_system_integrity_check = AsyncMock(
            return_value=mock_integrity_results
        )

        # Mock component metrics
        task_queue_manager.state_persistence_strategy.get_persistence_metrics = Mock(
            return_value={"strategy": "multi_layer_secure", "success_rate": 0.95}
        )

        task_queue_manager.state_lock_manager.get_lock_metrics = Mock(
            return_value={"active_locks": [], "metrics": {"locks_acquired": 10}}
        )

        task_queue_manager.integrity_monitor.get_integrity_metrics = Mock(
            return_value={"monitoring_active": True, "total_checks": 100}
        )

        # Execute integrity check
        result = await task_queue_manager.check_system_state_integrity()

        # Verify comprehensive results
        assert "integrity_check" in result
        assert "persistence_metrics" in result
        assert "lock_metrics" in result
        assert "integrity_monitor_metrics" in result
        assert "system_health" in result

        system_health = result["system_health"]
        assert system_health["state_protection_enabled"] is True
        assert "redis_connectivity" in system_health
        assert "monitoring_active" in system_health

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks(self, task_queue_manager):
        """Test expired locks cleanup."""
        # Mock lock manager cleanup
        task_queue_manager.state_lock_manager.force_release_expired_locks = AsyncMock(
            return_value=3  # 3 locks cleaned
        )

        # Execute cleanup
        result = await task_queue_manager.cleanup_expired_locks()

        # Verify results
        assert result["cleanup_successful"] is True
        assert result["expired_locks_cleaned"] == 3

        # Verify method call
        task_queue_manager.state_lock_manager.force_release_expired_locks.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_state_protection(self, task_queue_manager):
        """Test graceful shutdown of state protection components."""
        # Mock shutdown methods
        task_queue_manager.integrity_monitor.stop_monitoring = Mock()
        task_queue_manager.state_lock_manager.shutdown = AsyncMock()

        # Execute shutdown
        await task_queue_manager.shutdown_state_protection()

        # Verify shutdown calls
        task_queue_manager.integrity_monitor.stop_monitoring.assert_called_once()
        task_queue_manager.state_lock_manager.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_state_protection_error_handling(self, task_queue_manager, conversation_context):
        """Test error handling in state protection operations."""
        # Mock persistence strategy to raise exception
        task_queue_manager.state_persistence_strategy.persist_state_secure = AsyncMock(
            side_effect=Exception("Redis connection failed")
        )

        # Execute protected persistence
        result = await task_queue_manager.persist_state_with_protection(conversation_context)

        # Verify error handling
        assert result["success"] is False
        assert "error" in result
        assert "Redis connection failed" in result["error"]

    @pytest.mark.asyncio
    async def test_secure_state_operation_exception_propagation(self, task_queue_manager):
        """Test that exceptions in secure operations are properly propagated."""
        # Mock lock manager
        mock_lock = Mock()
        mock_lock.lock_id = "test_lock_123"

        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_lock)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)

        task_queue_manager.state_lock_manager.acquire_conversation_lock = Mock(
            return_value=async_context_manager
        )

        # Mock operation that raises exception
        mock_operation = AsyncMock(side_effect=ValueError("Operation failed"))

        # Execute and expect exception
        with pytest.raises(ValueError, match="Operation failed"):
            await task_queue_manager.secure_state_operation(
                "test_conversation",
                mock_operation
            )

        # Verify operation was called
        mock_operation.assert_called_once()

    @pytest.mark.asyncio
    async def test_integration_with_existing_methods(self, task_queue_manager):
        """Test that state protection integrates with existing TaskQueueManager methods."""
        # Mock components for health check
        task_queue_manager.integrity_monitor.get_integrity_metrics = Mock(
            return_value={"monitoring_active": True}
        )

        # Execute existing health check method
        health_status = task_queue_manager.get_health_status()

        # Verify health status includes standard information
        assert hasattr(health_status, 'status')
        assert hasattr(health_status, 'health_score')
        assert hasattr(health_status, 'issues')

        # Test module info includes state protection
        module_info = task_queue_manager.get_module_info()
        assert "module_name" in module_info
        assert "capabilities" in module_info

    def test_state_protection_components_not_none(self, task_queue_manager):
        """Test that state protection components are not None after initialization."""
        assert task_queue_manager.state_persistence_strategy is not None
        assert task_queue_manager.integrity_monitor is not None
        assert task_queue_manager.state_lock_manager is not None