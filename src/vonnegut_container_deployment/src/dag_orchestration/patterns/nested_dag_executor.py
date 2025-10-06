#!/usr/bin/env python3
"""
Nested DAG Executor for DAG Orchestration
=========================================

Implementation of nested DAG execution and hierarchical task structures
with support for sub-DAGs and complex workflow compositions.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition, TaskExecutionResult


class HierarchyLevel(Enum):
    """Levels in DAG hierarchy."""
    ROOT = "root"
    PARENT = "parent"
    CHILD = "child"
    LEAF = "leaf"


@dataclass
class HierarchicalTask:
    """Task that can contain sub-DAGs."""
    task_definition: TaskDefinition
    sub_dag: Optional[List['HierarchicalTask']] = None
    hierarchy_level: HierarchyLevel = HierarchyLevel.LEAF
    parent_task_id: Optional[str] = None
    execution_strategy: str = "parallel"  # parallel, sequential, conditional
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DAGHierarchy:
    """Represents a hierarchical DAG structure."""
    hierarchy_id: str
    root_tasks: List[HierarchicalTask]
    total_tasks: int = 0
    max_depth: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class NestedExecutionResult:
    """Result of nested DAG execution."""
    execution_id: str
    hierarchy_id: str
    total_tasks_executed: int
    successful_tasks: int
    failed_tasks: int
    execution_time: float
    hierarchy_results: Dict[str, Any] = field(default_factory=dict)
    execution_tree: Dict[str, Any] = field(default_factory=dict)


class NestedDAGExecutor(ReflectiveModule):
    """
    Executor for nested DAG structures and hierarchical tasks.
    
    Features:
    - Hierarchical task execution
    - Sub-DAG management
    - Nested dependency resolution
    - Execution tree tracking
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "NestedDAGExecutor"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Execution state
        self._active_hierarchies: Dict[str, DAGHierarchy] = {}
        self._execution_trees: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self._total_executions = 0
        self._successful_executions = 0
        self._failed_executions = 0
        self._max_depth_executed = 0
        
        self._logger.info("NestedDAGExecutor initialized")
    
    def create_hierarchy(self, root_tasks: List[HierarchicalTask]) -> DAGHierarchy:
        """Create a hierarchical DAG structure."""
        hierarchy_id = str(uuid.uuid4())
        
        # Calculate hierarchy statistics
        total_tasks, max_depth = self._analyze_hierarchy(root_tasks)
        
        hierarchy = DAGHierarchy(
            hierarchy_id=hierarchy_id,
            root_tasks=root_tasks,
            total_tasks=total_tasks,
            max_depth=max_depth
        )
        
        self._active_hierarchies[hierarchy_id] = hierarchy
        self._logger.info(f"Created hierarchy {hierarchy_id} with {total_tasks} tasks, max depth: {max_depth}")
        
        return hierarchy
    
    def _analyze_hierarchy(self, tasks: List[HierarchicalTask], current_depth: int = 0) -> tuple[int, int]:
        """Analyze hierarchy to calculate total tasks and max depth."""
        total_tasks = len(tasks)
        max_depth = current_depth
        
        for task in tasks:
            if task.sub_dag:
                sub_total, sub_max_depth = self._analyze_hierarchy(task.sub_dag, current_depth + 1)
                total_tasks += sub_total
                max_depth = max(max_depth, sub_max_depth)
        
        return total_tasks, max_depth
    
    async def execute_hierarchy(self, hierarchy: DAGHierarchy) -> NestedExecutionResult:
        """Execute a hierarchical DAG structure."""
        with self.trace_operation("execute_hierarchy",
                                hierarchy_id=hierarchy.hierarchy_id,
                                total_tasks=hierarchy.total_tasks) as trace:
            
            execution_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            try:
                self._total_executions += 1
                
                # Initialize execution tree
                execution_tree = {
                    'execution_id': execution_id,
                    'hierarchy_id': hierarchy.hierarchy_id,
                    'start_time': start_time.isoformat(),
                    'root_tasks': []
                }
                
                # Execute root tasks
                successful_tasks = 0
                failed_tasks = 0
                hierarchy_results = {}
                
                for root_task in hierarchy.root_tasks:
                    task_result = await self._execute_hierarchical_task(
                        root_task, execution_id, execution_tree
                    )
                    
                    hierarchy_results[root_task.task_definition.task_id] = task_result
                    
                    if task_result.get('success', False):
                        successful_tasks += task_result.get('tasks_executed', 1)
                    else:
                        failed_tasks += task_result.get('tasks_executed', 1)
                
                # Calculate execution time
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Update statistics
                if failed_tasks == 0:
                    self._successful_executions += 1
                else:
                    self._failed_executions += 1
                
                self._max_depth_executed = max(self._max_depth_executed, hierarchy.max_depth)
                
                # Create result
                result = NestedExecutionResult(
                    execution_id=execution_id,
                    hierarchy_id=hierarchy.hierarchy_id,
                    total_tasks_executed=successful_tasks + failed_tasks,
                    successful_tasks=successful_tasks,
                    failed_tasks=failed_tasks,
                    execution_time=execution_time,
                    hierarchy_results=hierarchy_results,
                    execution_tree=execution_tree
                )
                
                # Store execution tree
                self._execution_trees[execution_id] = execution_tree
                
                trace.output_result = {
                    'execution_id': execution_id,
                    'total_tasks_executed': successful_tasks + failed_tasks,
                    'successful_tasks': successful_tasks,
                    'failed_tasks': failed_tasks,
                    'execution_time': execution_time
                }
                
                self._logger.info(f"Completed hierarchy execution {execution_id}: "
                                f"{successful_tasks} successful, {failed_tasks} failed")
                
                return result
                
            except Exception as e:
                self._failed_executions += 1
                self._logger.error(f"Hierarchy execution {execution_id} failed: {e}")
                
                trace.output_result = {
                    'execution_id': execution_id,
                    'error': str(e)
                }
                
                raise e
    
    async def _execute_hierarchical_task(self, task: HierarchicalTask,
                                       execution_id: str,
                                       execution_tree: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a hierarchical task and its sub-DAG if present."""
        task_id = task.task_definition.task_id
        
        # Add task to execution tree
        task_node = {
            'task_id': task_id,
            'hierarchy_level': task.hierarchy_level.value,
            'start_time': datetime.now().isoformat(),
            'sub_tasks': []
        }
        
        if 'root_tasks' not in execution_tree:
            execution_tree['root_tasks'] = []
        execution_tree['root_tasks'].append(task_node)
        
        try:
            # Execute the main task
            main_result = await self._execute_single_task(task.task_definition)
            
            task_node['main_result'] = {
                'success': main_result is not None,
                'result': str(main_result) if main_result else None
            }
            
            # Execute sub-DAG if present
            sub_dag_results = {}
            total_sub_tasks = 0
            successful_sub_tasks = 0
            
            if task.sub_dag:
                self._logger.info(f"Executing sub-DAG for task {task_id} with {len(task.sub_dag)} sub-tasks")
                
                if task.execution_strategy == "sequential":
                    # Execute sub-tasks sequentially
                    for sub_task in task.sub_dag:
                        sub_result = await self._execute_hierarchical_task(
                            sub_task, execution_id, task_node
                        )
                        sub_dag_results[sub_task.task_definition.task_id] = sub_result
                        total_sub_tasks += sub_result.get('tasks_executed', 1)
                        if sub_result.get('success', False):
                            successful_sub_tasks += sub_result.get('tasks_executed', 1)
                
                elif task.execution_strategy == "parallel":
                    # Execute sub-tasks in parallel
                    sub_task_futures = []
                    for sub_task in task.sub_dag:
                        future = self._execute_hierarchical_task(sub_task, execution_id, task_node)
                        sub_task_futures.append((sub_task.task_definition.task_id, future))
                    
                    # Wait for all sub-tasks to complete
                    for sub_task_id, future in sub_task_futures:
                        try:
                            sub_result = await future
                            sub_dag_results[sub_task_id] = sub_result
                            total_sub_tasks += sub_result.get('tasks_executed', 1)
                            if sub_result.get('success', False):
                                successful_sub_tasks += sub_result.get('tasks_executed', 1)
                        except Exception as e:
                            sub_dag_results[sub_task_id] = {
                                'success': False,
                                'error': str(e),
                                'tasks_executed': 1
                            }
                            total_sub_tasks += 1
                
                else:  # conditional or other strategies
                    # For now, default to sequential
                    for sub_task in task.sub_dag:
                        sub_result = await self._execute_hierarchical_task(
                            sub_task, execution_id, task_node
                        )
                        sub_dag_results[sub_task.task_definition.task_id] = sub_result
                        total_sub_tasks += sub_result.get('tasks_executed', 1)
                        if sub_result.get('success', False):
                            successful_sub_tasks += sub_result.get('tasks_executed', 1)
            
            # Update task node with completion info
            task_node['end_time'] = datetime.now().isoformat()
            task_node['sub_dag_results'] = sub_dag_results
            task_node['total_sub_tasks'] = total_sub_tasks
            task_node['successful_sub_tasks'] = successful_sub_tasks
            
            # Return result summary
            overall_success = (main_result is not None and 
                             (not task.sub_dag or successful_sub_tasks == total_sub_tasks))
            
            return {
                'success': overall_success,
                'main_result': main_result,
                'sub_dag_results': sub_dag_results,
                'tasks_executed': 1 + total_sub_tasks,
                'successful_sub_tasks': successful_sub_tasks,
                'failed_sub_tasks': total_sub_tasks - successful_sub_tasks
            }
            
        except Exception as e:
            task_node['end_time'] = datetime.now().isoformat()
            task_node['error'] = str(e)
            
            self._logger.error(f"Failed to execute hierarchical task {task_id}: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'tasks_executed': 1,
                'successful_sub_tasks': 0,
                'failed_sub_tasks': 0
            }
    
    async def _execute_single_task(self, task_definition: TaskDefinition) -> Any:
        """Execute a single task."""
        try:
            if task_definition.execution_function:
                if asyncio.iscoroutinefunction(task_definition.execution_function):
                    return await task_definition.execution_function(
                        *task_definition.execution_args,
                        **task_definition.execution_kwargs
                    )
                else:
                    return task_definition.execution_function(
                        *task_definition.execution_args,
                        **task_definition.execution_kwargs
                    )
            else:
                return f"Task {task_definition.task_id} executed successfully"
        except Exception as e:
            self._logger.error(f"Task {task_definition.task_id} execution failed: {e}")
            raise e
    
    def create_hierarchical_task(self, task_definition: TaskDefinition,
                               sub_dag: Optional[List[HierarchicalTask]] = None,
                               execution_strategy: str = "parallel") -> HierarchicalTask:
        """Create a hierarchical task."""
        
        # Determine hierarchy level
        if sub_dag:
            hierarchy_level = HierarchyLevel.PARENT
        else:
            hierarchy_level = HierarchyLevel.LEAF
        
        return HierarchicalTask(
            task_definition=task_definition,
            sub_dag=sub_dag,
            hierarchy_level=hierarchy_level,
            execution_strategy=execution_strategy
        )
    
    def get_execution_tree(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution tree for a specific execution."""
        return self._execution_trees.get(execution_id)
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        success_rate = self._successful_executions / max(self._total_executions, 1)
        
        return {
            'total_executions': self._total_executions,
            'successful_executions': self._successful_executions,
            'failed_executions': self._failed_executions,
            'success_rate': success_rate,
            'max_depth_executed': self._max_depth_executed,
            'active_hierarchies': len(self._active_hierarchies),
            'stored_execution_trees': len(self._execution_trees)
        }
    
    def get_hierarchy_info(self, hierarchy_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific hierarchy."""
        if hierarchy_id not in self._active_hierarchies:
            return None
        
        hierarchy = self._active_hierarchies[hierarchy_id]
        
        return {
            'hierarchy_id': hierarchy.hierarchy_id,
            'total_tasks': hierarchy.total_tasks,
            'max_depth': hierarchy.max_depth,
            'root_task_count': len(hierarchy.root_tasks),
            'created_at': hierarchy.created_at.isoformat()
        }


# Convenience functions
def create_nested_dag_executor() -> NestedDAGExecutor:
    """Factory function to create nested DAG executor."""
    return NestedDAGExecutor()


def create_hierarchical_task(task_definition: TaskDefinition,
                           sub_dag: Optional[List[HierarchicalTask]] = None,
                           execution_strategy: str = "parallel") -> HierarchicalTask:
    """Convenience function to create hierarchical task."""
    executor = NestedDAGExecutor()
    return executor.create_hierarchical_task(task_definition, sub_dag, execution_strategy)