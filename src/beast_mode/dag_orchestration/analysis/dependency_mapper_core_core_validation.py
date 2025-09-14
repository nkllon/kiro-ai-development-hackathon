"""
Dependency Mapper Core Core Validation

This module was extracted from dependency_mapper_core_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
from ..models.dag_models import TaskNode, DependencyEdge, SpecificationNode
from ..models.enums import TaskStatus
from src.rm_ddd.core.health import ModuleHealth


class ValidatedependenciesClass:
    """Auto-generated class for functions."""

    def validate_dependencies(self, constraint_graph: ConstraintGraph) -> List[DependencyConflict]:
    """
    Validate dependency graph and return conflicts.

    Args:
    constraint_graph: Constraint graph to validate

    Returns:
    List[DependencyConflict]: All detected conflicts
    """
    return constraint_graph.conflicts

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

