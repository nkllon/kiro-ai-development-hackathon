from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import math
from ..models.dag_models import TaskNode, ParallelGroup, OptimizedExecution, ExecutionPhase, ResourceRequirements, ResourceAllocation, TeamAssignment
from ..models.enums import TaskStatus, OptimizationStrategy, ParallelizationLevel
from ..analysis.dependency_mapper import ConstraintGraph
from .parallel_optimizer_core_core import *
from src.rm_ddd.core.health import ModuleHealth


class RegistermoduleClass:
    """Auto-generated class for functions."""

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

