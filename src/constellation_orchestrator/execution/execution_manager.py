"""Execution management for Constellation Orchestrator."""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any
import structlog

from ..core.config import ConstellationConfig
from ..models.execution_state import ExecutionResult
from ..models.task_definition import TaskDefinition, TaskStatus
from ..agents.agent_manager import AgentManager
from ..status.status_manager import StatusManager


class ExecutionManager:
    """Manages task execution with parallel processing and retry logic."""
    
    def __init__(self, config: ConstellationConfig, agent_manager: AgentManager, status_manager: StatusManager):
        """Initialize execution manager."""
        self.config = config
        self.agent_manager = agent_manager
        self.status_manager = status_manager
        self.logger = structlog.get_logger(__name__)
        
        # Execution state
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_definitions: Dict[str, TaskDefinition] = {}
        
        self.logger.info("execution_manager_initialized")
    
    async def initialize(self) -> bool:
        """Initialize execution manager."""
        try:
            self.logger.info("execution_manager_initializing")
            return True
        except Exception as e:
            self.logger.error(
                "execution_manager_initialization_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def execute_task(self, task_id: str, task_definition: TaskDefinition) -> ExecutionResult:
        """Execute a single task with an available agent."""
        try:
            self.logger.info(
                "execution_manager_executing_task",
                task_id=task_id,
                prompt_length=len(task_definition.prompt)
            )
            
            # Store task definition
            self.task_definitions[task_id] = task_definition
            
            # Get available agent
            agent = await self.agent_manager.get_available_agent()
            if not agent:
                self.logger.error(
                    "execution_manager_no_available_agent",
                    task_id=task_id
                )
                return ExecutionResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error="No available agents",
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow()
                )
            
            # Execute task with retry logic
            result = await self._execute_with_retry(task_definition, agent)
            
            self.logger.info(
                "execution_manager_task_completed",
                task_id=task_id,
                status=result.status.value,
                duration=result.duration,
                agent_id=result.agent_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "execution_manager_task_execution_failed",
                task_id=task_id,
                error=str(e),
                error_type=type(e).__name__
            )
            
            return ExecutionResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=f"Execution error: {str(e)}",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow()
            )
    
    async def _execute_with_retry(self, task_definition: TaskDefinition, agent) -> ExecutionResult:
        """Execute task with retry logic."""
        last_result = None
        
        for attempt in range(task_definition.retry_count + 1):
            try:
                self.logger.debug(
                    "execution_manager_task_attempt",
                    task_id=task_definition.task_id,
                    attempt=attempt + 1,
                    max_attempts=task_definition.retry_count + 1,
                    agent_id=agent.agent_id
                )
                
                # Execute the task
                result = await agent.execute_prompt(task_definition)
                result.retry_count = attempt
                
                # If successful, return immediately
                if result.status == TaskStatus.COMPLETED:
                    return result
                
                # Store the result for potential retry
                last_result = result
                
                # If this was the last attempt, return the failed result
                if attempt >= task_definition.retry_count:
                    break
                
                # Wait before retry (exponential backoff)
                retry_delay = min(2 ** attempt, 30)  # Max 30 seconds
                self.logger.info(
                    "execution_manager_task_retry",
                    task_id=task_definition.task_id,
                    attempt=attempt + 1,
                    retry_delay=retry_delay,
                    error=result.error
                )
                
                await asyncio.sleep(retry_delay)
                
                # Try to get a different agent for retry
                new_agent = await self.agent_manager.get_available_agent()
                if new_agent and new_agent.agent_id != agent.agent_id:
                    agent = new_agent
                    self.logger.debug(
                        "execution_manager_retry_different_agent",
                        task_id=task_definition.task_id,
                        new_agent_id=agent.agent_id
                    )
                
            except Exception as e:
                self.logger.error(
                    "execution_manager_retry_attempt_failed",
                    task_id=task_definition.task_id,
                    attempt=attempt + 1,
                    error=str(e),
                    error_type=type(e).__name__
                )
                
                last_result = ExecutionResult(
                    task_id=task_definition.task_id,
                    status=TaskStatus.FAILED,
                    error=f"Retry attempt {attempt + 1} failed: {str(e)}",
                    retry_count=attempt,
                    agent_id=agent.agent_id,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow()
                )
        
        return last_result or ExecutionResult(
            task_id=task_definition.task_id,
            status=TaskStatus.FAILED,
            error="All retry attempts failed",
            retry_count=task_definition.retry_count,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
    
    async def execute_parallel(self, task_ids: List[str], max_concurrent: int) -> List[ExecutionResult]:
        """Execute multiple tasks in parallel with concurrency limit."""
        try:
            self.logger.info(
                "execution_manager_parallel_execution_starting",
                task_count=len(task_ids),
                max_concurrent=max_concurrent
            )
            
            # Get task definitions
            tasks_to_execute = []
            for task_id in task_ids:
                if task_id in self.task_definitions:
                    tasks_to_execute.append((task_id, self.task_definitions[task_id]))
                else:
                    self.logger.warning(
                        "execution_manager_task_definition_missing",
                        task_id=task_id
                    )
            
            if not tasks_to_execute:
                self.logger.warning("execution_manager_no_tasks_to_execute")
                return []
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def execute_with_semaphore(task_id: str, task_def: TaskDefinition) -> ExecutionResult:
                async with semaphore:
                    return await self.execute_task(task_id, task_def)
            
            # Create tasks for parallel execution
            execution_tasks = [
                execute_with_semaphore(task_id, task_def)
                for task_id, task_def in tasks_to_execute
            ]
            
            # Execute all tasks
            results = await asyncio.gather(*execution_tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                task_id, task_def = tasks_to_execute[i]
                
                if isinstance(result, Exception):
                    self.logger.error(
                        "execution_manager_parallel_task_exception",
                        task_id=task_id,
                        error=str(result),
                        error_type=type(result).__name__
                    )
                    
                    processed_results.append(ExecutionResult(
                        task_id=task_id,
                        status=TaskStatus.FAILED,
                        error=f"Parallel execution exception: {str(result)}",
                        start_time=datetime.utcnow(),
                        end_time=datetime.utcnow()
                    ))
                else:
                    processed_results.append(result)
            
            # Log summary
            completed_count = sum(1 for r in processed_results if r.status == TaskStatus.COMPLETED)
            failed_count = sum(1 for r in processed_results if r.status == TaskStatus.FAILED)
            
            self.logger.info(
                "execution_manager_parallel_execution_completed",
                total_tasks=len(processed_results),
                completed_tasks=completed_count,
                failed_tasks=failed_count,
                success_rate=completed_count / len(processed_results) if processed_results else 0.0
            )
            
            return processed_results
            
        except Exception as e:
            self.logger.error(
                "execution_manager_parallel_execution_failed",
                task_count=len(task_ids),
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Return failed results for all tasks
            return [
                ExecutionResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=f"Parallel execution failed: {str(e)}",
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow()
                )
                for task_id in task_ids
            ]
    
    async def retry_task(self, task_id: str, exclude_agent: Optional[str] = None) -> Optional[ExecutionResult]:
        """Retry a specific task, optionally excluding a specific agent."""
        try:
            if task_id not in self.task_definitions:
                self.logger.error(
                    "execution_manager_retry_task_not_found",
                    task_id=task_id
                )
                return None
            
            task_definition = self.task_definitions[task_id]
            
            # Get available agent (excluding specified agent if provided)
            agent = await self.agent_manager.get_available_agent()
            if not agent:
                self.logger.error(
                    "execution_manager_retry_no_available_agent",
                    task_id=task_id
                )
                return None
            
            # If we need to exclude a specific agent, try to get a different one
            if exclude_agent and agent.agent_id == exclude_agent:
                # Try to find a different agent
                all_agents = await self.agent_manager.get_agent_status()
                for agent_id, status in all_agents.items():
                    if agent_id != exclude_agent and status == "available":
                        agent = self.agent_manager.agents.get(agent_id)
                        break
                
                if not agent or agent.agent_id == exclude_agent:
                    self.logger.warning(
                        "execution_manager_retry_could_not_exclude_agent",
                        task_id=task_id,
                        exclude_agent=exclude_agent
                    )
            
            self.logger.info(
                "execution_manager_retrying_task",
                task_id=task_id,
                agent_id=agent.agent_id,
                excluded_agent=exclude_agent
            )
            
            # Execute the retry
            result = await agent.execute_prompt(task_definition)
            
            return result
            
        except Exception as e:
            self.logger.error(
                "execution_manager_retry_task_failed",
                task_id=task_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return None
    
    def add_task_definition(self, task_definition: TaskDefinition) -> None:
        """Add a task definition to the execution manager."""
        self.task_definitions[task_definition.task_id] = task_definition
    
    def add_task_definitions(self, task_definitions: List[TaskDefinition]) -> None:
        """Add multiple task definitions to the execution manager."""
        for task_def in task_definitions:
            self.task_definitions[task_def.task_id] = task_def
    
    def get_running_task_count(self) -> int:
        """Get number of currently running tasks."""
        return len(self.running_tasks)
    
    def get_task_definition(self, task_id: str) -> Optional[TaskDefinition]:
        """Get task definition by ID."""
        return self.task_definitions.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        try:
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                del self.running_tasks[task_id]
                
                self.logger.info(
                    "execution_manager_task_cancelled",
                    task_id=task_id
                )
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(
                "execution_manager_cancel_task_failed",
                task_id=task_id,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def cancel_all_tasks(self) -> int:
        """Cancel all running tasks."""
        try:
            cancelled_count = 0
            
            for task_id in list(self.running_tasks.keys()):
                if await self.cancel_task(task_id):
                    cancelled_count += 1
            
            self.logger.info(
                "execution_manager_all_tasks_cancelled",
                cancelled_count=cancelled_count
            )
            
            return cancelled_count
            
        except Exception as e:
            self.logger.error(
                "execution_manager_cancel_all_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return 0
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        try:
            return {
                'running_tasks': len(self.running_tasks),
                'total_task_definitions': len(self.task_definitions),
                'agent_statistics': self.agent_manager.get_pool_statistics()
            }
            
        except Exception as e:
            self.logger.error(
                "execution_manager_get_statistics_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {}
    
    async def health_check(self) -> bool:
        """Health check for execution manager."""
        try:
            # Check agent manager health
            agent_health = await self.agent_manager.health_check()
            
            # Check if we have task definitions (if we're supposed to)
            # This is a basic check - in a real scenario, we might have more sophisticated health checks
            
            return agent_health
            
        except Exception as e:
            self.logger.error(
                "execution_manager_health_check_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def shutdown(self) -> None:
        """Shutdown execution manager."""
        try:
            self.logger.info("execution_manager_shutting_down")
            
            # Cancel all running tasks
            cancelled_count = await self.cancel_all_tasks()
            
            # Clear task definitions
            self.task_definitions.clear()
            
            self.logger.info(
                "execution_manager_shutdown_complete",
                cancelled_tasks=cancelled_count
            )
            
        except Exception as e:
            self.logger.error(
                "execution_manager_shutdown_error",
                error=str(e),
                error_type=type(e).__name__
            )