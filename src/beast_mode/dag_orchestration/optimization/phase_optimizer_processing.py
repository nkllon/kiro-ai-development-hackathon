"""
Phase Optimizer Processing

This module was extracted from phase_optimizer.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import math
from ..models.dag_models import MVPPhase, TaskNode, ParallelGroup, ResourceRequirements, MVPRoute, RiskFactor
from ..models.enums import TaskStatus, RiskType, RiskImpact
from src.rm_ddd.core.health import ModuleHealth


def process_task(task: TaskNode):
    if task.task_id in processed:
        return
    for dep_id in task.dependencies:
        if dep_id in task_lookup and dep_id not in processed:
            process_task(task_lookup[dep_id])
    sorted_tasks.append(task)
    processed.add(task.task_id)

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

