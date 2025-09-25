"""
State machine implementations for conversation and task lifecycle management.

This module implements formal state machines for managing conversation state
and individual task lifecycles with comprehensive validation and logging.
"""

import logging
from datetime import datetime
from typing import Dict, Callable, Optional, Any, List, Tuple
import uuid

from .models import (
    ConversationState,
    TaskState,
    StateTransitionTrigger,
    ConversationContext,
    TaskContext,
    StateCheckpoint,
    HookEvent,
)


class ConversationStateMachine:
    """Formal state machine for conversation management based on architecture specification."""
    
    def __init__(self, context: ConversationContext, persistence_manager=None):
        self.context = context
        self.persistence = persistence_manager
        self._logger = logging.getLogger(f"{__name__}.ConversationStateMachine")
        self.transition_handlers: Dict[Tuple[ConversationState, StateTransitionTrigger], Callable] = {}
        self._setup_transition_table()
    
    def _setup_transition_table(self):
        """Set up the formal state transition table."""
        # Define valid transitions with their handlers
        transitions = {
            # From IDLE state
            (ConversationState.IDLE, StateTransitionTrigger.HOOK_EXECUTION): self._transition_to_hook_triggered,
            
            # From HOOK_TRIGGERED state
            (ConversationState.HOOK_TRIGGERED, StateTransitionTrigger.TASK_AVAILABLE): self._transition_to_task_pending,
            (ConversationState.HOOK_TRIGGERED, StateTransitionTrigger.CLEANUP_REQUIRED): self._transition_to_idle,
            
            # From TASK_PENDING state
            (ConversationState.TASK_PENDING, StateTransitionTrigger.TASK_START): self._transition_to_state_snapshot,
            (ConversationState.TASK_PENDING, StateTransitionTrigger.ERROR_DETECTED): self._transition_to_error_recovery,
            
            # From STATE_SNAPSHOT state
            (ConversationState.STATE_SNAPSHOT, StateTransitionTrigger.TASK_START): self._transition_to_task_executing,
            (ConversationState.STATE_SNAPSHOT, StateTransitionTrigger.ERROR_DETECTED): self._transition_to_error_recovery,
            
            # From TASK_EXECUTING state
            (ConversationState.TASK_EXECUTING, StateTransitionTrigger.TASK_SUCCESS): self._transition_to_task_complete,
            (ConversationState.TASK_EXECUTING, StateTransitionTrigger.TASK_FAILURE): self._transition_to_error_recovery,
            (ConversationState.TASK_EXECUTING, StateTransitionTrigger.ERROR_DETECTED): self._transition_to_error_recovery,
            
            # From TASK_COMPLETE state
            (ConversationState.TASK_COMPLETE, StateTransitionTrigger.CLEANUP_REQUIRED): self._transition_to_state_persist,
            
            # From STATE_PERSIST state
            (ConversationState.STATE_PERSIST, StateTransitionTrigger.CLEANUP_REQUIRED): self._transition_to_cleanup_temp,
            
            # From CLEANUP_TEMP state
            (ConversationState.CLEANUP_TEMP, StateTransitionTrigger.CLEANUP_REQUIRED): self._transition_to_idle,
            
            # From ERROR_RECOVERY state
            (ConversationState.ERROR_RECOVERY, StateTransitionTrigger.ROLLBACK_REQUIRED): self._transition_to_rollback_state,
            (ConversationState.ERROR_RECOVERY, StateTransitionTrigger.RECOVERY_COMPLETE): self._transition_to_idle,
            
            # From ROLLBACK_STATE state
            (ConversationState.ROLLBACK_STATE, StateTransitionTrigger.RECOVERY_COMPLETE): self._transition_to_idle,
        }
        
        self.transition_handlers.update(transitions)
    
    async def trigger_transition(self, trigger: StateTransitionTrigger, **kwargs) -> bool:
        """Trigger a state transition with validation."""
        current_state = self.context.current_state
        transition_key = (current_state, trigger)
        
        if transition_key not in self.transition_handlers:
            self._logger.warning(
                f"Invalid transition: {current_state.name} -> {trigger.name}",
                extra={"conversation_id": self.context.conversation_id}
            )
            return False
        
        try:
            # Record state history before transition
            self.context.state_history.append((current_state, datetime.now()))
            
            # Execute transition handler
            handler = self.transition_handlers[transition_key]
            success = await handler(**kwargs)
            
            if success:
                self._logger.info(
                    f"State transition successful: {current_state.name} -> {self.context.current_state.name}",
                    extra={
                        "conversation_id": self.context.conversation_id,
                        "trigger": trigger.name,
                        "previous_state": current_state.name,
                        "new_state": self.context.current_state.name
                    }
                )
                
                # Mark state as dirty for persistence
                self.context.dirty_state = True
                self.context.state_version += 1
                
                return True
            else:
                self._logger.error(
                    f"State transition failed: {current_state.name} -> {trigger.name}",
                    extra={"conversation_id": self.context.conversation_id}
                )
                return False
                
        except Exception as e:
            self._logger.error(
                f"State transition error: {current_state.name} -> {trigger.name}: {e}",
                extra={"conversation_id": self.context.conversation_id}
            )
            return False
    
    async def _transition_to_hook_triggered(self, hook_event: HookEvent = None, **kwargs) -> bool:
        """Transition to hook triggered state."""
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.HOOK_TRIGGERED
        
        if hook_event:
            self.context.conversation_metadata["last_hook_event"] = {
                "event_type": hook_event.event_type,
                "timestamp": hook_event.timestamp.isoformat(),
                "event_data": hook_event.event_data
            }
        
        return True
    
    async def _transition_to_task_pending(self, task: TaskContext = None, **kwargs) -> bool:
        """Transition to task pending state."""
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.TASK_PENDING
        
        if task:
            self.context.current_task = task
            self.context.task_queue.append(task)
        
        return True
    
    async def _transition_to_state_snapshot(self, **kwargs) -> bool:
        """Transition to state snapshot creation."""
        # Create checkpoint if persistence manager is available
        if self.persistence:
            try:
                checkpoint = await self.persistence.create_checkpoint(self.context)
                self.context.checkpoints.append(checkpoint)
                self._logger.info(
                    f"Created checkpoint {checkpoint.checkpoint_id}",
                    extra={"conversation_id": self.context.conversation_id}
                )
            except Exception as e:
                self._logger.error(
                    f"Failed to create checkpoint: {e}",
                    extra={"conversation_id": self.context.conversation_id}
                )
                return False
        
        # Only change state after successful checkpoint creation
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.STATE_SNAPSHOT
        return True
    
    async def _transition_to_task_executing(self, **kwargs) -> bool:
        """Transition to task executing state."""
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.TASK_EXECUTING
        
        if self.context.current_task:
            self.context.current_task.execution_start = datetime.now()
            self.context.current_task.task_state = TaskState.EXECUTING
        
        return True
    
    async def _transition_to_task_complete(self, **kwargs) -> bool:
        """Transition to task complete state."""
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.TASK_COMPLETE
        
        if self.context.current_task:
            self.context.current_task.execution_end = datetime.now()
            self.context.current_task.task_state = TaskState.COMPLETED
        
        return True
    
    async def _transition_to_state_persist(self, **kwargs) -> bool:
        """Transition to state persist."""
        # Persist state if persistence manager is available
        if self.persistence:
            try:
                success = await self.persistence.persist_conversation_state(self.context)
                if not success:
                    self._logger.error(
                        "Failed to persist conversation state",
                        extra={"conversation_id": self.context.conversation_id}
                    )
                    return False
                
                self.context.last_persistence = datetime.now()
                self.context.dirty_state = False
                
            except Exception as e:
                self._logger.error(
                    f"Error persisting conversation state: {e}",
                    extra={"conversation_id": self.context.conversation_id}
                )
                return False
        
        # Only change state after successful persistence
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.STATE_PERSIST
        return True
    
    async def _transition_to_cleanup_temp(self, **kwargs) -> bool:
        """Transition to cleanup temporary state."""
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.CLEANUP_TEMP
        
        # Move completed task to completed tasks list
        if self.context.current_task:
            # Create task result (this would be populated by the actual task execution)
            from .models import TaskResult
            task_result = TaskResult(
                task_id=self.context.current_task.task_id,
                success=True,  # This would be determined by actual execution
                execution_time_ms=0.0,  # This would be calculated from actual execution
            )
            self.context.completed_tasks.append(task_result)
            self.context.current_task = None
        
        return True
    
    async def _transition_to_idle(self, **kwargs) -> bool:
        """Transition to idle state."""
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.IDLE
        return True
    
    async def _transition_to_error_recovery(self, error: Exception = None, **kwargs) -> bool:
        """Transition to error recovery state."""
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.ERROR_RECOVERY
        
        if error:
            self.context.conversation_metadata["last_error"] = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.now().isoformat()
            }
        
        return True
    
    async def _transition_to_rollback_state(self, **kwargs) -> bool:
        """Transition to rollback state."""
        # Perform rollback if persistence manager is available
        if self.persistence and self.context.checkpoints:
            try:
                # Use the most recent checkpoint
                latest_checkpoint = self.context.checkpoints[-1]
                success = await self.persistence.rollback_to_checkpoint(self.context, latest_checkpoint)
                
                if not success:
                    self._logger.error(
                        "Failed to rollback to checkpoint",
                        extra={"conversation_id": self.context.conversation_id}
                    )
                    return False
                
                self._logger.info(
                    f"Rolled back to checkpoint {latest_checkpoint.checkpoint_id}",
                    extra={"conversation_id": self.context.conversation_id}
                )
                
            except Exception as e:
                self._logger.error(
                    f"Error during rollback: {e}",
                    extra={"conversation_id": self.context.conversation_id}
                )
                return False
        
        # Only change state after successful rollback (or if no rollback needed)
        self.context.previous_state = self.context.current_state
        self.context.current_state = ConversationState.ROLLBACK_STATE
        return True
    
    def get_valid_transitions(self) -> List[StateTransitionTrigger]:
        """Get valid transitions from current state."""
        current_state = self.context.current_state
        valid_triggers = []
        
        for (state, trigger) in self.transition_handlers.keys():
            if state == current_state:
                valid_triggers.append(trigger)
        
        return valid_triggers
    
    def can_transition(self, trigger: StateTransitionTrigger) -> bool:
        """Check if a transition is valid from current state."""
        return (self.context.current_state, trigger) in self.transition_handlers


