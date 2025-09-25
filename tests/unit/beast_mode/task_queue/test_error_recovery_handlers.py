"""
Unit tests for error recovery and rollback transition handlers

Tests the error recovery transitions:
TASK_EXECUTING → ERROR_RECOVERY → ROLLBACK_STATE → IDLE
And error recovery from various states with comprehensive validation.
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
    StateCheckpoint,
    TaskState,
)
from src.beast_mode.task_queue.state_machine import ConversationStateMachine


class TestErrorRecoveryHandlers:
    """Test suite for error recovery and rollback transition handlers."""
    
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
    async def test_error_recovery_handler_with_error(self, state_machine):
        """Test _transition_to_error_recovery handler with error information."""
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        
        test_error = ValueError("Task validation failed")
        success = await state_machine._transition_to_error_recovery(error=test_error)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ERROR_RECOVERY
        assert state_machine.context.previous_state == ConversationState.TASK_EXECUTING
        
        # Check error metadata
        assert "last_error" in state_machine.context.conversation_metadata
        error_info = state_machine.context.conversation_metadata["last_error"]
        assert error_info["error_type"] == "ValueError"
        assert error_info["error_message"] == "Task validation failed"
        assert "timestamp" in error_info
    
    @pytest.mark.asyncio
    async def test_error_recovery_handler_without_error(self, state_machine):
        """Test _transition_to_error_recovery handler without error information."""
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        
        success = await state_machine._transition_to_error_recovery()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ERROR_RECOVERY
        assert state_machine.context.previous_state == ConversationState.TASK_EXECUTING
        assert "last_error" not in state_machine.context.conversation_metadata
    
    @pytest.mark.asyncio
    async def test_rollback_state_handler_with_checkpoint(self, state_machine, mock_persistence_manager):
        """Test _transition_to_rollback_state handler with available checkpoint."""
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        
        # Add a checkpoint
        checkpoint = StateCheckpoint(
            checkpoint_id="test-checkpoint-001",
            conversation_id="test-conversation-001",
            created_at=datetime.now()
        )
        state_machine.context.checkpoints.append(checkpoint)
        
        success = await state_machine._transition_to_rollback_state()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ROLLBACK_STATE
        assert state_machine.context.previous_state == ConversationState.ERROR_RECOVERY
        
        # Verify rollback was called with the latest checkpoint
        mock_persistence_manager.rollback_to_checkpoint.assert_called_once_with(
            state_machine.context, checkpoint
        )
    
    @pytest.mark.asyncio
    async def test_rollback_state_handler_multiple_checkpoints(self, state_machine, mock_persistence_manager):
        """Test _transition_to_rollback_state handler uses the most recent checkpoint."""
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        
        # Add multiple checkpoints
        checkpoint1 = StateCheckpoint(
            checkpoint_id="checkpoint-001",
            created_at=datetime.now()
        )
        checkpoint2 = StateCheckpoint(
            checkpoint_id="checkpoint-002", 
            created_at=datetime.now()
        )
        state_machine.context.checkpoints.extend([checkpoint1, checkpoint2])
        
        success = await state_machine._transition_to_rollback_state()
        
        assert success is True
        # Should use the last (most recent) checkpoint
        mock_persistence_manager.rollback_to_checkpoint.assert_called_once_with(
            state_machine.context, checkpoint2
        )
    
    @pytest.mark.asyncio
    async def test_rollback_state_handler_no_checkpoints(self, state_machine, mock_persistence_manager):
        """Test _transition_to_rollback_state handler without checkpoints."""
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        state_machine.context.checkpoints = []
        
        success = await state_machine._transition_to_rollback_state()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ROLLBACK_STATE
        
        # Should not call rollback if no checkpoints
        mock_persistence_manager.rollback_to_checkpoint.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_rollback_state_handler_no_persistence(self, conversation_context):
        """Test _transition_to_rollback_state handler without persistence manager."""
        state_machine = ConversationStateMachine(conversation_context, None)
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        
        success = await state_machine._transition_to_rollback_state()
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ROLLBACK_STATE
    
    @pytest.mark.asyncio
    async def test_rollback_state_handler_rollback_failure(self, state_machine, mock_persistence_manager):
        """Test _transition_to_rollback_state handler when rollback fails."""
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        
        # Add checkpoint and make rollback fail
        checkpoint = StateCheckpoint(checkpoint_id="test-checkpoint")
        state_machine.context.checkpoints.append(checkpoint)
        mock_persistence_manager.rollback_to_checkpoint.return_value = False
        
        success = await state_machine._transition_to_rollback_state()
        
        assert success is False
        assert state_machine.context.current_state == ConversationState.ERROR_RECOVERY  # State unchanged
    
    @pytest.mark.asyncio
    async def test_rollback_state_handler_rollback_exception(self, state_machine, mock_persistence_manager):
        """Test _transition_to_rollback_state handler when rollback raises exception."""
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        
        # Add checkpoint and make rollback raise exception
        checkpoint = StateCheckpoint(checkpoint_id="test-checkpoint")
        state_machine.context.checkpoints.append(checkpoint)
        mock_persistence_manager.rollback_to_checkpoint.side_effect = Exception("Rollback failed")
        
        success = await state_machine._transition_to_rollback_state()
        
        assert success is False
        assert state_machine.context.current_state == ConversationState.ERROR_RECOVERY  # State unchanged
    
    @pytest.mark.asyncio
    async def test_error_recovery_from_task_executing(self, state_machine):
        """Test error recovery transition from TASK_EXECUTING state."""
        # Set up task execution state
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        task = TaskContext(task_id="test-task", task_state=TaskState.EXECUTING)
        state_machine.context.current_task = task
        
        # Trigger error recovery
        error = RuntimeError("Task execution failed")
        success = await state_machine.trigger_transition(
            StateTransitionTrigger.ERROR_DETECTED,
            error=error
        )
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ERROR_RECOVERY
        
        # Check error is recorded
        error_info = state_machine.context.conversation_metadata["last_error"]
        assert error_info["error_type"] == "RuntimeError"
        assert error_info["error_message"] == "Task execution failed"
    
    @pytest.mark.asyncio
    async def test_error_recovery_from_task_pending(self, state_machine):
        """Test error recovery transition from TASK_PENDING state."""
        state_machine.context.current_state = ConversationState.TASK_PENDING
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.ERROR_DETECTED)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ERROR_RECOVERY
    
    @pytest.mark.asyncio
    async def test_error_recovery_from_state_snapshot(self, state_machine):
        """Test error recovery transition from STATE_SNAPSHOT state."""
        state_machine.context.current_state = ConversationState.STATE_SNAPSHOT
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.ERROR_DETECTED)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ERROR_RECOVERY
    
    @pytest.mark.asyncio
    async def test_complete_error_recovery_workflow(self, state_machine, mock_persistence_manager):
        """Test complete error recovery workflow: ERROR_RECOVERY → ROLLBACK_STATE → IDLE."""
        # Set up error recovery state with checkpoint
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        checkpoint = StateCheckpoint(checkpoint_id="test-checkpoint")
        state_machine.context.checkpoints.append(checkpoint)
        
        # ERROR_RECOVERY → ROLLBACK_STATE
        success = await state_machine.trigger_transition(StateTransitionTrigger.ROLLBACK_REQUIRED)
        assert success is True
        assert state_machine.context.current_state == ConversationState.ROLLBACK_STATE
        
        # ROLLBACK_STATE → IDLE
        success = await state_machine.trigger_transition(StateTransitionTrigger.RECOVERY_COMPLETE)
        assert success is True
        assert state_machine.context.current_state == ConversationState.IDLE
    
    @pytest.mark.asyncio
    async def test_direct_recovery_to_idle(self, state_machine):
        """Test direct recovery from ERROR_RECOVERY to IDLE without rollback."""
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        
        success = await state_machine.trigger_transition(StateTransitionTrigger.RECOVERY_COMPLETE)
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.IDLE
    
    @pytest.mark.asyncio
    async def test_error_recovery_preserves_task_context(self, state_machine):
        """Test that error recovery preserves task context for potential retry."""
        # Set up task execution with error
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        task = TaskContext(
            task_id="test-task-001",
            task_type="code_generation",
            task_content="Generate function",
            task_state=TaskState.EXECUTING
        )
        state_machine.context.current_task = task
        
        # Trigger error recovery
        error = Exception("Network timeout")
        success = await state_machine.trigger_transition(
            StateTransitionTrigger.ERROR_DETECTED,
            error=error
        )
        
        assert success is True
        assert state_machine.context.current_state == ConversationState.ERROR_RECOVERY
        
        # Task context should be preserved
        assert state_machine.context.current_task == task
        assert task.task_id == "test-task-001"
        assert task.task_type == "code_generation"
    
    @pytest.mark.asyncio
    async def test_error_metadata_timestamp_format(self, state_machine):
        """Test that error metadata includes properly formatted timestamp."""
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        
        before_error = datetime.now()
        error = ValueError("Test error")
        success = await state_machine._transition_to_error_recovery(error=error)
        after_error = datetime.now()
        
        assert success is True
        
        error_info = state_machine.context.conversation_metadata["last_error"]
        error_timestamp = datetime.fromisoformat(error_info["timestamp"])
        
        # Timestamp should be between before and after
        assert before_error <= error_timestamp <= after_error
    
    @pytest.mark.asyncio
    async def test_multiple_error_recovery_cycles(self, state_machine, mock_persistence_manager):
        """Test multiple error recovery cycles update error metadata correctly."""
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        
        # First error
        error1 = ValueError("First error")
        success = await state_machine._transition_to_error_recovery(error=error1)
        assert success is True
        
        first_error_info = state_machine.context.conversation_metadata["last_error"].copy()
        
        # Transition back to executing (simulating retry)
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        
        # Second error
        error2 = RuntimeError("Second error")
        success = await state_machine._transition_to_error_recovery(error=error2)
        assert success is True
        
        # Check that error metadata was updated
        second_error_info = state_machine.context.conversation_metadata["last_error"]
        assert second_error_info["error_type"] == "RuntimeError"
        assert second_error_info["error_message"] == "Second error"
        assert second_error_info["timestamp"] != first_error_info["timestamp"]
    
    @pytest.mark.asyncio
    async def test_rollback_with_logging_verification(self, state_machine, mock_persistence_manager):
        """Test rollback transition with logging verification."""
        state_machine.context.current_state = ConversationState.ERROR_RECOVERY
        checkpoint = StateCheckpoint(checkpoint_id="test-checkpoint")
        state_machine.context.checkpoints.append(checkpoint)
        
        with patch.object(state_machine._logger, 'info') as mock_logger:
            success = await state_machine._transition_to_rollback_state()
            
            assert success is True
            mock_logger.assert_called_with(
                f"Rolled back to checkpoint {checkpoint.checkpoint_id}",
                extra={"conversation_id": state_machine.context.conversation_id}
            )
    
    @pytest.mark.asyncio
    async def test_error_recovery_state_history_tracking(self, state_machine):
        """Test that error recovery properly tracks state history."""
        initial_history_length = len(state_machine.context.state_history)
        state_machine.context.current_state = ConversationState.TASK_EXECUTING
        
        # Trigger error recovery through the main transition method
        success = await state_machine.trigger_transition(StateTransitionTrigger.ERROR_DETECTED)
        
        assert success is True
        assert len(state_machine.context.state_history) == initial_history_length + 1
        
        # Check history entry
        last_entry = state_machine.context.state_history[-1]
        assert last_entry[0] == ConversationState.TASK_EXECUTING  # Previous state
        assert isinstance(last_entry[1], datetime)  # Timestamp