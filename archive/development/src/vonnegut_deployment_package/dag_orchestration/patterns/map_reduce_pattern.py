#!/usr/bin/env python3
"""
Map-Reduce Pattern for DAG Orchestration
========================================

Implementation of map-reduce style parallel execution for data processing tasks
with automatic partitioning, parallel mapping, and result aggregation.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, TypeVar, Generic, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')


class PartitioningStrategy(Enum):
    """Strategies for data partitioning."""
    EQUAL_SIZE = "equal_size"
    ROUND_ROBIN = "round_robin"
    HASH_BASED = "hash_based"
    CUSTOM = "custom"


class AggregationStrategy(Enum):
    """Strategies for result aggregation."""
    CONCATENATE = "concatenate"
    SUM = "sum"
    MERGE = "merge"
    CUSTOM = "custom"


@dataclass
class MapTask(Generic[T, U]):
    """Definition of a map task."""
    task_id: str
    name: str
    map_function: Callable[[T], U]
    input_data: T
    partition_id: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReduceTask(Generic[U, V]):
    """Definition of a reduce task."""
    task_id: str
    name: str
    reduce_function: Callable[[List[U]], V]
    input_results: List[U]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MapReduceConfig:
    """Configuration for map-reduce execution."""
    partitioning_strategy: PartitioningStrategy = PartitioningStrategy.EQUAL_SIZE
    aggregation_strategy: AggregationStrategy = AggregationStrategy.CONCATENATE
    max_partitions: int = 10
    min_partition_size: int = 1
    max_workers: int = 10
    timeout_seconds: Optional[float] = None
    enable_intermediate_storage: bool = False
    custom_partitioner: Optional[Callable] = None
    custom_aggregator: Optional[Callable] = None


@dataclass
class MapReduceResult(Generic[V]):
    """Result of map-reduce execution."""
    execution_id: str
    final_result: V
    map_results: List[Any]
    reduce_results: List[Any]
    execution_time: float
    partition_count: int
    successful_maps: int
    failed_maps: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class MapReduceExecutor(ReflectiveModule, Generic[T, U, V]):
    """
    Map-Reduce executor for parallel data processing.
    
    Features:
    - Automatic data partitioning
    - Parallel map phase execution
    - Configurable aggregation strategies
    - Fault tolerance and error handling
    - Performance monitoring and optimization
    """
    
    def __init__(self, config: Optional[MapReduceConfig] = None):
        super().__init__()
        self.module_id = "MapReduceExecutor"
        self._config = config or MapReduceConfig()
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Execution state
        self._executor: Optional[ThreadPoolExecutor] = None
        self._active_executions: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self._total_executions = 0
        self._successful_executions = 0
        self._failed_executions = 0
        self._total_partitions_processed = 0
        
        self._logger.info(f"MapReduceExecutor initialized with config: {self._config}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "MapReduceExecutor",
            "version": "1.0.0",
            "description": "Map-Reduce executor for parallel data processing",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "configuration": {
                "partitioning_strategy": self._config.partitioning_strategy.value,
                "aggregation_strategy": self._config.aggregation_strategy.value,
                "max_partitions": self._config.max_partitions,
                "max_workers": self._config.max_workers
            },
            "statistics": {
                "total_executions": self._total_executions,
                "successful_executions": self._successful_executions,
                "failed_executions": self._failed_executions,
                "success_rate": self._successful_executions / max(self._total_executions, 1),
                "total_partitions_processed": self._total_partitions_processed,
                "active_executions": len(self._active_executions)
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            issues = []
            health_score = 1.0
            
            # Check executor state
            if self._executor and self._executor._shutdown:
                issues.append("Thread pool executor is shutdown")
                health_score *= 0.7
            
            # Check execution statistics
            if self._total_executions > 0:
                success_rate = self._successful_executions / self._total_executions
                if success_rate < 0.8:
                    issues.append(f"Low execution success rate: {success_rate:.1%}")
                    health_score *= 0.6
            
            # Check active executions
            if len(self._active_executions) > 10:
                issues.append(f"High number of active executions: {len(self._active_executions)}")
                health_score *= 0.8
            
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
            # In degraded mode, reduce parallelism and use simpler strategies
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.MONITORING
            ]
            
            # Reduce configuration for degraded mode
            self._config.max_workers = min(self._config.max_workers, 2)
            self._config.max_partitions = min(self._config.max_partitions, 4)
            self._config.partitioning_strategy = PartitioningStrategy.EQUAL_SIZE
            self._config.aggregation_strategy = AggregationStrategy.CONCATENATE
            
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
    
    async def execute_map_reduce(self, 
                                input_data: List[T],
                                map_function: Callable[[T], U],
                                reduce_function: Callable[[List[U]], V],
                                execution_id: Optional[str] = None) -> MapReduceResult[V]:
        """
        Execute map-reduce pattern on input data.
        
        Args:
            input_data: List of input data items
            map_function: Function to apply to each data item
            reduce_function: Function to aggregate map results
            execution_id: Optional execution identifier
            
        Returns:
            MapReduceResult with final result and execution details
        """
        with self.trace_operation("execute_map_reduce", 
                                input_size=len(input_data),
                                execution_id=execution_id) as trace:
            
            execution_id = execution_id or str(uuid.uuid4())
            start_time = datetime.now()
            
            try:
                # Track execution
                self._active_executions[execution_id] = {
                    'start_time': start_time,
                    'input_size': len(input_data),
                    'status': 'partitioning'
                }
                self._total_executions += 1
                
                # Phase 1: Partition data
                self._logger.info(f"Starting map-reduce execution {execution_id} with {len(input_data)} items")
                partitions = self._partition_data(input_data)
                self._active_executions[execution_id]['status'] = 'mapping'
                self._active_executions[execution_id]['partition_count'] = len(partitions)
                
                # Phase 2: Execute map tasks in parallel
                map_results = await self._execute_map_phase(partitions, map_function, execution_id)
                self._active_executions[execution_id]['status'] = 'reducing'
                self._active_executions[execution_id]['map_results'] = len(map_results)
                
                # Phase 3: Execute reduce phase
                final_result = await self._execute_reduce_phase(map_results, reduce_function, execution_id)
                
                # Calculate execution time
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Create result
                result = MapReduceResult(
                    execution_id=execution_id,
                    final_result=final_result,
                    map_results=map_results,
                    reduce_results=[final_result],  # Single reduce result
                    execution_time=execution_time,
                    partition_count=len(partitions),
                    successful_maps=len([r for r in map_results if r is not None]),
                    failed_maps=len([r for r in map_results if r is None]),
                    metadata={
                        'input_size': len(input_data),
                        'partitioning_strategy': self._config.partitioning_strategy.value,
                        'aggregation_strategy': self._config.aggregation_strategy.value,
                        'max_workers': self._config.max_workers
                    }
                )
                
                # Update statistics
                self._successful_executions += 1
                self._total_partitions_processed += len(partitions)
                
                trace.output_result = {
                    'execution_id': execution_id,
                    'execution_time': execution_time,
                    'partition_count': len(partitions),
                    'successful_maps': result.successful_maps,
                    'failed_maps': result.failed_maps
                }
                
                self._logger.info(f"Map-reduce execution {execution_id} completed successfully in {execution_time:.2f}s")
                return result
                
            except Exception as e:
                self._failed_executions += 1
                self._logger.error(f"Map-reduce execution {execution_id} failed: {e}")
                
                trace.output_result = {
                    'execution_id': execution_id,
                    'error': str(e)
                }
                
                raise e
                
            finally:
                # Cleanup
                if execution_id in self._active_executions:
                    del self._active_executions[execution_id]
    
    def _partition_data(self, data: List[T]) -> List[List[T]]:
        """Partition input data based on configured strategy."""
        if not data:
            return []
        
        if self._config.partitioning_strategy == PartitioningStrategy.CUSTOM and self._config.custom_partitioner:
            return self._config.custom_partitioner(data)
        
        # Calculate partition count
        partition_count = min(
            self._config.max_partitions,
            max(1, len(data) // self._config.min_partition_size)
        )
        
        if self._config.partitioning_strategy == PartitioningStrategy.EQUAL_SIZE:
            return self._partition_equal_size(data, partition_count)
        elif self._config.partitioning_strategy == PartitioningStrategy.ROUND_ROBIN:
            return self._partition_round_robin(data, partition_count)
        elif self._config.partitioning_strategy == PartitioningStrategy.HASH_BASED:
            return self._partition_hash_based(data, partition_count)
        else:
            return self._partition_equal_size(data, partition_count)
    
    def _partition_equal_size(self, data: List[T], partition_count: int) -> List[List[T]]:
        """Partition data into equal-sized chunks."""
        chunk_size = len(data) // partition_count
        remainder = len(data) % partition_count
        
        partitions = []
        start = 0
        
        for i in range(partition_count):
            # Add one extra item to first 'remainder' partitions
            size = chunk_size + (1 if i < remainder else 0)
            end = start + size
            partitions.append(data[start:end])
            start = end
        
        return [p for p in partitions if p]  # Remove empty partitions
    
    def _partition_round_robin(self, data: List[T], partition_count: int) -> List[List[T]]:
        """Partition data using round-robin distribution."""
        partitions = [[] for _ in range(partition_count)]
        
        for i, item in enumerate(data):
            partitions[i % partition_count].append(item)
        
        return [p for p in partitions if p]  # Remove empty partitions
    
    def _partition_hash_based(self, data: List[T], partition_count: int) -> List[List[T]]:
        """Partition data based on hash values."""
        partitions = [[] for _ in range(partition_count)]
        
        for item in data:
            partition_index = hash(str(item)) % partition_count
            partitions[partition_index].append(item)
        
        return [p for p in partitions if p]  # Remove empty partitions
    
    async def _execute_map_phase(self, partitions: List[List[T]], 
                                map_function: Callable[[T], U],
                                execution_id: str) -> List[U]:
        """Execute map phase in parallel."""
        if not self._executor or self._executor._shutdown:
            self._executor = ThreadPoolExecutor(max_workers=self._config.max_workers)
        
        # Create map tasks
        map_tasks = []
        for i, partition in enumerate(partitions):
            for j, item in enumerate(partition):
                task = MapTask(
                    task_id=f"{execution_id}_map_{i}_{j}",
                    name=f"Map task {i}-{j}",
                    map_function=map_function,
                    input_data=item,
                    partition_id=i
                )
                map_tasks.append(task)
        
        # Execute map tasks
        results = []
        futures = []
        
        for task in map_tasks:
            future = self._executor.submit(self._execute_map_task, task)
            futures.append(future)
        
        # Collect results
        for future in as_completed(futures):
            try:
                result = future.result(timeout=self._config.timeout_seconds)
                results.append(result)
            except Exception as e:
                self._logger.error(f"Map task failed: {e}")
                results.append(None)  # Mark as failed
        
        # Filter out failed results
        successful_results = [r for r in results if r is not None]
        return successful_results
    
    def _execute_map_task(self, task: MapTask[T, U]) -> U:
        """Execute a single map task."""
        try:
            return task.map_function(task.input_data)
        except Exception as e:
            self._logger.error(f"Map task {task.task_id} failed: {e}")
            raise e
    
    async def _execute_reduce_phase(self, map_results: List[U], 
                                  reduce_function: Callable[[List[U]], V],
                                  execution_id: str) -> V:
        """Execute reduce phase."""
        if not map_results:
            raise ValueError("No map results to reduce")
        
        # For now, we use a single reduce task
        # In the future, this could be extended to support multiple reduce tasks
        reduce_task = ReduceTask(
            task_id=f"{execution_id}_reduce",
            name="Reduce task",
            reduce_function=reduce_function,
            input_results=map_results
        )
        
        return self._execute_reduce_task(reduce_task)
    
    def _execute_reduce_task(self, task: ReduceTask[U, V]) -> V:
        """Execute a single reduce task."""
        try:
            return task.reduce_function(task.input_results)
        except Exception as e:
            self._logger.error(f"Reduce task {task.task_id} failed: {e}")
            raise e
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        success_rate = self._successful_executions / max(self._total_executions, 1)
        avg_partitions = self._total_partitions_processed / max(self._successful_executions, 1)
        
        return {
            'total_executions': self._total_executions,
            'successful_executions': self._successful_executions,
            'failed_executions': self._failed_executions,
            'success_rate': success_rate,
            'total_partitions_processed': self._total_partitions_processed,
            'average_partitions_per_execution': avg_partitions,
            'active_executions': len(self._active_executions),
            'configuration': {
                'partitioning_strategy': self._config.partitioning_strategy.value,
                'aggregation_strategy': self._config.aggregation_strategy.value,
                'max_partitions': self._config.max_partitions,
                'max_workers': self._config.max_workers
            }
        }
    
    def shutdown(self) -> None:
        """Shutdown the map-reduce executor."""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None
            self._logger.info("MapReduceExecutor shutdown completed")


# Convenience functions
def create_map_reduce_executor(config: Optional[MapReduceConfig] = None) -> MapReduceExecutor:
    """Factory function to create map-reduce executor."""
    return MapReduceExecutor(config=config)


async def execute_map_reduce(input_data: List[T],
                           map_function: Callable[[T], U],
                           reduce_function: Callable[[List[U]], V],
                           config: Optional[MapReduceConfig] = None) -> MapReduceResult[V]:
    """Convenience function to execute map-reduce pattern."""
    executor = create_map_reduce_executor(config)
    try:
        return await executor.execute_map_reduce(input_data, map_function, reduce_function)
    finally:
        executor.shutdown()


# Common aggregation functions
def sum_aggregator(results: List[float]) -> float:
    """Sum aggregation function."""
    return sum(results)


def concatenate_aggregator(results: List[List[T]]) -> List[T]:
    """Concatenate aggregation function."""
    result = []
    for sublist in results:
        result.extend(sublist)
    return result


def merge_dict_aggregator(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge dictionary aggregation function."""
    merged = {}
    for result_dict in results:
        merged.update(result_dict)
    return merged