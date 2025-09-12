import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
from ..models.dag_models import TaskNode, MVPRoute, MVPPhase, RiskFactor, ParallelGroup, ResourceRequirements
from ..models.enums import TaskStatus, RiskType, RiskImpact
from .risk_assessor_core_core_core import *
