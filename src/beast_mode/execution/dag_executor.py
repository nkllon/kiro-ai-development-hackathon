"""
DAG Executor for Beast Mode Framework
Provides systematic DAG-based task execution with observability
"""

import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, GracefulDegradationResult


@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskDefinition:
    """Definition of a task in the DAG"""
    task_id: str
    dependencies: List[str] = field(default_factory=list)
    executor: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    max_retries: int = 0
    timeout_seconds: Optional[float] = None


class DAGExecutor(ReflectiveModule):
    """
    DAG-based task executor with Beast Mode observability
    
    Features:
    - Automatic dependency resolution
    - Parallel execution within constraints
    - Comprehensive error handling and retries
    - Real-time progress tracking
    - Systematic logging and metrics
    """
    
    def __init__(self, max_concurrent: int = 10):
        super().__init__()
        self.max_concurrent = max_concurrent
        self.tasks: Dict[str, TaskDefinition] = {}
        self.results: Dict[str, TaskResult] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.execution_id = f"dag-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        
        # Task state tracking
        self.pending_tasks: Set[str] = set()
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        
        # Execution callbacks
        self.on_task_start: Optional[Callable[[str], None]] = None
        self.on_task_complete: Optional[Callable[[str, TaskResult], None]] = None
        self.on_task_fail: Optional[Callable[[str, TaskResult], None]] = None
        
        self.logger = logging.getLogger(f"DAGExecutor-{self.execution_id}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": f"dag_executor_{self.execution_id}",
            "name": "DAG Executor",
            "version": "1.0.0",
            "description": "DAG-based task executor with Beast Mode observability",
            "execution_id": self.execution_id,
            "max_concurrent": self.max_concurrent,
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "running_tasks": len(self.running_tasks)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        issues = []
        
        # Check for failed tasks
        if len(self.failed_tasks) > 0:
            issues.append(f"{len(self.failed_tasks)} tasks have failed")
        
        # Check for stuck execution
        if len(self.running_tasks) == 0 and len(self.pending_tasks) > 0:
            issues.append("Execution appears stuck - no running tasks but pending tasks remain")
        
        # Check resource utilization
        if len(self.running_tasks) > self.max_concurrent:
            issues.append(f"Running tasks ({len(self.running_tasks)}) exceed max concurrent ({self.max_concurrent})")
        
        # Determine status
        if not issues:
            status = ModuleStatus.HEALTHY
            health_score = 1.0
        elif len(self.failed_tasks) == 0:
            status = ModuleStatus.WARNING
            health_score = 0.7
        else:
            status = ModuleStatus.ERROR
            health_score = max(0.1, 1.0 - (len(self.failed_tasks) / len(self.tasks)))
        
        return ModuleHealth(
            module_id=f"dag_executor_{self.execution_id}",
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(timezone.utc),
            uptime_seconds=(datetime.now(timezone.utc) - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation"""
        try:
            # Cancel running tasks gracefully
            cancelled_tasks = []
            for task_id, task in self.running_tasks.items():
                if not task.done():
                    task.cancel()
                    cancelled_tasks.append(task_id)
            
            # Move cancelled tasks back to pending
            for task_id in cancelled_tasks:
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
                    self.pending_tasks.add(task_id)
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[ModuleCapability.DATA_PROCESSING] if cancelled_tasks else [],
                remaining_capabilities=[
                    ModuleCapability.CORE_FUNCTIONALITY,
                    ModuleCapability.VALIDATION,
                    ModuleCapability.MONITORING
                ]
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.DATA_PROCESSING, ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[ModuleCapability.MONITORING],
                error_message=str(e)
            )
    
    def add_task(self, task_id: str, dependencies: List[str] = None, 
                 executor: Callable = None, **metadata) -> 'DAGExecutor':
        """Add a task to the DAG"""
        if dependencies is None:
            dependencies = []
        
        self.tasks[task_id] = TaskDefinition(
            task_id=task_id,
            dependencies=dependencies,
            executor=executor,
            metadata=metadata
        )
        
        self.pending_tasks.add(task_id)
        self.logger.info(f"Added task: {task_id} (deps: {dependencies})")
        return self
    
    def validate_dag(self) -> Dict[str, Any]:
        """Validate the DAG structure"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
        
        # Check for missing dependencies
        for task_id, task_def in self.tasks.items():
            for dep in task_def.dependencies:
                if dep not in self.tasks:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Task '{task_id}' depends on non-existent task '{dep}'"
                    )
        
        # Check for cycles using DFS
        colors = {task_id: 0 for task_id in self.tasks}  # 0=white, 1=gray, 2=black
        cycles = []
        
        def dfs(node: str, path: List[str]) -> bool:
            if colors[node] == 1:  # Gray - cycle detected
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return True
            
            if colors[node] == 2:  # Black - already processed
                return False
            
            colors[node] = 1  # Mark as gray
            
            for dep in self.tasks[node].dependencies:
                if dep in self.tasks and dfs(dep, path + [node]):
                    return True
            
            colors[node] = 2  # Mark as black
            return False
        
        for task_id in self.tasks:
            if colors[task_id] == 0:
                if dfs(task_id, []):
                    validation_result["valid"] = False
        
        if cycles:
            validation_result["errors"].extend([
                f"Circular dependency: {' → '.join(cycle)}" for cycle in cycles
            ])
        
        # Calculate statistics
        validation_result["statistics"] = {
            "total_tasks": len(self.tasks),
            "total_dependencies": sum(len(task.dependencies) for task in self.tasks.values()),
            "max_parallelization": self._calculate_max_parallelization(),
            "execution_levels": len(self._get_execution_levels())
        }
        
        return validation_result
    
    def _calculate_max_parallelization(self) -> int:
        """Calculate maximum number of tasks that can run in parallel"""
        levels = self._get_execution_levels()
        return max(len(tasks) for tasks in levels.values()) if levels else 0
    
    def _get_execution_levels(self) -> Dict[int, List[str]]:
        """Get tasks grouped by execution level"""
        # Topological sort to determine levels
        in_degree = {task_id: 0 for task_id in self.tasks}
        
        for task_def in self.tasks.values():
            for dep in task_def.dependencies:
                if dep in in_degree:
                    in_degree[task_def.task_id] += 1
        
        levels = {}
        current_level = 0
        remaining_tasks = set(self.tasks.keys())
        
        while remaining_tasks:
            # Find tasks with no remaining dependencies
            ready_tasks = [
                task_id for task_id in remaining_tasks 
                if in_degree[task_id] == 0
            ]
            
            if not ready_tasks:
                # Circular dependency - should be caught in validation
                break
            
            levels[current_level] = ready_tasks
            
            # Remove ready tasks and update in-degrees
            for task_id in ready_tasks:
                remaining_tasks.remove(task_id)
                
                # Reduce in-degree for dependent tasks
                for other_task_id, other_task_def in self.tasks.items():
                    if task_id in other_task_def.dependencies:
                        in_degree[other_task_id] -= 1
            
            current_level += 1
        
        return levels
    
    def _get_ready_tasks(self) -> List[str]:
        """Get tasks that are ready to execute (dependencies satisfied)"""
        ready_tasks = []
        
        for task_id in self.pending_tasks:
            task_def = self.tasks[task_id]
            
            # Check if all dependencies are completed
            dependencies_satisfied = all(
                dep in self.completed_tasks for dep in task_def.dependencies
            )
            
            if dependencies_satisfied:
                ready_tasks.append(task_id)
        
        return ready_tasks
    
    async def _execute_task(self, task_id: str) -> TaskResult:
        """Execute a single task"""
        task_def = self.tasks[task_id]
        
        # Create result object
        result = TaskResult(
            task_id=task_id,
            success=False,
            started_at=datetime.now(timezone.utc)
        )
        
        self.logger.info(f"Starting task: {task_id}")
        
        # Call start callback
        if self.on_task_start:
            try:
                self.on_task_start(task_id)
            except Exception as e:
                self.logger.warning(f"Task start callback failed for {task_id}: {e}")
        
        try:
            start_time = time.time()
            
            # Execute the task
            if task_def.executor:
                if asyncio.iscoroutinefunction(task_def.executor):
                    result.result = await task_def.executor(task_id, task_def.metadata)
                else:
                    result.result = task_def.executor(task_id, task_def.metadata)
            else:
                # Default behavior - just mark as completed
                result.result = {"status": "completed", "task_id": task_id}
            
            result.success = True
            result.duration_seconds = time.time() - start_time
            result.completed_at = datetime.now(timezone.utc)
            
            self.logger.info(f"Completed task: {task_id} ({result.duration_seconds:.2f}s)")
            
            # Call completion callback
            if self.on_task_complete:
                try:
                    self.on_task_complete(task_id, result)
                except Exception as e:
                    self.logger.warning(f"Task completion callback failed for {task_id}: {e}")
        
        except Exception as e:
            result.success = False
            result.error = str(e)
            result.duration_seconds = time.time() - start_time
            result.completed_at = datetime.now(timezone.utc)
            
            self.logger.error(f"Failed task: {task_id} - {e}")
            
            # Call failure callback
            if self.on_task_fail:
                try:
                    self.on_task_fail(task_id, result)
                except Exception as e:
                    self.logger.warning(f"Task failure callback failed for {task_id}: {e}")
        
        return result
    
    async def execute(self) -> Dict[str, TaskResult]:
        """Execute the entire DAG"""
        self.logger.info(f"Starting DAG execution: {self.execution_id}")
        self.logger.info(f"Total tasks: {len(self.tasks)}, Max concurrent: {self.max_concurrent}")
        
        # Validate DAG before execution
        validation = self.validate_dag()
        if not validation["valid"]:
            raise ValueError(f"Invalid DAG: {validation['errors']}")
        
        start_time = time.time()
        
        try:
            while self.pending_tasks or self.running_tasks:
                # Start new tasks if we have capacity
                ready_tasks = self._get_ready_tasks()
                available_slots = self.max_concurrent - len(self.running_tasks)
                tasks_to_start = ready_tasks[:available_slots]
                
                for task_id in tasks_to_start:
                    self.pending_tasks.remove(task_id)
                    
                    # Start the task
                    task_coroutine = self._execute_task(task_id)
                    self.running_tasks[task_id] = asyncio.create_task(task_coroutine)
                
                # Wait for at least one task to complete
                if self.running_tasks:
                    done, pending = await asyncio.wait(
                        self.running_tasks.values(),
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    # Process completed tasks
                    for task in done:
                        # Find which task this was
                        completed_task_id = None
                        for task_id, running_task in self.running_tasks.items():
                            if running_task == task:
                                completed_task_id = task_id
                                break
                        
                        if completed_task_id:
                            # Get the result
                            result = await task
                            self.results[completed_task_id] = result
                            
                            # Update task state
                            del self.running_tasks[completed_task_id]
                            
                            if result.success:
                                self.completed_tasks.add(completed_task_id)
                            else:
                                self.failed_tasks.add(completed_task_id)
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
        
        except Exception as e:
            self.logger.error(f"DAG execution failed: {e}")
            raise
        
        finally:
            # Cancel any remaining tasks
            for task in self.running_tasks.values():
                if not task.done():
                    task.cancel()
        
        execution_time = time.time() - start_time
        
        # Log summary
        total_tasks = len(self.tasks)
        completed_count = len(self.completed_tasks)
        failed_count = len(self.failed_tasks)
        
        self.logger.info(f"DAG execution completed in {execution_time:.2f}s")
        self.logger.info(f"Tasks: {completed_count}/{total_tasks} completed, {failed_count} failed")
        
        return self.results
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution results"""
        total_tasks = len(self.tasks)
        completed_count = len(self.completed_tasks)
        failed_count = len(self.failed_tasks)
        pending_count = len(self.pending_tasks)
        running_count = len(self.running_tasks)
        
        total_duration = sum(
            result.duration_seconds for result in self.results.values()
            if result.duration_seconds
        )
        
        return {
            "execution_id": self.execution_id,
            "total_tasks": total_tasks,
            "completed": completed_count,
            "failed": failed_count,
            "pending": pending_count,
            "running": running_count,
            "success_rate": completed_count / total_tasks if total_tasks > 0 else 0,
            "total_duration_seconds": total_duration,
            "failed_tasks": list(self.failed_tasks),
            "completed_tasks": list(self.completed_tasks)
        }