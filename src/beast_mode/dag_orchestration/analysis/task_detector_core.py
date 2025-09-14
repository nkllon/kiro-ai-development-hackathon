import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from ..models.dag_models import TaskNode, DependencyEdge
from ..models.enums import TaskStatus
from .spec_parser import ParsedSpec
from .task_detector_core_core import *
from .task_detector_core_processing import *
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

