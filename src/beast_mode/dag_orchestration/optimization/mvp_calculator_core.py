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

