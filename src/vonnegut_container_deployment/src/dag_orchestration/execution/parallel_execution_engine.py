#!/usr/bin/env python3
"""
Parallel Execution Engine for DAG Orchestration
===============================================

Base parallel execution framework that integrates with existing DAG infrastructure
to provide dependency-aware parallel task execution.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)
from src.rm_ddd.core.dag_registry import DAGRegistry
from src.dag_orchestration.core.infrastructure_validator import InfrastructureValidator


class TaskExecutionStatus(Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ExecutionStrategy(Enum):
    """Parallel execution strategy options."""
    AGGRESSIVE = "aggressive"  # Maximum parallelism
    CONSERVATIVE = "conservative"  # Balanced approach
    SEQUENTIAL = "sequential"  # Fallback to sequential execution


@dataclass
class TaskDefinition:
    """Definition of a task for parallel execution."""
    task_id: str
    name: str
    dependencies: Set[str] = field(default_factory=set)
    execution_function: Optional[Callable] = None
    execution_args: Tuple = field(default_factory=tuple)
    execution_kwargs: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 0  # Higher number = higher priority


@dataclass
class TaskExecutionResult:
    """Result of task execution."""
    task_id: str
    status: TaskExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    resource_usage: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """Context for parallel execution session."""
    execution_id: str
    strategy: ExecutionStrategy
    max_workers: int
    start_time: datetime
    tasks: Dict[str, TaskDefinition] = field(default_factory=dict)
    results: Dict[str, TaskExecutionResult] = field(default_factory=dict)
    active_futures: Dict[str, Future] = field(default_factory=dict)
    completed_tasks: Set[str] = field(default_factory=set)
    failed_tasks: Set[str] = field(default_factory=set)
    cancelled_tasks: Set[str] = field(default_factory=set)


class ParallelExecutionEngine(ReflectiveModule):
    """
    Base parallel execution framework for DAG orchestration.
    
    Provides:
    - DAG-aware parallel task execution
    - Dependency resolution and scheduling
    - Resource-aware concurrency management
    - Failure isolation and recovery
    - Integration with existing Beast Mode infrastructure
    """
    
    def __init__(self, max_workers: int = 10, execution_strategy: ExecutionStrategy = ExecutionStrategy.CONSERVATIVE):
        super().__init__()
        self.module_id = "ParallelExecutionEngine"
        self._max_workers = max_workers
        self._execution_strategy = execution_strategy
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Initialize components
        self._dag_registry = DAGRegistry()
        self._infrastructure_validator = InfrastructureValidator()
        
        # Execution state
        self._executor: Optional[ThreadPoolExecutor] = None
        self._current_execution: Optional[ExecutionContext] = None
        self._execution_lock = threading.Lock()
        
        # Statistics
        self._total_executions = 0
        self._successful_executions = 0
        self._failed_executions = 0
        self._total_tasks_executed = 0
        
        self._logger.info(f"ParallelExecutionEngine initialized with {max_workers} workers, strategy: {execution_strategy.value}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "ParallelExecutionEngine",
            "version": "1.0.0",
            "description": "Base parallel execution framework for DAG orchestration",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "configuration": {
                "max_workers": self._max_workers,
                "execution_strategy": self._execution_strategy.value,
                "executor_active": self._executor is not None,
                "current_execution_active": self._current_execution is not None
            },
            "statistics": {
                "total_executions": self._total_executions,
                "successful_executions": self._successful_executions,
                "failed_executions": self._failed_executions,
                "success_rate": self._successful_executions / max(self._total_executions, 1),
                "total_tasks_executed": self._total_tasks_executed
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            issues = []
            health_score = 1.0
            
            # Check infrastructure validator health
            infra_health = self._infrastructure_validator.get_health_status()
            if infra_health.status != ModuleStatus.HEALTHY:
                issues.append(f"Infrastructure validator unhealthy: {infra_health.status.value}")
                health_score *= 0.8
            
            # Check DAG registry health
            dag_health = self._dag_registry.validate_dag()
            if not dag_health:
                issues.append("DAG registry validation failed")
                health_score *= 0.7
            
            # Check execution statistics
            if self._total_executions > 0:
                success_rate = self._successful_executions / self._total_executions
                if success_rate < 0.8:  # Less than 80% success rate
                    issues.append(f"Low execution success rate: {success_rate:.1%}")
                    health_score *= 0.6
            
            # Check executor state
            if self._executor and self._executor._shutdown:
                issues.append("Thread pool executor is shutdown")
                health_score *= 0.9
            
            # Determine overall status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.WARNING
            else:
                status = ModuleStatus.ERROR
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, fall back to sequential execution
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.API_INTEGRATION  # May lose parallel execution
            ]
            
            # Switch to sequential execution strategy
            self._execution_strategy = ExecutionStrategy.SEQUENTIAL
            
            # Reduce worker count
            if self._executor:
                self._max_workers = min(self._max_workers, 2)
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    async def execute_dag_parallel(self, tasks: List[TaskDefinition], 
                                 execution_requirements: Optional[Dict[str, Any]] = None) -> Dict[str, TaskExecutionResult]:
        """
        Execute tasks in parallel following DAG dependencies.
        
        Args:
            tasks: List of task definitions to execute
            execution_requirements: Optional execution requirements for validation
            
        Returns:
            Dictionary mapping task_id to TaskExecutionResult
        """
        with self.trace_operation("execute_dag_parallel", 
                                task_count=len(tasks), 
                                execution_requirements=execution_requirements) as trace:
            
            # Validate infrastructure preconditions
            if execution_requirements:
                validation_passed, validation_report = await self._infrastructure_validator.validate_for_execution(execution_requirements)
                if not validation_passed:
                    raise RuntimeError(f"Infrastructure validation failed: {validation_report.recommendations}")
            
            # Create execution context
            execution_context = ExecutionContext(
                execution_id=str(uuid.uuid4()),
                strategy=self._execution_strategy,
                max_workers=self._max_workers,
                start_time=datetime.now(),
                tasks={task.task_id: task for task in tasks}
            )
            
            try:
                with self._execution_lock:
                    self._current_execution = execution_context
                    self._total_executions += 1
                
                # Validate DAG structure
                self._validate_task_dag(tasks)
                
                # Initialize thread pool executor
                self._initialize_executor()
                
                # Execute tasks following DAG dependencies
                results = await self._execute_tasks_with_dependencies(execution_context)
                
                # Update statistics
                if all(result.status == TaskExecutionStatus.COMPLETED for result in results.values()):
                    self._successful_executions += 1
                else:
                    self._failed_executions += 1
                
                self._total_tasks_executed += len(results)
                
                trace.output_result = {
                    'execution_id': execution_context.execution_id,
                    'total_tasks': len(tasks),
                    'completed_tasks': len(execution_context.completed_tasks),
                    'failed_tasks': len(execution_context.failed_tasks),
                    'execution_duration': (datetime.now() - execution_context.start_time).total_seconds()
                }
                
                return results
                
            finally:
                with self._execution_lock:
                    self._current_execution = None
    
    def _validate_task_dag(self, tasks: List[TaskDefinition]) -> None:
        """Validate that tasks form a valid DAG structure."""
        # Register tasks with DAG registry for validation
        for task in tasks:
            success = self._dag_registry.register_module(task.task_id, task.dependencies)
            if not success:
                raise ValueError(f"Task {task.task_id} creates circular dependency")
        
        # Validate overall DAG structure
        if not self._dag_registry.validate_dag():
            raise ValueError("Task dependencies do not form a valid DAG")
    
    def _initialize_executor(self) -> None:
        """Initialize thread pool executor if not already active."""
        if self._executor is None or self._executor._shutdown:
            self._executor = ThreadPoolExecutor(max_workers=self._max_workers)
            self._logger.info(f"Initialized ThreadPoolExecutor with {self._max_workers} workers")
    
    async def _execute_tasks_with_dependencies(self, context: ExecutionContext) -> Dict[str, TaskExecutionResult]:
        """Execute tasks following DAG dependency constraints."""
        
        while len(context.completed_tasks) + len(context.failed_tasks) + len(context.cancelled_tasks) < len(context.tasks):
            # Get tasks ready for execution
            ready_tasks = self._get_ready_tasks(context)
            
            if not ready_tasks and not context.active_futures:
                # No ready tasks and no active futures - deadlock or completion
                break
            
            # Submit ready tasks for execution
            for task in ready_tasks:
                future = self._submit_task_for_execution(task, context)
                context.active_futures[task.task_id] = future
            
            # Wait for at least one task to complete
            if context.active_futures:
                await self._wait_for_task_completion(context)
        
        return context.results
    
    def _get_ready_tasks(self, context: ExecutionContext) -> List[TaskDefinition]:
        """Get tasks that are ready for execution (dependencies satisfied)."""
        ready_tasks = []
        
        for task_id, task in context.tasks.items():
            # Skip if already processed or currently running
            if (task_id in context.completed_tasks or 
                task_id in context.failed_tasks or 
                task_id in context.cancelled_tasks or
                task_id in context.active_futures):
                continue
            
            # Check if all dependencies are satisfied
            dependencies_satisfied = all(
                dep_id in context.completed_tasks for dep_id in task.dependencies
            )
            
            # Check if any dependency failed (and task should be skipped)
            dependencies_failed = any(
                dep_id in context.failed_tasks for dep_id in task.dependencies
            )
            
            if dependencies_satisfied and not dependencies_failed:
                ready_tasks.append(task)
            elif dependencies_failed:
                # Mark task as skipped due to failed dependencies
                result = TaskExecutionResult(
                    task_id=task_id,
                    status=TaskExecutionStatus.SKIPPED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_seconds=0.0,
                    error_message="Skipped due to failed dependencies"
                )
                context.results[task_id] = result
                context.cancelled_tasks.add(task_id)
        
        # Sort by priority (higher priority first)
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        
        return ready_tasks
    
    def _submit_task_for_execution(self, task: TaskDefinition, context: ExecutionContext) -> Future:
        """Submit a task for execution in the thread pool."""
        
        def execute_task():
            """Execute the task and return result."""
            start_time = datetime.now()
            
            try:
                # Execute the task function
                if task.execution_function:
                    result = task.execution_function(*task.execution_args, **task.execution_kwargs)
                else:
                    result = f"Task {task.task_id} executed successfully (no function provided)"
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return TaskExecutionResult(
                    task_id=task.task_id,
                    status=TaskExecutionStatus.COMPLETED,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration,
                    result=result
                )
                
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return TaskExecutionResult(
                    task_id=task.task_id,
                    status=TaskExecutionStatus.FAILED,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration,
                    error=e,
                    error_message=str(e)
                )
        
        # Submit task to executor
        future = self._executor.submit(execute_task)
        self._logger.info(f"Submitted task {task.task_id} for execution")
        
        return future
    
    async def _wait_for_task_completion(self, context: ExecutionContext) -> None:
        """Wait for at least one active task to complete."""
        if not context.active_futures:
            return
        
        # Convert to asyncio-compatible waiting
        loop = asyncio.get_event_loop()
        
        # Wait for first completion
        done_futures = []
        for task_id, future in list(context.active_futures.items()):
            if future.done():
                done_futures.append((task_id, future))
        
        # If no futures are done, wait a short time and check again
        if not done_futures:
            await asyncio.sleep(0.1)
            return
        
        # Process completed futures
        for task_id, future in done_futures:
            try:
                result = future.result()
                context.results[task_id] = result
                
                if result.status == TaskExecutionStatus.COMPLETED:
                    context.completed_tasks.add(task_id)
                    self._logger.info(f"Task {task_id} completed successfully")
                else:
                    context.failed_tasks.add(task_id)
                    self._logger.error(f"Task {task_id} failed: {result.error_message}")
                
            except Exception as e:
                # Handle unexpected future exceptions
                result = TaskExecutionResult(
                    task_id=task_id,
                    status=TaskExecutionStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_seconds=0.0,
                    error=e,
                    error_message=f"Future execution error: {str(e)}"
                )
                context.results[task_id] = result
                context.failed_tasks.add(task_id)
                self._logger.error(f"Task {task_id} future failed: {e}")
            
            # Remove from active futures
            del context.active_futures[task_id]
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics and performance metrics."""
        success_rate = self._successful_executions / max(self._total_executions, 1)
        avg_tasks_per_execution = self._total_tasks_executed / max(self._total_executions, 1)
        
        return {
            'total_executions': self._total_executions,
            'successful_executions': self._successful_executions,
            'failed_executions': self._failed_executions,
            'success_rate': success_rate,
            'total_tasks_executed': self._total_tasks_executed,
            'average_tasks_per_execution': avg_tasks_per_execution,
            'current_execution_active': self._current_execution is not None,
            'executor_configuration': {
                'max_workers': self._max_workers,
                'execution_strategy': self._execution_strategy.value,
                'executor_active': self._executor is not None and not self._executor._shutdown
            }
        }
    
    def shutdown(self) -> None:
        """Shutdown the parallel execution engine."""
        with self.trace_operation("shutdown") as trace:
            if self._executor:
                self._executor.shutdown(wait=True)
                self._executor = None
                self._logger.info("ThreadPoolExecutor shutdown completed")
            
            trace.output_result = {'shutdown_completed': True}
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.shutdown()
        except Exception:
            pass  # Ignore errors during cleanup


# Convenience functions for integration
def create_parallel_execution_engine(max_workers: int = 10, 
                                    strategy: ExecutionStrategy = ExecutionStrategy.CONSERVATIVE) -> ParallelExecutionEngine:
    """
    Factory function to create parallel execution engine.
    
    Args:
        max_workers: Maximum number of worker threads
        strategy: Execution strategy to use
        
    Returns:
        ParallelExecutionEngine instance
    """
    return ParallelExecutionEngine(max_workers=max_workers, execution_strategy=strategy)


def create_task_definition(task_id: str, name: str, 
                         execution_function: Optional[Callable] = None,
                         dependencies: Optional[Set[str]] = None,
                         **kwargs) -> TaskDefinition:
    """
    Convenience function to create task definition.
    
    Args:
        task_id: Unique task identifier
        name: Human-readable task name
        execution_function: Function to execute for this task
        dependencies: Set of task IDs this task depends on
        **kwargs: Additional task configuration
        
    Returns:
        TaskDefinition instance
    """
    return TaskDefinition(
        task_id=task_id,
        name=name,
        execution_function=execution_function,
        dependencies=dependencies or set(),
        **kwargs
    )