"""
Recursive DAG Orchestration System
==================================

A meta-programming system that uses DAG orchestration to orchestrate itself,
demonstrating the ultimate recursive capability with mathematical guarantees.
"""

from .core.recursive_orchestrator import RecursiveOrchestrator
from .core.recursion_context import RecursionContext, RecursionLevel

__all__ = [
    'RecursiveOrchestrator',
    'RecursionContext',
    'RecursionLevel'
]