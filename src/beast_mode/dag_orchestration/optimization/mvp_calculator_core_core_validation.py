"""
Mvp Calculator Core Core Validation

This module was extracted from mvp_calculator_core_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import heapq
from ..models.dag_models import EcosystemDAG, TaskNode, MVPRoute, MVPPhase, RiskFactor, ParallelGroup, ResourceRequirements
from ..models.enums import TaskStatus, RiskType, RiskImpact
from ..analysis.dependency_mapper import ConstraintGraph
from datetime import datetime
from datetime import datetime
from datetime import datetime
from src.rm_ddd.core.health import ModuleHealth


class CheckdependenciessatisfiedClass:
    """Auto-generated class for functions."""

    def _check_dependencies_satisfied(self, selected_tasks: List[TaskNode], all_tasks: List[TaskNode]) -> bool:
    """Check if all dependencies are satisfied."""
    selected_ids = {task.task_id for task in selected_tasks}
    task_lookup = {task.task_id: task for task in all_tasks}
    for task in selected_tasks:
    for dep_id in task.dependencies:
    if dep_id not in selected_ids and dep_id in task_lookup:
    dep_task = task_lookup[dep_id]
    if dep_task.completion_status != TaskStatus.COMPLETED:
    return False
    return True

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

