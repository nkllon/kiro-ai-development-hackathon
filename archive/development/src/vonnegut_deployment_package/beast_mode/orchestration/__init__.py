#!/usr/bin/env python3
"""
Beast Mode Orchestration Framework

Provides DAG-based task execution with proper mathematical validation,
independent task execution, and parallel orchestration capabilities.
"""

from .dag_validator import (
    DAGValidator,
    DAGValidationReport,
    ValidationResult,
    TaskNode
)

from .independent_task_executor import (
    IndependentTaskExecutor,
    TaskResult,
    TaskState,
    TaskExecutionContext,
    ExecutionMode,
    ResourceLimits
)

from .parallel_orchestrator import (
    ParallelOrchestrator,
    OrchestrationResult,
    WaveExecutionResult,
    OrchestrationState
)

__all__ = [
    # DAG Validation
    'DAGValidator',
    'DAGValidationReport', 
    'ValidationResult',
    'TaskNode',
    
    # Task Execution
    'IndependentTaskExecutor',
    'TaskResult',
    'TaskState',
    'TaskExecutionContext',
    'ExecutionMode',
    'ResourceLimits',
    
    # Orchestration
    'ParallelOrchestrator',
    'OrchestrationResult',
    'WaveExecutionResult',
    'OrchestrationState'
]