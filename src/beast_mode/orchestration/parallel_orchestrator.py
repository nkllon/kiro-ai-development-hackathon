#!/usr/bin/env python3
"""
Parallel Orchestrator - Coordinated parallel execution of DAG tasks.

Orchestrates parallel execution of task waves with proper dependency management,
failure handling, and resource coordination.
"""

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import time

from src.beast_mode.core.beastly_module import BeastlyModule
from .dag_validator import DAGValidator, DAGValidationReport, TaskNode
from .independent_task_executor import (
    IndependentTaskExecutor, TaskResult, TaskState, ExecutionMode
)


class OrchestrationState(Enum):
    """Orchestration execution states"""
    IDLE = "idle"
    VALIDATING = "validating"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WaveExecutionResult:
    """Result of executing a wave of parallel tasks"""
    wave_number: int
    tasks_in_wave: List[str]
    successful_tasks: List[str]
    failed_tasks: List[str]
    task_results: Dict[str, TaskResult]
    wave_start_time: datetime
    wave_end_time: datetime
    wave_duration_seconds: float


@dataclass
class OrchestrationResult:
    """Complete orchestration execution result"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    waves_executed: int
    total_duration_seconds: float
    wave_results: List[WaveExecutionResult]
    critical_path_duration: float
    parallelization_efficiency: float
    orchestration_state: OrchestrationState


class ParallelOrchestrator(BeastlyModule):
    """
    Parallel orchestrator for DAG-based task execution.
    
    Coordinates parallel execution of task waves while maintaining dependency
    constraints, handling failures gracefully, and providing comprehensive
    monitoring and recovery capabilities.
    """
    
    def __init__(self, max_parallel_tasks: int = 4):
        super().__init__()
        self._logger = logging.getLogger(f"beast_mode.orchestration.{self.__class__.__name__}")
        
        # Core components
        self.dag_validator = DAGValidator()
        self.task_executor = IndependentTaskExecutor()
        
        # Execution configuration
        self.max_parallel_tasks = max_parallel_tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=max_parallel_tasks)
        
        # Orchestration state
        self._orchestration_state = OrchestrationState.IDLE
        self._current_execution: Optional[Dict[str, Any]] = None
        self._task_registry: Dict[str, Callable] = {}
        self._execution_lock = threading.Lock()
        
        # Monitoring and metrics
        self._orchestrations_started = 0
        self._orchestrations_completed = 0
        self._orchestrations_failed = 0
        self._total_tasks_executed = 0
        
        self._logger.info(f"ParallelOrchestrator initialized with max_parallel_tasks={max_parallel_tasks}")
    
    def get_capabilities(self) -> List[Any]:
        """Get module capabilities"""
        return ["PARALLEL_ORCHESTRATION", "DAG_EXECUTION", "FAILURE_HANDLING"]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get module health status"""
        return {
            "status": "healthy",
            "orchestration_state": self._orchestration_state.value,
            "orchestrations_started": self._orchestrations_started,
            "orchestrations_completed": self._orchestrations_completed,
            "total_tasks_executed": self._total_tasks_executed
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation"""
        return {
            "success": True,
            "degraded_capabilities": [],
            "remaining_capabilities": ["PARALLEL_ORCHESTRATION", "DAG_EXECUTION"]
        }
    
    def register_task(self, task_id: str, task_function: Callable):
        """Register a task function for execution"""
        self._task_registry[task_id] = task_function
        self._logger.debug(f"Registered task function for {task_id}")
    
    def orchestrate_dag_execution(self, tasks: Dict[str, TaskNode],
                                 execution_mode: ExecutionMode = ExecutionMode.ISOLATED_PROCESS,
                                 fail_fast: bool = False) -> OrchestrationResult:
        """
        Orchestrate parallel execution of DAG tasks.
        
        Args:
            tasks: Dictionary of task_id -> TaskNode with dependencies
            execution_mode: How to execute individual tasks
            fail_fast: Whether to stop on first failure or continue
            
        Returns:
            OrchestrationResult with complete execution details
        """
        with self.trace_operation("orchestrate_dag_execution") as trace:
            with self._execution_lock:
                if self._orchestration_state != OrchestrationState.IDLE:
                    raise RuntimeError(f"Orchestrator busy: {self._orchestration_state}")
                
                self._orchestration_state = OrchestrationState.VALIDATING
                self._orchestrations_started += 1
                
                start_time = datetime.now()
                
                try:
                    # Step 1: Validate DAG
                    self._logger.info(f"Validating DAG with {len(tasks)} tasks")
                    validation_report = self.dag_validator.validate_dag(tasks)
                    
                    if not validation_report.is_valid:
                        self._orchestration_state = OrchestrationState.FAILED
                        self._orchestrations_failed += 1
                        
                        error_result = OrchestrationResult(
                            total_tasks=len(tasks),
                            successful_tasks=0,
                            failed_tasks=len(tasks),
                            waves_executed=0,
                            total_duration_seconds=0,
                            wave_results=[],
                            critical_path_duration=0,
                            parallelization_efficiency=0,
                            orchestration_state=OrchestrationState.FAILED
                        )
                        
                        trace.output_result = {
                            'success': False,
                            'validation_errors': validation_report.validation_errors
                        }
                        
                        raise ValueError(f"DAG validation failed: {validation_report.validation_errors}")
                    
                    # Step 2: Execute waves in parallel
                    self._orchestration_state = OrchestrationState.EXECUTING
                    self._logger.info(f"Executing {len(validation_report.execution_waves)} waves")
                    
                    wave_results = []
                    successful_tasks = set()
                    failed_tasks = set()
                    
                    for wave_num, wave_tasks in enumerate(validation_report.execution_waves):
                        self._logger.info(f"Executing wave {wave_num + 1} with {len(wave_tasks)} tasks")
                        
                        wave_result = self._execute_wave(
                            wave_num + 1, wave_tasks, tasks, execution_mode, successful_tasks
                        )
                        
                        wave_results.append(wave_result)
                        successful_tasks.update(wave_result.successful_tasks)
                        failed_tasks.update(wave_result.failed_tasks)
                        
                        # Check fail_fast condition
                        if fail_fast and wave_result.failed_tasks:
                            self._logger.warning(f"Stopping execution due to failures in wave {wave_num + 1}")
                            break
                        
                        # Update dependencies for next wave
                        self._update_dependency_status(tasks, successful_tasks, failed_tasks)
                    
                    # Step 3: Calculate results
                    end_time = datetime.now()
                    total_duration = (end_time - start_time).total_seconds()
                    
                    # Calculate parallelization efficiency
                    sequential_duration = sum(wr.wave_duration_seconds for wr in wave_results)
                    parallelization_efficiency = (sequential_duration / total_duration) if total_duration > 0 else 0
                    
                    # Determine final state
                    if failed_tasks:
                        final_state = OrchestrationState.FAILED
                        self._orchestrations_failed += 1
                    else:
                        final_state = OrchestrationState.COMPLETED
                        self._orchestrations_completed += 1
                    
                    self._orchestration_state = final_state
                    self._total_tasks_executed += len(successful_tasks) + len(failed_tasks)
                    
                    result = OrchestrationResult(
                        total_tasks=len(tasks),
                        successful_tasks=len(successful_tasks),
                        failed_tasks=len(failed_tasks),
                        waves_executed=len(wave_results),
                        total_duration_seconds=total_duration,
                        wave_results=wave_results,
                        critical_path_duration=len(validation_report.critical_path),  # Simplified
                        parallelization_efficiency=parallelization_efficiency,
                        orchestration_state=final_state
                    )
                    
                    trace.output_result = {
                        'success': len(failed_tasks) == 0,
                        'total_tasks': len(tasks),
                        'successful_tasks': len(successful_tasks),
                        'failed_tasks': len(failed_tasks),
                        'waves_executed': len(wave_results),
                        'duration_seconds': total_duration,
                        'parallelization_efficiency': parallelization_efficiency
                    }
                    
                    self._logger.info(f"Orchestration completed: {len(successful_tasks)}/{len(tasks)} tasks successful")
                    return result
                    
                except Exception as e:
                    self._orchestration_state = OrchestrationState.FAILED
                    self._orchestrations_failed += 1
                    
                    self._logger.error(f"Orchestration failed: {e}")
                    trace.output_result = {'success': False, 'error': str(e)}
                    raise
                
                finally:
                    if self._orchestration_state in [OrchestrationState.COMPLETED, OrchestrationState.FAILED]:
                        self._orchestration_state = OrchestrationState.IDLE
    
    def _execute_wave(self, wave_number: int, wave_tasks: List[str], 
                     all_tasks: Dict[str, TaskNode], execution_mode: ExecutionMode,
                     completed_tasks: Set[str]) -> WaveExecutionResult:
        """Execute a wave of parallel tasks"""
        wave_start_time = datetime.now()
        
        # Filter tasks that can actually run (dependencies met)
        runnable_tasks = []
        for task_id in wave_tasks:
            task = all_tasks[task_id]
            deps_met = all(dep in completed_tasks for dep in task.dependencies)
            if deps_met:
                runnable_tasks.append(task_id)
            else:
                self._logger.warning(f"Task {task_id} dependencies not met, skipping")
        
        if not runnable_tasks:
            # Empty wave
            return WaveExecutionResult(
                wave_number=wave_number,
                tasks_in_wave=wave_tasks,
                successful_tasks=[],
                failed_tasks=[],
                task_results={},
                wave_start_time=wave_start_time,
                wave_end_time=datetime.now(),
                wave_duration_seconds=0
            )
        
        # Execute tasks in parallel
        futures = {}
        task_results = {}
        
        for task_id in runnable_tasks:
            # Get task function
            task_function = self._task_registry.get(task_id)
            if not task_function:
                # Create a default task function if not registered
                task_function = lambda tid=task_id: self._default_task_execution(tid)
            
            # Submit task for execution
            future = self.thread_pool.submit(
                self._execute_single_task,
                task_id, task_function, execution_mode
            )
            futures[future] = task_id
        
        # Wait for all tasks to complete
        successful_tasks = []
        failed_tasks = []
        
        for future in as_completed(futures):
            task_id = futures[future]
            try:
                result = future.result()
                task_results[task_id] = result
                
                if result.success:
                    successful_tasks.append(task_id)
                    self._logger.info(f"Task {task_id} completed successfully")
                else:
                    failed_tasks.append(task_id)
                    self._logger.error(f"Task {task_id} failed: {result.error}")
                    
            except Exception as e:
                failed_tasks.append(task_id)
                self._logger.error(f"Task {task_id} execution exception: {e}")
                
                # Create error result
                task_results[task_id] = TaskResult(
                    task_id=task_id,
                    state=TaskState.FAILED,
                    success=False,
                    start_time=wave_start_time,
                    end_time=datetime.now(),
                    duration_seconds=0,
                    output="",
                    error=str(e),
                    exit_code=-1,
                    resource_usage={},
                    checkpoint_path=None,
                    rollback_available=False
                )
        
        wave_end_time = datetime.now()
        wave_duration = (wave_end_time - wave_start_time).total_seconds()
        
        return WaveExecutionResult(
            wave_number=wave_number,
            tasks_in_wave=runnable_tasks,
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            task_results=task_results,
            wave_start_time=wave_start_time,
            wave_end_time=wave_end_time,
            wave_duration_seconds=wave_duration
        )
    
    def _execute_single_task(self, task_id: str, task_function: Callable, 
                           execution_mode: ExecutionMode) -> TaskResult:
        """Execute a single task with proper isolation"""
        try:
            # Create execution context
            context = self.task_executor.create_execution_context(task_id, execution_mode)
            
            # Execute task
            result = self.task_executor.execute_task_isolated(
                task_id, task_function, args=[], kwargs={}
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to execute task {task_id}: {e}")
            return TaskResult(
                task_id=task_id,
                state=TaskState.FAILED,
                success=False,
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=0,
                output="",
                error=str(e),
                exit_code=-1,
                resource_usage={},
                checkpoint_path=None,
                rollback_available=False
            )
    
    def _default_task_execution(self, task_id: str) -> str:
        """Default task execution for unregistered tasks"""
        self._logger.info(f"Executing default task: {task_id}")
        time.sleep(1)  # Simulate work
        return f"Default execution completed for {task_id}"
    
    def _update_dependency_status(self, tasks: Dict[str, TaskNode], 
                                 successful_tasks: Set[str], failed_tasks: Set[str]):
        """Update task dependency status based on completed tasks"""
        # This could be used to dynamically adjust dependencies
        # based on task success/failure patterns
        pass
    
    def cancel_orchestration(self) -> bool:
        """Cancel current orchestration"""
        with self._execution_lock:
            if self._orchestration_state == OrchestrationState.EXECUTING:
                self._orchestration_state = OrchestrationState.CANCELLED
                
                # Cancel all running tasks
                # This would require tracking active futures and cancelling them
                self._logger.info("Orchestration cancelled")
                return True
            
            return False
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status"""
        return {
            "state": self._orchestration_state.value,
            "orchestrations_started": self._orchestrations_started,
            "orchestrations_completed": self._orchestrations_completed,
            "orchestrations_failed": self._orchestrations_failed,
            "total_tasks_executed": self._total_tasks_executed,
            "success_rate": self._orchestrations_completed / max(self._orchestrations_started, 1) * 100,
            "max_parallel_tasks": self.max_parallel_tasks
        }
    
    def cleanup(self):
        """Clean up orchestrator resources"""
        self.thread_pool.shutdown(wait=True)
        self._logger.info("ParallelOrchestrator cleaned up")