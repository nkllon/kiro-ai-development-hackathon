"""
Constellation Orchestrator - DAG-based AI prompt execution system.

A sophisticated orchestration platform for managing parallel execution of 90+ AI prompts
with comprehensive dependency management, multi-agent coordination, and systematic observability.
"""

from .core.orchestrator import ConstellationOrchestrator
from .core.config import ConstellationConfig
from .models.task_definition import TaskDefinition, TaskStatus
from .models.execution_state import ExecutionState, ExecutionResult

__version__ = "0.1.0"
__all__ = [
    "ConstellationOrchestrator",
    "ConstellationConfig", 
    "TaskDefinition",
    "TaskStatus",
    "ExecutionState",
    "ExecutionResult"
]