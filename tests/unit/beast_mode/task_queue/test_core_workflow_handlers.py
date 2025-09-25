"""
Unit tests for core workflow transition handlers

Tests the specific transition handlers for the core workflow:
IDLE → HOOK_TRIGGERED → TASK_PENDING → STATE_SNAPSHOT → TASK_EXECUTING → TASK_COMPLETE → STATE_PERSIST → CLEANUP_TEMP → IDLE
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
import uuid

from src.beast_mode.task_queue.models import (
    ConversationState,
    StateTransitionTrigger,
    ConversationContext,
    TaskContext,
    HookEvent,
    StateCheckpoint,
    TaskState,
)
from src.beast_mode.task_queue.state_machine import ConversationStateMachine


class TestCoreWorkflowHandlers:
    """Test suite for core workflow transition handlers."""
    
    @pytest.fixture
    def conversation_context(self):
        """Create a test conversation context."""
        return ConversationContext(
            conversation_id="test-conversation-001",
            instance_id="test-instance-001"
        )
    
    @pytest.fixture
    def mock_persistence_manager(self):
        """Create a mock persistence manager."""
        mock = AsyncMock()
        mock.create_checkpoint.return_value = StateCheckpoint(
            checkpoint_id="test-checkpoint-001",
            conversation_id="test-conversation-001"
        )
        mock.persist_conversation_state.return_value = True
        mock.rollback_to_checkpoint.return_value = True
        return mock
    
    @pytest.fixture
    def state_machine(self, conversation_context, mock_persistence_manager):
        """Create a ConversationStateMachine instance."""
        return ConversationStateMachine(conversation_context, mock_persistence_manager)
    
    @pytest.mark.asyncio
    async def test_hook_triggered_handler(self, state_machine):
        """Test _transition_to_hook_triggered handler."""
        hook_event = HookEvent(
            event_type="file_save",
            event_data={"file_path": "/test/file.py", "user": "test_user"}
        )
        
        # Call handler directly
        success = await state_machine._transition_to_hook_triggered(hook_event=hook_event)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.HOOK_TRIGGERED
        assert state_machine.context.previous_state == ConversationState.IDLE
        
        # Check hook event metadata
        assert "last_hook_event" in state_machine.context.conversation_metadata
        hook_metadata = state_machine.context.conversation_metadata["last_hook_event"]
        assert hook_metadata["event_type"] == "file_save"
        assert hook_metadata["event_data"]["file_path"] == "/test/file.py"
        assert "timestamp" in hook_metadata
    
    @pytest.mark.asyncio
    async def test_hook_triggered_handler_without_event(self, state_machine):
        """Test _transition_to_hook_triggered handler without hook event."""
        success = await state_machine._transition_to_hook_triggered()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.HOOK_TRIGGERED
        assert state_machine.context.previous_state == ConversationState.IDLE
        assert "last_hook_event" not in state_machine.context.conversation_metadata
    
    @pytest.mark.asyncio
    async def test_task_pending_handler(self, state_machine):
        """Test _transition_to_task_pending handler."""
        state_machine.context.current_state = ConversationState.HOOK_TRIGGERED
        
        task = TaskContext(
            task_id="test-task-001",
            task_type="code_generation",
            task_content="Generate a Python function"
        )
        
        success = await state_machine._transition_to_task_pending(task=task)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.TASK_PENDING
        assert state_machine.context.previous_state == ConversationState.HOOK_TRIGGERED
        assert state_machine.context.current_task == task
        assert task in state_machine.context.task_queue
    
    @pytest.mark.asyncio
    async def test_task_pending_handler_without_task(self, state_machine):
        """Test _transition_to_task_pending handler without task."""
        state_machine.context.current_state = ConversationState.HOOK_TRIGGERED
        
        success = await state_machine._transition_to_task_pending()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.TASK_PENDING
        assert state_machine.context.current_task is None
        assert len(state_machine.context.task_queue) == 0
    
    @pytest.mark.asyncio
    async def test_state_snapshot_handler_success(self, state_machine, mock_persistence_manager):
        """Test _transition_to_state_snapshot handler with successful checkpoint creation."""
        state_machine.context.current_state = ConversationState.TASK_PENDING
        
        success = await state_machine._transition_to_state_snapshot()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.STATE_SNAPSHOT
        assert state_machine.context.previous_state == ConversationState.TASK_PENDING
        
        # Verify checkpoint was created and stored
        mock_persistence_manager.create_checkpoint.assert_called_once_with(state_machine.context)
        assert len(state_machine.context.checkpoints) == 1
        assert state_machine.context.checkpoints[0].checkpoint_id == "test-checkpoint-001"
    
    @pytest.mark.asyncio
    async def test_state_snapshot_handler_no_persistence(self, conversation_context):
        """Test _transition_to_state_snapshot handler without persistence manager."""
        state_machine = ConversationStateMachine(conversation_context, None)
        state_machine.context.current_state = ConversationState.TASK_PENDING
        
        success = await state_machine._transition_to_state_snapshot()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.STATE_SNAPSHOT
        assert len(state_machine.context.checkpoints) == 0
    
    @pytest.mark.asyncio
    async def test_task_executing_handler(self, state_machine):
        """Test _transition_to_task_executing handler."""
        state_machine.context.current_state = ConversationState.STATE_SNAPSHOT
        
        task = TaskContext(task_id="test-task-001", task_state=TaskState.VALIDATED)
        state_machine.context.current_task = task
        
        success = await state_machine._transition_to_task_executing()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.TASK_EXECUTING
        assert state_machine.context.previous_state == ConversationState.STATE_SNAPSHOT
        
        # Check task state updates
        assert task.execution_start is not None
        assert task.task_state == TaskState.EXECUTING
    
    @pytest.mark.asyncio
    async def test_task_executing_handler_no_task(self, state_machine):
        """Test _transition_to_task_executing handler without current task."""
        state_machine.context.current_state = ConversationState.STATE_SNAPSHOT
        state_machine.context.current_task = None
        
        success = await state_machine._transition_to_task_executing()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.TASK_EXECUTING
    
    @pytest.mark.asyncio
    async def test_task_complete_handler(self, state_machine):
        """Test _transition_to_task_complete handler."""
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        
        task = TaskContext(task_id="test-task-001", task_state=TaskState.EXECUTING)
        task.execution_start = datetime.now()
        state_machine.context.current_task = task
        
        success = await state_machine._transition_to_task_complete()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.TASK_COMPLETE
        assert state_machine.context.previous_state == ConversationState.TASK_EXECUTING
        
        # Check task state updates
        assert task.execution_end is not None
        assert task.task_state == TaskState.COMPLETED
        assert task.execution_end > task.execution_start
    
    @pytest.mark.asyncio
    async def test_state_persist_handler_success(self, state_machine, mock_persistence_manager):
        """Test _transition_to_state_persist handler with successful persistence."""
        state_machine.context.current_state = ConversationState.TASK_COMPLETE
        state_machine.context.dirty_state = True
        
        success = await state_machine._transition_to_state_persist()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.STATE_PERSIST
        assert state_machine.context.previous_state == ConversationState.TASK_COMPLETE
        
        # Verify persistence was called and state updated
        mock_persistence_manager.persist_conversation_state.assert_called_once_with(state_machine.context)
        assert state_machine.context.last_persistence is not None
        assert state_machine.context.dirty_state is False
    
    @pytest.mark.asyncio
    async def test_state_persist_handler_no_persistence(self, conversation_context):
        """Test _transition_to_state_persist handler without persistence manager."""
        state_machine = ConversationStateMachine(conversation_context, None)
        state_machine.context.current_state = ConversationState.TASK_COMPLETE
        
        success = await state_machine._transition_to_state_persist()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.STATE_PERSIST
    
    @pytest.mark.asyncio
    async def test_cleanup_temp_handler(self, state_machine):
        """Test _transition_to_cleanup_temp handler."""
        state_machine.context.current_state = ConversationState.STATE_PERSIST
        
        # Set up a completed task
        task = TaskContext(
            task_id="test-task-001",
            task_state=TaskState.COMPLETED,
            execution_start=datetime.now(),
            execution_end=datetime.now()
        )
        state_machine.context.current_task = task
        
        success = await state_machine._transition_to_cleanup_temp()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.CLEANUP_TEMP
        assert state_machine.context.previous_state == ConversationState.STATE_PERSIST
        
        # Check task was moved to completed tasks
        assert len(state_machine.context.completed_tasks) == 1
        assert state_machine.context.completed_tasks[0].task_id == "test-task-001"
        assert state_machine.context.completed_tasks[0].success is True
        assert state_machine.context.current_task is None
    
    @pytest.mark.asyncio
    async def test_cleanup_temp_handler_no_task(self, state_machine):
        """Test _transition_to_cleanup_temp handler without current task."""
        state_machine.context.current_state = ConversationState.STATE_PERSIST
        state_machine.context.current_task = None
        
        success = await state_machine._transition_to_cleanup_temp()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.CLEANUP_TEMP
        assert len(state_machine.context.completed_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_idle_handler(self, state_machine):
        """Test _transition_to_idle handler."""
        state_machine.context.current_state = ConversationState.CLEANUP_TEMP
        
        success = await state_machine._transition_to_idle()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.IDLE
        assert state_machine.context.previous_state == ConversationState.CLEANUP_TEMP
    
    @pytest.mark.asyncio
    async def test_complete_success_workflow_integration(self, state_machine, mock_persistence_manager):
        """Test complete successful workflow through all handlers."""
        # Start with hook event
        hook_event = HookEvent(event_type="test_hook")
        success = await state_machine._transition_to_hook_triggered(hook_event=hook_event)
        assert success and state_machine.context.current_state == ConversationState.HOOK_TRIGGERED
        
        # Add task
        task = TaskContext(task_id="test-task-001", task_type="test")
        success = await state_machine._transition_to_task_pending(task=task)
        assert success and state_machine.context.current_state == ConversationState.TASK_PENDING
        
        # Create snapshot
        success = await state_machine._transition_to_state_snapshot()
        assert success and state_machine.context.current_state == ConversationState.STATE_SNAPSHOT
        
        # Start execution
        success = await state_machine._transition_to_task_executing()
        assert success and state_machine.context.current_state == ConversationState.TASK_EXECUTING
        
        # Complete task
        success = await state_machine._transition_to_task_complete()
        assert success and state_machine.context.current_state == ConversationState.TASK_COMPLETE
        
        # Persist state
        success = await state_machine._transition_to_state_persist()
        assert success and state_machine.context.current_state == ConversationState.STATE_PERSIST
        
        # Cleanup
        success = await state_machine._transition_to_cleanup_temp()
        assert success and state_machine.context.current_state == ConversationState.CLEANUP_TEMP
        
        # Return to idle
        success = await state_machine._transition_to_idle()
        assert success and state_machine.context.current_state == ConversationState.IDLE
        
        # Verify final state
        assert len(state_machine.context.completed_tasks) == 1
        assert state_machine.context.current_task is None
        assert len(state_machine.context.checkpoints) == 1
        assert state_machine.context.last_persistence is not None
        assert state_machine.context.dirty_state is False
    
    @pytest.mark.asyncio
    async def test_workflow_with_timing_verification(self, state_machine, mock_persistence_manager):
        """Test workflow with timing verification for task execution."""
        # Set up task with timing
        task = TaskContext(task_id="test-task-001")
        state_machine.context.current_task = task
        state_machine.context.current_state = ConversationState.STATE_SNAPSHOT
        
        # Start execution
        start_time = datetime.now()
        success = await state_machine._transition_to_task_executing()
        assert success
        assert task.execution_start >= start_time
        
        # Complete execution
        success = await state_machine._transition_to_task_complete()
        assert success
        assert task.execution_end >= task.execution_start
        
        # Verify timing consistency
        execution_duration = (task.execution_end - task.execution_start).total_seconds()
        assert execution_duration >= 0