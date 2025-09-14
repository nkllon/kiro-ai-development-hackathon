from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import math
from ..models.dag_models import MVPPhase, TaskNode, ParallelGroup, ResourceRequirements, MVPRoute, RiskFactor
from ..models.enums import TaskStatus, RiskType, RiskImpact
from .phase_optimizer_core_core_processing import *
from .phase_optimizer_core_core_utils import *
from .phase_optimizer_core_core_core import *
from src.rm_ddd.core.health import ModuleHealth

