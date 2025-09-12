from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import math
from ..models.dag_models import TaskNode, ParallelGroup, OptimizedExecution, ExecutionPhase, ResourceRequirements, ResourceAllocation, TeamAssignment
from ..models.enums import TaskStatus, OptimizationStrategy, ParallelizationLevel
from ..analysis.dependency_mapper import ConstraintGraph
from .parallel_optimizer_core_core import *
