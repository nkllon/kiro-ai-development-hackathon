#!/usr/bin/env python3
"""
Dependency-Aware Task Scheduler
==============================

Enhanced scheduling system that extends the parallel execution engine
with intelligent dependency-aware task scheduling and optimization.

Author: Beast Mode Framework  
Date: 2025-01-27
Version: 1.0
"""

import heapq
import threading
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration.execution.parallel_execution_engine import (
    TaskDefinition, 
    TaskExecutionStatus,
    ExecutionContext
)


class SchedulingStrategy(Enum):
    """Task scheduling strategy options."""
    FIFO = "fifo"  # First In, First Out
    PRIORITY = "priority"  # Priority-based scheduling
    CRITICAL_PATH = "critical_path"  # Critical path method
    RESOURCE_AWARE = "resource_aware"  # Resource-optimized scheduling
    ADAPTIVE = "adaptive"  # Adaptive strategy based on system state


@dataclass
class TaskSchedulingInfo:
    """Extended scheduling information for tasks."""
    task_id: str
    priority: int = 0
    estimated_duration: float = 1.0  # seconds
    resource_weight: float = 1.0  # relative resource consumption
    critical_path_length: float = 0.0  # length of critical path through this task
    ready_time: Optional[datetime] = None
    scheduled_time: Optional[datetime] = None
    dependency_count: int = 0
    dependent_task_count: int = 0


@dataclass
class SchedulingDecision:
    """Result of scheduling decision."""
    task_id: str
    scheduled_time: datetime
    estimated_completion: datetime
    scheduling_reason: str
    priority_score: float


