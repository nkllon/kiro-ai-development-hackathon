"""
Unit tests for Redis task queue operations

Tests Redis Streams operations, task validation, security,
and priority queue management with real Redis integration scenarios.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json
import uuid

from src.beast_mode.task_queue.models import (
    TaskContext,
    TaskState,
    QueueConfig,
    SecuritySettings,
    RetryPolicy,
)
from src.beast_mode.task_queue.redis_operations import (
    RedisTaskQueueOperations,
    TaskQueuePriorityManager,
    TaskValidationError,
)


class TestRedisTaskQueueOperations:
    """Test suite for RedisTaskQueueOperations."""
    
    @pytest.fixture
    def security_settings(self):
        """Create test security settings."""
        return SecuritySettings(
            validate_task_content=True,
            sanitize_inputs=True,
            max_payload_size_bytes=1048576,  # 1MB
            allowed_task_types=["code_generation", "file_analysis", "documentation"],
            dangerous_patterns=[r'eval\s*\(', r'exec\s*\(', r'subprocess\.', r'os\.system']
        )
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock = AsyncMock()
        mock.xadd.return_value = b"1234567890-0"
        mock.xreadgroup.return_value = []
        mock.xrevrange.return_value = []
        mock.xack.return_value = 1
        mock.xinfo_stream.return_value = {b'length': 5, b'first-entry': [b'1234567890-0'], b'last-entry': [b'1234567890-4']}
        mock.xinfo_groups.return_value = []
        mock.xpending_range.return_value = []
        mock.xclaim.return_value = []
        mock.xgroup_create.return_value = True
        return mock
    
    @pytest.fixture
    def redis_operations(self, mock_redis, security_settings):
        """Create RedisTaskQueueOperations instance."""
        return RedisTaskQueueOperations(mock_redis, security_settings)
    
    @pytest.fixture
    def sample_task(self):
        """Create sample task for testing."""
        return TaskContext(
            task_id="test-task-001",
            task_type="code_generation",
            task_content="Generate a Python function to calculate fibonacci numbers",
            task_parameters={"language": "python", "style": "recursive"},
            task_metadata={"priority": "high", "user_id": "user-123"},
            created_at=datetime.now(),
            task_state=TaskState.QUEUED
        )
    
    @pytest.mark.asyncio
    async def test_enqueue_task_success(self, redis_operations, sample_task, mock_redis):
        """Test successful task enqueuing."""
        queue_name = "high_priority"
        
        success = await redis_operations.enqueue_task(queue_name, sample_task)
        
        assert success is True
        
        # Verify Redis operations
        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args[0]
        assert call_args[0] == f"task_queue:{queue_name}"
        
        # Verify task metadata was updated
        assert "redis_message_id" in sample_task.task_metadata
        assert "queue_name" in sample_task.task_metadata
        assert "enqueued_at" in sample_task.task_metadata
        assert sample_task.task_metadata["queue_name"] == queue_name
    
    @pytest.mark.asyncio
    async def test_enqueue_task_security_validation_failure(self, redis_operations, sample_task):
        """Test task enqueuing with security validation failure."""
        # Create task with disallowed type
        sample_task.task_type = "malicious_code"
        
        success = await redis_operations.enqueue_task("test_queue", sample_task)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_enqueue_task_dangerous_content(self, redis_operations, sample_task):
        """Test task enqueuing with dangerous content patterns."""
        # Add dangerous content
        sample_task.task_content = "Please execute this: eval('malicious code')"
        
        success = await redis_operations.enqueue_task("test_queue", sample_task)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_enqueue_task_payload_too_large(self, redis_operations, sample_task):
        """Test task enqueuing with payload exceeding size limit."""
        # Create large payload
        large_content = "x" * (2 * 1024 * 1024)  # 2MB content
        sample_task.task_content = large_content
        
        success = await redis_operations.enqueue_task("test_queue", sample_task)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_dequeue_task_success(self, redis_operations, sample_task, mock_redis):
        """Test successful task dequeuing."""
        queue_name = "test_queue"
        consumer_group = "test_group"
        consumer_name = "test_consumer"
        
        # Mock Redis response
        serialized_task = redis_operations._serialize_task(sample_task)
        mock_redis.xreadgroup.return_value = [
            [b"task_queue:test_queue", [[b"1234567890-0", serialized_task]]]
        ]
        
        task = await redis_operations.dequeue_task(queue_name, consumer_group, consumer_name)
        
        assert task is not None
        assert task.task_id == sample_task.task_id
        assert task.task_state == TaskState.CLAIMED
        assert task.claimed_at is not None
        assert "redis_message_id" in task.task_metadata
        assert "consumer_group" in task.task_metadata
        assert "consumer_name" in task.task_metadata
        assert "dequeued_at" in task.task_metadata
        
        # Verify Redis operations
        mock_redis.xreadgroup.assert_called_once()
        mock_redis.xgroup_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_dequeue_task_no_messages(self, redis_operations, mock_redis):
        """Test task dequeuing when no messages available."""
        # Mock empty response
        mock_redis.xreadgroup.return_value = [[b"task_queue:test_queue", []]]
        
        task = await redis_operations.dequeue_task("test_queue", "test_group", "test_consumer")
        
        assert task is None
    
    @pytest.mark.asyncio
    async def test_peek_queue(self, redis_operations, sample_task, mock_redis):
        """Test peeking at queue contents."""
        queue_name = "test_queue"
        
        # Mock Redis response
        serialized_task = redis_operations._serialize_task(sample_task)
        mock_redis.xrevrange.return_value = [
            [b"1234567890-0", serialized_task],
            [b"1234567890-1", serialized_task]
        ]
        
        tasks = await redis_operations.peek_queue(queue_name, count=10)
        
        assert len(tasks) == 2
        assert all(task.task_id == sample_task.task_id for task in tasks)
        assert all("redis_message_id" in task.task_metadata for task in tasks)
        
        # Verify Redis operations
        mock_redis.xrevrange.assert_called_once_with(f"task_queue:{queue_name}", count=10)
    
    @pytest.mark.asyncio
    async def test_acknowledge_task_success(self, redis_operations, mock_redis):
        """Test successful task acknowledgment."""
        queue_name = "test_queue"
        consumer_group = "test_group"
        message_id = "1234567890-0"
        
        # Mock successful acknowledgment
        mock_redis.xack.return_value = 1
        
        success = await redis_operations.acknowledge_task(queue_name, consumer_group, message_id)
        
        assert success is True
        mock_redis.xack.assert_called_once_with(f"task_queue:{queue_name}", consumer_group, message_id)
    
    @pytest.mark.asyncio
    async def test_acknowledge_task_failure(self, redis_operations, mock_redis):
        """Test task acknowledgment failure."""
        queue_name = "test_queue"
        consumer_group = "test_group"
        message_id = "1234567890-0"
        
        # Mock failed acknowledgment
        mock_redis.xack.return_value = 0
        
        success = await redis_operations.acknowledge_task(queue_name, consumer_group, message_id)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_queue_info(self, redis_operations, mock_redis):
        """Test getting queue information."""
        queue_name = "test_queue"
        
        # Mock Redis responses
        mock_redis.xinfo_stream.return_value = {
            b'length': 10,
            b'first-entry': [b'1234567890-0', {}],
            b'last-entry': [b'1234567890-9', {}]
        }
        mock_redis.xinfo_groups.return_value = [
            {
                b'name': b'test_group',
                b'consumers': 2,
                b'pending': 5,
                b'last-delivered-id': b'1234567890-5'
            }
        ]
        
        queue_info = await redis_operations.get_queue_info(queue_name)
        
        assert queue_info["queue_name"] == queue_name
        assert queue_info["length"] == 10
        assert queue_info["first_entry_id"] == "1234567890-0"
        assert queue_info["last_entry_id"] == "1234567890-9"
        assert len(queue_info["consumer_groups"]) == 1
        assert queue_info["consumer_groups"][0]["name"] == "test_group"
        assert queue_info["consumer_groups"][0]["consumers"] == 2
        assert queue_info["consumer_groups"][0]["pending"] == 5
    
    @pytest.mark.asyncio
    async def test_get_pending_tasks(self, redis_operations, mock_redis):
        """Test getting pending tasks for consumer group."""
        queue_name = "test_queue"
        consumer_group = "test_group"
        consumer_name = "test_consumer"
        
        # Mock Redis response
        mock_redis.xpending_range.return_value = [
            [b"1234567890-0", b"test_consumer", 30000, 1],
            [b"1234567890-1", b"test_consumer", 60000, 2]
        ]
        
        pending_tasks = await redis_operations.get_pending_tasks(queue_name, consumer_group, consumer_name)
        
        assert len(pending_tasks) == 2
        assert pending_tasks[0]["message_id"] == "1234567890-0"
        assert pending_tasks[0]["consumer"] == "test_consumer"
        assert pending_tasks[0]["idle_time_ms"] == 30000
        assert pending_tasks[0]["delivery_count"] == 1
    
    @pytest.mark.asyncio
    async def test_claim_abandoned_tasks(self, redis_operations, sample_task, mock_redis):
        """Test claiming abandoned tasks."""
        queue_name = "test_queue"
        consumer_group = "test_group"
        consumer_name = "new_consumer"
        
        # Mock pending tasks response
        mock_redis.xpending_range.return_value = [
            [b"1234567890-0", b"old_consumer", 120000, 1]  # Idle for 2 minutes
        ]
        
        # Mock claim response
        serialized_task = redis_operations._serialize_task(sample_task)
        mock_redis.xclaim.return_value = [[b"1234567890-0", serialized_task]]
        
        claimed_tasks = await redis_operations.claim_abandoned_tasks(
            queue_name, consumer_group, consumer_name, min_idle_time_ms=60000
        )
        
        assert len(claimed_tasks) == 1
        assert claimed_tasks[0].task_id == sample_task.task_id
        assert "claimed_from_abandoned" in claimed_tasks[0].task_metadata
        assert "original_consumer" in claimed_tasks[0].task_metadata
        assert "reclaimed_at" in claimed_tasks[0].task_metadata
        assert claimed_tasks[0].task_metadata["original_consumer"] == "old_consumer"
    
    def test_serialize_deserialize_task(self, redis_operations, sample_task):
        """Test task serialization and deserialization."""
        # Serialize task
        serialized = redis_operations._serialize_task(sample_task)
        
        assert isinstance(serialized, dict)
        assert all(isinstance(v, str) for v in serialized.values())
        assert serialized["task_id"] == sample_task.task_id
        assert serialized["task_type"] == sample_task.task_type
        
        # Convert to bytes format (as Redis would return)
        redis_fields = {k.encode(): v.encode() for k, v in serialized.items()}
        
        # Deserialize task
        deserialized = redis_operations._deserialize_task(redis_fields)
        
        assert isinstance(deserialized, TaskContext)
        assert deserialized.task_id == sample_task.task_id
        assert deserialized.task_type == sample_task.task_type
        assert deserialized.task_content == sample_task.task_content
        assert deserialized.task_parameters == sample_task.task_parameters
        assert deserialized.task_metadata == sample_task.task_metadata
    
    def test_content_sanitization(self, redis_operations):
        """Test content sanitization functionality."""
        dangerous_content = "Execute this: <script>alert('xss')</script> and eval('malicious')"
        
        sanitized = redis_operations._sanitize_content(dangerous_content)
        
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
        assert "eval(" not in sanitized
        assert "eval_" in sanitized
    
    def test_parameter_sanitization(self, redis_operations):
        """Test parameter sanitization functionality."""
        dangerous_params = {
            "code": "eval('malicious code')",
            "script": "<script>alert('xss')</script>",
            "nested": {
                "command": "exec('rm -rf /')"
            },
            "safe_param": "normal content"
        }
        
        sanitized = redis_operations._sanitize_parameters(dangerous_params)
        
        assert "eval(" not in sanitized["code"]
        assert "eval_" in sanitized["code"]
        assert "<script>" not in sanitized["script"]
        assert "exec(" not in sanitized["nested"]["command"]
        assert sanitized["safe_param"] == "normal content"
    
    @pytest.mark.asyncio
    async def test_security_validation_allowed_task_type(self, redis_operations, sample_task):
        """Test security validation with allowed task type."""
        sample_task.task_type = "code_generation"  # Allowed type
        
        is_valid = await redis_operations._validate_task_security(sample_task)
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_security_validation_disallowed_task_type(self, redis_operations, sample_task):
        """Test security validation with disallowed task type."""
        sample_task.task_type = "system_command"  # Not in allowed list
        
        is_valid = await redis_operations._validate_task_security(sample_task)
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_security_validation_dangerous_patterns(self, redis_operations, sample_task):
        """Test security validation with dangerous patterns."""
        sample_task.task_content = "Please run: subprocess.call(['rm', '-rf', '/'])"
        
        is_valid = await redis_operations._validate_task_security(sample_task)
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_consumer_group_creation(self, redis_operations, mock_redis):
        """Test consumer group creation."""
        stream_key = "task_queue:test"
        consumer_group = "test_group"
        
        await redis_operations._ensure_consumer_group(stream_key, consumer_group)
        
        mock_redis.xgroup_create.assert_called_once_with(
            stream_key, consumer_group, id='0', mkstream=True
        )
    
    @pytest.mark.asyncio
    async def test_consumer_group_already_exists(self, redis_operations, mock_redis):
        """Test consumer group creation when group already exists."""
        stream_key = "task_queue:test"
        consumer_group = "test_group"
        
        # Mock BUSYGROUP error (group already exists)
        mock_redis.xgroup_create.side_effect = Exception("BUSYGROUP Consumer Group name already exists")
        
        # Should not raise exception
        await redis_operations._ensure_consumer_group(stream_key, consumer_group)


class TestTaskQueuePriorityManager:
    """Test suite for TaskQueuePriorityManager."""
    
    @pytest.fixture
    def mock_redis_operations(self):
        """Create mock RedisTaskQueueOperations."""
        return AsyncMock()
    
    @pytest.fixture
    def priority_manager(self, mock_redis_operations):
        """Create TaskQueuePriorityManager instance."""
        return TaskQueuePriorityManager(mock_redis_operations)
    
    @pytest.fixture
    def queue_configs(self):
        """Create test queue configurations with different priorities."""
        return [
            QueueConfig(
                name="low_priority",
                priority=3,
                max_concurrent_tasks=5,
                task_timeout_seconds=300,
                retry_policy=RetryPolicy()
            ),
            QueueConfig(
                name="high_priority",
                priority=1,
                max_concurrent_tasks=10,
                task_timeout_seconds=600,
                retry_policy=RetryPolicy()
            ),
            QueueConfig(
                name="medium_priority",
                priority=2,
                max_concurrent_tasks=7,
                task_timeout_seconds=450,
                retry_policy=RetryPolicy()
            )
        ]
    
    @pytest.fixture
    def sample_task(self):
        """Create sample task for testing."""
        return TaskContext(
            task_id="priority-test-task",
            task_type="code_generation",
            task_content="Test task content"
        )
    
    @pytest.mark.asyncio
    async def test_dequeue_by_priority_high_priority_first(self, priority_manager, queue_configs, sample_task, mock_redis_operations):
        """Test that high priority queues are checked first."""
        consumer_group = "test_group"
        consumer_name = "test_consumer"
        
        # Mock dequeue to return task from high priority queue
        mock_redis_operations.dequeue_task.side_effect = [
            sample_task,  # high_priority queue (priority 1)
            None,         # medium_priority queue (priority 2) - not reached
            None          # low_priority queue (priority 3) - not reached
        ]
        
        result = await priority_manager.dequeue_by_priority(
            queue_configs, consumer_group, consumer_name
        )
        
        assert result is not None
        task, queue_name = result
        assert task == sample_task
        assert queue_name == "high_priority"
        
        # Should only call dequeue for high priority queue
        mock_redis_operations.dequeue_task.assert_called_once_with(
            "high_priority", consumer_group, consumer_name, timeout_ms=100
        )
    
    @pytest.mark.asyncio
    async def test_dequeue_by_priority_fallback_to_lower_priority(self, priority_manager, queue_configs, sample_task, mock_redis_operations):
        """Test fallback to lower priority queues when higher priority queues are empty."""
        consumer_group = "test_group"
        consumer_name = "test_consumer"
        
        # Mock dequeue to return None for high priority, task from medium priority
        mock_redis_operations.dequeue_task.side_effect = [
            None,         # high_priority queue (priority 1) - empty
            sample_task,  # medium_priority queue (priority 2) - has task
            None          # low_priority queue (priority 3) - not reached
        ]
        
        result = await priority_manager.dequeue_by_priority(
            queue_configs, consumer_group, consumer_name
        )
        
        assert result is not None
        task, queue_name = result
        assert task == sample_task
        assert queue_name == "medium_priority"
        
        # Should call dequeue for high and medium priority queues
        assert mock_redis_operations.dequeue_task.call_count == 2
    
    @pytest.mark.asyncio
    async def test_dequeue_by_priority_no_tasks_available(self, priority_manager, queue_configs, mock_redis_operations):
        """Test when no tasks are available in any queue."""
        consumer_group = "test_group"
        consumer_name = "test_consumer"
        
        # Mock dequeue to return None for all queues
        mock_redis_operations.dequeue_task.return_value = None
        
        result = await priority_manager.dequeue_by_priority(
            queue_configs, consumer_group, consumer_name
        )
        
        assert result is None
        
        # Should call dequeue for all queues
        assert mock_redis_operations.dequeue_task.call_count == 3
    
    @pytest.mark.asyncio
    async def test_dequeue_by_priority_queue_error_handling(self, priority_manager, queue_configs, sample_task, mock_redis_operations):
        """Test error handling when queue operations fail."""
        consumer_group = "test_group"
        consumer_name = "test_consumer"
        
        # Mock dequeue to raise exception for first queue, return task from second
        mock_redis_operations.dequeue_task.side_effect = [
            Exception("Redis connection error"),  # high_priority queue - error
            sample_task,                          # medium_priority queue - success
            None                                  # low_priority queue - not reached
        ]
        
        result = await priority_manager.dequeue_by_priority(
            queue_configs, consumer_group, consumer_name
        )
        
        assert result is not None
        task, queue_name = result
        assert task == sample_task
        assert queue_name == "medium_priority"
    
    @pytest.mark.asyncio
    async def test_boost_aged_tasks(self, priority_manager, queue_configs, mock_redis_operations):
        """Test boosting aged tasks to higher priority queues."""
        # Create aged task
        aged_task = TaskContext(
            task_id="aged-task",
            task_type="code_generation",
            created_at=datetime.now() - timedelta(minutes=45)  # 45 minutes old
        )
        
        # Mock peek_queue to return aged task
        mock_redis_operations.peek_queue.return_value = [aged_task]
        
        await priority_manager.boost_aged_tasks(queue_configs, age_threshold_minutes=30)
        
        # Should call peek_queue for all queues
        assert mock_redis_operations.peek_queue.call_count == len(queue_configs)
    
    def test_find_higher_priority_queue(self, priority_manager, queue_configs):
        """Test finding higher priority queue."""
        # Test from low priority queue
        low_priority_queue = queue_configs[0]  # priority 3
        higher_queue = priority_manager._find_higher_priority_queue(low_priority_queue, queue_configs)
        
        assert higher_queue is not None
        assert higher_queue.priority < low_priority_queue.priority
        assert higher_queue.name == "high_priority"  # Should find highest priority
        
        # Test from high priority queue
        high_priority_queue = queue_configs[1]  # priority 1
        higher_queue = priority_manager._find_higher_priority_queue(high_priority_queue, queue_configs)
        
        assert higher_queue is None  # No higher priority available
    
    @pytest.mark.asyncio
    async def test_priority_queue_sorting(self, priority_manager, queue_configs, mock_redis_operations):
        """Test that queues are properly sorted by priority."""
        consumer_group = "test_group"
        consumer_name = "test_consumer"
        
        # Mock dequeue to return None for all queues
        mock_redis_operations.dequeue_task.return_value = None
        
        await priority_manager.dequeue_by_priority(queue_configs, consumer_group, consumer_name)
        
        # Verify queues were called in priority order
        calls = mock_redis_operations.dequeue_task.call_args_list
        assert len(calls) == 3
        
        # Should be called in order: high_priority (1), medium_priority (2), low_priority (3)
        assert calls[0][0][0] == "high_priority"
        assert calls[1][0][0] == "medium_priority"
        assert calls[2][0][0] == "low_priority"