"""
Task processing workflow integrated with conversation state machine.

This module implements the core task processing logic that coordinates
between task execution, conversation state management, and error recovery.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import uuid
import traceback

from .models import (
    ConversationContext,
    TaskContext,
    TaskState,
    ConversationState,
    StateTransitionTrigger,
    TaskResult,
    TaskFailure,
    HookEvent,
)
from .state_machine import ConversationStateMachine, TaskStateMachine
from .persistence import StatePersistenceManager


class TaskExecutionContext:
    """Isolated execution context for task processing."""
    
    def __init__(self, task: TaskContext, conversation: ConversationContext):
        self.task = task
        self.conversation = conversation
        self.execution_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        self.resources_allocated = {}
        self.cleanup_callbacks = []
    
    def add_cleanup_callback(self, callback: Callable):
        """Add cleanup callback for resource management."""
        self.cleanup_callbacks.append(callback)
    
    async def cleanup(self):
        """Execute all cleanup callbacks."""
        for callback in self.cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logging.getLogger(__name__).warning(f"Cleanup callback failed: {e}")


class TaskProcessor:
    """Processes tasks with full state machine integration."""
    
    def __init__(self, persistence_manager: StatePersistenceManager):
        self.persistence = persistence_manager
        self._logger = logging.getLogger(f"{__name__}.TaskProcessor")
        self.task_handlers: Dict[str, Callable] = {}
        self.active_executions: Dict[str, TaskExecutionContext] = {}
        
        # Register default task handlers
        self._register_default_handlers()
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a handler for specific task type."""
        self.task_handlers[task_type] = handler
        self._logger.info(f"Registered task handler for type: {task_type}")
    
    async def process_task_workflow(
        self, 
        conversation_context: ConversationContext,
        task: TaskContext
    ) -> TaskResult:
        """
        Process complete task workflow with state machine integration.
        
        This implements the full workflow:
        IDLE -> HOOK_TRIGGERED -> TASK_PENDING -> STATE_SNAPSHOT -> 
        TASK_EXECUTING -> TASK_COMPLETE -> STATE_PERSIST -> CLEANUP_TEMP -> IDLE
        """
        conversation_sm = ConversationStateMachine(conversation_context, self.persistence)
        task_sm = TaskStateMachine(task)
        execution_context = None
        
        try:
            self._logger.info(
                f"Starting task processing workflow: {task.task_id}",
                extra={
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "conversation_id": conversation_context.conversation_id
                }
            )
            
            # Step 1: Trigger hook execution (IDLE -> HOOK_TRIGGERED)
            hook_event = HookEvent(
                event_type="task_processing",
                event_data={"task_id": task.task_id, "task_type": task.task_type}
            )
            success = await conversation_sm.trigger_transition(
                StateTransitionTrigger.HOOK_EXECUTION,
                hook_event=hook_event
            )
            if not success:
                raise Exception("Failed to transition to HOOK_TRIGGERED")
            
            # Step 2: Transition to TASK_PENDING (HOOK_TRIGGERED -> TASK_PENDING)
            success = await conversation_sm.trigger_transition(
                StateTransitionTrigger.TASK_AVAILABLE,
                task=task
            )
            if not success:
                raise Exception("Failed to transition to TASK_PENDING")
            
            # Step 3: Claim and validate task
            await task_sm.transition_to(TaskState.CLAIMED, "Task claimed for processing")
            await task_sm.transition_to(TaskState.VALIDATED, "Task validation completed")
            
            # Step 4: Create state snapshot (TASK_PENDING -> STATE_SNAPSHOT)
            success = await conversation_sm.trigger_transition(
                StateTransitionTrigger.TASK_START
            )
            if not success:
                raise Exception("Failed to create state snapshot")
            
            # Step 5: Begin task execution (STATE_SNAPSHOT -> TASK_EXECUTING)
            success = await conversation_sm.trigger_transition(
                StateTransitionTrigger.TASK_START
            )
            if not success:
                raise Exception("Failed to transition to TASK_EXECUTING")
            
            await task_sm.transition_to(TaskState.EXECUTING, "Task execution started")
            
            # Step 6: Execute the actual task
            execution_context = TaskExecutionContext(task, conversation_context)
            self.active_executions[task.task_id] = execution_context
            
            task_result = await self._execute_task_with_isolation(execution_context)
            
            # Step 7: Handle execution result
            if task_result.success:
                await task_sm.transition_to(TaskState.COMPLETED, "Task completed successfully")
                
                # Transition conversation state to complete
                success = await conversation_sm.trigger_transition(
                    StateTransitionTrigger.TASK_SUCCESS
                )
                if not success:
                    self._logger.warning("Failed to transition to TASK_COMPLETE state")
                
                # Persist state
                success = await conversation_sm.trigger_transition(
                    StateTransitionTrigger.CLEANUP_REQUIRED
                )
                if not success:
                    self._logger.warning("Failed to transition to STATE_PERSIST")
                
                # Final cleanup
                success = await conversation_sm.trigger_transition(
                    StateTransitionTrigger.CLEANUP_REQUIRED
                )
                if not success:
                    self._logger.warning("Failed to transition to CLEANUP_TEMP")
                
                # Return to idle
                success = await conversation_sm.trigger_transition(
                    StateTransitionTrigger.CLEANUP_REQUIRED
                )
                if not success:
                    self._logger.warning("Failed to return to IDLE state")
                
            else:
                # Handle task failure
                await task_sm.transition_to(TaskState.FAILED, f"Task failed: {task_result.error_message}")
                
                # Trigger error recovery
                success = await conversation_sm.trigger_transition(
                    StateTransitionTrigger.TASK_FAILURE,
                    error=Exception(task_result.error_message)
                )
                if not success:
                    self._logger.error("Failed to trigger error recovery")
            
            self._logger.info(
                f"Task processing workflow completed: {task.task_id}",
                extra={
                    "task_id": task.task_id,
                    "success": task_result.success,
                    "execution_time_ms": task_result.execution_time_ms
                }
            )
            
            return task_result
            
        except Exception as e:
            self._logger.error(
                f"Error in task processing workflow: {e}",
                extra={
                    "task_id": task.task_id,
                    "conversation_id": conversation_context.conversation_id,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            
            # Attempt error recovery
            try:
                await task_sm.transition_to(TaskState.FAILED, f"Workflow error: {str(e)}")
                await conversation_sm.trigger_transition(
                    StateTransitionTrigger.ERROR_DETECTED,
                    error=e
                )
            except Exception as recovery_error:
                self._logger.error(f"Error recovery failed: {recovery_error}")
            
            # Return failure result
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e),
                execution_time_ms=(datetime.now() - task.created_at).total_seconds() * 1000
            )
            
        finally:
            # Cleanup execution context
            if execution_context:
                await execution_context.cleanup()
                self.active_executions.pop(task.task_id, None)
    
    async def _execute_task_with_isolation(self, execution_context: TaskExecutionContext) -> TaskResult:
        """Execute task with proper isolation and resource tracking."""
        task = execution_context.task
        start_time = datetime.now()
        
        try:
            # Get task handler
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise Exception(f"No handler registered for task type: {task.task_type}")
            
            # Set up resource monitoring
            execution_context.add_cleanup_callback(
                lambda: self._logger.info(f"Cleaned up resources for task: {task.task_id}")
            )
            
            # Execute task with timeout
            timeout_seconds = task.task_parameters.get("timeout_seconds", 30)
            
            try:
                result_data = await asyncio.wait_for(
                    handler(task, execution_context),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                raise Exception(f"Task execution timed out after {timeout_seconds} seconds")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result_data=result_data or {},
                execution_time_ms=execution_time,
                completed_at=datetime.now()
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self._logger.error(
                f"Task execution failed: {task.task_id}: {e}",
                extra={
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "execution_time_ms": execution_time,
                    "error": str(e)
                }
            )
            
            return TaskResult(
                task_id=task.task_id,
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time,
                completed_at=datetime.now()
            )
    
    def _register_default_handlers(self):
        """Register default task handlers for common task types."""
        
        async def code_generation_handler(task: TaskContext, context: TaskExecutionContext) -> Dict[str, Any]:
            """Handle code generation tasks."""
            self._logger.info(f"Processing code generation task: {task.task_id}")
            
            # Simulate code generation (in real implementation, this would call Claude)
            await asyncio.sleep(0.1)  # Simulate processing time
            
            return {
                "generated_code": f"# Generated code for task {task.task_id}",
                "language": task.task_parameters.get("language", "python"),
                "lines_generated": 42
            }
        
        async def file_analysis_handler(task: TaskContext, context: TaskExecutionContext) -> Dict[str, Any]:
            """Handle file analysis tasks."""
            self._logger.info(f"Processing file analysis task: {task.task_id}")
            
            # Simulate file analysis
            await asyncio.sleep(0.05)
            
            return {
                "analysis_result": "File analysis completed",
                "file_path": task.task_parameters.get("file_path", "unknown"),
                "issues_found": 0
            }
        
        async def documentation_handler(task: TaskContext, context: TaskExecutionContext) -> Dict[str, Any]:
            """Handle documentation tasks."""
            self._logger.info(f"Processing documentation task: {task.task_id}")
            
            # Simulate documentation generation
            await asyncio.sleep(0.08)
            
            return {
                "documentation": f"Documentation for task {task.task_id}",
                "format": task.task_parameters.get("format", "markdown"),
                "sections_generated": 3
            }
        
        async def testing_handler(task: TaskContext, context: TaskExecutionContext) -> Dict[str, Any]:
            """Handle testing tasks."""
            self._logger.info(f"Processing testing task: {task.task_id}")
            
            # Simulate test execution
            await asyncio.sleep(0.15)
            
            return {
                "test_results": "All tests passed",
                "tests_run": task.task_parameters.get("test_count", 5),
                "coverage_percent": 95.5
            }
        
        async def refactoring_handler(task: TaskContext, context: TaskExecutionContext) -> Dict[str, Any]:
            """Handle refactoring tasks."""
            self._logger.info(f"Processing refactoring task: {task.task_id}")
            
            # Simulate refactoring
            await asyncio.sleep(0.12)
            
            return {
                "refactoring_result": "Refactoring completed",
                "files_modified": task.task_parameters.get("file_count", 1),
                "improvements": ["Reduced complexity", "Improved readability"]
            }
        
        # Register all default handlers
        self.register_task_handler("code_generation", code_generation_handler)
        self.register_task_handler("file_analysis", file_analysis_handler)
        self.register_task_handler("documentation", documentation_handler)
        self.register_task_handler("testing", testing_handler)
        self.register_task_handler("refactoring", refactoring_handler)
    
    async def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get information about currently active task executions."""
        active_info = []
        
        for task_id, context in self.active_executions.items():
            execution_time = (datetime.now() - context.start_time).total_seconds()
            
            active_info.append({
                "task_id": task_id,
                "execution_id": context.execution_id,
                "task_type": context.task.task_type,
                "conversation_id": context.conversation.conversation_id,
                "execution_time_seconds": execution_time,
                "start_time": context.start_time.isoformat()
            })
        
        return active_info
    
    async def cancel_task_execution(self, task_id: str) -> bool:
        """Cancel an active task execution."""
        if task_id not in self.active_executions:
            return False
        
        try:
            context = self.active_executions[task_id]
            await context.cleanup()
            self.active_executions.pop(task_id, None)
            
            self._logger.info(f"Cancelled task execution: {task_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error cancelling task execution {task_id}: {e}")
            return False


class TaskWorkflowOrchestrator:
    """Orchestrates multiple task processing workflows."""
    
    def __init__(self, task_processor: TaskProcessor):
        self.task_processor = task_processor
        self._logger = logging.getLogger(f"{__name__}.TaskWorkflowOrchestrator")
        self.concurrent_limit = 5
        self.active_workflows = {}
    
    async def process_task_batch(
        self, 
        conversation_context: ConversationContext,
        tasks: List[TaskContext]
    ) -> List[TaskResult]:
        """Process a batch of tasks with concurrency control."""
        if not tasks:
            return []
        
        self._logger.info(
            f"Processing task batch: {len(tasks)} tasks",
            extra={"conversation_id": conversation_context.conversation_id}
        )
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.concurrent_limit)
        
        async def process_single_task(task: TaskContext) -> TaskResult:
            async with semaphore:
                return await self.task_processor.process_task_workflow(
                    conversation_context, task
                )
        
        # Process all tasks concurrently
        try:
            results = await asyncio.gather(
                *[process_single_task(task) for task in tasks],
                return_exceptions=True
            )
            
            # Convert exceptions to failed task results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(TaskResult(
                        task_id=tasks[i].task_id,
                        success=False,
                        error_message=str(result),
                        execution_time_ms=0.0
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self._logger.error(f"Error processing task batch: {e}")
            
            # Return failure results for all tasks
            return [
                TaskResult(
                    task_id=task.task_id,
                    success=False,
                    error_message=f"Batch processing error: {str(e)}",
                    execution_time_ms=0.0
                )
                for task in tasks
            ]
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get status of all active workflows."""
        active_executions = await self.task_processor.get_active_executions()
        
        return {
            "active_workflows": len(self.active_workflows),
            "active_executions": len(active_executions),
            "concurrent_limit": self.concurrent_limit,
            "executions": active_executions
        }