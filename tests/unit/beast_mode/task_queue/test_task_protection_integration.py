"""
Unit tests for task protection integration with TaskQueueManager
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.beast_mode.task_queue.task_queue_manager import TaskQueueManager
from src.beast_mode.task_queue.task_protection import (
    TaskDeduplicationManager,
    IdempotentTaskProcessor,
    PriorityTaskScheduler,
    TaskPriority,
    ProcessingStatus,
)
from src.beast_mode.task_queue.models import (
    TaskQueueConfig,
    QueueConfig,
    PersistenceConfig,
    CoordinationConfig,
    SecuritySettings,
    TaskContext,
    TaskResult,
    TaskFailure,
    TaskState,
)


class TestTaskProtectionIntegration:
    """Test integration of task protection components with TaskQueueManager."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client."""
        client = Mock()
        client.ping = AsyncMock(return_value=True)
        client.get = AsyncMock()
        client.set = AsyncMock(return_value=True)
        client.setex = AsyncMock(return_value=True)
        client.delete = AsyncMock(return_value=True)
        client.exists = AsyncMock(return_value=False)
        client.keys = AsyncMock(return_value=[])
        client.hset = AsyncMock(return_value=True)
        client.hgetall = AsyncMock(return_value={})
        client.zadd = AsyncMock(return_value=True)
        client.zcard = AsyncMock(return_value=0)
        client.zrange = AsyncMock(return_value=[])
        client.zpopmin = AsyncMock(return_value=[])
        client.zrem = AsyncMock(return_value=True)
        client.zrangebyscore = AsyncMock(return_value=[])
        client.expire = AsyncMock(return_value=True)
        client.pipeline = AsyncMock()

        # Mock pipeline context manager
        pipeline_mock = Mock()
        pipeline_mock.hset = AsyncMock()
        pipeline_mock.expire = AsyncMock()
        pipeline_mock.delete = AsyncMock()
        pipeline_mock.zadd = AsyncMock()
        pipeline_mock.zrem = AsyncMock()
        pipeline_mock.execute = AsyncMock()
        pipeline_mock.__aenter__ = AsyncMock(return_value=pipeline_mock)
        pipeline_mock.__aexit__ = AsyncMock(return_value=None)

        client.pipeline.return_value = pipeline_mock
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
    def task_context(self):
        """Create test task context."""
        return TaskContext(
            task_id="test_task_123",
            task_type="test_task",
            content={"action": "test", "data": "sample"},
            created_at=datetime.now(),
            state=TaskState.PENDING
        )

    @pytest.fixture
    async def task_queue_manager(self, task_queue_config, mock_redis_client):
        """Create TaskQueueManager with mocked task protection dependencies."""
        with patch.object(TaskDeduplicationManager, '__init__', return_value=None), \
             patch.object(IdempotentTaskProcessor, '__init__', return_value=None), \
             patch.object(PriorityTaskScheduler, '__init__', return_value=None):

            manager = TaskQueueManager(task_queue_config, mock_redis_client)

            # Mock the task protection components
            manager.task_deduplication = Mock(spec=TaskDeduplicationManager)
            manager.idempotent_processor = Mock(spec=IdempotentTaskProcessor)
            manager.priority_scheduler = Mock(spec=PriorityTaskScheduler)

            return manager

    @pytest.mark.asyncio
    async def test_task_protection_initialization(self, task_queue_config, mock_redis_client):
        """Test that task protection components are properly initialized."""
        with patch.object(TaskDeduplicationManager, '__init__', return_value=None) as mock_dedup_init, \
             patch.object(IdempotentTaskProcessor, '__init__', return_value=None) as mock_idempotent_init, \
             patch.object(PriorityTaskScheduler, '__init__', return_value=None) as mock_priority_init:

            manager = TaskQueueManager(task_queue_config, mock_redis_client)

            # Verify initialization calls were made
            mock_dedup_init.assert_called_once()
            mock_idempotent_init.assert_called_once()
            mock_priority_init.assert_called_once()

            # Verify components are available
            assert hasattr(manager, 'task_deduplication')
            assert hasattr(manager, 'idempotent_processor')
            assert hasattr(manager, 'priority_scheduler')

    @pytest.mark.asyncio
    async def test_process_task_with_protection_success(self, task_queue_manager, task_context):
        """Test successful task processing with full protection."""
        # Mock task deduplication
        mock_claim = Mock()
        mock_claim.claim_key = "test_claim_123"

        task_queue_manager.task_deduplication.is_task_already_processed = AsyncMock(return_value=False)
        task_queue_manager.task_deduplication.claim_task_for_processing = AsyncMock(return_value=mock_claim)
        task_queue_manager.task_deduplication.complete_task_processing = AsyncMock()

        # Mock idempotent processor
        expected_result = TaskResult(
            task_id=task_context.task_id,
            success=True,
            result={"status": "completed", "task_type": task_context.task_type},
            processing_time_ms=100.0
        )

        task_queue_manager.idempotent_processor.process_task_idempotently = AsyncMock(
            return_value=expected_result
        )

        # Execute protected processing
        result = await task_queue_manager.process_task_with_protection(task_context, TaskPriority.HIGH)

        # Verify results
        assert result["success"] is True
        assert result["task_id"] == task_context.task_id
        assert result["priority"] == "high"
        assert "claim_id" in result
        assert "protection_features" in result

        protection_features = result["protection_features"]
        assert protection_features["deduplication"] is True
        assert protection_features["idempotency"] is True

        # Verify method calls
        task_queue_manager.task_deduplication.is_task_already_processed.assert_called_once_with(task_context.task_id)
        task_queue_manager.task_deduplication.claim_task_for_processing.assert_called_once_with(task_context.task_id)
        task_queue_manager.idempotent_processor.process_task_idempotently.assert_called_once()
        task_queue_manager.task_deduplication.complete_task_processing.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_task_already_processed(self, task_queue_manager, task_context):
        """Test task processing when task already completed."""
        # Mock task already processed
        task_queue_manager.task_deduplication.is_task_already_processed = AsyncMock(return_value=True)

        result = await task_queue_manager.process_task_with_protection(task_context)

        # Verify skipped result
        assert result["success"] is True
        assert result["skipped"] is True
        assert result["reason"] == "Task already processed"
        assert result["task_id"] == task_context.task_id

        # Verify no claim was attempted
        task_queue_manager.task_deduplication.claim_task_for_processing.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_task_claim_failed(self, task_queue_manager, task_context):
        """Test task processing when claim fails (task claimed by another instance)."""
        task_queue_manager.task_deduplication.is_task_already_processed = AsyncMock(return_value=False)
        task_queue_manager.task_deduplication.claim_task_for_processing = AsyncMock(return_value=None)

        result = await task_queue_manager.process_task_with_protection(task_context)

        # Verify claim failure result
        assert result["success"] is False
        assert result["skipped"] is True
        assert result["reason"] == "Task already claimed by another instance"

        # Verify no processing was attempted
        task_queue_manager.idempotent_processor.process_task_idempotently.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_task_processing_failure(self, task_queue_manager, task_context):
        """Test task processing when processing fails."""
        # Mock successful claim
        mock_claim = Mock()
        mock_claim.claim_key = "test_claim_123"

        task_queue_manager.task_deduplication.is_task_already_processed = AsyncMock(return_value=False)
        task_queue_manager.task_deduplication.claim_task_for_processing = AsyncMock(return_value=mock_claim)
        task_queue_manager.task_deduplication.fail_task_processing = AsyncMock()

        # Mock processing failure
        task_queue_manager.idempotent_processor.process_task_idempotently = AsyncMock(
            side_effect=Exception("Processing failed")
        )

        result = await task_queue_manager.process_task_with_protection(task_context)

        # Verify failure result
        assert result["success"] is False
        assert result["error"] == "Processing failed"
        assert result["claim_id"] == mock_claim.claim_key

        # Verify failure was recorded
        task_queue_manager.task_deduplication.fail_task_processing.assert_called_once()

    @pytest.mark.asyncio
    async def test_enqueue_task_with_priority(self, task_queue_manager, task_context):
        """Test enqueueing task with priority."""
        task_queue_manager.priority_scheduler.enqueue_task = AsyncMock(return_value=True)

        result = await task_queue_manager.enqueue_task_with_priority(task_context, TaskPriority.CRITICAL)

        # Verify results
        assert result["success"] is True
        assert result["task_id"] == task_context.task_id
        assert result["priority"] == "critical"

        # Verify method call
        task_queue_manager.priority_scheduler.enqueue_task.assert_called_once_with(
            task_context, TaskPriority.CRITICAL
        )

    @pytest.mark.asyncio
    async def test_get_next_priority_task(self, task_queue_manager, task_context):
        """Test getting next priority task."""
        task_queue_manager.priority_scheduler.get_next_task_with_fairness = AsyncMock(
            return_value=(task_context, TaskPriority.HIGH)
        )

        result = await task_queue_manager.get_next_priority_task()

        # Verify results
        assert result["success"] is True
        assert result["task"]["task_id"] == task_context.task_id
        assert result["priority"] == "high"

        # Verify method call
        task_queue_manager.priority_scheduler.get_next_task_with_fairness.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_next_priority_task_no_tasks(self, task_queue_manager):
        """Test getting next priority task when no tasks available."""
        task_queue_manager.priority_scheduler.get_next_task_with_fairness = AsyncMock(return_value=None)

        result = await task_queue_manager.get_next_priority_task()

        # Verify no tasks result
        assert result["success"] is True
        assert result["task"] is None
        assert result["message"] == "No tasks available"

    @pytest.mark.asyncio
    async def test_get_task_protection_metrics(self, task_queue_manager):
        """Test getting comprehensive task protection metrics."""
        # Mock component metrics
        task_queue_manager.task_deduplication.get_deduplication_metrics = Mock(
            return_value={"tasks_claimed": 10, "tasks_completed": 8}
        )

        task_queue_manager.idempotent_processor.get_idempotency_metrics = Mock(
            return_value={"cache_hit_rate": 0.75, "idempotent_calls": 20}
        )

        task_queue_manager.priority_scheduler.get_scheduling_metrics = Mock(
            return_value={"tasks_boosted": 3, "weighted_selections": 15}
        )

        result = await task_queue_manager.get_task_protection_metrics()

        # Verify comprehensive results
        assert result["task_protection_enabled"] is True
        assert "deduplication" in result
        assert "idempotency" in result
        assert "scheduling" in result

        # Verify specific metrics
        assert result["deduplication"]["tasks_claimed"] == 10
        assert result["idempotency"]["cache_hit_rate"] == 0.75
        assert result["scheduling"]["tasks_boosted"] == 3

    @pytest.mark.asyncio
    async def test_get_priority_queue_status(self, task_queue_manager):
        """Test getting priority queue status."""
        expected_status = {
            "total_tasks": 15,
            "queues": {
                "critical": {"size": 2},
                "high": {"size": 5},
                "normal": {"size": 8},
                "low": {"size": 0}
            }
        }

        task_queue_manager.priority_scheduler.get_queue_status = AsyncMock(
            return_value=expected_status
        )

        result = await task_queue_manager.get_priority_queue_status()

        # Verify results
        assert result["total_tasks"] == 15
        assert "queues" in result
        assert result["queues"]["critical"]["size"] == 2

        # Verify method call
        task_queue_manager.priority_scheduler.get_queue_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_task_protection(self, task_queue_manager):
        """Test task protection cleanup operations."""
        task_queue_manager.task_deduplication.cleanup_expired_claims = AsyncMock(return_value=5)

        result = await task_queue_manager.cleanup_task_protection()

        # Verify cleanup results
        assert "cleanup_operations" in result
        cleanup_ops = result["cleanup_operations"]
        assert len(cleanup_ops) == 1
        assert cleanup_ops[0]["component"] == "task_deduplication"
        assert cleanup_ops[0]["items_cleaned"] == 5

        # Verify method call
        task_queue_manager.task_deduplication.cleanup_expired_claims.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalidate_task_idempotency(self, task_queue_manager, task_context):
        """Test invalidating task idempotency cache."""
        task_queue_manager.idempotent_processor.invalidate_idempotent_result = AsyncMock(
            return_value=True
        )

        result = await task_queue_manager.invalidate_task_idempotency(task_context)

        # Verify results
        assert result["success"] is True
        assert result["invalidated"] is True
        assert result["task_id"] == task_context.task_id

        # Verify method call
        task_queue_manager.idempotent_processor.invalidate_idempotent_result.assert_called_once_with(
            task_context
        )

    @pytest.mark.asyncio
    async def test_execute_task_logic_placeholder(self, task_queue_manager, task_context):
        """Test the placeholder task execution logic."""
        result = await task_queue_manager._execute_task_logic(task_context)

        # Verify placeholder results
        assert isinstance(result, TaskResult)
        assert result.task_id == task_context.task_id
        assert result.success is True
        assert result.result["status"] == "completed"
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_task_protection_error_handling(self, task_queue_manager, task_context):
        """Test error handling in task protection operations."""
        # Mock deduplication to raise exception
        task_queue_manager.task_deduplication.is_task_already_processed = AsyncMock(
            side_effect=Exception("Redis connection failed")
        )

        result = await task_queue_manager.process_task_with_protection(task_context)

        # Verify error handling
        assert result["success"] is False
        assert "error" in result
        assert "Redis connection failed" in result["error"]

    @pytest.mark.asyncio
    async def test_task_protection_without_components(self, task_context):
        """Test task protection behavior when components are not available."""
        # Create manager without task protection components
        config = TaskQueueConfig(
            queue_config=QueueConfig(task_queue_name="test", max_task_size=1024, max_queue_length=100),
            persistence_config=PersistenceConfig(),
            coordination_config=CoordinationConfig(),
            security_settings=SecuritySettings(dangerous_patterns=[], max_content_length=1000),
            max_consecutive_failures=3
        )

        manager = TaskQueueManager(config, None)
        manager.task_deduplication = None
        manager.idempotent_processor = None
        manager.priority_scheduler = None

        # Test various operations
        result = await manager.process_task_with_protection(task_context)
        assert result["error"] == "Task deduplication not available"

        result = await manager.enqueue_task_with_priority(task_context)
        assert result["error"] == "Priority scheduler not available"

        result = await manager.get_next_priority_task()
        assert result["error"] == "Priority scheduler not available"

        result = await manager.invalidate_task_idempotency(task_context)
        assert result["error"] == "Idempotent processor not available"

    def test_task_protection_components_not_none(self, task_queue_manager):
        """Test that task protection components are not None after initialization."""
        assert task_queue_manager.task_deduplication is not None
        assert task_queue_manager.idempotent_processor is not None
        assert task_queue_manager.priority_scheduler is not None

    @pytest.mark.asyncio
    async def test_process_task_without_idempotent_processor(self, task_queue_manager, task_context):
        """Test task processing when idempotent processor is not available."""
        # Mock successful claim
        mock_claim = Mock()
        mock_claim.claim_key = "test_claim_123"

        task_queue_manager.task_deduplication.is_task_already_processed = AsyncMock(return_value=False)
        task_queue_manager.task_deduplication.claim_task_for_processing = AsyncMock(return_value=mock_claim)
        task_queue_manager.task_deduplication.complete_task_processing = AsyncMock()

        # Remove idempotent processor to test fallback
        task_queue_manager.idempotent_processor = None

        result = await task_queue_manager.process_task_with_protection(task_context)

        # Verify fallback behavior worked
        assert result["success"] is True
        assert result["protection_features"]["idempotency"] is False

        # Verify deduplication still worked
        task_queue_manager.task_deduplication.complete_task_processing.assert_called_once()