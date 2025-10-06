#!/usr/bin/env python3
"""
Advanced Parallel Execution Patterns for DAG Orchestration
==========================================================

Advanced execution patterns including map-reduce, conditional execution,
dynamic DAG modification, and intelligent task batching.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

from .map_reduce_pattern import (
    MapReduceExecutor,
    MapTask,
    ReduceTask,
    MapReduceResult,
    MapReduceConfig
)
from .conditional_execution import (
    ConditionalExecutor,
    ConditionalTask,
    ExecutionCondition,
    ConditionEvaluator,
    ConditionalResult
)
from .dynamic_dag_modifier import (
    DynamicDAGModifier,
    DAGModification,
    ModificationType,
    DAGConsistencyValidator
)
from .streaming_execution import (
    StreamingExecutor,
    StreamingTask,
    DataStream,
    StreamProcessor,
    StreamingResult
)
from .intelligent_batching import (
    IntelligentBatcher,
    BatchingStrategy,
    TaskBatch,
    BatchOptimizer,
    BatchingResult
)
from .adaptive_scheduler import (
    AdaptiveScheduler,
    SchedulingPattern,
    PerformancePredictor,
    SchedulingOptimizer
)
from .nested_dag_executor import (
    NestedDAGExecutor,
    HierarchicalTask,
    DAGHierarchy,
    NestedExecutionResult
)

__all__ = [
    'MapReduceExecutor',
    'MapTask',
    'ReduceTask',
    'MapReduceResult',
    'MapReduceConfig',
    'ConditionalExecutor',
    'ConditionalTask',
    'ExecutionCondition',
    'ConditionEvaluator',
    'ConditionalResult',
    'DynamicDAGModifier',
    'DAGModification',
    'ModificationType',
    'DAGConsistencyValidator',
    'StreamingExecutor',
    'StreamingTask',
    'DataStream',
    'StreamProcessor',
    'StreamingResult',
    'IntelligentBatcher',
    'BatchingStrategy',
    'TaskBatch',
    'BatchOptimizer',
    'BatchingResult',
    'AdaptiveScheduler',
    'SchedulingPattern',
    'PerformancePredictor',
    'SchedulingOptimizer',
    'NestedDAGExecutor',
    'HierarchicalTask',
    'DAGHierarchy',
    'NestedExecutionResult'
]