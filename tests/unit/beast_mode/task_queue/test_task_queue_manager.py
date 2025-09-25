"""
Unit tests for TaskQueueManager - ReflectiveModule implementation
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.beast_mode.task_queue.task_queue_manager import TaskQueueManager
from src.beast_mode.task_queue.models import (
    TaskQueueConfig,
    QueueConfig,
    PersistenceConfig,
    CoordinationConfig,
    SecuritySettings,
    ConversationState,
    TaskContext,
    TaskResult,
)
from src.rm_ddd.core.unified_reflective_module import (
    ModuleStatus,
    ModuleCapability,
)


class TestTaskQueueManager:
    """Test TaskQueueManager ReflectiveModule implementation."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client."""
        client = Mock()
        client.ping = AsyncMock(return_value=True)
        return client

    @pytest.fixture
    def task_queue_config(self):
        """Create test TaskQueueConfig."""
        from src.beast_mode.task_queue.models import (
            RedisConfig, MonitoringConfig, PerformanceLimits, RetryPolicy
        )

        return TaskQueueConfig(
            redis_config=RedisConfig(
                host="localhost",
                port=6379
            ),
            queue_configs=[QueueConfig(
                name="test_task_queue",
                priority=1,
                max_concurrent_tasks=5,
                task_timeout_seconds=300,
                retry_policy=RetryPolicy(
                    max_retries=3,
                    backoff_multiplier=2.0
                )
            )],
            performance_limits=PerformanceLimits(
                task_retrieval_timeout_ms=100,
                checkpoint_creation_timeout_ms=50
            ),
            security_settings=SecuritySettings(
                dangerous_patterns=["rm -rf", "eval("],
                max_payload_size_bytes=10000
            ),
            monitoring_config=MonitoringConfig(
                prometheus_enabled=False,
                log_level="DEBUG"
            ),
            persistence_config=PersistenceConfig(
                hot_storage_ttl_hours=1,
                warm_storage_ttl_days=7
            )
        )

    @pytest.fixture
    def task_queue_manager(self, task_queue_config, mock_redis_client):
        """Create TaskQueueManager instance."""
        return TaskQueueManager(task_queue_config, mock_redis_client)

    def test_initialization_with_redis(self, task_queue_config, mock_redis_client):
        """Test TaskQueueManager initialization with Redis."""
        manager = TaskQueueManager(task_queue_config, mock_redis_client)

        assert manager.config == task_queue_config
        assert manager.redis_client == mock_redis_client
        assert manager._total_tasks_processed == 0
        assert manager._total_tasks_failed == 0
        assert manager._consecutive_failures == 0
        assert not manager._fallback_mode

    def test_initialization_without_redis(self, task_queue_config):
        """Test TaskQueueManager initialization without Redis."""
        manager = TaskQueueManager(task_queue_config, None)

        assert manager.config == task_queue_config
        assert manager.redis_client is None
        assert manager.conversation_state_machine is not None
        assert manager.persistence_manager is None

    def test_get_module_info(self, task_queue_manager):
        """Test get_module_info ReflectiveModule method."""
        info = task_queue_manager.get_module_info()

        assert info["module_name"] == "TaskQueueManager"
        assert info["module_version"] == "1.0.0"
        assert "description" in info
        assert "capabilities" in info
        assert "configuration" in info
        assert "statistics" in info

        # Check configuration details
        config = info["configuration"]
        assert "redis_enabled" in config
        assert "fallback_mode" in config
        assert "max_task_size" in config
        assert "queue_name" in config

        # Check statistics
        stats = info["statistics"]
        assert "total_tasks_processed" in stats
        assert "total_tasks_failed" in stats
        assert "consecutive_failures" in stats
        assert "uptime_hours" in stats

    def test_get_capabilities_with_redis(self, task_queue_manager):
        """Test get_capabilities with healthy Redis connection."""
        capabilities = task_queue_manager.get_capabilities()

        expected_capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.VALIDATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION,
        ]

        assert all(cap in capabilities for cap in expected_capabilities)

    def test_get_capabilities_without_redis(self, task_queue_config):
        """Test get_capabilities without Redis."""
        manager = TaskQueueManager(task_queue_config, None)
        capabilities = manager.get_capabilities()

        expected_capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.VALIDATION,
        ]

        assert all(cap in capabilities for cap in expected_capabilities)
        assert ModuleCapability.DATA_PROCESSING not in capabilities
        assert ModuleCapability.API_INTEGRATION not in capabilities

    def test_get_health_status_healthy(self, task_queue_manager):
        """Test get_health_status when healthy."""
        health = task_queue_manager.get_health_status()

        assert health.status == ModuleStatus.HEALTHY
        assert health.health_score == 1.0
        assert len(health.issues) == 0
        assert health.error_count == 0
        assert health.warning_count == 0

    def test_get_health_status_with_failures(self, task_queue_manager):
        """Test get_health_status with consecutive failures."""
        task_queue_manager._consecutive_failures = 3

        health = task_queue_manager.get_health_status()

        assert health.status == ModuleStatus.WARNING
        assert health.health_score < 1.0
        assert any("failures" in issue.lower() for issue in health.issues)

    def test_get_health_status_redis_unhealthy(self, task_queue_manager):
        """Test get_health_status with unhealthy Redis."""
        task_queue_manager._redis_connection_healthy = False

        health = task_queue_manager.get_health_status()

        assert health.status == ModuleStatus.WARNING
        assert health.health_score < 1.0
        assert any("redis" in issue.lower() for issue in health.issues)

    def test_graceful_degradation_redis_failure(self, task_queue_manager):
        """Test graceful degradation when Redis fails."""
        task_queue_manager._redis_connection_healthy = False

        result = task_queue_manager.graceful_degradation()

        assert result.success
        assert ModuleCapability.DATA_PROCESSING in result.degraded_capabilities
        assert ModuleCapability.API_INTEGRATION in result.degraded_capabilities
        assert ModuleCapability.CORE_FUNCTIONALITY in result.remaining_capabilities
        assert task_queue_manager._fallback_mode

    @pytest.mark.asyncio
    async def test_check_and_process_tasks_no_tasks(self, task_queue_manager):
        """Test check_and_process_tasks when no tasks available."""
        # Mock _get_queue_status to return no tasks
        task_queue_manager._get_queue_status = AsyncMock(
            return_value={"tasks_available": 0, "queue_health": "healthy"}
        )

        result = await task_queue_manager.check_and_process_tasks()

        assert result["status"] == "no_tasks"
        assert result["tasks_available"] == 0
        assert "timestamp" in result
        assert "processing_latency_ms" in result

    @pytest.mark.asyncio
    async def test_check_and_process_tasks_with_tasks(self, task_queue_manager):
        """Test check_and_process_tasks when tasks are available."""
        # Mock _get_queue_status to return tasks
        task_queue_manager._get_queue_status = AsyncMock(
            return_value={"tasks_available": 3, "queue_health": "healthy"}
        )

        # Mock _process_tasks_background
        task_queue_manager._process_tasks_background = AsyncMock()

        result = await task_queue_manager.check_and_process_tasks()

        assert result["status"] == "processing_started"
        assert result["tasks_available"] == 3
        assert "timestamp" in result
        assert "processing_latency_ms" in result

    @pytest.mark.asyncio
    async def test_check_and_process_tasks_not_ready(self, task_queue_manager):
        """Test check_and_process_tasks when manager not ready."""
        task_queue_manager._is_ready = Mock(return_value=False)

        result = await task_queue_manager.check_and_process_tasks()

        assert result["status"] == "degraded"
        assert "not ready" in result["message"]

    @pytest.mark.asyncio
    async def test_get_queue_status_healthy(self, task_queue_manager):
        """Test _get_queue_status with healthy Redis."""
        # Mock redis operations
        task_queue_manager.redis_ops = Mock()
        task_queue_manager.redis_ops.get_queue_size = AsyncMock(return_value=5)

        result = await task_queue_manager._get_queue_status()

        assert result["tasks_available"] == 5
        assert result["queue_health"] == "healthy"

    @pytest.mark.asyncio
    async def test_get_queue_status_no_redis_ops(self, task_queue_config):
        """Test _get_queue_status without Redis operations."""
        manager = TaskQueueManager(task_queue_config, None)

        result = await manager._get_queue_status()

        assert result["tasks_available"] == 0
        assert result["queue_health"] == "degraded"

    @pytest.mark.asyncio
    async def test_process_single_task_success(self, task_queue_manager):
        """Test _process_single_task successful processing."""
        # Mock components
        task_context = TaskContext(
            task_id="test_task_1",
            task_type="test",
            content={"action": "test"},
            created_at=datetime.now(),
            state=TaskContext.TaskState.PENDING
        )

        task_result = TaskResult(
            task_id="test_task_1",
            success=True,
            result={"status": "completed"},
            processing_time_ms=100.0
        )

        task_queue_manager.redis_ops = Mock()
        task_queue_manager.redis_ops.dequeue_task = AsyncMock(return_value=task_context)

        task_queue_manager.task_processor = Mock()
        task_queue_manager.task_processor.process_task = AsyncMock(return_value=task_result)

        result = await task_queue_manager._process_single_task()

        assert result["task_found"]
        assert result["success"]
        assert result["task_id"] == "test_task_1"

    @pytest.mark.asyncio
    async def test_process_single_task_no_task(self, task_queue_manager):
        """Test _process_single_task when no task available."""
        task_queue_manager.redis_ops = Mock()
        task_queue_manager.redis_ops.dequeue_task = AsyncMock(return_value=None)

        result = await task_queue_manager._process_single_task()

        assert not result["task_found"]
        assert result["success"]

    def test_is_ready_healthy(self, task_queue_manager):
        """Test _is_ready when manager is healthy."""
        assert task_queue_manager._is_ready()

    def test_is_ready_fallback_mode(self, task_queue_manager):
        """Test _is_ready in fallback mode."""
        task_queue_manager._fallback_mode = True
        assert task_queue_manager._is_ready()

    def test_is_ready_redis_unhealthy(self, task_queue_manager):
        """Test _is_ready with unhealthy Redis."""
        task_queue_manager._redis_connection_healthy = False
        assert not task_queue_manager._is_ready()

    def test_is_ready_too_many_failures(self, task_queue_manager):
        """Test _is_ready with too many consecutive failures."""
        task_queue_manager._consecutive_failures = 10  # Above config limit
        assert not task_queue_manager._is_ready()

    @pytest.mark.asyncio
    async def test_get_queue_metrics_success(self, task_queue_manager):
        """Test get_queue_metrics successful collection."""
        # Mock redis operations
        task_queue_manager.redis_ops = Mock()
        task_queue_manager.redis_ops.get_queue_size = AsyncMock(return_value=7)

        # Set some test data
        task_queue_manager._total_tasks_processed = 100
        task_queue_manager._total_tasks_failed = 5

        result = await task_queue_manager.get_queue_metrics()

        assert result["current_queue_size"] == 7
        assert result["total_processed"] == 100
        assert result["total_failed"] == 5
        assert "success_rate" in result
        assert "health_score" in result

    @pytest.mark.asyncio
    async def test_get_queue_metrics_no_redis(self, task_queue_config):
        """Test get_queue_metrics without Redis."""
        manager = TaskQueueManager(task_queue_config, None)

        result = await manager.get_queue_metrics()

        assert "error" in result
        assert "not available" in result["error"]

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, task_queue_manager):
        """Test health_check comprehensive endpoint."""
        # Mock get_queue_metrics
        task_queue_manager.get_queue_metrics = AsyncMock(
            return_value={"current_queue_size": 3, "success_rate": 0.95}
        )

        result = await task_queue_manager.health_check()

        assert "status" in result
        assert "health_score" in result
        assert "issues" in result
        assert "capabilities" in result
        assert "metrics" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_ready_check_endpoint(self, task_queue_manager):
        """Test ready_check endpoint."""
        result = await task_queue_manager.ready_check()

        assert "ready" in result
        assert "reason" in result
        assert "checks" in result
        assert "timestamp" in result

        checks = result["checks"]
        assert "redis_connectivity" in checks
        assert "consecutive_failures_ok" in checks
        assert "fallback_mode" in checks

    @pytest.mark.asyncio
    async def test_process_tasks_background_state_transitions(self, task_queue_manager):
        """Test background processing handles state transitions correctly."""
        # Mock state machine
        task_queue_manager.conversation_state_machine.handle_transition = AsyncMock()

        # Mock no tasks to process
        task_queue_manager._process_single_task = AsyncMock(
            return_value={"task_found": False, "success": True}
        )

        await task_queue_manager._process_tasks_background()

        # Verify state transitions were called
        assert task_queue_manager.conversation_state_machine.handle_transition.call_count == 2

        # Check transition to HOOK_TRIGGERED
        first_call = task_queue_manager.conversation_state_machine.handle_transition.call_args_list[0]
        assert first_call[0][0] == ConversationState.IDLE
        assert first_call[0][1] == ConversationState.HOOK_TRIGGERED

        # Check transition back to IDLE
        second_call = task_queue_manager.conversation_state_machine.handle_transition.call_args_list[1]
        assert second_call[0][1] == ConversationState.IDLE

    def test_module_integration_with_reflective_module_pattern(self, task_queue_manager):
        """Test that TaskQueueManager properly implements ReflectiveModule pattern."""
        # Test all required ReflectiveModule methods exist and work
        module_info = task_queue_manager.get_module_info()
        assert isinstance(module_info, dict)

        capabilities = task_queue_manager.get_capabilities()
        assert isinstance(capabilities, list)
        assert all(isinstance(cap, ModuleCapability) for cap in capabilities)

        health_status = task_queue_manager.get_health_status()
        assert hasattr(health_status, 'status')
        assert hasattr(health_status, 'health_score')

        degradation_result = task_queue_manager.graceful_degradation()
        assert hasattr(degradation_result, 'success')
        assert isinstance(degradation_result.success, bool)