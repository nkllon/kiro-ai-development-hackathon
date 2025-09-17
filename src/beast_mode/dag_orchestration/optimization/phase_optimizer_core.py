from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import math
from ..models.dag_models import MVPPhase, TaskNode, ParallelGroup, ResourceRequirements, MVPRoute, RiskFactor
from ..models.enums import TaskStatus, RiskType, RiskImpact
from .phase_optimizer_core_core import *
from .phase_optimizer_core_processing import *
from .phase_optimizer_core_utils import *
from src.rm_ddd.core.health import ModuleHealth


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