class DependencyAwareScheduler(ReflectiveModule):
    """
    Intelligent task scheduler that optimizes execution order based on
    dependencies, priorities, resource constraints, and critical path analysis.
    """
    
    def __init__(self, strategy: SchedulingStrategy = SchedulingStrategy.ADAPTIVE):
        super().__init__()
        self.module_id = "DependencyAwareScheduler"
        self._strategy = strategy
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Scheduling state
        self._task_info: Dict[str, TaskSchedulingInfo] = {}
        self._dependency_graph: Dict[str, Set[str]] = {}  # task_id -> dependencies
        self._reverse_dependencies: Dict[str, Set[str]] = {}  # task_id -> dependents
        self._ready_queue: List[Tuple[float, str]] = []  # priority queue of ready tasks
        self._scheduling_lock = threading.Lock()
        
        # Statistics
        self._total_scheduling_decisions = 0
        self._average_scheduling_time = 0.0
        self._critical_path_optimizations = 0
        
        self._logger.info(f"DependencyAwareScheduler initialized with strategy: {strategy.value}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "DependencyAwareScheduler",
            "version": "1.0.0",
            "description": "Intelligent dependency-aware task scheduler",
            "configuration": {
                "scheduling_strategy": self._strategy.value,
                "tasks_registered": len(self._task_info),
                "ready_tasks_queued": len(self._ready_queue)
            },
            "statistics": {
                "total_scheduling_decisions": self._total_scheduling_decisions,
                "average_scheduling_time_ms": self._average_scheduling_time * 1000,
                "critical_path_optimizations": self._critical_path_optimizations
            }
        }
    
    def get_capabilities(self) -> List:
        """Get module capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING
        ]
    
    def get_health_status(self):
        """Get module health status."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        try:
            issues = []
            health_score = 1.0
            
            # Check scheduling state
            if len(self._task_info) == 0:
                issues.append("No tasks registered for scheduling")
                health_score *= 0.8
            
            # Check for scheduling performance
            if self._total_scheduling_decisions > 0 and self._average_scheduling_time > 0.1:
                issues.append(f"High average scheduling time: {self._average_scheduling_time:.3f}s")
                health_score *= 0.9
            
            # Determine status
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
    
    def graceful_degradation(self):
        """Perform graceful degradation."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        try:
            # In degraded mode, fall back to FIFO scheduling
            remaining_capabilities = [ModuleCapability.CORE_FUNCTIONALITY]
            degraded_capabilities = [ModuleCapability.DATA_PROCESSING]
            
            # Switch to simpler strategy
            self._strategy = SchedulingStrategy.FIFO
            
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
    
    def register_tasks(self, tasks: List[TaskDefinition]) -> None:
        """
        Register tasks for scheduling analysis.
        
        Args:
            tasks: List of task definitions to register
        """
        with self.trace_operation("register_tasks", task_count=len(tasks)) as trace:
            with self._scheduling_lock:
                # Clear existing state
                self._task_info.clear()
                self._dependency_graph.clear()
                self._reverse_dependencies.clear()
                self._ready_queue.clear()
                
                # Register each task
                for task in tasks:
                    self._register_single_task(task)
                
                # Calculate critical path information
                self._calculate_critical_paths()
                
                # Initialize ready queue
                self._update_ready_queue()
                
                trace.output_result = {
                    'tasks_registered': len(tasks),
                    'ready_tasks': len(self._ready_queue),
                    'dependency_edges': sum(len(deps) for deps in self._dependency_graph.values())
                }
                
                self._logger.info(f"Registered {len(tasks)} tasks for scheduling")
    
    def _register_single_task(self, task: TaskDefinition) -> None:
        """Register a single task for scheduling."""
        # Create scheduling info
        scheduling_info = TaskSchedulingInfo(
            task_id=task.task_id,
            priority=task.priority,
            estimated_duration=getattr(task, 'estimated_duration', 1.0),
            resource_weight=task.resource_requirements.get('weight', 1.0),
            dependency_count=len(task.dependencies)
        )
        
        self._task_info[task.task_id] = scheduling_info
        
        # Build dependency graph
        self._dependency_graph[task.task_id] = task.dependencies.copy()
        
        # Build reverse dependency graph
        if task.task_id not in self._reverse_dependencies:
            self._reverse_dependencies[task.task_id] = set()
        
        for dep_id in task.dependencies:
            if dep_id not in self._reverse_dependencies:
                self._reverse_dependencies[dep_id] = set()
            self._reverse_dependencies[dep_id].add(task.task_id)
    
    def _calculate_critical_paths(self) -> None:
        """Calculate critical path lengths for all tasks using topological sort."""
        # Topological sort to process tasks in dependency order
        in_degree = {task_id: len(deps) for task_id, deps in self._dependency_graph.items()}
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        
        # Calculate critical path lengths
        while queue:
            current_task = queue.pop(0)
            current_info = self._task_info[current_task]
            
            # Calculate this task's critical path length
            max_predecessor_path = 0.0
            for dep_id in self._dependency_graph[current_task]:
                if dep_id in self._task_info:
                    dep_path = self._task_info[dep_id].critical_path_length
                    max_predecessor_path = max(max_predecessor_path, dep_path)
            
            current_info.critical_path_length = max_predecessor_path + current_info.estimated_duration
            
            # Update dependent tasks
            for dependent_id in self._reverse_dependencies.get(current_task, set()):
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        # Update dependent task counts
        for task_id, dependents in self._reverse_dependencies.items():
            if task_id in self._task_info:
                self._task_info[task_id].dependent_task_count = len(dependents)
    
    def _update_ready_queue(self) -> None:
        """Update the ready task queue based on current state."""
        self._ready_queue.clear()
        
        for task_id, info in self._task_info.items():
            # Check if all dependencies are satisfied (for initial scheduling)
            dependencies_ready = all(
                dep_id not in self._task_info or 
                self._task_info[dep_id].scheduled_time is not None
                for dep_id in self._dependency_graph[task_id]
            )
            
            if dependencies_ready and info.scheduled_time is None:
                priority_score = self._calculate_priority_score(task_id)
                heapq.heappush(self._ready_queue, (-priority_score, task_id))  # Negative for max-heap
    
    def _calculate_priority_score(self, task_id: str) -> float:
        """Calculate priority score for a task based on current strategy."""
        info = self._task_info[task_id]
        
        if self._strategy == SchedulingStrategy.FIFO:
            return 1.0  # All tasks have equal priority
        
        elif self._strategy == SchedulingStrategy.PRIORITY:
            return float(info.priority)
        
        elif self._strategy == SchedulingStrategy.CRITICAL_PATH:
            return info.critical_path_length
        
        elif self._strategy == SchedulingStrategy.RESOURCE_AWARE:
            # Prioritize tasks with lower resource requirements
            return 1.0 / max(info.resource_weight, 0.1)
        
        elif self._strategy == SchedulingStrategy.ADAPTIVE:
            # Combine multiple factors
            priority_factor = info.priority * 0.3
            critical_path_factor = info.critical_path_length * 0.4
            resource_factor = (1.0 / max(info.resource_weight, 0.1)) * 0.2
            dependency_factor = info.dependent_task_count * 0.1
            
            return priority_factor + critical_path_factor + resource_factor + dependency_factor
        
        else:
            return 1.0
    
    def get_next_ready_tasks(self, max_tasks: int = 1, 
                           execution_context: Optional[ExecutionContext] = None) -> List[SchedulingDecision]:
        """
        Get the next ready tasks for execution based on scheduling strategy.
        
        Args:
            max_tasks: Maximum number of tasks to return
            execution_context: Current execution context for state-aware decisions
            
        Returns:
            List of scheduling decisions for ready tasks
        """
        with self.trace_operation("get_next_ready_tasks", 
                                max_tasks=max_tasks,
                                queue_size=len(self._ready_queue)) as trace:
            
            scheduling_start = datetime.now()
            decisions = []
            
            with self._scheduling_lock:
                # Update ready queue based on current execution state
                if execution_context:
                    self._update_ready_queue_with_context(execution_context)
                
                # Get up to max_tasks from the ready queue
                selected_tasks = []
                temp_queue = []
                
                while self._ready_queue and len(selected_tasks) < max_tasks:
                    priority_score, task_id = heapq.heappop(self._ready_queue)
                    
                    # Verify task is still ready
                    if self._is_task_ready(task_id, execution_context):
                        selected_tasks.append((task_id, -priority_score))
                    else:
                        # Task no longer ready, put back in queue
                        temp_queue.append((priority_score, task_id))
                
                # Put back tasks that weren't ready
                for item in temp_queue:
                    heapq.heappush(self._ready_queue, item)
                
                # Create scheduling decisions
                current_time = datetime.now()
                for task_id, priority_score in selected_tasks:
                    info = self._task_info[task_id]
                    
                    decision = SchedulingDecision(
                        task_id=task_id,
                        scheduled_time=current_time,
                        estimated_completion=current_time + timedelta(seconds=info.estimated_duration),
                        scheduling_reason=f"Strategy: {self._strategy.value}, Priority: {priority_score:.2f}",
                        priority_score=priority_score
                    )
                    
                    decisions.append(decision)
                    
                    # Mark task as scheduled
                    info.scheduled_time = current_time
                    info.ready_time = current_time
                
                # Update statistics
                scheduling_time = (datetime.now() - scheduling_start).total_seconds()
                self._total_scheduling_decisions += len(decisions)
                self._average_scheduling_time = (
                    (self._average_scheduling_time * (self._total_scheduling_decisions - len(decisions)) + 
                     scheduling_time) / self._total_scheduling_decisions
                )
                
                if self._strategy in [SchedulingStrategy.CRITICAL_PATH, SchedulingStrategy.ADAPTIVE]:
                    self._critical_path_optimizations += len(decisions)
                
                trace.output_result = {
                    'decisions_made': len(decisions),
                    'scheduling_time_ms': scheduling_time * 1000,
                    'remaining_ready_tasks': len(self._ready_queue)
                }
                
                self._logger.info(f"Scheduled {len(decisions)} tasks using {self._strategy.value} strategy")
                
                return decisions
    
    def _update_ready_queue_with_context(self, execution_context: ExecutionContext) -> None:
        """Update ready queue considering current execution context."""
        # Remove tasks that are no longer ready due to execution state changes
        updated_queue = []
        
        while self._ready_queue:
            priority_score, task_id = heapq.heappop(self._ready_queue)
            
            if self._is_task_ready(task_id, execution_context):
                updated_queue.append((priority_score, task_id))
        
        # Rebuild queue
        self._ready_queue = updated_queue
        heapq.heapify(self._ready_queue)
        
        # Add newly ready tasks
        for task_id, info in self._task_info.items():
            if (info.scheduled_time is None and 
                task_id not in execution_context.active_futures and
                task_id not in execution_context.completed_tasks and
                task_id not in execution_context.failed_tasks and
                self._is_task_ready(task_id, execution_context)):
                
                priority_score = self._calculate_priority_score(task_id)
                heapq.heappush(self._ready_queue, (-priority_score, task_id))
    
    def _is_task_ready(self, task_id: str, execution_context: Optional[ExecutionContext] = None) -> bool:
        """Check if a task is ready for execution."""
        if task_id not in self._task_info:
            return False
        
        dependencies = self._dependency_graph.get(task_id, set())
        
        if execution_context:
            # Check against actual execution state
            for dep_id in dependencies:
                if (dep_id not in execution_context.completed_tasks and
                    dep_id not in execution_context.failed_tasks):
                    return False
            
            # Don't schedule if any dependency failed
            if any(dep_id in execution_context.failed_tasks for dep_id in dependencies):
                return False
        
        return True
    
    def notify_task_completion(self, task_id: str, success: bool) -> List[str]:
        """
        Notify scheduler of task completion and get newly ready tasks.
        
        Args:
            task_id: ID of completed task
            success: Whether task completed successfully
            
        Returns:
            List of task IDs that became ready due to this completion
        """
        with self.trace_operation("notify_task_completion", 
                                task_id=task_id, 
                                success=success) as trace:
            
            newly_ready = []
            
            with self._scheduling_lock:
                # Update dependent tasks
                for dependent_id in self._reverse_dependencies.get(task_id, set()):
                    if dependent_id in self._task_info:
                        dependent_info = self._task_info[dependent_id]
                        
                        # Check if all dependencies are now satisfied
                        if success and self._is_task_ready(dependent_id):
                            if dependent_info.scheduled_time is None:
                                newly_ready.append(dependent_id)
                                
                                # Add to ready queue
                                priority_score = self._calculate_priority_score(dependent_id)
                                heapq.heappush(self._ready_queue, (-priority_score, dependent_id))
                
                trace.output_result = {
                    'newly_ready_tasks': len(newly_ready),
                    'task_ids': newly_ready
                }
                
                if newly_ready:
                    self._logger.info(f"Task {task_id} completion made {len(newly_ready)} tasks ready")
                
                return newly_ready
    
    def get_scheduling_statistics(self) -> Dict[str, Any]:
        """Get comprehensive scheduling statistics."""
        with self._scheduling_lock:
            total_tasks = len(self._task_info)
            scheduled_tasks = sum(1 for info in self._task_info.values() if info.scheduled_time is not None)
            ready_tasks = len(self._ready_queue)
            
            # Calculate critical path statistics
            if self._task_info:
                max_critical_path = max(info.critical_path_length for info in self._task_info.values())
                avg_critical_path = sum(info.critical_path_length for info in self._task_info.values()) / total_tasks
            else:
                max_critical_path = avg_critical_path = 0.0
            
            return {
                'strategy': self._strategy.value,
                'total_tasks': total_tasks,
                'scheduled_tasks': scheduled_tasks,
                'ready_tasks': ready_tasks,
                'pending_tasks': total_tasks - scheduled_tasks,
                'total_scheduling_decisions': self._total_scheduling_decisions,
                'average_scheduling_time_ms': self._average_scheduling_time * 1000,
                'critical_path_optimizations': self._critical_path_optimizations,
                'critical_path_analysis': {
                    'max_critical_path_length': max_critical_path,
                    'average_critical_path_length': avg_critical_path
                }
            }


# Convenience functions
def create_dependency_aware_scheduler(strategy: SchedulingStrategy = SchedulingStrategy.ADAPTIVE) -> DependencyAwareScheduler:
    """
    Factory function to create dependency-aware scheduler.
    
    Args:
        strategy: Scheduling strategy to use
        
    Returns:
        DependencyAwareScheduler instance
    """
    return DependencyAwareScheduler(strategy=strategy)