#!/usr/bin/env python3
"""
Intelligent Task Batching for DAG Orchestration
===============================================

Implementation of intelligent task batching for resource optimization
and cost reduction with adaptive batching strategies.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition


class BatchingStrategy(Enum):
    """Strategies for task batching."""
    SIZE_BASED = "size_based"
    TIME_BASED = "time_based"
    RESOURCE_BASED = "resource_based"
    COST_BASED = "cost_based"
    SIMILARITY_BASED = "similarity_based"
    ADAPTIVE = "adaptive"


@dataclass
class TaskBatch:
    """A batch of tasks for execution."""
    batch_id: str
    tasks: List[TaskDefinition]
    batch_strategy: BatchingStrategy
    estimated_cost: float = 0.0
    estimated_time: float = 0.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchingResult:
    """Result of task batching operation."""
    batching_id: str
    original_task_count: int
    batch_count: int
    batches: List[TaskBatch]
    optimization_metrics: Dict[str, Any] = field(default_factory=dict)
    batching_time: float = 0.0


class BatchOptimizer:
    """Optimizer for task batching decisions."""
    
    def __init__(self):
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
    
    def optimize_batches(self, tasks: List[TaskDefinition], 
                        strategy: BatchingStrategy,
                        constraints: Dict[str, Any]) -> List[TaskBatch]:
        """Optimize task batching based on strategy and constraints."""
        
        if strategy == BatchingStrategy.SIZE_BASED:
            return self._optimize_by_size(tasks, constraints)
        elif strategy == BatchingStrategy.TIME_BASED:
            return self._optimize_by_time(tasks, constraints)
        elif strategy == BatchingStrategy.RESOURCE_BASED:
            return self._optimize_by_resources(tasks, constraints)
        elif strategy == BatchingStrategy.COST_BASED:
            return self._optimize_by_cost(tasks, constraints)
        elif strategy == BatchingStrategy.SIMILARITY_BASED:
            return self._optimize_by_similarity(tasks, constraints)
        elif strategy == BatchingStrategy.ADAPTIVE:
            return self._optimize_adaptive(tasks, constraints)
        else:
            return self._optimize_by_size(tasks, constraints)
    
    def _optimize_by_size(self, tasks: List[TaskDefinition], 
                         constraints: Dict[str, Any]) -> List[TaskBatch]:
        """Optimize batching by batch size."""
        batch_size = constraints.get('batch_size', 10)
        batches = []
        
        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i:i + batch_size]
            batch = TaskBatch(
                batch_id=str(uuid.uuid4()),
                tasks=batch_tasks,
                batch_strategy=BatchingStrategy.SIZE_BASED,
                metadata={'batch_size': len(batch_tasks)}
            )
            batches.append(batch)
        
        return batches
    
    def _optimize_by_time(self, tasks: List[TaskDefinition], 
                         constraints: Dict[str, Any]) -> List[TaskBatch]:
        """Optimize batching by time windows."""
        time_window = constraints.get('time_window_seconds', 300)  # 5 minutes
        batches = []
        current_batch = []
        current_time = 0.0
        
        for task in tasks:
            estimated_time = getattr(task, 'estimated_duration', 30.0)
            
            if current_time + estimated_time > time_window and current_batch:
                # Create batch
                batch = TaskBatch(
                    batch_id=str(uuid.uuid4()),
                    tasks=current_batch.copy(),
                    batch_strategy=BatchingStrategy.TIME_BASED,
                    estimated_time=current_time,
                    metadata={'time_window': time_window}
                )
                batches.append(batch)
                current_batch = []
                current_time = 0.0
            
            current_batch.append(task)
            current_time += estimated_time
        
        # Add remaining tasks
        if current_batch:
            batch = TaskBatch(
                batch_id=str(uuid.uuid4()),
                tasks=current_batch,
                batch_strategy=BatchingStrategy.TIME_BASED,
                estimated_time=current_time,
                metadata={'time_window': time_window}
            )
            batches.append(batch)
        
        return batches
    
    def _optimize_by_resources(self, tasks: List[TaskDefinition], 
                              constraints: Dict[str, Any]) -> List[TaskBatch]:
        """Optimize batching by resource requirements."""
        max_cpu = constraints.get('max_cpu_per_batch', 4.0)
        max_memory = constraints.get('max_memory_per_batch', 8.0)  # GB
        
        batches = []
        current_batch = []
        current_cpu = 0.0
        current_memory = 0.0
        
        for task in tasks:
            task_cpu = task.resource_requirements.get('cpu', 1.0)
            task_memory = task.resource_requirements.get('memory', 1.0)
            
            if ((current_cpu + task_cpu > max_cpu or 
                 current_memory + task_memory > max_memory) and current_batch):
                # Create batch
                batch = TaskBatch(
                    batch_id=str(uuid.uuid4()),
                    tasks=current_batch.copy(),
                    batch_strategy=BatchingStrategy.RESOURCE_BASED,
                    resource_requirements={
                        'cpu': current_cpu,
                        'memory': current_memory
                    },
                    metadata={'max_cpu': max_cpu, 'max_memory': max_memory}
                )
                batches.append(batch)
                current_batch = []
                current_cpu = 0.0
                current_memory = 0.0
            
            current_batch.append(task)
            current_cpu += task_cpu
            current_memory += task_memory
        
        # Add remaining tasks
        if current_batch:
            batch = TaskBatch(
                batch_id=str(uuid.uuid4()),
                tasks=current_batch,
                batch_strategy=BatchingStrategy.RESOURCE_BASED,
                resource_requirements={
                    'cpu': current_cpu,
                    'memory': current_memory
                },
                metadata={'max_cpu': max_cpu, 'max_memory': max_memory}
            )
            batches.append(batch)
        
        return batches
    
    def _optimize_by_cost(self, tasks: List[TaskDefinition], 
                         constraints: Dict[str, Any]) -> List[TaskBatch]:
        """Optimize batching by cost considerations."""
        max_cost_per_batch = constraints.get('max_cost_per_batch', 10.0)
        
        batches = []
        current_batch = []
        current_cost = 0.0
        
        for task in tasks:
            task_cost = getattr(task, 'estimated_cost', 1.0)
            
            if current_cost + task_cost > max_cost_per_batch and current_batch:
                # Create batch
                batch = TaskBatch(
                    batch_id=str(uuid.uuid4()),
                    tasks=current_batch.copy(),
                    batch_strategy=BatchingStrategy.COST_BASED,
                    estimated_cost=current_cost,
                    metadata={'max_cost_per_batch': max_cost_per_batch}
                )
                batches.append(batch)
                current_batch = []
                current_cost = 0.0
            
            current_batch.append(task)
            current_cost += task_cost
        
        # Add remaining tasks
        if current_batch:
            batch = TaskBatch(
                batch_id=str(uuid.uuid4()),
                tasks=current_batch,
                batch_strategy=BatchingStrategy.COST_BASED,
                estimated_cost=current_cost,
                metadata={'max_cost_per_batch': max_cost_per_batch}
            )
            batches.append(batch)
        
        return batches
    
    def _optimize_by_similarity(self, tasks: List[TaskDefinition], 
                               constraints: Dict[str, Any]) -> List[TaskBatch]:
        """Optimize batching by task similarity."""
        similarity_threshold = constraints.get('similarity_threshold', 0.7)
        
        # Simple similarity based on task name patterns
        task_groups = {}
        for task in tasks:
            # Extract task type from name (simple heuristic)
            task_type = task.name.split('_')[0] if '_' in task.name else task.name[:10]
            
            if task_type not in task_groups:
                task_groups[task_type] = []
            task_groups[task_type].append(task)
        
        batches = []
        for task_type, group_tasks in task_groups.items():
            # Further split large groups
            max_batch_size = constraints.get('max_batch_size', 20)
            
            for i in range(0, len(group_tasks), max_batch_size):
                batch_tasks = group_tasks[i:i + max_batch_size]
                batch = TaskBatch(
                    batch_id=str(uuid.uuid4()),
                    tasks=batch_tasks,
                    batch_strategy=BatchingStrategy.SIMILARITY_BASED,
                    metadata={
                        'task_type': task_type,
                        'similarity_threshold': similarity_threshold
                    }
                )
                batches.append(batch)
        
        return batches
    
    def _optimize_adaptive(self, tasks: List[TaskDefinition], 
                          constraints: Dict[str, Any]) -> List[TaskBatch]:
        """Adaptive optimization combining multiple strategies."""
        # Use different strategies based on task characteristics
        
        # Separate tasks by characteristics
        high_cost_tasks = [t for t in tasks if getattr(t, 'estimated_cost', 1.0) > 5.0]
        resource_intensive_tasks = [t for t in tasks 
                                  if t.resource_requirements.get('cpu', 1.0) > 2.0]
        regular_tasks = [t for t in tasks 
                        if t not in high_cost_tasks and t not in resource_intensive_tasks]
        
        batches = []
        
        # High cost tasks: optimize by cost
        if high_cost_tasks:
            cost_batches = self._optimize_by_cost(high_cost_tasks, constraints)
            batches.extend(cost_batches)
        
        # Resource intensive tasks: optimize by resources
        if resource_intensive_tasks:
            resource_batches = self._optimize_by_resources(resource_intensive_tasks, constraints)
            batches.extend(resource_batches)
        
        # Regular tasks: optimize by size
        if regular_tasks:
            size_batches = self._optimize_by_size(regular_tasks, constraints)
            batches.extend(size_batches)
        
        return batches


class IntelligentBatcher(ReflectiveModule):
    """
    Intelligent task batcher for resource optimization and cost reduction.
    
    Features:
    - Multiple batching strategies
    - Adaptive optimization
    - Resource and cost awareness
    - Performance monitoring
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "IntelligentBatcher"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Components
        self._optimizer = BatchOptimizer()
        
        # Statistics
        self._total_batching_operations = 0
        self._total_tasks_batched = 0
        self._total_batches_created = 0
        self._strategy_usage = {}
        
        self._logger.info("IntelligentBatcher initialized")
    
    async def create_batches(self, tasks: List[TaskDefinition],
                           strategy: BatchingStrategy = BatchingStrategy.ADAPTIVE,
                           constraints: Optional[Dict[str, Any]] = None) -> BatchingResult:
        """Create optimized task batches."""
        with self.trace_operation("create_batches", 
                                task_count=len(tasks),
                                strategy=strategy.value) as trace:
            
            start_time = datetime.now()
            batching_id = str(uuid.uuid4())
            constraints = constraints or {}
            
            try:
                # Update statistics
                self._total_batching_operations += 1
                self._total_tasks_batched += len(tasks)
                
                strategy_name = strategy.value
                self._strategy_usage[strategy_name] = self._strategy_usage.get(strategy_name, 0) + 1
                
                # Create batches using optimizer
                batches = self._optimizer.optimize_batches(tasks, strategy, constraints)
                self._total_batches_created += len(batches)
                
                # Calculate optimization metrics
                end_time = datetime.now()
                batching_time = (end_time - start_time).total_seconds()
                
                optimization_metrics = self._calculate_optimization_metrics(tasks, batches)
                
                result = BatchingResult(
                    batching_id=batching_id,
                    original_task_count=len(tasks),
                    batch_count=len(batches),
                    batches=batches,
                    optimization_metrics=optimization_metrics,
                    batching_time=batching_time
                )
                
                trace.output_result = {
                    'batching_id': batching_id,
                    'original_task_count': len(tasks),
                    'batch_count': len(batches),
                    'batching_time': batching_time,
                    'optimization_score': optimization_metrics.get('optimization_score', 0.0)
                }
                
                self._logger.info(f"Created {len(batches)} batches from {len(tasks)} tasks using {strategy.value} strategy")
                return result
                
            except Exception as e:
                self._logger.error(f"Failed to create batches: {e}")
                trace.output_result = {'error': str(e)}
                raise e
    
    def _calculate_optimization_metrics(self, original_tasks: List[TaskDefinition],
                                      batches: List[TaskBatch]) -> Dict[str, Any]:
        """Calculate optimization metrics for batching result."""
        
        # Calculate batch size statistics
        batch_sizes = [len(batch.tasks) for batch in batches]
        avg_batch_size = sum(batch_sizes) / len(batch_sizes) if batch_sizes else 0
        
        # Calculate resource utilization
        total_estimated_cost = sum(batch.estimated_cost for batch in batches)
        total_estimated_time = sum(batch.estimated_time for batch in batches)
        
        # Calculate optimization score (simple heuristic)
        # Higher score is better (fewer batches with good utilization)
        if len(batches) > 0:
            optimization_score = (len(original_tasks) / len(batches)) * 0.5 + avg_batch_size * 0.3
        else:
            optimization_score = 0.0
        
        return {
            'optimization_score': optimization_score,
            'average_batch_size': avg_batch_size,
            'min_batch_size': min(batch_sizes) if batch_sizes else 0,
            'max_batch_size': max(batch_sizes) if batch_sizes else 0,
            'total_estimated_cost': total_estimated_cost,
            'total_estimated_time': total_estimated_time,
            'batch_count': len(batches),
            'compression_ratio': len(original_tasks) / max(len(batches), 1)
        }
    
    def get_batching_statistics(self) -> Dict[str, Any]:
        """Get batching statistics."""
        avg_tasks_per_operation = self._total_tasks_batched / max(self._total_batching_operations, 1)
        avg_batches_per_operation = self._total_batches_created / max(self._total_batching_operations, 1)
        
        return {
            'total_batching_operations': self._total_batching_operations,
            'total_tasks_batched': self._total_tasks_batched,
            'total_batches_created': self._total_batches_created,
            'average_tasks_per_operation': avg_tasks_per_operation,
            'average_batches_per_operation': avg_batches_per_operation,
            'strategy_usage': self._strategy_usage
        }
    
    def recommend_strategy(self, tasks: List[TaskDefinition],
                          constraints: Dict[str, Any]) -> BatchingStrategy:
        """Recommend best batching strategy based on task characteristics."""
        
        # Analyze task characteristics
        has_cost_info = any(hasattr(task, 'estimated_cost') for task in tasks)
        has_resource_info = any(task.resource_requirements for task in tasks)
        has_time_info = any(hasattr(task, 'estimated_duration') for task in tasks)
        
        # Check constraints
        has_cost_constraints = 'max_cost_per_batch' in constraints
        has_resource_constraints = any(key in constraints for key in ['max_cpu_per_batch', 'max_memory_per_batch'])
        has_time_constraints = 'time_window_seconds' in constraints
        
        # Recommend strategy based on available information and constraints
        if has_cost_info and has_cost_constraints:
            return BatchingStrategy.COST_BASED
        elif has_resource_info and has_resource_constraints:
            return BatchingStrategy.RESOURCE_BASED
        elif has_time_info and has_time_constraints:
            return BatchingStrategy.TIME_BASED
        elif len(tasks) > 50:  # Large number of tasks
            return BatchingStrategy.SIMILARITY_BASED
        else:
            return BatchingStrategy.ADAPTIVE


# Convenience functions
def create_intelligent_batcher() -> IntelligentBatcher:
    """Factory function to create intelligent batcher."""
    return IntelligentBatcher()


def create_batch_optimizer() -> BatchOptimizer:
    """Factory function to create batch optimizer."""
    return BatchOptimizer()


async def batch_tasks(tasks: List[TaskDefinition],
                     strategy: BatchingStrategy = BatchingStrategy.ADAPTIVE,
                     constraints: Optional[Dict[str, Any]] = None) -> BatchingResult:
    """Convenience function to batch tasks."""
    batcher = create_intelligent_batcher()
    return await batcher.create_batches(tasks, strategy, constraints)