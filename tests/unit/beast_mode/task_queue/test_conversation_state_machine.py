"""
Unit tests for ConversationStateMachine

Tests all valid state transitions, invalid transition rejection,
and state transition handlers with mock dependencies.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from src.beast_mode.task_queue.models import (
    ConversationState,
    StateTransitionTrigger,
    ConversationContext,
    TaskContext,
    HookEvent,
    StateCheckpoint,
)
from src.beast_mode.task_queue.state_machine import ConversationStateMachine


class TestConversationStateMachine:
    """Test suite for ConversationStateMachine."""
    
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
    
    def test_initial_state(self, state_machine):
        """Test that state machine starts in IDLE state."""
        assert state_machine.context.current_state == ConversationState.IDLE
        assert state_machine.context.previous_state is None
        assert len(state_machine.context.state_history) == 0
    
    def test_transition_table_setup(self, state_machine):
        """Test that transition table is properly set up."""
        # Check that transition handlers are defined
        assert len(state_machine.transition_handlers) > 0
        
        # Check some key transitions exist
        assert (ConversationState.IDLE, StateTransitionTrigger.HOOK_EXECUTION) in state_machine.transition_handlers
        assert (ConversationState.TASK_PENDING, StateTransitionTrigger.TASK_START) in state_machine.transition_handlers
        assert (ConversationState.TASK_EXECUTING, StateTransitionTrigger.TASK_SUCCESS) in state_machine.transition_handlers
    
    @pytest.mark.asyncio
    async def test_valid_transition_idle_to_hook_triggered(self, state_machine):
        """Test valid transition from IDLE to HOOK_TRIGGERED."""
        hook_event = HookEvent(event_type="test_hook", event_data={"test": "data"})
        
        success = await state_machine.trigger_transition(
            StateTransitionTrigger.HOOK_EXECUTION,
            hook_event=hook_event
        )
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.HOOK_TRIGGERED
        assert state_machine.context.previous_state == ConversationState.IDLE
        assert len(state_machine.context.state_history) == 1
        assert state_machine.context.dirty_state is True
        assert state_machine.context.state_version == 2
        
        # Check hook event metadata
        assert "last_hook_event" in state_machine.context.conversation_metadata
        assert state_machine.context.conversation_metadata["last_hook_event"]["event_type"] == "test_hook"
    
    @pytest.mark.asyncio
    async def test_valid_transition_hook_triggered_to_task_pending(self, state_machine):
        """Test valid transition from HOOK_TRIGGERED to TASK_PENDING."""
        # First transition to HOOK_TRIGGERED
        await state_machine.trigger_transition(StateTransitionTrigger.HOOK_EXECUTION)
        
        # Create test task
        task = TaskContext(task_id="test-task-001", task_type="test")
        
        success = await state_machine.trigger_transition(
            StateTransitionTrigger.TASK_AVAILABLE,
            task=task
        )
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.TASK_PENDING
        assert state_machine.context.current_task == task
        assert task in state_machine.context.task_queue
    
    @pytest.mark.asyncio
    async def test_valid_transition_task_pending_to_state_snapshot(self, state_machine, mock_persistence_manager):
        """Test valid transition from TASK_PENDING to STATE_SNAPSHOT."""
        # Set up initial state
        state_machine.context.current_state = ConversationState.TASK_PENDING
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_START)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.STATE_SNAPSHOT
        
        # Verify checkpoint was created
        mock_persistence_manager.create_checkpoint.assert_called_once_with(state_machine.context)
        assert len(state_machine.context.checkpoints) == 1
    
    @pytest.mark.asyncio
    async def test_valid_transition_state_snapshot_to_task_executing(self, state_machine):
        """Test valid transition from STATE_SNAPSHOT to TASK_EXECUTING."""
        # Set up initial state with a task
        state_machine.context.current_state = ConversationState.STATE_SNAPSHOT
        task = TaskContext(task_id="test-task-001")
        state_machine.context.current_task = task
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_START)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.TASK_EXECUTING
        assert task.execution_start is not None
        assert task.task_state.name == "EXECUTING"
    
    @pytest.mark.asyncio
    async def test_valid_transition_task_executing_to_task_complete(self, state_machine):
        """Test valid transition from TASK_EXECUTING to TASK_COMPLETE."""
        # Set up initial state with a task
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        task = TaskContext(task_id="test-task-001")
        state_machine.context.current_task = task
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_SUCCESS)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.TASK_COMPLETE
        assert task.execution_end is not None
        assert task.task_state.name == "COMPLETED"
    
    @pytest.mark.asyncio
    async def test_valid_transition_complete_workflow(self, state_machine, mock_persistence_manager):
        """Test complete workflow from IDLE to IDLE through task execution."""
        # IDLE -> HOOK_TRIGGERED
        success = await state_machine.trigger_transition(StateTransitionTrigger.HOOK_EXECUTION)
        assert success and state_machine.context.current_state == ConversationState.HOOK_TRIGGERED
        
        # HOOK_TRIGGERED -> TASK_PENDING
        task = TaskContext(task_id="test-task-001")
        success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_AVAILABLE, task=task)
        assert success and state_machine.context.current_state == ConversationState.TASK_PENDING
        
        # TASK_PENDING -> STATE_SNAPSHOT
        success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_START)
        assert success and state_machine.context.current_state == ConversationState.STATE_SNAPSHOT
        
        # STATE_SNAPSHOT -> TASK_EXECUTING
        success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_START)
        assert success and state_machine.context.current_state == ConversationState.TASK_EXECUTING
        
        # TASK_EXECUTING -> TASK_COMPLETE
        success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_SUCCESS)
        assert success and state_machine.context.current_state == ConversationState.TASK_COMPLETE
        
        # TASK_COMPLETE -> STATE_PERSIST
        success = await state_machine.trigger_transition(StateTransitionTrigger.CLEANUP_REQUIRED)
        assert success and state_machine.context.current_state == ConversationState.STATE_PERSIST
        
        # STATE_PERSIST -> CLEANUP_TEMP
        success = await state_machine.trigger_transition(StateTransitionTrigger.CLEANUP_REQUIRED)
        assert success and state_machine.context.current_state == ConversationState.CLEANUP_TEMP
        
        # CLEANUP_TEMP -> IDLE
        success = await state_machine.trigger_transition(StateTransitionTrigger.CLEANUP_REQUIRED)
        assert success and state_machine.context.current_state == ConversationState.IDLE
        
        # Verify task was moved to completed tasks
        assert len(state_machine.context.completed_tasks) == 1
        assert state_machine.context.current_task is None
    
    @pytest.mark.asyncio
    async def test_invalid_transition_rejection(self, state_machine):
        """Test that invalid transitions are rejected."""
        # Try invalid transition from IDLE
        success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_SUCCESS)
        
        assert success is False
        assert state_machine.context.current_state == ConversationState.IDLE  # State unchanged
        assert len(state_machine.context.state_history) == 0  # No history recorded
    
    @pytest.mark.asyncio
    async def test_error_recovery_transition(self, state_machine):
        """Test transition to error recovery state."""
        # Set up state where error can occur
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        
        test_error = Exception("Test error")
        success = await state_machine.trigger_transition(
            StateTransitionTrigger.ERROR_DETECTED,
            error=test_error
        )
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ERROR_RECOVERY
        
        # Check error metadata
        assert "last_error" in state_machine.context.conversation_metadata
        error_info = state_machine.context.conversation_metadata["last_error"]
        assert error_info["error_type"] == "Exception"
        assert error_info["error_message"] == "Test error"
    
    @pytest.mark.asyncio
    async def test_rollback_transition(self, state_machine, mock_persistence_manager):
        """Test rollback state transition."""
        # Set up state with checkpoint
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        checkpoint = StateCheckpoint(checkpoint_id="test-checkpoint")
        state_machine.context.checkpoints.append(checkpoint)
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.ROLLBACK_REQUIRED)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ROLLBACK_STATE
        
        # Verify rollback was called
        mock_persistence_manager.rollback_to_checkpoint.assert_called_once_with(
            state_machine.context, checkpoint
        )
    
    @pytest.mark.asyncio
    async def test_checkpoint_creation_failure(self, state_machine, mock_persistence_manager):
        """Test handling of checkpoint creation failure."""
        # Make checkpoint creation fail
        mock_persistence_manager.create_checkpoint.side_effect = Exception("Checkpoint failed")
        
        state_machine.context.current_state = ConversationState.TASK_PENDING
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_START)
        
        assert success is False
        assert state_machine.context.current_state == ConversationState.TASK_PENDING  # State unchanged
    
    @pytest.mark.asyncio
    async def test_state_persistence_failure(self, state_machine, mock_persistence_manager):
        """Test handling of state persistence failure."""
        # Make persistence fail
        mock_persistence_manager.persist_conversation_state.return_value = False
        
        state_machine.context.current_state = ConversationState.TASK_COMPLETE
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.CLEANUP_REQUIRED)
        
        assert success is False
        assert state_machine.context.current_state == ConversationState.TASK_COMPLETE  # State unchanged
    
    def test_get_valid_transitions(self, state_machine):
        """Test getting valid transitions from current state."""
        # Test from IDLE state
        valid_transitions = state_machine.get_valid_transitions()
        assert StateTransitionTrigger.HOOK_EXECUTION in valid_transitions
        
        # Test from different state
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        valid_transitions = state_machine.get_valid_transitions()
        assert StateTransitionTrigger.TASK_SUCCESS in valid_transitions
        assert StateTransitionTrigger.TASK_FAILURE in valid_transitions
        assert StateTransitionTrigger.ERROR_DETECTED in valid_transitions
    
    def test_can_transition(self, state_machine):
        """Test checking if transition is valid."""
        # Valid transition from IDLE
        assert state_machine.can_transition(StateTransitionTrigger.HOOK_EXECUTION) is True
        
        # Invalid transition from IDLE
        assert state_machine.can_transition(StateTransitionTrigger.TASK_SUCCESS) is False
    
    @pytest.mark.asyncio
    async def test_transition_handler_exception(self, state_machine, mock_persistence_manager):
        """Test handling of exceptions in transition handlers."""
        # Make persistence manager raise exception
        mock_persistence_manager.create_checkpoint.side_effect = Exception("Test exception")
        
        state_machine.context.current_state = ConversationState.TASK_PENDING
        
        with patch.object(state_machine._logger, 'error') as mock_logger:
            success = await state_machine.trigger_transition(StateTransitionTrigger.TASK_START)
            
            assert success is False
            mock_logger.assert_called()
    
    @pytest.mark.asyncio
    async def test_state_version_increment(self, state_machine):
        """Test that state version increments on successful transitions."""
        initial_version = state_machine.context.state_version
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.HOOK_EXECUTION)
        
        assert success is True
        assert state_machine.context.state_version == initial_version + 1
    
    @pytest.mark.asyncio
    async def test_dirty_state_flag(self, state_machine):
        """Test that dirty state flag is set on transitions."""
        assert state_machine.context.dirty_state is False
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.HOOK_EXECUTION)
        
        assert success is True
        assert state_machine.context.dirty_state is True
    
    @pytest.mark.asyncio
    async def test_state_history_recording(self, state_machine):
        """Test that state history is properly recorded."""
        initial_history_length = len(state_machine.context.state_history)
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.HOOK_EXECUTION)
        
        assert success is True
        assert len(state_machine.context.state_history) == initial_history_length + 1
        
        # Check history entry
        last_entry = state_machine.context.state_history[-1]
        assert last_entry[0] == ConversationState.IDLE  # Previous state
        assert isinstance(last_entry[1], datetime)  # Timestamp