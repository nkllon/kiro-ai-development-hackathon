from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import heapq
from ..models.dag_models import EcosystemDAG, TaskNode, MVPRoute, MVPPhase, RiskFactor, ParallelGroup, ResourceRequirements
from ..models.enums import TaskStatus, RiskType, RiskImpact
from ..analysis.dependency_mapper import ConstraintGraph
from datetime import datetime
from datetime import datetime
from .mvp_calculator_core_validation import *
from .mvp_calculator_core_core import *
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