class TaskStateMachine:
    """State machine for individual task lifecycle management."""
    
    def __init__(self, task_context: TaskContext):
        self.task_context = task_context
        self._logger = logging.getLogger(f"{__name__}.TaskStateMachine")
        self.valid_transitions = self._define_valid_transitions()
    
    def _define_valid_transitions(self) -> Dict[TaskState, List[TaskState]]:
        """Define valid state transitions for tasks."""
        return {
            TaskState.QUEUED: [TaskState.CLAIMED, TaskState.CANCELLED, TaskState.EXPIRED],
            TaskState.CLAIMED: [TaskState.VALIDATED, TaskState.CANCELLED, TaskState.EXPIRED],
            TaskState.VALIDATED: [TaskState.EXECUTING, TaskState.CANCELLED],
            TaskState.EXECUTING: [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED],
            TaskState.FAILED: [TaskState.RETRYING, TaskState.CANCELLED],
            TaskState.RETRYING: [TaskState.EXECUTING, TaskState.FAILED, TaskState.CANCELLED],
            TaskState.COMPLETED: [],  # Terminal state
            TaskState.CANCELLED: [],  # Terminal state
            TaskState.EXPIRED: [],    # Terminal state
        }
    
    async def transition_to(self, new_state: TaskState, reason: str = "") -> bool:
        """Transition task to new state with validation."""
        current_state = self.task_context.task_state
        
        # Check if transition is valid
        if new_state not in self.valid_transitions.get(current_state, []):
            self._logger.warning(
                f"Invalid task state transition: {current_state.name} -> {new_state.name}",
                extra={
                    "task_id": self.task_context.task_id,
                    "reason": reason
                }
            )
            return False
        
        try:
            # Record state history
            self.task_context.state_history.append((current_state, datetime.now()))
            
            # Update state
            self.task_context.task_state = new_state
            
            # Update timestamps based on state
            now = datetime.now()
            if new_state == TaskState.CLAIMED:
                self.task_context.claimed_at = now
            elif new_state == TaskState.EXECUTING:
                self.task_context.execution_start = now
            elif new_state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
                self.task_context.execution_end = now
            
            self._logger.info(
                f"Task state transition: {current_state.name} -> {new_state.name}",
                extra={
                    "task_id": self.task_context.task_id,
                    "reason": reason,
                    "timestamp": now.isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self._logger.error(
                f"Error during task state transition: {e}",
                extra={
                    "task_id": self.task_context.task_id,
                    "current_state": current_state.name,
                    "target_state": new_state.name
                }
            )
            return False
    
    def get_valid_transitions(self) -> List[TaskState]:
        """Get valid transitions from current state."""
        return self.valid_transitions.get(self.task_context.task_state, [])
    
    def can_transition_to(self, new_state: TaskState) -> bool:
        """Check if transition to new state is valid."""
        return new_state in self.get_valid_transitions()
    
    def is_terminal_state(self) -> bool:
        """Check if current state is terminal."""
        return len(self.get_valid_transitions()) == 0
    
    def get_state_duration(self) -> Optional[float]:
        """Get duration in current state in seconds."""
        if not self.task_context.state_history:
            return None
        
        last_transition_time = self.task_context.state_history[-1][1]
        return (datetime.now() - last_transition_time).total_seconds()
    
    def get_total_execution_time(self) -> Optional[float]:
        """Get total execution time in seconds."""
        if not self.task_context.execution_start:
            return None
        
        end_time = self.task_context.execution_end or datetime.now()
        return (end_time - self.task_context.execution_start).total_seconds()