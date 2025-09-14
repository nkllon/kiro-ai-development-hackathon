"""
Phase Optimizer Core Utils

This module was extracted from phase_optimizer_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import math
from ..models.dag_models import MVPPhase, TaskNode, ParallelGroup, ResourceRequirements, MVPRoute, RiskFactor
from ..models.enums import TaskStatus, RiskType, RiskImpact
from src.rm_ddd.core.health import ModuleHealth


class IdentifyrequiredtoolsClass:
    """Auto-generated class for functions."""

    def _identify_required_tools(self, tasks: List[TaskNode]) -> List[str]:
    """Identify required tools for tasks."""
    tools = set()
    for task in tasks:
    task_text = f'{task.task_name} {task.description}'.lower()
    if any((keyword in task_text for keyword in ['git', 'version', 'repository'])):
    tools.add('Git')
    if any((keyword in task_text for keyword in ['docker', 'container'])):
    tools.add('Docker')
    if any((keyword in task_text for keyword in ['kubernetes', 'k8s'])):
    tools.add('Kubernetes')
    if any((keyword in task_text for keyword in ['ci/cd', 'pipeline', 'deployment'])):
    tools.add('CI/CD Pipeline')
    if any((keyword in task_text for keyword in ['test', 'pytest', 'testing'])):
    tools.add('Testing Framework')
    if any((keyword in task_text for keyword in ['api', 'rest', 'endpoint'])):
    tools.add('API Development Tools')
    return list(tools) if tools else ['Standard Development Environment']

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

