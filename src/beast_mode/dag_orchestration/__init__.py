"""
Beast Mode DAG Orchestration System.

Systematic dependency analysis, parallel execution orchestration, and MVP route
calculation for complex multi-spec ecosystems.
"""

from .core.orchestration_engine import OrchestrationEngine
from .analysis.dependency_analyzer import DependencyAnalyzer
from .optimization.mvp_calculator import MVPRouteCalculator
from .optimization.parallel_optimizer import ParallelExecutionOptimizer
from .models.dag_models import (
    EcosystemDAG,
    SpecificationNode,
    TaskNode,
    MVPRoute,
    MVPPhase,
    OptimizedExecution,
    ExecutionPhase,
    ParallelGroup,
    ResourceAllocation
)
from .models.enums import (
    TaskStatus,
    RiskType,
    RiskImpact,
    ExecutionStatus as ExecutionStatusEnum
)

__all__ = [
    # Core orchestration
    "OrchestrationEngine",
    "DependencyAnalyzer", 
    "MVPRouteCalculator",
    "ParallelExecutionOptimizer",
    
    # Data models
    "EcosystemDAG",
    "SpecificationNode", 
    "TaskNode",
    "MVPRoute",
    "MVPPhase",
    "OptimizedExecution",
    "ExecutionPhase",
    "ParallelGroup",
    "ResourceAllocation",
    
    # Enums
    "TaskStatus",
    "RiskType", 
    "RiskImpact",
    "ExecutionStatusEnum"
]