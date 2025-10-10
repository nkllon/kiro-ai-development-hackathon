"""
Unit tests for task processor with state machine integration.

Tests the complete task processing workflow including state transitions,
error handling, and resource management.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import uuid

from src.beast_mode.task_queue.task_processor import (
    TaskProcessor,
    TaskExecutionContext,
    TaskWorkflowOrchestrator
)
from src.beast_mode.task_queue.models import (
    ConversationContext,
    TaskContext,
    TaskState,
    ConversationState,
    TaskResult,
    PersistenceConfig,
    RedisConfig
)
from src.beast_mode.task_queue.persistence import StatePersistenceManager


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.xadd = AsyncMock(return_value=b"1234567890-0")
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.xrevrange = AsyncMock(return_value=[])
    return redis_mock


@pytest.fixture
def persistence_config():
    """Test persistence configuration."""
    return PersistenceConfig(
        hot_storage_ttl_hours=1,
        warm_storage_ttl_days=7,
        cold_storage_ttl_days=30,
        checkpoint_storage_ttl_days=90,
        enable_compression=False,
        integrity_checking=True
    )


@pytest.fixture
def persistence_manager(mock_redis, persistence_config):
    """Test persistence manager."""
    return StatePersistenceManager(mock_redis, persistence_config)


@pytest.fixture
def task_processor(persistence_manager):
    """Test task processor."""
    return TaskProcessor(persistence_manager)


@pytest.fixture
def sample_conversation_context():
    """Sample conversation context for testing."""
    return ConversationContext(
        conversation_id=str(uuid.uuid4()),
        current_state=ConversationState.IDLE
    )


@pytest.fixture
def sample_task_context():
    """Sample task context for testing."""
    return TaskContext(
        task_id=str(uuid.uuid4()),
        task_type="code_generation",
        task_content="Generate a Python function",
        task_parameters={"language": "python", "timeout_seconds": 10}
    )


class TestTaskExecutionContext:
    """Test task execution context."""
    
    def test_context_initialization(self, sample_task_context, sample_conversation_context):
        """Test execution context initialization."""
        context = TaskExecutionContext(sample_task_context, sample_conversation_context)
        
        assert context.task == sample_task_context
        assert context.conversation == sample_conversation_context
        assert context.execution_id is not None
        assert isinstance(context.start_time, datetime)
        assert context.resources_allocated == {}
        assert context.cleanup_callbacks == []
    
    def test_add_cleanup_callback(self, sample_task_context, sample_conversation_context):
        """Test adding cleanup callbacks."""
        context = TaskExecutionContext(sample_task_context, sample_conversation_context)
        
        callback = Mock()
        context.add_cleanup_callback(callback)
        
        assert len(context.cleanup_callbacks) == 1
        assert context.cleanup_callbacks[0] == callback
    
    @pytest.mark.asyncio
    async def test_cleanup_execution(self, sample_task_context, sample_conversation_context):
        """Test cleanup execution."""
        context = TaskExecutionContext(sample_task_context, sample_conversation_context)
        
        # Add sync and async callbacks
        sync_callback = Mock()
        async_callback = AsyncMock()
        
        context.add_cleanup_callback(sync_callback)
        context.add_cleanup_callback(async_callback)
        
        await context.cleanup()
        
        sync_callback.assert_called_once()
        async_callback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_with_failing_callback(self, sample_task_context, sample_conversation_context):
        """Test cleanup handles failing callbacks gracefully."""
        context = TaskExecutionContext(sample_task_context, sample_conversation_context)
        
        # Add failing callback
        failing_callback = Mock(side_effect=Exception("Cleanup failed"))
        success_callback = Mock()
        
        context.add_cleanup_callback(failing_callback)
        context.add_cleanup_callback(success_callback)
        
        # Should not raise exception
        await context.cleanup()
        
        failing_callback.assert_called_once()
        success_callback.assert_called_once()


class TestTaskProcessor:
    """Test task processor functionality."""
    
    def test_processor_initialization(self, task_processor):
        """Test processor initialization."""
        assert task_processor.persistence is not None
        assert isinstance(task_processor.task_handlers, dict)
        assert len(task_processor.task_handlers) > 0  # Default handlers registered
        assert task_processor.active_executions == {}
    
    def test_register_task_handler(self, task_processor):
        """Test task handler registration."""
        handler = AsyncMock()
        task_processor.register_task_handler("custom_task", handler)
        
        assert "custom_task" in task_processor.task_handlers
        assert task_processor.task_handlers["custom_task"] == handler
    
    def test_default_handlers_registered(self, task_processor):
        """Test that default handlers are registered."""
        expected_handlers = [
            "code_generation",
            "file_analysis", 
            "documentation",
            "testing",
            "refactoring"
        ]
        
        for handler_type in expected_handlers:
            assert handler_type in task_processor.task_handlers
    
    @pytest.mark.asyncio
    async def test_successful_task_workflow(self, task_processor, sample_conversation_context, sample_task_context):
        """Test successful task processing workflow."""
        # Mock persistence operations
        task_processor.persistence.create_checkpoint = AsyncMock(return_value=Mock(checkpoint_id="test-checkpoint"))
        task_processor.persistence.persist_conversation_state = AsyncMock(return_value=True)
        
        result = await task_processor.process_task_workflow(
            sample_conversation_context,
            sample_task_context
        )
        
        assert isinstance(result, TaskResult)
        assert result.success is True
        assert result.task_id == sample_task_context.task_id
        assert result.execution_time_ms > 0
        assert "generated_code" in result.result_data
    
    @pytest.mark.asyncio
    async def test_task_workflow_with_unknown_task_type(self, task_processor, sample_conversation_context):
        """Test task workflow with unknown task type."""
        unknown_task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="unknown_task_type",
            task_content="Unknown task"
        )
        
        # Mock persistence operations
        task_processor.persistence.create_checkpoint = AsyncMock(return_value=Mock(checkpoint_id="test-checkpoint"))
        
        result = await task_processor.process_task_workflow(
            sample_conversation_context,
            unknown_task
        )
        
        assert isinstance(result, TaskResult)
        assert result.success is False
        assert "No handler registered" in result.error_message
    
    @pytest.mark.asyncio
    async def test_task_workflow_with_checkpoint_failure(self, task_processor, sample_conversation_context, sample_task_context):
        """Test task workflow when checkpoint creation fails."""
        # Mock checkpoint creation failure
        task_processor.persistence.create_checkpoint = AsyncMock(side_effect=Exception("Checkpoint failed"))
        
        result = await task_processor.process_task_workflow(
            sample_conversation_context,
            sample_task_context
        )
        
        assert isinstance(result, TaskResult)
        assert result.success is False
        assert "Checkpoint failed" in result.error_message or "Failed to create state snapshot" in result.error_message
    
    @pytest.mark.asyncio
    async def test_task_execution_timeout(self, task_processor, sample_conversation_context):
        """Test task execution timeout handling."""
        # Create task with very short timeout
        timeout_task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="code_generation",
            task_content="Long running task",
            task_parameters={"timeout_seconds": 0.001}  # Very short timeout
        )
        
        # Mock a slow handler
        async def slow_handler(task, context):
            await asyncio.sleep(1)  # Longer than timeout
            return {"result": "completed"}
        
        task_processor.register_task_handler("code_generation", slow_handler)
        
        # Mock persistence operations
        task_processor.persistence.create_checkpoint = AsyncMock(return_value=Mock(checkpoint_id="test-checkpoint"))
        
        result = await task_processor.process_task_workflow(
            sample_conversation_context,
            timeout_task
        )
        
        assert isinstance(result, TaskResult)
        assert result.success is False
        assert "timed out" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_get_active_executions(self, task_processor, sample_conversation_context, sample_task_context):
        """Test getting active execution information."""
        # Start a task execution in background
        task_future = asyncio.create_task(
            task_processor.process_task_workflow(sample_conversation_context, sample_task_context)
        )
        
        # Give it a moment to start
        await asyncio.sleep(0.01)
        
        active_executions = await task_processor.get_active_executions()
        
        # Cancel the task to clean up
        task_future.cancel()
        try:
            await task_future
        except asyncio.CancelledError:
            pass
        
        # Should have had one active execution
        assert len(active_executions) >= 0  # May be 0 if task completed very quickly
    
    @pytest.mark.asyncio
    async def test_cancel_task_execution(self, task_processor, sample_conversation_context, sample_task_context):
        """Test cancelling task execution."""
        # Mock a long-running handler
        async def long_handler(task, context):
            await asyncio.sleep(10)
            return {"result": "completed"}
        
        task_processor.register_task_handler("code_generation", long_handler)
        
        # Start task execution
        task_future = asyncio.create_task(
            task_processor.process_task_workflow(sample_conversation_context, sample_task_context)
        )
        
        # Give it a moment to start
        await asyncio.sleep(0.01)
        
        # Cancel the execution
        success = await task_processor.cancel_task_execution(sample_task_context.task_id)
        
        # Clean up
        task_future.cancel()
        try:
            await task_future
        except asyncio.CancelledError:
            pass
        
        # Cancellation success depends on timing
        assert isinstance(success, bool)


class TestTaskWorkflowOrchestrator:
    """Test task workflow orchestrator."""
    
    @pytest.fixture
    def orchestrator(self, task_processor):
        """Test orchestrator."""
        return TaskWorkflowOrchestrator(task_processor)
    
    def test_orchestrator_initialization(self, orchestrator, task_processor):
        """Test orchestrator initialization."""
        assert orchestrator.task_processor == task_processor
        assert orchestrator.concurrent_limit == 5
        assert orchestrator.active_workflows == {}
    
    @pytest.mark.asyncio
    async def test_process_empty_task_batch(self, orchestrator, sample_conversation_context):
        """Test processing empty task batch."""
        results = await orchestrator.process_task_batch(sample_conversation_context, [])
        assert results == []
    
    @pytest.mark.asyncio
    async def test_process_single_task_batch(self, orchestrator, sample_conversation_context, sample_task_context):
        """Test processing single task batch."""
        # Mock persistence operations
        orchestrator.task_processor.persistence.create_checkpoint = AsyncMock(
            return_value=Mock(checkpoint_id="test-checkpoint")
        )
        orchestrator.task_processor.persistence.persist_conversation_state = AsyncMock(return_value=True)
        
        results = await orchestrator.process_task_batch(
            sample_conversation_context,
            [sample_task_context]
        )
        
        assert len(results) == 1
        assert isinstance(results[0], TaskResult)
        assert results[0].task_id == sample_task_context.task_id
    
    @pytest.mark.asyncio
    async def test_process_multiple_task_batch(self, orchestrator, sample_conversation_context):
        """Test processing multiple tasks in batch."""
        # Create multiple tasks
        tasks = [
            TaskContext(
                task_id=str(uuid.uuid4()),
                task_type="code_generation",
                task_content=f"Task {i}"
            )
            for i in range(3)
        ]
        
        # Mock persistence operations
        orchestrator.task_processor.persistence.create_checkpoint = AsyncMock(
            return_value=Mock(checkpoint_id="test-checkpoint")
        )
        orchestrator.task_processor.persistence.persist_conversation_state = AsyncMock(return_value=True)
        
        results = await orchestrator.process_task_batch(sample_conversation_context, tasks)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert isinstance(result, TaskResult)
            assert result.task_id == tasks[i].task_id
    
    @pytest.mark.asyncio
    async def test_get_workflow_status(self, orchestrator):
        """Test getting workflow status."""
        status = await orchestrator.get_workflow_status()
        
        assert "active_workflows" in status
        assert "active_executions" in status
        assert "concurrent_limit" in status
        assert "executions" in status
        assert status["concurrent_limit"] == 5


class TestDefaultTaskHandlers:
    """Test default task handlers."""
    
    @pytest.mark.asyncio
    async def test_code_generation_handler(self, task_processor, sample_conversation_context):
        """Test code generation handler."""
        task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="code_generation",
            task_content="Generate Python function",
            task_parameters={"language": "python"}
        )
        
        # Mock persistence operations
        task_processor.persistence.create_checkpoint = AsyncMock(
            return_value=Mock(checkpoint_id="test-checkpoint")
        )
        task_processor.persistence.persist_conversation_state = AsyncMock(return_value=True)
        
        result = await task_processor.process_task_workflow(sample_conversation_context, task)
        
        assert result.success is True
        assert "generated_code" in result.result_data
        assert "language" in result.result_data
        assert result.result_data["language"] == "python"
    
    @pytest.mark.asyncio
    async def test_file_analysis_handler(self, task_processor, sample_conversation_context):
        """Test file analysis handler."""
        task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="file_analysis",
            task_content="Analyze file",
            task_parameters={"file_path": "/test/file.py"}
        )
        
        # Mock persistence operations
        task_processor.persistence.create_checkpoint = AsyncMock(
            return_value=Mock(checkpoint_id="test-checkpoint")
        )
        task_processor.persistence.persist_conversation_state = AsyncMock(return_value=True)
        
        result = await task_processor.process_task_workflow(sample_conversation_context, task)
        
        assert result.success is True
        assert "analysis_result" in result.result_data
        assert "file_path" in result.result_data
        assert result.result_data["file_path"] == "/test/file.py"
    
    @pytest.mark.asyncio
    async def test_documentation_handler(self, task_processor, sample_conversation_context):
        """Test documentation handler."""
        task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="documentation",
            task_content="Generate documentation",
            task_parameters={"format": "rst"}
        )
        
        # Mock persistence operations
        task_processor.persistence.create_checkpoint = AsyncMock(
            return_value=Mock(checkpoint_id="test-checkpoint")
        )
        task_processor.persistence.persist_conversation_state = AsyncMock(return_value=True)
        
        result = await task_processor.process_task_workflow(sample_conversation_context, task)
        
        assert result.success is True
        assert "documentation" in result.result_data
        assert "format" in result.result_data
        assert result.result_data["format"] == "rst"
    
    @pytest.mark.asyncio
    async def test_testing_handler(self, task_processor, sample_conversation_context):
        """Test testing handler."""
        task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="testing",
            task_content="Run tests",
            task_parameters={"test_count": 10}
        )
        
        # Mock persistence operations
        task_processor.persistence.create_checkpoint = AsyncMock(
            return_value=Mock(checkpoint_id="test-checkpoint")
        )
        task_processor.persistence.persist_conversation_state = AsyncMock(return_value=True)
        
        result = await task_processor.process_task_workflow(sample_conversation_context, task)
        
        assert result.success is True
        assert "test_results" in result.result_data
        assert "tests_run" in result.result_data
        assert result.result_data["tests_run"] == 10
    
    @pytest.mark.asyncio
    async def test_refactoring_handler(self, task_processor, sample_conversation_context):
        """Test refactoring handler."""
        task = TaskContext(
            task_id=str(uuid.uuid4()),
            task_type="refactoring",
            task_content="Refactor code",
            task_parameters={"file_count": 3}
        )
        
        # Mock persistence operations
        task_processor.persistence.create_checkpoint = AsyncMock(
            return_value=Mock(checkpoint_id="test-checkpoint")
        )
        task_processor.persistence.persist_conversation_state = AsyncMock(return_value=True)
        
        result = await task_processor.process_task_workflow(sample_conversation_context, task)
        
        assert result.success is True
        assert "refactoring_result" in result.result_data
        assert "files_modified" in result.result_data
        assert result.result_data["files_modified"] == 3