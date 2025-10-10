"""
Unit tests for TaskStateMachine

Tests task lifecycle validation, state transitions, timeout handling,
and the "tap on the shoulder" callback mechanism for stuck tasks.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from src.beast_mode.task_queue.models import (
    TaskState,
    TaskContext,
)
from src.beast_mode.task_queue.state_machine import TaskStateMachine


class TestTaskStateMachine:
    """Test suite for TaskStateMachine."""
    
    @pytest.fixture
    def task_context(self):
        """Create test task context."""
        return TaskContext(
            task_id="test-task-001",
            task_type="code_generation",
            task_content="Generate a Python function",
            task_parameters={"language": "python", "complexity": "medium"},
            task_metadata={"priority": "high", "user_id": "user-123"},
            created_at=datetime.now() - timedelta(minutes=5),
            task_state=TaskState.QUEUED
        )
    
    @pytest.fixture
    def task_state_machine(self, task_context):
        """Create TaskStateMachine instance."""
        return TaskStateMachine(task_context)
    
    def test_task_state_machine_initialization(self, task_state_machine, task_context):
        """Test TaskStateMachine initialization."""
        assert task_state_machine.task_context == task_context
        assert task_state_machine.valid_transitions is not None
        assert len(task_state_machine.valid_transitions) > 0
        assert task_context.task_state in task_state_machine.valid_transitions
    
    def test_valid_transitions_definition(self, task_state_machine):
        """Test that valid transitions are properly defined."""
        transitions = task_state_machine.valid_transitions
        
        # Test QUEUED state transitions
        assert TaskState.CLAIMED in transitions[TaskState.QUEUED]
        assert TaskState.CANCELLED in transitions[TaskState.QUEUED]
        assert TaskState.EXPIRED in transitions[TaskState.QUEUED]
        
        # Test CLAIMED state transitions
        assert TaskState.VALIDATED in transitions[TaskState.CLAIMED]
        assert TaskState.CANCELLED in transitions[TaskState.CLAIMED]
        assert TaskState.EXPIRED in transitions[TaskState.CLAIMED]
        
        # Test EXECUTING state transitions
        assert TaskState.COMPLETED in transitions[TaskState.EXECUTING]
        assert TaskState.FAILED in transitions[TaskState.EXECUTING]
        assert TaskState.CANCELLED in transitions[TaskState.EXECUTING]
        
        # Test terminal states have no transitions
        assert len(transitions[TaskState.COMPLETED]) == 0
        assert len(transitions[TaskState.CANCELLED]) == 0
        assert len(transitions[TaskState.EXPIRED]) == 0
    
    @pytest.mark.asyncio
    async def test_valid_transition_queued_to_claimed(self, task_state_machine):
        """Test valid transition from QUEUED to CLAIMED."""
        assert task_state_machine.task_context.task_state == TaskState.QUEUED
        
        success = await task_state_machine.transition_to(TaskState.CLAIMED, "Task claimed by instance")
        
        assert success is True
        assert task_state_machine.task_context.task_state == TaskState.CLAIMED
        assert task_state_machine.task_context.claimed_at is not None
        assert len(task_state_machine.task_context.state_history) == 1
        
        # Check state history
        history_entry = task_state_machine.task_context.state_history[0]
        assert history_entry[0] == TaskState.QUEUED
        assert isinstance(history_entry[1], datetime)
    
    @pytest.mark.asyncio
    async def test_valid_transition_claimed_to_validated(self, task_state_machine):
        """Test valid transition from CLAIMED to VALIDATED."""
        # First transition to CLAIMED
        await task_state_machine.transition_to(TaskState.CLAIMED)
        
        success = await task_state_machine.transition_to(TaskState.VALIDATED, "Task validation passed")
        
        assert success is True
        assert task_state_machine.task_context.task_state == TaskState.VALIDATED
        assert len(task_state_machine.task_context.state_history) == 2
    
    @pytest.mark.asyncio
    async def test_valid_transition_validated_to_executing(self, task_state_machine):
        """Test valid transition from VALIDATED to EXECUTING."""
        # Set up state chain
        await task_state_machine.transition_to(TaskState.CLAIMED)
        await task_state_machine.transition_to(TaskState.VALIDATED)
        
        success = await task_state_machine.transition_to(TaskState.EXECUTING, "Task execution started")
        
        assert success is True
        assert task_state_machine.task_context.task_state == TaskState.EXECUTING
        assert task_state_machine.task_context.execution_start is not None
        assert len(task_state_machine.task_context.state_history) == 3
    
    @pytest.mark.asyncio
    async def test_valid_transition_executing_to_completed(self, task_state_machine):
        """Test valid transition from EXECUTING to COMPLETED."""
        # Set up state chain
        await task_state_machine.transition_to(TaskState.CLAIMED)
        await task_state_machine.transition_to(TaskState.VALIDATED)
        await task_state_machine.transition_to(TaskState.EXECUTING)
        
        success = await task_state_machine.transition_to(TaskState.COMPLETED, "Task completed successfully")
        
        assert success is True
        assert task_state_machine.task_context.task_state == TaskState.COMPLETED
        assert task_state_machine.task_context.execution_end is not None
        assert task_state_machine.task_context.execution_end > task_state_machine.task_context.execution_start
    
    @pytest.mark.asyncio
    async def test_valid_transition_executing_to_failed(self, task_state_machine):
        """Test valid transition from EXECUTING to FAILED."""
        # Set up state chain
        await task_state_machine.transition_to(TaskState.CLAIMED)
        await task_state_machine.transition_to(TaskState.VALIDATED)
        await task_state_machine.transition_to(TaskState.EXECUTING)
        
        success = await task_state_machine.transition_to(TaskState.FAILED, "Task execution failed")
        
        assert success is True
        assert task_state_machine.task_context.task_state == TaskState.FAILED
        assert task_state_machine.task_context.execution_end is not None
    
    @pytest.mark.asyncio
    async def test_valid_transition_failed_to_retrying(self, task_state_machine):
        """Test valid transition from FAILED to RETRYING."""
        # Set up state chain to FAILED
        await task_state_machine.transition_to(TaskState.CLAIMED)
        await task_state_machine.transition_to(TaskState.VALIDATED)
        await task_state_machine.transition_to(TaskState.EXECUTING)
        await task_state_machine.transition_to(TaskState.FAILED)
        
        success = await task_state_machine.transition_to(TaskState.RETRYING, "Retrying failed task")
        
        assert success is True
        assert task_state_machine.task_context.task_state == TaskState.RETRYING
    
    @pytest.mark.asyncio
    async def test_invalid_transition_rejection(self, task_state_machine):
        """Test that invalid transitions are rejected."""
        # Try invalid transition from QUEUED to COMPLETED
        assert task_state_machine.task_context.task_state == TaskState.QUEUED
        
        success = await task_state_machine.transition_to(TaskState.COMPLETED, "Invalid transition")
        
        assert success is False
        assert task_state_machine.task_context.task_state == TaskState.QUEUED  # State unchanged
        assert len(task_state_machine.task_context.state_history) == 0  # No history recorded
    
    @pytest.mark.asyncio
    async def test_invalid_transition_queued_to_executing(self, task_state_machine):
        """Test invalid transition from QUEUED directly to EXECUTING."""
        success = await task_state_machine.transition_to(TaskState.EXECUTING, "Skip validation")
        
        assert success is False
        assert task_state_machine.task_context.task_state == TaskState.QUEUED
    
    @pytest.mark.asyncio
    async def test_invalid_transition_from_terminal_state(self, task_state_machine):
        """Test that transitions from terminal states are rejected."""
        # Set up completed state
        await task_state_machine.transition_to(TaskState.CLAIMED)
        await task_state_machine.transition_to(TaskState.VALIDATED)
        await task_state_machine.transition_to(TaskState.EXECUTING)
        await task_state_machine.transition_to(TaskState.COMPLETED)
        
        # Try to transition from terminal state
        success = await task_state_machine.transition_to(TaskState.EXECUTING, "Invalid from terminal")
        
        assert success is False
        assert task_state_machine.task_context.task_state == TaskState.COMPLETED
    
    @pytest.mark.asyncio
    async def test_cancellation_from_various_states(self, task_state_machine):
        """Test that tasks can be cancelled from most states."""
        # Test cancellation from QUEUED
        success = await task_state_machine.transition_to(TaskState.CANCELLED, "User cancelled")
        assert success is True
        
        # Reset and test cancellation from CLAIMED
        task_state_machine.task_context.task_state = TaskState.CLAIMED
        task_state_machine.task_context.state_history = []
        success = await task_state_machine.transition_to(TaskState.CANCELLED, "System cancelled")
        assert success is True
        
        # Reset and test cancellation from EXECUTING
        task_state_machine.task_context.task_state = TaskState.EXECUTING
        task_state_machine.task_context.state_history = []
        success = await task_state_machine.transition_to(TaskState.CANCELLED, "Timeout cancelled")
        assert success is True
    
    @pytest.mark.asyncio
    async def test_expiration_from_early_states(self, task_state_machine):
        """Test that tasks can expire from early states."""
        # Test expiration from QUEUED
        success = await task_state_machine.transition_to(TaskState.EXPIRED, "Task expired in queue")
        assert success is True
        
        # Reset and test expiration from CLAIMED
        task_state_machine.task_context.task_state = TaskState.CLAIMED
        task_state_machine.task_context.state_history = []
        success = await task_state_machine.transition_to(TaskState.EXPIRED, "Claim expired")
        assert success is True
    
    @pytest.mark.asyncio
    async def test_retry_cycle(self, task_state_machine):
        """Test complete retry cycle: FAILED -> RETRYING -> EXECUTING -> COMPLETED."""
        # Set up to FAILED state
        await task_state_machine.transition_to(TaskState.CLAIMED)
        await task_state_machine.transition_to(TaskState.VALIDATED)
        await task_state_machine.transition_to(TaskState.EXECUTING)
        await task_state_machine.transition_to(TaskState.FAILED)
        
        # Retry cycle
        success = await task_state_machine.transition_to(TaskState.RETRYING, "Retry attempt")
        assert success is True
        
        success = await task_state_machine.transition_to(TaskState.EXECUTING, "Retry execution")
        assert success is True
        
        success = await task_state_machine.transition_to(TaskState.COMPLETED, "Retry successful")
        assert success is True
        
        assert task_state_machine.task_context.task_state == TaskState.COMPLETED
    
    def test_get_valid_transitions(self, task_state_machine):
        """Test getting valid transitions from current state."""
        # Test from QUEUED state
        valid_transitions = task_state_machine.get_valid_transitions()
        expected = [TaskState.CLAIMED, TaskState.CANCELLED, TaskState.EXPIRED]
        assert all(state in valid_transitions for state in expected)
        
        # Change state and test again
        task_state_machine.task_context.task_state = TaskState.EXECUTING
        valid_transitions = task_state_machine.get_valid_transitions()
        expected = [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]
        assert all(state in valid_transitions for state in expected)
    
    def test_can_transition_to(self, task_state_machine):
        """Test checking if transition to new state is valid."""
        # Valid transitions from QUEUED
        assert task_state_machine.can_transition_to(TaskState.CLAIMED) is True
        assert task_state_machine.can_transition_to(TaskState.CANCELLED) is True
        assert task_state_machine.can_transition_to(TaskState.EXPIRED) is True
        
        # Invalid transitions from QUEUED
        assert task_state_machine.can_transition_to(TaskState.EXECUTING) is False
        assert task_state_machine.can_transition_to(TaskState.COMPLETED) is False
    
    def test_is_terminal_state(self, task_state_machine):
        """Test terminal state detection."""
        # Non-terminal states
        assert task_state_machine.is_terminal_state() is False
        
        task_state_machine.task_context.task_state = TaskState.EXECUTING
        assert task_state_machine.is_terminal_state() is False
        
        # Terminal states
        task_state_machine.task_context.task_state = TaskState.COMPLETED
        assert task_state_machine.is_terminal_state() is True
        
        task_state_machine.task_context.task_state = TaskState.CANCELLED
        assert task_state_machine.is_terminal_state() is True
        
        task_state_machine.task_context.task_state = TaskState.EXPIRED
        assert task_state_machine.is_terminal_state() is True
    
    @pytest.mark.asyncio
    async def test_get_state_duration(self, task_state_machine):
        """Test getting duration in current state."""
        # No history initially
        assert task_state_machine.get_state_duration() is None
        
        # Transition to create history
        await task_state_machine.transition_to(TaskState.CLAIMED)
        
        duration = task_state_machine.get_state_duration()
        assert duration is not None
        assert duration >= 0
        assert duration < 1  # Should be very small for immediate test
    
    def test_get_total_execution_time_no_start(self, task_state_machine):
        """Test getting total execution time when execution hasn't started."""
        assert task_state_machine.get_total_execution_time() is None
    
    @pytest.mark.asyncio
    async def test_get_total_execution_time_with_execution(self, task_state_machine):
        """Test getting total execution time during and after execution."""
        # Set up to executing state
        await task_state_machine.transition_to(TaskState.CLAIMED)
        await task_state_machine.transition_to(TaskState.VALIDATED)
        await task_state_machine.transition_to(TaskState.EXECUTING)
        
        # Should have execution time now
        execution_time = task_state_machine.get_total_execution_time()
        assert execution_time is not None
        assert execution_time >= 0
        
        # Complete the task
        await task_state_machine.transition_to(TaskState.COMPLETED)
        
        # Should still have execution time
        final_execution_time = task_state_machine.get_total_execution_time()
        assert final_execution_time is not None
        assert final_execution_time >= execution_time
    
    @pytest.mark.asyncio
    async def test_state_history_tracking(self, task_state_machine):
        """Test that state history is properly tracked."""
        initial_history_length = len(task_state_machine.task_context.state_history)
        
        # Make several transitions
        await task_state_machine.transition_to(TaskState.CLAIMED)
        await task_state_machine.transition_to(TaskState.VALIDATED)
        await task_state_machine.transition_to(TaskState.EXECUTING)
        
        # Check history was recorded
        assert len(task_state_machine.task_context.state_history) == initial_history_length + 3
        
        # Check history entries
        history = task_state_machine.task_context.state_history
        assert history[-3][0] == TaskState.QUEUED
        assert history[-2][0] == TaskState.CLAIMED
        assert history[-1][0] == TaskState.VALIDATED
        
        # All timestamps should be datetime objects
        for state, timestamp in history:
            assert isinstance(timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_timestamp_updates(self, task_state_machine):
        """Test that timestamps are properly updated during transitions."""
        original_created = task_state_machine.task_context.created_at
        
        # Claim task
        await task_state_machine.transition_to(TaskState.CLAIMED)
        assert task_state_machine.task_context.claimed_at is not None
        assert task_state_machine.task_context.claimed_at > original_created
        
        # Start execution
        await task_state_machine.transition_to(TaskState.VALIDATED)
        await task_state_machine.transition_to(TaskState.EXECUTING)
        assert task_state_machine.task_context.execution_start is not None
        assert task_state_machine.task_context.execution_start > task_state_machine.task_context.claimed_at
        
        # Complete task
        await task_state_machine.transition_to(TaskState.COMPLETED)
        assert task_state_machine.task_context.execution_end is not None
        assert task_state_machine.task_context.execution_end > task_state_machine.task_context.execution_start
    
    @pytest.mark.asyncio
    async def test_transition_with_reason_logging(self, task_state_machine):
        """Test that transition reasons are properly logged."""
        with patch.object(task_state_machine._logger, 'info') as mock_logger:
            success = await task_state_machine.transition_to(
                TaskState.CLAIMED, 
                "Task claimed by instance-001 for user-123"
            )
            
            assert success is True
            mock_logger.assert_called_once()
            
            # Check log message contains reason
            call_args = mock_logger.call_args[0][0]
            assert "QUEUED -> CLAIMED" in call_args
    
    @pytest.mark.asyncio
    async def test_transition_error_handling(self, task_state_machine):
        """Test error handling during state transitions."""
        # Test with an invalid transition that will trigger error logging
        with patch.object(task_state_machine._logger, 'warning') as mock_logger:
            success = await task_state_machine.transition_to(TaskState.COMPLETED, "Invalid transition")
            
            assert success is False
            mock_logger.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_complex_task_lifecycle(self, task_state_machine):
        """Test complete complex task lifecycle with retry."""
        # Initial state
        assert task_state_machine.task_context.task_state == TaskState.QUEUED
        
        # Normal flow to failure
        await task_state_machine.transition_to(TaskState.CLAIMED, "Claimed by worker-1")
        await task_state_machine.transition_to(TaskState.VALIDATED, "Validation passed")
        await task_state_machine.transition_to(TaskState.EXECUTING, "Execution started")
        await task_state_machine.transition_to(TaskState.FAILED, "Network timeout")
        
        # Retry flow
        await task_state_machine.transition_to(TaskState.RETRYING, "Retry attempt 1")
        await task_state_machine.transition_to(TaskState.EXECUTING, "Retry execution")
        await task_state_machine.transition_to(TaskState.COMPLETED, "Retry successful")
        
        # Verify final state
        assert task_state_machine.task_context.task_state == TaskState.COMPLETED
        assert task_state_machine.is_terminal_state() is True
        assert len(task_state_machine.task_context.state_history) == 7
        
        # Verify timing
        assert task_state_machine.task_context.claimed_at is not None
        assert task_state_machine.task_context.execution_start is not None
        assert task_state_machine.task_context.execution_end is not None
        
        # Verify execution time calculation
        execution_time = task_state_machine.get_total_execution_time()
        assert execution_time is not None
        assert execution_time > 0


class TestTaskTimeoutCallbacks:
    """Test suite for task timeout and callback mechanisms - the 'tap on the shoulder' feature."""
    
    @pytest.fixture
    def long_running_task(self):
        """Create a task that's been running for a while."""
        return TaskContext(
            task_id="long-running-task-001",
            task_type="complex_analysis",
            task_content="Analyze large dataset",
            created_at=datetime.now() - timedelta(minutes=30),
            claimed_at=datetime.now() - timedelta(minutes=25),
            execution_start=datetime.now() - timedelta(minutes=20),
            task_state=TaskState.EXECUTING,
            task_metadata={
                "timeout_threshold_minutes": 15,
                "max_execution_time_minutes": 30,
                "callback_url": "http://supervisor/task-timeout",
                "priority": "high"
            }
        )
    
    @pytest.fixture
    def timeout_task_machine(self, long_running_task):
        """Create TaskStateMachine for timeout testing."""
        return TaskStateMachine(long_running_task)
    
    def test_task_timeout_detection(self, timeout_task_machine):
        """Test detection of tasks that have been running too long."""
        # Task has been executing for 20 minutes, threshold is 15
        execution_time = timeout_task_machine.get_total_execution_time()
        timeout_threshold = timeout_task_machine.task_context.task_metadata.get("timeout_threshold_minutes", 15) * 60
        
        assert execution_time is not None
        assert execution_time > timeout_threshold
        
        # This would trigger the "tap on the shoulder" callback
        is_timeout = execution_time > timeout_threshold
        assert is_timeout is True
    
    def test_task_age_calculation(self, timeout_task_machine):
        """Test calculation of task age for timeout detection."""
        task = timeout_task_machine.task_context
        
        # Calculate various age metrics
        total_age = (datetime.now() - task.created_at).total_seconds()
        claimed_age = (datetime.now() - task.claimed_at).total_seconds() if task.claimed_at else 0
        execution_age = timeout_task_machine.get_total_execution_time() or 0
        
        assert total_age > 25 * 60  # More than 25 minutes old
        assert claimed_age > 20 * 60  # Claimed more than 20 minutes ago
        assert execution_age > 15 * 60  # Executing more than 15 minutes
        
        # These metrics would be used for timeout callbacks
        timeout_data = {
            "task_id": task.task_id,
            "total_age_seconds": total_age,
            "execution_age_seconds": execution_age,
            "timeout_threshold_seconds": task.task_metadata.get("timeout_threshold_minutes", 15) * 60,
            "current_state": task.task_state.name,
            "callback_url": task.task_metadata.get("callback_url")
        }
        
        assert timeout_data["execution_age_seconds"] > timeout_data["timeout_threshold_seconds"]
    
    @pytest.mark.asyncio
    async def test_timeout_callback_trigger_conditions(self, timeout_task_machine):
        """Test conditions that would trigger timeout callbacks."""
        task = timeout_task_machine.task_context
        
        # Simulate timeout callback conditions
        execution_time = timeout_task_machine.get_total_execution_time() or 0
        state_duration = timeout_task_machine.get_state_duration() or 0
        
        conditions = {
            "execution_timeout": execution_time > 15 * 60,
            "total_timeout": (datetime.now() - task.created_at).total_seconds() > 30 * 60,
            "stuck_in_state": state_duration > 10 * 60,
            "high_priority": task.task_metadata.get("priority") == "high",
            "has_callback": "callback_url" in task.task_metadata
        }
        
        # This task should trigger callbacks
        assert conditions["execution_timeout"] is True
        assert conditions["high_priority"] is True
        assert conditions["has_callback"] is True
        
        # Simulate the "tap on the shoulder" - transition to a warning state
        # In a real implementation, this might be a new state like TIMEOUT_WARNING
        success = await timeout_task_machine.transition_to(
            TaskState.FAILED, 
            "Execution timeout - tap on the shoulder callback triggered"
        )
        assert success is True
    
    def test_message_queue_backlog_simulation(self, timeout_task_machine):
        """Test simulation of message queue backlog - the '50 messages while sleeping' scenario."""
        task = timeout_task_machine.task_context
        
        # Simulate message backlog data
        message_backlog = {
            "task_id": task.task_id,
            "messages_pending": 47,  # "50 messages for you while you were sleeping"
            "oldest_message_age_minutes": 18,
            "newest_message_age_minutes": 2,
            "high_priority_messages": 12,
            "user_messages": 23,
            "system_messages": 24,
            "callback_required": True
        }
        
        # Add backlog info to task metadata
        task.task_metadata["message_backlog"] = message_backlog
        
        # Check if callback should be triggered
        should_callback = (
            message_backlog["messages_pending"] > 10 or
            message_backlog["high_priority_messages"] > 5 or
            message_backlog["oldest_message_age_minutes"] > 15
        )
        
        assert should_callback is True
        assert message_backlog["messages_pending"] == 47
        assert message_backlog["high_priority_messages"] == 12
    
    @pytest.mark.asyncio
    async def test_rip_van_winkle_scenario(self, timeout_task_machine):
        """Test the 'Rip Van Winkle' scenario - task sleeping too long with message backlog."""
        task = timeout_task_machine.task_context
        
        # Simulate a task that's been "sleeping" (stuck in executing state)
        execution_time = timeout_task_machine.get_total_execution_time()
        state_duration = timeout_task_machine.get_state_duration()
        
        # Add Rip Van Winkle detection metadata
        rip_van_winkle_data = {
            "sleeping_threshold_minutes": 10,
            "execution_time_minutes": execution_time / 60 if execution_time else 0,
            "state_duration_minutes": state_duration / 60 if state_duration else 0,
            "message_backlog_count": 50,
            "wake_up_required": True,
            "wake_up_message": "Hey, you've been at that quite a while. Is everything okay? And oh, by the way, there have been 50 messages for you while you were sleeping, Rip Van Winkle."
        }
        
        task.task_metadata["rip_van_winkle"] = rip_van_winkle_data
        
        # Check if wake-up call is needed
        needs_wake_up = (
            rip_van_winkle_data["execution_time_minutes"] > rip_van_winkle_data["sleeping_threshold_minutes"] and
            rip_van_winkle_data["message_backlog_count"] > 10
        )
        
        assert needs_wake_up is True
        assert rip_van_winkle_data["execution_time_minutes"] > 15  # Been executing for more than 15 minutes
        assert rip_van_winkle_data["message_backlog_count"] == 50
        
        # Simulate the wake-up call by transitioning to a recovery state
        success = await timeout_task_machine.transition_to(
            TaskState.FAILED,
            rip_van_winkle_data["wake_up_message"]
        )
        assert success is True
    
    def test_callback_payload_generation(self, timeout_task_machine):
        """Test generation of callback payload for timeout notifications."""
        task = timeout_task_machine.task_context
        
        # Generate comprehensive callback payload
        callback_payload = {
            "event_type": "task_timeout_warning",
            "task_id": task.task_id,
            "task_type": task.task_type,
            "current_state": task.task_state.name,
            "timeout_info": {
                "execution_time_seconds": timeout_task_machine.get_total_execution_time(),
                "state_duration_seconds": timeout_task_machine.get_state_duration(),
                "timeout_threshold_seconds": task.task_metadata.get("timeout_threshold_minutes", 15) * 60,
                "max_execution_time_seconds": task.task_metadata.get("max_execution_time_minutes", 30) * 60
            },
            "task_info": {
                "created_at": task.created_at.isoformat(),
                "claimed_at": task.claimed_at.isoformat() if task.claimed_at else None,
                "execution_start": task.execution_start.isoformat() if task.execution_start else None,
                "priority": task.task_metadata.get("priority", "normal")
            },
            "message_backlog": task.task_metadata.get("message_backlog", {}),
            "callback_url": task.task_metadata.get("callback_url"),
            "suggested_actions": [
                "Check task progress",
                "Consider task cancellation",
                "Review message backlog",
                "Investigate potential deadlock"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        # Verify payload structure
        assert callback_payload["event_type"] == "task_timeout_warning"
        assert callback_payload["task_id"] == task.task_id
        assert callback_payload["timeout_info"]["execution_time_seconds"] > 15 * 60
        assert len(callback_payload["suggested_actions"]) > 0
        assert callback_payload["callback_url"] == "http://supervisor/task-timeout"